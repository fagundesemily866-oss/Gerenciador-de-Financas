import customtkinter as ctk
from datetime import datetime

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class LancamentoView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)

        self._criar_titulo()
        self._criar_formulario()

    def _criar_titulo(self):
        titulo = ctk.CTkLabel(
            self,
            text="LANÇAMENTOS",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        titulo.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

    def _criar_formulario(self):
        frame = ctk.CTkFrame(
            self,
            corner_radius=15
        )
        frame.grid(
            row=1,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame,
            text="Descrição:"
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.descricao = ctk.CTkEntry(
            frame,
            placeholder_text="Digite a descrição"
        )
        self.descricao.grid(row=0, column=1, padx=15, pady=10, sticky="ew")

        ctk.CTkLabel(
            frame,
            text="Valor:"
        ).grid(row=1, column=0, padx=15, pady=10, sticky="w")

        self.valor = ctk.CTkEntry(
            frame,
            placeholder_text="Ex: 150.00"
        )
        self.valor.grid(row=1, column=1, padx=15, pady=10, sticky="ew")

        ctk.CTkLabel(
            frame,
            text="Tipo:"
        ).grid(row=2, column=0, padx=15, pady=10, sticky="w")

        self.tipo = ctk.CTkComboBox(
            frame,
            values=["RECEITA", "DESPESA"]
        )
        self.tipo.set("RECEITA")
        self.tipo.grid(row=2, column=1, padx=15, pady=10, sticky="ew")

        ctk.CTkLabel(
            frame,
            text="Categoria:"
        ).grid(row=3, column=0, padx=15, pady=10, sticky="w")

        self.categoria = ctk.CTkEntry(
            frame,
            placeholder_text="Digite a categoria"
        )
        self.categoria.grid(row=3, column=1, padx=15, pady=10, sticky="ew")

        ctk.CTkLabel(
            frame,
            text="Terceiro:"
        ).grid(row=4, column=0, padx=15, pady=10, sticky="w")

        self.terceiro = ctk.CTkEntry(
            frame,
            placeholder_text="Opcional"
        )
        self.terceiro.grid(row=4, column=1, padx=15, pady=10, sticky="ew")

        ctk.CTkLabel(
            frame,
            text="Status:"
        ).grid(row=5, column=0, padx=15, pady=10, sticky="w")

        self.status = ctk.CTkComboBox(
            frame,
            values=["PAGO", "PENDENTE"]
        )
        self.status.set("PENDENTE")
        self.status.grid(row=5, column=1, padx=15, pady=10, sticky="ew")

        ctk.CTkLabel(
            frame,
            text="Vencimento:"
        ).grid(row=6, column=0, padx=15, pady=10, sticky="w")

        self.data_vencimento = ctk.CTkEntry(
            frame,
            placeholder_text="DD/MM/AAAA"
        )
        self.data_vencimento.grid(row=6, column=1, padx=15, pady=10, sticky="ew")

        self.mensagem = ctk.CTkLabel(
            frame,
            text="",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.mensagem.grid(
            row=7,
            column=0,
            columnspan=2,
            padx=15,
            pady=(10, 5)
        )

        botao = ctk.CTkButton(
            frame,
            text="Salvar lançamento",
            command=self.salvar_lancamento
        )
        botao.grid(
            row=8,
            column=0,
            columnspan=2,
            padx=15,
            pady=(10, 20)
        )

    def salvar_lancamento(self):
        descricao = self.descricao.get().strip()
        valor = self.valor.get().strip()
        tipo = self.tipo.get()
        categoria = self.categoria.get().strip()
        data_vencimento = self.data_vencimento.get().strip()

        if not descricao:
            self.mostrar_mensagem(
                "A descrição é obrigatória.",
                "erro"
            )
            return

        if len(descricao) < 3:
            self.mostrar_mensagem(
                "A descrição deve ter pelo menos 3 caracteres.",
                "erro"
            )
            return

        if not valor:
            self.mostrar_mensagem(
                "O valor é obrigatório.",
                "erro"
            )
            return

        try:
            valor_numerico = float(
                valor.replace(",", ".").replace("R$", "").strip()
            )
        except ValueError:
            self.mostrar_mensagem(
                "Digite um valor numérico válido.",
                "erro"
            )
            return

        if valor_numerico <= 0:
            self.mostrar_mensagem(
                "O valor deve ser maior que zero.",
                "erro"
            )
            return

        if not categoria:
            self.mostrar_mensagem(
                "A categoria é obrigatória.",
                "erro"
            )
            return

        if len(categoria) < 3:
            self.mostrar_mensagem(
                "A categoria deve ter pelo menos 3 caracteres.",
                "erro"
            )
            return

        if not data_vencimento:
            self.mostrar_mensagem(
                "A data de vencimento é obrigatória.",
                "erro"
            )
            return

        try:
            datetime.strptime(data_vencimento, "%d/%m/%Y")
        except ValueError:
            self.mostrar_mensagem(
                "Use uma data válida no formato DD/MM/AAAA.",
                "erro"
            )
            return

        self.mostrar_mensagem(
            "✓ Lançamento salvo com sucesso!",
            "sucesso"
        )

        print("Descrição:", descricao)
        print("Valor:", valor_numerico)
        print("Tipo:", tipo)
        print("Categoria:", categoria)
        print("Terceiro:", self.terceiro.get())
        print("Status:", self.status.get())
        print("Vencimento:", data_vencimento)

        self._limpar_campos()

    def mostrar_mensagem(self, texto, tipo):
        self.mensagem.configure(text=texto)

        if tipo == "erro":
            self.mensagem.configure(text_color="#F38BA8")
        else:
            self.mensagem.configure(text_color="#A6E3A1")

    def _limpar_campos(self):
        self.descricao.delete(0, "end")
        self.valor.delete(0, "end")
        self.categoria.delete(0, "end")
        self.terceiro.delete(0, "end")
        self.data_vencimento.delete(0, "end")

        self.tipo.set("RECEITA")
        self.status.set("PENDENTE")


if __name__ == "__main__":
    app = ctk.CTk()

    app.title("Testando View - Lançamentos")
    app.geometry("700x700")
    app.resizable(False, False)

    view = LancamentoView(app)
    view.pack(expand=True, fill="both", padx=20, pady=20)

    app.mainloop()