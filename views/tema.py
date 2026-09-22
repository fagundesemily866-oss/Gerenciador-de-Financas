"""
Módulo de Tema Visual — Paleta Relaxante Verde-Esmeralda
========================================================

Paleta inspirada na identidade visual do app (carteira verde com gráfico).
Tons suaves de verde e teal que transmitem calma e confiança ao usuário.
"""

# ──────────────────────────────────────────────────────────────
# PALETA DE CORES — "Serene Green"
# ──────────────────────────────────────────────────────────────

# Fundos e superfícies
COR_FUNDO_PRINCIPAL = "#0B1D1F"       # Verde-escuro profundo (base)
COR_SIDEBAR = "#0F2629"              # Sidebar levemente mais clara
COR_CARD = "#112E32"                 # Cards e painéis
COR_CARD_INTERNO = "#0A2024"         # Campos de input, subcards
COR_BORDA = "#1A4A4A"               # Bordas sutis

# Texto
COR_TEXTO_PRINCIPAL = "#E0F2F1"      # Branco esverdeado suave
COR_TEXTO_SECUNDARIO = "#80CBC4"     # Teal claro
COR_TEXTO_TERCIARIO = "#4A8A85"      # Teal apagado (hints)
COR_TEXTO_MUTED = "#3D6B67"          # Texto muito sutil

# Acentos
COR_ACENTO_PRIMARIO = "#4DB6AC"      # Teal médio — botões, links
COR_ACENTO_HOVER = "#3D9E94"         # Hover do acento primário
COR_SUCESSO = "#66BB6A"             # Verde suave (receitas, sucesso)
COR_SUCESSO_HOVER = "#57A75C"       # Hover do verde
COR_ALERTA = "#FFAB91"              # Salmão suave (alertas, despesas)
COR_ALERTA_HOVER = "#E8967D"        # Hover do salmão
COR_AVISO = "#FFE082"               # Âmbar suave (avisos, "faltam")
COR_INFO = "#81D4FA"                # Azul-claro (informativo)

# Elementos interativos (sidebar)
COR_BOTAO_NORMAL = "transparent"
COR_BOTAO_ATIVO = "#1A3F3F"          # Botão selecionado no menu
COR_BOTAO_HOVER = "#163636"          # Hover genérico
COR_BOTAO_SECUNDARIO = "#1A3F3F"     # Botões secundários
COR_BOTAO_SECUNDARIO_HOVER = "#245050"

# Avatar / Card do Usuário
COR_AVATAR_BG = "#1A3F3F"
COR_AVATAR_TEXTO = "#4DB6AC"
COR_CARD_USER_BG = "#0D2225"
COR_CARD_USER_BORDA = "#1A4A4A"

# Receitas e Despesas
COR_RECEITA = "#66BB6A"
COR_RECEITA_BG = "#1A3D2A"
COR_DESPESA = "#FFAB91"
COR_DESPESA_BG = "#3D2520"

# Barra de progresso
COR_PROGRESSO = "#26A69A"
COR_PROGRESSO_BG = "#1A3F3F"

# Logout / Fechar
COR_LOGOUT_BG = "#1A3F3F"
COR_LOGOUT_HOVER = "#245050"
COR_LOGOUT_TEXTO = "#E0F2F1"
COR_FECHAR_BG = "#3D2520"
COR_FECHAR_HOVER = "#4D3028"
COR_FECHAR_TEXTO = "#FFAB91"

# Botão excluir
COR_EXCLUIR_HOVER = "#3D2520"
COR_EXCLUIR_TEXTO = "#FFAB91"

# Tab / Segmented
COR_TAB_BG = "#0A2024"
COR_TAB_SELECIONADA = "#4DB6AC"
COR_TAB_SELECIONADA_HOVER = "#3D9E94"
COR_TAB_TEXTO = "#0B1D1F"

# ──────────────────────────────────────────────────────────────
# FONTES
# ──────────────────────────────────────────────────────────────
# Fontes elegantes do sistema. No Windows, "Segoe UI" é limpa e moderna.
# No macOS, "SF Pro Display" ou "Helvetica Neue".
# Fallback para "Arial" em qualquer SO.

FONTE_FAMILIA = "Segoe UI"

import customtkinter as ctk


def fonte(tamanho: int = 13, peso: str = "normal") -> ctk.CTkFont:
    """Retorna uma CTkFont com a fonte padrão do tema."""
    return ctk.CTkFont(family=FONTE_FAMILIA, size=tamanho, weight=peso)


def fonte_titulo() -> ctk.CTkFont:
    return fonte(24, "bold")


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
