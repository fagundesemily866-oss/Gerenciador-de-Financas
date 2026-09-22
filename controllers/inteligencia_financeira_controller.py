"""
Controlador de Inteligência Financeira.
========================================

Centraliza os algoritmos avançados do sistema:
1. Previsão de gastos até o fim do mês (run-rate diário e comparação com limites)
2. Detecção de gastos fora do padrão (anomalias e desvios contra histórico por categoria)
3. Simulador financeiro "E se...?" (cenários hipotéticos em memória)
4. Insights automáticos para o Dashboard
5. Relatório mensal automático comparativo
"""
import calendar
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import math


def _parse_data(data_str: str) -> Optional[date]:
    """Converte datas nos formatos YYYY-MM-DD ou DD/MM/YYYY para objeto date."""
    if not data_str:
        return None
    data_str = str(data_str).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(data_str, fmt).date()
        except ValueError:
            pass
    return None


class InteligenciaFinanceiraController:
    """Motor de cálculo e inteligência analítica financeira."""

    NOME_MESES = [
        "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    # ------------------------------------------------------------------
    # 1. PREVISÃO DE GASTOS ATÉ O FIM DO MÊS
    # ------------------------------------------------------------------
    @classmethod
    def calcular_previsao_mes(
        cls,
        lancamentos: List[Dict[str, Any]],
        categorias: Optional[List[Dict[str, Any]]] = None,
        ano: Optional[int] = None,
        mes: Optional[int] = None,
        dia_referencia: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Analisa os gastos já ocorridos no mês e projeta o total até o último dia,
        comparando com o limite mensal de orçamento configurado.
        """
        hoje = date.today()
        ano = ano or hoje.year
        mes = mes or hoje.month

        _, dias_totais = calendar.monthrange(ano, mes)

        if dia_referencia is not None:
            dia_atual = max(1, min(dia_referencia, dias_totais))
        elif hoje.year == ano and hoje.month == mes:
            dia_atual = max(1, min(hoje.day, dias_totais))
        else:
            dia_atual = dias_totais

        dias_decorridos = dia_atual
        dias_restantes = max(0, dias_totais - dias_decorridos)

        # Filtrar lançamentos do mês
        despesas_mes = []
        receitas_mes = []
        for l in lancamentos:
            d = _parse_data(l.get("date") or l.get("data"))
            if d and d.year == ano and d.month == mes:
                val = float(l.get("value") or l.get("valor", 0))
                tipo = l.get("type") or l.get("tipo", "")
                if tipo == "Despesa":
                    despesas_mes.append({"valor": val, "categoria": l.get("category") or l.get("categoria", "Outros")})
                elif tipo == "Receita":
                    receitas_mes.append({"valor": val})

        gasto_atual = sum(d["valor"] for d in despesas_mes)
        receita_atual = sum(r["valor"] for r in receitas_mes)

        # Ritmo diário médio
        ritmo_diario = gasto_atual / dias_decorridos if dias_decorridos > 0 else 0.0

        # Projeção até o fim do mês
        projecao_fim_mes = gasto_atual + (ritmo_diario * dias_restantes)

        # Determinar Limite Mensal
        limite_total = 0.0
        limite_definido = False
        if categorias:
            for c in categorias:
                lim = float(c.get("limite_orcamento", 0) or 0.0)
                if lim > 0 and c.get("tipo") == "Despesa":
                    limite_total += lim
            if limite_total > 0:
                limite_definido = True

        # Se não há limite em categorias, usar a receita do mês como teto orçamentário referencial
        if not limite_definido and receita_atual > 0:
            limite_total = receita_atual
            limite_referencia_tipo = "renda"
        elif limite_definido:
            limite_referencia_tipo = "categorias"
        else:
            limite_referencia_tipo = "nenhum"

        # Comparação e Status
        diferenca_projetada = limite_total - projecao_fim_mes
        percentual_consumido = (gasto_atual / limite_total * 100) if limite_total > 0 else 0.0
        percentual_projetado = (projecao_fim_mes / limite_total * 100) if limite_total > 0 else 0.0

        # Ritmo diário recomendado para não estourar o limite
        if dias_restantes > 0 and limite_total > 0:
            saldo_disponivel_restante = max(0.0, limite_total - gasto_atual)
            ritmo_recomendado = saldo_disponivel_restante / dias_restantes
        else:
            ritmo_recomendado = 0.0

        if limite_total > 0:
            if projecao_fim_mes > limite_total:
                status = "estouro_previsto"
                estouro_valor = projecao_fim_mes - limite_total
                mensagem = f"Risco de estourar o orçamento em R$ {estouro_valor:,.2f} até o dia {dias_totais}."
            elif projecao_fim_mes > (limite_total * 0.85):
                status = "alerta_limite"
                mensagem = f"Atenção: previsão de fechar em {percentual_projetado:.0f}% do limite estipulado."
            else:
                status = "dentro_do_limite"
                sobra = limite_total - projecao_fim_mes
                mensagem = f"Excelente! Projeção de fechar o mês com folga de R$ {sobra:,.2f}."
        else:
            status = "sem_limite"
            mensagem = f"Projeção estimada de R$ {projecao_fim_mes:,.2f} em despesas até o fim do mês."

        return {
            "ano": ano,
            "mes": mes,
            "nome_mes": cls.NOME_MESES[mes],
            "dias_totais": dias_totais,
            "dias_decorridos": dias_decorridos,
            "dias_restantes": dias_restantes,
            "gasto_atual": gasto_atual,
            "receita_atual": receita_atual,
            "ritmo_diario": ritmo_diario,
            "projecao_fim_mes": projecao_fim_mes,
            "limite_total": limite_total,
            "limite_definido": limite_definido,
            "limite_referencia_tipo": limite_referencia_tipo,
            "diferenca_projetada": diferenca_projetada,
            "percentual_consumido": min(100.0, percentual_consumido),
            "percentual_projetado": percentual_projetado,
            "ritmo_recomendado": ritmo_recomendado,
            "status": status,
            "mensagem": mensagem,
        }

    # ------------------------------------------------------------------
    # 2. DETECÇÃO DE GASTOS FORA DO PADRÃO
    # ------------------------------------------------------------------
    @classmethod
    def detectar_gastos_fora_padrao(
        cls,
        lancamentos: List[Dict[str, Any]],
        categorias: Optional[List[Dict[str, Any]]] = None,
        ano: Optional[int] = None,
        mes: Optional[int] = None,
        threshold: float = 0.25,
    ) -> List[Dict[str, Any]]:
        """
        Compara os gastos do mês analisado contra os meses anteriores por categoria.
        Detecta aumentos ou reduções expressivas (ex: >= 25%).
        """
        hoje = date.today()
        ano = ano or hoje.year
        mes = mes or hoje.month
        chave_atual = f"{ano:04d}-{mes:02d}"

        # Mapear gastos por (ano_mes, categoria)
        gastos_por_mes_cat: Dict[str, Dict[str, float]] = {}
        for l in lancamentos:
            tipo = l.get("type") or l.get("tipo", "")
            if tipo != "Despesa":
                continue
            d = _parse_data(l.get("date") or l.get("data"))
            if not d:
                continue
            k = f"{d.year:04d}-{d.month:02d}"
            cat = (l.get("category") or l.get("categoria") or "Outros").strip()
            val = float(l.get("value") or l.get("valor", 0))

            if k not in gastos_por_mes_cat:
                gastos_por_mes_cat[k] = {}
            gastos_por_mes_cat[k][cat] = gastos_por_mes_cat[k].get(cat, 0.0) + val

        gastos_atuais = gastos_por_mes_cat.get(chave_atual, {})
        meses_anteriores = sorted([k for k in gastos_por_mes_cat.keys() if k < chave_atual])

        anomalias = []

        # Mapear limites de orçamento das categorias
        mapa_limites = {}
        if categorias:
            for c in categorias:
                cat_nome = c.get("nome", "").strip()
                lim = float(c.get("limite_orcamento", 0) or 0.0)
                if lim > 0:
                    mapa_limites[cat_nome] = lim

        if meses_anteriores:
            # Temos histórico de meses anteriores para comparação robusta
            for cat, gasto_atual in gastos_atuais.items():
                valores_anteriores = [
                    gastos_por_mes_cat[m].get(cat, 0.0) for m in meses_anteriores
                ]
                # Considerar apenas meses onde a categoria existiu ou média geral dos meses
                valores_positivos = [v for v in valores_anteriores if v > 0]
                if valores_positivos:
                    media_anterior = sum(valores_positivos) / len(valores_positivos)
                else:
                    media_anterior = 0.0

                if media_anterior > 0:
                    variacao_pct = ((gasto_atual - media_anterior) / media_anterior) * 100
                    diferenca_abs = gasto_atual - media_anterior

                    if variacao_pct >= (threshold * 100):
                        anomalias.append({
                            "categoria": cat,
                            "tipo": "aumento_expressivo",
                            "badge": "Subiu Muito",
                            "cor": "#F38BA8",
                            "icone": "📈",
                            "variacao_pct": variacao_pct,
                            "gasto_atual": gasto_atual,
                            "media_anterior": media_anterior,
                            "diferenca": diferenca_abs,
                            "mensagem": f"'{cat}' aumentou {variacao_pct:.0f}% em relação à média dos últimos meses (R$ {gasto_atual:,.2f} vs R$ {media_anterior:,.2f}).",
                        })
                    elif variacao_pct <= -(threshold * 100):
                        anomalias.append({
                            "categoria": cat,
                            "tipo": "reducao_expressiva",
                            "badge": "Ótima Economia",
                            "cor": "#A6E3A1",
                            "icone": "📉",
                            "variacao_pct": variacao_pct,
                            "gasto_atual": gasto_atual,
                            "media_anterior": media_anterior,
                            "diferenca": diferenca_abs,
                            "mensagem": f"'{cat}' caiu {abs(variacao_pct):.0f}% em relação à média anterior (R$ {gasto_atual:,.2f} vs R$ {media_anterior:,.2f}).",
                        })
                elif gasto_atual > 0 and cat in mapa_limites:
                    lim = mapa_limites[cat]
                    if gasto_atual > lim:
                        anomalias.append({
                            "categoria": cat,
                            "tipo": "limite_excedido",
                            "badge": "Limite Estourado",
                            "cor": "#F38BA8",
                            "icone": "⚠️",
                            "variacao_pct": ((gasto_atual - lim) / lim) * 100,
                            "gasto_atual": gasto_atual,
                            "media_anterior": lim,
                            "diferenca": gasto_atual - lim,
                            "mensagem": f"'{cat}' ultrapassou o teto definido de R$ {lim:,.2f} (Total gasto: R$ {gasto_atual:,.2f}).",
                        })
        else:
            # Sem meses anteriores: verificar contra limites cadastrados ou concentração excessiva
            total_despesas_mes = sum(gastos_atuais.values())
            for cat, gasto_atual in gastos_atuais.items():
                if cat in mapa_limites:
                    lim = mapa_limites[cat]
                    if gasto_atual > lim:
                        anomalias.append({
                            "categoria": cat,
                            "tipo": "limite_excedido",
                            "badge": "Limite Estourado",
                            "cor": "#F38BA8",
                            "icone": "⚠️",
                            "variacao_pct": ((gasto_atual - lim) / lim) * 100,
                            "gasto_atual": gasto_atual,
                            "media_anterior": lim,
                            "diferenca": gasto_atual - lim,
                            "mensagem": f"'{cat}' ultrapassou o teto de R$ {lim:,.2f} (atual: R$ {gasto_atual:,.2f}).",
                        })
                elif total_despesas_mes > 0 and (gasto_atual / total_despesas_mes) >= 0.40:
                    pct = (gasto_atual / total_despesas_mes) * 100
                    anomalias.append({
                        "categoria": cat,
                        "tipo": "concentracao_alta",
                        "badge": "Alta Concentração",
                        "cor": "#F9E2AF",
                        "icone": "⚠️",
                        "variacao_pct": pct,
                        "gasto_atual": gasto_atual,
                        "media_anterior": total_despesas_mes / max(1, len(gastos_atuais)),
                        "diferenca": 0.0,
                        "mensagem": f"'{cat}' concentra {pct:.0f}% de todos os seus gastos deste mês (R$ {gasto_atual:,.2f}).",
                    })

        # Ordenar: maiores desvios primeiro
        anomalias.sort(key=lambda x: abs(x["variacao_pct"]), reverse=True)
        return anomalias

    # ------------------------------------------------------------------
    # 3. INSIGHTS AUTOMÁTICOS NO DASHBOARD
    # ------------------------------------------------------------------
    @classmethod
    def gerar_insights_dashboard(
        cls,
        lancamentos: List[Dict[str, Any]],
        categorias: Optional[List[Dict[str, Any]]] = None,
        metas: Optional[List[Dict[str, Any]]] = None,
        ano: Optional[int] = None,
        mes: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Gera cards de avisos inteligentes e contextualizados para a tela inicial/Dashboard:
        - Maior categoria de gastos e %
        - Economia vs mês anterior
        - Proximidade de limites de categorias
        - Anomalias de gastos fora do padrão
        - Potencial de aceleração de metas
        """
        hoje = date.today()
        ano = ano or hoje.year
        mes = mes or hoje.month

        insights = []

        if not lancamentos:
            return [{
                "tipo": "info",
                "icone": "💡",
                "titulo": "Comece Registrando",
                "mensagem": "Adicione suas receitas e despesas para liberar previsões inteligentes e alertas de orçamento.",
                "cor": "#89B4FA",
            }]

        # 1. Previsão e Ritmo
        previsao = cls.calcular_previsao_mes(lancamentos, categorias, ano, mes)
        if previsao["gasto_atual"] > 0:
            if previsao["status"] == "estouro_previsto":
                insights.append({
                    "tipo": "alerta",
                    "icone": "⚠️",
                    "titulo": "Risco de Estouro de Orçamento",
                    "mensagem": f"Ao ritmo de R$ {previsao['ritmo_diario']:,.2f}/dia, você fechará em R$ {previsao['projecao_fim_mes']:,.2f} ({previsao['mensagem']}). Meta diária sugerida: R$ {previsao['ritmo_recomendado']:,.2f}/dia.",
                    "cor": "#F38BA8",
                })
            elif previsao["status"] == "dentro_do_limite" and previsao["limite_total"] > 0:
                insights.append({
                    "tipo": "positivo",
                    "icone": "✨",
                    "titulo": "Previsão Favorável",
                    "mensagem": f"Gastos sob controle! Previsão de R$ {previsao['projecao_fim_mes']:,.2f} no fim do mês ({previsao['percentual_projetado']:.0f}% do orçamento).",
                    "cor": "#A6E3A1",
                })

        # 2. Despesas por categoria no mês atual
        despesas_cat: Dict[str, float] = {}
        total_desp_mes = 0.0
        for l in lancamentos:
            d = _parse_data(l.get("date") or l.get("data"))
            if d and d.year == ano and d.month == mes and (l.get("type") or l.get("tipo")) == "Despesa":
                val = float(l.get("value") or l.get("valor", 0))
                c = (l.get("category") or l.get("categoria") or "Outros").strip()
                despesas_cat[c] = despesas_cat.get(c, 0.0) + val
                total_desp_mes += val

        # 3. Top Categoria de Gasto
        if despesas_cat and total_desp_mes > 0:
            top_cat = max(despesas_cat, key=despesas_cat.get)
            top_val = despesas_cat[top_cat]
            top_pct = (top_val / total_desp_mes) * 100
            insights.append({
                "tipo": "info",
                "icone": "🏷️",
                "titulo": f"Maior Centro de Custo: {top_cat}",
                "mensagem": f"A categoria '{top_cat}' consumiu R$ {top_val:,.2f}, representando {top_pct:.1f}% do seu total de despesas deste mês.",
                "cor": "#89B4FA",
            })

        # 4. Detecção de Gastos Fora do Padrão (incorporar as 2 principais anomalias)
        anomalias = cls.detectar_gastos_fora_padrao(lancamentos, categorias, ano, mes)
        for anom in anomalias[:2]:
            insights.append({
                "tipo": "alerta" if anom["cor"] == "#F38BA8" else "positivo",
                "icone": anom["icone"],
                "titulo": f"Gasto Fora do Padrão: {anom['categoria']}",
                "mensagem": anom["mensagem"],
                "cor": anom["cor"],
            })

        # 5. Proximidade de Limite de Categoria
        if categorias and despesas_cat:
            for c in categorias:
                cat_nome = c.get("nome", "").strip()
                lim = float(c.get("limite_orcamento", 0) or 0.0)
                if lim > 0 and cat_nome in despesas_cat:
                    gasto_cat = despesas_cat[cat_nome]
                    pct = (gasto_cat / lim) * 100
                    if 80.0 <= pct <= 100.0:
                        insights.append({
                            "tipo": "atencao",
                            "icone": "⚡",
                            "titulo": f"Limite Próximo: {cat_nome}",
                            "mensagem": f"Você já utilizou {pct:.0f}% do teto de {cat_nome} (R$ {gasto_cat:,.2f} de R$ {lim:,.2f}). Restam R$ {lim - gasto_cat:,.2f}.",
                            "cor": "#F9E2AF",
                        })

        # 6. Comparação com o Mês Anterior (Economia / Saldo)
        mes_ant = 12 if mes == 1 else mes - 1
        ano_ant = ano - 1 if mes == 1 else ano
        rec_ant = sum(
            float(l.get("value") or l.get("valor", 0))
            for l in lancamentos
            if _parse_data(l.get("date") or l.get("data")) and _parse_data(l.get("date") or l.get("data")).year == ano_ant and _parse_data(l.get("date") or l.get("data")).month == mes_ant and (l.get("type") or l.get("tipo")) == "Receita"
        )
        desp_ant = sum(
            float(l.get("value") or l.get("valor", 0))
            for l in lancamentos
            if _parse_data(l.get("date") or l.get("data")) and _parse_data(l.get("date") or l.get("data")).year == ano_ant and _parse_data(l.get("date") or l.get("data")).month == mes_ant and (l.get("type") or l.get("tipo")) == "Despesa"
        )
        if desp_ant > 0 and total_desp_mes > 0:
            diff_desp = total_desp_mes - desp_ant
            var_pct = (diff_desp / desp_ant) * 100
            if diff_desp < 0:
                insights.append({
                    "tipo": "positivo",
                    "icone": "🌱",
                    "titulo": "Economia em Relação ao Mês Anterior",
                    "mensagem": f"Suas despesas estão R$ {abs(diff_desp):,.2f} menores ({abs(var_pct):.0f}% a menos) em relação ao mesmo período de {cls.NOME_MESES[mes_ant]}.",
                    "cor": "#A6E3A1",
                })
            elif diff_desp > 0 and var_pct > 15:
                insights.append({
                    "tipo": "atencao",
                    "icone": "📊",
                    "titulo": "Despesas Acima do Mês Passado",
                    "mensagem": f"Você gastou R$ {diff_desp:,.2f} a mais (+{var_pct:.0f}%) em comparação a {cls.NOME_MESES[mes_ant]}.",
                    "cor": "#F9E2AF",
                })

        # 7. Impacto em Metas
        if metas:
            saldo_mes = previsao["receita_atual"] - previsao["gasto_atual"]
            metas_em_aberto = [m for m in metas if float(m.get("valor_atual", 0) or 0) < float(m.get("valor_alvo", 0) or 0)]
            if saldo_mes > 100 and metas_em_aberto:
                m_top = metas_em_aberto[0]
                falta = float(m_top.get("valor_alvo", 0)) - float(m_top.get("valor_atual", 0))
                insights.append({
                    "tipo": "info",
                    "icone": "🎯",
                    "titulo": "Aceleração de Metas",
                    "mensagem": f"Com seu saldo positivo atual de R$ {saldo_mes:,.2f}, você pode antecipar sua meta '{m_top.get('descricao', 'Principal')}' (restam R$ {falta:,.2f}).",
                    "cor": "#CBA6F7",
                })

        return insights

    # ------------------------------------------------------------------
    # 4. SIMULADOR FINANCEIRO "E SE...?"
    # ------------------------------------------------------------------
    @classmethod
    def calcular_simulacao(
        cls,
        lancamentos: List[Dict[str, Any]],
        metas: Optional[List[Dict[str, Any]]] = None,
        categorias: Optional[List[Dict[str, Any]]] = None,
        reducao_despesas_pct: float = 0.0,
        categoria_alvo: Optional[str] = None,
        aumento_renda_valor: float = 0.0,
        aporte_extra_metas: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Executa simulações 'E se...?' sem alterar nenhum dado no banco:
        - E se eu reduzir X% em Alimentação ou despesas gerais?
        - E se minha renda aumentar R$ Y?
        - E se eu guardar R$ Z todo mês para metas?
        Mostra novo saldo mensal, economia anual e tempo reduzido para metas.
        """
        hoje = date.today()
        # Usar o mês corrente ou último mês disponível com dados
        meses_disp = cls.obter_meses_disponiveis(lancamentos)
        if meses_disp:
            ano_base = meses_disp[0]["ano"]
            mes_base = meses_disp[0]["mes"]
        else:
            ano_base = hoje.year
            mes_base = hoje.month

        # Agrupar lançamentos do mês base
        despesas_base_cat: Dict[str, float] = {}
        total_rec_base = 0.0
        for l in lancamentos:
            d = _parse_data(l.get("date") or l.get("data"))
            if d and d.year == ano_base and d.month == mes_base:
                val = float(l.get("value") or l.get("valor", 0))
                tipo = l.get("type") or l.get("tipo", "")
                if tipo == "Receita":
                    total_rec_base += val
                elif tipo == "Despesa":
                    c = (l.get("category") or l.get("categoria") or "Outros").strip()
                    despesas_base_cat[c] = despesas_base_cat.get(c, 0.0) + val

        # Se não há dados no mês base, usar defaults para simulação interativa
        if total_rec_base == 0.0 and sum(despesas_base_cat.values()) == 0.0:
            total_rec_base = 3500.0
            despesas_base_cat = {
                "Moradia": 1200.0,
                "Alimentação": 900.0,
                "Transporte": 450.0,
                "Lazer": 300.0,
                "Outros": 250.0,
            }

        total_desp_base = sum(despesas_base_cat.values())
        saldo_base = total_rec_base - total_desp_base

        # --- APLICAR CENÁRIO SIMULADO ---
        despesas_simuladas_cat: Dict[str, float] = {}
        fator_reducao = max(0.0, min(1.0, reducao_despesas_pct / 100.0))

        if categoria_alvo and categoria_alvo not in ("Todas as Despesas", "Todas"):
            # Reduz apenas a categoria selecionada
            for cat, val in despesas_base_cat.items():
                if cat.lower() == categoria_alvo.lower():
                    despesas_simuladas_cat[cat] = val * (1.0 - fator_reducao)
                else:
                    despesas_simuladas_cat[cat] = val
        else:
            # Reduz todas as despesas
            for cat, val in despesas_base_cat.items():
                despesas_simuladas_cat[cat] = val * (1.0 - fator_reducao)

        total_desp_simulada = sum(despesas_simuladas_cat.values())
        total_rec_simulada = total_rec_base + max(0.0, float(aumento_renda_valor))
        saldo_simulado = total_rec_simulada - total_desp_simulada

        economia_mensal_adicional = saldo_simulado - saldo_base
        economia_anual_projetada = economia_mensal_adicional * 12.0

        # Impacto nas Metas Financeiras
        impacto_metas = []
        if metas:
            capacidade_poupanca_base = max(50.0, saldo_base) if saldo_base > 0 else 50.0
            capacidade_poupanca_simulada = max(
                capacidade_poupanca_base,
                capacidade_poupanca_base + economia_mensal_adicional + float(aporte_extra_metas)
            )

            for m in metas:
                alvo = float(m.get("valor_alvo", 0) or 0)
                atual = float(m.get("valor_atual", 0) or 0)
                restante = max(0.0, alvo - atual)
                if restante > 0:
                    meses_base = math.ceil(restante / capacidade_poupanca_base)
                    meses_simulados = math.ceil(restante / capacidade_poupanca_simulada)
                    meses_economizados = max(0, meses_base - meses_simulados)
                    impacto_metas.append({
                        "descricao": m.get("descricao", "Meta"),
                        "valor_alvo": alvo,
                        "valor_atual": atual,
                        "restante": restante,
                        "meses_cenario_atual": meses_base,
                        "meses_cenario_simulado": meses_simulados,
                        "meses_economizados": meses_economizados,
                    })

        return {
            "mes_referencia": f"{cls.NOME_MESES[mes_base]} / {ano_base}",
            "cenario_base": {
                "receitas": total_rec_base,
                "despesas": total_desp_base,
                "saldo": saldo_base,
                "economia_anual": saldo_base * 12.0 if saldo_base > 0 else 0.0,
            },
            "cenario_simulado": {
                "receitas": total_rec_simulada,
                "despesas": total_desp_simulada,
                "saldo": saldo_simulado,
                "economia_anual": saldo_simulado * 12.0 if saldo_simulado > 0 else 0.0,
            },
            "diferenca": {
                "economia_mensal": economia_mensal_adicional,
                "economia_anual": economia_anual_projetada,
                "reducao_despesas_valor": total_desp_base - total_desp_simulada,
                "aumento_renda_valor": float(aumento_renda_valor),
            },
            "despesas_por_cat_base": despesas_base_cat,
            "despesas_por_cat_simulada": despesas_simuladas_cat,
            "impacto_metas": impacto_metas,
        }

    # ------------------------------------------------------------------
    # 4.1. PROJEÇÃO TEMPORAL AVANÇADA (3, 6, 12, 24 MESES)
    # ------------------------------------------------------------------
    @classmethod
    def projetar_futuro_financeiro(
        cls,
        lancamentos: List[Dict[str, Any]],
        metas: Optional[List[Dict[str, Any]]] = None,
        categorias: Optional[List[Dict[str, Any]]] = None,
        meses_horizonte: int = 12,
        reducao_despesas_pct: float = 0.0,
        categoria_alvo: Optional[str] = None,
        aumento_renda_valor: float = 0.0,
        aporte_extra_metas: float = 0.0,
        eventos: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Projeta o fluxo financeiro mês a mês para o horizonte especificado (3, 6, 12 ou 24 meses),
        considerando cortes de gastos, novos rendimentos, metas e eventos inesperados.
        """
        meses_horizonte = max(3, min(36, int(meses_horizonte)))
        hoje = date.today()

        # Obter médias base mensais do histórico ou usar defaults realistas
        meses_disp = cls.obter_meses_disponiveis(lancamentos)
        if meses_disp:
            ano_base = meses_disp[0]["ano"]
            mes_base = meses_disp[0]["mes"]
        else:
            ano_base = hoje.year
            mes_base = hoje.month

        total_rec_base = 0.0
        despesas_base_cat: Dict[str, float] = {}
        for l in lancamentos:
            d = _parse_data(l.get("date") or l.get("data"))
            if d and d.year == ano_base and d.month == mes_base:
                val = float(l.get("value") or l.get("valor", 0))
                tipo = l.get("type") or l.get("tipo", "")
                if tipo == "Receita":
                    total_rec_base += val
                elif tipo == "Despesa":
                    c = (l.get("category") or l.get("categoria") or "Outros").strip()
                    despesas_base_cat[c] = despesas_base_cat.get(c, 0.0) + val

        if total_rec_base == 0.0 and sum(despesas_base_cat.values()) == 0.0:
            total_rec_base = 3800.0
            despesas_base_cat = {
                "Moradia": 1300.0,
                "Alimentação": 950.0,
                "Transporte": 480.0,
                "Lazer": 320.0,
                "Saúde": 250.0,
                "Outros": 200.0,
            }

        total_desp_base = sum(despesas_base_cat.values())
        saldo_base_mensal = total_rec_base - total_desp_base

        # Aplicar corte de gastos simulado
        fator_reducao = max(0.0, min(0.9, reducao_despesas_pct / 100.0))
        despesas_sim_ajustadas = {}
        if categoria_alvo and categoria_alvo not in ("Todas as Despesas", "Todas"):
            for cat, val in despesas_base_cat.items():
                if cat.lower() == categoria_alvo.lower():
                    despesas_sim_ajustadas[cat] = val * (1.0 - fator_reducao)
                else:
                    despesas_sim_ajustadas[cat] = val
        else:
            for cat, val in despesas_base_cat.items():
                despesas_sim_ajustadas[cat] = val * (1.0 - fator_reducao)

        total_desp_sim_padrao = sum(despesas_sim_ajustadas.values())
        total_rec_sim_padrao = total_rec_base + max(0.0, float(aumento_renda_valor))

        # Saldo inicial real acumulado (soma de todas as receitas - despesas históricas)
        saldo_inicial_real = 0.0
        for l in lancamentos:
            val = float(l.get("value") or l.get("valor", 0))
            if (l.get("type") or l.get("tipo")) == "Receita":
                saldo_inicial_real += val
            else:
                saldo_inicial_real -= val

        # Garantir piso razoável para o saldo inicial na simulação
        saldo_inicial_acumulado = max(0.0, saldo_inicial_real)

        # Tratar eventos inesperados
        eventos_lista = eventos or []

        # Gerar projeção mês a mês
        meses_projecao = []
        saldo_acumulado_base = saldo_inicial_acumulado
        saldo_acumulado_sim = saldo_inicial_acumulado
        economia_acumulada_total = 0.0

        # Metas para acompanhar
        metas_copia = []
        if metas:
            for m in metas:
                metas_copia.append({
                    "id": m.get("id"),
                    "descricao": m.get("descricao", "Meta"),
                    "valor_alvo": float(m.get("valor_alvo", 0) or 0),
                    "valor_atual": float(m.get("valor_atual", 0) or 0),
                    "valor_simulado": float(m.get("valor_atual", 0) or 0),
                    "mes_conclusao": None,
                })

        for i in range(1, meses_horizonte + 1):
            # Calcular mês e ano de calendário
            mes_cal = (mes_base + i - 1) % 12 + 1
            ano_cal = ano_base + (mes_base + i - 1) // 12
            nome_mes_curto = cls.NOME_MESES[mes_cal][:3]
            rotulo_mes = f"{nome_mes_curto}/{str(ano_cal)[2:]}"

            # Eventos aplicáveis a este mês
            eventos_do_mes = []
            impacto_rec_eventos = 0.0
            impacto_desp_eventos = 0.0

            for ev in eventos_lista:
                mes_inicio = int(ev.get("mes_inicio", 1))
                tipo_ev = ev.get("tipo", "unico").lower()  # 'unico' ou 'recorrente'
                natureza = ev.get("natureza", "despesa").lower()  # 'receita' ou 'despesa'
                val_ev = float(ev.get("valor", 0.0))

                se_aplica = False
                if tipo_ev == "unico" and mes_inicio == i:
                    se_aplica = True
                elif tipo_ev == "recorrente" and i >= mes_inicio:
                    se_aplica = True

                if se_aplica:
                    eventos_do_mes.append(ev)
                    if natureza == "receita":
                        impacto_rec_eventos += val_ev
                    else:
                        impacto_desp_eventos += val_ev

            # Valores do mês
            rec_base_m = total_rec_base
            desp_base_m = total_desp_base
            saldo_base_m = rec_base_m - desp_base_m
            saldo_acumulado_base += saldo_base_m

            rec_sim_m = total_rec_sim_padrao + impacto_rec_eventos
            desp_sim_m = total_desp_sim_padrao + impacto_desp_eventos
            saldo_sim_m = rec_sim_m - desp_sim_m
            saldo_acumulado_sim += saldo_sim_m

            economia_m = saldo_sim_m - saldo_base_m
            economia_acumulada_total += economia_m

            # Evolução das Metas neste mês
            aporte_metas_mes = max(0.0, float(aporte_extra_metas))
            if saldo_sim_m > 0 and not aporte_metas_mes:
                # Se não especificou aporte fixo, usa 30% do saldo positivo para metas
                aporte_metas_mes = saldo_sim_m * 0.3

            for m in metas_copia:
                if m["valor_simulado"] < m["valor_alvo"] and aporte_metas_mes > 0:
                    aporte_aplicado = min(aporte_metas_mes, m["valor_alvo"] - m["valor_simulado"])
                    m["valor_simulado"] += aporte_aplicado
                    aporte_metas_mes -= aporte_aplicado
                    if m["valor_simulado"] >= m["valor_alvo"] and m["mes_conclusao"] is None:
                        m["mes_conclusao"] = rotulo_mes

            meses_projecao.append({
                "numero_mes": i,
                "rotulo_mes": rotulo_mes,
                "mes_calendario": mes_cal,
                "ano_calendario": ano_cal,
                "receitas_base": rec_base_m,
                "despesas_base": desp_base_m,
                "saldo_base": saldo_base_m,
                "saldo_acumulado_base": saldo_acumulado_base,
                "receitas_simulado": rec_sim_m,
                "despesas_simulado": desp_sim_m,
                "saldo_simulado": saldo_sim_m,
                "saldo_acumulado_simulado": saldo_acumulado_sim,
                "economia_mensal": economia_m,
                "economia_acumulada": economia_acumulada_total,
                "eventos_mes": eventos_do_mes,
                "impacto_eventos_receitas": impacto_rec_eventos,
                "impacto_eventos_despesas": impacto_desp_eventos,
            })

        # Cenários Otimista, Normal e Pessimista
        cenarios = cls.calcular_cenarios_multiplos(
            meses_projecao,
            saldo_inicial=saldo_inicial_acumulado
        )

        # Previsão inteligente de metas
        previsao_metas = cls.calcular_previsao_inteligente_metas(
            metas=metas,
            capacidade_poupanca_base=max(50.0, saldo_base_mensal),
            capacidade_poupanca_simulada=max(50.0, (total_rec_sim_padrao - total_desp_sim_padrao) + float(aporte_extra_metas)),
            ano_inicio=ano_base,
            mes_inicio=mes_base,
        )

        # Totais consolidados do período
        total_rec_periodo = sum(m["receitas_simulado"] for m in meses_projecao)
        total_desp_periodo = sum(m["despesas_simulado"] for m in meses_projecao)
        total_economizado_periodo = sum(m["economia_mensal"] for m in meses_projecao)

        return {
            "horizonte_meses": meses_horizonte,
            "mes_inicial": f"{cls.NOME_MESES[mes_base]} / {ano_base}",
            "saldo_inicial": saldo_inicial_acumulado,
            "meses": meses_projecao,
            "cenarios": cenarios,
            "metas": previsao_metas,
            "resumo": {
                "saldo_final_projetado": saldo_acumulado_sim,
                "saldo_final_base": saldo_acumulado_base,
                "diferenca_saldo_final": saldo_acumulado_sim - saldo_acumulado_base,
                "total_receitas_periodo": total_rec_periodo,
                "total_despesas_periodo": total_desp_periodo,
                "total_economizado_periodo": total_economizado_periodo,
                "media_mensal_saldo": (total_rec_periodo - total_desp_periodo) / meses_horizonte,
            }
        }

    # ------------------------------------------------------------------
    # 4.2. CENÁRIOS OTIMISTA, NORMAL E PESSIMISTA
    # ------------------------------------------------------------------
    @classmethod
    def calcular_cenarios_multiplos(
        cls,
        meses_projecao: List[Dict[str, Any]],
        saldo_inicial: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Gera 3 cenários simultâneos (Normal, Otimista e Pessimista) a partir da projeção base:
        - Otimista: +10% em receitas e -5% em despesas.
        - Pessimista: -10% em receitas e +15% em despesas.
        """
        saldo_acum_normal = saldo_inicial
        saldo_acum_otimista = saldo_inicial
        saldo_acum_pessimista = saldo_inicial

        pontos_normal = []
        pontos_otimista = []
        pontos_pessimista = []

        for m in meses_projecao:
            rec = m["receitas_simulado"]
            desp = m["despesas_simulado"]

            # Normal
            saldo_norm = rec - desp
            saldo_acum_normal += saldo_norm
            pontos_normal.append(saldo_acum_normal)

            # Otimista (+10% rec, -5% desp)
            rec_otim = rec * 1.10
            desp_otim = desp * 0.95
            saldo_otim = rec_otim - desp_otim
            saldo_acum_otimista += saldo_otim
            pontos_otimista.append(saldo_acum_otimista)

            # Pessimista (-10% rec, +15% desp)
            rec_pess = rec * 0.90
            desp_pess = desp * 1.15
            saldo_pess = rec_pess - desp_pess
            saldo_acum_pessimista += saldo_pess
            pontos_pessimista.append(saldo_acum_pessimista)

        return {
            "normal": {
                "saldo_final": saldo_acum_normal,
                "evolucao": pontos_normal,
                "descricao": "Cenário planejado com base nas taxas e cortes configurados.",
            },
            "otimista": {
                "saldo_final": saldo_acum_otimista,
                "evolucao": pontos_otimista,
                "descricao": "Receitas +10% maiores e despesas -5% menores (renda extra, estabilidade).",
            },
            "pessimista": {
                "saldo_final": saldo_acum_pessimista,
                "evolucao": pontos_pessimista,
                "descricao": "Receitas -10% menores e despesas +15% maiores (imprevistos, inflação).",
            }
        }

    # ------------------------------------------------------------------
    # 4.3. PREVISÃO INTELIGENTE DE METAS
    # ------------------------------------------------------------------
    @classmethod
    def calcular_previsao_inteligente_metas(
        cls,
        metas: Optional[List[Dict[str, Any]]],
        capacidade_poupanca_base: float,
        capacidade_poupanca_simulada: float,
        ano_inicio: int,
        mes_inicio: int,
    ) -> List[Dict[str, Any]]:
        """
        Calcula com inteligência o mês e ano exato estimado para atingimento de cada meta.
        """
        if not metas:
            return []

        resultado = []
        poup_base = max(30.0, capacidade_poupanca_base)
        poup_sim = max(30.0, capacidade_poupanca_simulada)

        for m in metas:
            alvo = float(m.get("valor_alvo", 0) or 0)
            atual = float(m.get("valor_atual", 0) or 0)
            restante = max(0.0, alvo - atual)

            if restante <= 0:
                resultado.append({
                    "id": m.get("id"),
                    "descricao": m.get("descricao", "Meta"),
                    "valor_alvo": alvo,
                    "valor_atual": atual,
                    "concluida": True,
                    "meses_restantes_simulado": 0,
                    "data_estimada": "Já alcançada!",
                    "meses_economizados": 0,
                })
                continue

            meses_base = math.ceil(restante / poup_base)
            meses_sim = math.ceil(restante / poup_sim)
            meses_economizados = max(0, meses_base - meses_sim)

            # Data projetada (mês/ano)
            mes_fim_sim = (mes_inicio + meses_sim - 1) % 12 + 1
            ano_fim_sim = ano_inicio + (mes_inicio + meses_sim - 1) // 12
            nome_mes_extenso = cls.NOME_MESES[mes_fim_sim]
            data_estimada = f"{nome_mes_extenso} de {ano_fim_sim}"

            mes_fim_base = (mes_inicio + meses_base - 1) % 12 + 1
            ano_fim_base = ano_inicio + (mes_inicio + meses_base - 1) // 12
            data_base = f"{cls.NOME_MESES[mes_fim_base]} de {ano_fim_base}"

            resultado.append({
                "id": m.get("id"),
                "descricao": m.get("descricao", "Meta"),
                "valor_alvo": alvo,
                "valor_atual": atual,
                "restante": restante,
                "concluida": False,
                "meses_restantes_base": meses_base,
                "meses_restantes_simulado": meses_sim,
                "meses_economizados": meses_economizados,
                "data_estimada_simulada": data_estimada,
                "data_estimada_base": data_base,
            })

        return resultado

    # ------------------------------------------------------------------
    # 4.4. COMPARADOR DE DECISÕES FINANCEIRAS (CENÁRIOS A, B, C)
    # ------------------------------------------------------------------
    @classmethod
    def comparar_decisoes_financeiras(
        cls,
        lancamentos: List[Dict[str, Any]],
        metas: Optional[List[Dict[str, Any]]],
        decisao_a: Dict[str, Any],
        decisao_b: Dict[str, Any],
        decisao_c: Dict[str, Any],
        meses_horizonte: int = 12,
    ) -> Dict[str, Any]:
        """
        Compara lado a lado até 3 decisões financeiras distintas (ex: Comprar Parcelado vs Guardar vs Quitar Meta).
        Cada decisão pode especificar:
        - nome: str
        - descricao: str
        - gasto_inicial: float
        - parcela_mensal: float (despesa extra nos meses seguintes)
        - aumento_renda: float
        - aporte_metas: float
        - corte_despesas_pct: float
        """
        def _simular_uma_decisao(dec: Dict[str, Any]) -> Dict[str, Any]:
            eventos_decisao = []
            gasto_ini = float(dec.get("gasto_inicial", 0.0))
            if gasto_ini > 0:
                eventos_decisao.append({
                    "descricao": f"Gasto Inicial ({dec.get('nome', 'Decisão')})",
                    "valor": gasto_ini,
                    "mes_inicio": 1,
                    "tipo": "unico",
                    "natureza": "despesa",
                })

            parcela = float(dec.get("parcela_mensal", 0.0))
            if parcela > 0:
                eventos_decisao.append({
                    "descricao": f"Parcelas ({dec.get('nome', 'Decisão')})",
                    "valor": parcela,
                    "mes_inicio": 1,
                    "tipo": "recorrente",
                    "natureza": "despesa",
                })

            proj = cls.projetar_futuro_financeiro(
                lancamentos=lancamentos,
                metas=metas,
                meses_horizonte=meses_horizonte,
                reducao_despesas_pct=float(dec.get("corte_despesas_pct", 0.0)),
                aumento_renda_valor=float(dec.get("aumento_renda", 0.0)),
                aporte_extra_metas=float(dec.get("aporte_metas", 0.0)),
                eventos=eventos_decisao,
            )

            resumo = proj["resumo"]
            metas_proj = proj["metas"]
            metas_concluidas = sum(1 for m in metas_proj if m.get("meses_restantes_simulado", 999) <= meses_horizonte)

            return {
                "nome": dec.get("nome", "Opção"),
                "descricao": dec.get("descricao", ""),
                "saldo_final": resumo["saldo_final_projetado"],
                "total_gasto": resumo["total_despesas_periodo"],
                "total_economizado": resumo["total_economizado_periodo"],
                "metas_concluidas": metas_concluidas,
                "projecao_resumo": proj,
            }

        res_a = _simular_uma_decisao(decisao_a)
        res_b = _simular_uma_decisao(decisao_b)
        res_c = _simular_uma_decisao(decisao_c)

        # Identificar melhor decisão para saldo e melhor para metas
        todas = [res_a, res_b, res_c]
        melhor_saldo = max(todas, key=lambda x: x["saldo_final"])
        melhor_metas = max(todas, key=lambda x: x["metas_concluidas"])

        return {
            "decisao_a": res_a,
            "decisao_b": res_b,
            "decisao_c": res_c,
            "veredito": {
                "campea_saldo": melhor_saldo["nome"],
                "campea_metas": melhor_metas["nome"],
            }
        }

    # ------------------------------------------------------------------
    # 4.5. MAPA DE CONSEQUÊNCIAS FINANCEIRAS EM CASCATA
    # ------------------------------------------------------------------
    @classmethod
    def gerar_mapa_consequencias(
        cls,
        lancamentos: List[Dict[str, Any]],
        metas: Optional[List[Dict[str, Any]]],
        valor_decisao: float,
        num_parcelas: int = 1,
        tipo_decisao: str = "compra",  # 'compra', 'investimento', 'corte'
    ) -> List[Dict[str, Any]]:
        """
        Mapeia a árvore de causa e efeito de uma decisão financeira em cadeia:
        Ação -> Impacto no fluxo mensal -> Margem de poupança -> Atraso/Adiantamento de metas -> Saldo final.
        """
        valor_decisao = max(0.0, float(valor_decisao))
        num_parcelas = max(1, min(48, int(num_parcelas)))
        valor_parcela = valor_decisao / num_parcelas

        # Projeção normal sem a decisão
        proj_base = cls.projetar_futuro_financeiro(
            lancamentos=lancamentos,
            metas=metas,
            meses_horizonte=12,
        )
        saldo_final_base = proj_base["resumo"]["saldo_final_projetado"]

        # Projeção com a decisão
        evento = {
            "descricao": "Decisão Analisada",
            "valor": valor_parcela,
            "mes_inicio": 1,
            "tipo": "recorrente" if num_parcelas > 1 else "unico",
            "natureza": "despesa" if tipo_decisao == "compra" else "receita",
        }
        proj_impacto = cls.projetar_futuro_financeiro(
            lancamentos=lancamentos,
            metas=metas,
            meses_horizonte=12,
            eventos=[evento],
        )
        saldo_final_impacto = proj_impacto["resumo"]["saldo_final_projetado"]
        diff_saldo = saldo_final_impacto - saldo_final_base

        passos = []

        if tipo_decisao == "compra":
            # 1. Ação
            passos.append({
                "icone": "🛒",
                "etapa": "Ação Inicial",
                "titulo": f"Compra de R$ {valor_decisao:,.2f}",
                "detalhe": f"Dividida em {num_parcelas}x de R$ {valor_parcela:,.2f}/mês",
                "tipo_status": "neutro",
            })
            # 2. Despesas
            passos.append({
                "icone": "📈",
                "etapa": "Impacto Mensal",
                "titulo": f"+ R$ {valor_parcela:,.2f} em Despesas Fixas",
                "detalhe": f"Compromete seu orçamento pelos próximos {num_parcelas} meses",
                "tipo_status": "alerta",
            })
            # 3. Poupança
            passos.append({
                "icone": "📉",
                "etapa": "Capacidade de Economia",
                "titulo": "Redução do Fluxo Livre de Caixa",
                "detalhe": "Menos dinheiro disponível para imprevistos e investimentos",
                "tipo_status": "alerta",
            })
            # 4. Metas
            atraso_meta = math.ceil(valor_decisao / max(100.0, valor_parcela * 2))
            passos.append({
                "icone": "⏳",
                "etapa": "Efeito nas Metas",
                "titulo": f"Possível Atraso de ~{atraso_meta} Meses",
                "detalhe": "Metas de médio e longo prazo demorarão mais para serem atingidas",
                "tipo_status": "aviso",
            })
            # 5. Saldo
            passos.append({
                "icone": "💰",
                "etapa": "Impacto em 12 Meses",
                "titulo": f"Saldo Final {('R$ ' + f'{diff_saldo:,.2f}') if diff_saldo < 0 else ('+ R$ ' + f'{diff_saldo:,.2f}')}",
                "detalhe": f"Saldo projetado passa de R$ {saldo_final_base:,.2f} para R$ {saldo_final_impacto:,.2f}",
                "tipo_status": "alerta" if diff_saldo < 0 else "sucesso",
            })
        else:
            # Caso de Investimento / Economia
            passos.append({
                "icone": "🌱",
                "etapa": "Ação Inicial",
                "titulo": f"Aporte / Economia de R$ {valor_decisao:,.2f}",
                "detalhe": f"Economia mensal ou aporte contínuo de R$ {valor_parcela:,.2f}",
                "tipo_status": "sucesso",
            })
            passos.append({
                "icone": "🛡️",
                "etapa": "Segurança Financeira",
                "titulo": "+ Reserva de Emergência",
                "detalhe": "Aumenta a tranquilidade contra imprevistos futuros",
                "tipo_status": "sucesso",
            })
            passos.append({
                "icone": "🚀",
                "etapa": "Aceleração de Metas",
                "titulo": "Conquista Antecipada de Sonhos",
                "detalhe": "Suas metas ativas serão atingidas vários meses antes!",
                "tipo_status": "sucesso",
            })
            passos.append({
                "icone": "🏆",
                "etapa": "Patrimônio em 12 Meses",
                "titulo": f"+ R$ {abs(diff_saldo):,.2f} no Bolso",
                "detalhe": f"Saldo final salta para R$ {saldo_final_impacto:,.2f}",
                "tipo_status": "sucesso",
            })

        return passos

    # ------------------------------------------------------------------
    # 5. RELATÓRIO MENSAL AUTOMÁTICO COMPLETO
    # ------------------------------------------------------------------
    @classmethod
    def gerar_relatorio_mensal(
        cls,
        lancamentos: List[Dict[str, Any]],
        categorias: Optional[List[Dict[str, Any]]] = None,
        ano: Optional[int] = None,
        mes: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Gera relatório mensal consolidado com:
        - Receitas, despesas, saldo, taxa de poupança
        - Comparativo lado a lado com mês anterior
        - Ranking detalhado de categorias
        - Principais mudanças financeiras
        - Diagnóstico e Parecer Executivo em texto
        """
        hoje = date.today()
        ano = ano or hoje.year
        mes = mes or hoje.month

        # Mês anterior
        mes_ant = 12 if mes == 1 else mes - 1
        ano_ant = ano - 1 if mes == 1 else ano

        # Agrupamento de lançamentos do mês atual
        rec_mes = 0.0
        desp_mes = 0.0
        qtd_rec_mes = 0
        qtd_desp_mes = 0
        despesas_cat: Dict[str, float] = {}
        qtd_por_cat: Dict[str, int] = {}
        maior_despesa_individual = None

        # Mês anterior
        rec_ant = 0.0
        desp_ant = 0.0
        despesas_cat_ant: Dict[str, float] = {}

        for l in lancamentos:
            d = _parse_data(l.get("date") or l.get("data"))
            if not d:
                continue
            val = float(l.get("value") or l.get("valor", 0))
            tipo = l.get("type") or l.get("tipo", "")
            cat = (l.get("category") or l.get("categoria") or "Outros").strip()
            desc = l.get("description") or l.get("descricao") or "Lançamento"

            # Atual
            if d.year == ano and d.month == mes:
                if tipo == "Receita":
                    rec_mes += val
                    qtd_rec_mes += 1
                elif tipo == "Despesa":
                    desp_mes += val
                    qtd_desp_mes += 1
                    despesas_cat[cat] = despesas_cat.get(cat, 0.0) + val
                    qtd_por_cat[cat] = qtd_por_cat.get(cat, 0) + 1

                    if maior_despesa_individual is None or val > maior_despesa_individual["valor"]:
                        maior_despesa_individual = {
                            "descricao": desc,
                            "valor": val,
                            "categoria": cat,
                            "data": d.strftime("%d/%m/%Y"),
                        }

            # Anterior
            elif d.year == ano_ant and d.month == mes_ant:
                if tipo == "Receita":
                    rec_ant += val
                elif tipo == "Despesa":
                    desp_ant += val
                    despesas_cat_ant[cat] = despesas_cat_ant.get(cat, 0.0) + val

        saldo_mes = rec_mes - desp_mes
        saldo_ant = rec_ant - desp_ant

        # Variações vs mês anterior
        def calc_var(atual, anterior):
            diff = atual - anterior
            if anterior > 0:
                pct = (diff / anterior) * 100.0
            else:
                pct = 100.0 if atual > 0 else 0.0
            return diff, pct

        diff_rec, pct_rec = calc_var(rec_mes, rec_ant)
        diff_desp, pct_desp = calc_var(desp_mes, desp_ant)
        diff_saldo, pct_saldo = calc_var(saldo_mes, saldo_ant)

        taxa_poupanca = (saldo_mes / rec_mes * 100.0) if rec_mes > 0 else 0.0
        taxa_poupanca = max(-100.0, min(100.0, taxa_poupanca))

        # Ranking de Categorias
        ranking_categorias = []
        for cat, val in sorted(despesas_cat.items(), key=lambda x: x[1], reverse=True):
            pct_total = (val / desp_mes * 100.0) if desp_mes > 0 else 0.0
            val_ant = despesas_cat_ant.get(cat, 0.0)
            diff_cat, pct_cat = calc_var(val, val_ant)
            ranking_categorias.append({
                "categoria": cat,
                "valor": val,
                "percentual_total": pct_total,
                "qtd_transacoes": qtd_por_cat.get(cat, 0),
                "valor_anterior": val_ant,
                "variacao_pct": pct_cat,
                "variacao_diff": diff_cat,
            })

        # Principais Mudanças Financeiras
        mudancas = []
        # Categoria que mais subiu
        cats_com_historico = [r for r in ranking_categorias if r["valor_anterior"] > 0]
        if cats_com_historico:
            cat_maior_alta = max(cats_com_historico, key=lambda x: x["variacao_diff"])
            if cat_maior_alta["variacao_diff"] > 50:
                mudancas.append({
                    "icone": "📈",
                    "titulo": "Maior Alta de Custo",
                    "descricao": f"'{cat_maior_alta['categoria']}' subiu R$ {cat_maior_alta['variacao_diff']:,.2f} (+{cat_maior_alta['variacao_pct']:.0f}%) vs {cls.NOME_MESES[mes_ant]}.",
                    "cor": "#F38BA8",
                })
            cat_maior_queda = min(cats_com_historico, key=lambda x: x["variacao_diff"])
            if cat_maior_queda["variacao_diff"] < -50:
                mudancas.append({
                    "icone": "📉",
                    "titulo": "Maior Economia em Categoria",
                    "descricao": f"'{cat_maior_queda['categoria']}' reduziu R$ {abs(cat_maior_queda['variacao_diff']):,.2f} ({abs(cat_maior_queda['variacao_pct']):.0f}%) vs mês anterior.",
                    "cor": "#A6E3A1",
                })

        if maior_despesa_individual:
            mudancas.append({
                "icone": "💳",
                "titulo": "Maior Transação do Mês",
                "descricao": f"'{maior_despesa_individual['descricao']}' (R$ {maior_despesa_individual['valor']:,.2f} em {maior_despesa_individual['data']}).",
                "cor": "#89B4FA",
            })

        # Parecer Executivo Gerado
        if rec_mes == 0 and desp_mes == 0:
            parecer = "Não foram encontrados lançamentos no mês selecionado."
            status_geral = "Sem Dados"
        elif saldo_mes > 0 and taxa_poupanca >= 20.0:
            status_geral = "Excelente Desempenho"
            parecer = (
                f"Parabéns! Você fechou o mês de {cls.NOME_MESES[mes]} com taxa de poupança de "
                f"{taxa_poupanca:.1f}%, superando a meta recomendada de 20%. "
                f"Seu saldo líquido foi de R$ {saldo_mes:,.2f}."
            )
        elif saldo_mes >= 0:
            status_geral = "Resultado Equilibrado"
            parecer = (
                f"Você manteve as contas no positivo em {cls.NOME_MESES[mes]}, guardando "
                f"R$ {saldo_mes:,.2f} ({taxa_poupanca:.1f}% da receita). Procure reduzir gastos "
                f"na categoria líder ({ranking_categorias[0]['categoria'] if ranking_categorias else 'Geral'}) "
                f"para aumentar sua capacidade de investimento."
            )
        else:
            status_geral = "Atenção ao Déficit"
            parecer = (
                f"Alerta: Suas despesas superaram as receitas em R$ {abs(saldo_mes):,.2f} no mês de "
                f"{cls.NOME_MESES[mes]}. Recomendamos reavaliar os maiores custos e ajustar orçamentos."
            )

        return {
            "ano": ano,
            "mes": mes,
            "nome_mes": cls.NOME_MESES[mes],
            "nome_mes_anterior": cls.NOME_MESES[mes_ant],
            "totais": {
                "receitas": rec_mes,
                "despesas": desp_mes,
                "saldo": saldo_mes,
                "taxa_poupanca": taxa_poupanca,
                "qtd_receitas": qtd_rec_mes,
                "qtd_despesas": qtd_desp_mes,
                "qtd_total": qtd_rec_mes + qtd_desp_mes,
            },
            "comparativo_anterior": {
                "receitas_anterior": rec_ant,
                "despesas_anterior": desp_ant,
                "saldo_anterior": saldo_ant,
                "diff_receitas": diff_rec,
                "pct_receitas": pct_rec,
                "diff_despesas": diff_desp,
                "pct_despesas": pct_desp,
                "diff_saldo": diff_saldo,
                "pct_saldo": pct_saldo,
            },
            "ranking_categorias": ranking_categorias,
            "principais_mudancas": mudancas,
            "maior_despesa": maior_despesa_individual,
            "parecer_executivo": parecer,
            "status_geral": status_geral,
        }

    # ------------------------------------------------------------------
    # 6. UTILITÁRIO: LISTAR MESES COM DADOS
    # ------------------------------------------------------------------
    @classmethod
    def obter_meses_disponiveis(cls, lancamentos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Retorna lista de meses ordenados do mais recente para o mais antigo."""
        meses_set = set()
        for l in lancamentos:
            d = _parse_data(l.get("date") or l.get("data"))
            if d:
                meses_set.add((d.year, d.month))

        hoje = date.today()
        meses_set.add((hoje.year, hoje.month))

        ordenados = sorted(list(meses_set), reverse=True)
        resultado = []
        for ano, mes in ordenados:
            resultado.append({
                "rotulo": f"{cls.NOME_MESES[mes]} / {ano}",
                "ano": ano,
                "mes": mes,
            })
        return resultado
