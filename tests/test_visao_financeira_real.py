"""Valida que o resumo financeiro nunca inventa saldos ou movimentações."""
import unittest
from datetime import date
from types import SimpleNamespace

from services.visao_financeira import resumo, dinheiro, periodo_anterior


class TestVisaoFinanceiraReal(unittest.TestCase):
    def test_conta_nova_sem_movimentacoes(self):
        r = resumo([], 2026, 10)
        self.assertEqual((r['receitas'], r['despesas'], r['saldo']), (0.0, 0.0, 0.0))
        self.assertEqual(r['lancamentos'], [])
        self.assertEqual(r['categorias'], [])

    def test_apenas_registros_do_mes_selecionado(self):
        transacoes = [
            {'date': '2026-10-05', 'type': 'Receita', 'value': 2500},
            {'date': '2026-10-06', 'type': 'Despesa', 'category': 'Alimentação', 'value': 200},
            {'date': '2026-10-15', 'type': 'Despesa', 'category': 'Moradia', 'value': 1000},
            {'date': '2026-09-30', 'type': 'Receita', 'value': 9000},
        ]
        r = resumo(transacoes, 2026, 10)
        self.assertEqual(r['receitas'], 2500)
        self.assertEqual(r['despesas'], 1200)
        self.assertEqual(r['saldo'], 1300)
        self.assertEqual(r['categorias'], [('Moradia', 1000), ('Alimentação', 200)])
        self.assertEqual(len(r['lancamentos']), 3)

    def test_dicionario_e_objeto(self):
        registro = SimpleNamespace(data=date(2026, 10, 8), tipo='DESPESA', valor=50, categoria='Lazer')
        r = resumo([registro], 2026, 10)
        self.assertEqual(r['despesas'], 50)
        self.assertEqual(r['categorias'], [('Lazer', 50)])

    def test_formato_moeda_e_periodo(self):
        self.assertEqual(dinheiro(10200.5), 'R$ 10.200,50')
        self.assertEqual(periodo_anterior(2026, 1), (2025, 12))


if __name__ == '__main__':
    unittest.main()
