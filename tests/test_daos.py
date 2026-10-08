"""Testes dos DAOs MySQL com conexão simulada (nunca alteram dados reais)."""
import unittest
from unittest.mock import Mock
from dao.usuario_dao import UsuarioDAO
from dao.categoria_dao import CategoriaDAO
from dao.lancamento_dao import LancamentoDAO
from services.sessao import Sessao


class TestDAOMySQL(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.conn = self.db.get_connection.return_value
        Sessao.limpar()
        self.addCleanup(Sessao.limpar)

    def test_foto_perfil_persiste_no_mysql(self):
        self.conn.execute.return_value.rowcount = 1
        ok = UsuarioDAO(self.db).atualizar_foto(5, 'data/perfis/usuario_5_a.png')
        self.assertTrue(ok)
        self.conn.execute.assert_called_once_with(
            'UPDATE usuario SET foto_perfil = %s WHERE id_usuario = %s',
            ('data/perfis/usuario_5_a.png', 5))
        self.conn.commit.assert_called_once()

    def test_busca_perfil_retorna_caminho_salvo(self):
        self.conn.execute.return_value.fetchone.return_value = {
            'id': 5, 'nome': 'A', 'tipo_perfil': 'PESSOAL',
            'foto_perfil': 'data/perfis/usuario_5_a.png'}
        usuario = UsuarioDAO(self.db).buscar_por_id(5)
        self.assertEqual(usuario['foto_perfil'], 'data/perfis/usuario_5_a.png')
        self.assertEqual(usuario['tipo_perfil'], 'PF')

    def test_categoria_usa_usuario_logado(self):
        Sessao.definir(4)
        self.conn.execute.return_value.lastrowid = 77
        CategoriaDAO(self.db).inserir('Salário', 'Receita')
        sql, params = self.conn.execute.call_args.args
        self.assertIn('INSERT INTO categoria', sql)
        self.assertEqual(params[0], 4)
        self.assertEqual(params[2], 'RECEITA')

    def test_lancamento_cria_categoria_de_receita_corretamente(self):
        Sessao.definir(4)
        self.conn.execute.return_value.fetchone.return_value = None
        self.conn.execute.return_value.lastrowid = 22
        LancamentoDAO(self.db).inserir('Salário', 2500, 'Receita', 'Salário', '2026-10-01')
        queries = [x.args for x in self.conn.execute.call_args_list]
        self.assertEqual(queries[0][1], ('Salário', 4, 'RECEITA'))
        self.assertIn('INSERT INTO categoria', queries[1][0])
        self.assertEqual(queries[1][1][2], 'RECEITA')
        self.assertEqual(queries[2][1][3], 'RECEITA')

    def test_lancamento_despesa_nao_reutiliza_categoria_receita(self):
        Sessao.definir(9)
        self.conn.execute.return_value.fetchone.return_value = None
        self.conn.execute.return_value.lastrowid = 22
        LancamentoDAO(self.db).inserir('Devolução', 40, 'Despesa', 'Outros', '2026-10-01')
        self.assertEqual(self.conn.execute.call_args_list[0].args[1][-1], 'DESPESA')
        self.assertEqual(self.conn.execute.call_args_list[1].args[1][2], 'DESPESA')

    def test_listagem_filtrada_pelo_usuario_logado(self):
        Sessao.definir(15)
        self.conn.execute.return_value.fetchall.return_value = []
        LancamentoDAO(self.db).listar_todos()
        query, params = self.conn.execute.call_args.args
        self.assertIn('l.id_usuario = %s', query)
        self.assertEqual(params, (15,))


if __name__ == '__main__':
    unittest.main()
