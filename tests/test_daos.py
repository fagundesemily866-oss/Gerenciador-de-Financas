import os
import sys
import unittest
import tempfile

# Adiciona o diretório do projeto ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.database import Database
from dao.usuario_dao import UsuarioDAO
from dao.categoria_dao import CategoriaDAO
from dao.meta_dao import MetaDAO
from dao.terceiro_dao import TerceiroDAO
from dao.saude_financeira_dao import SaudeFinanceiraDAO
from dao.lancamento_dao import LancamentoDAO
from models.usuario import Usuario
from models.categoria import Categoria
from models.meta import Meta
from models.terceiro import Terceiro
from models.saude_financeira import SaudeFinanceira


class TestDAOs(unittest.TestCase):

    def setUp(self):
        # Cria um arquivo de banco temporário para os testes
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = Database(db_path=self.temp_db.name)

        self.usuario_dao = UsuarioDAO(self.db)
        self.categoria_dao = CategoriaDAO(self.db)
        self.meta_dao = MetaDAO(self.db)
        self.terceiro_dao = TerceiroDAO(self.db)
        self.saude_dao = SaudeFinanceiraDAO(self.db)
        self.lancamento_dao = LancamentoDAO(self.db)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_usuario_dao(self):
        # 1. Inserir
        uid = self.usuario_dao.inserir(
            nome="Carlos Silva",
            email="carlos@teste.com",
            senha_hash="hash123",
            tipo_perfil="PF",
        )
        self.assertIsNotNone(uid)
        self.assertTrue(self.usuario_dao.existe_dados())

        # 2. Buscar por ID e por Email
        user = self.usuario_dao.buscar_por_id(uid)
        self.assertIsNotNone(user)
        self.assertEqual(user["nome"], "Carlos Silva")
        self.assertEqual(user["email"], "carlos@teste.com")

        user_email = self.usuario_dao.buscar_por_email("CARLOS@TESTE.COM")
        self.assertIsNotNone(user_email)
        self.assertEqual(user_email["id"], uid)

        # 3. Listar
        todos = self.usuario_dao.listar_todos()
        self.assertEqual(len(todos), 1)

        # 4. Atualizar
        sucesso_att = self.usuario_dao.atualizar(uid, "Carlos S.", "carlos.novo@teste.com", "PJ")
        self.assertTrue(sucesso_att)
        user_att = self.usuario_dao.buscar_por_id(uid)
        self.assertEqual(user_att["nome"], "Carlos S.")
        self.assertEqual(user_att["tipo_perfil"], "PJ")

        # 5. Alterar Senha
        self.assertTrue(self.usuario_dao.alterar_senha(uid, "nova_hash"))
        self.assertEqual(self.usuario_dao.buscar_por_id(uid)["senha_hash"], "nova_hash")

        # 6. Excluir
        self.assertTrue(self.usuario_dao.excluir(uid))
        self.assertIsNone(self.usuario_dao.buscar_por_id(uid))
        self.assertFalse(self.usuario_dao.existe_dados())

    def test_categoria_dao(self):
        # 1. Inserir
        cid = self.categoria_dao.inserir(
            nome="Alimentação",
            tipo="Despesa",
            escopo="Pessoal",
            limite_orcamento=600.0,
        )
        self.assertIsNotNone(cid)
        self.assertTrue(self.categoria_dao.existe_dados())

        # 2. Buscar por ID
        cat = self.categoria_dao.buscar_por_id(cid)
        self.assertEqual(cat["nome"], "Alimentação")
        self.assertEqual(cat["limite_orcamento"], 600.0)

        # 3. Listar por tipo
        despesas = self.categoria_dao.listar_por_tipo("Despesa")
        self.assertEqual(len(despesas), 1)
        receitas = self.categoria_dao.listar_por_tipo("Receita")
        self.assertEqual(len(receitas), 0)

        # 4. Atualizar limite
        self.assertTrue(self.categoria_dao.atualizar_limite(cid, 750.0))
        self.assertEqual(self.categoria_dao.buscar_por_id(cid)["limite_orcamento"], 750.0)

        # 5. Excluir
        self.assertTrue(self.categoria_dao.excluir(cid))
        self.assertIsNone(self.categoria_dao.buscar_por_id(cid))

    def test_meta_dao(self):
        # 1. Inserir
        mid = self.meta_dao.inserir(
            descricao="Viagem de Férias",
            valor_alvo=5000.0,
            valor_atual=1000.0,
            prazo="12 meses",
            data_limite="2027-12-31",
        )
        self.assertIsNotNone(mid)

        # 2. Buscar e calcular progresso com model
        meta_dict = self.meta_dao.buscar_por_id(mid)
        self.assertEqual(meta_dict["descricao"], "Viagem de Férias")
        meta_obj = Meta(**meta_dict)
        self.assertEqual(meta_obj.calcular_progresso(), 20.0)

        # 3. Guardar valor
        self.assertTrue(self.meta_dao.guardar_valor(mid, 1500.0))
        meta_dict2 = self.meta_dao.buscar_por_id(mid)
        self.assertEqual(meta_dict2["valor_atual"], 2500.0)
        meta_obj2 = Meta(**meta_dict2)
        self.assertEqual(meta_obj2.calcular_progresso(), 50.0)

        # 4. Atualizar
        self.assertTrue(
            self.meta_dao.atualizar(mid, "Viagem Europa", 6000.0, "18 meses", "2028-06-30")
        )
        self.assertEqual(self.meta_dao.buscar_por_id(mid)["descricao"], "Viagem Europa")

        # 5. Excluir
        self.assertTrue(self.meta_dao.excluir(mid))
        self.assertIsNone(self.meta_dao.buscar_por_id(mid))

    def test_terceiro_dao(self):
        # 1. Inserir
        tid = self.terceiro_dao.inserir(nome="Empresa XYZ", relacao="Cliente")
        self.assertIsNotNone(tid)

        # 2. Buscar
        terceiro = self.terceiro_dao.buscar_por_id(tid)
        self.assertEqual(terceiro["nome"], "Empresa XYZ")
        self.assertEqual(terceiro["relacao"], "Cliente")

        # 3. Atualizar
        self.assertTrue(self.terceiro_dao.atualizar(tid, "Empresa ABC", "Fornecedor"))
        att = self.terceiro_dao.buscar_por_id(tid)
        self.assertEqual(att["nome"], "Empresa ABC")
        self.assertEqual(att["relacao"], "Fornecedor")

        # 4. Excluir
        self.assertTrue(self.terceiro_dao.excluir(tid))
        self.assertIsNone(self.terceiro_dao.buscar_por_id(tid))

    def test_saude_financeira_dao(self):
        # Cria um usuário para respeitar a Foreign Key
        uid = self.usuario_dao.inserir(
            nome="Maria Teste",
            email="maria@teste.com",
            senha_hash="senha123",
        )

        # 1. Salvar diagnóstico
        sid1 = self.saude_dao.salvar_diagnostico(
            usuario_id=uid,
            score=750,
            plano_acao_json="[]",
            data_atualizacao="2026-09-01",
        )
        sid2 = self.saude_dao.salvar_diagnostico(
            usuario_id=uid,
            score=820,
            plano_acao_json="[]",
            data_atualizacao="2026-09-18",
        )
        self.assertIsNotNone(sid1)
        self.assertIsNotNone(sid2)

        # 2. Buscar última avaliação
        ultima = self.saude_dao.buscar_ultima_por_usuario(usuario_id=uid)
        self.assertIsNotNone(ultima)
        self.assertEqual(ultima["score"], 820)

        # 3. Histórico
        hist = self.saude_dao.listar_historico(usuario_id=uid)
        self.assertEqual(len(hist), 2)

        # 4. Excluir
        self.assertTrue(self.saude_dao.excluir(sid1))
        self.assertTrue(self.saude_dao.excluir(sid2))
        self.assertFalse(self.saude_dao.existe_dados(usuario_id=uid))

    def test_lancamento_dao(self):
        # 1. Inserir (compatibilidade com interface original)
        lid = self.lancamento_dao.inserir(
            descricao="Salário",
            valor=5000.0,
            tipo="Receita",
            categoria="Salário",
            data="2026-09-05",
        )
        self.assertIsNotNone(lid)

        self.lancamento_dao.inserir(
            descricao="Aluguel",
            valor=1500.0,
            tipo="Despesa",
            categoria="Moradia",
            data="2026-09-10",
        )

        self.assertTrue(self.lancamento_dao.existe_dados())

        # 2. Listar todos
        todos = self.lancamento_dao.listar_todos()
        self.assertEqual(len(todos), 2)

        # 3. Listar por tipo
        receitas = self.lancamento_dao.listar_por_tipo("Receita")
        self.assertEqual(len(receitas), 1)
        self.assertEqual(receitas[0]["description"], "Salário")

        despesas = self.lancamento_dao.listar_por_tipo("Despesa")
        self.assertEqual(len(despesas), 1)
        self.assertEqual(despesas[0]["description"], "Aluguel")

        # 4. Listar por categoria
        moradia = self.lancamento_dao.listar_por_categoria("Moradia")
        self.assertEqual(len(moradia), 1)

        # 5. Atualizar
        self.assertTrue(
            self.lancamento_dao.atualizar(
                lid, "Salário Mensal", 5500.0, "Receita", "Salário", "2026-09-05"
            )
        )
        att = self.lancamento_dao.buscar_por_id(lid)
        self.assertEqual(att["description"], "Salário Mensal")
        self.assertEqual(att["value"], 5500.0)

        # 6. Excluir
        self.assertTrue(self.lancamento_dao.excluir(lid))
        self.assertEqual(len(self.lancamento_dao.listar_todos()), 1)


if __name__ == "__main__":
    unittest.main()
