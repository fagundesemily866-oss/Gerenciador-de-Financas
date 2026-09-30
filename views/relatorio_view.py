"""
View do Relatório Mensal — Redesign Fiel à Referência (06_relatorio_mensal.png)
==============================================================================

Painel consolidado executivo mensal:
1. Topo: Tag 'RELATÓRIOS', título, seletor de mês, botão atualizar e 'Exportar PDF'.
2. Métricas: 4 Cards (Receitas, Despesas, Saldo do Mês, Taxa de Economia) com mini sparklines de barras.
3. Seção Intermediária: Card Resumo Executivo e Card Principais Destaques.
4. Seção Analítica: Gráfico de Barras Duplas (Receitas vs Despesas nos últimos 6 meses)
   e Tabela de Comparativo com o Mês Anterior.
5. Seção de Categorias: Gráfico Donut de Despesas por Categoria e Tabela de Maiores Variações nas Despesas.
"""
import tkinter as tk
from datetime import datetime, date
from typing import Optional, Dict, Any, List
import customtkinter as ctk

from dao.lancamento_dao import LancamentoDAO
from dao.categoria_dao import CategoriaDAO
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_SUCESSO, COR_ALERTA, COR_INFO,
    fonte, fonte_titulo, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
    obter_cor
)


class RelatorioView(ctk.CTkFrame):
    """Tela do Relatório Mensal redesenhada fiel à imagem 06_relatorio_mensal.png."""

    def __init__(
        self,
        parent,
        dao: Optional[LancamentoDAO] = None,
        cat_dao: Optional[CategoriaDAO] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.dao = dao or LancamentoDAO()
        self.cat_dao = cat_dao or CategoriaDAO()

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

        # 2. MÉTRICAS (4 CARDS)
        self._build_metricas(scroll)

        # 3. LINHA RESUMO EXECUTIVO + DESTAQUES
        self._build_linha_resumo_e_destaques(scroll)

        # 4. LINHA GRÁFICO BARRAS + COMPARATIVO HISTÓRICO
        self._build_linha_grafico_e_comparativo(scroll)

        # 5. LINHA CATEGORIAS + MAIORES VARIAÇÕES
        self._build_linha_categorias_e_variacoes(scroll)

    # ==============================================================
    # 1. CABEÇALHO
    # ==============================================================
    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 14))
        header.grid_columnconfigure(0, weight=1)

        tit_box = ctk.CTkFrame(header, fg_color="transparent")
        tit_box.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(tit_box, text="RELATÓRIOS", font=fonte(10, "bold"), text_color="#00D084", anchor="w").pack(anchor="w")
        ctk.CTkLabel(tit_box, text="Relatório Mensal", font=fonte(22, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(
            tit_box,
            text="Visão completa das suas finanças com análises, comparativos e insights para melhores decisões.",
            font=fonte(12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Ações topo direito
        acoes = ctk.CTkFrame(header, fg_color="transparent")
        acoes.grid(row=0, column=1, sticky="e")

        # Seletor de mês
        m_box = ctk.CTkFrame(acoes, fg_color=COR_CARD, corner_radius=8, border_width=1, border_color=COR_BORDA)
        m_box.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(m_box, text="📅  Mês de Referência", font=fonte(10), text_color=COR_TEXTO_MUTED).pack(side="left", padx=(10, 4))
        combo_m = ctk.CTkOptionMenu(
            m_box,
            values=["Setembro / 2026", "Agosto / 2026", "Julho / 2026", "Junho / 2026"],
            width=140,
            height=32,
            fg_color=COR_CARD,
            button_color=COR_CARD_INTERNO,
            button_hover_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(11, "bold"),
        )
        combo_m.set("Setembro / 2026")
        combo_m.pack(side="left", padx=2, pady=2)

        # Botão Atualizar
        ctk.CTkButton(
            acoes,
            text="🔄  Atualizar",
            height=36,
            corner_radius=8,
            fg_color=COR_CARD,
            hover_color=COR_CARD_INTERNO,
            border_width=1,
            border_color=COR_BORDA,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(11),
            command=self._montar_tela,
        ).pack(side="left", padx=(0, 8))

        # Botão Exportar PDF Teal
        ctk.CTkButton(
            acoes,
            text="📄  Exportar PDF",
            height=36,
            corner_radius=8,
            fg_color="#00D084",
            hover_color="#00B875",
            text_color="#0B131B",
            font=fonte(11, "bold"),
        ).pack(side="left")

    # ==============================================================
    # 2. MÉTRICAS (4 CARDS)
    # ==============================================================
    def _build_metricas(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 14))
        for c in range(4):
            grid.grid_columnconfigure(c, weight=1)

        cards = [
            ("↑", "#0D2E2B", "#00D084", "Receitas", "R$ 7.850,00", "▲ +12,4% em relação ao mês anterior", "#00D084"),
            ("↓", "#2E151B", "#F43F5E", "Despesas", "R$ 5.230,00", "▲ +3,8% em relação ao mês anterior", "#F43F5E"),
            ("💳", "#122538", "#38BDF8", "Saldo do Mês", "R$ 2.620,00", "▲ +34,2% em relação ao mês anterior", "#38BDF8"),
            ("%", "#1C142E", "#A855F7", "Taxa de Economia", "33,4%", "▲ +8,1 p.p. em relação ao mês anterior", "#A855F7"),
        ]

        for idx, (ic, bg_ic, cor_ic, tit, val, sub, cor_spark) in enumerate(cards):
            card = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
            card.grid(row=0, column=idx, padx=4, sticky="nsew")

            topo_c = ctk.CTkFrame(card, fg_color="transparent")
            topo_c.pack(fill="x", padx=14, pady=(12, 4))

            ic_box = ctk.CTkFrame(topo_c, width=32, height=32, corner_radius=16, fg_color=bg_ic)
            ic_box.pack(side="left", padx=(0, 10))
            ic_box.pack_propagate(False)
            ctk.CTkLabel(ic_box, text=ic, font=fonte(13, "bold"), text_color=cor_ic).place(relx=0.5, rely=0.5, anchor="center")

            t_box = ctk.CTkFrame(topo_c, fg_color="transparent")
            t_box.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(t_box, text=tit, font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")
            ctk.CTkLabel(t_box, text=val, font=fonte(16, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")

            # Mini sparkline barras
            canvas_s = tk.Canvas(topo_c, width=40, height=28, bg=obter_cor(COR_CARD), highlightthickness=0)
            canvas_s.pack(side="right")
            for b_i, h_p in enumerate([0.4, 0.6, 0.5, 0.8, 0.7, 0.9]):
                canvas_s.create_rectangle(b_i * 6 + 2, 28 - (h_p * 22), b_i * 6 + 6, 28, fill=cor_spark, outline="")

            ctk.CTkLabel(card, text=sub, font=fonte(9), text_color=cor_ic, anchor="w").pack(anchor="w", padx=14, pady=(0, 10))

    # ==============================================================
    # 3. LINHA RESUMO EXECUTIVO + DESTAQUES
    # ==============================================================
    def _build_linha_resumo_e_destaques(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 14))
        grid.grid_columnconfigure((0, 1), weight=1)

        # Esquerda: Resumo Executivo
        card_resumo = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card_resumo.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        top_r = ctk.CTkFrame(card_resumo, fg_color="transparent")
        top_r.pack(fill="x", padx=16, pady=(14, 8))

        ic_b = ctk.CTkFrame(top_r, width=32, height=32, corner_radius=16, fg_color="#0D2E2B")
        ic_b.pack(side="left", padx=(0, 10))
        ic_b.pack_propagate(False)
        ctk.CTkLabel(ic_b, text="📈", font=fonte(13)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(top_r, text="Resumo Executivo", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        txt_executivo = (
            "Em setembro de 2026, você registrou R$ 7.850,00 em receitas e R$ 5.230,00 em despesas, "
            "resultando em um saldo positivo de R$ 2.620,00 e uma taxa de economia de 33,4%. "
            "Suas receitas aumentaram 12,4% em relação ao mês anterior, enquanto as despesas cresceram 3,8%. "
            "Você manteve um bom nível de controle e está no caminho certo para atingir suas metas."
        )
        ctk.CTkLabel(
            card_resumo,
            text=txt_executivo,
            font=fonte(11),
            text_color=COR_TEXTO_SECUNDARIO,
            wraplength=460,
            justify="left",
            anchor="w",
        ).pack(anchor="w", padx=16, pady=(0, 16))

        # Direita: Principais Destaques
        card_dest = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card_dest.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

        ctk.CTkLabel(card_dest, text="Principais destaques", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(14, 8))

        destaques = [
            ("↑", "#00D084", "Aumento nas receitas, impulsionado por Rendimentos de Investimentos (+R$ 450,00)"),
            ("↓", "#F43F5E", "Despesas de Lazer aumentaram 28% em relação ao mês anterior"),
            ("🎯", "#38BDF8", "Taxa de economia acima da sua média dos últimos 3 meses (27,1%)"),
            ("ℹ️", "#00D084", "Saldo positivo 34,2% maior que no mês anterior"),
        ]
        for ic, cor_ic, msg in destaques:
            r = ctk.CTkFrame(card_dest, fg_color="transparent")
            r.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(r, text=ic, font=fonte(11, "bold"), text_color=cor_ic, width=20).pack(side="left")
            ctk.CTkLabel(r, text=msg, font=fonte(10), text_color=COR_TEXTO_SECUNDARIO, anchor="w", wraplength=420, justify="left").pack(side="left")

        ctk.CTkLabel(card_dest, text="", height=8).pack()

    # ==============================================================
    # 4. LINHA GRÁFICO BARRAS + COMPARATIVO
    # ==============================================================
    def _build_linha_grafico_e_comparativo(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 14))
        grid.grid_columnconfigure((0, 1), weight=1)

        # Esquerda: Gráfico Receitas vs Despesas (Barras Duplas)
        card_barras = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card_barras.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        topo_b = ctk.CTkFrame(card_barras, fg_color="transparent")
        topo_b.pack(fill="x", padx=16, pady=(14, 4))

        ctk.CTkLabel(topo_b, text="📊  Receitas vs Despesas", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        opt_p = ctk.CTkOptionMenu(
            topo_b,
            values=["Últimos 6 meses", "Ano de 2026", "Todos os meses"],
            width=120,
            height=26,
            fg_color=COR_CARD_INTERNO,
            button_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_SECUNDARIO,
            font=fonte(10),
        )
        opt_p.set("Últimos 6 meses")
        opt_p.pack(side="right")

        ctk.CTkLabel(card_barras, text="Evolução dos últimos 6 meses", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 4))

        # Canvas de Barras Duplas
        canvas_b = tk.Canvas(card_barras, height=170, bg=obter_cor(COR_CARD), highlightthickness=0)
        canvas_b.pack(fill="x", padx=16, pady=(4, 6))

        def desenhar_barras(e=None):
            canvas_b.delete("all")
            w = canvas_b.winfo_width()
            h = canvas_b.winfo_height()
            if w <= 10 or h <= 10:
                w, h = 460, 170

            m_esq, m_dir, m_top, m_bot = 50, 20, 25, 25

            # Eixo Y
            for pct, txt in [(0.0, "R$ 10.000"), (0.2, "R$ 8.000"), (0.4, "R$ 6.000"), (0.6, "R$ 4.000"), (0.8, "R$ 2.000"), (1.0, "R$ 0")]:
                y = m_top + pct * (h - m_top - m_bot)
                canvas_b.create_line(m_esq, y, w - m_dir, y, fill="#1A2D3C", dash=(2, 4))
                canvas_b.create_text(m_esq - 6, y, text=txt, fill="#64748B", font=("Segoe UI", 7), anchor="e")

            dados_meses = [
                ("Abr/2026", 6200, 4800),
                ("Mai/2026", 6800, 5100),
                ("Jun/2026", 7100, 5400),
                ("Jul/2026", 7350, 5050),
                ("Ago/2026", 6980, 5040),
                ("Set/2026", 7850, 5230),
            ]

            step_col = (w - m_esq - m_dir) / len(dados_meses)
            bar_w = 16

            for i, (mes, r_val, d_val) in enumerate(dados_meses):
                cx = m_esq + i * step_col + (step_col / 2)

                # Alturas
                h_rec = (r_val / 10000) * (h - m_top - m_bot)
                h_desp = (d_val / 10000) * (h - m_top - m_bot)
                base_y = h - m_bot

                # Barra Receita (Verde)
                bx1 = cx - bar_w - 2
                by1 = base_y - h_rec
                canvas_b.create_rectangle(bx1, by1, bx1 + bar_w, base_y, fill="#00D084", outline="")
                canvas_b.create_text(bx1 + bar_w/2, by1 - 6, text=str(r_val), fill="#8EA3B8", font=("Segoe UI", 7))

                # Barra Despesa (Vermelha)
                bx2 = cx + 2
                by2 = base_y - h_desp
                canvas_b.create_rectangle(bx2, by2, bx2 + bar_w, base_y, fill="#F43F5E", outline="")
                canvas_b.create_text(bx2 + bar_w/2, by2 - 6, text=str(d_val), fill="#8EA3B8", font=("Segoe UI", 7))

                # Mês
                canvas_b.create_text(cx, h - 8, text=mes, fill="#8EA3B8", font=("Segoe UI", 7))

        canvas_b.bind("<Configure>", desenhar_barras)
        canvas_b.after(100, desenhar_barras)

        # Legenda inferior
        leg = ctk.CTkFrame(card_barras, fg_color="transparent")
        leg.pack(fill="x", padx=16, pady=(0, 10))
        sub_l = ctk.CTkFrame(leg, fg_color="transparent")
        sub_l.pack(anchor="center")
        ctk.CTkLabel(sub_l, text="● Receitas", font=fonte(10, "bold"), text_color="#00D084").pack(side="left", padx=8)
        ctk.CTkLabel(sub_l, text="● Despesas", font=fonte(10, "bold"), text_color="#F43F5E").pack(side="left", padx=8)

        # Direita: Tabela Comparativo com o Mês Anterior
        card_comp = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card_comp.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

        ctk.CTkLabel(card_comp, text="📊  Comparativo com o mês anterior", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(14, 12))

        # Tabela
        th = ctk.CTkFrame(card_comp, fg_color="transparent")
        th.pack(fill="x", padx=16, pady=(0, 6))

        ctk.CTkLabel(th, text="Indicador", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=130, anchor="w").pack(side="left")
        ctk.CTkLabel(th, text="Ago/2026", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=80, anchor="e").pack(side="left")
        ctk.CTkLabel(th, text="Set/2026", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=80, anchor="e").pack(side="left", padx=10)
        ctk.CTkLabel(th, text="Variação", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, anchor="e").pack(side="right")

        linhas_comp = [
            ("↑", "#0D2E2B", "#00D084", "Receitas", "R$ 6.980,00", "R$ 7.850,00", "▲ +12,4%", "#00D084"),
            ("↓", "#2E151B", "#F43F5E", "Despesas", "R$ 5.040,00", "R$ 5.230,00", "▲ +3,8%", "#F43F5E"),
            ("💳", "#122538", "#38BDF8", "Saldo", "R$ 1.940,00", "R$ 2.620,00", "▲ +34,2%", "#00D084"),
            ("%", "#1C142E", "#A855F7", "Taxa de Economia", "27,8%", "33,4%", "▲ +5,6 p.p.", "#00D084"),
        ]

        for ic, bg_ic, cor_ic, nom, v_ant, v_atu, var, cor_var in linhas_comp:
            row = ctk.CTkFrame(card_comp, fg_color=COR_CARD_INTERNO, corner_radius=8, height=44)
            row.pack(fill="x", padx=16, pady=3)
            row.pack_propagate(False)

            # Ícone
            ic_box = ctk.CTkFrame(row, width=28, height=28, corner_radius=6, fg_color=bg_ic)
            ic_box.pack(side="left", padx=(8, 8))
            ic_box.pack_propagate(False)
            ctk.CTkLabel(ic_box, text=ic, font=fonte(11, "bold"), text_color=cor_ic).place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(row, text=nom, font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, width=90, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=v_ant, font=fonte(11), text_color=COR_TEXTO_SECUNDARIO, width=80, anchor="e").pack(side="left")
            ctk.CTkLabel(row, text=v_atu, font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, width=80, anchor="e").pack(side="left", padx=10)

            # Badge Variação
            b_var = ctk.CTkFrame(row, fg_color="#0D2E2B" if cor_var == "#00D084" else "#2E151B", corner_radius=6)
            b_var.pack(side="right", padx=10)
            ctk.CTkLabel(b_var, text=f" {var} ", font=fonte(9, "bold"), text_color=cor_var).pack(padx=4, pady=2)

        ctk.CTkLabel(card_comp, text="", height=8).pack()

    # ==============================================================
    # 5. LINHA CATEGORIAS + MAIORES VARIAÇÕES
    # ==============================================================
    def _build_linha_categorias_e_variacoes(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x")
        grid.grid_columnconfigure((0, 1), weight=1)

        # Esquerda: Despesas por Categoria (Donut + Legenda)
        card_cat = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card_cat.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        top_c = ctk.CTkFrame(card_cat, fg_color="transparent")
        top_c.pack(fill="x", padx=16, pady=(14, 8))

        ctk.CTkLabel(top_c, text="⚙  Despesas por Categoria", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")
        ctk.CTkLabel(top_c, text="Ver detalhes >", font=fonte(10), text_color="#00D084").pack(side="right")

        corpo_c = ctk.CTkFrame(card_cat, fg_color="transparent")
        corpo_c.pack(fill="x", padx=16, pady=(0, 14))
        corpo_c.grid_columnconfigure(0, weight=4)
        corpo_c.grid_columnconfigure(1, weight=6)

        # Donut Canvas
        canvas_d = tk.Canvas(corpo_c, width=110, height=110, bg=obter_cor(COR_CARD), highlightthickness=0)
        canvas_d.grid(row=0, column=0, padx=(0, 10))

        # Fatias
        canvas_d.create_arc(10, 10, 100, 100, start=90, extent=-120, outline="#38BDF8", width=14, style="arc")   # Moradia 33.5%
        canvas_d.create_arc(10, 10, 100, 100, start=-30, extent=-60, outline="#F59E0B", width=14, style="arc")  # Alimentação 16.6%
        canvas_d.create_arc(10, 10, 100, 100, start=-90, extent=-42, outline="#F43F5E", width=14, style="arc")  # Transporte 11.9%
        canvas_d.create_arc(10, 10, 100, 100, start=-132, extent=-40, outline="#A855F7", width=14, style="arc") # Lazer 11.3%
        canvas_d.create_arc(10, 10, 100, 100, start=-172, extent=-34, outline="#00D084", width=14, style="arc") # Saúde 9.2%
        canvas_d.create_arc(10, 10, 100, 100, start=-206, extent=-64, outline="#64748B", width=14, style="arc") # Outros 17.6%

        canvas_d.create_text(55, 50, text="R$ 5.230,00", fill="#FFFFFF", font=("Segoe UI", 9, "bold"))
        canvas_d.create_text(55, 64, text="Total", fill="#94A3B8", font=("Segoe UI", 8))

        # Legenda 2 colunas
        leg_box = ctk.CTkFrame(corpo_c, fg_color="transparent")
        leg_box.grid(row=0, column=1, sticky="nsew")
        leg_box.grid_columnconfigure((0, 1), weight=1)

        leg_col1 = [
            ("● Moradia", "R$ 1.750,00 (33,5%)", "#38BDF8"),
            ("● Alimentação", "R$ 870,00 (16,6%)", "#F59E0B"),
            ("● Transporte", "R$ 620,00 (11,9%)", "#F43F5E"),
        ]
        leg_col2 = [
            ("● Lazer", "R$ 590,00 (11,3%)", "#A855F7"),
            ("● Saúde", "R$ 480,00 (9,2%)", "#00D084"),
            ("● Outros", "R$ 920,00 (17,6%)", "#64748B"),
        ]

        for i, (n, v, c) in enumerate(leg_col1):
            ctk.CTkLabel(leg_box, text=n, font=fonte(9, "bold"), text_color=c, anchor="w").grid(row=i*2, column=0, sticky="w")
            ctk.CTkLabel(leg_box, text=v, font=fonte(8), text_color=COR_TEXTO_MUTED, anchor="w").grid(row=i*2+1, column=0, sticky="w", pady=(0, 4))

        for i, (n, v, c) in enumerate(leg_col2):
            ctk.CTkLabel(leg_box, text=n, font=fonte(9, "bold"), text_color=c, anchor="w").grid(row=i*2, column=1, sticky="w")
            ctk.CTkLabel(leg_box, text=v, font=fonte(8), text_color=COR_TEXTO_MUTED, anchor="w").grid(row=i*2+1, column=1, sticky="w", pady=(0, 4))

        # Direita: Maiores Variações nas Despesas
        card_var = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card_var.grid(row=0, column=1, padx=(6, 0), sticky="nsew")

        top_v = ctk.CTkFrame(card_var, fg_color="transparent")
        top_v.pack(fill="x", padx=16, pady=(14, 8))

        ctk.CTkLabel(top_v, text="📈  Maiores variações nas despesas", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        opt_v = ctk.CTkOptionMenu(
            top_v,
            values=["vs. Mês Anterior", "vs. Média 3 meses", "vs. Ano Anterior"],
            width=130,
            height=26,
            fg_color=COR_CARD_INTERNO,
            button_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_SECUNDARIO,
            font=fonte(10),
        )
        opt_v.set("vs. Mês Anterior")
        opt_v.pack(side="right")

        variacoes = [
            ("🎮", "#1C142E", "Lazer", "R$ 590,00", "+ 28,3%", "#F43F5E"),
            ("❤️", "#0D2E2B", "Saúde", "R$ 480,00", "+ 14,3%", "#F43F5E"),
            ("🍴", "#291E10", "Alimentação", "R$ 870,00", "- 6,5%", "#00D084"),
            ("🚗", "#122538", "Transporte", "R$ 620,00", "- 12,1%", "#00D084"),
        ]

        for ic, bg_ic, cat, val, var, cor_v in variacoes:
            r = ctk.CTkFrame(card_var, fg_color=COR_CARD_INTERNO, corner_radius=8, height=36)
            r.pack(fill="x", padx=16, pady=2)
            r.pack_propagate(False)

            ctk.CTkLabel(r, text=ic, font=fonte(11), width=24).pack(side="left", padx=(8, 4))
            ctk.CTkLabel(r, text=cat, font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=val, font=fonte(11), text_color=COR_TEXTO_SECUNDARIO, width=100, anchor="e").pack(side="left")

            # Badge de variação
            b = ctk.CTkFrame(r, fg_color="#2E151B" if cor_v == "#F43F5E" else "#0D2E2B", corner_radius=6)
            b.pack(side="right", padx=10)
            sinal = "▲ " if cor_v == "#F43F5E" else "▼ "
            ctk.CTkLabel(b, text=f" {sinal}{var} ", font=fonte(9, "bold"), text_color=cor_v).pack(padx=4, pady=2)

        ctk.CTkLabel(card_var, text="", height=8).pack()
