"""
View de Dashboard & Saúde Financeira — Redesign Fiel à Referência (01_dashboard.png)
=====================================================================================

Apresenta visão consolidada e moderna das finanças pessoais:
1. Topo: Título, subtítulo, data/hora formatada e seletor de mês.
2. Linha de Métricas: Saldo Atual, Receitas do Mês, Despesas do Mês, Economizado,
   Limite Mensal (com barra de uso) e Disponível para Gastar.
3. Seção Gráfica:
   - Saúde Financeira (Gauge circular com score 82/100, badge "Ótima", checklist e CTA)
   - Gastos por Categoria (Gráfico Donut de despesas com total central e legenda detalhada)
   - Fluxo de Caixa (Gráfico vetorial de linhas comparando Receitas e Despesas nos últimos 6 meses)
4. Seção Inferior:
   - Lançamentos Recentes (com status e valores destacados)
   - Próximos Vencimentos (com contagem regressiva em dias)
   - Minhas Metas (com progresso percentual e valores)
"""
import math
import tkinter as tk
from datetime import datetime
from typing import Optional, Dict, Any, List
import customtkinter as ctk

from dao.lancamento_dao import LancamentoDAO
from dao.categoria_dao import CategoriaDAO
from dao.meta_dao import MetaDAO
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_ACENTO_HOVER, COR_SUCESSO, COR_ALERTA,
    COR_AVISO, COR_INFO, COR_RECEITA, COR_RECEITA_BG, COR_DESPESA, COR_DESPESA_BG,
    COR_BOTAO_SECUNDARIO, COR_PROGRESSO, COR_PROGRESSO_BG,
    fonte, fonte_titulo, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
    fonte_grande_valor, obter_cor
)


