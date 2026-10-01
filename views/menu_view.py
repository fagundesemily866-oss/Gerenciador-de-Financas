import customtkinter as ctk
from PIL import Image

# Importações lazy (feitas só quando a view é aberta pela 1a vez)
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


# Mapa de imports lazy: chave -> (módulo, classe)
_VIEWS_LAZY = {
    "saude": ("views.saude_financeira_view", "SaudeFinanceiraView"),
    "assistente_ia": ("views.assistente_ia_view", "AssistenteIAView"),
    "lancamento": ("views.lancamento_view", "LancamentoView"),
    "meta": ("views.meta_view", "MetaView"),
    "simulador": ("views.simulador_view", "SimuladorView"),
    "relatorio": ("views.relatorio_view", "RelatorioView"),
    "terceiro": ("views.terceiro_view", "TerceiroView"),
    "categoria": ("views.categoria_view", "CategoriaView"),
    "usuario": ("views.usuario_view", "UsuarioView"),
}


def _import_view_class(chave: str):
    """Importa dinamicamente a classe de view sob demanda."""
    if chave not in _VIEWS_LAZY:
        return None
    modulo_path, classe_nome = _VIEWS_LAZY[chave]
    import importlib
    modulo = importlib.import_module(modulo_path)
    return getattr(modulo, classe_nome)





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
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Estado da sidebar (expandida=True / recolhida=False)
        self._sidebar_expandida = True
        self.SIDEBAR_LARGURA = 240
        self.SIDEBAR_MINI = 58

        # Inicializar gerenciador de notificações
        self.notificador = GerenciadorNotificacoes(self.winfo_toplevel())

        # Criar interface
        self._build_sidebar()
        self._build_conteudo()

        # Tela inicial
        self.selecionar("saude")

        # Adaptar layout quando a janela for redimensionada
        self.winfo_toplevel().bind("<Configure>", self._on_resize, add="+")

    # ==============================================================
    # SIDEBAR
    # ==============================================================

    # ==============================================================
    # SIDEBAR
    # ==============================================================

    def _on_resize(self, event=None):
        """Recolhe automaticamente a sidebar quando a janela fica muito estreita."""
        try:
            largura = self.winfo_toplevel().winfo_width()
        except Exception:
            return
        if largura < 1100 and self._sidebar_expandida:
            self._recolher_sidebar()
        elif largura >= 1100 and not self._sidebar_expandida:
            self._expandir_sidebar()

    def _recolher_sidebar(self):
        self._sidebar_expandida = False
        self.sidebar.configure(width=self.SIDEBAR_MINI)
        # Oculta textos do logo
        for w in self._sidebar_texto_widgets:
            try:
                w.pack_forget()
            except Exception:
                pass
        # Oculta card do usuário
        try:
            self.card_user.pack_forget()
        except Exception:
            pass
        # Botões viram só ícone, centralizado
        for chave, botao in self.botoes.items():
            botao.configure(
                text=getattr(botao, "_icone_mini", "●"),
                anchor="center",
                width=42,
            )
        self._btn_toggle.configure(text="›")

    def _expandir_sidebar(self):
        self._sidebar_expandida = True
        self.sidebar.configure(width=self.SIDEBAR_LARGURA)
        # Restaura textos do logo
        for w in self._sidebar_texto_widgets:
            try:
                w.pack(anchor="w")
            except Exception:
                pass
        # Restaura card do usuário
        try:
            self.card_user.pack(fill="x", padx=14, pady=(0, 14))
        except Exception:
            pass
        # Botões restauram texto completo
        for chave, botao in self.botoes.items():
            botao.configure(
                text=getattr(botao, "_texto_completo", chave),
                anchor="w",
                width=0,
            )
        self._btn_toggle.configure(text="‹")

    def _toggle_sidebar(self):
        if self._sidebar_expandida:
            self._recolher_sidebar()
        else:
            self._expandir_sidebar()

    def _build_sidebar(self):
        self._sidebar_texto_widgets = []
        self._sidebar_icone_widgets = []

        self.sidebar = ctk.CTkFrame(
            self,
            width=self.SIDEBAR_LARGURA,
            corner_radius=0,
            fg_color=COR_SIDEBAR,
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
        self.sidebar.grid_propagate(False)

        # 1. LOGO + BOTÃO TOGGLE NO TOPO
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=12, pady=(14, 8))

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
        logo_icon_box.pack(side="left", padx=(0, 8))
        logo_icon_box.pack_propagate(False)

        ctk.CTkLabel(
            logo_icon_box,
            text="📊",
            font=fonte(18),
        ).place(relx=0.5, rely=0.5, anchor="center")

        logo_text_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        logo_text_frame.pack(side="left", fill="both", expand=True)

        lbl_g = ctk.CTkLabel(
            logo_text_frame,
            text="Gerenciador de",
            font=fonte(12, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        )
        lbl_g.pack(anchor="w")
        self._sidebar_texto_widgets.append(lbl_g)

        lbl_f = ctk.CTkLabel(
            logo_text_frame,
            text="Finanças Pessoais",
            font=fonte(11),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        )
        lbl_f.pack(anchor="w")
        self._sidebar_texto_widgets.append(lbl_f)

        # Botão toggle de colapso
        self._btn_toggle = ctk.CTkButton(
            logo_frame,
            text="‹",
            width=28,
            height=28,
            corner_radius=8,
            fg_color=COR_CARD_INTERNO,
            hover_color=COR_CARD_HOVER,
            text_color=COR_TEXTO_SECUNDARIO,
            font=fonte(16, "bold"),
            command=self._toggle_sidebar,
        )
        self._btn_toggle.pack(side="right", padx=(4, 0))

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
        # Emojis para modo mini (sidebar recolhida)
        _icones_menu = {"saude": "📊", "assistente_ia": "🤖", "lancamento": "💰",
                        "meta": "🎯", "simulador": "🔮", "relatorio": "📄",
                        "terceiro": "🤝", "categoria": "🏷", "usuario": "👤"}

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
            # Guarda o texto original para restaurar depois
            botao._texto_completo = texto
            botao._icone_mini = _icones_menu.get(chave, "●")

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
        # Limpa views em cache para aplicar as cores do novo tema
        views_antigas = list(self.views.values())
        chave_atual = None
        for k, v in self.views.items():
            if v == self.view_atual:
                chave_atual = k
                break

        self.views.clear()
        self.view_atual = None

        for v in views_antigas:
            try:
                v.destroy()
            except Exception:
                pass

        if chave_atual:
            self.after(50, lambda: self.selecionar(chave_atual))

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
        texto = None
        classe_view = None

        for c, t, _ in self.itens_menu:
            if c == chave:
                texto = t
                break

        if texto is None:
            return

        # Atualizar aparência dos botões
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

        # Esconder view atual
        if self.view_atual is not None:
            self.view_atual.grid_forget()

        # Criar a nova view se ainda não existir (lazy loading)
        if chave not in self.views:
            titulo_limpo = texto.split("  ", 1)[-1]

            # Import lazy
            classe_view = _import_view_class(chave)

            if classe_view is None:
                nova_view = EmConstrucaoView(self.container, titulo=titulo_limpo)
            elif chave == "usuario":
                nova_view = classe_view(
                    self.container,
                    usuario_atual=self.usuario_logado,
                    on_foto_atualizada=self.atualizar_avatar_sidebar,
                )
            else:
                nova_view = classe_view(self.container)

            self.views[chave] = nova_view

        self.view_atual = self.views[chave]

        # Atualizar dados
        if hasattr(self.view_atual, "atualizar_dados"):
            try:
                self.view_atual.atualizar_dados()
            except Exception:
                pass

        # Mostrar a nova view
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