"""
View do Simulador Financeiro "E se...?".
==========================================

Permite simular cenários hipotéticos (corte de gastos, aumento de renda,
aportes extras em metas) sem alterar dados reais do banco de dados.
"""
from typing import Optional, Dict, Any, List
import customtkinter as ctk

from dao.lancamento_dao import LancamentoDAO
from dao.meta_dao import MetaDAO
from dao.categoria_dao import CategoriaDAO
from controllers.inteligencia_financeira_controller import InteligenciaFinanceiraController


class SimuladorView(ctk.CTkFrame):
    """Tela interativa do Simulador Financeiro 'E se...?'."""

    def __init__(
        self,
        parent,
        dao: Optional[LancamentoDAO] = None,
        meta_dao: Optional[MetaDAO] = None,
        cat_dao: Optional[CategoriaDAO] = None,
    ):
        super().__init__(parent, fg_color="transparent")

        self.dao = dao or LancamentoDAO()
        self.meta_dao = meta_dao or MetaDAO()
        self.cat_dao = cat_dao or CategoriaDAO()

        # Layout responsivo: Coluna 0 (Controles) e Coluna 1 (Resultados)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._criar_layout()
        self.atualizar_dados()

    # ==============================================================
    # CRIAÇÃO DO LAYOUT
    # ==============================================================
    def _criar_layout(self):
        # ----------------- PAINEL ESQUERDO: CONTROLES -----------------
        self.card_controles = ctk.CTkScrollableFrame(
            self,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        self.card_controles.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        self.card_controles.grid_columnconfigure(0, weight=1)

        # Cabeçalho
        ctk.CTkLabel(
            self.card_controles,
            text="🔮  PARÂMETROS DA SIMULAÇÃO",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#89B4FA",
            anchor="w",
        ).pack(fill="x", padx=15, pady=(15, 2))

        ctk.CTkLabel(
            self.card_controles,
            text="Ajuste os parâmetros abaixo para ver o impacto instantâneo.",
            font=ctk.CTkFont(size=12),
            text_color="#A6ADC8",
            anchor="w",
        ).pack(fill="x", padx=15, pady=(0, 15))

        # 1. Redução de Gastos (%)
        sec_gastos = ctk.CTkFrame(self.card_controles, fg_color="#181825", corner_radius=10)
        sec_gastos.pack(fill="x", padx=15, pady=(0, 12))

        header_g = ctk.CTkFrame(sec_gastos, fg_color="transparent")
        header_g.pack(fill="x", padx=12, pady=(10, 4))
        header_g.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_g,
            text="📉 Redução de Despesas:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#CDD6F4",
        ).grid(row=0, column=0, sticky="w")

        self.lbl_pct_reducao = ctk.CTkLabel(
            header_g,
            text="0%",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#A6E3A1",
        )
        self.lbl_pct_reducao.grid(row=0, column=1, sticky="e")

        self.slider_reducao = ctk.CTkSlider(
            sec_gastos,
            from_=0,
            to=50,
            number_of_steps=50,
            command=self._on_slider_reducao_change,
            button_color="#A6E3A1",
            button_hover_color="#94D38F",
            progress_color="#A6E3A1",
        )
        self.slider_reducao.set(0)
        self.slider_reducao.pack(fill="x", padx=12, pady=(4, 8))

        # Botões de atalho para redução
        frame_chips_red = ctk.CTkFrame(sec_gastos, fg_color="transparent")
        frame_chips_red.pack(fill="x", padx=12, pady=(0, 10))
        frame_chips_red.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for idx, pct in enumerate([0, 10, 20, 30]):
            ctk.CTkButton(
                frame_chips_red,
                text=f"-{pct}%" if pct > 0 else "0%",
                height=26,
                font=ctk.CTkFont(size=11),
                fg_color="#313244",
                hover_color="#45475A",
                command=lambda p=pct: self._set_reducao(p),
            ).grid(row=0, column=idx, padx=2, sticky="ew")

        # Categoria Alvo da Redução
        ctk.CTkLabel(
            sec_gastos,
            text="Aplicar redução em:",
            font=ctk.CTkFont(size=12),
            text_color="#A6ADC8",
        ).pack(anchor="w", padx=12, pady=(4, 2))

        self.combo_categoria = ctk.CTkComboBox(
            sec_gastos,
            values=["Todas as Despesas"],
            command=lambda _: self._recalcular(),
            fg_color="#11111b",
            border_color="#313244",
            button_color="#313244",
        )
        self.combo_categoria.set("Todas as Despesas")
        self.combo_categoria.pack(fill="x", padx=12, pady=(0, 12))

        # 2. Aumento de Renda Mensal (R$)
        sec_renda = ctk.CTkFrame(self.card_controles, fg_color="#181825", corner_radius=10)
        sec_renda.pack(fill="x", padx=15, pady=(0, 12))

        header_r = ctk.CTkFrame(sec_renda, fg_color="transparent")
        header_r.pack(fill="x", padx=12, pady=(10, 4))
        header_r.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_r,
            text="📈 Aumento de Renda / Extra:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#CDD6F4",
        ).grid(row=0, column=0, sticky="w")

        self.lbl_val_renda = ctk.CTkLabel(
            header_r,
            text="+ R$ 0,00",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#89B4FA",
        )
        self.lbl_val_renda.grid(row=0, column=1, sticky="e")

        self.slider_renda = ctk.CTkSlider(
            sec_renda,
            from_=0,
            to=5000,
            number_of_steps=100,
            command=self._on_slider_renda_change,
            button_color="#89B4FA",
            button_hover_color="#74A7F7",
            progress_color="#89B4FA",
        )
        self.slider_renda.set(0)
        self.slider_renda.pack(fill="x", padx=12, pady=(4, 8))

        # Atalhos de renda
        frame_chips_renda = ctk.CTkFrame(sec_renda, fg_color="transparent")
        frame_chips_renda.pack(fill="x", padx=12, pady=(0, 10))
        frame_chips_renda.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for idx, val in enumerate([0, 300, 750, 1500]):
            ctk.CTkButton(
                frame_chips_renda,
                text=f"+R${val}" if val > 0 else "R$ 0",
                height=26,
                font=ctk.CTkFont(size=11),
                fg_color="#313244",
                hover_color="#45475A",
                command=lambda v=val: self._set_renda(v),
            ).grid(row=0, column=idx, padx=2, sticky="ew")

        # 3. Aporte Adicional Direto para Metas
        sec_metas = ctk.CTkFrame(self.card_controles, fg_color="#181825", corner_radius=10)
        sec_metas.pack(fill="x", padx=15, pady=(0, 15))

        header_m = ctk.CTkFrame(sec_metas, fg_color="transparent")
        header_m.pack(fill="x", padx=12, pady=(10, 4))
        header_m.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_m,
            text="🎯 Aporte Extra para Metas:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#CDD6F4",
        ).grid(row=0, column=0, sticky="w")

        self.lbl_val_meta = ctk.CTkLabel(
            header_m,
            text="+ R$ 0,00",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#CBA6F7",
        )
        self.lbl_val_meta.grid(row=0, column=1, sticky="e")

        self.slider_meta = ctk.CTkSlider(
            sec_metas,
            from_=0,
            to=2000,
            number_of_steps=40,
            command=self._on_slider_meta_change,
            button_color="#CBA6F7",
            button_hover_color="#BA95E5",
            progress_color="#CBA6F7",
        )
        self.slider_meta.set(0)
        self.slider_meta.pack(fill="x", padx=12, pady=(4, 8))

        frame_chips_meta = ctk.CTkFrame(sec_metas, fg_color="transparent")
        frame_chips_meta.pack(fill="x", padx=12, pady=(0, 10))
        frame_chips_meta.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for idx, val in enumerate([0, 150, 300, 600]):
            ctk.CTkButton(
                frame_chips_meta,
                text=f"+R${val}" if val > 0 else "R$ 0",
                height=26,
                font=ctk.CTkFont(size=11),
                fg_color="#313244",
                hover_color="#45475A",
                command=lambda v=val: self._set_meta(v),
            ).grid(row=0, column=idx, padx=2, sticky="ew")

        # Botão Resetar Simulação
        ctk.CTkButton(
            self.card_controles,
            text="🔄 Resetar Todos os Parâmetros",
            height=34,
            fg_color="#313244",
            hover_color="#45475A",
            text_color="#CDD6F4",
            command=self._resetar,
        ).pack(fill="x", padx=15, pady=(0, 15))

        # ----------------- PAINEL DIREITO: RESULTADOS -----------------
        self.card_resultados = ctk.CTkScrollableFrame(
            self,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        self.card_resultados.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        self.card_resultados.grid_columnconfigure(0, weight=1)

        # Cabeçalho de Resultados
        ctk.CTkLabel(
            self.card_resultados,
            text="📊  PROJEÇÃO DE IMPACTO",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#A6E3A1",
            anchor="w",
        ).pack(fill="x", padx=15, pady=(15, 2))

        self.lbl_mes_ref = ctk.CTkLabel(
            self.card_resultados,
            text="Base de cálculo: Mês Atual",
            font=ctk.CTkFont(size=12),
            text_color="#A6ADC8",
            anchor="w",
        )
        self.lbl_mes_ref.pack(fill="x", padx=15, pady=(0, 15))

        # HERO CARD: Economia Anual e Mensal Gerada
        self.hero_card = ctk.CTkFrame(
            self.card_resultados,
            corner_radius=12,
            fg_color="#1B2A1E",
            border_width=1,
            border_color="#A6E3A1",
        )
        self.hero_card.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(
            self.hero_card,
            text="🎉 ECONOMIA EXTRA PROJETADA",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#A6E3A1",
        ).pack(anchor="w", padx=15, pady=(12, 2))

        self.lbl_hero_economia_mensal = ctk.CTkLabel(
            self.hero_card,
            text="+ R$ 0,00 / mês",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#A6E3A1",
        )
        self.lbl_hero_economia_mensal.pack(anchor="w", padx=15, pady=(0, 2))

        self.lbl_hero_economia_anual = ctk.CTkLabel(
            self.hero_card,
            text="Economia estimada de R$ 0,00 ao longo de 1 ano",
            font=ctk.CTkFont(size=12),
            text_color="#CDD6F4",
        )
        self.lbl_hero_economia_anual.pack(anchor="w", padx=15, pady=(0, 12))

        # COMPARATIVO: Cenário Atual vs Cenário Simulado
        frame_comparativo = ctk.CTkFrame(self.card_resultados, fg_color="transparent")
        frame_comparativo.pack(fill="x", padx=15, pady=(0, 15))
        frame_comparativo.grid_columnconfigure((0, 1), weight=1)

        # Coluna Real (Hoje)
        card_real = ctk.CTkFrame(frame_comparativo, fg_color="#181825", corner_radius=10)
        card_real.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ctk.CTkLabel(
            card_real,
            text="CENÁRIO ATUAL",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#A6ADC8",
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.lbl_real_rec = ctk.CTkLabel(card_real, text="Receitas: R$ 0,00", font=ctk.CTkFont(size=12), text_color="#CDD6F4")
        self.lbl_real_rec.pack(anchor="w", padx=12, pady=2)

        self.lbl_real_desp = ctk.CTkLabel(card_real, text="Despesas: R$ 0,00", font=ctk.CTkFont(size=12), text_color="#F38BA8")
        self.lbl_real_desp.pack(anchor="w", padx=12, pady=2)

        self.lbl_real_saldo = ctk.CTkLabel(card_real, text="Saldo: R$ 0,00", font=ctk.CTkFont(size=13, weight="bold"), text_color="#CDD6F4")
        self.lbl_real_saldo.pack(anchor="w", padx=12, pady=(4, 10))

        # Coluna Simulada (Com Mudanças)
        card_sim = ctk.CTkFrame(frame_comparativo, fg_color="#181825", corner_radius=10, border_width=1, border_color="#89B4FA")
        card_sim.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        ctk.CTkLabel(
            card_sim,
            text="CENÁRIO SIMULADO",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#89B4FA",
        ).pack(anchor="w", padx=12, pady=(10, 6))

        self.lbl_sim_rec = ctk.CTkLabel(card_sim, text="Receitas: R$ 0,00", font=ctk.CTkFont(size=12), text_color="#CDD6F4")
        self.lbl_sim_rec.pack(anchor="w", padx=12, pady=2)

        self.lbl_sim_desp = ctk.CTkLabel(card_sim, text="Despesas: R$ 0,00", font=ctk.CTkFont(size=12), text_color="#A6E3A1")
        self.lbl_sim_desp.pack(anchor="w", padx=12, pady=2)

        self.lbl_sim_saldo = ctk.CTkLabel(card_sim, text="Saldo: R$ 0,00", font=ctk.CTkFont(size=13, weight="bold"), text_color="#A6E3A1")
        self.lbl_sim_saldo.pack(anchor="w", padx=12, pady=(4, 10))

        # SEÇÃO: IMPACTO NAS METAS FINANCEIRAS
        ctk.CTkLabel(
            self.card_resultados,
            text="🎯  IMPACTO NAS SUAS METAS",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#CBA6F7",
            anchor="w",
        ).pack(fill="x", padx=15, pady=(5, 6))

        self.frame_container_metas = ctk.CTkFrame(self.card_resultados, fg_color="transparent")
        self.frame_container_metas.pack(fill="x", padx=15, pady=(0, 15))

        # Banner de segurança no rodapé
        banner_info = ctk.CTkFrame(self.card_resultados, fg_color="#181825", corner_radius=8)
        banner_info.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkLabel(
            banner_info,
            text="🔒 Simulação pura em memória: nenhum lançamento ou saldo real é alterado.",
            font=ctk.CTkFont(size=11),
            text_color="#BAC2DE",
        ).pack(padx=12, pady=8)

    # ==============================================================
    # INTERAÇÃO DOS SLIDERS
    # ==============================================================
    def _on_slider_reducao_change(self, val):
        self.lbl_pct_reducao.configure(text=f"-{int(val)}%")
        self._recalcular()

    def _set_reducao(self, val):
        self.slider_reducao.set(val)
        self.lbl_pct_reducao.configure(text=f"-{int(val)}%")
        self._recalcular()

    def _on_slider_renda_change(self, val):
        self.lbl_val_renda.configure(text=f"+ R$ {val:,.2f}")
        self._recalcular()

    def _set_renda(self, val):
        self.slider_renda.set(val)
        self.lbl_val_renda.configure(text=f"+ R$ {val:,.2f}")
        self._recalcular()

    def _on_slider_meta_change(self, val):
        self.lbl_val_meta.configure(text=f"+ R$ {val:,.2f}")
        self._recalcular()

    def _set_meta(self, val):
        self.slider_meta.set(val)
        self.lbl_val_meta.configure(text=f"+ R$ {val:,.2f}")
        self._recalcular()

    def _resetar(self):
        self.slider_reducao.set(0)
        self.lbl_pct_reducao.configure(text="0%")
        self.slider_renda.set(0)
        self.lbl_val_renda.configure(text="+ R$ 0,00")
        self.slider_meta.set(0)
        self.lbl_val_meta.configure(text="+ R$ 0,00")
        self.combo_categoria.set("Todas as Despesas")
        self._recalcular()

    # ==============================================================
    # ATUALIZAÇÃO DE DADOS
    # ==============================================================
    def atualizar_dados(self):
        """Carrega categorias ativas e calcula a simulação inicial."""
        # Atualizar opções de categoria
        categorias = self.cat_dao.listar_por_tipo("Despesa")
        nomes_cats = ["Todas as Despesas"] + [c["nome"] for c in categorias]
        self.combo_categoria.configure(values=nomes_cats)
        self._recalcular()

    def _recalcular(self):
        """Executa o cálculo analítico com os parâmetros atuais dos widgets."""
        lancamentos = self.dao.listar_todos()
        metas = self.meta_dao.listar_todas()
        categorias = self.cat_dao.listar_todas()

        pct_red = self.slider_reducao.get()
        cat_alvo = self.combo_categoria.get()
        aumento_renda = self.slider_renda.get()
        aporte_meta = self.slider_meta.get()

        resultado = InteligenciaFinanceiraController.calcular_simulacao(
            lancamentos=lancamentos,
            metas=metas,
            categorias=categorias,
            reducao_despesas_pct=pct_red,
            categoria_alvo=cat_alvo,
            aumento_renda_valor=aumento_renda,
            aporte_extra_metas=aporte_meta,
        )

        self._renderizar_resultados(resultado)

    def _renderizar_resultados(self, res: Dict[str, Any]):
        base = res["cenario_base"]
        sim = res["cenario_simulado"]
        diff = res["diferenca"]

        self.lbl_mes_ref.configure(text=f"Base de referência: {res['mes_referencia']}")

        # Hero
        self.lbl_hero_economia_mensal.configure(
            text=f"+ R$ {diff['economia_mensal']:,.2f} / mês"
        )
        self.lbl_hero_economia_anual.configure(
            text=f"Isso representa R$ {diff['economia_anual']:,.2f} a mais no seu bolso ao final de 12 meses!"
        )

        # Cenário Real
        self.lbl_real_rec.configure(text=f"Receitas: R$ {base['receitas']:,.2f}")
        self.lbl_real_desp.configure(text=f"Despesas: R$ {base['despesas']:,.2f}")
        cor_saldo_real = "#A6E3A1" if base["saldo"] >= 0 else "#F38BA8"
        self.lbl_real_saldo.configure(
            text=f"Saldo: R$ {base['saldo']:,.2f}",
            text_color=cor_saldo_real,
        )

        # Cenário Simulado
        self.lbl_sim_rec.configure(text=f"Receitas: R$ {sim['receitas']:,.2f}")
        self.lbl_sim_desp.configure(text=f"Despesas: R$ {sim['despesas']:,.2f}")
        cor_saldo_sim = "#A6E3A1" if sim["saldo"] >= 0 else "#F38BA8"
        self.lbl_sim_saldo.configure(
            text=f"Saldo: R$ {sim['saldo']:,.2f}",
            text_color=cor_saldo_sim,
        )

        # Renderizar Metas Impactadas
        for widget in self.frame_container_metas.winfo_children():
            widget.destroy()

        impacto_metas = res["impacto_metas"]
        if not impacto_metas:
            ctk.CTkLabel(
                self.frame_container_metas,
                text="Nenhuma meta em andamento cadastrada na aba 'Metas'.\nCadastre metas para visualizar a redução do tempo de conquista!",
                font=ctk.CTkFont(size=12),
                text_color="#A6ADC8",
                justify="left",
            ).pack(anchor="w", pady=4)
        else:
            for item in impacto_metas[:3]:
                card_m = ctk.CTkFrame(
                    self.frame_container_metas,
                    fg_color="#181825",
                    corner_radius=8,
                    border_width=1,
                    border_color="#313244",
                )
                card_m.pack(fill="x", pady=4)

                top_m = ctk.CTkFrame(card_m, fg_color="transparent")
                top_m.pack(fill="x", padx=10, pady=(8, 2))
                top_m.grid_columnconfigure(1, weight=1)

                ctk.CTkLabel(
                    top_m,
                    text=f"🎯 {item['descricao']}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#CDD6F4",
                ).grid(row=0, column=0, sticky="w")

                if item["meses_economizados"] > 0:
                    badge_texto = f"🚀 {item['meses_economizados']} mês(es) mais rápido!"
                    badge_cor = "#A6E3A1"
                else:
                    badge_texto = "Ritmo mantido"
                    badge_cor = "#BAC2DE"

                ctk.CTkLabel(
                    top_m,
                    text=badge_texto,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=badge_cor,
                ).grid(row=0, column=1, sticky="e")

                detalhe_m = (
                    f"Alvo: R$ {item['valor_alvo']:,.2f} | Atual: R$ {item['valor_atual']:,.2f} • "
                    f"Ritmo atual: {item['meses_cenario_atual']} meses ➔ Simulado: {item['meses_cenario_simulado']} meses"
                )
                ctk.CTkLabel(
                    card_m,
                    text=detalhe_m,
                    font=ctk.CTkFont(size=11),
                    text_color="#A6ADC8",
                ).pack(anchor="w", padx=10, pady=(0, 8))
