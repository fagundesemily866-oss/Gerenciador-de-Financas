"""
View de Terceiros — Redesign Fiel à Referência (07_terceiros.png)
================================================================

Gerenciador de contatos, fornecedores, clientes e familiares:
1. Topo: Título com ícone, subtítulo e barra de busca global.
2. Métricas: 4 Cards (Total de contatos, Fornecedores, Clientes, Familiares) com barras percentuais.
3. Coluna Esquerda: Filtros em abas, busca com ordenação, tabela rica com avatares/logos,
   badges de categoria, status de atividade e paginação.
4. Coluna Direita: Painel 'Novo contato' com abas Dados Principais / Observações,
   seletor de foto/avatar, botões em pílula de vínculo [Fornecedor / Cliente / Familiar],
   campos estruturados e botões Limpar / Salvar contato.
"""
import tkinter as tk
from datetime import datetime, date
from typing import Optional, Dict, Any, List
import customtkinter as ctk

from dao.terceiro_dao import TerceiroDAO
from models.terceiro import Terceiro
from views.notificacao_toast import GerenciadorNotificacoes
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_ACENTO_ROXO, COR_SUCESSO, COR_ALERTA, COR_INFO,
    fonte, fonte_titulo, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
)


class TerceiroView(ctk.CTkFrame):
    """Tela de Terceiros redesenhada fiel à imagem 07_terceiros.png."""

    def __init__(self, parent, dao: Optional[TerceiroDAO] = None):
        super().__init__(parent, fg_color="transparent")
        self.dao = dao or TerceiroDAO()

        self.filtro_tipo = "Todos"
        self.tipo_vinculo = "Fornecedor"
        self.aba_form = "Dados principais"

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

        # 3. CORPO: TABELA (ESQ) + NOVO CONTATO (DIR)
        corpo = ctk.CTkFrame(scroll, fg_color="transparent")
        corpo.pack(fill="both", expand=True, pady=(0, 10))
        corpo.grid_columnconfigure(0, weight=6)
        corpo.grid_columnconfigure(1, weight=4)

        self._build_tabela_terceiros(corpo)
        self._build_painel_novo_contato(corpo)

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

        ic_b = ctk.CTkFrame(tit_row, width=32, height=32, corner_radius=8, fg_color="#122538")
        ic_b.pack(side="left", padx=(0, 10))
        ic_b.pack_propagate(False)
        ctk.CTkLabel(ic_b, text="👥", font=fonte(14)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(tit_row, text="Terceiros", font=fonte(22, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        ctk.CTkLabel(
            tit_box,
            text="Gerencie seus fornecedores, clientes e familiares em um só lugar.",
            font=fonte(12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Ações topo direito
        acoes = ctk.CTkFrame(header, fg_color="transparent")
        acoes.grid(row=0, column=1, sticky="e")

        busca = ctk.CTkFrame(acoes, fg_color=COR_CARD, corner_radius=8, border_width=1, border_color=COR_BORDA, height=34)
        busca.pack(side="left", padx=(0, 8))
        busca.pack_propagate(False)

        ctk.CTkLabel(busca, text="🔍", font=fonte(10)).pack(side="left", padx=8)
        ctk.CTkEntry(busca, placeholder_text="Buscar no app...", width=140, fg_color="transparent", border_width=0, font=fonte(10)).pack(side="left")

        ctk.CTkButton(acoes, text="?", width=34, height=34, corner_radius=8, fg_color=COR_CARD, hover_color=COR_CARD_INTERNO, text_color=COR_TEXTO_MUTED).pack(side="left", padx=(0, 6))
        ctk.CTkButton(acoes, text="🔔", width=34, height=34, corner_radius=8, fg_color=COR_CARD, hover_color=COR_CARD_INTERNO, text_color=COR_TEXTO_MUTED).pack(side="left")

    # ==============================================================
    # 2. MÉTRICAS (4 CARDS)
    # ==============================================================
    def _build_metricas(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 14))
        for c in range(4):
            grid.grid_columnconfigure(c, weight=1)

        cards = [
            ("👥", "#122538", "#38BDF8", "Total de contatos", "12", "▲ +2 este mês", None),
            ("🚚", "#1C142E", "#A855F7", "Fornecedores", "5", "41,7% do total", 0.417),
            ("👤", "#0D2E2B", "#00D084", "Clientes", "4", "33,3% do total", 0.333),
            ("👨‍👩‍👧", "#291E10", "#F59E0B", "Familiares", "3", "25,0% do total", 0.25),
        ]

        # Ajustar com banco se houver
        reais = self.dao.listar_todos()
        if reais:
            cards[0] = ("👥", "#122538", "#38BDF8", "Total de contatos", str(len(reais)), "Cadastrados no banco", None)

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

            ctk.CTkLabel(card, text=sub, font=fonte(9), text_color=cor_ic if "▲" in sub else COR_TEXTO_MUTED, anchor="w").pack(anchor="w", padx=14, pady=(0, 4))

            if prog_val is not None:
                p = ctk.CTkProgressBar(card, height=4, corner_radius=2, progress_color=cor_ic, fg_color="#1C2F3F")
                p.set(prog_val)
                p.pack(fill="x", padx=14, pady=(0, 10))
            else:
                ctk.CTkLabel(card, text="", height=4).pack()

    # ==============================================================
    # 3. COLUNA ESQUERDA: TABELA DE TERCEIROS
    # ==============================================================
    def _build_tabela_terceiros(self, parent):
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Barra de Abas / Filtros em Pílula
        bar_f = ctk.CTkFrame(col, fg_color="transparent")
        bar_f.pack(fill="x", pady=(0, 8))

        abas = ctk.CTkFrame(bar_f, fg_color=COR_CARD_INTERNO, corner_radius=8, height=32)
        abas.pack(side="left")

        filtros = [("👥 Todos (12)", "Todos"), ("🚚 Fornecedores (5)", "Fornecedor"), ("👤 Clientes (4)", "Cliente"), ("👨‍👩‍👧 Familiares (3)", "Familiar")]
        for rotulo, val in filtros:
            ativo = (val == self.filtro_tipo)
            ctk.CTkButton(
                abas,
                text=rotulo,
                height=26,
                corner_radius=6,
                fg_color="#1E3143" if ativo else "transparent",
                text_color="#FFFFFF" if ativo else COR_TEXTO_SECUNDARIO,
                font=fonte(10, "bold" if ativo else "normal"),
                command=lambda v=val: self._set_filtro(v),
            ).pack(side="left", padx=2, pady=3)

        # Barra de Busca, Ordenação e Filtro
        f_pesq = ctk.CTkFrame(col, fg_color="transparent")
        f_pesq.pack(fill="x", pady=(0, 10))
        f_pesq.grid_columnconfigure(0, weight=1)

        b_box = ctk.CTkFrame(f_pesq, fg_color=COR_CARD, corner_radius=8, border_width=1, border_color=COR_BORDA, height=34)
        b_box.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        b_box.pack_propagate(False)

        ctk.CTkLabel(b_box, text="🔍", font=fonte(10)).pack(side="left", padx=8)
        self.entry_pesquisa = ctk.CTkEntry(
            b_box, placeholder_text="Buscar por nome, razão social ou observações...", fg_color="transparent", border_width=0, font=fonte(10)
        )
        self.entry_pesquisa.pack(side="left", fill="both", expand=True)

        # Ordenar
        ord_box = ctk.CTkFrame(f_pesq, fg_color="transparent")
        ord_box.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(ord_box, text="Ordenar por", font=fonte(10), text_color=COR_TEXTO_MUTED).pack(side="left", padx=(0, 6))
        opt_ord = ctk.CTkOptionMenu(
            ord_box,
            values=["Nome (A - Z)", "Nome (Z - A)", "Última atividade", "Mais recentes"],
            width=120,
            height=32,
            fg_color=COR_CARD,
            button_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(10),
        )
        opt_ord.set("Nome (A - Z)")
        opt_ord.pack(side="left", padx=(0, 6))

        ctk.CTkButton(ord_box, text="🌪", width=34, height=32, corner_radius=8, fg_color=COR_CARD, hover_color=COR_CARD_INTERNO, text_color=COR_TEXTO_MUTED).pack(side="left")

        # Card da Tabela
        card_tab = ctk.CTkFrame(col, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card_tab.pack(fill="x")

        # Cabeçalho da Tabela
        th = ctk.CTkFrame(card_tab, fg_color="transparent")
        th.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(th, text="Nome / Razão Social", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=150, anchor="w").pack(side="left")
        ctk.CTkLabel(th, text="Tipo ↕", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=80, anchor="w").pack(side="left", padx=8)
        ctk.CTkLabel(th, text="Telefone", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=100, anchor="w").pack(side="left")
        ctk.CTkLabel(th, text="E-mail", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=140, anchor="w").pack(side="left", padx=8)
        ctk.CTkLabel(th, text="Última atividade", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=100, anchor="w").pack(side="left")
        ctk.CTkLabel(th, text="Ações", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, anchor="e").pack(side="right", padx=(0, 8))

        # Lista de Contatos da Referência
        contatos = [
            ("🛒", "#2E151B", "Atacadão BH", "Atacado e Distribuição Ltda", "Fornecedor", "#A855F7", "#1C142E", "(31) 3300-1000", "vendas@atacadobh.com.br", "● 22/09/2025", "#00D084"),
            ("a", "#291E10", "Amazon Brasil", "Amazon Serviços de Varejo", "Fornecedor", "#A855F7", "#1C142E", "0800 038 0541", "contato@amazon.com.br", "● 18/09/2025", "#F59E0B"),
            ("FS", "#122538", "Carlos Silva", "Freelancer - Design", "Cliente", "#00D084", "#0D2E2B", "(31) 98811-2233", "carlos.silva@email.com", "● 25/09/2025", "#00D084"),
            ("MS", "#2A1F18", "Casa do Marceneiro", "Móveis e Planejados", "Fornecedor", "#A855F7", "#1C142E", "(31) 3333-7788", "contato@casadomarceneiro.com.br", "● 10/09/2025", "#F43F5E"),
            ("FO", "#1C142E", "Fernanda Oliveira", "Consultoria Financeira", "Cliente", "#00D084", "#0D2E2B", "(31) 98999-1122", "fernanda@oliveira.com", "● 21/09/2025", "#00D084"),
            ("JS", "#0D2E2B", "João Silva", "Pai", "Familiar", "#F59E0B", "#291E10", "(31) 98765-4321", "joao.silva@email.com", "● 15/09/2025", "#F59E0B"),
            ("it", "#291E10", "Itaú Unibanco", "Banco", "Fornecedor", "#A855F7", "#1C142E", "4004 4828", "relacionamento@itau.com.br", "● 20/09/2025", "#00D084"),
            ("LM", "#2E1528", "Laura Mendes", "Cliente - Consultoria", "Cliente", "#00D084", "#0D2E2B", "(31) 99666-8877", "laura.mendes@email.com", "● 19/09/2025", "#00D084"),
            ("BR", "#0D2E2B", "Petrobras", "Posto de Combustível", "Fornecedor", "#A855F7", "#1C142E", "0800 728 9001", "faleconosco@petrobras.com.br", "● 12/09/2025", "#F43F5E"),
            ("MO", "#291E10", "Maria Oliveira", "Mãe", "Familiar", "#F59E0B", "#291E10", "(31) 98888-7766", "maria.oliveira@email.com", "● 05/09/2025", "#F43F5E"),
        ]

        # Contatos reais do banco se existirem
        reais = self.dao.listar_todos()
        if reais:
            reais_c = []
            for t in reais:
                rel = getattr(t, "relacao", "Fornecedor")
                cor_v = "#A855F7" if rel == "Fornecedor" else ("#00D084" if rel == "Cliente" else "#F59E0B")
                bg_v = "#1C142E" if rel == "Fornecedor" else ("#0D2E2B" if rel == "Cliente" else "#291E10")
                reais_c.append((
                    "👤", "#182A3A", getattr(t, "nome", "Contato"), "Contato Cadastrado",
                    rel, cor_v, bg_v, "(31) 0000-0000", "contato@email.com", "● Ativo", "#00D084"
                ))
            if reais_c:
                contatos = reais_c

        # Filtrar se aplicável
        if self.filtro_tipo != "Todos":
            contatos = [c for c in contatos if c[4] == self.filtro_tipo]

        for av_txt, bg_av, nom, sub, tipo_b, cor_t, bg_t, tel, em, ult_atv, cor_atv in contatos:
            row = ctk.CTkFrame(card_tab, fg_color=COR_CARD_INTERNO, corner_radius=8, height=48)
            row.pack(fill="x", padx=14, pady=2)
            row.pack_propagate(False)

            # Avatar
            av_box = ctk.CTkFrame(row, width=30, height=30, corner_radius=15, fg_color=bg_av)
            av_box.pack(side="left", padx=(8, 8))
            av_box.pack_propagate(False)
            ctk.CTkLabel(av_box, text=av_txt, font=fonte(10, "bold"), text_color="#FFFFFF").place(relx=0.5, rely=0.5, anchor="center")

            # Nome
            n_box = ctk.CTkFrame(row, fg_color="transparent", width=140)
            n_box.pack(side="left", fill="y", padx=(0, 6))
            n_box.pack_propagate(False)
            ctk.CTkLabel(n_box, text=nom[:16], font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w", pady=(6, 0))
            ctk.CTkLabel(n_box, text=sub[:18], font=fonte(8), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

            # Badge Tipo
            tb = ctk.CTkFrame(row, fg_color=bg_t, corner_radius=6)
            tb.pack(side="left", padx=6)
            ctk.CTkLabel(tb, text=f" {tipo_b} ", font=fonte(9, "bold"), text_color=cor_t).pack(padx=4, pady=2)

            # Telefone
            ctk.CTkLabel(row, text=tel, font=fonte(9), text_color=COR_TEXTO_SECUNDARIO, width=100, anchor="w").pack(side="left", padx=6)

            # E-mail
            ctk.CTkLabel(row, text=em[:20], font=fonte(9), text_color=COR_TEXTO_MUTED, width=140, anchor="w").pack(side="left", padx=6)

            # Última atividade
            ctk.CTkLabel(row, text=ult_atv, font=fonte(9), text_color=cor_atv, width=90, anchor="w").pack(side="left")

            # Botões de Ação
            ctk.CTkButton(row, text="···", width=26, height=26, corner_radius=6, fg_color="transparent", hover_color="#1E3143", text_color=COR_TEXTO_MUTED).pack(side="right", padx=(2, 6))
            ctk.CTkButton(row, text="✏", width=26, height=26, corner_radius=6, fg_color="transparent", hover_color="#1E3143", text_color=COR_TEXTO_MUTED).pack(side="right")

        # Rodapé e Paginação
        rodape_tab = ctk.CTkFrame(card_tab, fg_color="transparent")
        rodape_tab.pack(fill="x", padx=14, pady=10)

        ctk.CTkLabel(rodape_tab, text=f"Mostrando 1 a {len(contatos)} de {len(contatos)} contatos", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(side="left")

        pag = ctk.CTkFrame(rodape_tab, fg_color="transparent")
        pag.pack(side="right")

        ctk.CTkButton(pag, text="‹", width=24, height=24, corner_radius=4, fg_color=COR_CARD_INTERNO, text_color=COR_TEXTO_MUTED).pack(side="left", padx=2)
        ctk.CTkButton(pag, text="1", width=24, height=24, corner_radius=4, fg_color="#38BDF8", text_color="#0B131B", font=fonte(9, "bold")).pack(side="left", padx=2)
        ctk.CTkButton(pag, text="2", width=24, height=24, corner_radius=4, fg_color=COR_CARD_INTERNO, text_color=COR_TEXTO_MUTED).pack(side="left", padx=2)
        ctk.CTkButton(pag, text="›", width=24, height=24, corner_radius=4, fg_color=COR_CARD_INTERNO, text_color=COR_TEXTO_MUTED).pack(side="left", padx=2)

    def _set_filtro(self, f: str):
        self.filtro_tipo = f
        self._montar_tela()

    # ==============================================================
    # 4. COLUNA DIREITA: NOVO CONTATO
    # ==============================================================
    def _build_painel_novo_contato(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=14, border_width=1, border_color=COR_BORDA)
        card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Topo
        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(topo, text="👤  Novo contato", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")
        ctk.CTkButton(topo, text="✕", width=24, height=24, corner_radius=12, fg_color="transparent", text_color=COR_TEXTO_MUTED).pack(side="right")

        # Abas [ Dados principais ] [ Observações ]
        abas = ctk.CTkFrame(card, fg_color="transparent")
        abas.pack(fill="x", padx=16, pady=(0, 12))

        b_d = ctk.CTkButton(
            abas, text="Dados principais", height=28, corner_radius=6,
            fg_color="#1E2B38" if self.aba_form == "Dados principais" else "transparent",
            text_color="#38BDF8" if self.aba_form == "Dados principais" else COR_TEXTO_MUTED,
            font=fonte(10, "bold"),
            command=lambda: self._set_aba_form("Dados principais")
        )
        b_d.pack(side="left", padx=(0, 8))

        b_o = ctk.CTkButton(
            abas, text="Observações", height=28, corner_radius=6,
            fg_color="#1E2B38" if self.aba_form == "Observações" else "transparent",
            text_color="#38BDF8" if self.aba_form == "Observações" else COR_TEXTO_MUTED,
            font=fonte(10, "bold"),
            command=lambda: self._set_aba_form("Observações")
        )
        b_o.pack(side="left")

        # Círculo Foto do Contato
        foto_f = ctk.CTkFrame(card, fg_color="transparent")
        foto_f.pack(fill="x", padx=16, pady=(0, 10))

        circulo = ctk.CTkFrame(foto_f, width=54, height=54, corner_radius=27, fg_color="#182A3A")
        circulo.pack(anchor="center")
        circulo.pack_propagate(False)
        ctk.CTkLabel(circulo, text="📷", font=fonte(16)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(foto_f, text="Adicionar foto", font=fonte(9), text_color="#38BDF8").pack(anchor="center", pady=(4, 0))

        # Campo Nome ou Razão Social
        ctk.CTkLabel(card, text="Nome ou Razão Social *", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        self.entry_nome = ctk.CTkEntry(
            card, placeholder_text="Ex.: Supermercado BH, João Silva...", height=36, corner_radius=8,
            fg_color=COR_CARD_INTERNO, border_width=1, border_color=COR_BORDA, text_color=COR_TEXTO_PRINCIPAL, font=fonte(10)
        )
        self.entry_nome.pack(fill="x", padx=16, pady=(0, 10))

        # Tipo de vínculo * (3 seletores)
        ctk.CTkLabel(card, text="Tipo de vínculo *", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        vinc_box = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, height=36)
        vinc_box.pack(fill="x", padx=16, pady=(0, 10))

        for v_nome, ic in [("Fornecedor", "🚚"), ("Cliente", "👤"), ("Familiar", "👨‍👩‍👧")]:
            ativo = (v_nome == self.tipo_vinculo)
            ctk.CTkButton(
                vinc_box,
                text=f"{ic} {v_nome}",
                height=28,
                corner_radius=6,
                fg_color="#3B2562" if (ativo and v_nome == "Fornecedor") else ("#0D2E2B" if (ativo and v_nome == "Cliente") else ("#291E10" if ativo else "transparent")),
                text_color="#FFFFFF" if ativo else COR_TEXTO_MUTED,
                font=fonte(9, "bold" if ativo else "normal"),
                command=lambda v=v_nome: self._set_vinculo(v),
            ).pack(side="left", fill="both", expand=True, padx=2, pady=3)

        # Telefone
        ctk.CTkLabel(card, text="Telefone", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_tel = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        f_tel.pack(fill="x", padx=16, pady=(0, 10))
        f_tel.pack_propagate(False)
        ctk.CTkLabel(f_tel, text="📞", font=fonte(11)).pack(side="left", padx=8)
        self.entry_tel = ctk.CTkEntry(f_tel, placeholder_text="(31) 00000-0000", fg_color="transparent", border_width=0, font=fonte(10))
        self.entry_tel.pack(side="left", fill="both", expand=True)

        # E-mail
        ctk.CTkLabel(card, text="E-mail", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_em = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        f_em.pack(fill="x", padx=16, pady=(0, 10))
        f_em.pack_propagate(False)
        ctk.CTkLabel(f_em, text="✉️", font=fonte(11)).pack(side="left", padx=8)
        self.entry_email = ctk.CTkEntry(f_em, placeholder_text="exemplo@email.com", fg_color="transparent", border_width=0, font=fonte(10))
        self.entry_email.pack(side="left", fill="both", expand=True)

        # Endereço
        ctk.CTkLabel(card, text="Endereço", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_end = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        f_end.pack(fill="x", padx=16, pady=(0, 10))
        f_end.pack_propagate(False)
        ctk.CTkLabel(f_end, text="📍", font=fonte(11)).pack(side="left", padx=8)
        self.entry_end = ctk.CTkEntry(f_end, placeholder_text="Ex.: Rua das Flores, 123 - Belo Horizonte/MG", fg_color="transparent", border_width=0, font=fonte(10))
        self.entry_end.pack(side="left", fill="both", expand=True)

        # Observações
        ctk.CTkLabel(card, text="Observações", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_obs = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=48)
        f_obs.pack(fill="x", padx=16, pady=(0, 14))
        f_obs.pack_propagate(False)
        ctk.CTkLabel(f_obs, text="📄", font=fonte(11)).pack(side="left", padx=8, anchor="n", pady=6)
        self.entry_obs = ctk.CTkEntry(f_obs, placeholder_text="Informações adicionais sobre este contato...", fg_color="transparent", border_width=0, font=fonte(10))
        self.entry_obs.pack(side="left", fill="both", expand=True)

        # Botões Limpar e Salvar
        b_box = ctk.CTkFrame(card, fg_color="transparent")
        b_box.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(
            b_box, text="🗑  Limpar", height=38, width=90, corner_radius=8,
            fg_color=COR_CARD_INTERNO, hover_color="#1E2F40", text_color=COR_TEXTO_SECUNDARIO, font=fonte(10),
            command=self._limpar_form,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            b_box, text="💾  Salvar contato", height=38, corner_radius=8,
            fg_color="#A855F7", hover_color="#9333EA", text_color="#FFFFFF", font=fonte(11, "bold"),
            command=self._salvar_contato,
        ).pack(side="left", fill="x", expand=True)

    def _set_aba_form(self, a: str):
        self.aba_form = a
        self._montar_tela()

    def _set_vinculo(self, v: str):
        self.tipo_vinculo = v
        self._montar_tela()

    def _limpar_form(self):
        self.entry_nome.delete(0, "end")
        self.entry_tel.delete(0, "end")
        self.entry_email.delete(0, "end")
        self.entry_end.delete(0, "end")
        self.entry_obs.delete(0, "end")

    def _salvar_contato(self):
        nom = self.entry_nome.get().strip()
        if not nom:
            return

        novo = Terceiro(
            nome=nom,
            relacao=self.tipo_vinculo,
            data_criacao=date.today().strftime("%Y-%m-%d"),
        )
        self.dao.inserir(novo)
        self._limpar_form()
        self._montar_tela()
