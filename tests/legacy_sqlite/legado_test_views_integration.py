import os
import unittest
import customtkinter as ctk

from models.database import Database
from dao.lancamento_dao import LancamentoDAO
from dao.meta_dao import MetaDAO
from dao.categoria_dao import CategoriaDAO
from dao.terceiro_dao import TerceiroDAO
from views.menu_view import MenuView


class TestViewsIntegration(unittest.TestCase):
    """Testa a integração das views, navegação e operações de exclusão."""

    @classmethod
    def setUpClass(cls):
        ctk.set_appearance_mode("Dark")
        cls.root = ctk.CTk()
        cls.root.withdraw()

        # Banco de testes isolado
        cls.db_test_path = "data/test_views.db"
        if os.path.exists(cls.db_test_path):
            try:
                os.remove(cls.db_test_path)
            except Exception:
                pass
        cls.db = Database(cls.db_test_path)

        cls.lancamento_dao = LancamentoDAO(cls.db)
        cls.meta_dao = MetaDAO(cls.db)
        cls.categoria_dao = CategoriaDAO(cls.db)
        cls.terceiro_dao = TerceiroDAO(cls.db)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass
        if os.path.exists(cls.db_test_path):
            try:
                os.remove(cls.db_test_path)
            except Exception:
                pass

    def setUp(self):
        self.usuario_mock = {
            "id": 1,
            "nome": "Usuário Teste",
            "email": "teste@financeiro.com",
            "tipo_perfil": "PF",
            "renda_mensal": 5000.0,
        }
        self.menu = MenuView(self.root, usuario_logado=self.usuario_mock)

    def tearDown(self):
        try:
            self.menu.destroy()
        except Exception:
            pass

    def test_navegacao_todas_views(self):
        """Verifica se todas as 9 views carregam e são instanciadas corretamente."""
        for chave, _, _ in self.menu.itens_menu:
            self.menu.selecionar(chave)
            self.root.update()
            self.assertIsNotNone(self.menu.view_atual, f"A view '{chave}' não foi instanciada.")

    def test_exclusao_lancamento(self):
        """Verifica a exclusão de lançamento no DAO."""
        lid = self.lancamento_dao.inserir(
            descricao="Compra Teste",
            valor=150.0,
            tipo="Despesa",
            categoria="Alimentação",
            data="2026-10-01",
        )
        self.assertIsNotNone(self.lancamento_dao.buscar_por_id(lid))
        sucesso = self.lancamento_dao.excluir(lid)
        self.assertTrue(sucesso)
        self.assertIsNone(self.lancamento_dao.buscar_por_id(lid))

    def test_exclusao_terceiro(self):
        """Verifica a exclusão de contato/terceiro no DAO."""
        tid = self.terceiro_dao.inserir(
            nome="Fornecedor Teste",
            relacao="Fornecedor",
        )
        self.assertIsNotNone(self.terceiro_dao.buscar_por_id(tid))
        sucesso = self.terceiro_dao.excluir(tid)
        self.assertTrue(sucesso)
        self.assertIsNone(self.terceiro_dao.buscar_por_id(tid))

    def test_simulador_arrastar_5_em_5(self):
        """Valida que o slider de economia arredonda para múltiplos de 5."""
        self.menu.selecionar("simulador")
        sim_view = self.menu.view_atual
        sim_view._on_change_corte(17.8)
        self.assertEqual(sim_view.corte_despesas_pct, 20.0)


if __name__ == "__main__":
    unittest.main()
