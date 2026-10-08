"""
Testes Automatizados para o Laboratório e Simulador Financeiro Avançado.
========================================================================

Verifica:
1. Projeção temporal contínua (3, 6, 12 e 24 meses);
2. Cálculo dos 3 cenários (Otimista, Normal e Pessimista);
3. Efeito cascata de eventos financeiros inesperados (únicos e recorrentes);
4. Previsão inteligente de datas de conclusão de metas;
5. Comparador de decisões financeiras (Cenários A, B e C);
6. Mapa de consequências financeiras;
7. Persistência de simulações com SimulacaoDAO;
8. Análise interpretativa da IA com fallback local.
"""
import unittest
import os
import shutil
import tempfile
from models.database import Database
from dao.simulacao_dao import SimulacaoDAO
from controllers.inteligencia_financeira_controller import InteligenciaFinanceiraController
from services.ai_service import AIService


class TestSimuladorAvancado(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_sim.db")
        self.db = Database(self.db_path)
        self.sim_dao = SimulacaoDAO(self.db)

        self.lancamentos_teste = [
            {"value": 4000.0, "type": "Receita", "category": "Salário", "date": "2026-09-05"},
            {"value": 1200.0, "type": "Despesa", "category": "Moradia", "date": "2026-09-10"},
            {"value": 800.0, "type": "Despesa", "category": "Alimentação", "date": "2026-09-12"},
            {"value": 400.0, "type": "Despesa", "category": "Transporte", "date": "2026-09-15"},
        ]

        self.metas_teste = [
            {"id": 1, "descricao": "Reserva de Emergência", "valor_alvo": 10000.0, "valor_atual": 4000.0},
            {"id": 2, "descricao": "Viagem de Férias", "valor_alvo": 6000.0, "valor_atual": 1500.0},
        ]

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_projecao_temporal_periodos(self):
        """Verifica se a projeção gera exatamente a quantidade de meses solicitada."""
        for h in [3, 6, 12, 24]:
            res = InteligenciaFinanceiraController.projetar_futuro_financeiro(
                lancamentos=self.lancamentos_teste,
                metas=self.metas_teste,
                meses_horizonte=h,
            )
            self.assertEqual(len(res["meses"]), h)
            self.assertIn("resumo", res)
            self.assertIn("saldo_final_projetado", res["resumo"])
            self.assertGreater(res["resumo"]["total_receitas_periodo"], 0)

    def test_02_cenarios_multiplos(self):
        """Verifica se Cenário Otimista > Normal > Pessimista em saldo final."""
        res = InteligenciaFinanceiraController.projetar_futuro_financeiro(
            lancamentos=self.lancamentos_teste,
            metas=self.metas_teste,
            meses_horizonte=12,
        )
        cenarios = res["cenarios"]
        saldo_otim = cenarios["otimista"]["saldo_final"]
        saldo_norm = cenarios["normal"]["saldo_final"]
        saldo_pess = cenarios["pessimista"]["saldo_final"]

        self.assertGreater(saldo_otim, saldo_norm)
        self.assertGreater(saldo_norm, saldo_pess)

    def test_03_eventos_inesperados_cascata(self):
        """Verifica se eventos únicos e recorrentes alteram as despesas a partir do mês correto."""
        evento_unico = {
            "descricao": "Conserto Carro",
            "valor": 1000.0,
            "mes_inicio": 2,
            "tipo": "unico",
            "natureza": "despesa",
        }
        evento_recorrente = {
            "descricao": "Curso de Idiomas",
            "valor": 200.0,
            "mes_inicio": 4,
            "tipo": "recorrente",
            "natureza": "despesa",
        }

        res = InteligenciaFinanceiraController.projetar_futuro_financeiro(
            lancamentos=self.lancamentos_teste,
            metas=self.metas_teste,
            meses_horizonte=6,
            eventos=[evento_unico, evento_recorrente],
        )

        meses = res["meses"]
        # Mês 1: sem eventos
        self.assertEqual(len(meses[0]["eventos_mes"]), 0)
        # Mês 2: evento único de 1000
        self.assertEqual(len(meses[1]["eventos_mes"]), 1)
        self.assertEqual(meses[1]["impacto_eventos_despesas"], 1000.0)
        # Mês 3: sem eventos
        self.assertEqual(len(meses[2]["eventos_mes"]), 0)
        # Mês 4: evento recorrente de 200
        self.assertEqual(len(meses[3]["eventos_mes"]), 1)
        self.assertEqual(meses[3]["impacto_eventos_despesas"], 200.0)
        # Mês 5: evento recorrente mantido
        self.assertEqual(len(meses[4]["eventos_mes"]), 1)
        self.assertEqual(meses[4]["impacto_eventos_despesas"], 200.0)

    def test_04_previsao_inteligente_metas(self):
        """Verifica se o cálculo inteligente projeta a data de conquista de metas."""
        res = InteligenciaFinanceiraController.projetar_futuro_financeiro(
            lancamentos=self.lancamentos_teste,
            metas=self.metas_teste,
            meses_horizonte=12,
            aporte_extra_metas=300.0,
        )
        metas = res["metas"]
        self.assertEqual(len(metas), 2)
        for m in metas:
            self.assertIn("data_estimada_simulada", m)
            self.assertIn("meses_restantes_simulado", m)
            self.assertGreater(m["meses_restantes_simulado"], 0)

    def test_05_comparador_decisoes(self):
        """Verifica a comparação lado a lado de 3 decisões e identificação de campeãs."""
        dec_a = {"nome": "Parcelar", "parcela_mensal": 300.0}
        dec_b = {"nome": "Poupar", "corte_despesas_pct": 10.0}
        dec_c = {"nome": "Aporte Meta", "aporte_metas": 400.0}

        comp = InteligenciaFinanceiraController.comparar_decisoes_financeiras(
            lancamentos=self.lancamentos_teste,
            metas=self.metas_teste,
            decisao_a=dec_a,
            decisao_b=dec_b,
            decisao_c=dec_c,
            meses_horizonte=12,
        )

        self.assertIn("decisao_a", comp)
        self.assertIn("decisao_b", comp)
        self.assertIn("decisao_c", comp)
        self.assertIn("campea_saldo", comp["veredito"])
        # Poupar deve gerar maior saldo final que parcelar
        self.assertGreater(comp["decisao_b"]["saldo_final"], comp["decisao_a"]["saldo_final"])

    def test_06_mapa_consequencias(self):
        """Verifica a geração da árvore em cascata de causa e efeito de uma decisão."""
        passos = InteligenciaFinanceiraController.gerar_mapa_consequencias(
            lancamentos=self.lancamentos_teste,
            metas=self.metas_teste,
            valor_decisao=3000.0,
            num_parcelas=10,
            tipo_decisao="compra",
        )
        self.assertGreaterEqual(len(passos), 4)
        for p in passos:
            self.assertIn("etapa", p)
            self.assertIn("titulo", p)
            self.assertIn("detalhe", p)

    def test_07_dao_persistir_simulacao(self):
        """Verifica salvar, listar e deletar simulação no SQLite."""
        sim_id = self.sim_dao.inserir(
            nome="Viagem de Verão",
            descricao="Planejamento de corte de gastos",
            parametros={"reducao_despesas_pct": 15, "horizonte_meses": 6},
            resultados={"saldo_final_projetado": 12500.0},
        )
        self.assertIsNotNone(sim_id)

        sim_carregada = self.sim_dao.buscar_por_id(sim_id)
        self.assertIsNotNone(sim_carregada)
        self.assertEqual(sim_carregada["nome"], "Viagem de Verão")
        self.assertEqual(sim_carregada["parametros"]["reducao_despesas_pct"], 15)

        todas = self.sim_dao.listar_todas()
        self.assertEqual(len(todas), 1)

        ok_del = self.sim_dao.deletar(sim_id)
        self.assertTrue(ok_del)
        self.assertEqual(len(self.sim_dao.listar_todas()), 0)

    def test_08_ai_service_analise_simulacao(self):
        """Verifica a geração do parecer de consultoria da IA com fallback inteligente."""
        ai = AIService()
        dados_mock = {
            "horizonte_meses": 12,
            "resumo": {
                "saldo_final_projetado": 15000.0,
                "total_economizado_periodo": 3600.0,
                "diferenca_saldo_final": 2500.0,
            },
            "metas": [
                {"descricao": "Carro", "meses_economizados": 3, "data_estimada_simulada": "Novembro de 2027"}
            ]
        }
        parecer = ai.analisar_simulacao_financeira(dados_mock)
        self.assertIsInstance(parecer, str)
        self.assertGreater(len(parecer), 50)
        self.assertTrue("projeção" in parecer.lower() or "saldo" in parecer.lower() or "meta" in parecer.lower())


if __name__ == "__main__":
    unittest.main()
