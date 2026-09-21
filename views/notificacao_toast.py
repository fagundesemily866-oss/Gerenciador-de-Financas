"""
Sistema de Notificações Toast.
===============================

Componente visual que exibe notificações modernas no estilo toast,
posicionadas no canto superior direito da janela principal.

Uso:
    from views.notificacao_toast import GerenciadorNotificacoes

    # Inicializar uma vez (preferencialmente no main ou MenuView)
    notificador = GerenciadorNotificacoes(janela_principal)

    # Disparar notificações de qualquer lugar
    notificador.sucesso("Lançamento salvo com sucesso!")
    notificador.erro("Erro ao excluir categoria.")
    notificador.info("Registro atualizado.")
    notificador.aviso("Você está próximo do limite mensal!")
    notificador.ia("Resposta do assistente pronta.")
"""
import customtkinter as ctk


class _ToastNotificacao(ctk.CTkFrame):
    """Uma notificação toast individual."""

    # Cores por tipo
    CORES = {
        "sucesso": {
            "bg": "#1A3A2A",
            "borda": "#2ECC71",
            "icone": "✅",
            "titulo_cor": "#2ECC71",
        },
        "erro": {
            "bg": "#3A1A1A",
            "borda": "#E74C3C",
            "icone": "❌",
            "titulo_cor": "#E74C3C",
        },
        "info": {
            "bg": "#1A2A3A",
            "borda": "#3498DB",
            "icone": "ℹ️",
            "titulo_cor": "#3498DB",
        },
        "aviso": {
            "bg": "#3A3A1A",
            "borda": "#F39C12",
            "icone": "⚠️",
            "titulo_cor": "#F39C12",
        },
        "ia": {
            "bg": "#2A1A3A",
            "borda": "#9B59B6",
            "icone": "🤖",
            "titulo_cor": "#9B59B6",
        },
    }

    TITULOS = {
        "sucesso": "Sucesso",
        "erro": "Erro",
        "info": "Informação",
        "aviso": "Aviso",
        "ia": "Assistente IA",
    }

    def __init__(self, parent, tipo: str, mensagem: str, gerenciador, duracao_ms: int = 4000, largura: int = 320):
        cores = self.CORES.get(tipo, self.CORES["info"])

        super().__init__(
            parent,
            fg_color=cores["bg"],
            corner_radius=12,
            border_width=2,
            border_color=cores["borda"],
            width=largura,
        )

        self.gerenciador = gerenciador
        self.duracao_ms = duracao_ms
        self._timer_id = None

        # Layout interno
        self.grid_columnconfigure(1, weight=1)

        # Ícone
        ctk.CTkLabel(
            self,
            text=cores["icone"],
            font=ctk.CTkFont(size=20),
            width=30,
        ).grid(row=0, column=0, rowspan=2, padx=(12, 6), pady=10)

        # Título
        ctk.CTkLabel(
            self,
            text=self.TITULOS.get(tipo, "Info"),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=cores["titulo_cor"],
            anchor="w",
        ).grid(row=0, column=1, sticky="w", pady=(10, 0))

        # Mensagem (truncada se muito longa)
        texto_msg = mensagem if len(mensagem) <= 80 else mensagem[:77] + "..."
        ctk.CTkLabel(
            self,
            text=texto_msg,
            font=ctk.CTkFont(size=11),
            text_color="#CDD6F4",
            anchor="w",
            wraplength=230,
        ).grid(row=1, column=1, sticky="w", pady=(0, 10))

        # Botão fechar
        btn_fechar = ctk.CTkButton(
            self,
            text="✕",
            width=24,
            height=24,
            corner_radius=12,
            fg_color="transparent",
            hover_color="#45475A",
            text_color="#A6ADC8",
            font=ctk.CTkFont(size=12),
            command=self._fechar,
        )
        btn_fechar.grid(row=0, column=2, padx=(4, 8), pady=(8, 0), sticky="ne")

        # Timer para auto-destruição
        self._timer_id = self.after(self.duracao_ms, self._fechar)

    def _fechar(self):
        """Remove esta notificação e reorganiza a pilha."""
        if self._timer_id:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

        self.gerenciador._remover_toast(self)


class GerenciadorNotificacoes:
    """
    Gerenciador central de notificações toast.

    Responsável por criar, empilhar e remover notificações na janela principal.
    """

    _instancia = None

    def __init__(self, janela_root: ctk.CTk):
        self.root = janela_root
        self._toasts: list[_ToastNotificacao] = []
        self._largura_toast = 320
        self._margem_topo = 15
        self._margem_direita = 15
        self._espaco_entre = 8

        # Salvar como instância global acessível
        GerenciadorNotificacoes._instancia = self

    @classmethod
    def obter_instancia(cls) -> "GerenciadorNotificacoes":
        """Retorna a instância singleton do gerenciador."""
        return cls._instancia

    # ------------------------------------------------------------------
    # Métodos públicos de conveniência
    # ------------------------------------------------------------------
    def sucesso(self, mensagem: str):
        """Exibe notificação de sucesso (verde)."""
        self._criar_toast("sucesso", mensagem)

    def erro(self, mensagem: str):
        """Exibe notificação de erro (vermelho)."""
        self._criar_toast("erro", mensagem)

    def info(self, mensagem: str):
        """Exibe notificação informativa (azul)."""
        self._criar_toast("info", mensagem)

    def aviso(self, mensagem: str):
        """Exibe notificação de aviso (amarelo)."""
        self._criar_toast("aviso", mensagem)

    def ia(self, mensagem: str):
        """Exibe notificação da IA (roxo)."""
        self._criar_toast("ia", mensagem)

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------
    def _criar_toast(self, tipo: str, mensagem: str):
        """Cria e posiciona uma nova notificação toast."""
        toast = _ToastNotificacao(
            self.root,
            tipo=tipo,
            mensagem=mensagem,
            gerenciador=self,
            largura=self._largura_toast,
        )

        self._toasts.append(toast)
        self._reposicionar_toasts()

    def _remover_toast(self, toast: _ToastNotificacao):
        """Remove um toast da lista e reorganiza."""
        if toast in self._toasts:
            self._toasts.remove(toast)
        try:
            toast.destroy()
        except Exception:
            pass
        self._reposicionar_toasts()

    def _reposicionar_toasts(self):
        """Recalcula posição Y de cada toast ativo."""
        y_offset = self._margem_topo

        for toast in self._toasts:
            # Posiciona no canto superior direito usando place (sem width/height aqui)
            toast.place(
                relx=1.0,
                x=-(self._margem_direita),
                y=y_offset,
                anchor="ne",
            )
            toast.lift()  # Garantir que fica acima de tudo

            # Atualizar posição para o próximo toast
            toast.update_idletasks()
            altura = toast.winfo_reqheight()
            y_offset += altura + self._espaco_entre