class SaudeFinanceiraView(ctk.CTkFrame):
    """Tela do Dashboard & Saúde Financeira conforme a imagem 01_dashboard.png."""

    def __init__(
        self,
        parent,
        dao: Optional[LancamentoDAO] = None,
        cat_dao: Optional[CategoriaDAO] = None,
        meta_dao: Optional[MetaDAO] = None,
    ):
        super().__init__(parent, fg_color="transparent")

        self.dao = dao or LancamentoDAO()
        self.cat_dao = cat_dao or CategoriaDAO()
        self.meta_dao = meta_dao or MetaDAO()
        self.parent_menu = parent

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._montar_tela()

    def _navegar_para(self, chave: str):
        """Tenta acionar o seletor do MenuView principal se disponível."""
        curr = self.master
        while curr:
            if hasattr(curr, "selecionar"):
                curr.selecionar(chave)
                break
            curr = getattr(curr, "master", None)

    def atualizar_dados(self):
        """Recarrega dados e redesenha a interface."""
        self._montar_tela()

    def _montar_tela(self):
        # Limpar widgets anteriores
        for w in self.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # 1. CABEÇALHO
        self._build_header(scroll)

        # 2. MÉTRICAS (6 CARDS)
        self._build_metricas(scroll)

        # 3. LINHA CENTRAL (3 CARDS COM GRÁFICOS)
        self._build_linha_graficos(scroll)

        # 4. LINHA INFERIOR (3 CARDS DE LISTAS)
        self._build_linha_listas(scroll)

    # ==============================================================
    # 1. CABEÇALHO
    # ==============================================================
    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 14))
        header.grid_columnconfigure(0, weight=1)

        # Esquerda: Título e subtítulo
        tit_box = ctk.CTkFrame(header, fg_color="transparent")
        tit_box.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            tit_box,
            text="Dashboard & Saúde",
            font=fonte(22, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            tit_box,
            text="Visão geral da sua vida financeira. Acompanhe seus resultados, evolua suas metas e mantenha o controle.",
            font=fonte(12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Direita: Data e Seletor de Mês
        dir_box = ctk.CTkFrame(header, fg_color="transparent")
        dir_box.grid(row=0, column=1, sticky="e")

        # Data atual formatada
        agora = datetime.now()
        dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        meses_nome = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        txt_data = f"Hoje é {agora.day} de {meses_nome[agora.month - 1]} de {agora.year}"
        txt_hora = f"{dias_semana[agora.weekday()]}, {agora.strftime('%H:%M')}"

        data_card = ctk.CTkFrame(dir_box, fg_color="transparent")
        data_card.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(
            data_card,
            text=f"📅  {txt_data}",
            font=fonte(11, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="e",
        ).pack(anchor="e")

        ctk.CTkLabel(
            data_card,
            text=txt_hora,
            font=fonte(10),
            text_color=COR_TEXTO_MUTED,
            anchor="e",
        ).pack(anchor="e")

        # Seletor de mês com botões de navegação
        nav_mes = ctk.CTkFrame(dir_box, fg_color=COR_CARD, corner_radius=10, border_width=1, border_color=COR_BORDA)
        nav_mes.pack(side="left")

        ctk.CTkLabel(
            nav_mes,
            text="📅",
            font=fonte(12),
        ).pack(side="left", padx=(10, 4))

        self.mes_combo = ctk.CTkOptionMenu(
            nav_mes,
            values=["Abril de 2026", "Março de 2026", "Fevereiro de 2026", "Janeiro de 2026"],
            width=130,
            height=30,
            fg_color=COR_CARD,
            button_color=COR_CARD_INTERNO,
            button_hover_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(12),
        )
        self.mes_combo.set("Abril de 2026")
        self.mes_combo.pack(side="left", padx=2, pady=3)

        btn_prev = ctk.CTkButton(
            nav_mes,
            text="‹",
            width=28,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_SECUNDARIO,
            font=fonte(16, "bold"),
        )
        btn_prev.pack(side="left", padx=(0, 2), pady=3)

        btn_next = ctk.CTkButton(
            nav_mes,
            text="›",
            width=28,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_SECUNDARIO,
            font=fonte(16, "bold"),
        )
        btn_next.pack(side="left", padx=(0, 6), pady=3)

    # ==============================================================
    # 2. MÉTRICAS (6 CARDS)
    # ==============================================================
    def _build_metricas(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 14))

        for c in range(6):
            grid.grid_columnconfigure(c, weight=1)

        dados_cards = [
            {
                "icone": "👛",
                "cor_icone_bg": "#0D2E2B",
                "label": "Saldo Atual",
                "tem_olho": True,
                "valor": "R$ 12.480,50",
                "cor_valor": "#00D084",
                "footer": "▲ + 8,2% vs. mês anterior",
                "cor_footer": "#00D084",
                "progresso": None,
            },
            {
                "icone": "↑",
                "cor_icone_bg": "#0D2E2B",
                "label": "Receitas do Mês",
                "tem_olho": False,
                "valor": "R$ 8.950,00",
                "cor_valor": "#00D084",
                "footer": "▲ + 12,4% vs. mar/2026",
                "cor_footer": "#00D084",
                "progresso": None,
            },
            {
                "icone": "↓",
                "cor_icone_bg": "#2E151B",
                "label": "Despesas do Mês",
                "tem_olho": False,
                "valor": "R$ 5.420,30",
                "cor_valor": "#F43F5E",
                "footer": "▲ + 4,1% vs. mar/2026",
                "cor_footer": "#F43F5E",
                "progresso": None,
            },
            {
                "icone": "🐷",
                "cor_icone_bg": "#0D2E2B",
                "label": "Economizado",
                "tem_olho": False,
                "valor": "R$ 3.529,70",
                "cor_valor": "#00D084",
                "footer": "39,4% da receita",
                "cor_footer": "#00D084",
                "progresso": None,
            },
            {
                "icone": "💳",
                "cor_icone_bg": "#122538",
                "label": "Limite Mensal",
                "tem_olho": False,
                "valor": "R$ 7.000,00",
                "cor_valor": "#FFFFFF",
                "footer": "77,4% utilizado",
                "cor_footer": "#F59E0B",
                "progresso": 0.774,
            },
            {
                "icone": "⏱",
                "cor_icone_bg": "#122538",
                "label": "Disponível para Gastar",
                "tem_olho": False,
                "valor": "R$ 1.579,70",
                "cor_valor": "#38BDF8",
                "footer": "22,6% do limite",
                "cor_footer": "#38BDF8",
                "progresso": None,
            },
        ]

        # Calcular valores reais se existirem
        lancamentos = self.dao.listar_todos()
        if lancamentos:
            rec = sum(l.valor for l in lancamentos if getattr(l, "tipo", "") == "Receita")
            desp = sum(l.valor for l in lancamentos if getattr(l, "tipo", "") == "Despesa")
            saldo = rec - desp
            if rec > 0 or desp > 0:
                dados_cards[0]["valor"] = f"R$ {saldo:,.2f}"
                dados_cards[1]["valor"] = f"R$ {rec:,.2f}"
                dados_cards[2]["valor"] = f"R$ {desp:,.2f}"
                economizado = max(0, saldo)
                dados_cards[3]["valor"] = f"R$ {economizado:,.2f}"
                pct_rec = (economizado / rec * 100) if rec > 0 else 0
                dados_cards[3]["footer"] = f"{pct_rec:.1f}% da receita"

        for idx, item in enumerate(dados_cards):
            card = ctk.CTkFrame(
                grid,
                fg_color=COR_CARD,
                corner_radius=12,
                border_width=1,
                border_color=COR_BORDA,
            )
            card.grid(row=0, column=idx, padx=4, sticky="nsew")

            topo_card = ctk.CTkFrame(card, fg_color="transparent")
            topo_card.pack(fill="x", padx=12, pady=(12, 6))

            # Ícone estilizado
            icon_box = ctk.CTkFrame(
                topo_card,
                width=32,
                height=32,
                corner_radius=8,
                fg_color=item["cor_icone_bg"],
            )
            icon_box.pack(side="left")
            icon_box.pack_propagate(False)

            ctk.CTkLabel(
                icon_box,
                text=item["icone"],
                font=fonte(14, "bold"),
            ).place(relx=0.5, rely=0.5, anchor="center")

            # Rótulo
            lbl_box = ctk.CTkFrame(topo_card, fg_color="transparent")
            lbl_box.pack(side="left", padx=(8, 0), fill="x", expand=True)

            txt_lbl = item["label"]
            if item["tem_olho"]:
                txt_lbl += " 👁"

            ctk.CTkLabel(
                lbl_box,
                text=txt_lbl,
                font=fonte(10, "bold"),
                text_color=COR_TEXTO_SECUNDARIO,
                anchor="w",
            ).pack(anchor="w")

            # Valor principal
            ctk.CTkLabel(
                card,
                text=item["valor"],
                font=fonte(16, "bold"),
                text_color=item["cor_valor"],
                anchor="w",
            ).pack(anchor="w", padx=12, pady=(0, 4))

            # Barra de progresso ou footer
            if item["progresso"] is not None:
                prog = ctk.CTkProgressBar(
                    card,
                    height=6,
                    corner_radius=3,
                    progress_color="#F59E0B",
                    fg_color=COR_PROGRESSO_BG,
                )
                prog.set(item["progresso"])
                prog.pack(fill="x", padx=12, pady=(2, 4))

            ctk.CTkLabel(
                card,
                text=item["footer"],
                font=fonte(10),
                text_color=item["cor_footer"],
                anchor="w",
            ).pack(anchor="w", padx=12, pady=(0, 12))

    # ==============================================================
    # 3. LINHA CENTRAL: 3 PAINÉIS COM GRÁFICOS
    # ==============================================================
    def _build_linha_graficos(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 14))
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        # 3.1 Painel Saúde Financeira
        self._build_panel_saude(grid, col=0)

        # 3.2 Painel Gastos por Categoria
        self._build_panel_categorias(grid, col=1)

        # 3.3 Painel Fluxo de Caixa
        self._build_panel_fluxo(grid, col=2)

    def _build_panel_saude(self, parent, col: int):
        card = ctk.CTkFrame(
            parent,
            fg_color=COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=COR_BORDA,
            height=260,
        )
        card.grid(row=0, column=col, padx=(0, 6), sticky="nsew")
        card.grid_propagate(False)

        # Topo
        ctk.CTkLabel(
            card,
            text="Saúde Financeira",
            font=fonte(13, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        ).pack(anchor="w", padx=14, pady=(12, 6))

        meio = ctk.CTkFrame(card, fg_color="transparent")
        meio.pack(fill="x", padx=14, pady=0)
        meio.grid_columnconfigure(1, weight=1)

        # Donut circular de Score
        canvas_score = tk.Canvas(
            meio,
            width=110,
            height=110,
            bg=obter_cor(COR_CARD),
            highlightthickness=0,
        )
        canvas_score.grid(row=0, column=0, padx=(0, 10))

        # Desenhar Donut de Score (82 de 100)
        # Fundo do arco
        canvas_score.create_arc(10, 10, 100, 100, start=0, extent=359, outline="#162E35", width=10, style="arc")
        # Arco de progresso (82% de 360 = 295 graus)
        canvas_score.create_arc(10, 10, 100, 100, start=90, extent=-295, outline="#00D084", width=10, style="arc")
        # Textos centrais
        canvas_score.create_text(55, 48, text="82", fill="#FFFFFF", font=("Segoe UI", 20, "bold"))
        canvas_score.create_text(55, 68, text="de 100", fill="#94A3B8", font=("Segoe UI", 9))

        # Lado direito do Donut: Badge e Checklist
        checklist = ctk.CTkFrame(meio, fg_color="transparent")
        checklist.grid(row=0, column=1, sticky="w")

        badge_box = ctk.CTkFrame(
            checklist,
            corner_radius=6,
            fg_color="#0D2E2B",
            border_width=1,
            border_color="#134E48",
        )
        badge_box.pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(
            badge_box,
            text=" Ótima ",
            font=fonte(11, "bold"),
            text_color="#00D084",
        ).pack(padx=6, pady=1)

        ctk.CTkLabel(
            checklist,
            text="Suas finanças estão em um bom caminho!",
            font=fonte(10),
            text_color=COR_TEXTO_SECUNDARIO,
            wraplength=170,
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(0, 4))

        itens_check = [
            ("✔", "Gastos dentro do limite", "#00D084"),
            ("✔", "Boa taxa de economia", "#00D084"),
            ("✔", "Poucas contas em atraso", "#00D084"),
            ("⚠️", "Diversifique seus investimentos", "#F59E0B"),
        ]
        for ic, txt, cor in itens_check:
            l = ctk.CTkFrame(checklist, fg_color="transparent")
            l.pack(anchor="w", pady=1)
            ctk.CTkLabel(l, text=ic, font=fonte(10, "bold"), text_color=cor).pack(side="left", padx=(0, 4))
            ctk.CTkLabel(l, text=txt, font=fonte(10), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        # Botão link inferior
        btn_link = ctk.CTkButton(
            card,
            text="Ver detalhes da análise →",
            fg_color="transparent",
            hover_color=COR_CARD_INTERNO,
            text_color="#00D084",
            font=fonte(11, "bold"),
            anchor="w",
            command=lambda: self._navegar_para("simulador"),
        )
        btn_link.pack(anchor="w", padx=14, pady=(8, 8))

    def _build_panel_categorias(self, parent, col: int):
        card = ctk.CTkFrame(
            parent,
            fg_color=COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=COR_BORDA,
            height=260,
        )
        card.grid(row=0, column=col, padx=3, sticky="nsew")
        card.grid_propagate(False)

        # Topo com Seletor
        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(
            topo,
            text="Gastos por Categoria",
            font=fonte(13, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
        ).pack(side="left")

        opt_mes = ctk.CTkOptionMenu(
            topo,
            values=["Neste mês", "Mês anterior", "Ano todo"],
            width=90,
            height=24,
            fg_color=COR_CARD_INTERNO,
            button_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_SECUNDARIO,
            font=fonte(10),
        )
        opt_mes.set("Neste mês")
        opt_mes.pack(side="right")

        meio = ctk.CTkFrame(card, fg_color="transparent")
        meio.pack(fill="both", expand=True, padx=10, pady=2)
        meio.grid_columnconfigure(0, weight=1)
        meio.grid_columnconfigure(1, weight=1)

        # Donut de categorias
        canvas_cat = tk.Canvas(
            meio,
            width=120,
            height=120,
            bg=obter_cor(COR_CARD),
            highlightthickness=0,
        )
        canvas_cat.grid(row=0, column=0, padx=2)

        # Fatias coloridas do Donut
        fatias = [
            (103, "#00D084"),  # Moradia 28.6%
            (65, "#F59E0B"),   # Alimentação 18.1%
            (44, "#F43F5E"),   # Transporte 12.2%
            (35, "#EC4899"),   # Saúde 9.6%
            (30, "#8B5CF6"),   # Lazer 8.3%
            (27, "#38BDF8"),   # Educação 7.4%
            (56, "#64748B"),   # Outros 15.8%
        ]
        start_angle = 90
        for ext, cor in fatias:
            canvas_cat.create_arc(
                12, 12, 108, 108,
                start=start_angle,
                extent=-ext,
                outline=cor,
                width=16,
                style="arc",
            )
            start_angle -= ext

        # Centro do Donut
        canvas_cat.create_text(60, 54, text="R$ 5.420,30", fill="#FFFFFF", font=("Segoe UI", 10, "bold"))
        canvas_cat.create_text(60, 68, text="Total de despesas", fill="#94A3B8", font=("Segoe UI", 7))

        # Legenda com scroll ou grid
        legenda = ctk.CTkFrame(meio, fg_color="transparent")
        legenda.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        itens_legenda = [
            ("🟢", "Moradia", "28,6%", "R$ 1.550,00"),
            ("🟠", "Alimentação", "18,1%", "R$ 980,40"),
            ("🔴", "Transporte", "12,2%", "R$ 660,00"),
            ("🟣", "Saúde", "9,6%", "R$ 520,00"),
            ("🔵", "Lazer", "8,3%", "R$ 450,00"),
            ("🟣", "Educação", "7,4%", "R$ 400,00"),
            ("⚪", "Outros", "15,8%", "R$ 859,90"),
        ]

        for ic, nome, pct, val in itens_legenda[:6]:
            row = ctk.CTkFrame(legenda, fg_color="transparent")
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=ic, font=fonte(8)).pack(side="left", padx=(0, 3))
            ctk.CTkLabel(row, text=nome[:9], font=fonte(10), text_color=COR_TEXTO_PRINCIPAL, width=65, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=pct, font=fonte(9), text_color=COR_TEXTO_MUTED, width=35, anchor="e").pack(side="left")
            ctk.CTkLabel(row, text=val, font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="e").pack(side="right")

    def _build_panel_fluxo(self, parent, col: int):
        card = ctk.CTkFrame(
            parent,
            fg_color=COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=COR_BORDA,
            height=260,
        )
        card.grid(row=0, column=col, padx=(6, 0), sticky="nsew")
        card.grid_propagate(False)

        # Topo
        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(
            topo,
            text="Fluxo de Caixa",
            font=fonte(13, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
        ).pack(side="left")

        opt_periodo = ctk.CTkOptionMenu(
            topo,
            values=["Últimos 6 meses", "Este ano", "Últimos 12 meses"],
            width=115,
            height=24,
            fg_color=COR_CARD_INTERNO,
            button_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_SECUNDARIO,
            font=fonte(10),
        )
        opt_periodo.set("Últimos 6 meses")
        opt_periodo.pack(side="right")

        # Gráfico vetorial de linhas no Canvas
        canvas_fluxo = tk.Canvas(
            card,
            bg=obter_cor(COR_CARD),
            highlightthickness=0,
            height=160,
        )
        canvas_fluxo.pack(fill="both", expand=True, padx=14, pady=(0, 2))

        # Desenhar no canvas após layout
        def desenhar(event=None):
            canvas_fluxo.delete("all")
            w = canvas_fluxo.winfo_width()
            h = canvas_fluxo.winfo_height()
            if w <= 10 or h <= 10:
                w, h = 320, 150

            margem_esq = 45
            margem_dir = 20
            margem_topo = 15
            margem_base = 35

            # Grid e labels do eixo Y
            valores_y = [(0, "R$ 15 mil"), (0.33, "R$ 10 mil"), (0.66, "R$ 5 mil"), (1.0, "R$ 0")]
            for pct, txt in valores_y:
                y = margem_topo + pct * (h - margem_topo - margem_base)
                canvas_fluxo.create_line(margem_esq, y, w - margem_dir, y, fill="#1A2D3C", dash=(2, 4))
                canvas_fluxo.create_text(margem_esq - 6, y, text=txt, fill="#64748B", font=("Segoe UI", 7), anchor="e")

            # Meses e coordenadas
            meses = [
                ("Nov\n2025", 0.55, 0.70),
                ("Dez\n2025", 0.52, 0.68),
                ("Jan\n2026", 0.45, 0.65),
                ("Fev\n2026", 0.28, 0.58),
                ("Mar\n2026", 0.26, 0.59),
                ("Abr\n2026", 0.12, 0.50),
            ]

            step_x = (w - margem_esq - margem_dir) / (len(meses) - 1)
            pts_rec = []
            pts_desp = []

            for i, (mes, p_rec, p_desp) in enumerate(meses):
                x = margem_esq + i * step_x
                y_rec = margem_topo + p_rec * (h - margem_topo - margem_base)
                y_desp = margem_topo + p_desp * (h - margem_topo - margem_base)
                pts_rec.append((x, y_rec))
                pts_desp.append((x, y_desp))

                # Label mês
                canvas_fluxo.create_text(x, h - 14, text=mes, fill="#8EA3B8", font=("Segoe UI", 7), justify="center")

            # Linha Receitas (Teal / Verde neon)
            for i in range(len(pts_rec) - 1):
                canvas_fluxo.create_line(pts_rec[i][0], pts_rec[i][1], pts_rec[i+1][0], pts_rec[i+1][1], fill="#00D084", width=2)
            for x, y in pts_rec:
                canvas_fluxo.create_oval(x-3.5, y-3.5, x+3.5, y+3.5, fill="#00D084", outline="#101C26", width=1.5)

            # Linha Despesas (Coral / Vermelho)
            for i in range(len(pts_desp) - 1):
                canvas_fluxo.create_line(pts_desp[i][0], pts_desp[i][1], pts_desp[i+1][0], pts_desp[i+1][1], fill="#F43F5E", width=2)
            for x, y in pts_desp:
                canvas_fluxo.create_oval(x-3.5, y-3.5, x+3.5, y+3.5, fill="#F43F5E", outline="#101C26", width=1.5)

        canvas_fluxo.bind("<Configure>", desenhar)
        canvas_fluxo.after(100, desenhar)

        # Legenda inferior
        leg_fluxo = ctk.CTkFrame(card, fg_color="transparent")
        leg_fluxo.pack(fill="x", padx=14, pady=(0, 6))

        sub_leg = ctk.CTkFrame(leg_fluxo, fg_color="transparent")
        sub_leg.pack(anchor="center")

        ctk.CTkLabel(sub_leg, text="● Receitas", font=fonte(10, "bold"), text_color="#00D084").pack(side="left", padx=8)
        ctk.CTkLabel(sub_leg, text="● Despesas", font=fonte(10, "bold"), text_color="#F43F5E").pack(side="left", padx=8)

    # ==============================================================
    # 4. LINHA INFERIOR: 3 CARDS DE LISTAGEM
    # ==============================================================
    def _build_linha_listas(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 10))
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        # 4.1 Lançamentos Recentes
        self._build_lista_lancamentos(grid, col=0)

        # 4.2 Próximos Vencimentos
        self._build_lista_vencimentos(grid, col=1)

        # 4.3 Minhas Metas
        self._build_lista_metas(grid, col=2)

    def _build_lista_lancamentos(self, parent, col: int):
        card = ctk.CTkFrame(
            parent,
            fg_color=COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=COR_BORDA,
            height=300,
        )
        card.grid(row=0, column=col, padx=(0, 6), sticky="nsew")
        card.grid_propagate(False)

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=14, pady=(12, 8))

        ctk.CTkLabel(
            topo,
            text="Lançamentos Recentes",
            font=fonte(13, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
        ).pack(side="left")

        btn_ver = ctk.CTkButton(
            topo,
            text="Ver todos →",
            fg_color="transparent",
            hover_color=COR_CARD_INTERNO,
            text_color="#00D084",
            font=fonte(11),
            width=70,
            command=lambda: self._navegar_para("lancamento"),
        )
        btn_ver.pack(side="right")

        # Itens
        itens = [
            ("👛", "#102E24", "Salário", "Receita • 10/04/2026", "+ R$ 5.000,00", "#00D084"),
            ("🛒", "#2E151B", "Supermercado Extra", "Alimentação • 09/04/2026", "- R$ 286,40", "#F43F5E"),
            ("🚗", "#122538", "Uber", "Transporte • 08/04/2026", "- R$ 32,50", "#F43F5E"),
            ("❤️", "#2E151B", "Academia", "Saúde • 07/04/2026", "- R$ 120,00", "#F43F5E"),
            ("📺", "#241A35", "Netflix", "Lazer • 05/04/2026", "- R$ 39,90", "#F43F5E"),
        ]

        # Tentar pegar lançamentos reais do banco se existirem
        reais = self.dao.listar_todos()
        if reais:
            itens_reais = []
            for r in reais[:5]:
                eh_rec = (getattr(r, "tipo", "") == "Receita")
                cor_v = "#00D084" if eh_rec else "#F43F5E"
                sinal = "+ " if eh_rec else "- "
                bg_i = "#102E24" if eh_rec else "#2E151B"
                ic = "💰" if eh_rec else "🛒"
                itens_reais.append((
                    ic, bg_i, getattr(r, "descricao", "Lançamento"),
                    f"{getattr(r, 'categoria', 'Geral')} • {getattr(r, 'data', '')}",
                    f"{sinal}R$ {getattr(r, 'valor', 0):,.2f}", cor_v
                ))
            if itens_reais:
                itens = itens_reais

        for ic, bg_ic, tit, sub, val, cor_val in itens[:5]:
            linha = ctk.CTkFrame(card, fg_color="transparent")
            linha.pack(fill="x", padx=14, pady=3)

            # Ícone
            ic_box = ctk.CTkFrame(linha, width=32, height=32, corner_radius=8, fg_color=bg_ic)
            ic_box.pack(side="left", padx=(0, 10))
            ic_box.pack_propagate(False)

            ctk.CTkLabel(ic_box, text=ic, font=fonte(12)).place(relx=0.5, rely=0.5, anchor="center")

            # Textos
            txt_box = ctk.CTkFrame(linha, fg_color="transparent")
            txt_box.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(txt_box, text=tit[:18], font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
            ctk.CTkLabel(txt_box, text=sub[:24], font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

            # Valor
            ctk.CTkLabel(linha, text=val, font=fonte(11, "bold"), text_color=cor_val, anchor="e").pack(side="right")

    def _build_lista_vencimentos(self, parent, col: int):
        card = ctk.CTkFrame(
            parent,
            fg_color=COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=COR_BORDA,
            height=300,
        )
        card.grid(row=0, column=col, padx=3, sticky="nsew")
        card.grid_propagate(False)

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=14, pady=(12, 8))

        ctk.CTkLabel(
            topo,
            text="Próximos Vencimentos",
            font=fonte(13, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
        ).pack(side="left")

        btn_ver = ctk.CTkButton(
            topo,
            text="Ver todos →",
            fg_color="transparent",
            hover_color=COR_CARD_INTERNO,
            text_color="#00D084",
            font=fonte(11),
            width=70,
            command=lambda: self._navegar_para("lancamento"),
        )
        btn_ver.pack(side="right")

        itens = [
            ("12\nABR", "💳", "Cartão de Crédito", "Nubank • Fatura", "R$ 1.250,90", "Em 2 dias", "#F43F5E"),
            ("15\nABR", "🏠", "Aluguel", "Imobiliária XYZ", "R$ 1.550,00", "Em 5 dias", "#F59E0B"),
            ("18\nABR", "📶", "Internet", "Vivo Fibra", "R$ 120,00", "Em 8 dias", "#38BDF8"),
            ("20\nABR", "❤️", "Plano de Saúde", "Amil", "R$ 520,00", "Em 10 dias", "#38BDF8"),
            ("25\nABR", "🎓", "Escola", "Mensalidade", "R$ 400,00", "Em 15 dias", "#94A3B8"),
        ]

        for data_b, ic, tit, sub, val, prazo, cor_p in itens:
            linha = ctk.CTkFrame(card, fg_color="transparent")
            linha.pack(fill="x", padx=14, pady=3)

            # Badge Data
            d_box = ctk.CTkFrame(linha, width=30, height=32, corner_radius=6, fg_color="#182A3A")
            d_box.pack(side="left", padx=(0, 8))
            d_box.pack_propagate(False)

            ctk.CTkLabel(d_box, text=data_b, font=fonte(8, "bold"), text_color="#CBD5E1").place(relx=0.5, rely=0.5, anchor="center")

            # Ícone
            ic_box = ctk.CTkFrame(linha, width=30, height=32, corner_radius=6, fg_color="#122538")
            ic_box.pack(side="left", padx=(0, 8))
            ic_box.pack_propagate(False)

            ctk.CTkLabel(ic_box, text=ic, font=fonte(11)).place(relx=0.5, rely=0.5, anchor="center")

            # Textos
            txt_box = ctk.CTkFrame(linha, fg_color="transparent")
            txt_box.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(txt_box, text=tit[:16], font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
            ctk.CTkLabel(txt_box, text=sub[:20], font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

            # Valor e badge prazo
            dir_box = ctk.CTkFrame(linha, fg_color="transparent")
            dir_box.pack(side="right")

            ctk.CTkLabel(dir_box, text=val, font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="e").pack(anchor="e")
            ctk.CTkLabel(dir_box, text=prazo, font=fonte(9, "bold"), text_color=cor_p, anchor="e").pack(anchor="e")

    def _build_lista_metas(self, parent, col: int):
        card = ctk.CTkFrame(
            parent,
            fg_color=COR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=COR_BORDA,
            height=300,
        )
        card.grid(row=0, column=col, padx=(6, 0), sticky="nsew")
        card.grid_propagate(False)

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=14, pady=(12, 8))

        ctk.CTkLabel(
            topo,
            text="Minhas Metas",
            font=fonte(13, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
        ).pack(side="left")

        btn_ver = ctk.CTkButton(
            topo,
            text="Ver todas →",
            fg_color="transparent",
            hover_color=COR_CARD_INTERNO,
            text_color="#00D084",
            font=fonte(11),
            width=70,
            command=lambda: self._navegar_para("meta"),
        )
        btn_ver.pack(side="right")

        # Metas default ou reais
        metas = [
            ("✈", "Viagem para o Japão", "R$ 8.500,00 de R$ 15.000,00", 0.56, "56%"),
            ("🏠", "Entrada do Apê", "R$ 40.000,00 de R$ 120.000,00", 0.33, "33%"),
            ("🐷", "Reserva de Emergência", "R$ 12.000,00 de R$ 24.000,00", 0.50, "50%"),
        ]

        reais_metas = self.meta_dao.listar_todas()
        if reais_metas:
            custom_metas = []
            for m in reais_metas[:3]:
                alvo = getattr(m, "valor_alvo", 1) or 1
                atual = getattr(m, "valor_atual", 0) or 0
                pct = min(1.0, atual / alvo) if alvo > 0 else 0
                pct_txt = f"{int(pct * 100)}%"
                custom_metas.append((
                    "🎯", getattr(m, "titulo", "Meta"),
                    f"R$ {atual:,.2f} de R$ {alvo:,.2f}",
                    pct, pct_txt
                ))
            if custom_metas:
                metas = custom_metas

        for ic, tit, val_txt, pct, pct_txt in metas:
            box_meta = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=10, border_width=1, border_color=COR_BORDA)
            box_meta.pack(fill="x", padx=14, pady=5)

            topo_m = ctk.CTkFrame(box_meta, fg_color="transparent")
            topo_m.pack(fill="x", padx=10, pady=(8, 4))

            # Ícone
            ic_box = ctk.CTkFrame(topo_m, width=30, height=30, corner_radius=6, fg_color="#122538")
            ic_box.pack(side="left", padx=(0, 8))
            ic_box.pack_propagate(False)

            ctk.CTkLabel(ic_box, text=ic, font=fonte(13)).place(relx=0.5, rely=0.5, anchor="center")

            # Nome e valor
            t_box = ctk.CTkFrame(topo_m, fg_color="transparent")
            t_box.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(t_box, text=tit, font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
            ctk.CTkLabel(t_box, text=val_txt, font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

            ctk.CTkLabel(topo_m, text=pct_txt, font=fonte(11, "bold"), text_color="#00D084").pack(side="right")

            # Barra de progresso verde teal
            prog = ctk.CTkProgressBar(
                box_meta,
                height=6,
                corner_radius=3,
                progress_color="#00D084",
                fg_color="#1C2F3F",
            )
            prog.set(pct)
            prog.pack(fill="x", padx=10, pady=(2, 8))