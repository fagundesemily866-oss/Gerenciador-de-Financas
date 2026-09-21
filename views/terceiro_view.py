import customtkinter as ctk
from datetime import datetime
from typing import Optional
from dao.terceiro_dao import TerceiroDAO
from views.notificacao_toast import GerenciadorNotificacoes


class TerceiroView(ctk.CTkFrame):
    """Tela de gerenciamento de Terceiros (contatos, fornecedores, clientes)."""

    def __init__(self, parent, dao: Optional[TerceiroDAO] = None):
        super().__init__(parent, fg_color="transparent")
        self.dao = dao or TerceiroDAO()
        self.filtro_relacao = "Todos"
        self.busca_texto = ""

        # Grid principal: 2 colunas
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._criar_painel_formulario()
        self._criar_painel_lista()
        self.atualizar_dados()

    # ==========================================================
    # FORMULÁRIO (ESQUERDA)
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
            text="🤝  NOVO TERCEIRO",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#A6ADC8",
        )
        titulo.pack(anchor="w", padx=20, pady=(20, 15))

        # Nome
        ctk.CTkLabel(card_form, text="Nome ou Razão Social:", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.entry_nome = ctk.CTkEntry(
            card_form,
            placeholder_text="Ex: Supermercado BH, João Silva...",
            fg_color="#181825",
            border_color="#313244",
        )
        self.entry_nome.pack(fill="x", padx=20, pady=(0, 10))

        # Relação
        ctk.CTkLabel(card_form, text="Relação / Vínculo:", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.combo_relacao = ctk.CTkComboBox(
            card_form,
            values=[
                "Fornecedor",
                "Cliente",
                "Prestador de Serviços",
                "Familiar",
                "Amigo",
                "Outros",
            ],
            fg_color="#181825",
            border_color="#313244",
            button_color="#313244",
        )
        self.combo_relacao.set("Fornecedor")
        self.combo_relacao.pack(fill="x", padx=20, pady=(0, 15))

        # Feedback
        self.lbl_feedback = ctk.CTkLabel(
            card_form,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.lbl_feedback.pack(fill="x", padx=20, pady=(0, 10))

        # Botão Salvar
        btn_salvar = ctk.CTkButton(
            card_form,
            text="Adicionar Terceiro",
            fg_color="#CBA6F7",
            text_color="#1E1E2E",
            hover_color="#B48EAD",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._salvar_terceiro,
        )
        btn_salvar.pack(fill="x", padx=20, pady=(0, 20))

    # ==========================================================
    # LISTA (DIREITA)
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

        # Header: título + filtro por relação
        header = ctk.CTkFrame(card_lista, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 6))
        header.grid_columnconfigure(0, weight=1)

        self.lbl_total_terceiros = ctk.CTkLabel(
            header,
            text="Terceiros Cadastrados",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#CDD6F4",
            anchor="w",
        )
        self.lbl_total_terceiros.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        # Filtro por relação — linha separada
        self.filtro_btn = ctk.CTkSegmentedButton(
            header,
            values=["Todos", "Fornecedor", "Cliente", "Familiar"],
            command=self._alterar_filtro,
            selected_color="#313244",
            selected_hover_color="#45475A",
        )
        self.filtro_btn.set("Todos")
        self.filtro_btn.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Barra de busca por texto
        self.entry_busca = ctk.CTkEntry(
            card_lista,
            placeholder_text="🔍 Buscar por nome ou relação...",
            fg_color="#181825",
            border_color="#313244",
        )
        self.entry_busca.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 8))
        self.entry_busca.bind("<KeyRelease>", lambda e: self._filtrar_busca())

        # ScrollFrame para os cards
        self.scroll_terceiros = ctk.CTkScrollableFrame(
            card_lista,
            fg_color="transparent",
            corner_radius=10,
        )
        self.scroll_terceiros.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.scroll_terceiros.grid_columnconfigure(0, weight=1)

    # ==========================================================
    # AÇÕES
    # ==========================================================
    def _alterar_filtro(self, valor):
        self.filtro_relacao = valor
        self.atualizar_dados()

    def _filtrar_busca(self):
        self.busca_texto = self.entry_busca.get().strip().lower()
        self.atualizar_dados()

    def _salvar_terceiro(self):
        nome = self.entry_nome.get().strip()
        relacao = self.combo_relacao.get()

        if not nome:
            self._mostrar_feedback("O nome é obrigatório!", "#F38BA8")
            return

        try:
            self.dao.inserir(nome=nome, relacao=relacao)
            self._mostrar_feedback(f"✓ '{nome}' cadastrado!", "#A6E3A1")
            self.entry_nome.delete(0, "end")
            self.atualizar_dados()
            notif = GerenciadorNotificacoes.obter_instancia()
            if notif:
                notif.sucesso(f"Terceiro '{nome}' cadastrado!")
        except Exception as e:
            self._mostrar_feedback(f"Erro ao salvar: {e}", "#F38BA8")
            notif = GerenciadorNotificacoes.obter_instancia()
            if notif:
                notif.erro(f"Erro ao salvar terceiro: {e}")

    def _mostrar_feedback(self, texto: str, cor: str):
        self.lbl_feedback.configure(text=texto, text_color=cor)

    def _excluir_terceiro(self, terceiro_id: int):
        self.dao.excluir(terceiro_id)
        self.atualizar_dados()
        notif = GerenciadorNotificacoes.obter_instancia()
        if notif:
            notif.sucesso("Terceiro excluído com sucesso!")

    def atualizar_dados(self):
        """Recarrega os terceiros cadastrados no banco."""
        for widget in self.scroll_terceiros.winfo_children():
            widget.destroy()

        terceiros = self.dao.listar_todos()

        # Filtro por relação
        if self.filtro_relacao != "Todos":
            terceiros = [
                t for t in terceiros
                if self.filtro_relacao.lower() in t["relacao"].lower()
            ]

        # Filtro por busca de texto
        if self.busca_texto:
            terceiros = [
                t for t in terceiros
                if self.busca_texto in t["nome"].lower()
                or self.busca_texto in t["relacao"].lower()
            ]

        self.lbl_total_terceiros.configure(
            text=f"Terceiros Cadastrados ({len(terceiros)})"
        )

        if not terceiros:
            msg = (
                "Nenhum terceiro cadastrado.\nAdicione clientes, fornecedores ou contatos!"
                if not self.busca_texto and self.filtro_relacao == "Todos"
                else "Nenhum resultado para o filtro aplicado."
            )
            ctk.CTkLabel(
                self.scroll_terceiros,
                text=msg,
                font=ctk.CTkFont(size=13),
                text_color="#6C7086",
                justify="center",
            ).pack(pady=40)
            return

        for t in terceiros:
            self._renderizar_card(t)

    def _renderizar_card(self, t: dict):
        card = ctk.CTkFrame(
            self.scroll_terceiros,
            fg_color="#181825",
            corner_radius=10,
            border_width=1,
            border_color="#313244",
        )
        card.pack(fill="x", padx=5, pady=5)
        card.grid_columnconfigure(1, weight=1)

        # Badge com relação
        badge = ctk.CTkFrame(card, fg_color="#313244", corner_radius=6)
        badge.grid(row=0, column=0, rowspan=2, padx=12, pady=10)
        ctk.CTkLabel(
            badge,
            text=t["relacao"].upper(),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#89B4FA",
        ).pack(padx=8, pady=4)

        # Nome
        ctk.CTkLabel(
            card,
            text=t["nome"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#CDD6F4",
            anchor="w",
        ).grid(row=0, column=1, sticky="w", pady=(8, 0))

        # Data de criação formatada
        data_raw = t.get("data_criacao", "-")
        try:
            data_formatada = datetime.strptime(data_raw, "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            data_formatada = data_raw

        ctk.CTkLabel(
            card,
            text=f"Cadastrado em: {data_formatada}",
            font=ctk.CTkFont(size=11),
            text_color="#6C7086",
            anchor="w",
        ).grid(row=1, column=1, sticky="w", pady=(0, 8))

        # Botão Excluir
        btn_del = ctk.CTkButton(
            card,
            text="🗑️",
            width=32,
            height=32,
            fg_color="transparent",
            hover_color="#3E2633",
            text_color="#F38BA8",
            command=lambda tid=t["id"]: self._excluir_terceiro(tid),
        )
        btn_del.grid(row=0, column=2, rowspan=2, padx=12, pady=8)


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Testando TerceiroView")
    app.geometry("950x600")
    view = TerceiroView(app)
    view.pack(expand=True, fill="both", padx=20, pady=20)
    app.mainloop()
