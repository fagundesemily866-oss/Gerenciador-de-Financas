"""Diagnóstico mensal transparente da saúde financeira com dados reais da conta.

Não grava dados, não gera movimentações e não atribui uma pontuação fictícia
para meses que ainda não possuem lançamentos.
"""
from controllers.saude_financeira_controller import SaudeFinanceiraController
from services.visao_financeira import resumo, campo


def analisar_saude_mensal(lancamentos, ano, mes):
    """Devolve um diagnóstico exclusivamente sobre lançamentos do mês informado."""
    dados = resumo(lancamentos, ano, mes)
    # Lançamentos podem trazer tipos com capitalização diferente; o resumo
    # já os normaliza. Descarta tipos desconhecidos em vez de gerar um score.
    reconhecidos = [
        l for l in dados['lancamentos']
        if str(campo(l, 'type', campo(l, 'tipo', ''))).upper()
        in ('RECEITA', 'DESPESA')
    ]
    receitas, despesas, saldo = dados['receitas'], dados['despesas'], dados['saldo']

    if not reconhecidos:
        return {
            'disponivel': False, 'score': None, 'situacao': 'Aguardando dados',
            'cor': '#94A3B8', 'resumo': dados, 'percentual_gastos': None,
            'mensagem': 'Cadastre receitas ou despesas neste mês para receber uma avaliação.',
            'orientacoes': [
                'Adicione os lançamentos do mês para acompanhar sua situação financeira.',
                'As avaliações futuras serão calculadas com seus dados reais, sem exemplos automáticos.',
            ],
        }

    score = SaudeFinanceiraController._calcular_score(receitas, despesas, saldo)
    if score >= 800:
        situacao, cor = 'Excelente', '#00D084'
    elif score >= 600:
        situacao, cor = 'Boa', '#34D399'
    elif score >= 400:
        situacao, cor = 'Regular', '#FBBF24'
    elif score >= 200:
        situacao, cor = 'Atenção', '#FB923C'
    else:
        situacao, cor = 'Crítica', '#FB7185'

    gasto_pct = (despesas / receitas * 100) if receitas > 0 else None
    if receitas <= 0 and despesas > 0:
        mensagem = 'Há despesas registradas, mas nenhuma receita neste mês.'
        orientacoes = [
            'Registre suas receitas para avaliar quanto da renda está comprometida.',
            'Revise as despesas cadastradas e identifique quais são prioritárias.',
        ]
    elif saldo < 0:
        mensagem = 'Suas despesas ultrapassaram as receitas do mês.'
        orientacoes = [
            'Revise primeiro as categorias com os maiores gastos.',
            'Considere reduzir despesas não essenciais para recuperar o equilíbrio.',
        ]
    elif despesas == 0:
        mensagem = 'Há receitas registradas, mas nenhuma despesa no período.'
        orientacoes = [
            'Registre também suas despesas para ter uma avaliação mais completa.',
            'Acompanhe seu orçamento ao longo do mês.',
        ]
    else:
        mensagem = 'O saldo do mês é positivo ou equilibrado.'
        if gasto_pct is not None and gasto_pct >= 80:
            orientacoes = [
                'Grande parte da renda já está comprometida; acompanhe os próximos gastos.',
                'Revise limites de orçamento por categoria.',
            ]
        else:
            orientacoes = [
                'Acompanhe receitas e despesas regularmente para manter o controle.',
                'Considere direcionar parte do saldo disponível a uma meta financeira.',
            ]
    return {
        'disponivel': True, 'score': score, 'situacao': situacao,
        'cor': cor, 'resumo': dados, 'percentual_gastos': gasto_pct,
        'mensagem': mensagem, 'orientacoes': orientacoes,
    }
