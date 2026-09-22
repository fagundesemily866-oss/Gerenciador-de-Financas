"""
View do Simulador Financeiro Avançado — Laboratório de Decisões.
==============================================================

Funcionalidades integradas:
1. Projeção temporal contínua (3m, 6m, 1 ano, 2 anos)
2. Gráfico interativo de evolução financeira vetorial (Canvas)
3. Cenários Otimista, Normal e Pessimista simultâneos
4. Eventos financeiros inesperados com efeito cascata
5. Linha do tempo financeira mensal interativa (clique para detalhar o mês)
6. Comparador de decisões financeiras lado a lado (Cenários A, B e C)
7. Mapa de consequências em cascata (efeito dominó das decisões)
8. Previsão inteligente de metas com cálculo de mês/ano estimado
9. Assistente de IA integrado com consultoria interpretativa
10. Salvar, recuperar e comparar simulações no banco de dados SQLite
"""
import threading
from typing import Optional, Dict, Any, List
import customtkinter as ctk

from dao.lancamento_dao import LancamentoDAO
from dao.meta_dao import MetaDAO
from dao.categoria_dao import CategoriaDAO
from dao.simulacao_dao import SimulacaoDAO
from services.ai_service import AIService
from controllers.inteligencia_financeira_controller import InteligenciaFinanceiraController
from views.grafico_evolucao import GraficoEvolucaoCanvas
from views.notificacao_toast import GerenciadorNotificacoes
from views.tema import (
    COR_FUNDO_PRINCIPAL, COR_CARD, COR_CARD_INTERNO, COR_BORDA,
    COR_TEXTO_PRINCIPAL, COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_ACENTO_HOVER, COR_SUCESSO, COR_SUCESSO_HOVER,
    COR_ALERTA, COR_ALERTA_HOVER, COR_AVISO, COR_INFO,
    COR_BOTAO_SECUNDARIO, COR_BOTAO_SECUNDARIO_HOVER,
    fonte, fonte_titulo, fonte_subtitulo
)


