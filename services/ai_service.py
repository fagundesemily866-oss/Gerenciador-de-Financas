"""
Serviço de Integração com IA (Google GenAI / Gemini).
=====================================================

Carrega a chave da API do arquivo .env e fornece métodos para
enviar perguntas ao modelo, recebendo respostas em linguagem natural.

A comunicação com a API é feita de forma síncrona neste serviço;
a View responsável deve chamar os métodos em thread separada para
não travar a interface gráfica.
"""
import os
from typing import Optional

from dotenv import load_dotenv

# Carrega variáveis do .env (busca na raiz do projeto)
load_dotenv()

# Tenta carregar a nova biblioteca oficial google-genai, com fallback para google-generativeai
try:
    from google import genai
    from google.genai import types as genai_types
    HAS_GENAI = True
except ImportError:
    genai = None
    genai_types = None
    HAS_GENAI = False

if not HAS_GENAI:
    try:
        import google.generativeai as legacy_genai
        HAS_LEGACY_GENAI = True
    except ImportError:
        legacy_genai = None
        HAS_LEGACY_GENAI = False
else:
    legacy_genai = None
    HAS_LEGACY_GENAI = False



class AIService:
    """Wrapper para comunicação com a API Gemini do Google."""

    SYSTEM_INSTRUCTION = (
        "Você é um consultor financeiro pessoal integrado a um aplicativo de "
        "gerenciamento de finanças. Responda de forma clara, objetiva e em "
        "português do Brasil. Foque em dicas práticas de economia, "
        "investimentos, controle de gastos e planejamento financeiro. "
        "Quando fizer sentido, use emojis para tornar a resposta mais "
        "amigável. Mantenha respostas curtas e diretas (máximo ~200 palavras)."
    )

    MODELOS_PREFERENCIAIS = [
        "gemini-3.5-flash-lite",
        "gemini-3.6-flash",
        "gemini-flash-latest",
        "gemini-2.5-flash",
    ]

    def __init__(self):
        self._api_key: Optional[str] = os.getenv("AI_API_KEY")
        self._client = None
        self._chat = None
        self._model_name: str = os.getenv("AI_MODEL", "gemini-3.5-flash-lite")
        self._inicializado = False
        self._erro_inicializacao: Optional[str] = None
        self._modo_novo_sdk = False

        self._inicializar()

    # ------------------------------------------------------------------
    # Inicialização
    # ------------------------------------------------------------------
    def _inicializar(self):
        """Configura o cliente da API e cria a sessão de chat."""
        if not HAS_GENAI and not HAS_LEGACY_GENAI:
            self._erro_inicializacao = (
                "Nenhum pacote do Google Gemini instalado.\n"
                "Execute: pip install google-genai python-dotenv"
            )
            return

        if not self._api_key:
            self._erro_inicializacao = (
                "Chave de API não encontrada.\n"
                "Verifique se o arquivo .env contém a variável AI_API_KEY."
            )
            return

        # Limpa espaços acidentais ou aspas que o usuário possa ter colocado
        self._api_key = self._api_key.strip().strip("'\"() ")

        # 1. Tentar com o novo SDK google-genai
        if HAS_GENAI:
            try:
                self._client = genai.Client(api_key=self._api_key)
                self._chat = self._client.chats.create(
                    model=self._model_name,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=self.SYSTEM_INSTRUCTION
                    ),
                )
                self._modo_novo_sdk = True
                self._inicializado = True
                return
            except Exception as exc:
                self._erro_inicializacao = f"Erro ao configurar IA (google-genai): {exc}"

        # 2. Fallback para SDK legado google-generativeai
        if HAS_LEGACY_GENAI:
            try:
                legacy_genai.configure(api_key=self._api_key)
                model = legacy_genai.GenerativeModel(
                    model_name=self._model_name,
                    system_instruction=self.SYSTEM_INSTRUCTION,
                )
                self._chat = model.start_chat(history=[])
                self._modo_novo_sdk = False
                self._inicializado = True
                self._erro_inicializacao = None
                return
            except Exception as exc:
                self._erro_inicializacao = f"Erro ao configurar IA: {exc}"

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    @property
    def disponivel(self) -> bool:
        """Retorna True se o serviço está pronto para uso."""
        return self._inicializado

    @property
    def erro(self) -> Optional[str]:
        """Retorna mensagem de erro de inicialização, se houver."""
        return self._erro_inicializacao

    def enviar_pergunta(self, mensagem: str) -> str:
        """
        Envia uma pergunta ao modelo e retorna a resposta como texto.

        Parâmetros
        ----------
        mensagem : str
            Texto da pergunta do usuário.

        Retorna
        -------
        str
            Resposta do modelo ou mensagem de erro amigável.
        """
        if not self._inicializado:
            return (
                f"⚠️ Assistente indisponível.\n{self._erro_inicializacao or ''}"
            )

        if not mensagem or not mensagem.strip():
            return "Por favor, digite uma pergunta."

        try:
            response = self._chat.send_message(mensagem.strip())
            return response.text
        except Exception as exc:
            msg_erro = str(exc)
            # Tratamento de mensagens amigáveis em português
            if "API_KEY_INVALID" in msg_erro or "API key not valid" in msg_erro:
                return (
                    "❌ Chave de API inválida.\n"
                    "Verifique a chave informada no arquivo .env."
                )
            if "NOT_FOUND" in msg_erro or "is not found" in msg_erro:
                return (
                    f"❌ Modelo '{self._model_name}' não encontrado ou indisponível.\n"
                    f"Detalhes: {msg_erro}"
                )
            if "RESOURCE_EXHAUSTED" in msg_erro or "429" in msg_erro:
                return (
                    "⚠️ Limite de requisições atingido. Por favor, aguarde alguns instantes."
                )
            return f"❌ Erro ao se comunicar com a IA: {msg_erro}"

    def resetar_conversa(self):
        """Reinicia o histórico de conversa."""
        if not self._inicializado:
            return

        if self._modo_novo_sdk and self._client:
            self._chat = self._client.chats.create(
                model=self._model_name,
                config=genai_types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_INSTRUCTION
                ),
            )
        elif not self._modo_novo_sdk and HAS_LEGACY_GENAI:
            model = legacy_genai.GenerativeModel(
                model_name=self._model_name,
                system_instruction=self.SYSTEM_INSTRUCTION,
            )
            self._chat = model.start_chat(history=[])
