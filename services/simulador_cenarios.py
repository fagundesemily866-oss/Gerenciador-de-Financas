"""
Cálculos do Simulador de Cenários (Otimista / Planejado / Pessimista).

Módulo sem interface gráfica: recebe os lançamentos e metas REAIS do usuário e
devolve, para cada cenário, os totais, as consequências e a situação de cada meta.
Sem dados reais, ``simular`` retorna None (a tela mostra um estado vazio em vez de
números inventados).
"""
import math
from datetime import date, datetime
from typing import Any, Dict, List, Optional

# Variação de cada cenário sobre o cenário planejado (mesmas regras do controller)
AJUSTES = {
    "otimista": {"rec": 1.10, "desp": 0.95, "nome": "Otimista"},
    "planejado": {"rec": 1.00, "desp": 1.00, "nome": "Planejado"},
    "pessimista": {"rec": 0.90, "desp": 1.15, "nome": "Pessimista"},
}


def _data(txt) -> Optional[date]:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(txt).strip(), fmt).date()
        except (ValueError, TypeError):
            pass
    return None


def _brl(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def base_mensal(lancamentos: List[Dict[str, Any]], hoje: Optional[date] = None) -> Optional[Dict[str, float]]:
    """Média mensal de receitas/despesas dos últimos 3 meses que têm lançamentos."""
    por_mes: Dict[tuple, List[float]] = {}
    for l in lancamentos:
        d = _data(l.get("date"))
        if not d:
            continue
        r = por_mes.setdefault((d.year, d.month), [0.0, 0.0])
        if l.get("type") == "Receita":
            r[0] += float(l["value"])
        elif l.get("type") == "Despesa":
            r[1] += float(l["value"])
    if not por_mes:
        return None
    meses = sorted(por_mes)[-3:]
    n = len(meses)
    return {
        "receita": sum(por_mes[m][0] for m in meses) / n,
        "despesa": sum(por_mes[m][1] for m in meses) / n,
        "meses_base": n,
    }


def _meses_ate(limite: date, hoje: date) -> int:
    return max(0, math.ceil((limite - hoje).days / 30.4))


def _prazo_meta(meta: Dict[str, Any], hoje: date) -> Optional[date]:
    """Data limite da meta: campo data_limite (dd/mm/aaaa) ou, na falta, hoje + 'N meses'."""
    d = _data(meta.get("data_limite"))
    if d:
        return d
    try:
        n = int(str(meta.get("prazo", "")).split()[0])
        ano = hoje.year + (hoje.month - 1 + n) // 12
        mes = (hoje.month - 1 + n) % 12 + 1
        return date(ano, mes, min(hoje.day, 28))
    except (ValueError, IndexError):
        return None


def simular(
    lancamentos: List[Dict[str, Any]],
    metas: List[Dict[str, Any]],
    horizonte_meses: int,
    corte_despesas_pct: float,
    renda_extra: float,
    aporte_metas: float,
    hoje: Optional[date] = None,
) -> Optional[Dict[str, Any]]:
    hoje = hoje or date.today()
    base = base_mensal(lancamentos, hoje)
    if base is None:
        return None
    horizonte = max(1, int(horizonte_meses))
    saldo_inicial = sum(
        float(l["value"]) if l.get("type") == "Receita" else -float(l["value"]) for l in lancamentos
    )
    metas_abertas = [m for m in metas if float(m.get("valor_atual") or 0) < float(m.get("valor_alvo") or 0)]

    cenarios: Dict[str, Dict[str, Any]] = {}
    for chave, aj in AJUSTES.items():
        rec_m = (base["receita"] + renda_extra) * aj["rec"]
        desp_m = base["despesa"] * (1 - corte_despesas_pct / 100.0) * aj["desp"]
        saldo_m = rec_m - desp_m
        evolucao, acum = [], saldo_inicial
        for _ in range(horizonte):
            acum += saldo_m
            evolucao.append(acum)
        cenarios[chave] = {
            "nome": aj["nome"], "receita_mensal": rec_m, "despesa_mensal": desp_m, "saldo_mensal": saldo_m,
            "evolucao": evolucao, "saldo_final": acum,
            "receitas_acumuladas": rec_m * horizonte, "despesas_acumuladas": desp_m * horizonte,
            "economizado": saldo_m * horizonte,
        }

    # --- metas por cenário ---
    for chave, c in cenarios.items():
        capacidade = max(0.0, c["saldo_mensal"])
        # aporte_metas <= 0 = automático: 70% da sobra mensal do cenário vai para as metas
        aporte_total = capacidade * 0.7 if aporte_metas <= 0 else min(aporte_metas, capacidade)

        def peso(m):  # metas com prazo mais curto / mais a completar recebem mais
            prazo_m = _prazo_meta(m, hoje)
            mp = max(1, _meses_ate(prazo_m, hoje)) if prazo_m else 12
            return (float(m["valor_alvo"]) - float(m["valor_atual"])) / mp
        pesos = {id(m): peso(m) for m in metas_abertas}
        soma_pesos = sum(pesos.values()) or 1.0
        c["aporte_metas_mensal"] = aporte_total
        c["metas"] = []
        for m in metas_abertas:
            alvo, atual = float(m["valor_alvo"]), float(m["valor_atual"])
            restante = alvo - atual
            aporte = aporte_total * pesos[id(m)] / soma_pesos
            meses = math.ceil(restante / aporte) if aporte > 0 else None
            prazo = _prazo_meta(m, hoje)
            meses_prazo = _meses_ate(prazo, hoje) if prazo else None
            if meses is None:
                status = "sem_aporte"
            elif prazo is None:
                status = "sem_prazo"
            elif prazo <= hoje:
                status = "atrasada"
            elif meses < meses_prazo - 1:
                status = "antes"
            elif meses <= meses_prazo:
                status = "no_prazo"
            else:
                status = "atrasada"
            falta_no_prazo = max(0.0, restante - aporte * meses_prazo) if meses_prazo is not None else None
            c["metas"].append({
                "id": m.get("id"), "nome": m.get("descricao", "Meta"), "atual": atual, "alvo": alvo,
                "pct_atual": atual / alvo * 100 if alvo else 0.0, "restante": restante,
                "aporte_mensal": aporte, "meses": meses, "meses_prazo": meses_prazo,
                "prazo": prazo, "status": status, "falta_no_prazo": falta_no_prazo,
                "valor_fim_horizonte": min(alvo, atual + aporte * horizonte),
                "pct_fim_horizonte": min(alvo, atual + aporte * horizonte) / alvo * 100 if alvo else 0.0,
            })

    plan = cenarios["planejado"]
    for chave, c in cenarios.items():
        c["diferenca_vs_planejado"] = c["saldo_final"] - plan["saldo_final"]
        c["consequencias"] = _consequencias(c, plan, chave, base, horizonte, corte_despesas_pct, renda_extra, aporte_metas)

    return {"horizonte": horizonte, "base": base, "saldo_inicial": saldo_inicial, "cenarios": cenarios}


def _consequencias(c, plan, chave, base, horizonte, corte, renda_extra, aporte_metas) -> List[Dict[str, str]]:
    itens = [{"tipo": "info", "texto": f"Você terá acumulado {_brl(c['saldo_final'])} em {horizonte} meses "
                                       f"(economizando {_brl(c['economizado'])} no período)."}]
    economia_corte = base["despesa"] * corte / 100.0 * AJUSTES[chave]["desp"] * horizonte
    if corte > 0:
        itens.append({"tipo": "bom", "texto": f"Cortar {corte:.0f}% das despesas libera {_brl(economia_corte)} no período."})
    if renda_extra > 0:
        itens.append({"tipo": "bom", "texto": f"A renda extra de {_brl(renda_extra)}/mês soma "
                                              f"{_brl(renda_extra * AJUSTES[chave]['rec'] * horizonte)} ao seu saldo."})
    itens.append({"tipo": "info", "texto": f"Despesas somam {_brl(c['despesas_acumuladas'])} contra receitas de "
                                           f"{_brl(c['receitas_acumuladas'])}."})
    if chave != "planejado":
        d = c["diferenca_vs_planejado"]
        itens.append({"tipo": "bom" if d >= 0 else "ruim",
                      "texto": f"{abs(d) and _brl(abs(d))} {'a mais' if d >= 0 else 'a menos'} que o cenário planejado."})
    if c["saldo_mensal"] < 0:
        itens.append({"tipo": "ruim", "texto": "As despesas superam as receitas: o saldo diminui a cada mês e não sobra para as metas."})
    elif aporte_metas > c["saldo_mensal"] > 0 and aporte_metas > 0:
        itens.append({"tipo": "ruim", "texto": f"Só sobram {_brl(c['saldo_mensal'])}/mês: o aporte desejado de {_brl(aporte_metas)} não cabe."})
    atrasadas = [m for m in c["metas"] if m["status"] in ("atrasada", "sem_aporte")]
    adiantadas = [m for m in c["metas"] if m["status"] == "antes"]
    if atrasadas:
        itens.append({"tipo": "ruim", "texto": f"{len(atrasadas)} meta(s) ficariam atrasadas."})
    if adiantadas:
        itens.append({"tipo": "bom", "texto": f"{len(adiantadas)} meta(s) seriam atingidas antes do prazo."})
    return itens


def frase_meta(m: Dict[str, Any], cenario: str) -> str:
    """Frase curta e clara para o usuário, ex.: 'Neste cenário, esta meta ficará atrasada.'"""
    s = m["status"]
    if s == "antes":
        return f"Neste cenário {cenario}, esta meta será atingida antes do prazo."
    if s == "no_prazo":
        return f"Neste cenário {cenario}, esta meta será atingida dentro do prazo."
    if s == "atrasada":
        return f"Neste cenário {cenario}, esta meta ficará atrasada."
    if s == "sem_prazo":
        return f"Neste cenário {cenario}, esta meta não tem prazo definido."
    return f"Neste cenário {cenario}, não sobra valor para esta meta."
