"""
View de Categorias — Redesign Fiel à Referência (08_categorias.png)
===================================================================

Gerenciador de categorias e limites de gastos:
1. Topo: Título com subtítulo e card de dica contextual.
2. Métricas: 4 Cards (Total de Categorias, Categorias de Despesas, Categorias de Receitas, Uso do Orçamento).
3. Coluna Esquerda: Abas de filtro [Todas / Despesas / Receitas], busca, tabela estilizada com ícones,
   badges de tipo, contexto de uso, limites e barras de progresso percentuais.
4. Coluna Direita: Formulário "Nova Categoria" e painel de "Categorias Sugeridas" em grid interativo.
"""
import tkinter as tk
from datetime import datetime, date
from typing import Optional, Dict, Any, List
import customtkinter as ctk

from dao.categoria_dao import CategoriaDAO
from models.categoria import Categoria
from services.visao_financeira import campo
from views.notificacao_toast import GerenciadorNotificacoes
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_SUCESSO, COR_ALERTA, COR_INFO,
    fonte, fonte_titulo, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
)


class CategoriaView(ctk.CTkFrame):
    """Tela de Categorias redesenhada fiel à imagem 08_categorias.png."""

    def __init__(self, parent, dao: Optional[CategoriaDAO] = None):
        super().__init__(parent, fg_color="transparent")
        self.dao = dao or CategoriaDAO()
        self.filtro_tipo = "Todas"

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

        # 3. CORPO: TABELA (ESQ) + NOVA CATEGORIA & SUGESTÕES (DIR)
        corpo = ctk.CTkFrame(scroll, fg_color="transparent")
        corpo.pack(fill="both", expand=True, pady=(0, 10))
        corpo.grid_columnconfigure(0, weight=6)
        corpo.grid_columnconfigure(1, weight=4)

        self._build_coluna_tabela(corpo)
        self._build_coluna_formulario(corpo)

    # ==============================================================
    # 1. CABEÇALHO
    # ==============================================================
    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)

        tit_box = ctk.CTkFrame(header, fg_color="transparent")
        tit_box.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(tit_box, text="Categorias", font=fonte(22, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(
            tit_box,
            text="Organize seus gastos e receitas com categorias personalizadas.",
            font=fonte(12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Card de Dica à direita
        dica_box = ctk.CTkFrame(
            header,
            fg_color=("#FEF3C7", "#1E1A11"),
            corner_radius=10,
            border_width=1,
            border_color=("#FDE68A", "#3E3019"),
        )
        dica_box.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(dica_box, text="💡", font=fonte(14)).pack(side="left", padx=(12, 6), pady=8)

        t_d = ctk.CTkFrame(dica_box, fg_color="transparent")
        t_d.pack(side="left", padx=(0, 14), pady=8)

        ctk.CTkLabel(t_d, text="Dica", font=fonte(10, "bold"), text_color=("#D97706", "#F59E0B"), anchor="w").pack(anchor="w")
        ctk.CTkLabel(
            t_d,
            text="Use categorias para ter relatórios mais precisos\ne acompanhar seus limites de gastos.",
            font=fonte(9),
            text_color=("#92400E", "#FCD34D"),
            justify="left",
            anchor="w",
        ).pack(anchor="w")

    # ==============================================================
    # 2. MÉTRICAS (4 CARDS)
    # ==============================================================
    def _build_metricas(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 14))
        for c in range(4):
            grid.grid_columnconfigure(c, weight=1)

        reais = self.dao.listar_todas()
        desp = [c for c in reais if campo(c, 'tipo', '') == 'Despesa']
        rec = [c for c in reais if campo(c, 'tipo', '') == 'Receita']
        limite = sum(float(campo(c, 'limite_orcamento', 0) or 0) for c in desp)
        cards = [
            ("📁", "#122538", "#38BDF8", "Total de Categorias", str(len(reais)), "Cadastradas no MySQL", None),
            ("↓", "#2E151B", "#F43F5E", "Categorias de Despesas", str(len(desp)), "Somente desta conta", None),
            ("↑", "#0D2E2B", "#00D084", "Categorias de Receitas", str(len(rec)), "Somente desta conta", None),
            ("⏱", "#122538", "#38BDF8", "Limites mensais", f"R$ {limite:,.2f}", "Valores cadastrados", None),
        ]

        for idx, (ic, bg_ic, cor_ic, tit, val, sub, prog_val) in enumerate(cards):
            card = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
            card.grid(row=0, column=idx, padx=4, sticky="nsew")

            topo_c = ctk.CTkFrame(card, fg_color="transparent")
            topo_c.pack(fill="x", padx=14, pady=(12, 4))

            ic_box = ctk.CTkFrame(topo_c, width=32, height=32, corner_radius=8, fg_color=bg_ic)
            ic_box.pack(side="left", padx=(0, 10))
            ic_box.pack_propagate(False)
            ctk.CTkLabel(ic_box, text=ic, font=fonte(12)).place(relx=0.5, rely=0.5, anchor="center")

            t_box = ctk.CTkFrame(topo_c, fg_color="transparent")
            t_box.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(t_box, text=tit, font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")
            ctk.CTkLabel(t_box, text=val, font=fonte(18, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")

            if prog_val is not None:
                p = ctk.CTkProgressBar(card, height=6, corner_radius=3, progress_color="#38BDF8", fg_color="#1C2F3F")
                p.set(prog_val)
                p.pack(fill="x", padx=14, pady=(2, 4))

            ctk.CTkLabel(card, text=sub, font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w", padx=14, pady=(0, 10))

    # ==============================================================
    # 3. COLUNA ESQUERDA: TABELA DE CATEGORIAS
    # ==============================================================
    def _build_coluna_tabela(self, parent):
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Barra de Abas / Filtro e Busca
        bar_f = ctk.CTkFrame(col, fg_color="transparent")
        bar_f.pack(fill="x", pady=(0, 10))
        bar_f.grid_columnconfigure(1, weight=1)

        # Abas
        abas = ctk.CTkFrame(bar_f, fg_color=COR_CARD_INTERNO, corner_radius=8, height=32)
        abas.grid(row=0, column=0, sticky="w", padx=(0, 8))

        atuais = self.dao.listar_todas()
        qtd_despesas = sum(campo(c, "tipo") == "Despesa" for c in atuais)
        qtd_receitas = sum(campo(c, "tipo") == "Receita" for c in atuais)
        for nome_p, qtde in [("Todas", len(atuais)), ("Despesas", qtd_despesas), ("Receitas", qtd_receitas)]:
            aba_txt = f"{nome_p} ({qtde})"
            ativo = (nome_p == self.filtro_tipo)
            ctk.CTkButton(
                abas,
                text=aba_txt,
                height=26,
                corner_radius=6,
                fg_color="#00D084" if ativo else "transparent",
                text_color="#0B131B" if ativo else COR_TEXTO_SECUNDARIO,
                font=fonte(10, "bold" if ativo else "normal"),
                command=lambda v=nome_p: self._set_filtro(v),
            ).pack(side="left", padx=2, pady=3)

        # Campo de busca
        f_b = ctk.CTkFrame(bar_f, fg_color=COR_CARD, corner_radius=8, border_width=1, border_color=COR_BORDA, height=32)
        f_b.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        f_b.pack_propagate(False)

        ctk.CTkLabel(f_b, text="🔍", font=fonte(10)).pack(side="left", padx=8)
        self.entry_busca = ctk.CTkEntry(
            f_b, placeholder_text="Buscar categoria pelo nome...", fg_color="transparent", border_width=0, font=fonte(10)
        )
        self.entry_busca.pack(side="left", fill="both", expand=True)

        # Ordenar
        opt_ord = ctk.CTkOptionMenu(
            bar_f,
            values=["Mais recentes", "Maior limite", "Ordem alfabética"],
            width=110,
            height=32,
            fg_color=COR_CARD,
            button_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(10),
        )
        opt_ord.set("Mais recentes")
        opt_ord.grid(row=0, column=2, sticky="e")

        # Card da Tabela
        card_tab = ctk.CTkFrame(col, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card_tab.pack(fill="x")

        # Cabeçalho da Tabela
        th = ctk.CTkFrame(card_tab, fg_color="transparent")
        th.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(th, text="Categoria", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=140, anchor="w").pack(side="left")
        ctk.CTkLabel(th, text="Tipo", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=70, anchor="w").pack(side="left", padx=6)
        ctk.CTkLabel(th, text="Contexto de Uso", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=90, anchor="w").pack(side="left")
        ctk.CTkLabel(th, text="Limite / Meta Mensal", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=110, anchor="w").pack(side="left")
        ctk.CTkLabel(th, text="Progresso", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=110, anchor="w").pack(side="left")
        ctk.CTkLabel(th, text="Ações", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, anchor="e").pack(side="right", padx=(0, 6))

        # Mostrar somente categorias reais do usuário autenticado.
        categorias_demo = []
        reais = self.dao.listar_todas()
        from dao.lancamento_dao import LancamentoDAO
        from services.visao_financeira import resumo, dinheiro
        totais = dict(resumo(LancamentoDAO().listar_todos())["categorias"])
        for cat in reais:
            eh_rec = (campo(cat, "tipo", "") == "Receita")
            nome = campo(cat, "nome", "Categoria")
            lim = float(campo(cat, "limite_orcamento", 0) or 0)
            gasto = totais.get(nome, 0) if not eh_rec else 0
            progresso = min(1.0, gasto / lim) if lim > 0 else 0.0
            categorias_demo.append((
                "🏷️", "#0D2E2B" if eh_rec else "#2E151B", nome,
                campo(cat, "tipo", "Despesa"), campo(cat, "escopo", "Pessoal"),
                dinheiro(lim) if lim else "Sem limite", progresso,
                f"{progresso:.0%}" if lim > 0 else "—",
                "#00D084" if eh_rec or progresso < 1 else "#F43F5E", campo(cat, "id", None),
            ))
        if not categorias_demo:
            ctk.CTkLabel(card_tab, text="Nenhuma categoria cadastrada nesta conta.",
                         text_color=COR_TEXTO_SECUNDARIO, font=fonte(12)).pack(pady=22)

        if self.filtro_tipo != "Todas":
            tipo_alvo = "Despesa" if self.filtro_tipo == "Despesas" else "Receita"
            categorias_demo = [c for c in categorias_demo if c[3] == tipo_alvo]

        categorias_fmt = []
        for item in categorias_demo:
            if len(item) == 9:
                categorias_fmt.append((*item, None))
            else:
                categorias_fmt.append(item)

        for ic, bg_ic, nom, tip, ctx, lim, prog_p, prog_txt, cor_p, cid in categorias_fmt:
            row = ctk.CTkFrame(card_tab, fg_color=COR_CARD_INTERNO, corner_radius=8, height=44)
            row.pack(fill="x", padx=14, pady=2)
            row.pack_propagate(False)

            # Ícone
            ic_box = ctk.CTkFrame(row, width=28, height=28, corner_radius=6, fg_color=bg_ic)
            ic_box.pack(side="left", padx=(8, 8))
            ic_box.pack_propagate(False)
            ctk.CTkLabel(ic_box, text=ic, font=fonte(11)).place(relx=0.5, rely=0.5, anchor="center")

            # Nome
            ctk.CTkLabel(row, text=nom, font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL, width=105, anchor="w").pack(side="left")

            # Badge Tipo
            bg_tipo = "#2E151B" if tip == "Despesa" else "#0D2E2B"
            cor_tipo = "#F43F5E" if tip == "Despesa" else "#00D084"
            tb = ctk.CTkFrame(row, fg_color=bg_tipo, corner_radius=6)
            tb.pack(side="left", padx=4)
            ctk.CTkLabel(tb, text=f" {tip} ", font=fonte(9, "bold"), text_color=cor_tipo).pack(padx=4, pady=2)

            # Contexto
            ctk.CTkLabel(row, text=ctx, font=fonte(9), text_color=COR_TEXTO_MUTED, width=80, anchor="w").pack(side="left", padx=6)

            # Limite
            ctk.CTkLabel(row, text=lim, font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL, width=95, anchor="w").pack(side="left")

            # Barra de progresso + %
            p_box = ctk.CTkFrame(row, fg_color="transparent", width=110)
            p_box.pack(side="left", padx=4)

            p_bar = ctk.CTkProgressBar(p_box, height=5, corner_radius=2, progress_color=cor_p, fg_color="#1C2F3F", width=65)
            p_bar.set(prog_p)
            p_bar.pack(side="left")

            ctk.CTkLabel(p_box, text=prog_txt, font=fonte(9, "bold"), text_color=cor_p, width=35, anchor="e").pack(side="left")

            # Botão Apagar Categoria
            ctk.CTkButton(
                row,
                text="🗑️",
                width=26,
                height=26,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#3E1A23",
                text_color="#F43F5E",
                font=fonte(10),
                command=lambda id_=cid, n=nom: self._apagar_categoria(id_, n),
            ).pack(side="right", padx=(2, 8))

        ctk.CTkLabel(card_tab, text="", height=8).pack()


    def _apagar_categoria(self, categoria_id: Optional[int], nome: str):
        from tkinter import messagebox
        if messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente apagar a categoria '{nome}'?"):
            if categoria_id is not None:
                try:
                    self.dao.excluir(categoria_id)
                except Exception as exc:
                    print(f"Erro ao excluir categoria: {exc}")
            self._montar_tela()

    def _set_filtro(self, f: str):
        self.filtro_tipo = f
        self._montar_tela()

    # ==============================================================
    # 4. COLUNA DIREITA: NOVA CATEGORIA + SUGESTÕES
    # ==============================================================
    def _build_coluna_formulario(self, parent):
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # 4.1 Card Nova Categoria
        self._build_card_nova_categoria(col)

        # 4.2 Card Categorias Sugeridas
        self._build_card_sugestoes(col)

    def _build_card_nova_categoria(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=14, border_width=1, border_color=COR_BORDA)
        card.pack(fill="x", pady=(0, 12))

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 12))

        ctk.CTkLabel(topo, text="🏷️  Nova Categoria", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")
        ctk.CTkButton(
            topo, text="🔄  Limpar", height=26, corner_radius=6,
            fg_color="transparent", hover_color=COR_CARD_INTERNO, text_color=COR_TEXTO_MUTED, font=fonte(10),
            command=self._limpar_form
        ).pack(side="right")

        # Nome
        ctk.CTkLabel(card, text="Nome da Categoria", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        self.entry_nome = ctk.CTkEntry(
            card, placeholder_text="Ex.: Viagem, Alimentação, Salário...", height=36, corner_radius=8,
            fg_color=COR_CARD_INTERNO, border_width=1, border_color=COR_BORDA, text_color=COR_TEXTO_PRINCIPAL, font=fonte(10)
        )
        self.entry_nome.pack(fill="x", padx=16, pady=(0, 10))

        # Linha: Tipo | Contexto de Uso
        l1 = ctk.CTkFrame(card, fg_color="transparent")
        l1.pack(fill="x", padx=16, pady=(0, 10))
        l1.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(l1, text="Tipo", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.combo_tipo = ctk.CTkOptionMenu(
            l1, values=["Despesa", "Receita"], height=36, corner_radius=8,
            fg_color=COR_CARD_INTERNO, button_color=COR_CARD_INTERNO, text_color=COR_TEXTO_PRINCIPAL, font=fonte(10)
        )
        self.combo_tipo.set("Despesa")
        self.combo_tipo.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(l1, text="Contexto de Uso", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.combo_ctx = ctk.CTkOptionMenu(
            l1, values=["Pessoal", "Empresarial", "Familiar", "Outros"], height=36, corner_radius=8,
            fg_color=COR_CARD_INTERNO, button_color=COR_CARD_INTERNO, text_color=COR_TEXTO_PRINCIPAL, font=fonte(10)
        )
        self.combo_ctx.set("Pessoal")
        self.combo_ctx.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # Limite de Orçamento
        ctk.CTkLabel(card, text="Limite de Orçamento (R$/mês)", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        self.entry_limite = ctk.CTkEntry(
            card, placeholder_text="0,00", height=36, corner_radius=8,
            fg_color=COR_CARD_INTERNO, border_width=1, border_color=COR_BORDA, text_color=COR_TEXTO_PRINCIPAL, font=fonte(10)
        )
        self.entry_limite.pack(fill="x", padx=16, pady=(0, 4))

        ctk.CTkLabel(card, text="Deixe 0 para sem limite de orçamento", font=fonte(8), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 16))

        # Botão Adicionar Categoria Teal
        ctk.CTkButton(
            card,
            text="＋  Adicionar Categoria",
            height=40,
            corner_radius=10,
            fg_color="#00D084",
            hover_color="#00B875",
            text_color="#0B131B",
            font=fonte(11, "bold"),
            command=self._salvar_categoria,
        ).pack(fill="x", padx=16, pady=(0, 16))

    def _build_card_sugestoes(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=14, border_width=1, border_color=COR_BORDA)
        card.pack(fill="x")

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(14, 10))

        ctk.CTkLabel(topo, text="💡  Categorias Sugeridas", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")
        ctk.CTkButton(
            topo, text="＋  Adicionar todas", fg_color="transparent", hover_color=COR_CARD_INTERNO, text_color="#00D084", font=fonte(10)
        ).pack(side="right")

        # Grid 2 colunas com tags interativas
        grid_sug = ctk.CTkFrame(card, fg_color="transparent")
        grid_sug.pack(fill="x", padx=16, pady=(0, 14))
        grid_sug.grid_columnconfigure((0, 1), weight=1)

        sugestoes = [
            ("🍴", "Alimentação"), ("🎮", "Lazer"),
            ("🚗", "Transporte"), ("🏢", "Contas e Serviços"),
            ("❤️", "Saúde"), ("🛍️", "Shopping"),
            ("🎓", "Educação"), ("🔄", "Assinaturas"),
            ("✈️", "Viagem"), ("🎁", "Presentes"),
        ]

        for i, (ic, tit) in enumerate(sugestoes):
            r, c = i // 2, i % 2
            b = ctk.CTkButton(
                grid_sug,
                text=f"{ic}  {tit}  ＋",
                height=32,
                corner_radius=8,
                fg_color=COR_CARD_INTERNO,
                hover_color="#1E3143",
                text_color=COR_TEXTO_PRINCIPAL,
                font=fonte(10),
                command=lambda t=tit: self._adicionar_sugerida(t),
            )
            b.grid(row=r, column=c, padx=3, pady=3, sticky="ew")

    def _limpar_form(self):
        self.entry_nome.delete(0, "end")
        self.entry_limite.delete(0, "end")

    def _salvar_categoria(self):
        nom = self.entry_nome.get().strip()
        if not nom:
            return

        tip = self.combo_tipo.get()
        ctx = self.combo_ctx.get()
        lim_txt = self.entry_limite.get().replace("R$", "").replace(".", "").replace(",", ".").strip() or "0"
        try:
            lim = float(lim_txt)
        except Exception:
            lim = 0.0

        self.dao.inserir(
            nome=nom,
            tipo=tip,
            escopo=ctx,
            limite_orcamento=lim,
        )
        self._limpar_form()
        self._montar_tela()

    def _adicionar_sugerida(self, tit: str):
        self.entry_nome.delete(0, "end")
        self.entry_nome.insert(0, tit)
