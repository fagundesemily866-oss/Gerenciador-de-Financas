"""Regressões dos relatórios e do simulador, com dados em memória."""
import unittest
from datetime import date
from services.simulador_cenarios import simular, frase_meta
from services.resumo_executivo import gerar_resumo


class TestSimuladorEResumo(unittest.TestCase):
    def setUp(self):
        hoje = date.today()
        mes = hoje.strftime('%Y-%m')
        self.lancamentos = [
            {'value': 4200., 'type': 'Receita', 'category': 'Salário', 'date': f'{mes}-01'},
            {'value': 1500., 'type': 'Despesa', 'category': 'Moradia', 'date': f'{mes}-02'},
            {'value': 450., 'type': 'Despesa', 'category': 'Alimentação', 'date': f'{mes}-03'},
        ]
        self.metas = [{'id': 1, 'descricao': 'Reserva', 'valor_alvo': 5000, 'valor_atual': 1000,
                       'data_limite': f'{hoje.year+1}-10-01'}]
        self.categorias = [
            {'nome': 'Moradia', 'tipo': 'Despesa', 'limite_orcamento': 2000.},
            {'nome': 'Alimentação', 'tipo': 'Despesa', 'limite_orcamento': 800.},
        ]

    def test_cenarios_ordenados_e_metas(self):
        result = simular(self.lancamentos, self.metas, 12, 10, 0, 0)
        cenarios = result['cenarios']
        self.assertGreater(cenarios['otimista']['saldo_final'], cenarios['planejado']['saldo_final'])
        self.assertGreater(cenarios['planejado']['saldo_final'], cenarios['pessimista']['saldo_final'])
        self.assertEqual(len(cenarios['planejado']['metas']), 1)
        for k in cenarios:
            self.assertTrue(frase_meta(cenarios[k]['metas'][0], k).startswith('Neste cenário'))

    def test_sem_dados_nao_inventa_numeros(self):
        self.assertIsNone(simular([], [], 12, 0, 0, 0))
        self.assertIsNone(gerar_resumo([], []))

    def test_resumo_bate_com_lancamentos(self):
        resumo = gerar_resumo(self.lancamentos, self.categorias)
        self.assertEqual(resumo['receitas'], 4200.)
        self.assertEqual(resumo['despesas'], 1950.)
        self.assertEqual(resumo['saldo'], 2250.)


if __name__ == '__main__':
    unittest.main()
