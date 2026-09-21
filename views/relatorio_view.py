"""
View do Relatório Mensal Automático.
=====================================

Apresenta resumo executivo do mês com receitas, despesas, taxa de economia,
ranking de categorias mais utilizadas, comparativo com o mês anterior
e principais mudanças financeiras.
"""
from typing import Optional, Dict, Any, List
import customtkinter as ctk

from dao.lancamento_dao import LancamentoDAO
from dao.categoria_dao import CategoriaDAO
from controllers.inteligencia_financeira_controller import InteligenciaFinanceiraController


class RelatorioView(ctk.CTkFrame):
    """Tela executiva do Relatório Mensal Inteligente."""

    def __init__(
        self,
        parent,
        dao: Optional[LancamentoDAO] = None,
        cat_dao: Optional[CategoriaDAO] = None,
    ):
        super().__init__(parent, fg_color="transparent")

        self.dao = dao or LancamentoDAO()
        self.cat_dao = cat_dao or CategoriaDAO()

        self.meses_mapa: List[Dict[str, Any]] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._criar_topo()
        self._criar_area_conteudo()
        self.atualizar_dados()

    # ==============================================================
    # TOPO (SELEÇÃO DO MÊS)
    # ==============================================================
    def _criar_topo(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        topo.grid_columnconfigure(0, weight=1)

        # Informações da tela
        info_frame = ctk.CTkFrame(topo, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            info_frame,
            text="📄  RELATÓRIO MENSAL INTELIGENTE",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#89B4FA",
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text="Resumo detalhado de receitas, despesas e comparação com o histórico.",
            font=ctk.CTkFont(size=12),
            text_color="#A6ADC8",
            anchor="w",
        ).pack(anchor="w")

        # Filtros no canto direito
        acoes_frame = ctk.CTkFrame(topo, fg_color="transparent")
        acoes_frame.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            acoes_frame,
            text="Mês de Referência:",
            font=ctk.CTkFont(size=12),
            text_color="#CDD6F4",
        ).pack(side="left", padx=(0, 8))

        self.combo_mes = ctk.CTkComboBox(
            acoes_frame,
            values=["Mês Atual"],
            command=self._on_selecionar_mes,
            width=180,
            fg_color="#181825",
            border_color="#313244",
            button_color="#313244",
        )
        self.combo_mes.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            acoes_frame,
            text="🔄 Atualizar",
            width=90,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#313244",
            hover_color="#45475A",
            command=self.atualizar_dados,
        ).pack(side="left")

    # ==============================================================
    # ÁREA DE CONTEÚDO COM SCROLL
    # ==============================================================
    def _criar_area_conteudo(self):
        self.scroll_conteudo = ctk.CTkScrollableFrame(
            self,
            corner_radius=15,
            fg_color="transparent",
        )
        self.scroll_conteudo.grid(row=1, column=0, sticky="nsew")
        self.scroll_conteudo.grid_columnconfigure(0, weight=1)

    # ==============================================================
    # ATUALIZAÇÃO DOS DADOS
    # ==============================================================
    def atualizar_dados(self):
        lancamentos = self.dao.listar_todos()
        self.meses_mapa = InteligenciaFinanceiraController.obter_meses_disponiveis(lancamentos)

        rotulos = [m["rotulo"] for m in self.meses_mapa]
        self.combo_mes.configure(values=rotulos)

        # Selecionar o primeiro (mais recente) se ainda não selecionado
        sel_atual = self.combo_mes.get()
        if sel_atual not in rotulos and rotulos:
            self.combo_mes.set(rotulos[0])

        self._gerar_relatorio()

    def _on_selecionar_mes(self, rotulo):
        self._gerar_relatorio()

    def _gerar_relatorio(self):
        rotulo_sel = self.combo_mes.get()
        item_sel = next((m for m in self.meses_mapa if m["rotulo"] == rotulo_sel), None)

        lancamentos = self.dao.listar_todos()
        categorias = self.cat_dao.listar_todas()

        if item_sel:
            ano = item_sel["ano"]
            mes = item_sel["mes"]
        else:
            ano, mes = None, None

        rel = InteligenciaFinanceiraController.gerar_relatorio_mensal(
            lancamentos=lancamentos,
            categorias=categorias,
            ano=ano,
            mes=mes,
        )

        self._renderizar_relatorio(rel)

    # ==============================================================
    # RENDERIZAÇÃO DA TELA
    # ==============================================================
    def _renderizar_relatorio(self, rel: Dict[str, Any]):
        for w in self.scroll_conteudo.winfo_children():
            w.destroy()

        tot = rel["totais"]
        ant = rel["comparativo_anterior"]

        # ---------------- 1. CARDS KPI (4 COLUNAS) ----------------
        frame_kpi = ctk.CTkFrame(self.scroll_conteudo, fg_color="transparent")
        frame_kpi.pack(fill="x", pady=(0, 15))
        frame_kpi.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 1.1 Receitas
        c_rec = ctk.CTkFrame(frame_kpi, corner_radius=12, fg_color="#1E1E2E", border_width=1, border_color="#313244")
        c_rec.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(c_rec, text="📈 RECEITAS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#A6ADC8").pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(c_rec, text=f"R$ {tot['receitas']:,.2f}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#A6E3A1").pack(anchor="w", padx=12, pady=0)
        sinal_rec = "▲ +" if ant["pct_receitas"] >= 0 else "▼ "
        cor_badge_rec = "#A6E3A1" if ant["pct_receitas"] >= 0 else "#F38BA8"
        ctk.CTkLabel(c_rec, text=f"{sinal_rec}{ant['pct_receitas']:.0f}% vs mês anterior", font=ctk.CTkFont(size=11), text_color=cor_badge_rec).pack(anchor="w", padx=12, pady=(2, 10))

        # 1.2 Despesas
        c_desp = ctk.CTkFrame(frame_kpi, corner_radius=12, fg_color="#1E1E2E", border_width=1, border_color="#313244")
        c_desp.grid(row=0, column=1, sticky="ew", padx=3)
        ctk.CTkLabel(c_desp, text="📉 DESPESAS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#A6ADC8").pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(c_desp, text=f"R$ {tot['despesas']:,.2f}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#F38BA8").pack(anchor="w", padx=12, pady=0)
        sinal_desp = "▲ +" if ant["pct_despesas"] >= 0 else "▼ "
        # Se despesa subiu é vermelho, se caiu é verde
        cor_badge_desp = "#F38BA8" if ant["pct_despesas"] > 0 else "#A6E3A1"
        ctk.CTkLabel(c_desp, text=f"{sinal_desp}{ant['pct_despesas']:.0f}% vs mês anterior", font=ctk.CTkFont(size=11), text_color=cor_badge_desp).pack(anchor="w", padx=12, pady=(2, 10))

        # 1.3 Saldo Líquido
        c_saldo = ctk.CTkFrame(frame_kpi, corner_radius=12, fg_color="#1E1E2E", border_width=1, border_color="#313244")
        c_saldo.grid(row=0, column=2, sticky="ew", padx=3)
        ctk.CTkLabel(c_saldo, text="💰 SALDO DO MÊS", font=ctk.CTkFont(size=11, weight="bold"), text_color="#A6ADC8").pack(anchor="w", padx=12, pady=(10, 2))
        cor_saldo = "#A6E3A1" if tot["saldo"] >= 0 else "#F38BA8"
        sinal_s = "+" if tot["saldo"] > 0 else ""
        ctk.CTkLabel(c_saldo, text=f"{sinal_s}R$ {tot['saldo']:,.2f}", font=ctk.CTkFont(size=18, weight="bold"), text_color=cor_saldo).pack(anchor="w", padx=12, pady=0)
        ctk.CTkLabel(c_saldo, text=f"{tot['qtd_total']} transações", font=ctk.CTkFont(size=11), text_color="#A6ADC8").pack(anchor="w", padx=12, pady=(2, 10))

        # 1.4 Taxa de Poupança
        c_poup = ctk.CTkFrame(frame_kpi, corner_radius=12, fg_color="#1E1E2E", border_width=1, border_color="#313244")
        c_poup.grid(row=0, column=3, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(c_poup, text="🌱 TAXA DE ECONOMIA", font=ctk.CTkFont(size=11, weight="bold"), text_color="#A6ADC8").pack(anchor="w", padx=12, pady=(10, 2))
        cor_taxa = "#A6E3A1" if tot["taxa_poupanca"] >= 20 else ("#F9E2AF" if tot["taxa_poupanca"] >= 0 else "#F38BA8")
        ctk.CTkLabel(c_poup, text=f"{tot['taxa_poupanca']:.1f}%", font=ctk.CTkFont(size=18, weight="bold"), text_color=cor_taxa).pack(anchor="w", padx=12, pady=0)
        status_taxa = "Meta > 20% atingida" if tot["taxa_poupanca"] >= 20 else ("Positiva" if tot["taxa_poupanca"] >= 0 else "Déficit")
        ctk.CTkLabel(c_poup, text=status_taxa, font=ctk.CTkFont(size=11), text_color="#CDD6F4").pack(anchor="w", padx=12, pady=(2, 10))

        # ---------------- 2. DIAGNÓSTICO EXECUTIVO ----------------
        card_diag = ctk.CTkFrame(
            self.scroll_conteudo,
            corner_radius=12,
            fg_color="#181825",
            border_width=1,
            border_color="#313244",
        )
        card_diag.pack(fill="x", pady=(0, 15))

        top_diag = ctk.CTkFrame(card_diag, fg_color="transparent")
        top_diag.pack(fill="x", padx=15, pady=(12, 4))
        top_diag.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            top_diag,
            text=f"📋  DIAGNÓSTICO EXECUTIVO • {rel['nome_mes']}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#89B4FA",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            top_diag,
            text=f"Status: {rel['status_geral']}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#A6E3A1" if "Excelente" in rel['status_geral'] or "Equilibrado" in rel['status_geral'] else "#F38BA8",
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            card_diag,
            text=rel["parecer_executivo"],
            font=ctk.CTkFont(size=13),
            text_color="#CDD6F4",
            wraplength=800,
            justify="left",
        ).pack(anchor="w", padx=15, pady=(0, 12))

        # ---------------- 3. GRID DE 2 COLUNAS: RANKING E MUDANÇAS ----------------
        duo = ctk.CTkFrame(self.scroll_conteudo, fg_color="transparent")
        duo.pack(fill="x", pady=(0, 15))
        duo.grid_columnconfigure(0, weight=6)
        duo.grid_columnconfigure(1, weight=5)

        # 3.1 RANKING DE CATEGORIAS
        col_rank = ctk.CTkFrame(duo, corner_radius=12, fg_color="#1E1E2E", border_width=1, border_color="#313244")
        col_rank.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(
            col_rank,
            text="🏷️  CATEGORIAS MAIS UTILIZADAS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        ).pack(anchor="w", padx=15, pady=(15, 10))

        ranking = rel["ranking_categorias"]
        if not ranking:
            ctk.CTkLabel(
                col_rank,
                text="Nenhuma despesa registrada neste mês.",
                font=ctk.CTkFont(size=12),
                text_color="#A6ADC8",
            ).pack(padx=15, pady=20)
        else:
            for item in ranking[:6]:
                linha = ctk.CTkFrame(col_rank, fg_color="#181825", corner_radius=8)
                linha.pack(fill="x", padx=15, pady=4)

                top_l = ctk.CTkFrame(linha, fg_color="transparent")
                top_l.pack(fill="x", padx=10, pady=(6, 2))
                top_l.grid_columnconfigure(1, weight=1)

                ctk.CTkLabel(
                    top_l,
                    text=item["categoria"],
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#CDD6F4",
                ).grid(row=0, column=0, sticky="w")

                ctk.CTkLabel(
                    top_l,
                    text=f"R$ {item['valor']:,.2f} ({item['percentual_total']:.1f}%)",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#F38BA8",
                ).grid(row=0, column=1, sticky="e")

                # Barra de proporção
                prog = ctk.CTkProgressBar(
                    linha,
                    height=6,
                    corner_radius=3,
                    fg_color="#313244",
                    progress_color="#F38BA8",
                )
                prog.set(max(0.01, item["percentual_total"] / 100.0))
                prog.pack(fill="x", padx=10, pady=(0, 6))

            ctk.CTkLabel(col_rank, text="", height=4).pack()

        # 3.2 PRINCIPAIS MUDANÇAS & DESTAQUES
        col_mudancas = ctk.CTkFrame(duo, corner_radius=12, fg_color="#1E1E2E", border_width=1, border_color="#313244")
        col_mudancas.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(
            col_mudancas,
            text="⚡  DESTAQUES & MUDANÇAS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Tabela Comparativa Lado a Lado
        tab_comp = ctk.CTkFrame(col_mudancas, fg_color="#181825", corner_radius=8)
        tab_comp.pack(fill="x", padx=15, pady=(0, 10))

        linhas_comp = [
            ("Receitas", tot["receitas"], ant["receitas_anterior"], "#A6E3A1"),
            ("Despesas", tot["despesas"], ant["despesas_anterior"], "#F38BA8"),
            ("Saldo", tot["saldo"], ant["saldo_anterior"], cor_saldo),
        ]

        header_tab = ctk.CTkFrame(tab_comp, fg_color="transparent")
        header_tab.pack(fill="x", padx=10, pady=(6, 2))
        header_tab.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(header_tab, text="Métrica", font=ctk.CTkFont(size=11, weight="bold"), text_color="#A6ADC8").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header_tab, text=rel["nome_mes"][:3], font=ctk.CTkFont(size=11, weight="bold"), text_color="#89B4FA").grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(header_tab, text=rel["nome_mes_anterior"][:3], font=ctk.CTkFont(size=11, weight="bold"), text_color="#A6ADC8").grid(row=0, column=2, sticky="e")

        for nome, val_atual, val_ant, cor in linhas_comp:
            l_item = ctk.CTkFrame(tab_comp, fg_color="transparent")
            l_item.pack(fill="x", padx=10, pady=2)
            l_item.grid_columnconfigure((0, 1, 2), weight=1)

            ctk.CTkLabel(l_item, text=nome, font=ctk.CTkFont(size=11), text_color="#CDD6F4").grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(l_item, text=f"R${val_atual:,.0f}", font=ctk.CTkFont(size=11, weight="bold"), text_color=cor).grid(row=0, column=1, sticky="e")
            ctk.CTkLabel(l_item, text=f"R${val_ant:,.0f}", font=ctk.CTkFont(size=11), text_color="#A6ADC8").grid(row=0, column=2, sticky="e")

        ctk.CTkLabel(tab_comp, text="", height=4).pack()

        # Destaques detectados
        mudancas = rel["principais_mudancas"]
        if mudancas:
            for m in mudancas:
                c_m = ctk.CTkFrame(col_mudancas, fg_color="#181825", corner_radius=8)
                c_m.pack(fill="x", padx=15, pady=4)

                top_m = ctk.CTkFrame(c_m, fg_color="transparent")
                top_m.pack(fill="x", padx=10, pady=(6, 2))

                ctk.CTkLabel(
                    top_m,
                    text=f"{m['icone']}  {m['titulo']}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=m["cor"],
                ).pack(anchor="w")

                ctk.CTkLabel(
                    c_m,
                    text=m["descricao"],
                    font=ctk.CTkFont(size=11),
                    text_color="#CDD6F4",
                    wraplength=350,
                    justify="left",
                ).pack(anchor="w", padx=10, pady=(0, 6))
        else:
            ctk.CTkLabel(
                col_mudancas,
                text="Sem dados suficientes do mês anterior para comparação de desvios.",
                font=ctk.CTkFont(size=11),
                text_color="#A6ADC8",
                wraplength=340,
                justify="left",
            ).pack(padx=15, pady=10)
