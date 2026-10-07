"""Resumo Executivo do Relatório Mensal: poucos números e dois destaques, com dados reais."""
from datetime import datetime
from typing import Any, Dict, List, Optional

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def _brl(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _totais(lancs: List[Dict[str, Any]], ano: int, mes: int):
    rec = desp = 0.0
    cats: Dict[str, float] = {}
    for l in lancs:
        try:
            d = datetime.strptime(str(l["date"])[:10], "%Y-%m-%d")
        except ValueError:
            continue
        if (d.year, d.month) != (ano, mes):
            continue
        if l["type"] == "Receita":
            rec += float(l["value"])
        elif l["type"] == "Despesa":
            desp += float(l["value"])
            cats[l["category"]] = cats.get(l["category"], 0.0) + float(l["value"])
    return rec, desp, cats


def gerar_resumo(lancs: List[Dict[str, Any]], categorias: List[Dict[str, Any]],
                 ano: Optional[int] = None, mes: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Sem ano/mês, usa o mês mais recente com lançamentos. Sem lançamentos retorna None."""
    meses = sorted({(int(str(l["date"])[:4]), int(str(l["date"])[5:7])) for l in lancs if l.get("date")})
    if not meses:
        return None
    ano, mes = (ano, mes) if ano and mes else meses[-1]
    rec, desp, cats = _totais(lancs, ano, mes)
    saldo = rec - desp
    economia = saldo / rec * 100 if rec > 0 else 0.0
    ant_ano, ant_mes = (ano, mes - 1) if mes > 1 else (ano - 1, 12)
    rec_a, desp_a, cats_a = _totais(lancs, ant_ano, ant_mes)
    saldo_a = rec_a - desp_a

    # Destaque positivo (o mais relevante que existir)
    if saldo_a > 0 and saldo > saldo_a:
        positivo = f"Saldo {(saldo - saldo_a) / saldo_a * 100:.0f}% maior que no mês anterior."
    elif rec > 0 and economia >= 20:
        positivo = f"Você economizou {economia:.0f}% da renda do mês."
    elif desp_a > 0 and desp < desp_a:
        positivo = f"Despesas {(desp_a - desp) / desp_a * 100:.0f}% menores que no mês anterior."
    elif saldo > 0:
        positivo = f"Mês fechado no positivo, com {_brl(saldo)} de sobra."
    else:
        positivo = "Nenhum destaque positivo neste mês."

    # Principal alerta: saldo negativo > categoria acima do limite > maior alta de categoria
    limites = {c["nome"]: float(c.get("limite_orcamento") or 0) for c in categorias if c.get("tipo") == "Despesa"}
    estouros = [(n, v - limites[n]) for n, v in cats.items() if limites.get(n, 0) > 0 and v > limites[n]]
    altas = [(n, (v - cats_a[n]) / cats_a[n] * 100) for n, v in cats.items() if cats_a.get(n, 0) > 0 and v > cats_a[n] * 1.15]
    if saldo < 0:
        alerta = f"Despesas superaram as receitas em {_brl(-saldo)}."
    elif estouros:
        n, ex = max(estouros, key=lambda x: x[1])
        alerta = f"{n} passou do limite em {_brl(ex)}."
    elif altas:
        n, p = max(altas, key=lambda x: x[1])
        alerta = f"{n} subiu {p:.0f}% em relação ao mês anterior."
    else:
        alerta = "Nenhum alerta neste mês."

    return {"ano": ano, "mes": mes, "titulo_mes": f"{MESES[mes - 1].capitalize()} de {ano}",
            "saldo": saldo, "receitas": rec, "despesas": desp, "economia_pct": economia,
            "positivo": positivo, "alerta": alerta, "tem_alerta": alerta != "Nenhum alerta neste mês."}
