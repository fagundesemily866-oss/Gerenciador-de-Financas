"""
Gerenciador de Finanças Pessoais
=================================

Ponto de entrada da aplicação. Inicializa o banco de dados, exibe a tela de
Login/Cadastro e, após autenticação bem-sucedida, exibe o MenuView com todas
as funcionalidades do sistema financeiro.

Como executar (a partir da pasta Gerenciador-de-Financas):
    python main.py

Requisitos:
    pip install customtkinter pillow
"""
import os
import sys
import customtkinter as ctk
from dotenv import load_dotenv
from idioma import instalar_idioma, definir_idioma, obter_idioma

# Carrega variáveis de ambiente do .env (chave da API, etc.)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from models.database import Database
from services.sessao import Sessao
from views.tema import COR_FUNDO_PRINCIPAL, carregar_tema_preferido
from views.login_view import LoginView
from views.menu_view import MenuView


# ----------------------------------------------------------------------
# Configuração global de aparência (deve ocorrer UMA única vez, aqui)
# ----------------------------------------------------------------------
ctk.set_appearance_mode(carregar_tema_preferido())
ctk.set_default_color_theme("green")
instalar_idioma(ctk)


class AppManager:
    """Gerencia a transição entre telas de Login e Menu Principal."""

    def __init__(self, app: ctk.CTk):
        self.app = app
        self.tela_atual = None
        self.mostrar_login()

    def mostrar_login(self):
        """Exibe a tela de Login."""
        # Encerra a sessão: nenhum dado de usuário fica acessível sem login
        Sessao.limpar()
        if self.tela_atual is not None:
            self.tela_atual.destroy()

        self.tela_atual = LoginView(
            self.app,
            on_login_sucesso=self.mostrar_menu,
        )
        self.tela_atual.pack(expand=True, fill="both")

    def mostrar_menu(self, usuario_logado: dict, aba_inicial: str = "dashboard"):
        """Exibe a tela principal após login bem-sucedido."""
        # Define o usuário logado ANTES de criar as telas: DAOs e views passam a
        # enxergar apenas os dados dele (ver services/sessao.py).
        Sessao.definir(usuario_logado["id"])
        if self.tela_atual is not None:
            self.tela_atual.destroy()

        self.tela_atual = MenuView(
            self.app,
            usuario_logado=usuario_logado,
            on_logout=self.mostrar_login,
            on_idioma_alterado=self.alterar_idioma,
        )
        self.tela_atual.pack(expand=True, fill="both")
        if aba_inicial != "dashboard":
            view = self.tela_atual
            self.app.after_idle(lambda: view.winfo_exists() and view.selecionar(aba_inicial))

    def alterar_idioma(self, codigo: str) -> None:
        """Reconstrói a interface no novo idioma sem encerrar a sessão nem alterar dados."""
        if codigo == obter_idioma():
            return
        usuario = self.tela_atual.usuario_logado
        definir_idioma(codigo)
        self.app.title("Gerenciador de Finanças Pessoais")
        self.app.after_idle(lambda: self.mostrar_menu(usuario, aba_inicial="usuario"))


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Inicializa a conexão com o banco MySQL (DDL deve ter sido rodado)
    # ------------------------------------------------------------------
    try:
        Database().get_connection()
    except Exception as exc:
        print(
            f"[ERRO] Não foi possível conectar ao MySQL: {exc}\n"
            "Verifique se:\n"
            "  1. O servidor MySQL está iniciado\n"
            "  2. O usuário pode criar o banco pelas migrations\n"
            "  3. As credenciais em .env estão corretas"
        )
        sys.exit(1)

    # ------------------------------------------------------------------
    # 2. Cria a janela principal
    # ------------------------------------------------------------------
    app = ctk.CTk()
    app.title("Gerenciador de Finanças Pessoais")
    app.geometry("1280x800")
    app.minsize(1050, 680)

    # ------------------------------------------------------------------
    # 2.1. Define o ícone personalizado da janela
    # ------------------------------------------------------------------
    caminho_base = os.path.dirname(os.path.abspath(__file__))
    caminho_icone = os.path.join(caminho_base, "assets", "icon.ico")
    if os.path.exists(caminho_icone):
        try:
            app.iconbitmap(caminho_icone)
        except Exception:
            pass  # Fallback silencioso se o SO não suportar

    # ------------------------------------------------------------------
    # 2.2. Configura a cor de fundo da janela principal
    # ------------------------------------------------------------------
    app.configure(fg_color="#0B131B")

    # ------------------------------------------------------------------
    # 3. Inicia o gerenciador de telas (Login → Menu)
    # ------------------------------------------------------------------
    AppManager(app)

    app.mainloop()


if __name__ == "__main__":
    main()
