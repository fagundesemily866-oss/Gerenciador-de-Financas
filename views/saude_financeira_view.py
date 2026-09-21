"""
View de Saúde Financeira & Dashboard Inteligente.
=================================================

Centraliza os principais indicadores analíticos da conta:
- Score de Saúde Financeira (0-1000)
- Previsão de gastos até o fim do mês (run-rate diário e limite de orçamento)
- Insights automáticos & Detecção de gastos fora do padrão
- Alertas de vazamento de orçamento e plano de ação direcionado
- Resumo executivo do período
"""
from typing import Optional, Dict, Any
import customtkinter as ctk

from dao.lancamento_dao import LancamentoDAO
from dao.categoria_dao import CategoriaDAO
from dao.meta_dao import MetaDAO
from controllers.saude_financeira_controller import SaudeFinanceiraController
from controllers.inteligencia_financeira_controller import InteligenciaFinanceiraController


class SaudeFinanceiraView(ctk.CTkFrame):
    """Tela do Dashboard Inteligente e Saúde Financeira."""

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

        self.resultado_saude = None
        self.resultado_previsao = None
        self.lista_insights = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.conteudo = None
        self.atualizar_dados()

    # ==============================================================
    # CARREGAMENTO / ATUALIZAÇÃO
    # ==============================================================
    def atualizar_dados(self):
        """Recarrega lançamentos, calcula scores, previsões e insights."""
        lancamentos = self.dao.listar_todos()
        categorias = self.cat_dao.listar_todas()
        metas = self.meta_dao.listar_todas()

        if lancamentos:
            self.resultado_saude = SaudeFinanceiraController.calcular_saude(lancamentos)
            self.resultado_previsao = InteligenciaFinanceiraController.calcular_previsao_mes(
                lancamentos, categorias
            )
            self.lista_insights = InteligenciaFinanceiraController.gerar_insights_dashboard(
                lancamentos, categorias, metas
            )
        else:
            self.resultado_saude = None
            self.resultado_previsao = None
            self.lista_insights = []

        self._montar_interface()

    # ==============================================================
    # MONTAR INTERFACE
    # ==============================================================
    def _montar_interface(self):
        if self.conteudo is not None:
            self.conteudo.destroy()
            self.conteudo = None

        if self.resultado_saude is None:
            self._montar_estado_vazio()
        else:
            self._montar_estado_com_dados()

    # ==============================================================
    # ESTADO SEM DADOS
    # ==============================================================
    def _montar_estado_vazio(self):
        self.conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.conteudo.grid(row=0, column=0, sticky="nsew")
        self.conteudo.grid_columnconfigure(0, weight=1)
        self.conteudo.grid_rowconfigure(0, weight=1)

        frame = ctk.CTkFrame(
            self.conteudo,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(frame, text="🧾", font=ctk.CTkFont(size=54)).pack(pady=(70, 10))

        ctk.CTkLabel(
            frame,
            text="Você ainda não lançou nenhum dado financeiro",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#CDD6F4",
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            frame,
            text=(
                "Cadastre suas receitas e despesas na aba 'Lançamentos' para liberar:\n"
                "• Previsão de gastos até o fim do mês e limites\n"
                "• Detecção automática de gastos fora do padrão\n"
                "• Insights inteligentes no Dashboard e score de saúde."
            ),
            font=ctk.CTkFont(size=13),
            text_color="#A6ADC8",
            justify="center",
        ).pack(pady=(0, 60))

    # ==============================================================
    # ESTADO COM DADOS (SCROLLABLE DASHBOARD)
    # ==============================================================
    def _montar_estado_com_dados(self):
        self.conteudo = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )
        self.conteudo.grid(row=0, column=0, sticky="nsew")
        self.conteudo.grid_columnconfigure(0, weight=1)

        # 1. LINHA TOPO: SCORE HERO (ESQUERDA) + PREVISÃO FIM DO MÊS (DIREITA)
        linha_topo = ctk.CTkFrame(self.conteudo, fg_color="transparent")
        linha_topo.pack(fill="x", pady=(0, 15))
        linha_topo.grid_columnconfigure((0, 1), weight=1)

        self._build_hero_score(linha_topo)
        self._build_card_previsao(linha_topo)

        # 2. SEÇÃO CENTRAL: INSIGHTS INTELIGENTES & ANOMALIAS
        self._build_secao_insights()

        # 3. LINHA INFERIOR: VAZAMENTO/PLANO (ESQUERDA) + RESUMO (DIREITA)
        linha_inferior = ctk.CTkFrame(self.conteudo, fg_color="transparent")
        linha_inferior.pack(fill="x", pady=(0, 15))
        linha_inferior.grid_columnconfigure((0, 1), weight=1)

        self._build_alerta_vazamento_e_plano(linha_inferior)
        self._build_resumo(linha_inferior)

    # ==============================================================
    # 1. SCORE HERO
    # ==============================================================
    def _build_hero_score(self, parent):
        frame_score = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        frame_score.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        ctk.CTkLabel(
            frame_score,
            text="📊  SAÚDE FINANCEIRA",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        ).pack(anchor="w", padx=20, pady=(15, 2))

        score = self.resultado_saude["score"]
        cor_score = self._cor_por_score(score)

        score_val = ctk.CTkLabel(
            frame_score,
            text=str(score),
            font=ctk.CTkFont(size=50, weight="bold"),
            text_color=cor_score,
        )
        score_val.pack(anchor="w", padx=20, pady=(0, 2))

        progresso = ctk.CTkProgressBar(
            frame_score,
            height=10,
            corner_radius=5,
            progress_color=cor_score,
            fg_color="#313244",
        )
        progresso.set(score / 1000)
        progresso.pack(fill="x", padx=20, pady=(2, 8))

        ctk.CTkLabel(
            frame_score,
            text=f"• {self.resultado_saude['status_texto']} (Escala 0-1000)",
            font=ctk.CTkFont(size=12),
            text_color="#BAC2DE",
        ).pack(anchor="w", padx=20, pady=(0, 15))

    # ==============================================================
    # 2. CARD DE PREVISÃO DE GASTOS ATÉ O FIM DO MÊS (FUNCIONALIDADE 1)
    # ==============================================================
    def _build_card_previsao(self, parent):
        prev = self.resultado_previsao
        frame_prev = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        frame_prev.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)

        header_prev = ctk.CTkFrame(frame_prev, fg_color="transparent")
        header_prev.pack(fill="x", padx=20, pady=(15, 2))
        header_prev.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_prev,
            text=f"🔮  PREVISÃO DE GASTOS • {prev['nome_mes']}".upper(),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#89B4FA",
        ).grid(row=0, column=0, sticky="w")

        # Badge de Status
        if prev["status"] == "estouro_previsto":
            badge_txt, badge_cor = "⚠️ Risco de Estouro", "#F38BA8"
        elif prev["status"] == "alerta_limite":
            badge_txt, badge_cor = "⚡ Alerta Limite", "#F9E2AF"
        elif prev["status"] == "dentro_do_limite":
            badge_txt, badge_cor = "✓ Dentro da Meta", "#A6E3A1"
        else:
            badge_txt, badge_cor = "Projeção Mês", "#89B4FA"

        ctk.CTkLabel(
            header_prev,
            text=badge_txt,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=badge_cor,
        ).grid(row=0, column=1, sticky="e")

        # Valor da Projeção
        ctk.CTkLabel(
            frame_prev,
            text=f"R$ {prev['projecao_fim_mes']:,.2f}",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#CDD6F4",
        ).pack(anchor="w", padx=20, pady=(0, 2))

        # Barra de dias decorridos vs dias totais
        pct_mes = prev["dias_decorridos"] / max(1, prev["dias_totais"])
        prog_dias = ctk.CTkProgressBar(
            frame_prev,
            height=8,
            corner_radius=4,
            progress_color="#89B4FA",
            fg_color="#313244",
        )
        prog_dias.set(pct_mes)
        prog_dias.pack(fill="x", padx=20, pady=(2, 6))

        # Detalhes: Gasto atual, dias restantes e ritmo
        txt_dias = f"Dia {prev['dias_decorridos']} de {prev['dias_totais']} ({prev['dias_restantes']} dias restantes)"
        txt_ritmo = f"Ritmo atual: R$ {prev['ritmo_diario']:,.2f}/dia"
        if prev["limite_total"] > 0:
            txt_teto = f" • Teto: R$ {prev['limite_total']:,.2f}"
        else:
            txt_teto = ""

        ctk.CTkLabel(
            frame_prev,
            text=f"{txt_dias} • {txt_ritmo}{txt_teto}",
            font=ctk.CTkFont(size=11),
            text_color="#A6ADC8",
        ).pack(anchor="w", padx=20, pady=(0, 2))

        ctk.CTkLabel(
            frame_prev,
            text=prev["mensagem"],
            font=ctk.CTkFont(size=12, weight="bold" if prev["status"] == "estouro_previsto" else "normal"),
            text_color=badge_cor,
        ).pack(anchor="w", padx=20, pady=(2, 15))

    # ==============================================================
    # 3. SEÇÃO DE INSIGHTS AUTOMÁTICOS & GASTOS FORA DO PADRÃO (FUNC. 2 E 4)
    # ==============================================================
    def _build_secao_insights(self):
        frame_insights = ctk.CTkFrame(
            self.conteudo,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        frame_insights.pack(fill="x", pady=(0, 15))

        top_ins = ctk.CTkFrame(frame_insights, fg_color="transparent")
        top_ins.pack(fill="x", padx=20, pady=(15, 10))
        top_ins.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            top_ins,
            text="💡  INSIGHTS AUTOMÁTICOS & DETECÇÃO DE PADRÕES",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            top_ins,
            text="Atualizado com base nos seus últimos lançamentos",
            font=ctk.CTkFont(size=11),
            text_color="#585B70",
        ).grid(row=0, column=1, sticky="e")

        # Container em grade/linhas para os cards de insights
        grid_ins = ctk.CTkFrame(frame_insights, fg_color="transparent")
        grid_ins.pack(fill="x", padx=15, pady=(0, 15))
        grid_ins.grid_columnconfigure((0, 1), weight=1)

        for idx, item in enumerate(self.lista_insights[:4]):
            col = idx % 2
            row = idx // 2

            card_item = ctk.CTkFrame(
                grid_ins,
                fg_color="#181825",
                corner_radius=10,
                border_width=1,
                border_color="#313244",
            )
            card_item.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)

            top_item = ctk.CTkFrame(card_item, fg_color="transparent")
            top_item.pack(fill="x", padx=12, pady=(10, 4))

            ctk.CTkLabel(
                top_item,
                text=f"{item['icone']}  {item['titulo']}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=item.get("cor", "#CDD6F4"),
            ).pack(anchor="w")

            ctk.CTkLabel(
                card_item,
                text=item["mensagem"],
                font=ctk.CTkFont(size=12),
                text_color="#CDD6F4",
                wraplength=420,
                justify="left",
            ).pack(anchor="w", padx=12, pady=(0, 10))

    # ==============================================================
    # 4. ALERTA DE VAZAMENTO & PLANO DE AÇÃO
    # ==============================================================
    def _build_alerta_vazamento_e_plano(self, parent):
        frame_esq = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        frame_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        vaz = self.resultado_saude["vazamento"]
        if vaz:
            # Alerta de Vazamento
            f_vaz = ctk.CTkFrame(frame_esq, fg_color="#2A1B28", corner_radius=10, border_width=1, border_color="#F38BA8")
            f_vaz.pack(fill="x", padx=15, pady=(15, 10))

            ctk.CTkLabel(
                f_vaz,
                text="⚠️  ALERTA DE VAZAMENTO DE ORÇAMENTO",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#F38BA8",
            ).pack(anchor="w", padx=12, pady=(10, 2))

            ctk.CTkLabel(
                f_vaz,
                text=f"A categoria '{vaz['categoria']}' atingiu R$ {vaz['atual']:,.2f}, ultrapassando o limite recomendado de R$ {vaz['limite']:,.2f}.",
                font=ctk.CTkFont(size=12),
                text_color="#CDD6F4",
                wraplength=380,
                justify="left",
            ).pack(anchor="w", padx=12, pady=(0, 10))
        else:
            f_vaz = ctk.CTkFrame(frame_esq, fg_color="#1B2A1E", corner_radius=10, border_width=1, border_color="#A6E3A1")
            f_vaz.pack(fill="x", padx=15, pady=(15, 10))

            ctk.CTkLabel(
                f_vaz,
                text="✅  NENHUM VAZAMENTO IDENTIFICADO",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#A6E3A1",
            ).pack(anchor="w", padx=12, pady=(10, 2))

            ctk.CTkLabel(
                f_vaz,
                text="Suas categorias de gastos permanecem sob controle proporcional à renda.",
                font=ctk.CTkFont(size=12),
                text_color="#CDD6F4",
                wraplength=380,
                justify="left",
            ).pack(anchor="w", padx=12, pady=(0, 10))

        # Plano de Ação
        ctk.CTkLabel(
            frame_esq,
            text="🎯  PLANO DE AÇÃO DIRECIONADO",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        ).pack(anchor="w", padx=15, pady=(5, 6))

        for item in self.resultado_saude["plano_acao"][:3]:
            item_frame = ctk.CTkFrame(frame_esq, fg_color="#181825", corner_radius=8)
            item_frame.pack(fill="x", padx=15, pady=3)

            chk = ctk.CTkCheckBox(
                item_frame,
                text=item["missao"],
                font=ctk.CTkFont(size=12),
                text_color="#CDD6F4" if not item["concluida"] else "#585B70",
                checkbox_height=18,
                checkbox_width=18,
                state="disabled",
            )
            if item["concluida"]:
                chk.select()
            chk.pack(side="left", padx=10, pady=8)

            ctk.CTkLabel(
                item_frame,
                text=item["pontos"],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#89B4FA",
            ).pack(side="right", padx=10)

        ctk.CTkLabel(frame_esq, text="", height=4).pack()

    # ==============================================================
    # 5. RESUMO DO PERÍODO
    # ==============================================================
    def _build_resumo(self, parent):
        resumo = self.resultado_saude["resumo"]
        frame_resumo = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        frame_resumo.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)

        ctk.CTkLabel(
            frame_resumo,
            text="📌  RESUMO GERAL ACUMULADO",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        ).pack(anchor="w", padx=20, pady=(15, 10))

        linhas = [
            ("Receitas Totais", resumo["total_receitas"], "#A6E3A1"),
            ("Despesas Totais", resumo["total_despesas"], "#F38BA8"),
            ("Saldo Geral", resumo["saldo"], "#A6E3A1" if resumo["saldo"] >= 0 else "#F38BA8"),
        ]

        for nome, valor, cor in linhas:
            linha = ctk.CTkFrame(frame_resumo, fg_color="transparent")
            linha.pack(fill="x", padx=20, pady=4)

            ctk.CTkLabel(
                linha,
                text=nome,
                font=ctk.CTkFont(size=13),
                text_color="#CDD6F4",
            ).pack(side="left")

            ctk.CTkLabel(
                linha,
                text=f"R$ {valor:,.2f}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=cor,
            ).pack(side="right")

        ctk.CTkLabel(
            frame_resumo,
            text=f"Total de {resumo['qtd_lancamentos']} lançamento(s) registrados no histórico.",
            font=ctk.CTkFont(size=11),
            text_color="#A6ADC8",
        ).pack(anchor="w", padx=20, pady=(15, 15))

    @staticmethod
    def _cor_por_score(score):
        if score >= 600:
            return "#A6E3A1"
        if score >= 400:
            return "#F9E2AF"
        return "#F38BA8"