class SimuladorView(ctk.CTkFrame):
    """Tela do Laboratório de Decisões e Simulação Financeira."""

    def __init__(
        self,
        parent,
        dao: Optional[LancamentoDAO] = None,
        meta_dao: Optional[MetaDAO] = None,
        cat_dao: Optional[CategoriaDAO] = None,
        sim_dao: Optional[SimulacaoDAO] = None,
    ):
        super().__init__(parent, fg_color="transparent")

        self.dao = dao or LancamentoDAO()
        self.meta_dao = meta_dao or MetaDAO()
        self.cat_dao = cat_dao or CategoriaDAO()
        self.sim_dao = sim_dao or SimulacaoDAO()
        self.ai_service = AIService()
        self.notificador = None

        # Estado da simulação
        self._horizonte_meses = 12
        self._eventos_inesperados: List[Dict[str, Any]] = []
        self._dados_projecao: Optional[Dict[str, Any]] = None
        self._mes_selecionado_idx = 0

        # Layout da tela principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._criar_topo_navegacao()
        self._criar_container_conteudo()

        # Renderizar aba inicial e atualizar dados
        self._alternar_aba("🔮 Projeção & Gráficos")

    def _obter_notificador(self):
        if not self.notificador:
            try:
                top = self.winfo_toplevel()
                self.notificador = GerenciadorNotificacoes(top)
            except Exception:
                pass
        return self.notificador

    def _notificar(self, msg: str, tipo: str = "sucesso"):
        n = self._obter_notificador()
        if n:
            n.mostrar(msg, tipo=tipo)

    # ==============================================================
    # 1. BARRA SUPERIOR DE NAVEGAÇÃO ENTRE MÓDULOS
    # ==============================================================
    def _criar_topo_navegacao(self):
        self.barra_topo = ctk.CTkFrame(self, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        self.barra_topo.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        self.barra_topo.grid_columnconfigure(0, weight=1)

        topo_inner = ctk.CTkFrame(self.barra_topo, fg_color="transparent")
        topo_inner.pack(fill="x", padx=12, pady=8)
        topo_inner.grid_columnconfigure(0, weight=1)

        # Seletor de Módulos
        self.seletor_modulo = ctk.CTkSegmentedButton(
            topo_inner,
            values=[
                "🔮 Projeção & Gráficos",
                "⏳ Linha do Tempo & Eventos",
                "⚖️ Comparador de Decisões",
                "🗺️ Mapa de Consequências",
                "💾 Simulações Salvas",
            ],
            command=self._alternar_aba,
            font=fonte(12, "bold"),
            selected_color=COR_ACENTO_PRIMARIO,
            selected_hover_color=COR_ACENTO_HOVER,
            unselected_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_PRINCIPAL,
        )
        self.seletor_modulo.grid(row=0, column=0, sticky="w")

        # Botão Ação Rápida: Salvar
        btn_salvar = ctk.CTkButton(
            topo_inner,
            text="💾 Salvar Cenário",
            font=fonte(11, "bold"),
            fg_color=COR_ACENTO_PRIMARIO,
            hover_color=COR_ACENTO_HOVER,
            text_color=COR_FUNDO_PRINCIPAL,
            height=32,
            command=self._abrir_modal_salvar,
        )
        btn_salvar.grid(row=0, column=1, padx=(10, 0), sticky="e")

    def _criar_container_conteudo(self):
        self.container_abas = ctk.CTkFrame(self, fg_color="transparent")
        self.container_abas.grid(row=1, column=0, sticky="nsew")
        self.container_abas.grid_columnconfigure(0, weight=1)
        self.container_abas.grid_rowconfigure(0, weight=1)

        # Criação dos frames de cada aba
        self.frame_projecao = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        self.frame_timeline = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        self.frame_comparador = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        self.frame_consequencias = ctk.CTkFrame(self.container_abas, fg_color="transparent")
        self.frame_salvas = ctk.CTkFrame(self.container_abas, fg_color="transparent")

        self._construir_aba_projecao()
        self._construir_aba_timeline()
        self._construir_aba_comparador()
        self._construir_aba_consequencias()
        self._construir_aba_salvas()

    def _alternar_aba(self, nome_aba: str):
        # Esconder todos os frames
        for f in (self.frame_projecao, self.frame_timeline, self.frame_comparador,
                  self.frame_consequencias, self.frame_salvas):
            f.grid_forget()

        if "Projeção" in nome_aba:
            self.frame_projecao.grid(row=0, column=0, sticky="nsew")
            self._recalcular()
        elif "Linha do Tempo" in nome_aba:
            self.frame_timeline.grid(row=0, column=0, sticky="nsew")
            self._renderizar_timeline()
        elif "Comparador" in nome_aba:
            self.frame_comparador.grid(row=0, column=0, sticky="nsew")
            self._executar_comparador()
        elif "Mapa" in nome_aba:
            self.frame_consequencias.grid(row=0, column=0, sticky="nsew")
            self._renderizar_mapa_consequencias()
        elif "Salvas" in nome_aba:
            self.frame_salvas.grid(row=0, column=0, sticky="nsew")
            self._listar_simulacoes_salvas()

    # ==============================================================
    # 2. ABA: PROJEÇÃO & GRÁFICOS (Sliders, Gráfico e 3 Cenários)
    # ==============================================================
    def _construir_aba_projecao(self):
        self.frame_projecao.grid_columnconfigure(0, weight=4)  # Coluna da esquerda (Controles)
        self.frame_projecao.grid_columnconfigure(1, weight=6)  # Coluna da direita (Gráfico e Resultados)
        self.frame_projecao.grid_rowconfigure(0, weight=1)

        # ----------------- PAINEL ESQUERDO: CONTROLES -----------------
        self.card_controles = ctk.CTkScrollableFrame(
            self.frame_projecao,
            corner_radius=12,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
        )
        self.card_controles.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        self.card_controles.grid_columnconfigure(0, weight=1)

        # Cabeçalho Controles
        ctk.CTkLabel(
            self.card_controles,
            text="🎛️  PARÂMETROS DA SIMULAÇÃO",
            font=fonte(13, "bold"),
            text_color=COR_ACENTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 4))

        # 1. Seletor de Período (Horizonte de Projeção)
        card_per = ctk.CTkFrame(self.card_controles, fg_color=COR_CARD_INTERNO, corner_radius=10)
        card_per.pack(fill="x", padx=12, pady=(0, 10))
        ctk.CTkLabel(
            card_per,
            text="📅 Horizonte de Tempo:",
            font=fonte(12, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(8, 4))

        self.seletor_periodo = ctk.CTkSegmentedButton(
            card_per,
            values=["3 Meses", "6 Meses", "1 Ano (12m)", "2 Anos (24m)"],
            command=self._on_mudar_periodo,
            font=fonte(11),
            selected_color=COR_ACENTO_PRIMARIO,
            selected_hover_color=COR_ACENTO_HOVER,
            unselected_color=COR_CARD,
        )
        self.seletor_periodo.set("1 Ano (12m)")
        self.seletor_periodo.pack(fill="x", padx=10, pady=(0, 10))

        # 2. Redução de Gastos
        sec_gastos = ctk.CTkFrame(self.card_controles, fg_color=COR_CARD_INTERNO, corner_radius=10)
        sec_gastos.pack(fill="x", padx=12, pady=(0, 10))

        header_g = ctk.CTkFrame(sec_gastos, fg_color="transparent")
        header_g.pack(fill="x", padx=12, pady=(8, 2))
        header_g.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_g,
            text="📉 Corte de Despesas:",
            font=fonte(12, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
        ).grid(row=0, column=0, sticky="w")

        self.lbl_pct_reducao = ctk.CTkLabel(
            header_g,
            text="0%",
            font=fonte(12, "bold"),
            text_color=COR_SUCESSO,
        )
        self.lbl_pct_reducao.grid(row=0, column=1, sticky="e")

        self.slider_reducao = ctk.CTkSlider(
            sec_gastos,
            from_=0,
            to=50,
            number_of_steps=50,
            command=self._on_slider_reducao_change,
            button_color=COR_SUCESSO,
            button_hover_color=COR_SUCESSO_HOVER,
            progress_color=COR_SUCESSO,
        )
        self.slider_reducao.set(0)
        self.slider_reducao.pack(fill="x", padx=12, pady=(4, 6))

        # Categoria Alvo da Redução
        ctk.CTkLabel(
            sec_gastos,
            text="Aplicar redução em:",
            font=fonte(11),
            text_color=COR_TEXTO_SECUNDARIO,
        ).pack(anchor="w", padx=12, pady=(2, 2))

        self.combo_categoria = ctk.CTkComboBox(
            sec_gastos,
            values=["Todas as Despesas"],
            command=lambda _: self._recalcular(),
            fg_color=COR_CARD,
            border_color=COR_BORDA,
            button_color=COR_BOTAO_SECUNDARIO,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(11),
        )
        self.combo_categoria.pack(fill="x", padx=12, pady=(0, 8))

        # 3. Aumento de Renda
        sec_renda = ctk.CTkFrame(self.card_controles, fg_color=COR_CARD_INTERNO, corner_radius=10)
        sec_renda.pack(fill="x", padx=12, pady=(0, 10))

        header_r = ctk.CTkFrame(sec_renda, fg_color="transparent")
        header_r.pack(fill="x", padx=12, pady=(8, 2))
        header_r.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_r,
            text="📈 Aumento de Renda / Extra:",
            font=fonte(12, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
        ).grid(row=0, column=0, sticky="w")

        self.lbl_val_renda = ctk.CTkLabel(
            header_r,
            text="+ R$ 0,00",
            font=fonte(12, "bold"),
            text_color=COR_ACENTO_PRIMARIO,
        )
        self.lbl_val_renda.grid(row=0, column=1, sticky="e")

        self.slider_renda = ctk.CTkSlider(
            sec_renda,
            from_=0,
            to=5000,
            number_of_steps=50,
            command=self._on_slider_renda_change,
            button_color=COR_ACENTO_PRIMARIO,
            button_hover_color=COR_ACENTO_HOVER,
            progress_color=COR_ACENTO_PRIMARIO,
        )
        self.slider_renda.set(0)
        self.slider_renda.pack(fill="x", padx=12, pady=(4, 8))

        # 4. Aporte Extra em Metas
        sec_metas = ctk.CTkFrame(self.card_controles, fg_color=COR_CARD_INTERNO, corner_radius=10)
        sec_metas.pack(fill="x", padx=12, pady=(0, 10))

        header_m = ctk.CTkFrame(sec_metas, fg_color="transparent")
        header_m.pack(fill="x", padx=12, pady=(8, 2))
        header_m.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_m,
            text="🎯 Aporte Mensal para Metas:",
            font=fonte(12, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
        ).grid(row=0, column=0, sticky="w")

        self.lbl_val_meta = ctk.CTkLabel(
            header_m,
            text="+ R$ 0,00",
            font=fonte(12, "bold"),
            text_color=COR_AVISO,
        )
        self.lbl_val_meta.grid(row=0, column=1, sticky="e")

        self.slider_meta = ctk.CTkSlider(
            sec_metas,
            from_=0,
            to=3000,
            number_of_steps=60,
            command=self._on_slider_meta_change,
            button_color=COR_AVISO,
            button_hover_color=COR_AVISO,
            progress_color=COR_AVISO,
        )
        self.slider_meta.set(0)
        self.slider_meta.pack(fill="x", padx=12, pady=(4, 8))

        # Botão Resetar e Consultoria IA
        frame_botoes = ctk.CTkFrame(self.card_controles, fg_color="transparent")
        frame_botoes.pack(fill="x", padx=12, pady=(4, 12))
        frame_botoes.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            frame_botoes,
            text="🔄 Resetar",
            height=32,
            fg_color=COR_BOTAO_SECUNDARIO,
            hover_color=COR_BOTAO_SECUNDARIO_HOVER,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(11),
            command=self._resetar,
        ).grid(row=0, column=0, padx=(0, 4), sticky="ew")

        ctk.CTkButton(
            frame_botoes,
            text="🤖 Parecer da IA",
            height=32,
            fg_color=COR_ACENTO_PRIMARIO,
            hover_color=COR_ACENTO_HOVER,
            text_color=COR_FUNDO_PRINCIPAL,
            font=fonte(11, "bold"),
            command=self._solicitar_analise_ia,
        ).grid(row=0, column=1, padx=(4, 0), sticky="ew")

        # ----------------- PAINEL DIREITO: GRÁFICO E RESULTADOS -----------------
        self.card_resultados = ctk.CTkScrollableFrame(
            self.frame_projecao,
            corner_radius=12,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
        )
        self.card_resultados.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        self.card_resultados.grid_columnconfigure(0, weight=1)

        # Gráfico Canvas Integrado
        self.grafico = GraficoEvolucaoCanvas(self.card_resultados, height=260)
        self.grafico.pack(fill="x", padx=12, pady=(12, 10))

        # CARDS DOS 3 CENÁRIOS (Otimista, Normal, Pessimista)
        self.frame_3_cenarios = ctk.CTkFrame(self.card_resultados, fg_color="transparent")
        self.frame_3_cenarios.pack(fill="x", padx=12, pady=(0, 10))
        self.frame_3_cenarios.grid_columnconfigure((0, 1, 2), weight=1)

        # Card Cenário Otimista
        self.card_otimista = ctk.CTkFrame(self.frame_3_cenarios, fg_color=COR_CARD_INTERNO, corner_radius=10, border_width=1, border_color=COR_SUCESSO)
        self.card_otimista.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        ctk.CTkLabel(self.card_otimista, text="🚀 OTIMISTA", font=fonte(10, "bold"), text_color=COR_SUCESSO).pack(anchor="w", padx=10, pady=(6, 0))
        self.lbl_val_otimista = ctk.CTkLabel(self.card_otimista, text="R$ 0,00", font=fonte(14, "bold"), text_color=COR_TEXTO_PRINCIPAL)
        self.lbl_val_otimista.pack(anchor="w", padx=10, pady=(0, 2))
        ctk.CTkLabel(self.card_otimista, text="+10% Rec / -5% Desp", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=10, pady=(0, 6))

        # Card Cenário Normal
        self.card_normal = ctk.CTkFrame(self.frame_3_cenarios, fg_color=COR_CARD_INTERNO, corner_radius=10, border_width=1, border_color=COR_ACENTO_PRIMARIO)
        self.card_normal.grid(row=0, column=1, sticky="nsew", padx=2)
        ctk.CTkLabel(self.card_normal, text="📊 PLANEJADO (NORMAL)", font=fonte(10, "bold"), text_color=COR_ACENTO_PRIMARIO).pack(anchor="w", padx=10, pady=(6, 0))
        self.lbl_val_normal = ctk.CTkLabel(self.card_normal, text="R$ 0,00", font=fonte(14, "bold"), text_color=COR_TEXTO_PRINCIPAL)
        self.lbl_val_normal.pack(anchor="w", padx=10, pady=(0, 2))
        ctk.CTkLabel(self.card_normal, text="Com base nos seus sliders", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=10, pady=(0, 6))

        # Card Cenário Pessimista
        self.card_pessimista = ctk.CTkFrame(self.frame_3_cenarios, fg_color=COR_CARD_INTERNO, corner_radius=10, border_width=1, border_color=COR_ALERTA)
        self.card_pessimista.grid(row=0, column=2, sticky="nsew", padx=(4, 0))
        ctk.CTkLabel(self.card_pessimista, text="⚠️ PESSIMISTA", font=fonte(10, "bold"), text_color=COR_ALERTA).pack(anchor="w", padx=10, pady=(6, 0))
        self.lbl_val_pessimista = ctk.CTkLabel(self.card_pessimista, text="R$ 0,00", font=fonte(14, "bold"), text_color=COR_TEXTO_PRINCIPAL)
        self.lbl_val_pessimista.pack(anchor="w", padx=10, pady=(0, 2))
        ctk.CTkLabel(self.card_pessimista, text="-10% Rec / +15% Desp", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=10, pady=(0, 6))

        # PREVISÃO INTELIGENTE DE METAS
        self.sec_metas_previsao = ctk.CTkFrame(self.card_resultados, fg_color="transparent")
        self.sec_metas_previsao.pack(fill="x", padx=12, pady=(0, 10))
        ctk.CTkLabel(
            self.sec_metas_previsao,
            text="🎯  PREVISÃO INTELIGENTE DE METAS",
            font=fonte(12, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        ).pack(fill="x", pady=(0, 6))

        self.container_cards_metas = ctk.CTkFrame(self.sec_metas_previsao, fg_color="transparent")
        self.container_cards_metas.pack(fill="x")

        # PARECER CONSULTIVO DA IA (Card com retorno do assistente)
        self.card_parecer_ia = ctk.CTkFrame(
            self.card_resultados,
            corner_radius=10,
            fg_color=COR_CARD_INTERNO,
            border_width=1,
            border_color=COR_ACENTO_PRIMARIO,
        )
        self.card_parecer_ia.pack(fill="x", padx=12, pady=(0, 12))

        ctk.CTkLabel(
            self.card_parecer_ia,
            text="🤖  CONSULTORIA DA IA",
            font=fonte(11, "bold"),
            text_color=COR_ACENTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x", padx=12, pady=(10, 4))

        self.lbl_texto_ia = ctk.CTkLabel(
            self.card_parecer_ia,
            text="Clique em '🤖 Parecer da IA' para gerar uma análise consultiva detalhada sobre esta projeção.",
            font=fonte(11),
            text_color=COR_TEXTO_SECUNDARIO,
            justify="left",
            wraplength=480,
            anchor="w",
        )
        self.lbl_texto_ia.pack(fill="x", padx=12, pady=(0, 10))

    def _on_mudar_periodo(self, valor: str):
        if "3 Meses" in valor:
            self._horizonte_meses = 3
        elif "6 Meses" in valor:
            self._horizonte_meses = 6
        elif "2 Anos" in valor:
            self._horizonte_meses = 24
        else:
            self._horizonte_meses = 12
        self._recalcular()

    def _on_slider_reducao_change(self, val):
        self.lbl_pct_reducao.configure(text=f"{int(val)}%")
        self._recalcular()

    def _on_slider_renda_change(self, val):
        self.lbl_val_renda.configure(text=f"+ R$ {val:,.2f}")
        self._recalcular()

    def _on_slider_meta_change(self, val):
        self.lbl_val_meta.configure(text=f"+ R$ {val:,.2f}")
        self._recalcular()

    def _resetar(self):
        self.slider_reducao.set(0)
        self.slider_renda.set(0)
        self.slider_meta.set(0)
        self.lbl_pct_reducao.configure(text="0%")
        self.lbl_val_renda.configure(text="+ R$ 0,00")
        self.lbl_val_meta.configure(text="+ R$ 0,00")
        self._eventos_inesperados.clear()
        self._recalcular()
        self._notificar("Parâmetros do laboratório restaurados!", "info")

    # ==============================================================
    # 3. ABA: LINHA DO TEMPO & EVENTOS INESPERADOS
    # ==============================================================
    def _construir_aba_timeline(self):
        self.frame_timeline.grid_columnconfigure(0, weight=1)
        self.frame_timeline.grid_rowconfigure(1, weight=1)

        # Topo da Linha do Tempo: Régua horizontal de meses
        topo_timeline = ctk.CTkFrame(self.frame_timeline, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        topo_timeline.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))
        topo_timeline.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            topo_timeline,
            text="⏳  LINHA DO TEMPO FINANCEIRA MÊS A MÊS (Clique em um mês para detalhar)",
            font=fonte(12, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(10, 6))

        self.scroll_regua_meses = ctk.CTkScrollableFrame(topo_timeline, height=75, orientation="horizontal", fg_color=COR_CARD_INTERNO)
        self.scroll_regua_meses.pack(fill="x", padx=12, pady=(0, 12))

        # Corpo inferior: Dividido em Detalhe do Mês Selecionado (Esquerda) e Cadastro de Eventos (Direita)
        corpo_timeline = ctk.CTkFrame(self.frame_timeline, fg_color="transparent")
        corpo_timeline.grid(row=1, column=0, sticky="nsew")
        corpo_timeline.grid_columnconfigure((0, 1), weight=1)
        corpo_timeline.grid_rowconfigure(0, weight=1)

        # Card Detalhe do Mês Selecionado
        self.card_detalhe_mes = ctk.CTkFrame(corpo_timeline, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        self.card_detalhe_mes.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.card_detalhe_mes.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.card_detalhe_mes,
            text="🔍  DETALHES DO MÊS SELECIONADO",
            font=fonte(13, "bold"),
            text_color=COR_ACENTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 6))

        self.lbl_nome_mes_detalhe = ctk.CTkLabel(self.card_detalhe_mes, text="Selecione um mês na régua acima", font=fonte(15, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w")
        self.lbl_nome_mes_detalhe.pack(fill="x", padx=14, pady=(0, 8))

        self.frame_dados_mes = ctk.CTkFrame(self.card_detalhe_mes, fg_color=COR_CARD_INTERNO, corner_radius=8)
        self.frame_dados_mes.pack(fill="x", padx=14, pady=(0, 10))

        self.lbl_mes_rec = ctk.CTkLabel(self.frame_dados_mes, text="Receitas: R$ 0,00", font=fonte(12), text_color=COR_SUCESSO, anchor="w")
        self.lbl_mes_rec.pack(fill="x", padx=12, pady=(8, 2))

        self.lbl_mes_desp = ctk.CTkLabel(self.frame_dados_mes, text="Despesas: R$ 0,00", font=fonte(12), text_color=COR_ALERTA, anchor="w")
        self.lbl_mes_desp.pack(fill="x", padx=12, pady=2)

        self.lbl_mes_saldo = ctk.CTkLabel(self.frame_dados_mes, text="Saldo do Mês: R$ 0,00", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w")
        self.lbl_mes_saldo.pack(fill="x", padx=12, pady=2)

        self.lbl_mes_acumulado = ctk.CTkLabel(self.frame_dados_mes, text="Saldo Acumulado: R$ 0,00", font=fonte(12, "bold"), text_color=COR_ACENTO_PRIMARIO, anchor="w")
        self.lbl_mes_acumulado.pack(fill="x", padx=12, pady=(2, 8))

        ctk.CTkLabel(self.card_detalhe_mes, text="Eventos Ativos Neste Mês:", font=fonte(11, "bold"), text_color=COR_TEXTO_SECUNDARIO, anchor="w").pack(fill="x", padx=14, pady=(4, 2))
        self.lbl_mes_eventos_desc = ctk.CTkLabel(self.card_detalhe_mes, text="Nenhum evento inesperado afetando este mês.", font=fonte(11), text_color=COR_TEXTO_MUTED, anchor="w")
        self.lbl_mes_eventos_desc.pack(fill="x", padx=14, pady=(0, 10))

        # Card de Cadastro e Lista de Eventos Inesperados
        self.card_eventos = ctk.CTkScrollableFrame(corpo_timeline, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        self.card_eventos.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.card_eventos.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.card_eventos,
            text="⚡  EVENTOS FINANCEIROS INESPERADOS",
            font=fonte(13, "bold"),
            text_color=COR_AVISO,
            anchor="w",
        ).pack(fill="x", padx=12, pady=(12, 4))

        # Form de inclusão rápida de evento
        form_ev = ctk.CTkFrame(self.card_eventos, fg_color=COR_CARD_INTERNO, corner_radius=8)
        form_ev.pack(fill="x", padx=10, pady=(0, 10))

        self.entry_ev_nome = ctk.CTkEntry(form_ev, placeholder_text="Ex: Manutenção do Carro, Bônus, Emergência", font=fonte(11), fg_color=COR_CARD, border_color=COR_BORDA)
        self.entry_ev_nome.pack(fill="x", padx=10, pady=(8, 4))

        row_ev_vals = ctk.CTkFrame(form_ev, fg_color="transparent")
        row_ev_vals.pack(fill="x", padx=10, pady=2)
        row_ev_vals.grid_columnconfigure((0, 1, 2), weight=1)

        self.entry_ev_valor = ctk.CTkEntry(row_ev_vals, placeholder_text="Valor R$ (ex: 800)", font=fonte(11), fg_color=COR_CARD, border_color=COR_BORDA)
        self.entry_ev_valor.grid(row=0, column=0, padx=2, sticky="ew")

        self.combo_ev_tipo = ctk.CTkComboBox(row_ev_vals, values=["Gasto Único", "Despesa Mensal", "Renda Extra"], font=fonte(11), fg_color=COR_CARD, border_color=COR_BORDA)
        self.combo_ev_tipo.grid(row=0, column=1, padx=2, sticky="ew")

        self.entry_ev_mes = ctk.CTkEntry(row_ev_vals, placeholder_text="No mês (ex: 3)", font=fonte(11), fg_color=COR_CARD, border_color=COR_BORDA)
        self.entry_ev_mes.grid(row=0, column=2, padx=2, sticky="ew")

        ctk.CTkButton(
            form_ev,
            text="➕ Inserir Evento na Simulação",
            font=fonte(11, "bold"),
            fg_color=COR_AVISO,
            hover_color=COR_AVISO,
            text_color=COR_FUNDO_PRINCIPAL,
            height=30,
            command=self._adicionar_evento,
        ).pack(fill="x", padx=10, pady=(6, 8))

        ctk.CTkLabel(self.card_eventos, text="Eventos Cadastrados:", font=fonte(11, "bold"), text_color=COR_TEXTO_SECUNDARIO, anchor="w").pack(fill="x", padx=12, pady=(4, 2))
        self.container_lista_eventos = ctk.CTkFrame(self.card_eventos, fg_color="transparent")
        self.container_lista_eventos.pack(fill="x", padx=8, pady=(0, 8))

    def _adicionar_evento(self):
        nome = self.entry_ev_nome.get().strip()
        valor_str = self.entry_ev_valor.get().strip()
        tipo_str = self.combo_ev_tipo.get()
        mes_str = self.entry_ev_mes.get().strip()

        if not nome or not valor_str:
            self._notificar("Preencha a descrição e o valor do evento!", "erro")
            return

        try:
            val = float(valor_str.replace("R$", "").replace(".", "").replace(",", "."))
            mes_ini = int(mes_str) if mes_str else 1
        except ValueError:
            self._notificar("Valor ou mês inválido!", "erro")
            return

        natureza = "receita" if "Renda" in tipo_str else "despesa"
        tipo = "recorrente" if "Mensal" in tipo_str else "unico"

        evento = {
            "id": len(self._eventos_inesperados) + 1,
            "descricao": nome,
            "valor": val,
            "mes_inicio": max(1, min(self._horizonte_meses, mes_ini)),
            "tipo": tipo,
            "natureza": natureza,
        }
        self._eventos_inesperados.append(evento)
        self.entry_ev_nome.delete(0, "end")
        self.entry_ev_valor.delete(0, "end")
        self.entry_ev_mes.delete(0, "end")

        self._recalcular()
        self._renderizar_timeline()
        self._notificar(f"Evento '{nome}' inserido com sucesso!", "sucesso")

    def _remover_evento(self, ev_id: int):
        self._eventos_inesperados = [e for e in self._eventos_inesperados if e.get("id") != ev_id]
        self._recalcular()
        self._renderizar_timeline()
        self._notificar("Evento removido da projeção.", "info")

    def _renderizar_timeline(self):
        if not self._dados_projecao:
            return

        # Limpar régua
        for w in self.scroll_regua_meses.winfo_children():
            w.destroy()

        meses = self._dados_projecao.get("meses", [])
        for idx, m in enumerate(meses):
            cor_chip = COR_ACENTO_PRIMARIO if idx == self._mes_selecionado_idx else COR_CARD
            has_ev = len(m["eventos_mes"]) > 0

            chip = ctk.CTkFrame(self.scroll_regua_meses, fg_color=cor_chip, corner_radius=8, width=70, height=52)
            chip.pack(side="left", padx=4, pady=2)
            chip.pack_propagate(False)

            txt_icone = "⚡ " if has_ev else ""
            lbl_mes = ctk.CTkLabel(chip, text=f"{txt_icone}{m['rotulo_mes']}", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL)
            lbl_mes.pack(pady=(4, 0))

            lbl_saldo_res = ctk.CTkLabel(chip, text=f"R${m['saldo_simulado']:,.0f}", font=fonte(9), text_color=COR_TEXTO_SECUNDARIO)
            lbl_saldo_res.pack()

            # Evento de clique no chip
            for widget in (chip, lbl_mes, lbl_saldo_res):
                widget.bind("<Button-1>", lambda e, i=idx: self._selecionar_mes_timeline(i))

        # Atualizar detalhe do mês selecionado
        if meses and 0 <= self._mes_selecionado_idx < len(meses):
            sel = meses[self._mes_selecionado_idx]
            self.lbl_nome_mes_detalhe.configure(text=f"Mês {sel['numero_mes']} — {sel['rotulo_mes']}")
            self.lbl_mes_rec.configure(text=f"Receitas Projetadas: R$ {sel['receitas_simulado']:,.2f}")
            self.lbl_mes_desp.configure(text=f"Despesas Projetadas: R$ {sel['despesas_simulado']:,.2f}")

            cor_saldo = COR_SUCESSO if sel["saldo_simulado"] >= 0 else COR_ALERTA
            self.lbl_mes_saldo.configure(text=f"Saldo no Mês: R$ {sel['saldo_simulado']:,.2f}", text_color=cor_saldo)
            self.lbl_mes_acumulado.configure(text=f"Saldo Acumulado: R$ {sel['saldo_acumulado_simulado']:,.2f}")

            if sel["eventos_mes"]:
                ev_textos = [f"• {e['descricao']} ({e['natureza'].capitalize()} de R$ {e['valor']:,.2f})" for e in sel["eventos_mes"]]
                self.lbl_mes_eventos_desc.configure(text="\n".join(ev_textos), text_color=COR_AVISO)
            else:
                self.lbl_mes_eventos_desc.configure(text="Nenhum evento inesperado afetando este mês.", text_color=COR_TEXTO_MUTED)

        # Renderizar lista de eventos cadastrados
        for w in self.container_lista_eventos.winfo_children():
            w.destroy()

        if not self._eventos_inesperados:
            ctk.CTkLabel(self.container_lista_eventos, text="Nenhum evento inesperado adicionado ainda.", font=fonte(11), text_color=COR_TEXTO_MUTED).pack(anchor="w", pady=4)
        else:
            for ev in self._eventos_inesperados:
                item_card = ctk.CTkFrame(self.container_lista_eventos, fg_color=COR_CARD_INTERNO, corner_radius=6)
                item_card.pack(fill="x", pady=2)
                item_card.grid_columnconfigure(0, weight=1)

                txt_tipo = "Mensal" if ev["tipo"] == "recorrente" else "Único"
                desc = f"⚡ {ev['descricao']} — R$ {ev['valor']:,.2f} ({ev['natureza'].capitalize()}, {txt_tipo} a partir do mês {ev['mes_inicio']})"
                ctk.CTkLabel(item_card, text=desc, font=fonte(10), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=0, padx=8, pady=4, sticky="w")

                btn_del = ctk.CTkButton(
                    item_card,
                    text="✕",
                    width=24,
                    height=20,
                    fg_color=COR_ALERTA,
                    hover_color=COR_ALERTA_HOVER,
                    text_color=COR_FUNDO_PRINCIPAL,
                    command=lambda eid=ev["id"]: self._remover_evento(eid),
                )
                btn_del.grid(row=0, column=1, padx=6, pady=4, sticky="e")

    def _selecionar_mes_timeline(self, idx: int):
        self._mes_selecionado_idx = idx
        self._renderizar_timeline()

    # ==============================================================
    # 4. ABA: COMPARADOR DE DECISÕES FINANCEIRAS (A, B, C)
    # ==============================================================
    def _construir_aba_comparador(self):
        self.frame_comparador.grid_columnconfigure(0, weight=1)
        self.frame_comparador.grid_rowconfigure(1, weight=1)

        topo = ctk.CTkFrame(self.frame_comparador, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        topo.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))

        ctk.CTkLabel(
            topo,
            text="⚖️  COMPARADOR DE DECISÕES FINANCEIRAS (Simule diferentes caminhos lado a lado)",
            font=fonte(13, "bold"),
            text_color=COR_ACENTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            topo,
            text="Veja como 3 decisões distintas impactam seu saldo, economia e metas em 12 meses.",
            font=fonte(11),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(0, 10))

        # Container dos 3 Cenários lado a lado
        self.container_cards_decisoes = ctk.CTkScrollableFrame(self.frame_comparador, fg_color="transparent")
        self.container_cards_decisoes.grid(row=1, column=0, sticky="nsew")
        self.container_cards_decisoes.grid_columnconfigure((0, 1, 2), weight=1)

    def _executar_comparador(self):
        lancamentos = self.dao.listar_todos()
        metas = self.meta_dao.listar_todas()

        decisao_a = {
            "nome": "Cenário A: Comprar Parcelado",
            "descricao": "Aquisição de R$ 3.600 em 12x de R$ 300.",
            "gasto_inicial": 0.0,
            "parcela_mensal": 300.0,
            "aumento_renda": 0.0,
            "aporte_metas": 0.0,
            "corte_despesas_pct": 0.0,
        }
        decisao_b = {
            "nome": "Cenário B: Guardar e Poupar",
            "descricao": "Corte de 10% em despesas para reserva.",
            "gasto_inicial": 0.0,
            "parcela_mensal": 0.0,
            "aumento_renda": 0.0,
            "aporte_metas": 0.0,
            "corte_despesas_pct": 10.0,
        }
        decisao_c = {
            "nome": "Cenário C: Foco em Metas",
            "descricao": "R$ 350 extras por mês direcionados a metas.",
            "gasto_inicial": 0.0,
            "parcela_mensal": 0.0,
            "aumento_renda": 0.0,
            "aporte_metas": 350.0,
            "corte_despesas_pct": 5.0,
        }

        comparativo = InteligenciaFinanceiraController.comparar_decisoes_financeiras(
            lancamentos=lancamentos,
            metas=metas,
            decisao_a=decisao_a,
            decisao_b=decisao_b,
            decisao_c=decisao_c,
            meses_horizonte=12,
        )

        for w in self.container_cards_decisoes.winfo_children():
            w.destroy()

        veredito = comparativo["veredito"]
        decisoes = [comparativo["decisao_a"], comparativo["decisao_b"], comparativo["decisao_c"]]

        for idx, dec in enumerate(decisoes):
            destaque_cor = COR_ACENTO_PRIMARIO if dec["nome"] == veredito["campea_saldo"] else COR_BORDA
            card = ctk.CTkFrame(
                self.container_cards_decisoes,
                fg_color=COR_CARD,
                corner_radius=12,
                border_width=2 if dec["nome"] == veredito["campea_saldo"] else 1,
                border_color=destaque_cor,
            )
            card.grid(row=0, column=idx, sticky="nsew", padx=6, pady=4)

            ctk.CTkLabel(card, text=dec["nome"], font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=12, pady=(12, 2))
            ctk.CTkLabel(card, text=dec["descricao"], font=fonte(10), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=12, pady=(0, 10))

            card_inner = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8)
            card_inner.pack(fill="x", padx=10, pady=(0, 10))

            ctk.CTkLabel(card_inner, text="Saldo Final Projetado:", font=fonte(10), text_color=COR_TEXTO_TERCIARIO).pack(anchor="w", padx=10, pady=(8, 0))
            ctk.CTkLabel(card_inner, text=f"R$ {dec['saldo_final']:,.2f}", font=fonte(16, "bold"), text_color=COR_SUCESSO if dec['saldo_final'] >= 0 else COR_ALERTA).pack(anchor="w", padx=10, pady=(0, 6))

            ctk.CTkLabel(card_inner, text=f"Total Gasto em 1 Ano: R$ {dec['total_gasto']:,.2f}", font=fonte(11), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(card_inner, text=f"Economia Gerada: R$ {dec['total_economizado']:,.2f}", font=fonte(11), text_color=COR_AVISO).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(card_inner, text=f"Metas Concluídas: {dec['metas_concluidas']}", font=fonte(11, "bold"), text_color=COR_ACENTO_PRIMARIO).pack(anchor="w", padx=10, pady=(2, 8))

            if dec["nome"] == veredito["campea_saldo"]:
                ctk.CTkLabel(card, text="🏆 Maior Saldo Final", font=fonte(11, "bold"), text_color=COR_ACENTO_PRIMARIO).pack(anchor="w", padx=12, pady=(0, 10))
            elif dec["nome"] == veredito["campea_metas"] and dec["metas_concluidas"] > 0:
                ctk.CTkLabel(card, text="🎯 Campeã em Metas Conquistadas", font=fonte(11, "bold"), text_color=COR_SUCESSO).pack(anchor="w", padx=12, pady=(0, 10))

    # ==============================================================
    # 5. ABA: MAPA DE CONSEQUÊNCIAS FINANCEIRAS
    # ==============================================================
    def _construir_aba_consequencias(self):
        self.frame_consequencias.grid_columnconfigure(0, weight=1)
        self.frame_consequencias.grid_rowconfigure(1, weight=1)

        topo = ctk.CTkFrame(self.frame_consequencias, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        topo.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))

        ctk.CTkLabel(
            topo,
            text="🗺️  MAPA DE CONSEQUÊNCIAS FINANCEIRAS EM CASCATA",
            font=fonte(13, "bold"),
            text_color=COR_ACENTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            topo,
            text="Visualize o efeito dominó de uma decisão em toda a sua vida financeira.",
            font=fonte(11),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(0, 8))

        # Controles do Mapa
        bar_inputs = ctk.CTkFrame(topo, fg_color="transparent")
        bar_inputs.pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkLabel(bar_inputs, text="Decisão:", font=fonte(11), text_color=COR_TEXTO_PRINCIPAL).pack(side="left", padx=(0, 6))
        self.combo_mapa_tipo = ctk.CTkComboBox(bar_inputs, values=["Compra Parcelada", "Investimento / Economia"], width=160, font=fonte(11))
        self.combo_mapa_tipo.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(bar_inputs, text="Valor R$:", font=fonte(11), text_color=COR_TEXTO_PRINCIPAL).pack(side="left", padx=(0, 6))
        self.entry_mapa_valor = ctk.CTkEntry(bar_inputs, placeholder_text="Ex: 3000", width=90, font=fonte(11))
        self.entry_mapa_valor.insert(0, "3000")
        self.entry_mapa_valor.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(bar_inputs, text="Parcelas:", font=fonte(11), text_color=COR_TEXTO_PRINCIPAL).pack(side="left", padx=(0, 6))
        self.entry_mapa_parcelas = ctk.CTkEntry(bar_inputs, placeholder_text="10", width=60, font=fonte(11))
        self.entry_mapa_parcelas.insert(0, "10")
        self.entry_mapa_parcelas.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            bar_inputs,
            text="Simular Efeito Dominó",
            font=fonte(11, "bold"),
            fg_color=COR_ACENTO_PRIMARIO,
            hover_color=COR_ACENTO_HOVER,
            text_color=COR_FUNDO_PRINCIPAL,
            command=self._renderizar_mapa_consequencias,
        ).pack(side="left")

        # Container dos nós em cascata
        self.scroll_mapa = ctk.CTkScrollableFrame(self.frame_consequencias, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        self.scroll_mapa.grid(row=1, column=0, sticky="nsew")
        self.scroll_mapa.grid_columnconfigure(0, weight=1)

    def _renderizar_mapa_consequencias(self):
        try:
            val = float(self.entry_mapa_valor.get().replace(".", "").replace(",", "."))
            parc = int(self.entry_mapa_parcelas.get())
        except ValueError:
            val, parc = 3000.0, 10

        tipo_dec = "compra" if "Compra" in self.combo_mapa_tipo.get() else "investimento"
        lancamentos = self.dao.listar_todos()
        metas = self.meta_dao.listar_todas()

        passos = InteligenciaFinanceiraController.gerar_mapa_consequencias(
            lancamentos=lancamentos,
            metas=metas,
            valor_decisao=val,
            num_parcelas=parc,
            tipo_decisao=tipo_dec,
        )

        for w in self.scroll_mapa.winfo_children():
            w.destroy()

        for idx, p in enumerate(passos):
            # Card do nó
            cor_borda = COR_ALERTA if p["tipo_status"] == "alerta" else (COR_SUCESSO if p["tipo_status"] == "sucesso" else COR_BORDA)
            card_no = ctk.CTkFrame(self.scroll_mapa, fg_color=COR_CARD_INTERNO, corner_radius=10, border_width=1, border_color=cor_borda)
            card_no.pack(fill="x", padx=20, pady=4)
            card_no.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(card_no, text=p["icone"], font=("Segoe UI", 20)).grid(row=0, column=0, rowspan=2, padx=12, pady=10)
            ctk.CTkLabel(card_no, text=f"{p['etapa']} — {p['titulo']}", font=fonte(12, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=1, sticky="w", pady=(8, 0))
            ctk.CTkLabel(card_no, text=p["detalhe"], font=fonte(11), text_color=COR_TEXTO_SECUNDARIO).grid(row=1, column=1, sticky="w", pady=(0, 8))

            # Conector de seta para o próximo nó
            if idx < len(passos) - 1:
                ctk.CTkLabel(self.scroll_mapa, text="↓", font=("Segoe UI", 16, "bold"), text_color=COR_ACENTO_PRIMARIO).pack(pady=1)

    # ==============================================================
    # 6. ABA: SIMULAÇÕES SALVAS (Persistência no SQLite)
    # ==============================================================
    def _construir_aba_salvas(self):
        self.frame_salvas.grid_columnconfigure(0, weight=1)
        self.frame_salvas.grid_rowconfigure(1, weight=1)

        topo = ctk.CTkFrame(self.frame_salvas, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        topo.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 10))

        ctk.CTkLabel(
            topo,
            text="💾  SIMULAÇÕES SALVAS & HISTÓRICO",
            font=fonte(13, "bold"),
            text_color=COR_ACENTO_PRIMARIO,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            topo,
            text="Recupere cenários salvos, compare seus resultados ou exclua simulações antigas.",
            font=fonte(11),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(0, 10))

        self.scroll_lista_salvas = ctk.CTkScrollableFrame(self.frame_salvas, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        self.scroll_lista_salvas.grid(row=1, column=0, sticky="nsew")
        self.scroll_lista_salvas.grid_columnconfigure(0, weight=1)

    def _listar_simulacoes_salvas(self):
        for w in self.scroll_lista_salvas.winfo_children():
            w.destroy()

        simulacoes = self.sim_dao.listar_todas()
        if not simulacoes:
            ctk.CTkLabel(
                self.scroll_lista_salvas,
                text="Nenhuma simulação salva ainda.\nClique em '💾 Salvar Cenário' no topo para salvar sua primeira projeção!",
                font=fonte(12),
                text_color=COR_TEXTO_MUTED,
                justify="center",
            ).pack(pady=40)
            return

        for sim in simulacoes:
            card = ctk.CTkFrame(self.scroll_lista_salvas, fg_color=COR_CARD_INTERNO, corner_radius=10, border_width=1, border_color=COR_BORDA)
            card.pack(fill="x", padx=14, pady=6)
            card.grid_columnconfigure(0, weight=1)

            top_line = ctk.CTkFrame(card, fg_color="transparent")
            top_line.pack(fill="x", padx=12, pady=(10, 2))
            top_line.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(top_line, text=f"📁 {sim['nome']}", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(top_line, text=sim.get("data_criacao", ""), font=fonte(10), text_color=COR_TEXTO_TERCIARIO).grid(row=0, column=1, sticky="e")

            if sim.get("descricao"):
                ctk.CTkLabel(card, text=sim["descricao"], font=fonte(11), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=12, pady=(0, 6))

            res = sim.get("resultados", {})
            saldo_proj = res.get("saldo_final_projetado", 0.0)
            econ_proj = res.get("total_economizado_periodo", 0.0)
            ctk.CTkLabel(card, text=f"Saldo Projetado: R$ {saldo_proj:,.2f} | Economia: R$ {econ_proj:,.2f}", font=fonte(11, "bold"), text_color=COR_SUCESSO if saldo_proj >= 0 else COR_ALERTA).pack(anchor="w", padx=12, pady=(0, 8))

            botoes_card = ctk.CTkFrame(card, fg_color="transparent")
            botoes_card.pack(fill="x", padx=12, pady=(0, 10))

            ctk.CTkButton(
                botoes_card,
                text="📥 Carregar Cenário",
                font=fonte(11, "bold"),
                height=26,
                fg_color=COR_ACENTO_PRIMARIO,
                hover_color=COR_ACENTO_HOVER,
                text_color=COR_FUNDO_PRINCIPAL,
                command=lambda s=sim: self._carregar_simulacao(s),
            ).pack(side="left", padx=(0, 8))

            ctk.CTkButton(
                botoes_card,
                text="🗑️ Excluir",
                font=fonte(11),
                height=26,
                fg_color=COR_ALERTA,
                hover_color=COR_ALERTA_HOVER,
                text_color=COR_FUNDO_PRINCIPAL,
                command=lambda sid=sim["id"]: self._excluir_simulacao(sid),
            ).pack(side="left")

    def _carregar_simulacao(self, sim: Dict[str, Any]):
        params = sim.get("parametros", {})
        self._horizonte_meses = params.get("horizonte_meses", 12)
        self.slider_reducao.set(params.get("reducao_despesas_pct", 0))
        self.slider_renda.set(params.get("aumento_renda_valor", 0))
        self.slider_meta.set(params.get("aporte_extra_metas", 0))
        self._eventos_inesperados = params.get("eventos", [])

        self.lbl_pct_reducao.configure(text=f"{int(params.get('reducao_despesas_pct', 0))}%")
        self.lbl_val_renda.configure(text=f"+ R$ {params.get('aumento_renda_valor', 0):,.2f}")
        self.lbl_val_meta.configure(text=f"+ R$ {params.get('aporte_extra_metas', 0):,.2f}")

        self._alternar_aba("🔮 Projeção & Gráficos")
        self._recalcular()
        self._notificar(f"Cenário '{sim['nome']}' carregado com sucesso!", "sucesso")

    def _excluir_simulacao(self, sim_id: int):
        self.sim_dao.deletar(sim_id)
        self._listar_simulacoes_salvas()
        self._notificar("Simulação excluída.", "info")

    def _abrir_modal_salvar(self):
        modal = ctk.CTkToplevel(self)
        modal.title("Salvar Cenário de Simulação")
        modal.geometry("420x260")
        modal.configure(fg_color=COR_FUNDO_PRINCIPAL)
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        ctk.CTkLabel(modal, text="💾 Salvar Simulação Atual", font=fonte(14, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(padx=20, pady=(16, 6))
        ctk.CTkLabel(modal, text="Dê um nome para identificar este teste financeiro:", font=fonte(11), text_color=COR_TEXTO_SECUNDARIO).pack(padx=20, pady=(0, 10))

        entry_nome = ctk.CTkEntry(modal, placeholder_text="Ex: Viagem de Férias / Novo Emprego", font=fonte(12), fg_color=COR_CARD, border_color=COR_BORDA)
        entry_nome.pack(fill="x", padx=20, pady=(0, 8))

        entry_desc = ctk.CTkEntry(modal, placeholder_text="Descrição ou notas opcionais", font=fonte(11), fg_color=COR_CARD, border_color=COR_BORDA)
        entry_desc.pack(fill="x", padx=20, pady=(0, 14))

        def _confirmar():
            nome = entry_nome.get().strip()
            if not nome:
                return
            desc = entry_desc.get().strip()

            params = {
                "horizonte_meses": self._horizonte_meses,
                "reducao_despesas_pct": self.slider_reducao.get(),
                "aumento_renda_valor": self.slider_renda.get(),
                "aporte_extra_metas": self.slider_meta.get(),
                "eventos": self._eventos_inesperados,
            }
            resumo = self._dados_projecao.get("resumo", {}) if self._dados_projecao else {}

            self.sim_dao.inserir(
                nome=nome,
                descricao=desc,
                parametros=params,
                resultados=resumo,
            )
            modal.destroy()
            self._notificar(f"Simulação '{nome}' salva com sucesso!", "sucesso")

        btn_confirm = ctk.CTkButton(
            modal,
            text="Confirmar e Salvar",
            font=fonte(12, "bold"),
            fg_color=COR_ACENTO_PRIMARIO,
            hover_color=COR_ACENTO_HOVER,
            text_color=COR_FUNDO_PRINCIPAL,
            height=34,
            command=_confirmar,
        )
        btn_confirm.pack(fill="x", padx=20, pady=(0, 10))

    # ==============================================================
    # 7. MOTOR DE CÁLCULO E RENDERIZAÇÃO
    # ==============================================================
    def atualizar_dados(self):
        """Chamado pelo MenuView quando a aba é aberta."""
        cats = [c["nome"] for c in self.cat_dao.listar_todas()]
        self.combo_categoria.configure(values=["Todas as Despesas"] + cats)
        self._recalcular()

    def _recalcular(self):
        lancamentos = self.dao.listar_todos()
        metas = self.meta_dao.listar_todas()
        categorias = self.cat_dao.listar_todas()

        pct_red = self.slider_reducao.get()
        cat_alvo = self.combo_categoria.get()
        aumento_renda = self.slider_renda.get()
        aporte_meta = self.slider_meta.get()

        resultado = InteligenciaFinanceiraController.projetar_futuro_financeiro(
            lancamentos=lancamentos,
            metas=metas,
            categorias=categorias,
            meses_horizonte=self._horizonte_meses,
            reducao_despesas_pct=pct_red,
            categoria_alvo=cat_alvo,
            aumento_renda_valor=aumento_renda,
            aporte_extra_metas=aporte_meta,
            eventos=self._eventos_inesperados,
        )

        self._dados_projecao = resultado
        self._renderizar_resultados(resultado)

    def _renderizar_resultados(self, res: Dict[str, Any]):
        # 1. Atualizar Gráfico
        self.grafico.atualizar_dados(res)

        # 2. Atualizar Cards dos 3 Cenários
        cenarios = res.get("cenarios", {})
        otim = cenarios.get("otimista", {}).get("saldo_final", 0.0)
        norm = cenarios.get("normal", {}).get("saldo_final", 0.0)
        pess = cenarios.get("pessimista", {}).get("saldo_final", 0.0)

        self.lbl_val_otimista.configure(text=f"R$ {otim:,.2f}")
        self.lbl_val_normal.configure(text=f"R$ {norm:,.2f}")
        self.lbl_val_pessimista.configure(text=f"R$ {pess:,.2f}")

        # 3. Atualizar Previsão Inteligente de Metas
        for w in self.container_cards_metas.winfo_children():
            w.destroy()

        metas_prev = res.get("metas", [])
        if not metas_prev:
            ctk.CTkLabel(
                self.container_cards_metas,
                text="Cadastre metas na aba '🎯 Metas' para acompanhar a previsão inteligente de conquista!",
                font=fonte(11),
                text_color=COR_TEXTO_MUTED,
            ).pack(anchor="w", pady=4)
        else:
            for m in metas_prev[:3]:
                card_m = ctk.CTkFrame(self.container_cards_metas, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA)
                card_m.pack(fill="x", pady=3)
                card_m.grid_columnconfigure(1, weight=1)

                ctk.CTkLabel(card_m, text=f"🎯 {m['descricao']}", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=0, padx=10, pady=(6, 2), sticky="w")

                if m["concluida"]:
                    badge_txt = "✅ Concluída!"
                    badge_cor = COR_SUCESSO
                elif m.get("meses_economizados", 0) > 0:
                    badge_txt = f"🚀 Antecipada em {m['meses_economizados']} mês(es)!"
                    badge_cor = COR_SUCESSO
                else:
                    badge_txt = "Em andamento"
                    badge_cor = COR_TEXTO_SECUNDARIO

                ctk.CTkLabel(card_m, text=badge_txt, font=fonte(10, "bold"), text_color=badge_cor).grid(row=0, column=1, padx=10, pady=(6, 2), sticky="e")

                detalhe = (
                    f"Previsão estimada: {m.get('data_estimada_simulada', 'N/D')} • "
                    f"Alvo: R$ {m['valor_alvo']:,.2f} (Restam R$ {m['restante']:,.2f})"
                )
                ctk.CTkLabel(card_m, text=detalhe, font=fonte(10), text_color=COR_TEXTO_SECUNDARIO).grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 6), sticky="w")

    # ==============================================================
    # 8. CONSULTORIA DE IA EM THREAD (Assíncrona)
    # ==============================================================
    def _solicitar_analise_ia(self):
        self.lbl_texto_ia.configure(text="🤖 Analisando seu cenário financeiro com inteligência artificial... Aguarde alguns instantes.")

        def _worker():
            try:
                analise = self.ai_service.analisar_simulacao_financeira(self._dados_projecao)
                # Voltar para a thread da interface
                self.after(0, lambda: self._exibir_analise_ia(analise))
            except Exception as exc:
                self.after(0, lambda: self._exibir_analise_ia(f"Não foi possível gerar a análise da IA: {exc}"))

        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()

    def _exibir_analise_ia(self, texto: str):
        self.lbl_texto_ia.configure(text=texto)
        self._notificar("Parecer da IA atualizado!", "sucesso")
