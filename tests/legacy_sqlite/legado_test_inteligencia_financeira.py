import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from controllers.inteligencia_financeira_controller import InteligenciaFinanceiraController
from models.database import Database
from dao.lancamento_dao import LancamentoDAO
from dao.categoria_dao import CategoriaDAO
from dao.meta_dao import MetaDAO


class TestInteligenciaFinanceira(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db = Database(db_path=self.temp_db.name)

        self.lancamento_dao = LancamentoDAO(self.db)
        self.categoria_dao = CategoriaDAO(self.db)
        self.meta_dao = MetaDAO(self.db)

        # Configurar categorias com limites
        self.categoria_dao.inserir("Alimentação", "Despesa", limite_orcamento=1000.0)
        self.categoria_dao.inserir("Transporte", "Despesa", limite_orcamento=500.0)
        self.categoria_dao.inserir("Lazer", "Despesa", limite_orcamento=400.0)
        self.categoria_dao.inserir("Salário", "Receita")

        # Configurar meta
        self.meta_dao.inserir("Reserva de Emergência", valor_alvo=12000.0, valor_atual=2000.0)

        # Inserir dados do mês anterior (2026-08)
        self.lancamento_dao.inserir("Salário Ago", 6000.0, "Receita", "Salário", "2026-08-05")
        self.lancamento_dao.inserir("Supermercado Ago", 800.0, "Despesa", "Alimentação", "2026-08-10")
        self.lancamento_dao.inserir("Combustível Ago", 400.0, "Despesa", "Transporte", "2026-08-12")

        # Inserir dados do mês atual (2026-09)
        self.lancamento_dao.inserir("Salário Set", 6000.0, "Receita", "Salário", "2026-09-05")
        self.lancamento_dao.inserir("Supermercado Set", 1200.0, "Despesa", "Alimentação", "2026-09-10")
        self.lancamento_dao.inserir("Restaurante Set", 200.0, "Despesa", "Alimentação", "2026-09-15")
        self.lancamento_dao.inserir("Metrô Set", 100.0, "Despesa", "Transporte", "2026-09-12")

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    def test_previsao_gastos_fim_do_mes(self):
        lancamentos = self.lancamento_dao.listar_todos()
        categorias = self.categoria_dao.listar_todas()

        # Simular dia 15 de setembro (mês de 30 dias)
        prev = InteligenciaFinanceiraController.calcular_previsao_mes(
            lancamentos, categorias, ano=2026, mes=9, dia_referencia=15
        )

        self.assertEqual(prev["mes"], 9)
        self.assertEqual(prev["dias_totais"], 30)
        self.assertEqual(prev["dias_decorridos"], 15)
        self.assertEqual(prev["dias_restantes"], 15)

        # Gastos no mês: 1200 + 200 + 100 = 1500
        self.assertEqual(prev["gasto_atual"], 1500.0)
        self.assertEqual(prev["ritmo_diario"], 100.0)
        # Projeção: 1500 + 100 * 15 = 3000.0
        self.assertEqual(prev["projecao_fim_mes"], 3000.0)
        # Limite categorias: 1000 + 500 + 400 = 1900.0
        self.assertEqual(prev["limite_total"], 1900.0)
        self.assertEqual(prev["status"], "estouro_previsto")

    def test_deteccao_gastos_fora_padrao(self):
        lancamentos = self.lancamento_dao.listar_todos()
        categorias = self.categoria_dao.listar_todas()

        anomalias = InteligenciaFinanceiraController.detectar_gastos_fora_padrao(
            lancamentos, categorias, ano=2026, mes=9
        )

        self.assertTrue(len(anomalias) >= 1)
        cats_anomalias = [a["categoria"] for a in anomalias]
        self.assertIn("Alimentação", cats_anomalias)
        # Alimentação subiu de 800 para 1400 (+75%)
        alim = next(a for a in anomalias if a["categoria"] == "Alimentação")
        self.assertEqual(alim["tipo"], "aumento_expressivo")
        self.assertGreater(alim["variacao_pct"], 50)

    def test_insights_automaticos_dashboard(self):
        lancamentos = self.lancamento_dao.listar_todos()
        categorias = self.categoria_dao.listar_todas()
        metas = self.meta_dao.listar_todas()

        insights = InteligenciaFinanceiraController.gerar_insights_dashboard(
            lancamentos, categorias, metas, ano=2026, mes=9
        )

        self.assertTrue(len(insights) >= 3)
        titulos = [i["titulo"] for i in insights]
        # Deve ter insight de maior centro de custo e anomalia/previsão
        self.assertTrue(any("Maior Centro de Custo" in t for t in titulos))

    def test_simulador_financeiro_e_se(self):
        lancamentos = self.lancamento_dao.listar_todos()
        metas = self.meta_dao.listar_todas()
        categorias = self.categoria_dao.listar_todas()

        # Simular corte de 20% nas despesas e aumento de renda de R$ 1.000
        sim = InteligenciaFinanceiraController.calcular_simulacao(
            lancamentos, metas, categorias, reducao_despesas_pct=20.0, aumento_renda_valor=1000.0
        )

        base = sim["cenario_base"]
        simulado = sim["cenario_simulado"]
        diff = sim["diferenca"]

        self.assertGreater(simulado["receitas"], base["receitas"])
        self.assertLess(simulado["despesas"], base["despesas"])
        self.assertGreater(simulado["saldo"], base["saldo"])
        self.assertEqual(diff["aumento_renda_valor"], 1000.0)
        self.assertGreater(diff["economia_anual"], 0.0)

        # Metas impactadas
        self.assertTrue(len(sim["impacto_metas"]) > 0)
        meta_impactada = sim["impacto_metas"][0]
        self.assertLessEqual(meta_impactada["meses_cenario_simulado"], meta_impactada["meses_cenario_atual"])

    def test_relatorio_mensal_automatico(self):
        lancamentos = self.lancamento_dao.listar_todos()
        categorias = self.categoria_dao.listar_todas()

        rel = InteligenciaFinanceiraController.gerar_relatorio_mensal(
            lancamentos, categorias, ano=2026, mes=9
        )

        tot = rel["totais"]
        self.assertEqual(tot["receitas"], 6000.0)
        self.assertEqual(tot["despesas"], 1500.0)
        self.assertEqual(tot["saldo"], 4500.0)
        self.assertEqual(tot["taxa_poupanca"], 75.0)

        # Ranking
        self.assertTrue(len(rel["ranking_categorias"]) >= 2)
        self.assertEqual(rel["ranking_categorias"][0]["categoria"], "Alimentação")

        # Comparativo com mês anterior (Agosto)
        ant = rel["comparativo_anterior"]
        self.assertEqual(ant["receitas_anterior"], 6000.0)
        self.assertEqual(ant["despesas_anterior"], 1200.0)

        # Parecer executivo
        self.assertIn("Excelente Desempenho", rel["status_geral"])


if __name__ == "__main__":
    unittest.main()
