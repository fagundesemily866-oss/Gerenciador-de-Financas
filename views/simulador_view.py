"""
View do Simulador de Cenários — Redesign Fiel à Referência (05_simulador_de_cenarios.png)
========================================================================================

Laboratório de decisões financeiras e simulação preditiva:
1. Topo: Tag 'PLANEJE SEU FUTURO', título explicativo e botões Carregar / Salvar Cenário.
2. Painel Esquerdo: Configuração do Cenário com seletor de horizonte temporal (3m, 6m, 1 ano, 2 anos, 5 anos),
   sliders de corte de despesas (%), aumento de renda extra (R$) e aporte em metas (R$), com botões de ação.
3. Abas Centrais: Comparação de Cenários, Consequências e Visão por Metas.
4. Painel Central: Gráfico vetorial de evolução temporal no Canvas com curvas Otimista (Verde),
   Planejado (Azul) e Pessimista (Vermelho) com legenda de valores flutuante.
5. 3 Cards Comparativos de Cenários com badges, valores projetados e acumulados.
6. Seção Inferior: Principais Consequências e Parecer Inteligente da IA.
"""
import tkinter as tk
from datetime import datetime, date
from typing import Optional, Dict, Any, List
import customtkinter as ctk

from dao.lancamento_dao import LancamentoDAO
from dao.meta_dao import MetaDAO
from dao.categoria_dao import CategoriaDAO
from dao.simulacao_dao import SimulacaoDAO
from services.ai_service import AIService
from services.simulador_cenarios import simular, frase_meta
from views.notificacao_toast import GerenciadorNotificacoes
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_ACENTO_ROXO, COR_SUCESSO, COR_ALERTA, COR_INFO,
    fonte, fonte_titulo, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
    obter_cor
)


