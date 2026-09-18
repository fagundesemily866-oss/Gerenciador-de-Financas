import customtkinter as ctk

# Configuração global de aparência
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class UsuarioView(ctk.CTkFrame):

    def __init__(self, parent, data_mock=None):
        super().__init__(parent, fg_color="transparent")

        # Dados de teste (Mock)
        self.data = data_mock or {
            "nome": "",
            "email": "",
            "tipo_perfil": "",
            "data_criacao": ""
        }

        # Configuração do Grid Principal
        self.grid_columnconfigure(0, weight=1, pad=15)
        self.grid_rowconfigure((0, 1), weight=1, pad=15)

        # Inicialização dos Componentes
        self._build_perfil()
        self._build_editar_dados()
        self._build_alterar_senha()

    def _build_perfil(self):
        """Card Principal: Dados do Perfil (Hero)"""
        frame_perfil = ctk.CTkFrame(
            self, corner_radius=15, fg_color="#1E1E2E", border_width=1, border_color="#313244"
        )
        frame_perfil.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        title = ctk.CTkLabel(
            frame_perfil,
            text="MEU PERFIL",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        )
        title.pack(anchor="w", padx=20, pady=(15, 5))

        nome_val = ctk.CTkLabel(
            frame_perfil,
            text=self.data["nome"],
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#CDD6F4",
        )
        nome_val.pack(anchor="w", padx=20, pady=0)

        email_lbl = ctk.CTkLabel(
            frame_perfil,
            text=self.data["email"],
            font=ctk.CTkFont(size=14),
            text_color="#A6ADC8",
        )
        email_lbl.pack(anchor="w", padx=20, pady=(2, 10))

        badge_frame = ctk.CTkFrame(frame_perfil, fg_color="#313244", corner_radius=6)
        badge_frame.pack(anchor="w", padx=20, pady=(0, 15))

        badge = ctk.CTkLabel(
            badge_frame,
            text=f"  {self.data['tipo_perfil']}  ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#89B4FA",
        )
        badge.pack(padx=4, pady=4)

        membro_lbl = ctk.CTkLabel(
            frame_perfil,
            text=f"Membro desde {self.data['data_criacao']}",
            font=ctk.CTkFont(size=11),
            text_color="#585B70",
        )
        membro_lbl.pack(anchor="w", padx=20, pady=(0, 15))

    def _build_editar_dados(self):
        """Card de Edição de Dados"""
        frame_editar = ctk.CTkFrame(
            self, corner_radius=15, fg_color="#1E1E2E", border_width=1, border_color="#313244"
        )
        frame_editar.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        title = ctk.CTkLabel(
            frame_editar,
            text="✏️ EDITAR DADOS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        campo_nome = ctk.CTkEntry(
            frame_editar,
            placeholder_text="Nome",
            fg_color="#181825",
            border_color="#313244",
        )
        campo_nome.insert(0, self.data["nome"])
        campo_nome.pack(fill="x", padx=20, pady=4)

        campo_email = ctk.CTkEntry(
            frame_editar,
            placeholder_text="E-mail",
            fg_color="#181825",
            border_color="#313244",
        )
        campo_email.insert(0, self.data["email"])
        campo_email.pack(fill="x", padx=20, pady=4)

        combo_tipo = ctk.CTkComboBox(
            frame_editar,
            values=["PESSOAL", "PJ"],
            fg_color="#181825",
            border_color="#313244",
            button_color="#313244",
        )
        combo_tipo.set(self.data["tipo_perfil"])
        combo_tipo.pack(fill="x", padx=20, pady=4)

        btn_salvar = ctk.CTkButton(
            frame_editar,
            text="Salvar Alterações",
            fg_color="#89B4FA",
            text_color="#1E1E2E",
            hover_color="#74A0E8",
        )
        btn_salvar.pack(fill="x", padx=20, pady=(10, 15))

    def _build_alterar_senha(self):
        """Card de Alteração de Senha"""
        frame_senha = ctk.CTkFrame(
            self, corner_radius=15, fg_color="#1E1E2E", border_width=1, border_color="#313244"
        )
        frame_senha.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)

        title = ctk.CTkLabel(
            frame_senha,
            text=" ALTERAR SENHA",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        campo_senha_atual = ctk.CTkEntry(
            frame_senha,
            placeholder_text="Senha atual",
            show="•",
            fg_color="#181825",
            border_color="#313244",
        )
        campo_senha_atual.pack(fill="x", padx=20, pady=4)

        campo_senha_nova = ctk.CTkEntry(
            frame_senha,
            placeholder_text="Nova senha",
            show="•",
            fg_color="#181825",
            border_color="#313244",
        )
        campo_senha_nova.pack(fill="x", padx=20, pady=4)

        campo_senha_confirma = ctk.CTkEntry(
            frame_senha,
            placeholder_text="Confirmar nova senha",
            show="•",
            fg_color="#181825",
            border_color="#313244",
        )
        campo_senha_confirma.pack(fill="x", padx=20, pady=4)

        btn_alterar = ctk.CTkButton(
            frame_senha,
            text="Alterar Senha",
            fg_color="#313244",
            text_color="#CDD6F4",
            hover_color="#45475A",
        )
        btn_alterar.pack(fill="x", padx=20, pady=(10, 15))

if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Testando View - Usuário")
    app.geometry("900x600")
    app.resizable(False, False)

    view = UsuarioView(app)
    view.pack(expand=True, fill="both", padx=20, pady=20)

    app.mainloop()