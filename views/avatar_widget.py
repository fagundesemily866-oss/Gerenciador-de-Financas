"""Avatar circular em Canvas: sem labels quadrados sobre a foto.

O Canvas tem exatamente a cor da superfície em volta e a imagem tem
transparência real nos cantos. Serve para o Perfil e para a barra lateral.
"""
import tkinter as tk

from PIL import Image, ImageTk

from services.foto_perfil import avatar_circular
from views.tema import obter_cor


class AvatarCircularCanvas(tk.Canvas):
    """Avatar circular com borda e iniciais enquanto nenhuma foto é escolhida."""

    def __init__(
        self,
        master,
        *,
        tamanho: int,
        iniciais: str,
        fundo_externo,
        fundo_interno,
        cor_borda,
        cor_texto,
        **kwargs,
    ):
        self.tamanho = int(tamanho)
        if self.tamanho < 24:
            raise ValueError("O avatar deve ter pelo menos 24 pixels")
        self._fundo_externo = fundo_externo
        self._fundo_interno = fundo_interno
        self._cor_borda = cor_borda
        self._cor_texto = cor_texto
        self._iniciais = iniciais or "U"
        self._imagem_original = None
        self._imagem_tk = None  # Mantém referência de PhotoImage para o Tk.
        super().__init__(
            master,
            width=self.tamanho,
            height=self.tamanho,
            bg=obter_cor(fundo_externo),
            bd=0,
            relief="flat",
            highlightthickness=0,
            **kwargs,
        )
        self._redesenhar()

    def _redesenhar(self):
        self.configure(bg=obter_cor(self._fundo_externo))
        self.delete("all")
        n = self.tamanho
        # Borda desenhada no próprio círculo: sem frame/label retangular por cima.
        self.create_oval(
            1, 1, n - 2, n - 2,
            fill=obter_cor(self._fundo_interno),
            outline=obter_cor(self._cor_borda),
            width=2,
        )
        if self._imagem_original is None:
            self._imagem_tk = None
            self.create_text(
                n // 2, n // 2,
                text=self._iniciais,
                fill=obter_cor(self._cor_texto),
                font=("Segoe UI", max(11, n // 3), "bold"),
            )
            return

        # Mantém pequena margem entre a foto e a borda verde. As quinas são
        # transparentes, revelando o círculo de baixo; não há fundo quadrado.
        lado = n - 8
        imagem = avatar_circular(self._imagem_original, lado)
        imagem = imagem.resize((lado, lado), Image.Resampling.LANCZOS)
        self._imagem_tk = ImageTk.PhotoImage(imagem, master=self)
        self.create_image(n // 2, n // 2, image=self._imagem_tk, anchor="center")

    def mostrar_foto(self, imagem: Image.Image):
        self._imagem_original = imagem.copy()
        self._redesenhar()

    def atualizar_cores(self):
        """Reaplica a paleta ao alternar entre temas claro e escuro."""
        self._redesenhar()
