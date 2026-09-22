import customtkinter as ctk
from datetime import datetime, date
from typing import Optional
from dao.lancamento_dao import LancamentoDAO
from dao.categoria_dao import CategoriaDAO
from views.notificacao_toast import GerenciadorNotificacoes
from dao.terceiro_dao import TerceiroDAO
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_ACENTO_HOVER, COR_SUCESSO, COR_SUCESSO_HOVER,
    COR_ALERTA, COR_ALERTA_HOVER, COR_INFO,
    COR_RECEITA, COR_RECEITA_BG, COR_DESPESA, COR_DESPESA_BG,
    COR_BOTAO_SECUNDARIO, COR_BOTAO_SECUNDARIO_HOVER,
    COR_EXCLUIR_HOVER, COR_EXCLUIR_TEXTO,
    fonte, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
    fonte_grande_valor,
)



class LancamentoView(ctk.CTkFrame):
    """Tela interativa de Lançamentos com Dashboard de Saldo, Formulário Inteligente e Histórico."""

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

        self.filtro_tipo = "Todos"
        self.busca_texto = ""

        # Layout Principal: Linha 0 (Cards Resumo), Linha 1 (Formulário + Lista)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._criar_cards_resumo()
        self._criar_formulario()
        self._criar_painel_historico()
        self.atualizar_dados()

    # ==========================================================
    # CARDS DE RESUMO (TOPO)
    # ==========================================================
    def _criar_cards_resumo(self):
        frame_resumo = ctk.CTkFrame(self, fg_color="transparent")
        frame_resumo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        frame_resumo.grid_columnconfigure((0, 1, 2), weight=1)

        # 1. Total Receitas
        card_rec = ctk.CTkFrame(
            frame_resumo,
            corner_radius=12,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
        )
        card_rec.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkLabel(
            card_rec,
            text="📈 TOTAL RECEITAS",
            font=fonte(11, "bold"),
            text_color=COR_TEXTO_SECUNDARIO,
        ).pack(anchor="w", padx=15, pady=(12, 2))
        self.lbl_total_receitas = ctk.CTkLabel(
            card_rec,
            text="R$ 0,00",
            font=fonte_grande_valor(),
            text_color=COR_RECEITA,
        )
        self.lbl_total_receitas.pack(anchor="w", padx=15, pady=(0, 12))

        # 2. Total Despesas
        card_desp = ctk.CTkFrame(
            frame_resumo,
            corner_radius=12,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
        )
        card_desp.grid(row=0, column=1, sticky="ew", padx=4)
        ctk.CTkLabel(
            card_desp,
            text="📉 TOTAL DESPESAS",
            font=fonte(11, "bold"),
            text_color=COR_TEXTO_SECUNDARIO,
        ).pack(anchor="w", padx=15, pady=(12, 2))
        self.lbl_total_despesas = ctk.CTkLabel(
            card_desp,
            text="R$ 0,00",
            font=fonte_grande_valor(),
            text_color=COR_DESPESA,
        )
        self.lbl_total_despesas.pack(anchor="w", padx=15, pady=(0, 12))

        # 3. Saldo Atual
        card_saldo = ctk.CTkFrame(
            frame_resumo,
            corner_radius=12,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
        )
        card_saldo.grid(row=0, column=2, sticky="ew", padx=(8, 0))
        ctk.CTkLabel(
            card_saldo,
            text="💳 SALDO LÍQUIDO",
            font=fonte(11, "bold"),
            text_color=COR_TEXTO_SECUNDARIO,
        ).pack(anchor="w", padx=15, pady=(12, 2))
        self.lbl_saldo = ctk.CTkLabel(
            card_saldo,
            text="R$ 0,00",
            font=fonte_grande_valor(),
            text_color=COR_ACENTO_PRIMARIO,
        )
        self.lbl_saldo.pack(anchor="w", padx=15, pady=(0, 12))

    # ==========================================================
    # FORMULÁRIO (ESQUERDA)
    # ==========================================================
    def _criar_formulario(self):
        self.card_form = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_DESPESA_BG,
        )
        self.card_form.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        # Título dinâmico
        self.lbl_titulo_form = ctk.CTkLabel(
            self.card_form,
            text="➕  NOVA DESPESA",
            font=fonte_subtitulo(),
            text_color=COR_DESPESA,
        )
        self.lbl_titulo_form.pack(anchor="w", padx=20, pady=(15, 10))

        # SELETOR VISUAL DE TIPO (RECEITA / DESPESA) COM BOTÕES LADO A LADO
        frame_tipo = ctk.CTkFrame(self.card_form, fg_color="transparent")
        frame_tipo.pack(fill="x", padx=20, pady=(0, 10))
        frame_tipo.grid_columnconfigure((0, 1), weight=1)

        self.tipo_selecionado = "DESPESA"

        self.btn_sel_despesa = ctk.CTkButton(
            frame_tipo,
            text="🔴  DESPESA",
            font=fonte(13, "bold"),
            height=38,
            fg_color=COR_DESPESA,
            text_color="#0B1D1F",
            hover_color=COR_ALERTA_HOVER,
            command=lambda: self._selecionar_tipo("DESPESA"),
        )
        self.btn_sel_despesa.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.btn_sel_receita = ctk.CTkButton(
            frame_tipo,
            text="🟢  RECEITA",
            font=fonte(13, "bold"),
            height=38,
            fg_color=COR_BOTAO_SECUNDARIO,
            text_color=COR_TEXTO_SECUNDARIO,
            hover_color=COR_BOTAO_SECUNDARIO_HOVER,
            command=lambda: self._selecionar_tipo("RECEITA"),
        )
        self.btn_sel_receita.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Descrição
        self.lbl_descricao = ctk.CTkLabel(
            self.card_form, text="Descrição:", font=fonte_corpo()
        )
        self.lbl_descricao.pack(anchor="w", padx=20, pady=(0, 2))
        self.descricao = ctk.CTkEntry(
            self.card_form,
            placeholder_text="Ex: Aluguel, Supermercado, Luz, Combustível...",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            font=fonte_corpo(),
        )
        self.descricao.pack(fill="x", padx=20, pady=(0, 8))

        # Campo Valor
        ctk.CTkLabel(self.card_form, text="Valor (R$):", font=fonte_corpo()).pack(
            anchor="w", padx=20, pady=(0, 2)
        )
        self.valor = ctk.CTkEntry(
            self.card_form,
            placeholder_text="0.00",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            font=fonte(14, "bold"),
        )
        self.valor.pack(fill="x", padx=20, pady=(0, 4))

        # Atalhos rápidos de valores (+10, +50, +100, +500)
        chips_frame = ctk.CTkFrame(self.card_form, fg_color="transparent")
        chips_frame.pack(fill="x", padx=20, pady=(0, 8))
        chips_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        valores_rapidos = [10, 50, 100, 500]
        for idx, val in enumerate(valores_rapidos):
            btn_chip = ctk.CTkButton(
                chips_frame,
                text=f"+{val}",
                height=24,
                font=fonte_pequena(),
                fg_color=COR_BOTAO_SECUNDARIO,
                hover_color=COR_BOTAO_SECUNDARIO_HOVER,
                text_color=COR_TEXTO_PRINCIPAL,
                command=lambda v=val: self._somar_ao_valor(v),
            )
            btn_chip.grid(row=0, column=idx, padx=2, sticky="ew")

        btn_limpar_val = ctk.CTkButton(
            chips_frame,
            text="C",
            height=24,
            width=28,
            font=fonte(11, "bold"),
            fg_color=COR_DESPESA_BG,
            hover_color=COR_EXCLUIR_HOVER,
            text_color=COR_DESPESA,
            command=lambda: self.valor.delete(0, "end"),
        )
        btn_limpar_val.grid(row=0, column=4, padx=2, sticky="ew")

        # Linha dupla: Categoria e Terceiro
        duo2 = ctk.CTkFrame(self.card_form, fg_color="transparent")
        duo2.pack(fill="x", padx=20, pady=(0, 8))
        duo2.grid_columnconfigure((0, 1), weight=1)

        self.lbl_categoria = ctk.CTkLabel(
            duo2, text="Categoria da Despesa:", font=fonte_corpo()
        )
        self.lbl_categoria.grid(row=0, column=0, sticky="w", pady=(0, 2))

        self.lbl_terceiro = ctk.CTkLabel(
            duo2, text="Beneficiário / Fornecedor (opcional):", font=fonte_corpo()
        )
        self.lbl_terceiro.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 2))

        self.categoria = ctk.CTkComboBox(
            duo2,
            values=["Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Educação", "Outros"],
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            button_color=COR_BOTAO_SECUNDARIO,
            font=fonte_corpo(),
        )
        self.categoria.grid(row=1, column=0, sticky="ew")

        self.terceiro = ctk.CTkComboBox(
            duo2,
            values=["Nenhum"],
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            button_color=COR_BOTAO_SECUNDARIO,
            font=fonte_corpo(),
        )
        self.terceiro.grid(row=1, column=1, sticky="ew", padx=(10, 0))

        # Linha dupla: Vencimento e Status
        duo3 = ctk.CTkFrame(self.card_form, fg_color="transparent")
        duo3.pack(fill="x", padx=20, pady=(0, 10))
        duo3.grid_columnconfigure((0, 1), weight=1)

        self.lbl_data = ctk.CTkLabel(
            duo3, text="Data / Vencimento:", font=fonte_corpo()
        )
        self.lbl_data.grid(row=0, column=0, sticky="w", pady=(0, 2))

        self.lbl_status = ctk.CTkLabel(
            duo3, text="Status do Pagamento:", font=fonte_corpo()
        )
        self.lbl_status.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 2))

        self.data_vencimento = ctk.CTkEntry(
            duo3,
            placeholder_text="DD/MM/AAAA",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            font=fonte_corpo(),
        )
        hoje_formatado = date.today().strftime("%d/%m/%Y")
        self.data_vencimento.insert(0, hoje_formatado)
        self.data_vencimento.grid(row=1, column=0, sticky="ew")

        ctk.CTkLabel(
            duo3,
            text="📅 Formato: DD/MM/AAAA",
            font=fonte_hint(),
            text_color=COR_TEXTO_MUTED,
            anchor="w",
        ).grid(row=2, column=0, sticky="w", pady=(2, 0))

        self.status = ctk.CTkComboBox(
            duo3,
            values=["PAGO", "PENDENTE"],
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            button_color=COR_BOTAO_SECUNDARIO,
            font=fonte_corpo(),
        )
        self.status.set("PAGO")
        self.status.grid(row=1, column=1, sticky="ew", padx=(10, 0))

        # Feedback
        self.mensagem = ctk.CTkLabel(
            self.card_form,
            text="",
            font=fonte(12, "bold"),
        )
        self.mensagem.pack(fill="x", padx=20, pady=(0, 6))

        # Botões Salvar e Limpar lado a lado
        btn_box = ctk.CTkFrame(self.card_form, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=(0, 15))
        btn_box.grid_columnconfigure(0, weight=3)
        btn_box.grid_columnconfigure(1, weight=1)

        self.btn_salvar = ctk.CTkButton(
            btn_box,
            text="Salvar Despesa",
            fg_color=COR_DESPESA,
            text_color="#0B1D1F",
            hover_color=COR_ALERTA_HOVER,
            font=fonte(13, "bold"),
            height=38,
            command=self.salvar_lancamento,
        )
        self.btn_salvar.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        btn_limpar = ctk.CTkButton(
            btn_box,
            text="Limpar",
            fg_color=COR_BOTAO_SECUNDARIO,
            text_color=COR_TEXTO_PRINCIPAL,
            hover_color=COR_BOTAO_SECUNDARIO_HOVER,
            font=fonte_corpo(),
            height=38,
            command=self._limpar_campos,
        )
        btn_limpar.grid(row=0, column=1, sticky="ew")

        # Inicializa os textos, placeholders e categorias contextuais
        self._selecionar_tipo("DESPESA")

    def _atualizar_categorias_por_tipo(self, tipo: str):
        """Atualiza dinamicamente as opções de categoria conforme Receita ou Despesa."""
        tipo_busca = "Receita" if tipo == "RECEITA" else "Despesa"
        try:
            todas = self.cat_dao.listar_todas()
            filtradas = [
                c["nome"]
                for c in todas
                if c.get("tipo", "").strip().lower() == tipo_busca.lower()
            ]
        except Exception:
            filtradas = []

        if not filtradas:
            if tipo == "RECEITA":
                filtradas = ["Salário", "Rendimentos", "Vendas", "Freelance", "Bonificação", "Outras Receitas"]
            else:
                filtradas = ["Alimentação", "Transporte", "Moradia", "Lazer", "Saúde", "Educação", "Outras Despesas"]

        self.categoria.configure(values=filtradas)
        if filtradas:
            self.categoria.set(filtradas[0])

    def _selecionar_tipo(self, tipo):
        self.tipo_selecionado = tipo
        if tipo == "RECEITA":
            # Botões de tipo
            self.btn_sel_receita.configure(fg_color=COR_RECEITA, text_color="#0B1D1F")
            self.btn_sel_despesa.configure(fg_color=COR_BOTAO_SECUNDARIO, text_color=COR_TEXTO_SECUNDARIO)

            # Título e borda do card
            self.lbl_titulo_form.configure(text="➕  NOVA RECEITA", text_color=COR_RECEITA)
            self.card_form.configure(border_color=COR_RECEITA_BG)

            # Textos dos campos adaptados para Receita
            self.descricao.configure(
                placeholder_text="Ex: Salário, Rendimentos, Venda, Freelance, Pix recebido..."
            )
            self.lbl_categoria.configure(text="Categoria da Receita:")
            self.lbl_terceiro.configure(text="Fonte Pagadora / Cliente (opcional):")
            self.lbl_data.configure(text="Data do Recebimento:")
            self.lbl_status.configure(text="Status do Recebimento:")

            # Opções de Status adequadas para RECEITA
            self.status.configure(values=["RECEBIDO", "A RECEBER"])
            self.status.set("RECEBIDO")

            # Botão salvar
            self.btn_salvar.configure(
                text="Salvar Receita",
                fg_color=COR_RECEITA,
                hover_color=COR_SUCESSO_HOVER,
                text_color="#0B1D1F",
            )
        else:
            # Botões de tipo
            self.btn_sel_despesa.configure(fg_color=COR_DESPESA, text_color="#0B1D1F")
            self.btn_sel_receita.configure(fg_color=COR_BOTAO_SECUNDARIO, text_color=COR_TEXTO_SECUNDARIO)

            # Título e borda do card
            self.lbl_titulo_form.configure(text="➕  NOVA DESPESA", text_color=COR_DESPESA)
            self.card_form.configure(border_color=COR_DESPESA_BG)

            # Textos dos campos adaptados para Despesa
            self.descricao.configure(
                placeholder_text="Ex: Aluguel, Supermercado, Luz, Combustível, Cartão..."
            )
            self.lbl_categoria.configure(text="Categoria da Despesa:")
            self.lbl_terceiro.configure(text="Beneficiário / Fornecedor (opcional):")
            self.lbl_data.configure(text="Data / Vencimento:")
            self.lbl_status.configure(text="Status do Pagamento:")

            # Opções de Status adequadas para DESPESA
            self.status.configure(values=["PAGO", "PENDENTE"])
            self.status.set("PAGO")

            # Botão salvar
            self.btn_salvar.configure(
                text="Salvar Despesa",
                fg_color=COR_DESPESA,
                hover_color=COR_ALERTA_HOVER,
                text_color="#0B1D1F",
            )

        # Atualiza categorias disponíveis de acordo com o tipo
        self._atualizar_categorias_por_tipo(tipo)

    def _somar_ao_valor(self, quantia):
        val_atual_str = self.valor.get().strip().replace(",", ".").replace("R$", "")
        try:
            val_atual = float(val_atual_str) if val_atual_str else 0.0
        except ValueError:
            val_atual = 0.0
        novo_val = val_atual + quantia
        self.valor.delete(0, "end")
        self.valor.insert(0, f"{novo_val:.2f}")

    # ==========================================================
    # PAINEL DE HISTÓRICO (DIREITA)
    # ==========================================================
    def _criar_painel_historico(self):
        card_hist = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
        )
        card_hist.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        card_hist.grid_columnconfigure(0, weight=1)
        card_hist.grid_rowconfigure(2, weight=1)

        # Header com título e filtros
        header = ctk.CTkFrame(card_hist, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 6))
        header.grid_columnconfigure(0, weight=1)

        self.lbl_qtd_lancamentos = ctk.CTkLabel(
            header,
            text="Lançamentos Recentes",
            font=fonte_subtitulo(),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        )
        self.lbl_qtd_lancamentos.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        # Filtro de tipo (linha separada do título)
        self.filtro_btn = ctk.CTkSegmentedButton(
            header,
            values=["Todos", "Receitas", "Despesas"],
            command=self._alterar_filtro,
            selected_color=COR_BOTAO_SECUNDARIO,
            selected_hover_color=COR_BOTAO_SECUNDARIO_HOVER,
        )
        self.filtro_btn.set("Todos")
        self.filtro_btn.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Barra de busca por texto
        self.entry_busca = ctk.CTkEntry(
            card_hist,
            placeholder_text="🔍 Buscar por descrição ou categoria...",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            font=fonte_corpo(),
        )
        self.entry_busca.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 8))
        self.entry_busca.bind("<KeyRelease>", lambda e: self._filtrar_busca())

        # ScrollFrame para a lista
        self.scroll_lancamentos = ctk.CTkScrollableFrame(
            card_hist,
            fg_color="transparent",
            corner_radius=10,
        )
        self.scroll_lancamentos.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 15))
        self.scroll_lancamentos.grid_columnconfigure(0, weight=1)

    # ==========================================================
    # AÇÕES E CRUD
    # ==========================================================
    def _alterar_filtro(self, valor):
        self.filtro_tipo = valor
        self.atualizar_dados()

    def _filtrar_busca(self):
        self.busca_texto = self.entry_busca.get().strip().lower()
        self.atualizar_dados()

    def salvar_lancamento(self):
        descricao = self.descricao.get().strip()
        valor_str = self.valor.get().strip()
        tipo = self.tipo_selecionado
        categoria = self.categoria.get().strip()
        data_vencimento = self.data_vencimento.get().strip()

        if not descricao or len(descricao) < 3:
            self.mostrar_mensagem("A descrição deve ter pelo menos 3 caracteres.", "erro")
            return

        if not valor_str:
            self.mostrar_mensagem("O valor é obrigatório.", "erro")
            return

        try:
            valor_num = float(valor_str.replace(",", ".").replace("R$", "").strip())
            if valor_num <= 0:
                self.mostrar_mensagem("O valor deve ser maior que zero.", "erro")
                return
        except ValueError:
            self.mostrar_mensagem("Digite um valor numérico válido.", "erro")
            return

        if not categoria:
            self.mostrar_mensagem("A categoria é obrigatória.", "erro")
            return

        if not data_vencimento:
            self.mostrar_mensagem("A data é obrigatória.", "erro")
            return

        try:
            data_dt = datetime.strptime(data_vencimento, "%d/%m/%Y")
            data_iso = data_dt.strftime("%Y-%m-%d")
        except ValueError:
            self.mostrar_mensagem("Use o formato DD/MM/AAAA para a data.", "erro")
            return

        tipo_banco = "Receita" if tipo == "RECEITA" else "Despesa"

        try:
            self.dao.inserir(
                descricao=descricao,
                valor=valor_num,
                tipo=tipo_banco,
                categoria=categoria,
                data=data_iso,
            )
            self.mostrar_mensagem("✓ Lançamento salvo com sucesso!", "sucesso")
            self._limpar_campos()
            self.atualizar_dados()
            try:
                notif = GerenciadorNotificacoes.obter_instancia()
                if notif:
                    notif.sucesso(f"Lançamento '{descricao}' salvo!")
            except Exception:
                pass
        except Exception as e:
            self.mostrar_mensagem(f"Erro ao salvar: {e}", "erro")
            try:
                notif = GerenciadorNotificacoes.obter_instancia()
                if notif:
                    notif.erro(f"Erro ao salvar lançamento: {e}")
            except Exception:
                pass

    def _excluir_lancamento(self, lancamento_id: int):
        self.dao.excluir(lancamento_id)
        self.atualizar_dados()
        try:
            notif = GerenciadorNotificacoes.obter_instancia()
            if notif:
                notif.sucesso("Lançamento excluído!")
        except Exception:
            pass

    def mostrar_mensagem(self, texto, tipo):
        self.mensagem.configure(text=texto)
        cor = COR_ALERTA if tipo == "erro" else COR_SUCESSO
        self.mensagem.configure(text_color=cor)

    def _limpar_campos(self):
        self.descricao.delete(0, "end")
        self.valor.delete(0, "end")
        self.data_vencimento.delete(0, "end")
        self.data_vencimento.insert(0, date.today().strftime("%d/%m/%Y"))
        if self.tipo_selecionado == "RECEITA":
            self.status.set("RECEBIDO")
        else:
            self.status.set("PAGO")

    # ==========================================================
    # ATUALIZAÇÃO GERAL E SINCRONIZAÇÃO
    # ==========================================================
    def atualizar_dados(self):
        """Atualiza saldos, listas e opções dinâmicas dos ComboBoxes."""
        lancamentos = self.dao.listar_todos()

        # Calcula Totais
        total_rec = sum(l["value"] for l in lancamentos if l["type"] == "Receita")
        total_desp = sum(l["value"] for l in lancamentos if l["type"] == "Despesa")
        saldo = total_rec - total_desp

        self.lbl_total_receitas.configure(text=f"R$ {total_rec:.2f}")
        self.lbl_total_despesas.configure(text=f"R$ {total_desp:.2f}")

        cor_saldo = COR_RECEITA if saldo >= 0 else COR_DESPESA
        sinal = "+" if saldo > 0 else ""
        self.lbl_saldo.configure(text=f"{sinal}R$ {saldo:.2f}", text_color=cor_saldo)

        # Atualiza opções de Categorias filtradas pelo tipo ativo (Receita / Despesa)
        self._atualizar_categorias_por_tipo(self.tipo_selecionado)

        # Atualiza opções de Terceiros do TerceiroDAO
        try:
            terceiros = self.ter_dao.listar_todos()
            nomes_ter = ["Nenhum"] + [t["nome"] for t in terceiros] if terceiros else ["Nenhum"]
            self.terceiro.configure(values=nomes_ter)
            if self.terceiro.get() not in nomes_ter:
                self.terceiro.set(nomes_ter[0])
        except Exception:
            pass

        # Filtra os lançamentos para exibição
        filtrados = lancamentos
        if self.filtro_tipo == "Receitas":
            filtrados = [l for l in filtrados if l["type"] == "Receita"]
        elif self.filtro_tipo == "Despesas":
            filtrados = [l for l in filtrados if l["type"] == "Despesa"]

        if self.busca_texto:
            filtrados = [
                l
                for l in filtrados
                if self.busca_texto in l["description"].lower()
                or self.busca_texto in l["category"].lower()
            ]

        self.lbl_qtd_lancamentos.configure(
            text=f"Lançamentos Recentes ({len(filtrados)})"
        )

        # Renderiza a lista
        for w in self.scroll_lancamentos.winfo_children():
            w.destroy()

        if not filtrados:
            ctk.CTkLabel(
                self.scroll_lancamentos,
                text="Nenhum lançamento encontrado.",
                font=fonte_corpo(),
                text_color=COR_TEXTO_TERCIARIO,
            ).pack(pady=40)
            return

        # Renderiza em ordem decrescente de data/id
        for l in reversed(filtrados):
            self._renderizar_card_lancamento(l)

    def _renderizar_card_lancamento(self, l: dict):
        card = ctk.CTkFrame(
            self.scroll_lancamentos,
            fg_color=COR_CARD_INTERNO,
            corner_radius=10,
            border_width=1,
            border_color=COR_BORDA,
        )
        card.pack(fill="x", padx=4, pady=4)
        card.grid_columnconfigure(1, weight=1)

        eh_rec = l["type"] == "Receita"
        cor_val = COR_RECEITA if eh_rec else COR_DESPESA
        sinal = "+" if eh_rec else "-"
        icone = "↑" if eh_rec else "↓"
        bg_ico = COR_RECEITA_BG if eh_rec else COR_DESPESA_BG

        # Ícone de Tipo
        ico_frame = ctk.CTkFrame(card, fg_color=bg_ico, corner_radius=6, width=32, height=32)
        ico_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=8)
        ico_frame.grid_propagate(False)
        ctk.CTkLabel(
            ico_frame,
            text=icone,
            font=fonte(14, "bold"),
            text_color=cor_val,
        ).pack(expand=True)

        # Descrição e detalhes
        ctk.CTkLabel(
            card,
            text=l["description"],
            font=fonte(13, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        ).grid(row=0, column=1, sticky="w", pady=(6, 0))

        # Data formatada para DD/MM/AAAA
        data_exibicao = l["date"]
        try:
            data_exibicao = datetime.strptime(l["date"], "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            pass

        info_detalhe = f"{l['category']}  •  {data_exibicao}"
        ctk.CTkLabel(
            card,
            text=info_detalhe,
            font=fonte_pequena(),
            text_color=COR_TEXTO_TERCIARIO,
            anchor="w",
        ).grid(row=1, column=1, sticky="w", pady=(0, 6))

        # Valor
        ctk.CTkLabel(
            card,
            text=f"{sinal}R$ {l['value']:.2f}",
            font=fonte(13, "bold"),
            text_color=cor_val,
        ).grid(row=0, column=2, rowspan=2, padx=8)

        # Botão Excluir
        btn_del = ctk.CTkButton(
            card,
            text="✕",
            width=26,
            height=26,
            fg_color="transparent",
            hover_color=COR_EXCLUIR_HOVER,
            text_color=COR_EXCLUIR_TEXTO,
            font=fonte(11, "bold"),
            command=lambda lid=l["id"]: self._excluir_lancamento(lid),
        )
        btn_del.grid(row=0, column=3, rowspan=2, padx=(0, 8))


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Testando LancamentoView")
    app.geometry("1050x650")
    view = LancamentoView(app)
    view.pack(expand=True, fill="both", padx=20, pady=20)
    app.mainloop()