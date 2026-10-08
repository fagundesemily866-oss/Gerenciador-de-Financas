"""Totais reais por usuário; nunca cria dados nem utiliza valores de exemplo."""
from collections import defaultdict
from datetime import date, datetime


def dinheiro(valor):
    """Formata números no padrão brasileiro."""
    return 'R$ ' + f'{float(valor or 0):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


def mes_de(valor):
    if isinstance(valor, (date, datetime)):
        return valor.year, valor.month
    try:
        dia = date.fromisoformat(str(valor)[:10])
        return dia.year, dia.month
    except (ValueError, TypeError):
        return None


def campo(item, chave, padrao=None):
    return item.get(chave, padrao) if isinstance(item, dict) else getattr(item, chave, padrao)


def resumo(lancamentos, ano=None, mes=None):
    """Soma lançamentos referentes ao mês escolhido, com categorias ordenadas."""
    hoje = date.today()
    ano = ano or hoje.year
    mes = mes or hoje.month
    filtrados = [l for l in (lancamentos or []) if mes_de(campo(l, 'date', campo(l, 'data'))) == (ano, mes)]
    receitas = despesas = 0.0
    gastos = defaultdict(float)
    for l in filtrados:
        tipo = str(campo(l, 'type', campo(l, 'tipo', ''))).upper()
        valor = float(campo(l, 'value', campo(l, 'valor', 0)) or 0)
        if tipo == 'RECEITA':
            receitas += valor
        elif tipo == 'DESPESA':
            despesas += valor
            gastos[str(campo(l, 'category', campo(l, 'categoria', 'Sem categoria')) or 'Sem categoria')] += valor
    return {
        'ano': ano, 'mes': mes, 'receitas': receitas, 'despesas': despesas,
        'saldo': receitas - despesas, 'lancamentos': filtrados,
        'categorias': sorted(gastos.items(), key=lambda x: x[1], reverse=True),
    }


def periodo_anterior(ano, mes):
    return (ano - 1, 12) if mes == 1 else (ano, mes - 1)
