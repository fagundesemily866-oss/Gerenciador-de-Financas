"""Testes matemáticos do gerador de demonstração, sem MySQL."""
import random
import unittest
from datetime import date
from unittest.mock import Mock
from services.financas_aleatorias import GeradorFinancasAleatorias, _somar_meses, _ultimo_dia, _arredondar


class TestGeracaoDemo(unittest.TestCase):
    def test_calendario_virada_ano(self):
        self.assertEqual(_somar_meses(2026, 1, -1), (2025, 12))
        self.assertEqual(_somar_meses(2026, 12, 2), (2027, 2))
        self.assertEqual(_ultimo_dia(2028, 2), 29)

    def test_arredondamento(self):
        self.assertEqual(_arredondar(236, 10), 240.0)

    def test_renda_pj_maior_faixa(self):
        gerador = GeradorFinancasAleatorias(db=Mock(), rng=random.Random(6), hoje=date(2026, 10, 8))
        self.assertGreaterEqual(gerador._sortear_renda('PJ'), 9000)
        self.assertGreaterEqual(gerador._sortear_renda('PF'), 3200)

    def test_geracao_e_deterministica_com_mesma_semente(self):
        g1 = GeradorFinancasAleatorias(db=Mock(), rng=random.Random(12))
        g2 = GeradorFinancasAleatorias(db=Mock(), rng=random.Random(12))
        self.assertEqual(g1._sortear_renda('PF'), g2._sortear_renda('PF'))
        self.assertEqual(g1._sortear_taxa_poupanca(), g2._sortear_taxa_poupanca())


if __name__ == '__main__':
    unittest.main()
