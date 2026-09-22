import customtkinter as ctk

from views.usuario_view import UsuarioView
from views.lancamento_view import LancamentoView
from views.saude_financeira_view import SaudeFinanceiraView
from views.categoria_view import CategoriaView
from views.meta_view import MetaView
from views.terceiro_view import TerceiroView
from views.simulador_view import SimuladorView
from views.relatorio_view import RelatorioView
from views.assistente_ia_view import AssistenteIAView
from views.notificacao_toast import GerenciadorNotificacoes
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_CARD_USER_BG, COR_CARD_USER_BORDA,
    COR_BORDA, COR_SIDEBAR, COR_TEXTO_PRINCIPAL, COR_TEXTO_SECUNDARIO,
    COR_TEXTO_TERCIARIO, COR_ACENTO_PRIMARIO, COR_AVATAR_BG, COR_AVATAR_TEXTO,
    COR_BOTAO_NORMAL, COR_BOTAO_ATIVO, COR_BOTAO_HOVER,
    COR_BOTAO_SECUNDARIO, COR_BOTAO_SECUNDARIO_HOVER,
    COR_LOGOUT_BG, COR_LOGOUT_HOVER, COR_LOGOUT_TEXTO,
    COR_FECHAR_BG, COR_FECHAR_HOVER, COR_FECHAR_TEXTO,
    fonte, fonte_titulo, fonte_subtitulo, fonte_corpo, fonte_pequena,
)




class EmConstrucaoView(ctk.CTkFrame):
    """Placeholder para as views que ainda não foram implementadas."""

    def __init__(self, parent, titulo="Em construção"):
        super().__init__(
            parent,
            fg_color="transparent"
        )

        ctk.CTkLabel(
            self,
            text="🚧",
            font=fonte(48)
        ).pack(
            pady=(80, 10)
        )

        ctk.CTkLabel(
            self,
            text=titulo,
            font=fonte(22, "bold"),
        ).pack()

        ctk.CTkLabel(
            self,
            text="Esta tela ainda está em desenvolvimento.",
            font=fonte(14),
            text_color=COR_TEXTO_TERCIARIO,
        ).pack(
            pady=5
        )


