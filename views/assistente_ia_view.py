"""
View do Assistente de IA.
==========================

Interface de chat integrada ao aplicativo, permitindo que o usuário
envie perguntas e receba respostas de um modelo de IA em tempo real.

A comunicação com a API é feita em thread separada para manter a
interface responsiva.
"""
import threading
import customtkinter as ctk

from services.ai_service import AIService
from views.notificacao_toast import GerenciadorNotificacoes


class _BalaoMensagem(ctk.CTkFrame):
    """Balão de mensagem individual no chat."""

    def __init__(self, parent, texto: str, eh_usuario: bool, largura_max: int = 500):
        # Cores conforme quem enviou
        if eh_usuario:
            bg_cor = "#1E3A5F"
            borda_cor = "#2980B9"
            label_cor = "#89B4FA"
            nome = "Você"
        else:
            bg_cor = "#2A1A3A"
            borda_cor = "#6C3483"
            label_cor = "#CBA6F7"
            nome = "🤖 Assistente IA"

        super().__init__(
            parent,
            fg_color=bg_cor,
            corner_radius=12,
            border_width=1,
            border_color=borda_cor,
        )

        # Nome do remetente
        ctk.CTkLabel(
            self,
            text=nome,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=label_cor,
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(8, 2))

        # Texto da mensagem
        ctk.CTkLabel(
            self,
            text=texto,
            font=ctk.CTkFont(size=13),
            text_color="#CDD6F4",
            anchor="w",
            justify="left",
            wraplength=largura_max - 40,
        ).pack(anchor="w", padx=12, pady=(2, 10))


