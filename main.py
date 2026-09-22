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

# Carrega variáveis de ambiente do .env (chave da API, etc.)
load_dotenv()

from models.database import Database
from views.login_view import LoginView
from views.menu_view import MenuView


# ----------------------------------------------------------------------
# Configuração global de aparência (deve ocorrer UMA única vez, aqui)
# ----------------------------------------------------------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


class AppManager:
    """Gerencia a transição entre telas de Login e Menu Principal."""

    def __init__(self, app: ctk.CTk):
        self.app = app
        self.tela_atual = None
        self.mostrar_login()

    def mostrar_login(self):
        """Exibe a tela de Login."""
        if self.tela_atual is not None:
            self.tela_atual.destroy()

        self.tela_atual = LoginView(
            self.app,
            on_login_sucesso=self.mostrar_menu,
        )
        self.tela_atual.pack(expand=True, fill="both")

    def mostrar_menu(self, usuario_logado: dict):
        """Exibe a tela principal após login bem-sucedido."""
        if self.tela_atual is not None:
            self.tela_atual.destroy()

        self.tela_atual = MenuView(
            self.app,
            usuario_logado=usuario_logado,
            on_logout=self.mostrar_login,
        )
        self.tela_atual.pack(expand=True, fill="both")


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Inicializa o banco de dados (cria arquivo e schema se necessário)
    # ------------------------------------------------------------------
    try:
        Database()
    except Exception as exc:
        print(f"[ERRO] Não foi possível inicializar o banco de dados: {exc}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 2. Cria a janela principal
    # ------------------------------------------------------------------
    app = ctk.CTk()
    app.title("Gerenciador de Finanças Pessoais")
    app.geometry("1100x700")
    app.minsize(950, 650)

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
    # 2.2. Configura a cor de fundo da janela principal (verde escuro)
    # ------------------------------------------------------------------
    app.configure(fg_color="#0B1D1F")

    # ------------------------------------------------------------------
    # 3. Inicia o gerenciador de telas (Login → Menu)
    # ------------------------------------------------------------------
    AppManager(app)

    app.mainloop()


if __name__ == "__main__":
    main()