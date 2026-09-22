import customtkinter as ctk
from typing import Optional
from dao.categoria_dao import CategoriaDAO
from views.notificacao_toast import GerenciadorNotificacoes
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_ACENTO_HOVER, COR_SUCESSO, COR_ALERTA,
    COR_RECEITA, COR_RECEITA_BG, COR_DESPESA, COR_DESPESA_BG,
    COR_BOTAO_SECUNDARIO, COR_BOTAO_SECUNDARIO_HOVER,
    COR_EXCLUIR_HOVER, COR_EXCLUIR_TEXTO,
    fonte, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
)


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
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
        )
        card_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        titulo = ctk.CTkLabel(
            card_form,
            text="🏷️  NOVA CATEGORIA",
            font=fonte_subtitulo(),
            text_color=COR_TEXTO_SECUNDARIO,
        )
        titulo.pack(anchor="w", padx=20, pady=(20, 15))

        # Campo Nome
        ctk.CTkLabel(
            card_form, text="Nome da Categoria:", font=fonte_corpo()
        ).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_nome = ctk.CTkEntry(
            card_form,
            placeholder_text="Ex: Alimentação, Lazer, Salário...",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            font=fonte_corpo(),
        )
        self.entry_nome.pack(fill="x", padx=20, pady=(0, 10))

        # Tipo
        ctk.CTkLabel(card_form, text="Tipo:", font=fonte_corpo()).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.combo_tipo = ctk.CTkComboBox(
            card_form,
            values=["Despesa", "Receita"],
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            button_color=COR_BOTAO_SECUNDARIO,
            font=fonte_corpo(),
        )
        self.combo_tipo.set("Despesa")
        self.combo_tipo.pack(fill="x", padx=20, pady=(0, 10))

        # Contexto de Uso (antes: Escopo)
        ctk.CTkLabel(card_form, text="Contexto de Uso:", font=fonte_corpo()).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.combo_escopo = ctk.CTkComboBox(
            card_form,
            values=["Pessoal", "Empresarial", "Familiar", "Outros"],
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            button_color=COR_BOTAO_SECUNDARIO,
            font=fonte_corpo(),
        )
        self.combo_escopo.set("Pessoal")
        self.combo_escopo.pack(fill="x", padx=20, pady=(0, 10))

        # Limite de Orçamento
        ctk.CTkLabel(
            card_form,
            text="Limite de Orçamento (R$/mês):",
            font=fonte_corpo(),
        ).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_limite = ctk.CTkEntry(
            card_form,
            placeholder_text="0.00",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            font=fonte_corpo(),
        )
        self.entry_limite.pack(fill="x", padx=20, pady=(0, 4))

        # Hint do campo limite
        ctk.CTkLabel(
            card_form,
            text="💡 Deixe 0 para sem limite de orçamento",
            font=fonte_hint(),
            text_color=COR_TEXTO_MUTED,
            anchor="w",
        ).pack(anchor="w", padx=20, pady=(0, 12))

        # Mensagem de Feedback
        self.lbl_feedback = ctk.CTkLabel(
            card_form,
            text="",
            font=fonte(12, "bold"),
        )
        self.lbl_feedback.pack(fill="x", padx=20, pady=(0, 10))

        # Botão Salvar
        btn_salvar = ctk.CTkButton(
            card_form,
            text="Adicionar Categoria",
            fg_color=COR_ACENTO_PRIMARIO,
            text_color="#0B1D1F",
            hover_color=COR_ACENTO_HOVER,
            font=fonte(13, "bold"),
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
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
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
            font=fonte_subtitulo(),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        )
        self.lbl_total_categorias.grid(row=0, column=0, sticky="w")

        # Botão Categorias Sugeridas (ao lado do título)
        btn_padrao = ctk.CTkButton(
            header,
            text="⚡ Sugeridas",
            width=90,
            height=28,
            font=fonte(11, "bold"),
            fg_color=COR_BOTAO_SECUNDARIO,
            hover_color=COR_BOTAO_SECUNDARIO_HOVER,
            text_color=COR_ACENTO_PRIMARIO,
            command=self._inserir_categorias_padrao,
        )
        btn_padrao.grid(row=0, column=1, sticky="e", padx=(8, 0))

        # Filtro segmentado — linha separada do título
        self.filtro_btn = ctk.CTkSegmentedButton(
            header,
            values=["Todas", "Despesas", "Receitas"],
            command=self._alterar_filtro,
            selected_color=COR_BOTAO_SECUNDARIO,
            selected_hover_color=COR_BOTAO_SECUNDARIO_HOVER,
        )
        self.filtro_btn.set("Todas")
        self.filtro_btn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        # Barra de busca por texto
        self.entry_busca = ctk.CTkEntry(
            card_lista,
            placeholder_text="🔍 Buscar categoria pelo nome...",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            font=fonte_corpo(),
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
            self._mostrar_feedback("O nome da categoria é obrigatório!", COR_ALERTA)
            return

        limite = 0.0
        if limite_str:
            try:
                limite = float(limite_str)
                if limite < 0:
                    self._mostrar_feedback("O limite não pode ser negativo!", COR_ALERTA)
                    return
            except ValueError:
                self._mostrar_feedback("Digite um valor de limite válido!", COR_ALERTA)
                return

        try:
            self.dao.inserir(
                nome=nome,
                tipo=tipo,
                escopo=escopo,
                limite_orcamento=limite,
            )
            self._mostrar_feedback(f"✓ Categoria '{nome}' criada!", COR_SUCESSO)
            self.entry_nome.delete(0, "end")
            self.entry_limite.delete(0, "end")
            try:
                notif = GerenciadorNotificacoes.obter_instancia()
                if notif:
                    notif.sucesso(f"Categoria '{nome}' cadastrada!")
            except Exception:
                pass
        except Exception as e:
            self._mostrar_feedback(f"Erro ao salvar: {e}", COR_ALERTA)
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
            self._mostrar_feedback(f"✓ {inseridas} categorias sugeridas adicionadas!", COR_SUCESSO)
        else:
            self._mostrar_feedback("As categorias sugeridas já existem!", COR_ACENTO_PRIMARIO)
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
                font=fonte_corpo(),
                text_color=COR_TEXTO_TERCIARIO,
                justify="center",
            ).pack(pady=40)
            return

        for cat in categorias:
            self._renderizar_card_categoria(cat)

    def _renderizar_card_categoria(self, cat: dict):
        card = ctk.CTkFrame(
            self.scroll_cards,
            fg_color=COR_CARD_INTERNO,
            corner_radius=10,
            border_width=1,
            border_color=COR_BORDA,
        )
        card.pack(fill="x", padx=5, pady=5)
        card.grid_columnconfigure(1, weight=1)

        # Cor do badge por tipo
        cor_tipo = COR_RECEITA if cat["tipo"] == "Receita" else COR_DESPESA
        bg_badge = COR_RECEITA_BG if cat["tipo"] == "Receita" else COR_DESPESA_BG

        # Badge do tipo
        badge_frame = ctk.CTkFrame(card, fg_color=bg_badge, corner_radius=6)
        badge_frame.grid(row=0, column=0, rowspan=2, padx=12, pady=12)
        ctk.CTkLabel(
            badge_frame,
            text=cat["tipo"].upper(),
            font=fonte(10, "bold"),
            text_color=cor_tipo,
        ).pack(padx=8, pady=4)

        # Nome
        ctk.CTkLabel(
            card,
            text=cat["nome"],
            font=fonte(14, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        ).grid(row=0, column=1, sticky="w", pady=(8, 0))

        # Detalhes: contexto + teto
        info_detalhes = f"Contexto: {cat.get('escopo', 'Pessoal')}"
        if cat.get("limite_orcamento", 0) > 0:
            info_detalhes += f"  •  Teto: R$ {cat['limite_orcamento']:.2f}/mês"

        ctk.CTkLabel(
            card,
            text=info_detalhes,
            font=fonte_pequena(),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).grid(row=1, column=1, sticky="w", pady=(0, 8))

        # Botão excluir
        btn_del = ctk.CTkButton(
            card,
            text="🗑️",
            width=32,
            height=32,
            fg_color="transparent",
            hover_color=COR_EXCLUIR_HOVER,
            text_color=COR_EXCLUIR_TEXTO,
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
