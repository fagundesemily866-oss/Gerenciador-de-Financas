"""Testes sem MySQL para o diagnóstico da tela independente de Saúde Financeira."""
import unittest
from services.saude_mensal import analisar_saude_mensal


class TestSaudeMensal(unittest.TestCase):
    @staticmethod
    def l(tipo, valor, mes=10, categoria='Alimentação'):
        return {
            'type': tipo, 'value': valor,
            'date': f'2026-{mes:02d}-08', 'category': categoria,
        }

    def test_conta_vazia_exibe_estado_sem_score_ficticio(self):
        resultado = analisar_saude_mensal([], 2026, 10)
        self.assertFalse(resultado['disponivel'])
        self.assertIsNone(resultado['score'])
        self.assertEqual(resultado['situacao'], 'Aguardando dados')
        self.assertEqual(resultado['resumo']['saldo'], 0)

    def test_apenas_lancamentos_de_outros_meses_nao_contam(self):
        resultado = analisar_saude_mensal([self.l('RECEITA', 2500, 9)], 2026, 10)
        self.assertIsNone(resultado['score'])

    def test_despesas_sem_receitas_apresentam_alerta(self):
        resultado = analisar_saude_mensal([self.l('Despesa', 1000)], 2026, 10)
        self.assertEqual(resultado['score'], 150)
        self.assertEqual(resultado['situacao'], 'Crítica')
        self.assertIn('nenhuma receita', resultado['mensagem'])

    def test_dados_reais_dao_com_tipos_variantes(self):
        mov = [self.l('RECEITA', 4000), self.l('Despesa', 800), self.l('DESPESA', 200)]
        resultado = analisar_saude_mensal(mov, 2026, 10)
        self.assertEqual(resultado['resumo']['receitas'], 4000)
        self.assertEqual(resultado['resumo']['despesas'], 1000)
        self.assertEqual(resultado['resumo']['saldo'], 3000)
        self.assertAlmostEqual(resultado['percentual_gastos'], 25.0)
        self.assertEqual(resultado['score'], 875)
        self.assertEqual(resultado['situacao'], 'Excelente')

    def test_saldo_negativo_orienta_revisar_categorias(self):
        resultado = analisar_saude_mensal([self.l('Receita', 700), self.l('Despesa', 1000)], 2026, 10)
        self.assertLess(resultado['resumo']['saldo'], 0)
        self.assertTrue(any('categorias' in x for x in resultado['orientacoes']))


if __name__ == '__main__':
    unittest.main()
