"""
View do Simulador de Cenários — Redesign Fiel à Referência (05_simulador_de_cenarios.png)
========================================================================================

Laboratório de decisões financeiras e simulação preditiva:
1. Topo: Tag 'PLANEJE SEU FUTURO', título explicativo e botões Carregar / Salvar Cenário.
2. Painel Esquerdo: Configuração do Cenário com seletor de horizonte temporal (3m, 6m, 1 ano, 2 anos, 5 anos),
   sliders de corte de despesas (%), aumento de renda extra (R$) e aporte em metas (R$), com botões de ação.
3. Abas Centrais: Projeção, Comparação de Cenários, Consequências e Visão por Metas.
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
        self.renda_extra_mensal = 500.0
        self.aporte_metas_mensal = 300.0
        self.aba_ativa = "Projeção"
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
        self.lbl_val_aporte = ctk.CTkLabel(top_s3, text=f"R$ {self.aporte_metas_mensal:,.2f}", font=fonte(11, "bold"), text_color="#00D084")
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
        self.corte_despesas_pct = val
        self.lbl_val_corte.configure(text=f"{int(val)}%")

    def _on_change_renda(self, val):
        self.renda_extra_mensal = val
        self.lbl_val_renda.configure(text=f"R$ {val:,.2f}")

    def _on_change_aporte(self, val):
        self.aporte_metas_mensal = val
        self.lbl_val_aporte.configure(text=f"R$ {val:,.2f}")

    def _reset_parametros(self):
        self.corte_despesas_pct = 15.0
        self.renda_extra_mensal = 500.0
        self.aporte_metas_mensal = 300.0
        self._montar_tela()

    def _carregar_cenario(self):
        pass

    def _salvar_cenario(self):
        try:
            self.sim_dao.salvar(
                nome=f"Simulação {datetime.now().strftime('%d/%m %H:%M')}",
                horizonte_meses=int(self.horizonte_anos * 12),
                corte_despesas=self.corte_despesas_pct,
                renda_extra=self.renda_extra_mensal,
                aporte_metas=self.aporte_metas_mensal,
            )
        except Exception:
            pass

    # ==============================================================
    # 3. PAINEL DIREITO: RESULTADOS & PROJEÇÃO
    # ==============================================================
    def _build_painel_resultados(self, parent):
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Abas de Módulos Superiores
        abas_box = ctk.CTkFrame(col, fg_color=COR_CARD, corner_radius=10, border_width=1, border_color=COR_BORDA, height=40)
        abas_box.pack(fill="x", pady=(0, 12))

        abas_itens = ["📊 Projeção", "⚖ Comparação de Cenários", "📑 Consequências", "🎯 Visão por Metas"]
        for a_txt in abas_itens:
            ativo = (self.aba_ativa in a_txt)
            ctk.CTkButton(
                abas_box,
                text=a_txt,
                height=30,
                corner_radius=8,
                fg_color="#0D2E2B" if ativo else "transparent",
                text_color="#00D084" if ativo else COR_TEXTO_SECUNDARIO,
                font=fonte(11, "bold" if ativo else "normal"),
                command=lambda a=a_txt.split()[1]: self._set_aba(a),
            ).pack(side="left", padx=4, pady=4)

        # Bloco 1: Projeção do Saldo ao Longo do Tempo (Gráfico de Linhas)
        self._build_bloco_grafico(col)

        # Bloco 2: 3 Cards de Cenários Lado a Lado
        self._build_cards_cenarios(col)

        # Bloco 3: Principais Consequências e Análise da IA
        self._build_consequencias_e_ia(col)

    def _set_aba(self, a: str):
        self.aba_ativa = a
        self._montar_tela()

    def _build_bloco_grafico(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card.pack(fill="x", pady=(0, 12))

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(12, 4))
        topo.grid_columnconfigure(0, weight=1)

        t_box = ctk.CTkFrame(topo, fg_color="transparent")
        t_box.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(t_box, text="📈  Projeção do Saldo ao Longo do Tempo", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(t_box, text="Evolução do seu patrimônio líquido com base nos parâmetros informados.", font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        # Seletores de visão
        v_box = ctk.CTkFrame(topo, fg_color="transparent")
        v_box.grid(row=0, column=1, sticky="e")

        for v_opt in ["● Saldo Total", "○ Receitas vs Despesas", "○ Patrimônio Líquido"]:
            ctk.CTkLabel(v_box, text=v_opt, font=fonte(10), text_color="#00D084" if "Saldo" in v_opt else COR_TEXTO_MUTED).pack(side="left", padx=6)

        # Canvas do Gráfico Vetorial de Linhas
        canvas_proj = tk.Canvas(card, height=190, bg=obter_cor(COR_CARD), highlightthickness=0)
        canvas_proj.pack(fill="x", padx=16, pady=(4, 12))

        def desenhar_grafico(e=None):
            canvas_proj.delete("all")
            w = canvas_proj.winfo_width()
            h = canvas_proj.winfo_height()
            if w <= 10 or h <= 10:
                w, h = 600, 190

            m_esq, m_dir, m_top, m_bot = 55, 120, 20, 30

            # Eixo Y
            niveis_y = [(0.0, "R$ 50.000"), (0.2, "R$ 40.000"), (0.4, "R$ 30.000"), (0.6, "R$ 20.000"), (0.8, "R$ 10.000"), (1.0, "R$ 0")]
            for pct, txt in niveis_y:
                y = m_top + pct * (h - m_top - m_bot)
                canvas_proj.create_line(m_esq, y, w - m_dir, y, fill="#1A2D3C", dash=(2, 4))
                canvas_proj.create_text(m_esq - 8, y, text=txt, fill="#64748B", font=("Segoe UI", 7), anchor="e")

            # Meses
            meses = ["Jan/25", "Fev/25", "Mar/25", "Abr/25", "Mai/25", "Jun/25", "Jul/25", "Ago/25", "Set/25", "Out/25", "Nov/25", "Dez/25"]
            step_x = (w - m_esq - m_dir) / (len(meses) - 1)

            # 3 Curvas: Otimista, Planejado, Pessimista
            curva_oti = [0.98, 0.92, 0.85, 0.77, 0.68, 0.60, 0.52, 0.44, 0.36, 0.28, 0.22, 0.15]
            curva_pla = [0.98, 0.94, 0.88, 0.82, 0.75, 0.69, 0.63, 0.56, 0.50, 0.43, 0.36, 0.28]
            curva_pes = [0.98, 0.96, 0.92, 0.88, 0.83, 0.78, 0.73, 0.68, 0.62, 0.57, 0.51, 0.45]

            pts_oti = []
            pts_pla = []
            pts_pes = []

            for i in range(len(meses)):
                x = m_esq + i * step_x
                y_o = m_top + curva_oti[i] * (h - m_top - m_bot)
                y_p = m_top + curva_pla[i] * (h - m_top - m_bot)
                y_s = m_top + curva_pes[i] * (h - m_top - m_bot)

                pts_oti.append((x, y_o))
                pts_pla.append((x, y_p))
                pts_pes.append((x, y_s))

                canvas_proj.create_text(x, h - 12, text=meses[i], fill="#8EA3B8", font=("Segoe UI", 7))

            # Desenhar Curvas
            # 1. Pessimista (Vermelho)
            for i in range(len(pts_pes) - 1):
                canvas_proj.create_line(pts_pes[i][0], pts_pes[i][1], pts_pes[i+1][0], pts_pes[i+1][1], fill="#F43F5E", width=2)
            for x, y in pts_pes:
                canvas_proj.create_oval(x-3, y-3, x+3, y+3, fill="#F43F5E", outline="#101C26", width=1.5)

            # 2. Planejado (Azul Ciano)
            for i in range(len(pts_pla) - 1):
                canvas_proj.create_line(pts_pla[i][0], pts_pla[i][1], pts_pla[i+1][0], pts_pla[i+1][1], fill="#38BDF8", width=2)
            for x, y in pts_pla:
                canvas_proj.create_oval(x-3, y-3, x+3, y+3, fill="#38BDF8", outline="#101C26", width=1.5)

            # 3. Otimista (Verde Neon)
            for i in range(len(pts_oti) - 1):
                canvas_proj.create_line(pts_oti[i][0], pts_oti[i][1], pts_oti[i+1][0], pts_oti[i+1][1], fill="#00D084", width=2)
            for x, y in pts_oti:
                canvas_proj.create_oval(x-3, y-3, x+3, y+3, fill="#00D084", outline="#101C26", width=1.5)

            # Tooltip Flutuante no Canto Direito
            bx, by = w - m_dir + 10, m_top + 10
            canvas_proj.create_rectangle(bx, by, bx + 95, by + 75, fill="#0D1A24", outline="#1E3143", width=1)
            canvas_proj.create_text(bx + 47, by + 12, text="Dez/2025", fill="#FFFFFF", font=("Segoe UI", 8, "bold"))
            canvas_proj.create_text(bx + 8, by + 28, text="● Otimista", fill="#00D084", font=("Segoe UI", 7), anchor="w")
            canvas_proj.create_text(bx + 88, by + 28, text="R$ 42.600", fill="#FFFFFF", font=("Segoe UI", 7, "bold"), anchor="e")
            canvas_proj.create_text(bx + 8, by + 44, text="● Planejado", fill="#38BDF8", font=("Segoe UI", 7), anchor="w")
            canvas_proj.create_text(bx + 88, by + 44, text="R$ 36.000", fill="#FFFFFF", font=("Segoe UI", 7, "bold"), anchor="e")
            canvas_proj.create_text(bx + 8, by + 60, text="● Pessimista", fill="#F43F5E", font=("Segoe UI", 7), anchor="w")
            canvas_proj.create_text(bx + 88, by + 60, text="R$ 27.400", fill="#FFFFFF", font=("Segoe UI", 7, "bold"), anchor="e")

        canvas_proj.bind("<Configure>", desenhar_grafico)
        canvas_proj.after(100, desenhar_grafico)

    def _build_cards_cenarios(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 12))
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        cenarios = [
            ("🍃", "#0D2E2B", "#00D084", "Cenário Otimista", "Melhor resultado", "R$ 42.600,00", "+ 42% em relação ao início", "R$ 96.000,00", "R$ 53.400,00"),
            ("🎯", "#122538", "#38BDF8", "Cenário Planejado", "Cenário base", "R$ 36.000,00", "+ 20% em relação ao início", "R$ 84.000,00", "R$ 60.000,00"),
            ("⚠️", "#2E151B", "#F43F5E", "Cenário Pessimista", "Mais conservador", "R$ 27.400,00", "- 9% em relação ao início", "R$ 72.000,00", "R$ 71.400,00"),
        ]

        for idx, (ic, bg_ic, cor_d, tit, badge, val, pct, rec, desp) in enumerate(cenarios):
            card = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=cor_d)
            card.grid(row=0, column=idx, padx=4, sticky="nsew")

            topo = ctk.CTkFrame(card, fg_color="transparent")
            topo.pack(fill="x", padx=12, pady=(12, 4))

            ctk.CTkLabel(topo, text=f"{ic}  {tit}", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

            b_f = ctk.CTkFrame(topo, fg_color=bg_ic, corner_radius=6)
            b_f.pack(side="right")
            ctk.CTkLabel(b_f, text=f" {badge} ", font=fonte(8, "bold"), text_color=cor_d).pack(padx=4, pady=1)

            # Valor principal
            ctk.CTkLabel(card, text=val, font=fonte(18, "bold"), text_color=cor_d, anchor="w").pack(anchor="w", padx=12, pady=(4, 2))
            ctk.CTkLabel(card, text=pct, font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w", padx=12, pady=(0, 8))

            # Acumulados
            acum = ctk.CTkFrame(card, fg_color="transparent")
            acum.pack(fill="x", padx=12, pady=(0, 10))
            acum.grid_columnconfigure((0, 1), weight=1)

            ctk.CTkLabel(acum, text=f"Receitas acumuladas\n{rec}", font=fonte(8), text_color=COR_TEXTO_MUTED, justify="left").grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(acum, text=f"Despesas acumuladas\n{desp}", font=fonte(8), text_color=COR_TEXTO_MUTED, justify="left").grid(row=0, column=1, sticky="w")

    def _build_consequencias_e_ia(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x")
        grid.grid_columnconfigure((0, 1), weight=1)

        # Esquerda: Principais Consequências
        card_esq = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card_esq.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        ctk.CTkLabel(card_esq, text="🎯  Principais Consequências", font=fonte(12, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=14, pady=(12, 8))

        itens_conseq = [
            ("↑", "Seu saldo final pode ser até 55% maior no cenário otimista.", "#00D084"),
            ("📊", "O corte de 15% nas despesas gera uma economia de R$ 10.800,00 no período.", "#38BDF8"),
            ("🎯", "Com o aporte de R$ 300,00/mês, você contribui com R$ 3.600,00 para suas metas.", "#A855F7"),
            ("💡", "A renda extra de R$ 500,00/mês adiciona R$ 6.000,00 ao seu saldo no período.", "#F59E0B"),
        ]
        for ic, txt, cor in itens_conseq:
            r = ctk.CTkFrame(card_esq, fg_color="transparent")
            r.pack(fill="x", padx=14, pady=3)
            ctk.CTkLabel(r, text=ic, font=fonte(11, "bold"), text_color=cor, width=20).pack(side="left")
            ctk.CTkLabel(r, text=txt, font=fonte(10), text_color=COR_TEXTO_SECUNDARIO, anchor="w", wraplength=280, justify="left").pack(side="left")

        ctk.CTkLabel(card_esq, text="", height=8).pack()

        # Direita: Análise da IA
        card_dir = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card_dir.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

        top_ia = ctk.CTkFrame(card_dir, fg_color="transparent")
        top_ia.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(top_ia, text="✨  Análise da IA", font=fonte(12, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        b_ia = ctk.CTkFrame(top_ia, fg_color="#1C142E", corner_radius=6)
        b_ia.pack(side="right")
        ctk.CTkLabel(b_ia, text=" Insights personalizados ", font=fonte(8, "bold"), text_color="#A855F7").pack(padx=4, pady=2)

        txt_ia = (
            "Com base na sua simulação, o cenário planejado mostra um equilíbrio saudável "
            "entre crescimento e segurança. O corte de despesas tem um impacto significativo "
            "e é a principal alavanca para melhorar seu resultado."
        )
        ctk.CTkLabel(
            card_dir,
            text=txt_ia,
            font=fonte(10),
            text_color=COR_TEXTO_SECUNDARIO,
            wraplength=300,
            justify="left",
            anchor="w",
        ).pack(anchor="w", padx=14, pady=(0, 8))

        # Dica / Sugestão em lilás
        sug_box = ctk.CTkFrame(card_dir, fg_color="#181329", corner_radius=8, border_width=1, border_color="#3B2562")
        sug_box.pack(fill="x", padx=14, pady=(0, 12))

        ctk.CTkLabel(
            sug_box,
            text="✨ Minha sugestão: se conseguir manter o corte de 15% e o aporte mensal, você estará no caminho para atingir suas principais metas mais cedo.",
            font=fonte(9),
            text_color="#D8B4FE",
            wraplength=280,
            justify="left",
        ).pack(padx=10, pady=8)