class MenuView(ctk.CTkFrame):
    """Janela principal: menu lateral + área de conteúdo."""

    def __init__(self, parent, usuario_logado=None, on_logout=None):
        super().__init__(
            parent,
            fg_color="transparent"
        )

        self.parent = parent
        self.usuario_logado = usuario_logado or {
            "id": 1,
            "nome": "Usuário",
            "email": "usuario@exemplo.com",
            "tipo_perfil": "PF",
        }
        self.on_logout = on_logout

        # Views já criadas
        self.views = {}

        # View atualmente exibida
        self.view_atual = None

        # Botões do menu
        self.botoes = {}

        # Itens do menu
        self.itens_menu = [
            (
                "saude",
                "📊  Dashboard & Saúde",
                SaudeFinanceiraView
            ),
            (
                "assistente_ia",
                "🤖  Assistente IA",
                AssistenteIAView
            ),
            (
                "lancamento",
                "💰  Lançamentos",
                LancamentoView
            ),
            (
                "meta",
                "🎯  Metas",
                MetaView
            ),
            (
                "simulador",
                "🔮  Simulador de Cenários",
                SimuladorView
            ),
            (
                "relatorio",
                "📄  Relatório Mensal",
                RelatorioView
            ),
            (
                "terceiro",
                "🤝  Terceiros",
                TerceiroView
            ),
            (
                "categoria",
                "🏷️  Categorias",
                CategoriaView
            ),
            (
                "usuario",
                "👤  Meu Perfil",
                UsuarioView
            ),
        ]

        # Breve explicação de cada tela exibida no canto
        self.explicacoes_telas = {
            "saude": "💡 Visão geral da saúde financeira, saldos e score mensal",
            "assistente_ia": "💡 Assistência inteligente e recomendações personalizadas",
            "lancamento": "💡 Registro e acompanhamento de receitas, despesas e fluxo",
            "meta": "💡 Planejamento de objetivos e progresso de economia para sonhos",
            "simulador": "💡 Teste de corte de gastos e renda extra sem alterar dados reais",
            "relatorio": "💡 Demonstrativos mensais consolidados, gráficos e balanços",
            "terceiro": "💡 Cadastro e controle de contatos, clientes e fornecedores",
            "categoria": "💡 Organização de despesas e limites de orçamento por categoria",
            "usuario": "💡 Dados cadastrais, segurança da conta e preferências de perfil",
        }

        # Layout principal
        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )

        # Inicializar gerenciador de notificações
        self.notificador = GerenciadorNotificacoes(self.winfo_toplevel())

        # Criar interface
        self._build_sidebar()
        self._build_conteudo()

        # Tela inicial
        self.selecionar("saude")

    # ==============================================================
    # SIDEBAR
    # ==============================================================

    def _build_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=COR_SIDEBAR,
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)

        # Espaço para empurrar opções para baixo
        self.sidebar.grid_rowconfigure(
            len(self.itens_menu) + 2,
            weight=1
        )

        # Card do Usuário Logado no topo da Sidebar
        card_user = ctk.CTkFrame(
            self.sidebar,
            fg_color=COR_CARD_USER_BG,
            corner_radius=10,
            border_width=1,
            border_color=COR_CARD_USER_BORDA,
        )
        card_user.grid(row=0, column=0, padx=12, pady=(15, 12), sticky="ew")
        card_user.grid_columnconfigure(1, weight=1)

        # Iniciais
        nome_completo = self.usuario_logado.get("nome", "Usuário")
        partes_nome = nome_completo.split()
        iniciais = (partes_nome[0][0] + (partes_nome[-1][0] if len(partes_nome) > 1 else "")).upper()

        avatar = ctk.CTkFrame(card_user, width=38, height=38, corner_radius=19, fg_color=COR_AVATAR_BG)
        avatar.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        avatar.grid_propagate(False)
        ctk.CTkLabel(
            avatar,
            text=iniciais,
            font=fonte(13, "bold"),
            text_color=COR_AVATAR_TEXTO,
        ).pack(expand=True)

        ctk.CTkLabel(
            card_user,
            text=nome_completo[:16],
            font=fonte(12, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        ).grid(row=0, column=1, sticky="w", pady=(8, 0))

        tipo_badge = f"Perfil {self.usuario_logado.get('tipo_perfil', 'PF')}"
        ctk.CTkLabel(
            card_user,
            text=tipo_badge,
            font=fonte(10),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).grid(row=1, column=1, sticky="w", pady=(0, 8))

        # Botões do Menu
        for i, (chave, texto, _) in enumerate(
            self.itens_menu,
            start=1
        ):

            botao = ctk.CTkButton(
                self.sidebar,
                text=texto,
                anchor="w",
                height=40,
                corner_radius=8,
                fg_color=COR_BOTAO_NORMAL,
                text_color=(COR_TEXTO_PRINCIPAL, COR_TEXTO_PRINCIPAL),
                hover_color=(COR_BOTAO_HOVER, COR_BOTAO_HOVER),
                font=fonte(13),
                command=lambda c=chave: self.selecionar(c)
            )

            botao.grid(
                row=i,
                column=0,
                padx=12,
                pady=3,
                sticky="ew"
            )

            self.botoes[chave] = botao

        # Tema
        self.opcao_tema = ctk.CTkOptionMenu(
            self.sidebar,
            values=[
                "Dark",
                "Light",
                "System"
            ],
            command=ctk.set_appearance_mode,
            width=210,
            fg_color=COR_BOTAO_SECUNDARIO,
            button_color=COR_ACENTO_PRIMARIO,
            font=fonte(12),
        )

        self.opcao_tema.set("Dark")

        self.opcao_tema.grid(
            row=len(self.itens_menu) + 3,
            column=0,
            padx=15,
            pady=(10, 6)
        )

        # Botão Desconectar / Logout
        if self.on_logout:
            btn_logout = ctk.CTkButton(
                self.sidebar,
                text="🚪 Desconectar",
                width=210,
                height=32,
                fg_color=COR_LOGOUT_BG,
                hover_color=COR_LOGOUT_HOVER,
                text_color=COR_LOGOUT_TEXTO,
                font=fonte(12),
                command=self.on_logout,
            )
            btn_logout.grid(
                row=len(self.itens_menu) + 4,
                column=0,
                padx=15,
                pady=(0, 6)
            )

        # Botão sair do aplicativo
        ctk.CTkButton(
            self.sidebar,
            text="Fechar App",
            width=210,
            height=32,
            fg_color=COR_FECHAR_BG,
            hover_color=COR_FECHAR_HOVER,
            text_color=COR_FECHAR_TEXTO,
            font=fonte(12),
            command=self.parent.destroy
        ).grid(
            row=len(self.itens_menu) + 5,
            column=0,
            padx=15,
            pady=(0, 15)
        )

    # ==============================================================
    # ÁREA DE CONTEÚDO
    # ==============================================================

    def _build_conteudo(self):

        self.area_conteudo = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.area_conteudo.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=20,
            pady=20
        )

        self.area_conteudo.grid_columnconfigure(
            0,
            weight=1
        )

        self.area_conteudo.grid_rowconfigure(
            1,
            weight=1
        )

        # Cabeçalho da tela (Título à esquerda + Breve explicação no canto direito)
        self.header_tela = ctk.CTkFrame(
            self.area_conteudo,
            fg_color="transparent"
        )
        self.header_tela.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 15)
        )
        self.header_tela.grid_columnconfigure(0, weight=1)

        self.titulo_tela = ctk.CTkLabel(
            self.header_tela,
            text="",
            font=fonte_titulo(),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w"
        )
        self.titulo_tela.grid(
            row=0,
            column=0,
            sticky="w"
        )

        # Card informativo no canto direito
        self.card_info_tela = ctk.CTkFrame(
            self.header_tela,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
            corner_radius=8,
        )
        self.card_info_tela.grid(
            row=0,
            column=1,
            sticky="e",
            padx=(10, 0)
        )

        self.lbl_info_tela = ctk.CTkLabel(
            self.card_info_tela,
            text="",
            font=fonte(11),
            text_color=COR_TEXTO_SECUNDARIO,
            padx=12,
            pady=5,
        )
        self.lbl_info_tela.pack()

        # Container das telas
        #
        # IMPORTANTE:
        # Não usamos CTkScrollableFrame aqui.
        # Cada View passa a ocupar todo o espaço disponível.
        self.container = ctk.CTkFrame(
            self.area_conteudo,
            fg_color="transparent"
        )

        self.container.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        self.container.grid_columnconfigure(
            0,
            weight=1
        )

        self.container.grid_rowconfigure(
            0,
            weight=1
        )

    # ==============================================================
    # NAVEGAÇÃO
    # ==============================================================

    def selecionar(self, chave):

        # ----------------------------------------------------------
        # Descobrir a view correspondente
        # ----------------------------------------------------------

        texto = None
        classe_view = None

        for c, t, v in self.itens_menu:

            if c == chave:
                texto = t
                classe_view = v
                break

        if texto is None:
            return

        # ----------------------------------------------------------
        # Atualizar aparência dos botões
        # ----------------------------------------------------------

        for c, botao in self.botoes.items():

            if c == chave:

                botao.configure(
                    fg_color=(
                        COR_BOTAO_ATIVO,
                        COR_BOTAO_ATIVO,
                    )
                )

            else:

                botao.configure(
                    fg_color="transparent"
                )

        # ----------------------------------------------------------
        # ESCONDER A VIEW ATUAL
        # ----------------------------------------------------------

        if self.view_atual is not None:

            self.view_atual.grid_forget()

        # ----------------------------------------------------------
        # Criar a nova view se ainda não existir
        # ----------------------------------------------------------

        if chave not in self.views:

            titulo_limpo = texto.split(
                "  ",
                1
            )[-1]

            if classe_view is None:

                nova_view = EmConstrucaoView(
                    self.container,
                    titulo=titulo_limpo
                )

            else:
                if classe_view == UsuarioView:
                    nova_view = classe_view(self.container, usuario_atual=self.usuario_logado)
                else:
                    nova_view = classe_view(self.container)

            self.views[chave] = nova_view

        # ----------------------------------------------------------
        # Pegar a view
        # ----------------------------------------------------------

        self.view_atual = self.views[chave]

        # ----------------------------------------------------------
        # Atualizar dados
        # ----------------------------------------------------------

        if hasattr(
            self.view_atual,
            "atualizar_dados"
        ):

            self.view_atual.atualizar_dados()

        # ----------------------------------------------------------
        # MOSTRAR A NOVA VIEW
        # ----------------------------------------------------------

        self.view_atual.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        # ----------------------------------------------------------
        # Atualizar título
        # ----------------------------------------------------------

        titulo_limpo = texto.split(
            "  ",
            1
        )[-1]

        self.titulo_tela.configure(
            text=titulo_limpo
        )

        # Atualizar explicação contextual no canto superior
        explicacao = self.explicacoes_telas.get(chave, "")
        self.lbl_info_tela.configure(
            text=explicacao
        )


# ==============================================================
# TESTE
# ==============================================================

if __name__ == "__main__":

    app = ctk.CTk()

    app.title(
        "Gerenciador Financeiro Pessoal"
    )

    app.geometry(
        "1100x700"
    )

    app.minsize(
        900,
        600
    )

    menu = MenuView(app)

    menu.pack(
        expand=True,
        fill="both"
    )

    app.mainloop()