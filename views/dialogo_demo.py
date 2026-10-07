"""
Diálogo de confirmação do modo demonstração.

Avisa, de forma clara, que as "finanças aleatórias" são FICTÍCIAS (somente para
apresentações) e pede a confirmação do usuário antes de gerar os dados.
"""
from typing import Callable, Optional

import customtkinter as ctk

from views.tema import (
    COR_CARD, COR_BORDA, COR_TEXTO_PRINCIPAL, COR_TEXTO_SECUNDARIO,
    COR_ACENTO_PRIMARIO, COR_ACENTO_HOVER, COR_AVISO,
    COR_BOTAO_SECUNDARIO, COR_BOTAO_SECUNDARIO_HOVER, fonte,
)


class DialogoConfirmarDemo(ctk.CTkToplevel):
    """Janela modal: 'Gerar dados fictícios de demonstração?'."""

    def __init__(
        self,
        parent,
        on_confirmar: Callable[[], None],
        on_cancelar: Optional[Callable[[], None]] = None,
    ):
        super().__init__(parent)
        self._on_confirmar = on_confirmar
        self._on_cancelar = on_cancelar
        self._decidido = False

        self.title("Modo demonstração")
        self.resizable(False, False)
        self.configure(fg_color=COR_CARD)
        self.protocol("WM_DELETE_WINDOW", self._cancelar)

        ctk.CTkLabel(self, text="🎲", font=fonte(34)).pack(pady=(20, 4))
        ctk.CTkLabel(
            self, text="Criar finanças aleatórias?",
            font=fonte(16, "bold"), text_color=COR_TEXTO_PRINCIPAL,
        ).pack()
        ctk.CTkLabel(
            self,
            text=(
                "Serão gerados dados FICTÍCIOS (receitas, despesas, categorias,\n"
                "terceiros, metas e saúde financeira) apenas para demonstração.\n\n"
                "Eles não representam finanças reais e a conta ficará\n"
                "identificada como \"modo demonstração\"."
            ),
            font=fonte(12), text_color=COR_TEXTO_SECUNDARIO, justify="center",
        ).pack(padx=28, pady=(8, 4))
        ctk.CTkLabel(
            self, text="Se preferir começar do zero, cancele.",
            font=fonte(11), text_color=COR_AVISO,
        ).pack(pady=(0, 12))

        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.pack(fill="x", padx=28, pady=(0, 20))
        botoes.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            botoes, text="Cancelar", height=38,
            fg_color=COR_BOTAO_SECUNDARIO, hover_color=COR_BOTAO_SECUNDARIO_HOVER,
            text_color=COR_TEXTO_PRINCIPAL, font=fonte(12), command=self._cancelar,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(
            botoes, text="🎲  Gerar dados fictícios", height=38,
            fg_color=COR_ACENTO_PRIMARIO, hover_color=COR_ACENTO_HOVER,
            text_color="#0B1D1F", font=fonte(12, "bold"), command=self._confirmar,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self._centralizar(parent)
        # transient/grab precisam esperar a janela estar visível (evita erro no Windows/Linux)
        self.after(60, self._tornar_modal)

    def _centralizar(self, parent):
        self.update_idletasks()
        try:
            raiz = parent.winfo_toplevel()
            x = raiz.winfo_rootx() + (raiz.winfo_width() - self.winfo_reqwidth()) // 2
            y = raiz.winfo_rooty() + (raiz.winfo_height() - self.winfo_reqheight()) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

    def _tornar_modal(self):
        try:
            self.transient(self.master.winfo_toplevel())
            self.grab_set()
            self.focus_force()
        except Exception:
            pass

    def _confirmar(self):
        self._decidido = True
        self._fechar()
        self._on_confirmar()

    def _cancelar(self):
        if self._decidido:
            return
        self._decidido = True
        self._fechar()
        if self._on_cancelar:
            self._on_cancelar()

    def _fechar(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()
