"""
View de Lançamentos — Redesign Fiel à Referência (03_lancamentos.png)
======================================================================

Layout completo para registro e controle de transações:
1. Topo: Cabeçalho com ícone, título, subtítulo e seletor de mês.
2. Linha de Métricas: Total de Receitas, Total de Despesas e Saldo Líquido com mini sparklines.
3. Coluna Esquerda: Formulário moderno "Novo Lançamento" com alternador [Despesa / Receita],
   campos com ícones inline, categorias e beneficiários, e botão de salvar contextual.
4. Coluna Direita: "Lançamentos Recentes" com abas [Todos / Receitas / Despesas], barra de busca,
   tabela refinada com badges de data, ícones de categoria, status de pagamento e menu de ações.
"""
import tkinter as tk
from datetime import datetime, date
from typing import Optional, List
import customtkinter as ctk

from dao.lancamento_dao import LancamentoDAO
from dao.categoria_dao import CategoriaDAO
from dao.terceiro_dao import TerceiroDAO
from models.lancamento import Lancamento
from views.notificacao_toast import GerenciadorNotificacoes
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_SUCESSO, COR_ALERTA, COR_INFO,
    COR_RECEITA, COR_DESPESA, COR_BOTAO_SECUNDARIO,
    fonte, fonte_titulo, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
    obter_cor
)


