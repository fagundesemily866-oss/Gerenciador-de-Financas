"""
Componente de Gráfico Moderno de Projeção e Evolução Financeira.
================================================================

Implementado com tkinter.Canvas de alta performance, 100% integrado ao
tema relaxante do aplicativo (paleta Serene Green) e sem dependências externas.
Suporta:
- Curvas de saldo projetado, receitas, despesas e economia acumulada;
- Comparativo simultâneo dos 3 cenários (Otimista, Normal e Pessimista);
- Grid sutil com valores em R$ no eixo Y e meses no eixo X;
- Marcadores de pontos interativos e tooltips;
- Redimensionamento automático responsivo (<Configure>).
"""
import tkinter as tk
from typing import List, Dict, Any, Optional
import customtkinter as ctk

from views.tema import (
    COR_FUNDO_PRINCIPAL, COR_CARD, COR_CARD_INTERNO, COR_BORDA,
    COR_TEXTO_PRINCIPAL, COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO,
    COR_ACENTO_PRIMARIO, COR_SUCESSO, COR_ALERTA, COR_AVISO, fonte
)


class GraficoEvolucaoCanvas(ctk.CTkFrame):
    """Widget de visualização gráfica vetorial para evolução e cenários financeiros."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA, **kwargs)

        self._dados_projecao: Optional[Dict[str, Any]] = None
        self._modo_visualizacao = "saldo_fluxo"  # 'saldo_fluxo' ou 'cenarios'
        self._hover_info = None

        self._criar_estrutura()

    def _criar_estrutura(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Barra de controles do gráfico (Legenda e Alternância de Modo)
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 6))
        self.top_bar.grid_columnconfigure(0, weight=1)

        # Legenda dinâmica
        self.frame_legenda = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.frame_legenda.grid(row=0, column=0, sticky="w")

        # Botão de alternância de visão
        self.btn_modo = ctk.CTkSegmentedButton(
            self.top_bar,
            values=["📈 Saldo & Fluxo", "🔮 3 Cenários"],
            command=self._on_mudar_modo,
            font=fonte(11, "bold"),
            selected_color=COR_ACENTO_PRIMARIO,
            selected_hover_color=COR_ACENTO_PRIMARIO,
            unselected_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_PRINCIPAL,
        )
        self.btn_modo.set("📈 Saldo & Fluxo")
        self.btn_modo.grid(row=0, column=1, sticky="e")

        # Canvas do gráfico
        self.canvas_frame = ctk.CTkFrame(self, fg_color=COR_CARD_INTERNO, corner_radius=10)
        self.canvas_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg=COR_CARD_INTERNO,
            bd=0,
            highlightthickness=0,
            relief="flat",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.canvas.bind("<Configure>", lambda e: self.redesenhar())
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)

    def _on_mudar_modo(self, escolha: str):
        if "Cenários" in escolha:
            self._modo_visualizacao = "cenarios"
        else:
            self._modo_visualizacao = "saldo_fluxo"
        self._atualizar_legenda()
        self.redesenhar()

    def _atualizar_legenda(self):
        for w in self.frame_legenda.winfo_children():
            w.destroy()

        if self._modo_visualizacao == "saldo_fluxo":
            itens = [
                ("● Saldo Projetado", COR_ACENTO_PRIMARIO),
                ("● Receitas", COR_SUCESSO),
                ("● Despesas", COR_ALERTA),
                ("● Economia", COR_AVISO),
            ]
        else:
            itens = [
                ("● Otimista (+10% / -5%)", COR_SUCESSO),
                ("● Normal (Planejado)", COR_ACENTO_PRIMARIO),
                ("● Pessimista (-10% / +15%)", COR_ALERTA),
            ]

        col = 0
        for texto, cor in itens:
            ctk.CTkLabel(
                self.frame_legenda,
                text=texto,
                font=fonte(11, "bold"),
                text_color=cor,
            ).grid(row=0, column=col, padx=(0, 12))
            col += 1

    def atualizar_dados(self, dados_projecao: Dict[str, Any]):
        """Recebe o dicionário retornado por InteligenciaFinanceiraController.projetar_futuro_financeiro."""
        self._dados_projecao = dados_projecao
        self._atualizar_legenda()
        self.redesenhar()

    def redesenhar(self):
        """Limpa e redesenha o gráfico com base nos dados atuais e tamanho do canvas."""
        self.canvas.delete("all")
        if not self._dados_projecao or "meses" not in self._dados_projecao:
            self._desenhar_placeholder("Nenhum dado de simulação disponível.")
            return

        meses = self._dados_projecao["meses"]
        if not meses:
            self._desenhar_placeholder("Sem meses para projetar.")
            return

        largura = self.canvas.winfo_width()
        altura = self.canvas.winfo_height()

        if largura < 80 or altura < 80:
            return

        # Margens
        margem_esq = 75
        margem_dir = 30
        margem_topo = 30
        margem_base = 40

        area_w = largura - margem_esq - margem_dir
        area_h = altura - margem_topo - margem_base

        if area_w <= 10 or area_h <= 10:
            return

        # Coletar pontos conforme o modo
        n_pontos = len(meses)
        labels_x = [m["rotulo_mes"] for m in meses]

        if self._modo_visualizacao == "saldo_fluxo":
            serie_saldo = [m["saldo_acumulado_simulado"] for m in meses]
            serie_rec = [m["receitas_simulado"] for m in meses]
            serie_desp = [m["despesas_simulado"] for m in meses]
            serie_econ = [m["economia_acumulada"] for m in meses]
            todos_valores = serie_saldo + serie_rec + serie_desp + serie_econ
        else:
            cenarios = self._dados_projecao.get("cenarios", {})
            serie_otimista = cenarios.get("otimista", {}).get("evolucao", [])
            serie_normal = cenarios.get("normal", {}).get("evolucao", [])
            serie_pessimista = cenarios.get("pessimista", {}).get("evolucao", [])
            todos_valores = serie_otimista + serie_normal + serie_pessimista

        if not todos_valores:
            return

        val_min = min(0.0, min(todos_valores))
        val_max = max(100.0, max(todos_valores))
        # Adicionar folga vertical
        intervalo = max(1.0, val_max - val_min)
        val_max += intervalo * 0.12
        val_min -= intervalo * 0.05
        range_val = max(1.0, val_max - val_min)

        def _coord_y(val):
            prop = (val - val_min) / range_val
            return (margem_topo + area_h) - (prop * area_h)

        def _coord_x(idx):
            if n_pontos <= 1:
                return margem_esq + area_w / 2
            return margem_esq + (idx / (n_pontos - 1)) * area_w

        # 1. Grid Horizontal e Rótulos do Eixo Y
        num_linhas_grid = 5
        for i in range(num_linhas_grid + 1):
            val_linha = val_min + (i / num_linhas_grid) * range_val
            y = _coord_y(val_linha)

            # Linha guia sutil
            self.canvas.create_line(
                margem_esq, y, largura - margem_dir, y,
                fill=COR_BORDA,
                dash=(2, 4),
                width=1
            )

            # Texto em R$
            rotulo_y = f"R$ {val_linha:,.0f}" if abs(val_linha) >= 1000 else f"R$ {val_linha:.0f}"
            self.canvas.create_text(
                margem_esq - 8, y,
                text=rotulo_y,
                fill=COR_TEXTO_TERCIARIO,
                anchor="e",
                font=("Segoe UI", 8)
            )

        # Linha Zero de destaque se estiver no gráfico
        if val_min < 0 < val_max:
            y_zero = _coord_y(0.0)
            self.canvas.create_line(
                margem_esq, y_zero, largura - margem_dir, y_zero,
                fill=COR_TEXTO_SECUNDARIO,
                width=1
            )

        # 2. Rótulos do Eixo X (Meses)
        passo_x = max(1, n_pontos // 12) if n_pontos > 12 else 1
        for idx in range(0, n_pontos, passo_x):
            x = _coord_x(idx)
            rot = labels_x[idx]
            self.canvas.create_text(
                x, margem_topo + area_h + 16,
                text=rot,
                fill=COR_TEXTO_SECUNDARIO,
                anchor="center",
                font=("Segoe UI", 9)
            )
            # Marquinha vertical
            self.canvas.create_line(x, margem_topo + area_h, x, margem_topo + area_h + 4, fill=COR_BORDA)

        # 3. Desenho das Séries
        self._pontos_plotados = []

        if self._modo_visualizacao == "saldo_fluxo":
            # Área e Linha de Saldo
            self._desenhar_serie(serie_saldo, COR_ACENTO_PRIMARIO, "Saldo Projetado", _coord_x, _coord_y, espessura=3, preencher=True)
            # Linha de Receitas
            self._desenhar_serie(serie_rec, COR_SUCESSO, "Receitas", _coord_x, _coord_y, espessura=2)
            # Linha de Despesas
            self._desenhar_serie(serie_desp, COR_ALERTA, "Despesas", _coord_x, _coord_y, espessura=2)
            # Linha de Economia Acumulada
            self._desenhar_serie(serie_econ, COR_AVISO, "Economia Acumulada", _coord_x, _coord_y, espessura=2, tracejada=True)
        else:
            # 3 Cenários
            self._desenhar_serie(serie_otimista, COR_SUCESSO, "Cenário Otimista", _coord_x, _coord_y, espessura=2.5)
            self._desenhar_serie(serie_normal, COR_ACENTO_PRIMARIO, "Cenário Normal", _coord_x, _coord_y, espessura=3)
            self._desenhar_serie(serie_pessimista, COR_ALERTA, "Cenário Pessimista", _coord_x, _coord_y, espessura=2.5)

    def _desenhar_serie(self, serie: List[float], cor: str, nome: str, f_x, f_y, espessura=2, preencher=False, tracejada=False):
        if not serie or len(serie) < 2:
            return

        coords = []
        for i, val in enumerate(serie):
            coords.extend([f_x(i), f_y(val)])

        # Preenchimento translúcido sob a linha de saldo
        if preencher and len(coords) >= 4:
            area_coords = list(coords)
            # Fechar na base
            area_coords.extend([f_x(len(serie) - 1), self.canvas.winfo_height() - 40, f_x(0), self.canvas.winfo_height() - 40])
            self.canvas.create_polygon(
                area_coords,
                fill="#0D2C2F",
                outline="",
            )

        # Linha principal
        dash = (4, 3) if tracejada else ()
        self.canvas.create_line(
            coords,
            fill=cor,
            width=espessura,
            smooth=True,
            dash=dash,
            capstyle="round",
            joinstyle="round"
        )

        # Marcadores de pontos
        raio = 3.5
        for i, val in enumerate(serie):
            px = f_x(i)
            py = f_y(val)
            self.canvas.create_oval(
                px - raio, py - raio, px + raio, py + raio,
                fill=cor,
                outline=COR_CARD_INTERNO,
                width=1.5
            )
            # Registrar ponto para hover
            self._pontos_plotados.append({
                "x": px,
                "y": py,
                "val": val,
                "nome": nome,
                "cor": cor,
            })

    def _on_mouse_move(self, event):
        """Detecta proximidade com pontos e exibe tooltip com o valor."""
        if not hasattr(self, "_pontos_plotados") or not self._pontos_plotados:
            return

        mx, my = event.x, event.y
        ponto_proximo = None
        dist_min = 16.0

        for pt in self._pontos_plotados:
            dist = ((pt["x"] - mx) ** 2 + (pt["y"] - my) ** 2) ** 0.5
            if dist < dist_min:
                dist_min = dist
                ponto_proximo = pt

        self.canvas.delete("tooltip")
        if ponto_proximo:
            px = ponto_proximo["x"]
            py = ponto_proximo["y"]
            texto = f"{ponto_proximo['nome']}: R$ {ponto_proximo['val']:,.2f}"

            # Caixa do tooltip
            tw = len(texto) * 6.5 + 16
            th = 22
            tx1 = max(10, min(self.canvas.winfo_width() - tw - 10, px - tw / 2))
            ty1 = max(10, py - 32)
            tx2 = tx1 + tw
            ty2 = ty1 + th

            self.canvas.create_rectangle(
                tx1, ty1, tx2, ty2,
                fill=COR_FUNDO_PRINCIPAL,
                outline=ponto_proximo["cor"],
                width=1.5,
                tags="tooltip"
            )
            self.canvas.create_text(
                (tx1 + tx2) / 2, (ty1 + ty2) / 2,
                text=texto,
                fill=COR_TEXTO_PRINCIPAL,
                font=("Segoe UI", 9, "bold"),
                tags="tooltip"
            )

    def _on_mouse_leave(self, event):
        self.canvas.delete("tooltip")

    def _desenhar_placeholder(self, mensagem: str):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.canvas.create_text(
            w / 2, h / 2,
            text=mensagem,
            fill=COR_TEXTO_TERCIARIO,
            font=("Segoe UI", 12)
        )
