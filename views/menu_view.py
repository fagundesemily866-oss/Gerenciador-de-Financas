import customtkinter as ctk
from PIL import Image

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
    COR_CARD, COR_CARD_INTERNO, COR_CARD_USER_BG, COR_CARD_USER_BORDA, COR_CARD_HOVER,
    COR_BORDA, COR_SIDEBAR, COR_TEXTO_PRINCIPAL, COR_TEXTO_SECUNDARIO,
    COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED, COR_ACENTO_PRIMARIO, COR_AVATAR_BG, COR_AVATAR_TEXTO,
    COR_BOTAO_NORMAL, COR_BOTAO_ATIVO, COR_BOTAO_ATIVO_TEXTO, COR_BOTAO_HOVER,
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

        # Imagem do avatar da sidebar (mantém referência para não ser coletada pelo GC)
        self.avatar_image = None

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

        # 1. LOGO NO TOPO
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(18, 12))

        # Ícone estilizado do Logo
        logo_icon_box = ctk.CTkFrame(
            logo_frame,
            width=36,
            height=36,
            corner_radius=10,
            fg_color=("#CCFBF1", "#0D2E2B"),
            border_width=1,
            border_color=("#99F6E4", "#134E48"),
        )
        logo_icon_box.pack(side="left", padx=(0, 10))
        logo_icon_box.pack_propagate(False)

        ctk.CTkLabel(
            logo_icon_box,
            text="📊",
            font=fonte(18),
        ).place(relx=0.5, rely=0.5, anchor="center")

        logo_text_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        logo_text_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            logo_text_frame,
            text="Gerenciador de",
            font=fonte(12, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_text_frame,
            text="Finanças Pessoais",
            font=fonte(11),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(anchor="w")

        # 2. CARD DO USUÁRIO LOGADO
        self.card_user = ctk.CTkFrame(
            self.sidebar,
            fg_color=COR_CARD_USER_BG,
            corner_radius=12,
            border_width=1,
            border_color=COR_CARD_USER_BORDA,
            cursor="hand2",
        )
        self.card_user.pack(fill="x", padx=14, pady=(0, 14))
        self.card_user.grid_columnconfigure(1, weight=1)

        nome_completo = self.usuario_logado.get("nome", "Usuário Demo")
        partes_nome = nome_completo.split()
        iniciais = (partes_nome[0][0] + (partes_nome[-1][0] if len(partes_nome) > 1 else "")).upper()

        avatar = ctk.CTkFrame(self.card_user, width=34, height=34, corner_radius=17, fg_color=COR_AVATAR_BG)
        avatar.grid(row=0, column=0, rowspan=2, padx=(10, 8), pady=8)
        avatar.grid_propagate(False)

        self.lbl_avatar = ctk.CTkLabel(
            avatar,
            text=iniciais,
            font=fonte(12, "bold"),
            text_color=COR_AVATAR_TEXTO,
        )
        self.lbl_avatar.pack(expand=True)

        lbl_nome = ctk.CTkLabel(
            self.card_user,
            text=nome_completo[:14],
            font=fonte(11, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        )
        lbl_nome.grid(row=0, column=1, sticky="w", pady=(8, 0))

        tipo_badge = f"Perfil {self.usuario_logado.get('tipo_perfil', 'PF')}"
        lbl_tipo = ctk.CTkLabel(
            self.card_user,
            text=tipo_badge,
            font=fonte(10),
            text_color=COR_TEXTO_MUTED,
            anchor="w",
        )
        lbl_tipo.grid(row=1, column=1, sticky="w", pady=(0, 8))

        lbl_seta = ctk.CTkLabel(
            self.card_user,
            text="›",
            font=fonte(16, "bold"),
            text_color=COR_TEXTO_MUTED,
        )
        lbl_seta.grid(row=0, column=2, rowspan=2, padx=(4, 10))

        for widget in [self.card_user, avatar, self.lbl_avatar, lbl_nome, lbl_tipo, lbl_seta]:
            widget.bind("<Button-1>", lambda e: self.selecionar("usuario"))

        # 3. CONTAINER COM OS BOTÕES DO MENU (ROLÁVEL SE NECESSÁRIO EM TELAS PEQUENAS)
        nav_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_container.pack(fill="both", expand=True, padx=12, pady=0)

        # Botões do Menu
        for chave, texto, _ in self.itens_menu:
            botao = ctk.CTkButton(
                nav_container,
                text=texto,
                anchor="w",
                height=38,
                corner_radius=8,
                fg_color="transparent",
                text_color=COR_TEXTO_SECUNDARIO,
                hover_color=COR_BOTAO_HOVER,
                font=fonte(12, "normal"),
                command=lambda c=chave: self.selecionar(c),
            )
            botao.pack(fill="x", pady=2)
            self.botoes[chave] = botao

        # 4. RODAPÉ DA SIDEBAR
        rodape_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        rodape_frame.pack(fill="x", padx=14, pady=(10, 14), side="bottom")

        # Seletor de Tema
        tema_box = ctk.CTkFrame(rodape_frame, fg_color=COR_CARD_USER_BG, corner_radius=8, border_width=1, border_color=COR_CARD_USER_BORDA)
        tema_box.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            tema_box,
            text="🌙  Tema",
            font=fonte(11),
            text_color=COR_TEXTO_SECUNDARIO,
        ).pack(side="left", padx=10, pady=4)

        self.opcao_tema = ctk.CTkOptionMenu(
            tema_box,
            values=["Dark", "Light"],
            command=self._alterar_tema,
            width=90,
            height=26,
            fg_color=COR_BOTAO_SECUNDARIO,
            button_color=COR_ACENTO_PRIMARIO,
            font=fonte(11),
        )
        self.opcao_tema.set("Dark")
        self.opcao_tema.pack(side="right", padx=6, pady=4)

        # Botão Sair da Conta / Logout
        if self.on_logout:
            btn_logout = ctk.CTkButton(
                rodape_frame,
                text="🚪  Sair da Conta",
                height=32,
                corner_radius=8,
                fg_color=COR_LOGOUT_BG,
                hover_color=COR_LOGOUT_HOVER,
                text_color=COR_LOGOUT_TEXTO,
                font=fonte(11),
                command=self.on_logout,
            )
            btn_logout.pack(fill="x", pady=(0, 6))

        # Botão Sair do Aplicativo
        ctk.CTkButton(
            rodape_frame,
            text="⏻  Fechar App",
            height=32,
            corner_radius=8,
            fg_color=COR_FECHAR_BG,
            hover_color=COR_FECHAR_HOVER,
            text_color=COR_FECHAR_TEXTO,
            font=fonte(11),
            command=self.parent.destroy,
        ).pack(fill="x")

    def _alterar_tema(self, modo: str):
        ctk.set_appearance_mode(modo)

    # ==============================================================
    # AVATAR DA SIDEBAR
    # ==============================================================

    def atualizar_avatar_sidebar(self, imagem_pil: Image.Image):
        """Recebe uma imagem PIL e atualiza o avatar circular na sidebar."""
        imagem_mini = imagem_pil.copy()
        imagem_mini.thumbnail((34, 34))

        self.avatar_image = ctk.CTkImage(
            light_image=imagem_mini,
            dark_image=imagem_mini,
            size=(34, 34),
        )

        self.lbl_avatar.configure(image=self.avatar_image, text="")

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
            padx=14,
            pady=14
        )
        self.area_conteudo.grid_columnconfigure(0, weight=1)
        self.area_conteudo.grid_rowconfigure(0, weight=1)

        # Container das telas onde as Views ocupam todo o espaço
        self.container = ctk.CTkFrame(
            self.area_conteudo,
            fg_color="transparent"
        )
        self.container.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

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
                    fg_color=COR_BOTAO_ATIVO,
                    text_color=COR_BOTAO_ATIVO_TEXTO,
                    font=fonte(12, "bold"),
                )
            else:
                botao.configure(
                    fg_color="transparent",
                    text_color=COR_TEXTO_SECUNDARIO,
                    font=fonte(12, "normal"),
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
            titulo_limpo = texto.split("  ", 1)[-1]

            if classe_view is None:
                nova_view = EmConstrucaoView(
                    self.container,
                    titulo=titulo_limpo
                )
            else:
                if classe_view == UsuarioView:
                    nova_view = classe_view(
                        self.container,
                        usuario_atual=self.usuario_logado,
                        on_foto_atualizada=self.atualizar_avatar_sidebar,
                    )
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

        if hasattr(self.view_atual, "atualizar_dados"):
            self.view_atual.atualizar_dados()

        # ----------------------------------------------------------
        # MOSTRAR A NOVA VIEW
        # ----------------------------------------------------------

        self.view_atual.grid(
            row=0,
            column=0,
            sticky="nsew"
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