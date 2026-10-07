"""
View de Celebração de Meta Atingida
=====================================
Exibe animação de confetes/foguetes subindo de baixo e explodindo no meio,
depois mostra pop-up perguntando se deseja: Aumentar meta, Excluir ou Manter.
"""
import tkinter as tk
import random
import math
from typing import Callable, Optional
import customtkinter as ctk

from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_SUCESSO, COR_ALERTA,
    fonte,
)


class ConfeteParticula:
    """Representa uma partícula de confete ou foguete."""

    def __init__(self, canvas: tk.Canvas, x: float, y: float, tipo: str = "confete"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.tipo = tipo  # "foguete", "confete", "estrela"
        self.ativo = True

        if tipo == "foguete":
            self.vx = random.uniform(-2, 2)
            self.vy = -random.uniform(8, 14)  # Sobe rápido
            self.fase = "subindo"  # "subindo" -> "explodindo"
            self.vida = 0
            self.cor = random.choice(["#00D084", "#38BDF8", "#F59E0B", "#F43F5E", "#A855F7"])
            self.tamanho = random.uniform(6, 10)
            self.explosao_x = x
            self.explosao_y = random.uniform(80, 200)  # Altura da explosão
            self.particulas_explodidas = []
            self.shape = canvas.create_oval(
                x - self.tamanho, y - self.tamanho,
                x + self.tamanho, y + self.tamanho,
                fill=self.cor, outline=""
            )
        else:
            # Confetes e estrelas normais
            self.vx = random.uniform(-5, 5)
            self.vy = random.uniform(-12, -4)
            self.gravidade = random.uniform(0.2, 0.5)
            self.rotacao = random.uniform(0, 360)
            self.rot_speed = random.uniform(-8, 8)
            self.vida = random.randint(80, 160)
            self.vida_max = self.vida
            self.cor = random.choice([
                "#00D084", "#38BDF8", "#F59E0B", "#F43F5E",
                "#A855F7", "#FB923C", "#FACC15", "#34D399",
            ])

            if tipo == "estrela":
                self.tamanho = random.uniform(4, 8)
                self.shape = canvas.create_text(
                    x, y, text="★", fill=self.cor,
                    font=("Segoe UI", int(self.tamanho * 2))
                )
            else:
                w = random.uniform(6, 12)
                h = random.uniform(3, 7)
                self.tamanho = w
                self.shape = canvas.create_rectangle(
                    x, y, x + w, y + h,
                    fill=self.cor, outline=""
                )

    def atualizar(self):
        if not self.ativo:
            return

        if self.tipo == "foguete":
            self.vida += 1
            if self.fase == "subindo":
                self.y += self.vy
                self.x += self.vx
                self.canvas.coords(
                    self.shape,
                    self.x - self.tamanho, self.y - self.tamanho,
                    self.x + self.tamanho, self.y + self.tamanho
                )
                # Quando atingir a altura de explosão
                if self.y <= self.explosao_y:
                    self.fase = "explodindo"
                    self.canvas.delete(self.shape)
                    self.shape = None
                    # Criar partículas de explosão
                    for _ in range(20):
                        angulo = random.uniform(0, 2 * math.pi)
                        vel = random.uniform(3, 9)
                        p = _PartiulaExplosao(
                            self.canvas,
                            self.x, self.y,
                            math.cos(angulo) * vel,
                            math.sin(angulo) * vel,
                            self.cor,
                        )
                        self.particulas_explodidas.append(p)
            elif self.fase == "explodindo":
                todas_mortas = True
                for p in self.particulas_explodidas:
                    p.atualizar()
                    if p.ativo:
                        todas_mortas = False
                if todas_mortas:
                    self.ativo = False
        else:
            # Confete/estrela normal
            self.vy += self.gravidade
            self.x += self.vx
            self.y += self.vy
            self.vida -= 1

            alpha_pct = self.vida / self.vida_max

            try:
                if self.tipo == "estrela":
                    self.canvas.coords(self.shape, self.x, self.y)
                else:
                    w = self.tamanho
                    h = w * 0.5
                    self.canvas.coords(
                        self.shape,
                        self.x, self.y,
                        self.x + w, self.y + h
                    )
            except Exception:
                pass

            if self.vida <= 0:
                self.ativo = False
                try:
                    self.canvas.delete(self.shape)
                except Exception:
                    pass

    def destruir(self):
        try:
            if self.shape:
                self.canvas.delete(self.shape)
            for p in getattr(self, "particulas_explodidas", []):
                p.destruir()
        except Exception:
            pass
        self.ativo = False


class _PartiulaExplosao:
    """Mini-partícula criada na explosão de foguetes."""

    def __init__(self, canvas, x, y, vx, vy, cor):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.cor = cor
        self.ativo = True
        self.vida = random.randint(20, 50)
        self.vida_max = self.vida
        self.gravidade = 0.3
        r = random.uniform(2, 5)
        self.shape = canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=cor, outline=""
        )

    def atualizar(self):
        if not self.ativo:
            return
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravidade
        self.vida -= 1
        try:
            r = 3 * (self.vida / self.vida_max)
            self.canvas.coords(
                self.shape,
                self.x - r, self.y - r,
                self.x + r, self.y + r
            )
        except Exception:
            pass
        if self.vida <= 0:
            self.ativo = False
            try:
                self.canvas.delete(self.shape)
            except Exception:
                pass

    def destruir(self):
        try:
            self.canvas.delete(self.shape)
        except Exception:
            pass
        self.ativo = False