class AssistenteIAView(ctk.CTkFrame):
    """Tela do Assistente de IA com interface de chat."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.ai_service = AIService()
        self._aguardando_resposta = False

        # Layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._criar_header()
        self._criar_area_chat()
        self._criar_area_input()

        # Mensagem de boas-vindas
        self._adicionar_mensagem_ia(
            "Olá! 👋 Sou seu assistente financeiro pessoal.\n\n"
            "Posso te ajudar com:\n"
            "💡 Dicas de economia e investimentos\n"
            "📊 Análise de gastos e orçamento\n"
            "🎯 Planejamento de metas financeiras\n"
            "📈 Estratégias para melhorar suas finanças\n\n"
            "Como posso te ajudar hoje?"
        )

        # Verificar disponibilidade
        if not self.ai_service.disponivel:
            self._adicionar_mensagem_ia(
                f"⚠️ Atenção: {self.ai_service.erro}\n\n"
                "Verifique a configuração e reinicie o aplicativo."
            )

    # ==================================================================
    # CONSTRUÇÃO DA INTERFACE
    # ==================================================================

    def _criar_header(self):
        """Cria o cabeçalho com status e botão de reset."""
        header = ctk.CTkFrame(
            self,
            fg_color="#1E1E2E",
            corner_radius=12,
            border_width=1,
            border_color="#313244",
            height=50,
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)

        # Ícone e título
        ctk.CTkLabel(
            header,
            text="🤖",
            font=ctk.CTkFont(size=22),
        ).grid(row=0, column=0, padx=(15, 5), pady=10)

        ctk.CTkLabel(
            header,
            text="Assistente Financeiro IA",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#CDD6F4",
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        # Indicador de status
        status_cor = "#2ECC71" if self.ai_service.disponivel else "#E74C3C"
        status_texto = "Online" if self.ai_service.disponivel else "Offline"

        self.lbl_status = ctk.CTkLabel(
            header,
            text=f"● {status_texto}",
            font=ctk.CTkFont(size=11),
            text_color=status_cor,
        )
        self.lbl_status.grid(row=0, column=2, padx=10)

        # Botão nova conversa
        ctk.CTkButton(
            header,
            text="🔄 Nova Conversa",
            width=130,
            height=30,
            corner_radius=8,
            fg_color="#313244",
            hover_color="#45475A",
            text_color="#CDD6F4",
            font=ctk.CTkFont(size=11),
            command=self._nova_conversa,
        ).grid(row=0, column=3, padx=(0, 12), pady=10)

    def _criar_area_chat(self):
        """Cria a área scrollável de mensagens."""
        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#181825",
            corner_radius=12,
            border_width=1,
            border_color="#313244",
            scrollbar_button_color="#313244",
            scrollbar_button_hover_color="#45475A",
        )
        self.chat_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.chat_frame.grid_columnconfigure(0, weight=1)

    def _criar_area_input(self):
        """Cria a área de entrada de texto e botão enviar."""
        input_frame = ctk.CTkFrame(
            self,
            fg_color="#1E1E2E",
            corner_radius=12,
            border_width=1,
            border_color="#313244",
            height=55,
        )
        input_frame.grid(row=2, column=0, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_propagate(False)

        # Campo de texto
        self.entry_msg = ctk.CTkEntry(
            input_frame,
            placeholder_text="Digite sua pergunta...",
            font=ctk.CTkFont(size=13),
            height=38,
            corner_radius=10,
            fg_color="#181825",
            border_color="#313244",
            text_color="#CDD6F4",
        )
        self.entry_msg.grid(row=0, column=0, sticky="ew", padx=(10, 8), pady=8)
        self.entry_msg.bind("<Return>", lambda e: self._enviar_mensagem())

        # Botão enviar
        self.btn_enviar = ctk.CTkButton(
            input_frame,
            text="Enviar ➤",
            width=100,
            height=38,
            corner_radius=10,
            fg_color="#2980B9",
            hover_color="#3498DB",
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._enviar_mensagem,
        )
        self.btn_enviar.grid(row=0, column=1, padx=(0, 10), pady=8)

    # ==================================================================
    # LÓGICA DE CHAT
    # ==================================================================

    def _enviar_mensagem(self):
        """Envia a pergunta do usuário e solicita resposta da IA."""
        mensagem = self.entry_msg.get().strip()
        if not mensagem or self._aguardando_resposta:
            return

        # Limpar campo
        self.entry_msg.delete(0, "end")

        # Mostrar mensagem do usuário
        self._adicionar_balao(mensagem, eh_usuario=True)

        # Indicador de loading
        self._aguardando_resposta = True
        self.btn_enviar.configure(state="disabled", text="⏳ ...")
        self._mostrar_indicador_digitando()

        # Enviar para IA em thread separada
        thread = threading.Thread(
            target=self._processar_resposta_ia,
            args=(mensagem,),
            daemon=True,
        )
        thread.start()

    def _processar_resposta_ia(self, mensagem: str):
        """Executa a chamada à API em background (thread)."""
        resposta = self.ai_service.enviar_pergunta(mensagem)

        # Atualizar UI na thread principal
        self.after(0, self._receber_resposta, resposta)

    def _receber_resposta(self, resposta: str):
        """Callback executado na thread principal ao receber resposta."""
        # Remover indicador de digitando
        self._remover_indicador_digitando()

        # Mostrar resposta
        self._adicionar_mensagem_ia(resposta)

        # Restaurar botão
        self._aguardando_resposta = False
        self.btn_enviar.configure(state="normal", text="Enviar ➤")

        # Notificação toast
        notificador = GerenciadorNotificacoes.obter_instancia()
        if notificador:
            notificador.ia("Resposta do assistente pronta!")

    def _adicionar_mensagem_ia(self, texto: str):
        """Adiciona uma mensagem da IA no chat."""
        self._adicionar_balao(texto, eh_usuario=False)

    def _adicionar_balao(self, texto: str, eh_usuario: bool):
        """Adiciona um balão de mensagem ao chat."""
        # Frame wrapper para alinhamento
        wrapper = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        wrapper.pack(fill="x", padx=10, pady=4)
        wrapper.grid_columnconfigure(0, weight=1)

        balao = _BalaoMensagem(wrapper, texto, eh_usuario)

        if eh_usuario:
            balao.pack(anchor="e", padx=(60, 0))
        else:
            balao.pack(anchor="w", padx=(0, 60))

        # Scroll para o final
        self.chat_frame.after(50, self._scroll_para_baixo)

    def _scroll_para_baixo(self):
        """Rola o chat até a última mensagem."""
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def _mostrar_indicador_digitando(self):
        """Mostra indicador de que a IA está pensando."""
        self._frame_digitando = ctk.CTkFrame(
            self.chat_frame, fg_color="transparent"
        )
        self._frame_digitando.pack(fill="x", padx=10, pady=4)

        indicador = ctk.CTkFrame(
            self._frame_digitando,
            fg_color="#2A1A3A",
            corner_radius=12,
            border_width=1,
            border_color="#6C3483",
        )
        indicador.pack(anchor="w", padx=(0, 60))

        ctk.CTkLabel(
            indicador,
            text="🤖 Pensando...",
            font=ctk.CTkFont(size=12),
            text_color="#CBA6F7",
        ).pack(padx=15, pady=10)

        self.chat_frame.after(50, self._scroll_para_baixo)

    def _remover_indicador_digitando(self):
        """Remove o indicador de digitando."""
        if hasattr(self, "_frame_digitando") and self._frame_digitando:
            try:
                self._frame_digitando.destroy()
            except Exception:
                pass
            self._frame_digitando = None

    def _nova_conversa(self):
        """Reinicia a conversa."""
        # Limpar chat
        for widget in self.chat_frame.winfo_children():
            widget.destroy()

        # Resetar serviço
        self.ai_service.resetar_conversa()

        # Mensagem de boas-vindas novamente
        self._adicionar_mensagem_ia(
            "Conversa reiniciada! 🔄\n\n"
            "Como posso te ajudar agora?"
        )

        # Notificação
        notificador = GerenciadorNotificacoes.obter_instancia()
        if notificador:
            notificador.info("Conversa reiniciada.")