class SimuladorView(ctk.CTkFrame):
    """Tela do Simulador de Cenários redesenhada fiel à imagem 05_simulador_de_cenarios.png."""

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

        # Parâmetros da Simulação
        self.horizonte_anos = 1  # 1 ano padrão
        self.corte_despesas_pct = 15.0
        self.renda_extra_mensal = 0.0
        self.aporte_metas_mensal = 0.0
        self.aba_ativa = "Comparação"
        self.visao_saldo = "Saldo Total"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._montar_tela()

    def atualizar_dados(self):
        self._montar_tela()

    def _montar_tela(self):
        for w in self.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # 1. CABEÇALHO
        self._build_header(scroll)

        # 2. CORPO (PAINEL ESQUERDO + CONTEÚDO PRINCIPAL DIREITO)
        corpo = ctk.CTkFrame(scroll, fg_color="transparent")
        corpo.pack(fill="both", expand=True, pady=(0, 10))
        corpo.grid_columnconfigure(0, weight=3)
        corpo.grid_columnconfigure(1, weight=7)

        self._build_painel_configuracao(corpo)
        self._build_painel_resultados(corpo)

    # ==============================================================
    # 1. CABEÇALHO
    # ==============================================================
    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)

        tit_box = ctk.CTkFrame(header, fg_color="transparent")
        tit_box.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            tit_box,
            text="PLANEJE SEU FUTURO",
            font=fonte(10, "bold"),
            text_color="#00D084",
            anchor="w",
        ).pack(anchor="w")

        t_row = ctk.CTkFrame(tit_box, fg_color="transparent")
        t_row.pack(anchor="w")
        ctk.CTkLabel(t_row, text="Simulador de Cenários", font=fonte(22, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")
        ctk.CTkLabel(t_row, text=" ⓘ", font=fonte(14), text_color=COR_TEXTO_MUTED).pack(side="left")

        ctk.CTkLabel(
            tit_box,
            text="Descubra como diferentes decisões financeiras podem impactar seus resultados ao longo do tempo.",
            font=fonte(12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Botões de Ação Topo Direito
        btn_box = ctk.CTkFrame(header, fg_color="transparent")
        btn_box.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            btn_box,
            text="📂  Carregar Cenário",
            height=36,
            corner_radius=8,
            fg_color=COR_CARD,
            hover_color=COR_CARD_INTERNO,
            border_width=1,
            border_color=COR_BORDA,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(11, "bold"),
            command=self._carregar_cenario,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_box,
            text="💾  Salvar Cenário",
            height=36,
            corner_radius=8,
            fg_color="#00D084",
            hover_color="#00B875",
            text_color="#0B131B",
            font=fonte(11, "bold"),
            command=self._salvar_cenario,
        ).pack(side="left")

    # ==============================================================
    # 2. PAINEL ESQUERDO: CONFIGURAÇÃO DO CENÁRIO
    # ==============================================================
    def _build_painel_configuracao(self, parent):
        card = ctk.CTkFrame(
            parent,
            fg_color=COR_CARD,
            corner_radius=14,
            border_width=1,
            border_color=COR_BORDA,
        )
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Topo
        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 12))

        ctk.CTkLabel(topo, text="⚙  Configuração do Cenário", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(topo, text="Ajuste os parâmetros e veja o impacto no seu futuro.", font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        # 1. Horizonte de Tempo
        ctk.CTkLabel(card, text="📅  Horizonte de Tempo", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 6))

        h_box = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, height=36)
        h_box.pack(fill="x", padx=16, pady=(0, 14))

        horizontes = [("3 Meses", 0.25), ("6 Meses", 0.5), ("1 Ano", 1), ("2 Anos", 2), ("5 Anos", 5)]
        for rotulo, val in horizontes:
            ativo = (val == self.horizonte_anos)
            ctk.CTkButton(
                h_box,
                text=rotulo,
                height=28,
                corner_radius=6,
                fg_color="#00D084" if ativo else "transparent",
                text_color="#0B131B" if ativo else COR_TEXTO_SECUNDARIO,
                font=fonte(10, "bold" if ativo else "normal"),
                command=lambda v=val: self._set_horizonte(v),
            ).pack(side="left", fill="both", expand=True, padx=2, pady=4)

        # 2. % Corte de Despesas
        top_s1 = ctk.CTkFrame(card, fg_color="transparent")
        top_s1.pack(fill="x", padx=16, pady=(0, 2))
        ctk.CTkLabel(top_s1, text="%  Corte de Despesas", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")
        self.lbl_val_corte = ctk.CTkLabel(top_s1, text=f"{int(self.corte_despesas_pct)}%", font=fonte(11, "bold"), text_color="#00D084")
        self.lbl_val_corte.pack(side="right")

        ctk.CTkLabel(card, text="Redução nas despesas mensais", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 6))

        self.slider_corte = ctk.CTkSlider(
            card,
            from_=0,
            to=50,
            number_of_steps=10,
            progress_color="#00D084",
            button_color="#00D084",
            button_hover_color="#00B875",
            command=self._on_change_corte,
        )
        self.slider_corte.set(self.corte_despesas_pct)
        self.slider_corte.pack(fill="x", padx=16, pady=(0, 2))

        # Marcações do slider
        marks1 = ctk.CTkFrame(card, fg_color="transparent")
        marks1.pack(fill="x", padx=16, pady=(0, 6))
        for m in ["0%", "10%", "20%", "30%", "50%"]:
            ctk.CTkLabel(marks1, text=m, font=fonte(8), text_color=COR_TEXTO_MUTED).pack(side="left", expand=True)

        ctk.CTkLabel(card, text="Aplicar redução em:", font=fonte(10), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 2))
        combo_aplica = ctk.CTkOptionMenu(
            card,
            values=["Todas as Despesas", "Despesas Variáveis", "Lazer e Outros"],
            height=32,
            corner_radius=8,
            fg_color=COR_CARD_INTERNO,
            button_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(11),
        )
        combo_aplica.set("Todas as Despesas")
        combo_aplica.pack(fill="x", padx=16, pady=(0, 14))

        # 3. Aumento de Renda Extra
        top_s2 = ctk.CTkFrame(card, fg_color="transparent")
        top_s2.pack(fill="x", padx=16, pady=(0, 2))
        ctk.CTkLabel(top_s2, text="↑  Aumento de Renda Extra", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")
        self.lbl_val_renda = ctk.CTkLabel(top_s2, text=f"R$ {self.renda_extra_mensal:,.2f}", font=fonte(11, "bold"), text_color="#00D084")
        self.lbl_val_renda.pack(side="right")

        ctk.CTkLabel(card, text="Valor adicional por mês", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 6))

        self.slider_renda = ctk.CTkSlider(
            card,
            from_=0,
            to=2000,
            number_of_steps=20,
            progress_color="#00D084",
            button_color="#00D084",
            button_hover_color="#00B875",
            command=self._on_change_renda,
        )
        self.slider_renda.set(self.renda_extra_mensal)
        self.slider_renda.pack(fill="x", padx=16, pady=(0, 2))

        marks2 = ctk.CTkFrame(card, fg_color="transparent")
        marks2.pack(fill="x", padx=16, pady=(0, 14))
        for m in ["R$ 0", "R$ 500", "R$ 1.000", "R$ 2.000"]:
            ctk.CTkLabel(marks2, text=m, font=fonte(8), text_color=COR_TEXTO_MUTED).pack(side="left", expand=True)

        # 4. Aporte Mensal para Metas
        top_s3 = ctk.CTkFrame(card, fg_color="transparent")
        top_s3.pack(fill="x", padx=16, pady=(0, 2))
        ctk.CTkLabel(top_s3, text="🎯  Aporte Mensal para Metas", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")
        self.lbl_val_aporte = ctk.CTkLabel(top_s3, text="Automático" if self.aporte_metas_mensal <= 0 else f"R$ {self.aporte_metas_mensal:,.2f}", font=fonte(11, "bold"), text_color="#00D084")
        self.lbl_val_aporte.pack(side="right")

        ctk.CTkLabel(card, text="Valor que será investido mensalmente", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 6))

        self.slider_aporte = ctk.CTkSlider(
            card,
            from_=0,
            to=2000,
            number_of_steps=20,
            progress_color="#00D084",
            button_color="#00D084",
            button_hover_color="#00B875",
            command=self._on_change_aporte,
        )
        self.slider_aporte.set(self.aporte_metas_mensal)
        self.slider_aporte.pack(fill="x", padx=16, pady=(0, 2))

        marks3 = ctk.CTkFrame(card, fg_color="transparent")
        marks3.pack(fill="x", padx=16, pady=(0, 18))
        for m in ["R$ 0", "R$ 300", "R$ 1.000", "R$ 2.000"]:
            ctk.CTkLabel(marks3, text=m, font=fonte(8), text_color=COR_TEXTO_MUTED).pack(side="left", expand=True)

        # Botões de Ação
        botoes = ctk.CTkFrame(card, fg_color="transparent")
        botoes.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(
            botoes,
            text="🔄  Limpar",
            height=38,
            width=90,
            corner_radius=8,
            fg_color=COR_CARD_INTERNO,
            hover_color="#1E2F40",
            text_color=COR_TEXTO_SECUNDARIO,
            font=fonte(11),
            command=self._reset_parametros,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            botoes,
            text="▶  Atualizar Simulação",
            height=38,
            corner_radius=8,
            fg_color="#00D084",
            hover_color="#00B875",
            text_color="#0B131B",
            font=fonte(11, "bold"),
            command=self._montar_tela,
        ).pack(side="left", fill="x", expand=True)

    def _set_horizonte(self, h):
        self.horizonte_anos = h
        self._montar_tela()

    def _on_change_corte(self, val):
        val_fixo = round(float(val) / 5.0) * 5.0
        self.corte_despesas_pct = val_fixo
        try:
            self.slider_corte.set(val_fixo)
        except Exception:
            pass
        self.lbl_val_corte.configure(text=f"{int(val_fixo)}%")
        self._agendar_atualizacao_drag()

    def _on_change_renda(self, val):
        val_fixo = round(float(val) / 50.0) * 50.0
        self.renda_extra_mensal = val_fixo
        try:
            self.slider_renda.set(val_fixo)
        except Exception:
            pass
        self.lbl_val_renda.configure(text=f"R$ {val_fixo:,.2f}")
        self._agendar_atualizacao_drag()

    def _on_change_aporte(self, val):
        val_fixo = round(float(val) / 50.0) * 50.0
        self.aporte_metas_mensal = val_fixo
        try:
            self.slider_aporte.set(val_fixo)
        except Exception:
            pass
        self.lbl_val_aporte.configure(text="Automático" if val_fixo <= 0 else f"R$ {val_fixo:,.2f}")
        self._agendar_atualizacao_drag()

    def _agendar_atualizacao_drag(self):
        """Atualização reativa em tempo real com debounce ao arrastar os sliders."""
        if hasattr(self, "_drag_timer") and self._drag_timer:
            try:
                self.after_cancel(self._drag_timer)
            except Exception:
                pass
        self._drag_timer = self.after(80, self._atualizar_projecao_live)

    def _atualizar_projecao_live(self):
        if hasattr(self, "_desenhar_grafico_func"):
            self._desenhar_grafico_func()
        if hasattr(self, "_atualizar_cards_dinamicos"):
            self._atualizar_cards_dinamicos()

    def _reset_parametros(self):
        self.corte_despesas_pct = 15.0
        self.renda_extra_mensal = 0.0
        self.aporte_metas_mensal = 0.0
        self._montar_tela()

    def _carregar_cenario(self):
        pass

    def _salvar_cenario(self):
        try:
            self.sim_dao.inserir(
                nome=f"Simulação {datetime.now().strftime('%d/%m %H:%M')}",
                parametros={
                    "horizonte_meses": int(round(self.horizonte_anos * 12)),
                    "corte_despesas": self.corte_despesas_pct,
                    "renda_extra": self.renda_extra_mensal,
                    "aporte_metas": self.aporte_metas_mensal,
                },
            )
        except Exception:
            pass

    # ==============================================================
    # 3. PAINEL DIREITO: RESULTADOS (dados reais via services.simulador_cenarios)
    # ==============================================================
    _CORES = {
        "otimista": ("🍃", "#0D2E2B", "#00D084"),
        "planejado": ("🎯", "#122538", "#38BDF8"),
        "pessimista": ("⚠️", "#2E151B", "#F43F5E"),
    }
    _STATUS = {  # status da meta -> (rótulo, cor)
        "antes": ("✔ Antes do prazo", "#00D084"),
        "no_prazo": ("✔ Dentro do prazo", "#38BDF8"),
        "atrasada": ("✖ Atrasada", "#F43F5E"),
        "sem_prazo": ("• Sem prazo", "#94A3B8"),
        "sem_aporte": ("✖ Sem aporte", "#F43F5E"),
        "concluida": ("✔ Meta concluída", "#00D084"),
    }
    _ABAS = ["⚖ Comparação", "📑 Consequências", "🎯 Visão por Metas"]

    @staticmethod
    def _brl(v: float) -> str:
        return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _calcular(self, metas=None):
        """Usa o MetaDAO (MySQL/migrations), o mesmo da tela Minhas Metas."""
        if metas is None:
            metas = self.meta_dao.listar_todas()
        return simular(
            self.dao.listar_todos(),
            metas,
            max(1, int(round(self.horizonte_anos * 12))),
            self.corte_despesas_pct,
            self.renda_extra_mensal,
            self.aporte_metas_mensal,
        )

    def _build_painel_resultados(self, parent):
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self._abas_box = ctk.CTkFrame(col, fg_color=COR_CARD, corner_radius=10, border_width=1, border_color=COR_BORDA, height=40)
        self._abas_box.pack(fill="x", pady=(0, 12))
        self._desenhar_abas()

        self._area_result = ctk.CTkFrame(col, fg_color="transparent")
        self._area_result.pack(fill="x")
        self._render_resultados()

    def _desenhar_abas(self):
        for w in self._abas_box.winfo_children():
            w.destroy()
        self._abas_box.grid_columnconfigure(tuple(range(len(self._ABAS))), weight=1, uniform="aba")
        for i, a_txt in enumerate(self._ABAS):
            ativo = (self.aba_ativa in a_txt)
            ctk.CTkButton(
                self._abas_box, text=a_txt, height=30, corner_radius=8,
                fg_color="#0D2E2B" if ativo else "transparent",
                text_color="#00D084" if ativo else COR_TEXTO_SECUNDARIO,
                font=fonte(11, "bold" if ativo else "normal"),
                command=lambda a=a_txt.split()[1]: self._set_aba(a),
            ).grid(row=0, column=i, sticky="ew", padx=4, pady=4)

    def _set_aba(self, a: str):
        self.aba_ativa = a
        self._desenhar_abas()
        self._render_resultados()

    def _atualizar_projecao_live(self):
        """Chamado ao arrastar sliders: recalcula só a área de resultados."""
        if hasattr(self, "_area_result") and self._area_result.winfo_exists():
            self._render_resultados()

    def _render_resultados(self):
        for w in self._area_result.winfo_children():
            w.destroy()

        if self.aba_ativa == "Visão":
            # Busca novamente as metas no MySQL a cada abertura/atualização da aba.
            # Não depender de ter lançamentos para exibir metas já cadastradas.
            metas = self.meta_dao.listar_todas()
            res = self._calcular(metas=metas)
            self._res = res
            self._build_visao_metas(self._area_result, res, metas=metas)
            return

        res = self._calcular()
        if res is None:
            card = ctk.CTkFrame(self._area_result, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
            card.pack(fill="x")
            ctk.CTkLabel(card, text="Ainda não há lançamentos para simular.", font=fonte(14, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(pady=(24, 4))
            ctk.CTkLabel(card, text='Cadastre receitas e despesas (ou use "Criar finanças aleatórias" ao criar a conta) para ver os cenários.',
                         font=fonte(11), text_color=COR_TEXTO_MUTED, wraplength=520).pack(pady=(0, 24), padx=16)
            return
        self._res = res
        if self.aba_ativa == "Comparação":
            self._build_cards_cenarios(self._area_result, res)
            self._build_tabela_comparacao(self._area_result, res)
        else:
            self._build_consequencias(self._area_result, res)

    def _card(self, parent, titulo, subtitulo=None):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(card, text=titulo, font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w", padx=16, pady=(12, 0))
        if subtitulo:
            ctk.CTkLabel(card, text=subtitulo, font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w", wraplength=560, justify="left").pack(anchor="w", padx=16)
        return card

    # ---------------- Cards dos 3 cenários ----------------
    def _build_cards_cenarios(self, parent, res):
        """Três cards lado a lado; em área estreita empilham em uma coluna (sem cortar texto)."""
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 12))
        cards = []
        for k, c in res["cenarios"].items():
            ic, bg, cor = self._CORES[k]
            card = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=cor)
            ctk.CTkLabel(card, text=f"{ic}  {c['nome']}", font=fonte(12, "bold"), text_color=cor, anchor="w").pack(fill="x", padx=12, pady=(12, 2))
            ctk.CTkLabel(card, text=self._brl(c["saldo_final"]), font=fonte(16, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(fill="x", padx=12)
            ctk.CTkLabel(card, text="acumulado ao final", font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(fill="x", padx=12)
            ctk.CTkLabel(card, text="Economizado", font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(fill="x", padx=12, pady=(8, 0))
            ctk.CTkLabel(card, text=self._brl(c["economizado"]), font=fonte(11, "bold"), text_color=COR_TEXTO_SECUNDARIO, anchor="w").pack(fill="x", padx=12)
            if k != "planejado":
                d = c["diferenca_vs_planejado"]
                ctk.CTkLabel(card, text=f"{'+' if d >= 0 else '-'}{self._brl(abs(d))}", font=fonte(11, "bold"),
                             text_color="#00D084" if d >= 0 else "#F43F5E", anchor="w").pack(fill="x", padx=12, pady=(8, 0))
                ctk.CTkLabel(card, text="vs planejado", font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(fill="x", padx=12, pady=(0, 12))
            else:
                ctk.CTkLabel(card, text="Cenário base", font=fonte(11, "bold"), text_color=COR_TEXTO_SECUNDARIO, anchor="w").pack(fill="x", padx=12, pady=(8, 0))
                ctk.CTkLabel(card, text="referência de comparação", font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(fill="x", padx=12, pady=(0, 12))
            cards.append(card)

        estado = {"cols": None}

        def reflow(_e=None):
            cols = 3 if grid.winfo_width() >= 600 else 1
            if cols == estado["cols"]:
                return
            estado["cols"] = cols
            for i in range(3):
                grid.grid_columnconfigure(i, weight=1 if i < cols else 0, uniform="cen" if i < cols else "")
            for i, card in enumerate(cards):
                if cols == 3:
                    card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 5, 0 if i == 2 else 5), pady=0)
                else:
                    card.grid(row=i, column=0, sticky="ew", padx=0, pady=(0 if i == 0 else 8, 0))

        grid.bind("<Configure>", reflow)
        reflow()

    # ---------------- Comparação ----------------
    def _build_tabela_comparacao(self, parent, res):
        card = self._card(parent, "⚖  Comparação de Cenários", "Receitas e despesas do período e o que sobra em cada cenário.")
        tab = ctk.CTkFrame(card, fg_color="transparent")
        tab.pack(fill="x", padx=16, pady=(8, 12))
        tab.grid_columnconfigure((0, 1, 2, 3), weight=1)
        for j, tit in enumerate(["", "Otimista", "Planejado", "Pessimista"]):
            ctk.CTkLabel(tab, text=tit, font=fonte(11, "bold"), text_color=COR_TEXTO_SECUNDARIO).grid(row=0, column=j, sticky="w", pady=2)
        linhas = [("Receitas", "receitas_acumuladas"), ("Despesas", "despesas_acumuladas"),
                  ("Economizado", "economizado"), ("Saldo final", "saldo_final"), ("Dif. vs planejado", "diferenca_vs_planejado")]
        for r, (rot, chave) in enumerate(linhas, start=1):
            ctk.CTkLabel(tab, text=rot, font=fonte(11), text_color=COR_TEXTO_MUTED).grid(row=r, column=0, sticky="w", pady=2)
            for j, k in enumerate(("otimista", "planejado", "pessimista"), start=1):
                v = res["cenarios"][k][chave]
                cor = COR_TEXTO_PRINCIPAL if chave != "diferenca_vs_planejado" else ("#00D084" if v >= 0 else "#F43F5E")
                ctk.CTkLabel(tab, text=self._brl(v), font=fonte(11), text_color=cor).grid(row=r, column=j, sticky="w", pady=2)

    # ---------------- Consequências ----------------
    def _build_consequencias(self, parent, res, resumido: bool = False):
        card = self._card(parent, "📑  Principais Consequências", "O que acontece com você em cada cenário.")
        chaves = ("planejado",) if resumido else ("otimista", "planejado", "pessimista")
        for k in chaves:
            c = res["cenarios"][k]
            ic, _, cor = self._CORES[k]
            ctk.CTkLabel(card, text=f"{ic}  {c['nome']}", font=fonte(12, "bold"), text_color=cor).pack(anchor="w", padx=16, pady=(10, 2))
            for item in c["consequencias"]:
                marca, cc = {"bom": ("✔", "#00D084"), "ruim": ("✖", "#F43F5E")}.get(item["tipo"], ("•", COR_TEXTO_SECUNDARIO))
                ctk.CTkLabel(card, text=f"{marca}  {item['texto']}", font=fonte(11), text_color=cc if item["tipo"] != "info" else COR_TEXTO_SECUNDARIO,
                             anchor="w", justify="left", wraplength=540).pack(anchor="w", padx=24, pady=1)
        if resumido:
            ctk.CTkLabel(card, text="Veja os três cenários na aba “Consequências”.", font=fonte(10), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(8, 0))
        ctk.CTkFrame(card, height=8, fg_color="transparent").pack()

    # ---------------- Visão por Metas ----------------
    @staticmethod
    def _formatar_prazo(valor) -> str:
        """Exibe a data real da meta, vinda de meta_reserva.data_limite."""
        if isinstance(valor, (date, datetime)):
            return valor.strftime("%d/%m/%Y")
        if not valor:
            return ""
        try:
            return datetime.strptime(str(valor)[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            return str(valor)

    def _build_visao_metas(self, parent, res, metas=None):
        """Mostra TODAS as metas reais: em andamento e concluídas.

        Se faltam lançamentos, mostra os valores reais sem inventar projeções.
        """
        metas = metas if metas is not None else self.meta_dao.listar_todas()
        resumo = ctk.CTkFrame(parent, fg_color="transparent")
        resumo.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            resumo, text=f"{len(metas)} meta(s) cadastrada(s)",
            font=fonte(11), text_color=COR_TEXTO_SECUNDARIO,
        ).pack(side="left")
        ctk.CTkButton(
            resumo, text="↻  Atualizar metas", width=130, height=28,
            fg_color=COR_CARD_INTERNO, hover_color=COR_CARD,
            border_width=1, border_color=COR_BORDA,
            text_color=COR_TEXTO_PRINCIPAL, font=fonte(10),
            command=self._render_resultados,
        ).pack(side="right")

        if not metas:
            card = self._card(parent, "🎯  Visão por Metas")
            ctk.CTkLabel(
                card, text="Nenhuma meta cadastrada. Crie uma meta em 'Minhas Metas' para acompanhá-la aqui.",
                font=fonte(11), text_color=COR_TEXTO_MUTED,
                wraplength=520, justify="left",
            ).pack(anchor="w", padx=16, pady=(8, 20))
            return

        if res is None:
            aviso = self._card(
                parent, "Projeções indisponíveis",
                "Suas metas já aparecem abaixo com os valores reais. Cadastre receitas e despesas "
                "para ver a comparação dos cenários otimista, planejado e pessimista.",
            )
            ctk.CTkFrame(aviso, height=10, fg_color="transparent").pack()
            metas_exibidas = []
            for m in metas:
                alvo = float(m.get("valor_alvo") or 0)
                atual = float(m.get("valor_atual") or 0)
                concluida = bool(m.get("concluida")) or (alvo > 0 and atual >= alvo)
                metas_exibidas.append({
                    "nome": m.get("descricao") or "Meta",
                    "atual": atual, "alvo": alvo,
                    "restante": max(0.0, alvo - atual),
                    "pct_atual": min(100.0, 100 * atual / alvo) if alvo > 0 else 0,
                    "prazo": m.get("data_limite"),
                    "status": "concluida" if concluida else "sem_projecao",
                })
        else:
            metas_exibidas = res["cenarios"]["planejado"]["metas"]

        for idx, mp in enumerate(metas_exibidas):
            prazo = self._formatar_prazo(mp.get("prazo"))
            subtitulo = (
                f"{self._brl(mp['atual'])} de {self._brl(mp['alvo'])}"
                f"  •  faltam {self._brl(mp['restante'])}"
                + (f"  •  prazo {prazo}" if prazo else "")
            )
            card = self._card(parent, f"🎯  {mp['nome']}", subtitulo)
            barra = ctk.CTkProgressBar(card, height=10, progress_color="#00D084")
            barra.pack(fill="x", padx=16, pady=(10, 0))
            barra.set(max(0.0, min(1.0, mp["pct_atual"] / 100)))
            ctk.CTkLabel(
                card, text=f"{mp['pct_atual']:.0f}% do valor-alvo guardado",
                font=fonte(10), text_color=COR_TEXTO_MUTED,
            ).pack(anchor="w", padx=16, pady=(4, 0))

            if mp["status"] == "concluida":
                ctk.CTkLabel(
                    card, text="✔  Meta concluída — os valores acima são os reais do banco.",
                    font=fonte(11, "bold"), text_color="#00D084",
                    wraplength=500, justify="left",
                ).pack(anchor="w", padx=16, pady=(8, 16))
                continue

            if res is None:
                ctk.CTkLabel(
                    card, text="Em andamento  •  aguardando lançamentos para calcular projeções.",
                    font=fonte(10), text_color=COR_TEXTO_SECUNDARIO,
                    wraplength=500, justify="left",
                ).pack(anchor="w", padx=16, pady=(8, 16))
                continue

            linha = ctk.CTkFrame(card, fg_color="transparent")
            linha.pack(fill="x", padx=12, pady=(8, 12))
            caixas = []
            for k in ("otimista", "planejado", "pessimista"):
                m = res["cenarios"][k]["metas"][idx]
                _, _, cor = self._CORES[k]
                rotulo, cor_status = self._STATUS[m["status"]]
                box = ctk.CTkFrame(linha, fg_color=COR_CARD_INTERNO, corner_radius=8,
                                   border_width=1, border_color=cor_status)
                ctk.CTkLabel(box, text=res["cenarios"][k]["nome"], font=fonte(10, "bold"), text_color=cor).pack(anchor="w", padx=10, pady=(8, 0))
                ctk.CTkLabel(box, text=rotulo, font=fonte(11, "bold"), text_color=cor_status).pack(anchor="w", padx=10)
                tempo = f"{m['meses']} meses" if m["meses"] is not None else "—"
                ctk.CTkLabel(box, text=f"Atinge em: {tempo}", font=fonte(10), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=10)
                ctk.CTkLabel(box, text=f"Aporte: {self._brl(m['aporte_mensal'])}/mês", font=fonte(10), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=10)
                ctk.CTkLabel(box, text=f"Previsão: {m['pct_fim_horizonte']:.0f}% em {res['horizonte']}m", font=fonte(10), text_color=COR_TEXTO_SECUNDARIO).pack(anchor="w", padx=10)
                if m["falta_no_prazo"] is not None and m["falta_no_prazo"] > 0:
                    ctk.CTkLabel(box, text=f"Faltaria no prazo: {self._brl(m['falta_no_prazo'])}", font=fonte(10), text_color="#F43F5E").pack(anchor="w", padx=10)
                ctk.CTkLabel(
                    box, text=frase_meta(m, res["cenarios"][k]["nome"].lower()),
                    font=fonte(10, "bold"), text_color=cor_status,
                    wraplength=300, justify="left", anchor="w",
                ).pack(fill="x", padx=10, pady=(4, 8))
                caixas.append(box)

            # Em áreas pequenas empilha os cenários, evitando textos cortados.
            estado = {"colunas": None}

            def reorganizar(_evento=None, *, painel=linha, cards=caixas, memoria=estado):
                colunas = 3 if painel.winfo_width() >= 660 else 1
                if colunas == memoria["colunas"]:
                    return
                memoria["colunas"] = colunas
                for j in range(3):
                    painel.grid_columnconfigure(j, weight=1 if j < colunas else 0)
                for j, caixa in enumerate(cards):
                    coluna = j if colunas == 3 else 0
                    linha_idx = 0 if colunas == 3 else j
                    caixa.grid(row=linha_idx, column=coluna, sticky="nsew",
                               padx=4, pady=(0 if linha_idx == 0 else 8, 0))

            linha.bind("<Configure>", reorganizar)
            reorganizar()