class LancamentoView(ctk.CTkFrame):
    """Tela de Lançamentos redesenhada fiel à imagem 03_lancamentos.png."""

    def __init__(
        self,
        parent,
        dao: Optional[LancamentoDAO] = None,
        cat_dao: Optional[CategoriaDAO] = None,
        ter_dao: Optional[TerceiroDAO] = None,
    ):
        super().__init__(parent, fg_color="transparent")

        self.dao = dao or LancamentoDAO()
        self.cat_dao = cat_dao or CategoriaDAO()
        self.ter_dao = ter_dao or TerceiroDAO()

        self.tipo_selecionado = "Despesa"  # "Despesa" ou "Receita"
        self.filtro_aba = "Todos"          # "Todos", "Receitas", "Despesas"
        self.busca_texto = ""

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

        # 2. MÉTRICAS (3 CARDS COM MINI GRÁFICOS)
        self._build_metricas(scroll)

        # 3. CORPO: FORMULÁRIO (ESQ) + HISTÓRICO (DIR)
        corpo = ctk.CTkFrame(scroll, fg_color="transparent")
        corpo.pack(fill="both", expand=True, pady=(0, 10))
        corpo.grid_columnconfigure(0, weight=4)
        corpo.grid_columnconfigure(1, weight=6)

        self._build_formulario(corpo)
        self._build_painel_historico(corpo)

    # ==============================================================
    # 1. CABEÇALHO
    # ==============================================================
    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)

        tit_box = ctk.CTkFrame(header, fg_color="transparent")
        tit_box.grid(row=0, column=0, sticky="w")

        tit_row = ctk.CTkFrame(tit_box, fg_color="transparent")
        tit_row.pack(anchor="w")

        # Ícone de documento
        ic_box = ctk.CTkFrame(tit_row, width=32, height=32, corner_radius=8, fg_color="#182A3A")
        ic_box.pack(side="left", padx=(0, 10))
        ic_box.pack_propagate(False)
        ctk.CTkLabel(ic_box, text="📄", font=fonte(14)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(tit_row, text="Lançamentos", font=fonte(22, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        ctk.CTkLabel(
            tit_box,
            text="Registre e acompanhe todas as suas receitas, despesas e mantenha suas finanças em dia.",
            font=fonte(12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Seletor de mês
        nav_mes = ctk.CTkFrame(header, fg_color=COR_CARD, corner_radius=10, border_width=1, border_color=COR_BORDA)
        nav_mes.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(nav_mes, text="📅", font=fonte(12)).pack(side="left", padx=(10, 4))

        self.mes_combo = ctk.CTkOptionMenu(
            nav_mes,
            values=["Setembro de 2026", "Agosto de 2026", "Julho de 2026", "Abril de 2026"],
            width=140,
            height=30,
            fg_color=COR_CARD,
            button_color=COR_CARD_INTERNO,
            button_hover_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(12),
        )
        self.mes_combo.set("Setembro de 2026")
        self.mes_combo.pack(side="left", padx=2, pady=3)

        ctk.CTkButton(
            nav_mes, text="‹", width=28, height=28, corner_radius=6,
            fg_color="transparent", hover_color=COR_CARD_INTERNO, text_color=COR_TEXTO_SECUNDARIO, font=fonte(16, "bold")
        ).pack(side="left", padx=(0, 2), pady=3)

        ctk.CTkButton(
            nav_mes, text="›", width=28, height=28, corner_radius=6,
            fg_color="transparent", hover_color=COR_CARD_INTERNO, text_color=COR_TEXTO_SECUNDARIO, font=fonte(16, "bold")
        ).pack(side="left", padx=(0, 6), pady=3)

    # ==============================================================
    # 2. MÉTRICAS (3 CARDS COM MINI GRÁFICOS)
    # ==============================================================
    def _build_metricas(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 14))
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        # Calcular totais reais ou usar padrão de exibição
        lancamentos = self.dao.listar_todos()
        rec_tot = sum(l.valor for l in lancamentos if getattr(l, "tipo", "") == "Receita") if lancamentos else 4850.0
        desp_tot = sum(l.valor for l in lancamentos if getattr(l, "tipo", "") == "Despesa") if lancamentos else 3290.0
        saldo_tot = rec_tot - desp_tot if lancamentos else 1560.0

        cards_data = [
            ("↑", "#0D2E2B", "#00D084", "Total de Receitas", f"R$ {rec_tot:,.2f}", "+12% em relação ao mês anterior", "barras", "#00D084"),
            ("↓", "#2E151B", "#F43F5E", "Total de Despesas", f"R$ {desp_tot:,.2f}", "+8% em relação ao mês anterior", "barras", "#F43F5E"),
            ("💳", "#122538", "#38BDF8", "Saldo Líquido", f"R$ {saldo_tot:,.2f}", "+28% em relação ao mês anterior", "linha", "#38BDF8"),
        ]

        for idx, (ic, bg_ic, cor_ic, tit, val, foot, tipo_spark, cor_spark) in enumerate(cards_data):
            card = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
            card.grid(row=0, column=idx, padx=4, sticky="nsew")

            row_top = ctk.CTkFrame(card, fg_color="transparent")
            row_top.pack(fill="x", padx=14, pady=(12, 4))

            # Ícone
            ic_box = ctk.CTkFrame(row_top, width=34, height=34, corner_radius=17, fg_color=bg_ic)
            ic_box.pack(side="left", padx=(0, 10))
            ic_box.pack_propagate(False)
            ctk.CTkLabel(ic_box, text=ic, font=fonte(14, "bold"), text_color=cor_ic).place(relx=0.5, rely=0.5, anchor="center")

            # Título e Valor
            t_box = ctk.CTkFrame(row_top, fg_color="transparent")
            t_box.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(t_box, text=tit, font=fonte(11), text_color=COR_TEXTO_SECUNDARIO, anchor="w").pack(anchor="w")
            ctk.CTkLabel(t_box, text=val, font=fonte(18, "bold"), text_color=cor_ic, anchor="w").pack(anchor="w")

            # Mini sparkline à direita
            canvas_spark = tk.Canvas(row_top, width=50, height=34, bg=obter_cor(COR_CARD), highlightthickness=0)
            canvas_spark.pack(side="right")

            if tipo_spark == "barras":
                alturas = [0.3, 0.5, 0.4, 0.7, 0.9, 0.6]
                for b_i, h_p in enumerate(alturas):
                    bx = b_i * 8 + 2
                    by = 34 - (h_p * 26)
                    canvas_spark.create_rectangle(bx, by, bx + 5, 34, fill=cor_spark, outline="")
            else:
                pts = [(2, 26), (12, 22), (22, 24), (32, 12), (42, 14), (48, 6)]
                for p_i in range(len(pts) - 1):
                    canvas_spark.create_line(pts[p_i][0], pts[p_i][1], pts[p_i+1][0], pts[p_i+1][1], fill=cor_spark, width=2)

            # Footer
            ctk.CTkLabel(
                card,
                text=f"▲ {foot}",
                font=fonte(10),
                text_color=cor_ic,
                anchor="w",
            ).pack(anchor="w", padx=14, pady=(2, 12))

    # ==============================================================
    # 3. FORMULÁRIO (COLUNA ESQUERDA)
    # ==============================================================
    def _build_formulario(self, parent):
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

        ic_box = ctk.CTkFrame(topo, width=32, height=32, corner_radius=16, fg_color="#0D2E2B")
        ic_box.pack(side="left", padx=(0, 10))
        ic_box.pack_propagate(False)
        ctk.CTkLabel(ic_box, text="＋", font=fonte(14, "bold"), text_color="#00D084").place(relx=0.5, rely=0.5, anchor="center")

        tit_box = ctk.CTkFrame(topo, fg_color="transparent")
        tit_box.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(tit_box, text="Novo Lançamento", font=fonte(14, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(tit_box, text="Registre uma receita ou despesa de forma rápida e organizada.", font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        # Pílulas Seletoras: [- Despesa] e [+ Receita]
        pilula_box = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=10, height=42)
        pilula_box.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_tipo_despesa = ctk.CTkButton(
            pilula_box,
            text="⛔  Despesa",
            height=34,
            corner_radius=8,
            fg_color="#F43F5E" if self.tipo_selecionado == "Despesa" else "transparent",
            text_color="#FFFFFF" if self.tipo_selecionado == "Despesa" else COR_TEXTO_SECUNDARIO,
            hover_color="#E11D48",
            font=fonte(12, "bold"),
            command=lambda: self._set_tipo("Despesa"),
        )
        self.btn_tipo_despesa.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        self.btn_tipo_receita = ctk.CTkButton(
            pilula_box,
            text="＋  Receita",
            height=34,
            corner_radius=8,
            fg_color="#00D084" if self.tipo_selecionado == "Receita" else "transparent",
            text_color="#0B131B" if self.tipo_selecionado == "Receita" else COR_TEXTO_SECUNDARIO,
            hover_color="#00B875",
            font=fonte(12, "bold"),
            command=lambda: self._set_tipo("Receita"),
        )
        self.btn_tipo_receita.pack(side="right", fill="both", expand=True, padx=4, pady=4)

        # Campo: Valor (R$) *
        ctk.CTkLabel(card, text="Valor (R$) *", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_val = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=38)
        f_val.pack(fill="x", padx=16, pady=(0, 12))
        f_val.pack_propagate(False)

        ctk.CTkLabel(f_val, text="💰", font=fonte(13)).pack(side="left", padx=10)
        self.entry_valor = ctk.CTkEntry(
            f_val, placeholder_text="0,00", font=fonte(13, "bold"), fg_color="transparent", border_width=0, text_color=COR_TEXTO_PRINCIPAL
        )
        self.entry_valor.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Campo: Descrição *
        ctk.CTkLabel(card, text="Descrição *", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_desc = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=38)
        f_desc.pack(fill="x", padx=16, pady=(0, 12))
        f_desc.pack_propagate(False)

        ctk.CTkLabel(f_desc, text="📄", font=fonte(13)).pack(side="left", padx=10)
        self.entry_desc = ctk.CTkEntry(
            f_desc, placeholder_text="Ex: Aluguel, Supermercado, Conta de Luz...", font=fonte(11), fg_color="transparent", border_width=0, text_color=COR_TEXTO_PRINCIPAL
        )
        self.entry_desc.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Linha dupla: Categoria e Beneficiário
        grid_campos = ctk.CTkFrame(card, fg_color="transparent")
        grid_campos.pack(fill="x", padx=16, pady=(0, 12))
        grid_campos.grid_columnconfigure((0, 1), weight=1)

        # Categoria
        ctk.CTkLabel(grid_campos, text="Categoria *", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=0, sticky="w", pady=(0, 4))
        f_cat = ctk.CTkFrame(grid_campos, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=38)
        f_cat.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        f_cat.pack_propagate(False)

        ctk.CTkLabel(f_cat, text="🍴", font=fonte(12)).pack(side="left", padx=(8, 4))

        cats = []
        if self.cat_dao:
            try:
                for c in self.cat_dao.listar_todas():
                    cats.append(c["nome"] if isinstance(c, dict) else getattr(c, "nome", str(c)))
            except Exception:
                pass
        if not cats:
            cats = ["Alimentação", "Moradia", "Transporte", "Saúde", "Lazer", "Educação", "Salário", "Investimentos", "Outros"]

        self.combo_categoria = ctk.CTkOptionMenu(
            f_cat,
            values=cats,
            height=30,
            fg_color=COR_CARD_INTERNO,
            button_color=COR_CARD,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(11),
        )
        self.combo_categoria.set(cats[0])
        self.combo_categoria.pack(side="left", fill="both", expand=True)

        # Beneficiário / Fornecedor
        ctk.CTkLabel(grid_campos, text="Beneficiário / Fornecedor", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=1, sticky="w", pady=(0, 4))
        f_ter = ctk.CTkFrame(grid_campos, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=38)
        f_ter.grid(row=1, column=1, sticky="ew", padx=(6, 0))
        f_ter.pack_propagate(False)

        ctk.CTkLabel(f_ter, text="👤", font=fonte(12)).pack(side="left", padx=(8, 4))
        self.entry_beneficiario = ctk.CTkEntry(
            f_ter, placeholder_text="Ex: Pão de Açúcar", font=fonte(11), fg_color="transparent", border_width=0, text_color=COR_TEXTO_PRINCIPAL
        )
        self.entry_beneficiario.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Linha dupla: Data e Status
        grid_campos2 = ctk.CTkFrame(card, fg_color="transparent")
        grid_campos2.pack(fill="x", padx=16, pady=(0, 6))
        grid_campos2.grid_columnconfigure((0, 1), weight=1)

        # Data
        ctk.CTkLabel(grid_campos2, text="Data *", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=0, sticky="w", pady=(0, 4))
        f_dat = ctk.CTkFrame(grid_campos2, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=38)
        f_dat.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        f_dat.pack_propagate(False)

        ctk.CTkLabel(f_dat, text="📅", font=fonte(12)).pack(side="left", padx=(8, 4))
        self.entry_data = ctk.CTkEntry(
            f_dat, font=fonte(11), fg_color="transparent", border_width=0, text_color=COR_TEXTO_PRINCIPAL
        )
        self.entry_data.insert(0, date.today().strftime("%d/%m/%Y"))
        self.entry_data.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Status
        ctk.CTkLabel(grid_campos2, text="Status do Pagamento", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=1, sticky="w", pady=(0, 4))
        f_stat = ctk.CTkFrame(grid_campos2, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=38)
        f_stat.grid(row=1, column=1, sticky="ew", padx=(6, 0))
        f_stat.pack_propagate(False)

        ctk.CTkLabel(f_stat, text="💳", font=fonte(12)).pack(side="left", padx=(8, 4))
        self.combo_status = ctk.CTkOptionMenu(
            f_stat,
            values=["Pago", "Pendente", "Recebido"],
            height=30,
            fg_color=COR_CARD_INTERNO,
            button_color=COR_CARD,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(11),
        )
        self.combo_status.set("Pago")
        self.combo_status.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(card, text="ⓘ Formato da data: DD/MM/AAAA", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 14))

        # Botões Salvar e Limpar
        botoes_box = ctk.CTkFrame(card, fg_color="transparent")
        botoes_box.pack(fill="x", padx=16, pady=(0, 16))

        cor_btn_salvar = "#F43F5E" if self.tipo_selecionado == "Despesa" else "#00D084"
        self.btn_salvar = ctk.CTkButton(
            botoes_box,
            text="＋  Salvar Lançamento",
            height=40,
            corner_radius=10,
            fg_color=cor_btn_salvar,
            hover_color="#E11D48" if self.tipo_selecionado == "Despesa" else "#00B875",
            text_color="#FFFFFF" if self.tipo_selecionado == "Despesa" else "#0B131B",
            font=fonte(12, "bold"),
            command=self._salvar_lancamento,
        )
        self.btn_salvar.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            botoes_box,
            text="🔄  Limpar Campos",
            height=40,
            width=130,
            corner_radius=10,
            fg_color=COR_CARD_INTERNO,
            hover_color="#1E2F40",
            text_color=COR_TEXTO_SECUNDARIO,
            font=fonte(11),
            command=self._limpar_formulario,
        ).pack(side="right")

    def _set_tipo(self, novo_tipo: str):
        self.tipo_selecionado = novo_tipo
        if novo_tipo == "Despesa":
            self.btn_tipo_despesa.configure(fg_color="#F43F5E", text_color="#FFFFFF")
            self.btn_tipo_receita.configure(fg_color="transparent", text_color=COR_TEXTO_SECUNDARIO)
            self.btn_salvar.configure(fg_color="#F43F5E", hover_color="#E11D48", text_color="#FFFFFF")
            self.combo_status.set("Pago")
        else:
            self.btn_tipo_despesa.configure(fg_color="transparent", text_color=COR_TEXTO_SECUNDARIO)
            self.btn_tipo_receita.configure(fg_color="#00D084", text_color="#0B131B")
            self.btn_salvar.configure(fg_color="#00D084", hover_color="#00B875", text_color="#0B131B")
            self.combo_status.set("Recebido")

    def _limpar_formulario(self):
        self.entry_valor.delete(0, "end")
        self.entry_desc.delete(0, "end")
        self.entry_beneficiario.delete(0, "end")
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, date.today().strftime("%d/%m/%Y"))

    def _salvar_lancamento(self):
        try:
            val_txt = self.entry_valor.get().replace("R$", "").replace(".", "").replace(",", ".").strip()
            val = float(val_txt)
        except Exception:
            return

        desc = self.entry_desc.get().strip() or "Lançamento"
        cat = self.combo_categoria.get()
        data_txt = self.entry_data.get().strip()

        try:
            d_obj = datetime.strptime(data_txt, "%d/%m/%Y")
            data_sql = d_obj.strftime("%Y-%m-%d")
        except Exception:
            data_sql = date.today().strftime("%Y-%m-%d")

        novo = Lancamento(
            descricao=desc,
            valor=val,
            tipo=self.tipo_selecionado,
            categoria=cat,
            data=data_sql,
        )
        self.dao.inserir(novo)
        self._limpar_formulario()
        self._montar_tela()

    # ==============================================================
    # 4. HISTÓRICO RECENTE (COLUNA DIREITA)
    # ==============================================================
    def _build_painel_historico(self, parent):
        card = ctk.CTkFrame(
            parent,
            fg_color=COR_CARD,
            corner_radius=14,
            border_width=1,
            border_color=COR_BORDA,
        )
        card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Topo
        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 10))

        ic_box = ctk.CTkFrame(topo, width=32, height=32, corner_radius=16, fg_color="#0D2E2B")
        ic_box.pack(side="left", padx=(0, 10))
        ic_box.pack_propagate(False)
        ctk.CTkLabel(ic_box, text="🕒", font=fonte(13)).place(relx=0.5, rely=0.5, anchor="center")

        tit_box = ctk.CTkFrame(topo, fg_color="transparent")
        tit_box.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(tit_box, text="Lançamentos Recentes", font=fonte(14, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(tit_box, text="Acompanhe, edite ou filtre seus lançamentos.", font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        ctk.CTkButton(
            topo, text="Ver todos →", fg_color="transparent", hover_color=COR_CARD_INTERNO, text_color="#00D084", font=fonte(11), width=70
        ).pack(side="right")

        # Barra de Filtros em Abas e Busca
        barra_busca = ctk.CTkFrame(card, fg_color="transparent")
        barra_busca.pack(fill="x", padx=16, pady=(0, 12))
        barra_busca.grid_columnconfigure(1, weight=1)

        # Abas de filtro
        abas_frame = ctk.CTkFrame(barra_busca, fg_color=COR_CARD_INTERNO, corner_radius=8, height=34)
        abas_frame.grid(row=0, column=0, sticky="w", padx=(0, 10))

        for aba_nome in ["Todos (7)", "Receitas (3)", "Despesas (4)"]:
            nome_puro = aba_nome.split()[0]
            ativo = (nome_puro == self.filtro_aba)
            b = ctk.CTkButton(
                abas_frame,
                text=aba_nome,
                height=26,
                corner_radius=6,
                fg_color="#00D084" if ativo else "transparent",
                text_color="#0B131B" if ativo else COR_TEXTO_SECUNDARIO,
                font=fonte(10, "bold" if ativo else "normal"),
                command=lambda a=nome_puro: self._filtrar_aba(a),
            )
            b.pack(side="left", padx=2, pady=4)

        # Campo de busca
        f_busca = ctk.CTkFrame(barra_busca, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=34)
        f_busca.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        f_busca.pack_propagate(False)

        ctk.CTkLabel(f_busca, text="🔍", font=fonte(11)).pack(side="left", padx=8)
        self.entry_busca = ctk.CTkEntry(
            f_busca, placeholder_text="Buscar por descrição, categoria...", font=fonte(11), fg_color="transparent", border_width=0, text_color=COR_TEXTO_PRINCIPAL
        )
        self.entry_busca.pack(side="left", fill="both", expand=True)

        # Botão de sliders de filtro
        ctk.CTkButton(
            barra_busca, text="🎛️", width=34, height=34, corner_radius=8, fg_color=COR_CARD_INTERNO, hover_color="#1E2F40", text_color=COR_TEXTO_PRINCIPAL
        ).grid(row=0, column=2, sticky="e")

        # Cabeçalho da Tabela
        th = ctk.CTkFrame(card, fg_color="transparent")
        th.pack(fill="x", padx=16, pady=(0, 6))

        ctk.CTkLabel(th, text="Data ↕", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=60, anchor="w").pack(side="left")
        ctk.CTkLabel(th, text="Descrição", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=150, anchor="w").pack(side="left", padx=(10, 0))
        ctk.CTkLabel(th, text="Categoria", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=100, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(th, text="Status", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=80, anchor="w").pack(side="left")
        ctk.CTkLabel(th, text="Ações", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=40, anchor="center").pack(side="right", padx=(4, 6))
        ctk.CTkLabel(th, text="Valor (R$)", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, anchor="e").pack(side="right", padx=(0, 10))

        # Lista de Lançamentos
        lancamentos_demo = getattr(self, "_itens_demo_cache", [
            ("29\nSET", "🛒", "#2E151B", "Supermercado Extra", "Compras do mês", "🍴 Alimentação", "● Pago", "- R$ 320,50", "#F43F5E", None),
            ("28\nSET", "💼", "#102E24", "Salário", "Empresa XYZ", "💼 Salário", "● Pago", "+ R$ 3.500,00", "#00D084", None),
            ("25\nSET", "🏠", "#2E151B", "Aluguel", "Apartamento", "🏠 Moradia", "● Pago", "- R$ 1.200,00", "#F43F5E", None),
            ("23\nSET", "📈", "#102E24", "Rendimento CDB", "Banco Inter", "📈 Investimentos", "● Pago", "+ R$ 150,00", "#00D084", None),
            ("20\nSET", "💡", "#2E151B", "Conta de Luz", "Enel", "📄 Contas", "● Pago", "- R$ 180,90", "#F43F5E", None),
            ("18\nSET", "🚗", "#2E151B", "Combustível", "Posto Ipiranga", "🚗 Transporte", "● Pago", "- R$ 230,00", "#F43F5E", None),
            ("15\nSET", "💻", "#102E24", "Freelance - Projeto", "Cliente ABC", "💼 Serviços", "● Recebido", "+ R$ 1.200,00", "#00D084", None),
        ])

        # Pegar lançamentos reais do banco
        reais = self.dao.listar_todos()
        if reais:
            demo_convertido = []
            for r in reais:
                eh_rec = (getattr(r, "tipo", "") == "Receita")
                cor_v = "#00D084" if eh_rec else "#F43F5E"
                sinal = "+ " if eh_rec else "- "
                bg_i = "#102E24" if eh_rec else "#2E151B"
                ic = "💼" if eh_rec else "🛒"
                d_str = getattr(r, "data", "")
                badge_d = d_str[-5:].replace("-", "\n") if len(d_str) >= 5 else "HOJE"
                lid = getattr(r, "id", None)
                demo_convertido.append((
                    badge_d, ic, bg_i, getattr(r, "descricao", "Item"),
                    "Detalhe", getattr(r, "categoria", "Geral"),
                    "● Pago" if not eh_rec else "● Recebido",
                    f"{sinal}R$ {getattr(r, 'valor', 0):,.2f}", cor_v, lid
                ))
            if demo_convertido:
                lancamentos_demo = demo_convertido

        for d_badge, ic, bg_ic, tit, sub, cat_b, st_b, val, cor_val, lid in lancamentos_demo:
            linha = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, height=48)
            linha.pack(fill="x", padx=16, pady=3)
            linha.pack_propagate(False)

            # Badge Data
            d_box = ctk.CTkFrame(linha, width=32, height=32, corner_radius=6, fg_color="#182A3A")
            d_box.pack(side="left", padx=(8, 8))
            d_box.pack_propagate(False)
            ctk.CTkLabel(d_box, text=d_badge, font=fonte(8, "bold"), text_color="#CBD5E1").place(relx=0.5, rely=0.5, anchor="center")

            # Ícone
            ic_box = ctk.CTkFrame(linha, width=30, height=30, corner_radius=6, fg_color=bg_ic)
            ic_box.pack(side="left", padx=(0, 8))
            ic_box.pack_propagate(False)
            ctk.CTkLabel(ic_box, text=ic, font=fonte(12)).place(relx=0.5, rely=0.5, anchor="center")

            # Título e Subtítulo
            t_box = ctk.CTkFrame(linha, fg_color="transparent", width=140)
            t_box.pack(side="left", fill="y", padx=(0, 8))
            t_box.pack_propagate(False)

            ctk.CTkLabel(t_box, text=tit[:18], font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w", pady=(6, 0))
            ctk.CTkLabel(t_box, text=sub[:20], font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

            # Badge Categoria
            cat_box = ctk.CTkFrame(linha, fg_color="#182836", corner_radius=6, height=24)
            cat_box.pack(side="left", padx=(0, 10))
            ctk.CTkLabel(cat_box, text=f" {cat_b} ", font=fonte(9), text_color=COR_TEXTO_SECUNDARIO).pack(padx=4, pady=2)

            # Status
            st_cor = "#00D084" if "Pago" in st_b or "Recebido" in st_b else "#F59E0B"
            ctk.CTkLabel(linha, text=st_b, font=fonte(10, "bold"), text_color=st_cor, width=70, anchor="w").pack(side="left")

            # Botão Apagar / Excluir
            ctk.CTkButton(
                linha,
                text="🗑️",
                width=28,
                height=28,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#3E1A23",
                text_color="#F43F5E",
                font=fonte(11),
                command=lambda id_=lid, t=tit: self._apagar_lancamento(id_, t),
            ).pack(side="right", padx=(4, 6))

            # Valor
            ctk.CTkLabel(linha, text=val, font=fonte(11, "bold"), text_color=cor_val, anchor="e").pack(side="right", padx=6)

        ctk.CTkLabel(card, text="", height=8).pack()


    def _apagar_lancamento(self, lancamento_id: Optional[int], descricao: str):
        """Exclui um lançamento do banco de dados ou da lista em exibição."""
        from tkinter import messagebox
        if messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente apagar o lançamento '{descricao}'?"):
            if lancamento_id is not None:
                try:
                    self.dao.excluir(lancamento_id)
                except Exception as exc:
                    print(f"Erro ao excluir: {exc}")
            else:
                # Remove do cache demo
                if hasattr(self, "_itens_demo_cache"):
                    self._itens_demo_cache = [x for x in self._itens_demo_cache if x[3] != descricao]
                else:
                    self._itens_demo_cache = [
                        ("29\nSET", "🛒", "#2E151B", "Supermercado Extra", "Compras do mês", "🍴 Alimentação", "● Pago", "- R$ 320,50", "#F43F5E", None),
                        ("28\nSET", "💼", "#102E24", "Salário", "Empresa XYZ", "💼 Salário", "● Pago", "+ R$ 3.500,00", "#00D084", None),
                        ("25\nSET", "🏠", "#2E151B", "Aluguel", "Apartamento", "🏠 Moradia", "● Pago", "- R$ 1.200,00", "#F43F5E", None),
                        ("23\nSET", "📈", "#102E24", "Rendimento CDB", "Banco Inter", "📈 Investimentos", "● Pago", "+ R$ 150,00", "#00D084", None),
                        ("20\nSET", "💡", "#2E151B", "Conta de Luz", "Enel", "📄 Contas", "● Pago", "- R$ 180,90", "#F43F5E", None),
                        ("18\nSET", "🚗", "#2E151B", "Combustível", "Posto Ipiranga", "🚗 Transporte", "● Pago", "- R$ 230,00", "#F43F5E", None),
                        ("15\nSET", "💻", "#102E24", "Freelance - Projeto", "Cliente ABC", "💼 Serviços", "● Recebido", "+ R$ 1.200,00", "#00D084", None),
                    ]
                    self._itens_demo_cache = [x for x in self._itens_demo_cache if x[3] != descricao]

            self._montar_tela()

    def _filtrar_aba(self, aba: str):
        self.filtro_aba = aba
        self._montar_tela()