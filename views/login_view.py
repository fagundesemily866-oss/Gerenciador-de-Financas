import customtkinter as ctk
from datetime import date
from typing import Callable, Optional, Dict, Any
from dao.usuario_dao import UsuarioDAO
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_ACENTO_PRIMARIO,
    COR_ACENTO_HOVER, COR_SUCESSO, COR_SUCESSO_HOVER, COR_ALERTA,
    COR_BOTAO_SECUNDARIO, COR_BOTAO_SECUNDARIO_HOVER,
    COR_TAB_BG, COR_TAB_SELECIONADA, COR_TAB_SELECIONADA_HOVER,
    COR_TAB_TEXTO, COR_TEXTO_MUTED,
    fonte, fonte_titulo, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
)



class LoginView(ctk.CTkFrame):
    """Tela de Login e Cadastro de Usuários com visual moderno e intuitivo."""

    def __init__(
        self,
        parent,
        on_login_sucesso: Callable[[Dict[str, Any]], None],
        dao: Optional[UsuarioDAO] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.on_login_sucesso = on_login_sucesso
        self.dao = dao or UsuarioDAO()

        # Centraliza o container na tela
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_interface()

    def _build_interface(self):
        # Card Central
        card = ctk.CTkFrame(
            self,
            width=460,
            corner_radius=20,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
        )
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_columnconfigure(0, weight=1)

        # Cabeçalho / Logo — usando ícone de carteira em vez de diamante
        ctk.CTkLabel(
            card,
            text="📊",
            font=fonte(40),
        ).pack(pady=(25, 5))

        ctk.CTkLabel(
            card,
            text="Gerenciador Financeiro",
            font=fonte(22, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
        ).pack()

        ctk.CTkLabel(
            card,
            text="Controle inteligente de finanças pessoais",
            font=fonte_corpo(),
            text_color=COR_TEXTO_SECUNDARIO,
        ).pack(pady=(2, 15))

        # Abas: Entrar / Criar Conta
        self.tabview = ctk.CTkTabview(
            card,
            width=390,
            fg_color="transparent",
            segmented_button_fg_color=COR_TAB_BG,
            segmented_button_selected_color=COR_TAB_SELECIONADA,
            segmented_button_selected_hover_color=COR_TAB_SELECIONADA_HOVER,
            text_color=COR_TAB_TEXTO,
        )
        self.tabview.pack(padx=20, pady=(0, 20))

        tab_login = self.tabview.add("Entrar")
        tab_cadastro = self.tabview.add("Criar Conta")

        self._build_tab_login(tab_login)
        self._build_tab_cadastro(tab_cadastro)

    # ==========================================================
    # ABA: ENTRAR
    # ==========================================================
    def _build_tab_login(self, tab):
        ctk.CTkLabel(tab, text="E-mail:", font=fonte_corpo()).pack(
            anchor="w", padx=10, pady=(10, 2)
        )
        self.entry_login_email = ctk.CTkEntry(
            tab,
            placeholder_text="seu.email@exemplo.com",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            height=38,
            font=fonte_corpo(),
        )
        self.entry_login_email.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(tab, text="Senha:", font=fonte_corpo()).pack(
            anchor="w", padx=10, pady=(0, 2)
        )

        senha_frame = ctk.CTkFrame(tab, fg_color="transparent")
        senha_frame.pack(fill="x", padx=10, pady=(0, 10))
        senha_frame.grid_columnconfigure(0, weight=1)

        self.entry_login_senha = ctk.CTkEntry(
            senha_frame,
            placeholder_text="Sua senha",
            show="•",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            height=38,
            font=fonte_corpo(),
        )
        self.entry_login_senha.grid(row=0, column=0, sticky="ew")

        self.btn_ver_senha_login = ctk.CTkButton(
            senha_frame,
            text="👁️",
            width=38,
            height=38,
            fg_color=COR_BOTAO_SECUNDARIO,
            hover_color=COR_BOTAO_SECUNDARIO_HOVER,
            command=lambda: self._toggle_senha(self.entry_login_senha, self.btn_ver_senha_login),
        )
        self.btn_ver_senha_login.grid(row=0, column=1, padx=(6, 0))

        self.lbl_feedback_login = ctk.CTkLabel(
            tab,
            text="",
            font=fonte(12, "bold"),
        )
        self.lbl_feedback_login.pack(fill="x", padx=10, pady=(0, 6))

        # Botão Entrar
        btn_entrar = ctk.CTkButton(
            tab,
            text="Entrar no Sistema",
            height=40,
            fg_color=COR_ACENTO_PRIMARIO,
            text_color="#0B1D1F",
            hover_color=COR_ACENTO_HOVER,
            font=fonte(13, "bold"),
            command=self._fazer_login,
        )
        btn_entrar.pack(fill="x", padx=10, pady=(4, 10))

        # Divisor
        ctk.CTkLabel(
            tab,
            text="─────── ou ───────",
            font=fonte_pequena(),
            text_color=COR_TEXTO_MUTED,
        ).pack(pady=(0, 8))

        # Botão Acesso Rápido Demo
        btn_demo = ctk.CTkButton(
            tab,
            text="⚡ Acesso Rápido (Usuário Demo)",
            height=36,
            fg_color=COR_BOTAO_SECUNDARIO,
            text_color=COR_TEXTO_PRINCIPAL,
            hover_color=COR_BOTAO_SECUNDARIO_HOVER,
            font=fonte_corpo(),
            command=self._acesso_demo,
        )
        btn_demo.pack(fill="x", padx=10, pady=(0, 10))

    # ==========================================================
    # ABA: CRIAR CONTA
    # ==========================================================
    def _build_tab_cadastro(self, tab):
        ctk.CTkLabel(tab, text="Nome Completo:", font=fonte_corpo()).pack(
            anchor="w", padx=10, pady=(6, 2)
        )
        self.entry_cad_nome = ctk.CTkEntry(
            tab,
            placeholder_text="Ex: João da Silva",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            height=34,
            font=fonte_corpo(),
        )
        self.entry_cad_nome.pack(fill="x", padx=10, pady=(0, 6))

        ctk.CTkLabel(tab, text="E-mail:", font=fonte_corpo()).pack(
            anchor="w", padx=10, pady=(0, 2)
        )
        self.entry_cad_email = ctk.CTkEntry(
            tab,
            placeholder_text="exemplo@email.com",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            height=34,
            font=fonte_corpo(),
        )
        self.entry_cad_email.pack(fill="x", padx=10, pady=(0, 6))

        # Perfil
        ctk.CTkLabel(tab, text="Tipo de Perfil:", font=fonte_corpo()).pack(
            anchor="w", padx=10, pady=(0, 2)
        )
        self.combo_cad_tipo = ctk.CTkComboBox(
            tab,
            values=["PF - Pessoa Física", "PJ - Pessoa Jurídica"],
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            button_color=COR_BOTAO_SECUNDARIO,
            height=34,
            font=fonte_corpo(),
        )
        self.combo_cad_tipo.pack(fill="x", padx=10, pady=(0, 6))

        # Senha e Confirmação
        ctk.CTkLabel(tab, text="Senha:", font=fonte_corpo()).pack(
            anchor="w", padx=10, pady=(0, 2)
        )
        self.entry_cad_senha = ctk.CTkEntry(
            tab,
            placeholder_text="Mínimo 4 caracteres",
            show="•",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            height=34,
            font=fonte_corpo(),
        )
        self.entry_cad_senha.pack(fill="x", padx=10, pady=(0, 6))

        ctk.CTkLabel(tab, text="Confirmar Senha:", font=fonte_corpo()).pack(
            anchor="w", padx=10, pady=(0, 2)
        )
        self.entry_cad_confirma = ctk.CTkEntry(
            tab,
            placeholder_text="Repita sua senha",
            show="•",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            height=34,
            font=fonte_corpo(),
        )
        self.entry_cad_confirma.pack(fill="x", padx=10, pady=(0, 8))

        self.lbl_feedback_cad = ctk.CTkLabel(
            tab,
            text="",
            font=fonte(12, "bold"),
        )
        self.lbl_feedback_cad.pack(fill="x", padx=10, pady=(0, 6))

        btn_cadastrar = ctk.CTkButton(
            tab,
            text="Criar Minha Conta",
            height=38,
            fg_color=COR_SUCESSO,
            text_color="#0B1D1F",
            hover_color=COR_SUCESSO_HOVER,
            font=fonte(13, "bold"),
            command=self._fazer_cadastro,
        )
        btn_cadastrar.pack(fill="x", padx=10, pady=(0, 10))

    # ==========================================================
    # AÇÕES
    # ==========================================================
    def _toggle_senha(self, entry, botao):
        if entry.cget("show") == "•":
            entry.configure(show="")
            botao.configure(text="🔒")
        else:
            entry.configure(show="•")
            botao.configure(text="👁️")

    def _fazer_login(self):
        email = self.entry_login_email.get().strip()
        senha = self.entry_login_senha.get().strip()

        if not email:
            self._mostrar_feedback_login("Informe o seu e-mail!", COR_ALERTA)
            return

        if not senha:
            self._mostrar_feedback_login("Informe a sua senha!", COR_ALERTA)
            return

        usuario = self.dao.buscar_por_email(email)
        if not usuario:
            self._mostrar_feedback_login("Usuário não encontrado com este e-mail!", COR_ALERTA)
            return

        if usuario["senha_hash"] != senha:
            self._mostrar_feedback_login("Senha incorreta!", COR_ALERTA)
            return

        self.on_login_sucesso(usuario)

    def _fazer_cadastro(self):
        nome = self.entry_cad_nome.get().strip()
        email = self.entry_cad_email.get().strip()
        tipo_raw = self.combo_cad_tipo.get()
        tipo = "PJ" if "PJ" in tipo_raw else "PF"
        senha = self.entry_cad_senha.get().strip()
        confirma = self.entry_cad_confirma.get().strip()

        if not nome:
            self._mostrar_feedback_cad("Informe seu nome completo!", COR_ALERTA)
            return

        if not email or "@" not in email:
            self._mostrar_feedback_cad("Informe um e-mail válido!", COR_ALERTA)
            return

        if len(senha) < 4:
            self._mostrar_feedback_cad("A senha deve ter pelo menos 4 caracteres!", COR_ALERTA)
            return

        if senha != confirma:
            self._mostrar_feedback_cad("As senhas digitadas não coincidem!", COR_ALERTA)
            return

        # Verifica se já existe
        existente = self.dao.buscar_por_email(email)
        if existente:
            self._mostrar_feedback_cad("Este e-mail já está cadastrado!", COR_ALERTA)
            return

        try:
            uid = self.dao.inserir(
                nome=nome,
                email=email,
                senha_hash=senha,
                tipo_perfil=tipo,
                data_criacao=date.today().strftime("%Y-%m-%d"),
            )
            novo_user = self.dao.buscar_por_id(uid)
            self._mostrar_feedback_cad("✓ Conta criada com sucesso!", COR_SUCESSO)
            self.after(500, lambda: self.on_login_sucesso(novo_user))
        except Exception as e:
            self._mostrar_feedback_cad(f"Erro ao cadastrar: {e}", COR_ALERTA)

    def _acesso_demo(self):
        """Entra com o usuário demo ou cria um caso o banco esteja limpo."""
        todos = self.dao.listar_todos()
        if todos:
            user = todos[0]
        else:
            uid = self.dao.inserir(
                nome="Usuário Demo",
                email="demo@financeiro.com",
                senha_hash="1234",
                tipo_perfil="PF",
                data_criacao=date.today().strftime("%Y-%m-%d"),
            )
            user = self.dao.buscar_por_id(uid)

        self.on_login_sucesso(user)

    def _mostrar_feedback_login(self, texto: str, cor: str):
        self.lbl_feedback_login.configure(text=texto, text_color=cor)

    def _mostrar_feedback_cad(self, texto: str, cor: str):
        self.lbl_feedback_cad.configure(text=texto, text_color=cor)


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Testando LoginView")
    app.geometry("800x650")
    view = LoginView(app, on_login_sucesso=lambda u: print(f"Logado como {u['nome']}"))
    view.pack(expand=True, fill="both")
    app.mainloop()
