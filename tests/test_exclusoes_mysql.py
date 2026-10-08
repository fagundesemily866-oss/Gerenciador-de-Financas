"""Testes de exclusão sem conectar ao banco real; todos usam MySQL simulado."""
import unittest
from unittest.mock import Mock
from pathlib import Path

from services.sessao import Sessao
from dao.categoria_dao import CategoriaDAO
from dao.terceiro_dao import TerceiroDAO
from dao.lancamento_dao import LancamentoDAO
from dao.meta_dao import MetaDAO
from dao.simulacao_dao import SimulacaoDAO
from dao.saude_financeira_dao import SaudeFinanceiraDAO
from dao.usuario_dao import UsuarioDAO
from models.database import Database, _ConnectionProxy


class TestExclusoesSeguras(unittest.TestCase):
    def setUp(self):
        self.db = Mock()
        self.conn = self.db.get_connection.return_value
        self.conn.execute.return_value.rowcount = 1
        Sessao.definir(9)
        self.addCleanup(Sessao.limpar)

    def test_categoria_arquiva_preservando_historico(self):
        self.assertTrue(CategoriaDAO(self.db).excluir(17))
        sql, params = self.conn.execute.call_args.args
        self.assertIn('UPDATE categoria SET ativa = 0', sql)
        self.assertNotIn('DELETE FROM categoria', sql)
        self.assertEqual(params, (17, 9))
        self.conn.commit.assert_called_once()

    def test_categoria_arquivada_nao_aparece_nas_listas(self):
        self.conn.execute.return_value.fetchall.return_value = []
        CategoriaDAO(self.db).listar_todas()
        sql, params = self.conn.execute.call_args.args
        self.assertIn('ativa = 1', sql)
        self.assertEqual(params, (9,))

    def test_lancamento_novo_nao_usa_categoria_arquivada(self):
        self.conn.execute.return_value.fetchone.return_value = {'id_categoria': 13}
        resultado = LancamentoDAO(self.db)._resolver_categoria(self.conn, 'Alimentação', 9, 'Despesa')
        self.assertEqual(resultado, 13)
        sql, _ = self.conn.execute.call_args.args
        self.assertIn('ativa = 1', sql)

    def test_lancamento_somente_usuario(self):
        self.assertTrue(LancamentoDAO(self.db).excluir(15))
        sql, params = self.conn.execute.call_args.args
        self.assertIn('DELETE FROM lancamento', sql)
        self.assertIn('id_usuario = %s', sql)
        self.assertEqual(params, (15, 9))

    def test_terceiro_somente_usuario(self):
        self.assertTrue(TerceiroDAO(self.db).excluir(3))
        self.assertEqual(self.conn.execute.call_args.args[1], (3, 9))

    def test_meta_somente_usuario(self):
        self.assertTrue(MetaDAO(self.db).excluir(12))
        self.assertEqual(self.conn.execute.call_args.args[1], (12, 9))

    def test_simulacao_somente_usuario(self):
        self.assertTrue(SimulacaoDAO(self.db).deletar(42))
        self.assertEqual(self.conn.execute.call_args.args[1], (42, 9))

    def test_saude_financeira_somente_usuario(self):
        self.assertTrue(SaudeFinanceiraDAO(self.db).excluir(11))
        self.assertEqual(self.conn.execute.call_args.args[1], (11, 9))

    def test_retorno_false_se_registro_nao_apagado(self):
        self.conn.execute.return_value.rowcount = 0
        self.assertFalse(MetaDAO(self.db).excluir(120))

    def test_nao_permite_deletar_sem_login(self):
        Sessao.limpar()
        for instancia, nome in [(CategoriaDAO(self.db), 'excluir'),
                                 (TerceiroDAO(self.db), 'excluir'),
                                 (MetaDAO(self.db), 'excluir'),
                                 (LancamentoDAO(self.db), 'excluir'),
                                 (SimulacaoDAO(self.db), 'deletar'),
                                 (SaudeFinanceiraDAO(self.db), 'excluir')]:
            with self.subTest(classe=type(instancia).__name__):
                with self.assertRaises(ValueError):
                    getattr(instancia, nome)(1)
        self.conn.execute.assert_not_called()

    def test_conta_rejeita_tentar_excluir_outro_usuario(self):
        with self.assertRaises(ValueError):
            UsuarioDAO(self.db).excluir(10)
        self.conn.execute.assert_not_called()

    def test_conta_exclui_lancamentos_antes_do_usuario(self):
        self.conn.execute.return_value.fetchone.return_value = {'id_usuario': 9}
        self.assertTrue(UsuarioDAO(self.db).excluir(9))
        sqls = [c.args[0].strip() for c in self.conn.execute.call_args_list]
        self.assertTrue(sqls[0].startswith('SELECT id_usuario'))
        self.assertEqual(sqls[1], 'DELETE FROM lancamento WHERE id_usuario = %s')
        self.assertEqual(sqls[2], 'DELETE FROM usuario WHERE id_usuario = %s')
        self.conn.commit.assert_called_once()
        self.conn.rollback.assert_not_called()

    def test_conta_reverte_se_delete_falhar(self):
        self.conn.execute.side_effect = [Mock(fetchone=lambda: {'id_usuario': 9}),
                                         Mock(), RuntimeError('FK bloqueada')]
        with self.assertRaises(RuntimeError):
            UsuarioDAO(self.db).excluir(9)
        self.conn.rollback.assert_called_once()
        self.conn.commit.assert_not_called()

    def test_conta_nao_existente_nao_continua(self):
        self.conn.execute.return_value.fetchone.return_value = None
        self.assertFalse(UsuarioDAO(self.db).excluir(9))
        self.conn.rollback.assert_called_once()
        self.assertEqual(self.conn.execute.call_count, 1)

    def test_connection_proxy_suporta_rollback(self):
        raw = Mock()
        _ConnectionProxy(raw).rollback()
        raw.rollback.assert_called_once()

    def test_migration_de_categoria_nao_destroi_dados(self):
        migration = Path(__file__).resolve().parent.parent / 'migrations' / 'ddl' / 'V1__criar_estrutura.sql'
        sql = migration.read_text(encoding='utf-8')
        self.assertIn('ativa BOOLEAN NOT NULL DEFAULT TRUE', sql)
        self.assertIn('REFERENCES categoria(id_categoria)', sql)


if __name__ == '__main__':
    unittest.main()
