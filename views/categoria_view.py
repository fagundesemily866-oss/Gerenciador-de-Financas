import customtkinter as ctk
from typing import Optional
from dao.categoria_dao import CategoriaDAO
from views.notificacao_toast import GerenciadorNotificacoes


class CategoriaView(ctk.CTkFrame):
    """Tela de gerenciamento de Categorias."""

    def __init__(self, parent, dao: Optional[CategoriaDAO] = None):
        super().__init__(parent, fg_color="transparent")
        self.dao = dao or CategoriaDAO()
        self.filtro_tipo = "Todas"
        self.busca_texto = ""

        # Grid principal: 2 colunas proporcionais
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._criar_painel_formulario()
        self._criar_painel_lista()
        self.atualizar_dados()

    # ==========================================================
    # PAINEL DE FORMULÁRIO (ESQUERDA)
    # ==========================================================
    def _criar_painel_formulario(self):
        card_form = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        card_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        titulo = ctk.CTkLabel(
            card_form,
            text="🏷️  NOVA CATEGORIA",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#A6ADC8",
        )
        titulo.pack(anchor="w", padx=20, pady=(20, 15))

        # Campo Nome
        ctk.CTkLabel(
            card_form, text="Nome da Categoria:", font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_nome = ctk.CTkEntry(
            card_form,
            placeholder_text="Ex: Alimentação, Lazer, Salário...",
            fg_color="#181825",
            border_color="#313244",
        )
        self.entry_nome.pack(fill="x", padx=20, pady=(0, 10))

        # Tipo
        ctk.CTkLabel(card_form, text="Tipo:", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.combo_tipo = ctk.CTkComboBox(
            card_form,
            values=["Despesa", "Receita"],
            fg_color="#181825",
            border_color="#313244",
            button_color="#313244",
        )
        self.combo_tipo.set("Despesa")
        self.combo_tipo.pack(fill="x", padx=20, pady=(0, 10))

        # Contexto de Uso (antes: Escopo)
        ctk.CTkLabel(card_form, text="Contexto de Uso:", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.combo_escopo = ctk.CTkComboBox(
            card_form,
            values=["Pessoal", "Empresarial", "Familiar", "Outros"],
            fg_color="#181825",
            border_color="#313244",
            button_color="#313244",
        )
        self.combo_escopo.set("Pessoal")
        self.combo_escopo.pack(fill="x", padx=20, pady=(0, 10))

        # Limite de Orçamento
        ctk.CTkLabel(
            card_form,
            text="Limite de Orçamento (R$/mês):",
            font=ctk.CTkFont(size=13),
        ).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_limite = ctk.CTkEntry(
            card_form,
            placeholder_text="0.00",
            fg_color="#181825",
            border_color="#313244",
        )
        self.entry_limite.pack(fill="x", padx=20, pady=(0, 4))

        # Hint do campo limite
        ctk.CTkLabel(
            card_form,
            text="💡 Deixe 0 para sem limite de orçamento",
            font=ctk.CTkFont(size=10),
            text_color="#585B70",
            anchor="w",
        ).pack(anchor="w", padx=20, pady=(0, 12))

        # Mensagem de Feedback
        self.lbl_feedback = ctk.CTkLabel(
            card_form,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.lbl_feedback.pack(fill="x", padx=20, pady=(0, 10))

        # Botão Salvar
        btn_salvar = ctk.CTkButton(
            card_form,
            text="Adicionar Categoria",
            fg_color="#89B4FA",
            text_color="#1E1E2E",
            hover_color="#74A0E8",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._salvar_categoria,
        )
        btn_salvar.pack(fill="x", padx=20, pady=(0, 20))

    # ==========================================================
    # PAINEL DE LISTA (DIREITA)
    # ==========================================================
    def _criar_painel_lista(self):
        card_lista = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        card_lista.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        card_lista.grid_columnconfigure(0, weight=1)
        card_lista.grid_rowconfigure(2, weight=1)

        # Header: título + botão sugeridas (linha 0)
        header = ctk.CTkFrame(card_lista, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 6))
        header.grid_columnconfigure(0, weight=1)

        self.lbl_total_categorias = ctk.CTkLabel(
            header,
            text="Categorias Cadastradas",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#CDD6F4",
            anchor="w",
        )
        self.lbl_total_categorias.grid(row=0, column=0, sticky="w")

        # Botão Categorias Sugeridas (ao lado do título)
        btn_padrao = ctk.CTkButton(
            header,
            text="⚡ Sugeridas",
            width=90,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#313244",
            hover_color="#45475A",
            text_color="#89B4FA",
            command=self._inserir_categorias_padrao,
        )
        btn_padrao.grid(row=0, column=1, sticky="e", padx=(8, 0))

        # Filtro segmentado — linha separada do título
        self.filtro_btn = ctk.CTkSegmentedButton(
            header,
            values=["Todas", "Despesas", "Receitas"],
            command=self._alterar_filtro,
            selected_color="#313244",
            selected_hover_color="#45475A",
        )
        self.filtro_btn.set("Todas")
        self.filtro_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        # Barra de busca por texto
        self.entry_busca = ctk.CTkEntry(
            card_lista,
            placeholder_text="🔍 Buscar categoria pelo nome...",
            fg_color="#181825",
            border_color="#313244",
        )
        self.entry_busca.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 8))
        self.entry_busca.bind("<KeyRelease>", lambda e: self._filtrar_busca())

        # ScrollFrame para os cards
        self.scroll_cards = ctk.CTkScrollableFrame(
            card_lista,
            fg_color="transparent",
            corner_radius=10,
        )
        self.scroll_cards.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.scroll_cards.grid_columnconfigure(0, weight=1)

    # ==========================================================
    # AÇÕES
    # ==========================================================
    def _alterar_filtro(self, valor):
        self.filtro_tipo = valor
        self.atualizar_dados()

    def _filtrar_busca(self):
        self.busca_texto = self.entry_busca.get().strip().lower()
        self.atualizar_dados()

    def _salvar_categoria(self):
        nome = self.entry_nome.get().strip()
        tipo = self.combo_tipo.get()
        escopo = self.combo_escopo.get()
        limite_str = self.entry_limite.get().strip().replace(",", ".")

        if not nome:
            self._mostrar_feedback("O nome da categoria é obrigatório!", "#F38BA8")
            return

        limite = 0.0
        if limite_str:
            try:
                limite = float(limite_str)
                if limite < 0:
                    self._mostrar_feedback("O limite não pode ser negativo!", "#F38BA8")
                    return
            except ValueError:
                self._mostrar_feedback("Digite um valor de limite válido!", "#F38BA8")
                return

        try:
            self.dao.inserir(
                nome=nome,
                tipo=tipo,
                escopo=escopo,
                limite_orcamento=limite,
            )
            self._mostrar_feedback(f"✓ Categoria '{nome}' criada!", "#A6E3A1")
            self.entry_nome.delete(0, "end")
            self.entry_limite.delete(0, "end")
            try:
                notif = GerenciadorNotificacoes.obter_instancia()
                if notif:
                    notif.sucesso(f"Categoria '{nome}' cadastrada!")
            except Exception:
                pass
        except Exception as e:
            self._mostrar_feedback(f"Erro ao salvar: {e}", "#F38BA8")
            try:
                notif = GerenciadorNotificacoes.obter_instancia()
                if notif:
                    notif.erro(f"Erro ao salvar categoria: {e}")
            except Exception:
                pass

    def _inserir_categorias_padrao(self):
        padroes = [
            ("Alimentação", "Despesa", "Pessoal", 800.0),
            ("Transporte", "Despesa", "Pessoal", 350.0),
            ("Moradia", "Despesa", "Pessoal", 1200.0),
            ("Salário", "Receita", "Pessoal", 0.0),
            ("Lazer", "Despesa", "Pessoal", 300.0),
            ("Saúde", "Despesa", "Pessoal", 250.0),
            ("Educação", "Despesa", "Pessoal", 200.0),
            ("Rendimentos", "Receita", "Pessoal", 0.0),
        ]
        existentes = {c["nome"].upper() for c in self.dao.listar_todas()}
        inseridas = 0
        for nome, tipo, escopo, limite in padroes:
            if nome.upper() not in existentes:
                self.dao.inserir(nome=nome, tipo=tipo, escopo=escopo, limite_orcamento=limite)
                inseridas += 1

        if inseridas > 0:
            self._mostrar_feedback(f"✓ {inseridas} categorias sugeridas adicionadas!", "#A6E3A1")
        else:
            self._mostrar_feedback("As categorias sugeridas já existem!", "#89B4FA")
        self.atualizar_dados()

    def _mostrar_feedback(self, texto: str, cor: str):
        self.lbl_feedback.configure(text=texto, text_color=cor)

    def _excluir_categoria(self, categoria_id: int):
        self.dao.excluir(categoria_id)
        self.atualizar_dados()
        notif = GerenciadorNotificacoes.obter_instancia()
        if notif:
            notif.sucesso("Categoria excluída com sucesso!")

    def atualizar_dados(self):
        """Recarrega a lista de categorias do banco de dados."""
        for widget in self.scroll_cards.winfo_children():
            widget.destroy()

        if self.filtro_tipo == "Despesas":
            categorias = self.dao.listar_por_tipo("Despesa")
        elif self.filtro_tipo == "Receitas":
            categorias = self.dao.listar_por_tipo("Receita")
        else:
            categorias = self.dao.listar_todas()

        # Aplicar busca por texto
        if self.busca_texto:
            categorias = [c for c in categorias if self.busca_texto in c["nome"].lower()]

        self.lbl_total_categorias.configure(
            text=f"Categorias Cadastradas ({len(categorias)})"
        )

        if not categorias:
            msg = (
                "Nenhuma categoria encontrada.\nCadastre a primeira no formulário ao lado!"
                if not self.busca_texto
                else f"Nenhum resultado para '{self.busca_texto}'."
            )
            ctk.CTkLabel(
                self.scroll_cards,
                text=msg,
                font=ctk.CTkFont(size=13),
                text_color="#6C7086",
                justify="center",
            ).pack(pady=40)
            return

        for cat in categorias:
            self._renderizar_card_categoria(cat)

    def _renderizar_card_categoria(self, cat: dict):
        card = ctk.CTkFrame(
            self.scroll_cards,
            fg_color="#181825",
            corner_radius=10,
            border_width=1,
            border_color="#313244",
        )
        card.pack(fill="x", padx=5, pady=5)
        card.grid_columnconfigure(1, weight=1)

        # Cor do badge por tipo
        cor_tipo = "#A6E3A1" if cat["tipo"] == "Receita" else "#F38BA8"
        bg_badge = "#2A3831" if cat["tipo"] == "Receita" else "#3E2633"

        # Badge do tipo
        badge_frame = ctk.CTkFrame(card, fg_color=bg_badge, corner_radius=6)
        badge_frame.grid(row=0, column=0, rowspan=2, padx=12, pady=12)
        ctk.CTkLabel(
            badge_frame,
            text=cat["tipo"].upper(),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=cor_tipo,
        ).pack(padx=8, pady=4)

        # Nome
        ctk.CTkLabel(
            card,
            text=cat["nome"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#CDD6F4",
            anchor="w",
        ).grid(row=0, column=1, sticky="w", pady=(8, 0))

        # Detalhes: contexto + teto
        info_detalhes = f"Contexto: {cat.get('escopo', 'Pessoal')}"
        if cat.get("limite_orcamento", 0) > 0:
            info_detalhes += f"  •  Teto: R$ {cat['limite_orcamento']:.2f}/mês"

        ctk.CTkLabel(
            card,
            text=info_detalhes,
            font=ctk.CTkFont(size=11),
            text_color="#A6ADC8",
            anchor="w",
        ).grid(row=1, column=1, sticky="w", pady=(0, 8))

        # Botão excluir
        btn_del = ctk.CTkButton(
            card,
            text="🗑️",
            width=32,
            height=32,
            fg_color="transparent",
            hover_color="#3E2633",
            text_color="#F38BA8",
            command=lambda cid=cat["id"]: self._excluir_categoria(cid),
        )
        btn_del.grid(row=0, column=2, rowspan=2, padx=12, pady=8)


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Testando CategoriaView")
    app.geometry("950x600")
    view = CategoriaView(app)
    view.pack(expand=True, fill="both", padx=20, pady=20)
    app.mainloop()