class CelebracaoMetaView(ctk.CTkToplevel):
    """
    Janela popup de celebração de meta atingida.
    Exibe foguetes e confetes e depois um pop-up de opções.
    """

    def __init__(
        self,
        parent,
        titulo_meta: str,
        valor_meta: float,
        on_aumentar: Optional[Callable] = None,
        on_recuar: Optional[Callable] = None,
        on_excluir: Optional[Callable] = None,
        on_manter: Optional[Callable] = None,
        meta_id: Optional[int] = None,
    ):
        super().__init__(parent)
        self.titulo_meta = titulo_meta
        self.valor_meta = valor_meta
        self.on_aumentar = on_aumentar
        self.on_recuar = on_recuar
        self.on_excluir = on_excluir
        self.on_manter = on_manter
        self.meta_id = meta_id

        self.particulas = []
        self._animando = True
        self._popup_mostrado = False

        self.title("🎉 Meta Atingida!")
        self.resizable(False, False)
        self.configure(fg_color="#0B131B")

        # Centraliza na tela
        largura, altura = 600, 480
        self.geometry(f"{largura}x{altura}")
        self.after(10, self._centralizar)

        # Garante que fique na frente
        self.attributes("-topmost", True)
        self.grab_set()

        self._build_ui()
        self._iniciar_animacao()

    def _centralizar(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h = 600, 480
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Canvas de animação (fundo inteiro)
        self.canvas = tk.Canvas(
            self, width=600, height=480,
            bg="#0B131B", highlightthickness=0
        )
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Texto de celebração (por cima do canvas)
        self.canvas.create_text(
            300, 50,
            text="🎯 META ATINGIDA! 🎉",
            fill="#00D084",
            font=("Segoe UI", 22, "bold"),
            tags="texto_principal"
        )
        self.canvas.create_text(
            300, 90,
            text=f'"{self.titulo_meta}"',
            fill="#FFFFFF",
            font=("Segoe UI", 14),
            tags="texto_titulo"
        )
        self.canvas.create_text(
            300, 120,
            text=f"R$ {self.valor_meta:,.2f} poupados! 💰",
            fill="#F59E0B",
            font=("Segoe UI", 12, "bold"),
            tags="texto_valor"
        )

    def _iniciar_animacao(self):
        """Lança foguetes e confetes por 3 segundos, depois mostra o popup."""
        largura = 600
        altura = 480

        # Lança foguetes de baixo para cima
        for _ in range(6):
            x = random.uniform(50, largura - 50)
            p = ConfeteParticula(self.canvas, x, altura, "foguete")
            self.particulas.append(p)

        # Confetes e estrelas espalhados
        for _ in range(40):
            x = random.uniform(0, largura)
            p_tipo = random.choice(["confete", "confete", "estrela"])
            p = ConfeteParticula(self.canvas, x, altura - 20, p_tipo)
            self.particulas.append(p)

        self._loop_animacao()
        # Depois de 3 segundos, mostra o popup
        self.after(3000, self._mostrar_popup)

    def _loop_animacao(self):
        if not self._animando:
            return

        try:
            # Adiciona mais confetes periodicamente nos primeiros 2.5 s
            if random.random() < 0.3:
                x = random.uniform(0, 600)
                tipo = random.choice(["confete", "estrela"])
                p = ConfeteParticula(self.canvas, x, 490, tipo)
                self.particulas.append(p)

            for p in self.particulas[:]:
                p.atualizar()
                if not p.ativo:
                    self.particulas.remove(p)

            self.after(16, self._loop_animacao)  # ~60fps
        except Exception:
            pass

    def _mostrar_popup(self):
        if self._popup_mostrado:
            return
        self._popup_mostrado = True

        # Card do popup sobre o canvas
        popup = ctk.CTkFrame(
            self,
            fg_color="#101C26",
            corner_radius=20,
            border_width=2,
            border_color="#00D084",
            width=420,
            height=260,
        )
        popup.place(relx=0.5, rely=0.5, anchor="center")
        popup.grid_propagate(False)

        # Emoji grande
        ctk.CTkLabel(
            popup, text="🏆", font=fonte(48)
        ).pack(pady=(16, 4))

        ctk.CTkLabel(
            popup,
            text="Parabéns! Você atingiu sua meta!",
            font=fonte(14, "bold"),
            text_color="#00D084",
        ).pack()

        ctk.CTkLabel(
            popup,
            text="O que você gostaria de fazer?",
            font=fonte(11),
            text_color="#94A3B8",
        ).pack(pady=(4, 14))

        # Botões
        btn_row = ctk.CTkFrame(popup, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 10))
        btn_row.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            btn_row,
            text="📈 Aumentar\nMeta",
            height=48,
            corner_radius=10,
            fg_color="#122538",
            hover_color="#1E3A5F",
            text_color="#38BDF8",
            font=fonte(10, "bold"),
            command=self._acao_aumentar,
        ).grid(row=0, column=0, padx=4, sticky="ew")

        ctk.CTkButton(
            btn_row,
            text="📉 Recuar\na Meta",
            height=48,
            corner_radius=10,
            fg_color="#2A141A",
            hover_color="#452B18",
            text_color="#F43F5E",
            font=fonte(10, "bold"),
            command=self._acao_recuar,
        ).grid(row=0, column=1, padx=4, sticky="ew")

        ctk.CTkButton(
            btn_row,
            text="✅ Apenas\nManter",
            height=48,
            corner_radius=10,
            fg_color="#0D2E2B",
            hover_color="#134E48",
            text_color="#00D084",
            font=fonte(10, "bold"),
            command=self._acao_manter,
        ).grid(row=0, column=2, padx=4, sticky="ew")

    def _acao_aumentar(self):
        self._fechar()
        if self.on_aumentar:
            self.on_aumentar(self.meta_id)

    def _acao_recuar(self):
        self._fechar()
        if self.on_recuar:
            self.on_recuar(self.meta_id)

    def _acao_excluir(self):
        self._fechar()
        if self.on_excluir:
            self.on_excluir(self.meta_id)

    def _acao_manter(self):
        self._fechar()
        if self.on_manter:
            self.on_manter(self.meta_id)

    def _fechar(self):
        self._animando = False
        for p in self.particulas:
            p.destruir()
        self.particulas.clear()
        try:
            self.destroy()
        except Exception:
            pass
