import customtkinter as ctk
from datetime import date
from typing import Optional
from dao.usuario_dao import UsuarioDAO
from views.notificacao_toast import GerenciadorNotificacoes
from PIL import Image, ImageTk
from tkinter import filedialog


class UsuarioView(ctk.CTkFrame):
    """Tela de Meu Perfil com dados persistidos no banco de dados SQLite."""

    def __init__(self, parent, dao: Optional[UsuarioDAO] = None, usuario_atual: Optional[dict] = None,
                 on_foto_atualizada: Optional[callable] = None):
        super().__init__(parent, fg_color="transparent")
        self.dao = dao or UsuarioDAO()
        # Callback chamado com a imagem PIL sempre que o usuário troca a foto,
        # usado pelo MenuView para atualizar o avatar da sidebar em tempo real.
        self.on_foto_atualizada = on_foto_atualizada

        if usuario_atual:
            self.usuario_atual = usuario_atual
        else:
            self._garantir_usuario_ativo()

        # Configuração do Grid Principal
        self.grid_columnconfigure(0, weight=1, pad=15)
        self.grid_columnconfigure(1, weight=1, pad=15)
        self.grid_rowconfigure((0, 1), weight=1, pad=15)

        # Inicialização dos Componentes
        self._build_perfil()
        self._build_editar_dados()
        self._build_alterar_senha()
        self.atualizar_dados()

    def _garantir_usuario_ativo(self):
        """Garante que existe pelo menos um usuário no banco para a sessão."""
        todos = self.dao.listar_todos()
        if todos:
            self.usuario_atual = todos[0]
        else:
            uid = self.dao.inserir(
                nome="Usuário Financeiro",
                email="usuario@exemplo.com",
                senha_hash="123456",
                tipo_perfil="PF",
                data_criacao=date.today().strftime("%Y-%m-%d"),
            )
            self.usuario_atual = self.dao.buscar_por_id(uid)

    # ==========================================================
    # CARD PRINCIPAL: MEU PERFIL (HERO) — com avatar de iniciais
    # ==========================================================
    def _build_perfil(self):
        frame_perfil = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        frame_perfil.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        title = ctk.CTkLabel(
            frame_perfil,
            text="MEU PERFIL",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        # Foto de perfil

        self.foto_perfil = None

        self.btn_avatar = ctk.CTkButton(
            frame_perfil,
            text="👤",
            width=80,
            height=80,
            corner_radius=40,
            fg_color="#313244",
            hover_color="#45475A",
            command=self._escolher_foto
        )

        self.btn_avatar.pack(anchor="w", padx=20, pady=(0, 8))

        self.lbl_nome = ctk.CTkLabel(
            frame_perfil,
            text="",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#CDD6F4",
        )
        self.lbl_nome.pack(anchor="w", padx=20, pady=0)

        self.lbl_email = ctk.CTkLabel(
            frame_perfil,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="#A6ADC8",
        )
        self.lbl_email.pack(anchor="w", padx=20, pady=(2, 10))

        badge_frame = ctk.CTkFrame(frame_perfil, fg_color="#313244", corner_radius=6)
        badge_frame.pack(anchor="w", padx=20, pady=(0, 10))

        self.lbl_badge = ctk.CTkLabel(
            badge_frame,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#89B4FA",
        )
        self.lbl_badge.pack(padx=8, pady=4)

        self.lbl_membro = ctk.CTkLabel(
            frame_perfil,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#6C7086",
        )
        self.lbl_membro.pack(anchor="w", padx=20, pady=(0, 15))

    # ==========================================================
    # CARD: EDITAR DADOS
    # ==========================================================
    def _build_editar_dados(self):
        frame_editar = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        frame_editar.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        title = ctk.CTkLabel(
            frame_editar,
            text="✏️  EDITAR DADOS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        ctk.CTkLabel(frame_editar, text="Nome Completo:", font=ctk.CTkFont(size=12)).pack(
            anchor="w", padx=20, pady=(0, 2)
        )
        self.campo_nome = ctk.CTkEntry(
            frame_editar,
            placeholder_text="Nome",
            fg_color="#181825",
            border_color="#313244",
        )
        self.campo_nome.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkLabel(frame_editar, text="E-mail:", font=ctk.CTkFont(size=12)).pack(
            anchor="w", padx=20, pady=(0, 2)
        )
        self.campo_email = ctk.CTkEntry(
            frame_editar,
            placeholder_text="E-mail",
            fg_color="#181825",
            border_color="#313244",
        )
        self.campo_email.pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkLabel(frame_editar, text="Tipo de Perfil:", font=ctk.CTkFont(size=12)).pack(
            anchor="w", padx=20, pady=(0, 2)
        )
        self.combo_tipo = ctk.CTkComboBox(
            frame_editar,
            values=["Pessoa Física (PF)", "Pessoa Jurídica (PJ)"],
            fg_color="#181825",
            border_color="#313244",
            button_color="#313244",
        )
        self.combo_tipo.pack(fill="x", padx=20, pady=(0, 10))

        self.lbl_feedback_perfil = ctk.CTkLabel(
            frame_editar,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.lbl_feedback_perfil.pack(fill="x", padx=20, pady=(0, 6))

        btn_salvar = ctk.CTkButton(
            frame_editar,
            text="Salvar Alterações",
            fg_color="#89B4FA",
            text_color="#1E1E2E",
            hover_color="#74A0E8",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._salvar_dados_perfil,
        )
        btn_salvar.pack(fill="x", padx=20, pady=(0, 15))

    # ==========================================================
    # CARD: ALTERAR SENHA
    # ==========================================================
    def _build_alterar_senha(self):
        frame_senha = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        frame_senha.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)

        title = ctk.CTkLabel(
            frame_senha,
            text="🔒  ALTERAR SENHA",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        ctk.CTkLabel(frame_senha, text="Senha Atual:", font=ctk.CTkFont(size=12)).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.campo_senha_atual = ctk.CTkEntry(
            frame_senha,
            placeholder_text="Digite sua senha atual",
            show="•",
            fg_color="#181825",
            border_color="#313244",
        )
        self.campo_senha_atual.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(frame_senha, text="Nova Senha:", font=ctk.CTkFont(size=12)).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.campo_senha_nova = ctk.CTkEntry(
            frame_senha,
            placeholder_text="Mínimo de 4 caracteres",
            show="•",
            fg_color="#181825",
            border_color="#313244",
        )
        self.campo_senha_nova.pack(fill="x", padx=20, pady=(0, 4))

        # Hint de senha
        ctk.CTkLabel(
            frame_senha,
            text="🔑 A senha deve ter no mínimo 4 caracteres",
            font=ctk.CTkFont(size=10),
            text_color="#585B70",
            anchor="w",
        ).pack(anchor="w", padx=20, pady=(0, 8))

        ctk.CTkLabel(frame_senha, text="Confirmar Nova Senha:", font=ctk.CTkFont(size=12)).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.campo_senha_confirma = ctk.CTkEntry(
            frame_senha,
            placeholder_text="Confirme a nova senha",
            show="•",
            fg_color="#181825",
            border_color="#313244",
        )
        self.campo_senha_confirma.pack(fill="x", padx=20, pady=(0, 15))

        self.lbl_feedback_senha = ctk.CTkLabel(
            frame_senha,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.lbl_feedback_senha.pack(fill="x", padx=20, pady=(0, 8))

        btn_alterar = ctk.CTkButton(
            frame_senha,
            text="Atualizar Senha",
            fg_color="#313244",
            text_color="#CDD6F4",
            hover_color="#45475A",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._alterar_senha,
        )
        btn_alterar.pack(fill="x", padx=20, pady=(0, 15))

    # ==========================================================
    # AÇÕES E ATUALIZAÇÃO
    # ==========================================================

    def _escolher_foto(self):
        caminho = filedialog.askopenfilename(
            title="Escolher foto de perfil",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not caminho:
            return

        imagem_original = Image.open(caminho)
        imagem_original = imagem_original.convert("RGB")

        # Miniatura para o avatar grande desta própria tela (Meu Perfil)
        imagem_perfil = imagem_original.copy()
        imagem_perfil.thumbnail((80, 80))

        self.foto_perfil = ctk.CTkImage(
            light_image=imagem_perfil,
            dark_image=imagem_perfil,
            size=(80, 80)
        )

        self.btn_avatar.configure(
            image=self.foto_perfil,
            text=""
        )

        # Avisa o MenuView (sidebar) para atualizar o avatar lá em cima também
        if self.on_foto_atualizada:
            self.on_foto_atualizada(imagem_original)

    def _salvar_dados_perfil(self):
        nome = self.campo_nome.get().strip()
        email = self.campo_email.get().strip()
        tipo_raw = self.combo_tipo.get()

        # Extrair PF ou PJ do texto descritivo
        tipo = "PJ" if "PJ" in tipo_raw else "PF"

        if not nome:
            self.lbl_feedback_perfil.configure(
                text="O nome não pode ser vazio!", text_color="#F38BA8"
            )
            return

        if not email or "@" not in email:
            self.lbl_feedback_perfil.configure(
                text="Digite um e-mail válido!", text_color="#F38BA8"
            )
            return

        try:
            self.dao.atualizar(
                usuario_id=self.usuario_atual["id"],
                nome=nome,
                email=email,
                tipo_perfil=tipo,
            )
            self.lbl_feedback_perfil.configure(
                text="✓ Dados atualizados com sucesso!", text_color="#A6E3A1"
            )
            try:
                notif = GerenciadorNotificacoes.obter_instancia()
                if notif:
                    notif.sucesso("Perfil atualizado com sucesso!")
            except Exception:
                pass
        except Exception as e:
            self.lbl_feedback_perfil.configure(
                text=f"Erro ao atualizar: {e}", text_color="#F38BA8"
            )
            try:
                notif = GerenciadorNotificacoes.obter_instancia()
                if notif:
                    notif.erro(f"Erro ao atualizar perfil: {e}")
            except Exception:
                pass

    def _alterar_senha(self):
        atual = self.campo_senha_atual.get()
        nova = self.campo_senha_nova.get()
        confirma = self.campo_senha_confirma.get()

        senha_gravada = self.usuario_atual.get("senha_hash", "")

        if atual != senha_gravada:
            self.lbl_feedback_senha.configure(
                text="Senha atual incorreta!",
                text_color="#F38BA8"
            )
            return

        if len(nova) < 4:
            self.lbl_feedback_senha.configure(
                text="A nova senha deve ter no mínimo 4 caracteres!",
                text_color="#F38BA8"
            )
            return

        if nova != confirma:
            self.lbl_feedback_senha.configure(
                text="As senhas não coincidem!",
                text_color="#F38BA8"
            )
            return

        try:
            self.dao.alterar_senha(
                self.usuario_atual["id"],
                nova
            )

            self.lbl_feedback_senha.configure(
                text="✓ Senha alterada com sucesso!",
                text_color="#A6E3A1"
            )

            self.campo_senha_atual.delete(0, "end")
            self.campo_senha_nova.delete(0, "end")
            self.campo_senha_confirma.delete(0, "end")

            self.atualizar_dados()

        except Exception as e:
            self.lbl_feedback_senha.configure(
                text=f"Erro ao alterar senha: {e}",
                text_color="#F38BA8"
            )

    def atualizar_dados(self):
        """Recarrega os dados do usuário a partir do SQLite."""
        if hasattr(self, "usuario_atual") and self.usuario_atual:
            dados = self.dao.buscar_por_id(self.usuario_atual["id"])
            if dados:
                self.usuario_atual = dados

        # Atualiza labels do Card Hero
        nome = self.usuario_atual.get("nome", "Usuário")
        email = self.usuario_atual.get("email", "")
        tipo = self.usuario_atual.get("tipo_perfil", "PF")
        criacao = self.usuario_atual.get("data_criacao", "-")

        self.lbl_nome.configure(text=nome)
        self.lbl_email.configure(text=email)

        # Badge descritivo
        tipo_desc = "Pessoa Física" if tipo == "PF" else "Pessoa Jurídica"
        self.lbl_badge.configure(text=f"  {tipo_desc} ({tipo})  ")
        self.lbl_membro.configure(text=f"Membro desde {criacao}")

        # Atualiza campos de edição
        self.campo_nome.delete(0, "end")
        self.campo_nome.insert(0, nome)

        self.campo_email.delete(0, "end")
        self.campo_email.insert(0, email)

        # Setar combo com texto descritivo
        tipo_combo = "Pessoa Física (PF)" if tipo == "PF" else "Pessoa Jurídica (PJ)"
        self.combo_tipo.set(tipo_combo)


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Testando UsuarioView")
    app.geometry("900x600")
    view = UsuarioView(app)
    view.pack(expand=True, fill="both", padx=20, pady=20)
    app.mainloop()