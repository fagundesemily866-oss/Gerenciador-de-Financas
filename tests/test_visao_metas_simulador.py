"""Regressões do simulador de metas, sem necessidade de MySQL ou Tkinter."""
import unittest
from datetime import date

from services.simulador_cenarios import frase_meta, simular


LANCAMENTOS = [
    {"value": 3500, "type": "Receita", "date": "2026-10-01"},
    {"value": 1800, "type": "Despesa", "date": "2026-10-01"},
]


class TestVisaoMetas(unittest.TestCase):
    def setUp(self):
        self.metas = [
            {"id": 10, "descricao": "Notebook", "valor_alvo": 4000,
             "valor_atual": 1500, "concluida": False, "data_limite": "2027-10-01"},
            {"id": 11, "descricao": "Reserva", "valor_alvo": 3000,
             "valor_atual": 3000, "concluida": True, "data_limite": "2026-08-01"},
        ]

    def _simular(self, metas):
        return simular(LANCAMENTOS, metas, 12, 15.0, 0.0, 0.0, hoje=date(2026, 10, 8))

    def test_exibe_metas_incompletas_e_concluidas_em_todos_cenarios(self):
        result = self._simular(self.metas)
        for nome in ("otimista", "planejado", "pessimista"):
            metas = result["cenarios"][nome]["metas"]
            self.assertEqual([m["nome"] for m in metas], ["Notebook", "Reserva"])
            self.assertEqual(metas[1]["status"], "concluida")
            self.assertEqual(metas[1]["aporte_mensal"], 0)
            self.assertEqual(metas[1]["pct_fim_horizonte"], 100)
            self.assertEqual(metas[1]["meses"], 0)
            self.assertEqual(metas[1]["restante"], 0)
            self.assertIn("já foi concluída", frase_meta(metas[1], nome))
            self.assertGreater(metas[0]["aporte_mensal"], 0)

    def test_somente_concluidas_nao_somem_e_nao_recebem_aportes(self):
        result = self._simular(self.metas[1:])
        for c in result["cenarios"].values():
            self.assertEqual(len(c["metas"]), 1)
            self.assertEqual(c["metas"][0]["status"], "concluida")
            self.assertEqual(c["metas"][0]["aporte_mensal"], 0)
            self.assertFalse(any("ficariam atrasadas" in x["texto"] for x in c["consequencias"]))

    def test_meta_com_valor_atingido_sem_flag_tambem_aparece(self):
        meta = {**self.metas[1], "concluida": False}
        result = self._simular([meta])
        self.assertEqual(result["cenarios"]["planejado"]["metas"][0]["status"], "concluida")

    def test_sem_lancamentos_nao_fabrica_projecao_financeira(self):
        self.assertIsNone(simular([], self.metas, 12, 0, 0, 0))

    def test_usa_somente_metas_recebidas_do_dao(self):
        # simular recebe a lista do MetaDAO já filtrada, sem inventar registros
        result = self._simular(self.metas[:1])
        self.assertEqual(len(result["cenarios"]["planejado"]["metas"]), 1)
        self.assertEqual(result["cenarios"]["planejado"]["metas"][0]["id"], 10)


if __name__ == "__main__":
    unittest.main()
