"""
Módulo de Tema Visual — Paleta Relaxante Verde-Esmeralda
========================================================

Paleta inspirada na identidade visual do app (carteira verde com gráfico).
Tons suaves de verde e teal que transmitem calma e confiança ao usuário.
"""

import customtkinter as ctk

# ──────────────────────────────────────────────────────────────
# PALETA DE CORES — "Modern Fintech Dark & Clean Light"
# ──────────────────────────────────────────────────────────────

# Fundos e superfícies
COR_FUNDO_PRINCIPAL = ("#F1F5F9", "#0B131B")       # Fundo base da janela
COR_SIDEBAR = ("#E2E8F0", "#091017")               # Sidebar
COR_CARD = ("#FFFFFF", "#101C26")                  # Cards e painéis principais
COR_CARD_INTERNO = ("#F8FAFC", "#152330")          # Inputs, tabelas e subcards
COR_CARD_HOVER = ("#F1F5F9", "#192A3A")            # Efeito hover para cards
COR_BORDA = ("#CBD5E1", "#1E3143")                 # Bordas sutis e divisores

# Texto
COR_TEXTO_PRINCIPAL = ("#0F172A", "#FFFFFF")       # Contraste alto para títulos e valores
COR_TEXTO_SECUNDARIO = ("#334155", "#94A3B8")      # Rótulos e subtítulos
COR_TEXTO_TERCIARIO = ("#64748B", "#64748B")       # Textos auxiliares e hints
COR_TEXTO_MUTED = ("#94A3B8", "#475569")           # Metadados e textos discretos

# Acentos
COR_ACENTO_PRIMARIO = ("#059669", "#00D084")       # Verde-Esmeralda / Teal brilhante das fotos
COR_ACENTO_HOVER = ("#047857", "#00B875")          # Hover do destaque
COR_ACENTO_ROXO = ("#7C3AED", "#8B5CF6")           # Roxo (IA, tags, destaques especiais)
COR_ACENTO_ROXO_HOVER = ("#6D28D9", "#7C3AED")
COR_SUCESSO = ("#16A34A", "#00D084")              # Verde (receitas, metas concluídas)
COR_SUCESSO_HOVER = ("#15803D", "#00B875")        # Hover do sucesso
COR_ALERTA = ("#DC2626", "#F43F5E")               # Vermelho/Coral (despesas, alertas)
COR_ALERTA_HOVER = ("#B91C1C", "#E11D48")         # Hover do alerta
COR_AVISO = ("#D97706", "#F59E0B")                # Âmbar/Laranja (atenção)
COR_INFO = ("#0284C7", "#38BDF8")                 # Azul informativo

# Elementos interativos (sidebar)
COR_BOTAO_NORMAL = "transparent"
COR_BOTAO_ATIVO = ("#CCFBF1", "#102F33")           # Botão selecionado no menu (fundo teal escuro)
COR_BOTAO_ATIVO_TEXTO = ("#0F766E", "#00D084")     # Texto do botão selecionado
COR_BOTAO_HOVER = ("#E2E8F0", "#14222E")           # Hover na barra
COR_BOTAO_SECUNDARIO = ("#E2E8F0", "#152330")      # Botões secundários
COR_BOTAO_SECUNDARIO_HOVER = ("#CBD5E1", "#1E3143")

# Avatar / Card do Usuário
COR_AVATAR_BG = ("#D1FAE5", "#0F3836")
COR_AVATAR_TEXTO = ("#047857", "#00D084")
COR_CARD_USER_BG = ("#F8FAFC", "#101D27")
COR_CARD_USER_BORDA = ("#E2E8F0", "#1E3143")

# Receitas e Despesas
COR_RECEITA = ("#16A34A", "#00D084")
COR_RECEITA_BG = ("#DCFCE7", "#102E24")
COR_DESPESA = ("#DC2626", "#F43F5E")
COR_DESPESA_BG = ("#FEE2E2", "#2E151B")

# Barra de progresso
COR_PROGRESSO = ("#059669", "#00D084")
COR_PROGRESSO_BG = ("#E2E8F0", "#1C2F3F")

# Logout / Fechar
COR_LOGOUT_BG = ("#F1F5F9", "#152330")
COR_LOGOUT_HOVER = ("#E2E8F0", "#1E3143")
COR_LOGOUT_TEXTO = ("#0F172A", "#CBD5E1")
COR_FECHAR_BG = ("#FEE2E2", "#2A141A")
COR_FECHAR_HOVER = ("#FECACA", "#3E1A23")
COR_FECHAR_TEXTO = ("#DC2626", "#F43F5E")

# Botão excluir
COR_EXCLUIR_HOVER = ("#FEE2E2", "#2A141A")
COR_EXCLUIR_TEXTO = ("#DC2626", "#F43F5E")

# Tab / Segmented
COR_TAB_BG = ("#E2E8F0", "#101D27")
COR_TAB_SELECIONADA = ("#059669", "#00D084")
COR_TAB_SELECIONADA_HOVER = ("#047857", "#00B875")
COR_TAB_TEXTO = ("#FFFFFF", "#0B131B")


def obter_cor(cor) -> str:
    """
    Retorna a cor string apropriada para widgets nativos do Tkinter (como tk.Canvas)
    que não aceitam tuplas (light, dark) do CustomTkinter.
    """
    if isinstance(cor, (tuple, list)):
        modo = ctk.get_appearance_mode().lower()
        return cor[0] if modo == "light" else cor[1]
    return cor

# ──────────────────────────────────────────────────────────────
# FONTES
# ──────────────────────────────────────────────────────────────
FONTE_FAMILIA = "Segoe UI"


def fonte(tamanho: int = 13, peso: str = "normal", slant: str = "roman") -> ctk.CTkFont:
    """Retorna uma CTkFont com a fonte padrão do tema."""
    if peso == "italic":
        peso = "normal"
        slant = "italic"
    elif peso not in ("normal", "bold"):
        peso = "normal"
    return ctk.CTkFont(family=FONTE_FAMILIA, size=tamanho, weight=peso, slant=slant)


def fonte_titulo() -> ctk.CTkFont:
    return fonte(22, "bold")


def fonte_subtitulo() -> ctk.CTkFont:
    return fonte(14, "bold")


def fonte_corpo() -> ctk.CTkFont:
    return fonte(13)


def fonte_pequena() -> ctk.CTkFont:
    return fonte(11)


def fonte_hint() -> ctk.CTkFont:
    return fonte(10)


def fonte_grande_valor() -> ctk.CTkFont:
    return fonte(20, "bold")


def obter_cor_texto_principal() -> str:
    return "#0F172A" if ctk.get_appearance_mode().lower() == "light" else "#FFFFFF"

def obter_cor_texto_secundario() -> str:
    return "#334155" if ctk.get_appearance_mode().lower() == "light" else "#94A3B8"

def obter_cor_canvas_linha() -> str:
    return "#E2E8F0" if ctk.get_appearance_mode().lower() == "light" else "#1A2D3C"

def obter_cor_canvas_bg() -> str:
    return "#FFFFFF" if ctk.get_appearance_mode().lower() == "light" else "#101C26"
