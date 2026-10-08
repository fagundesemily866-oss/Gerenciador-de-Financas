"""
View de Metas Financeiras — Com dados reais, celebração de meta atingida e modo claro correto.
"""
import re
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, date
from typing import Optional, List
import customtkinter as ctk

from dao.meta_dao import MetaDAO
from models.meta import Meta
from views.notificacao_toast import GerenciadorNotificacoes
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_SUCESSO, COR_ALERTA, COR_AVISO, COR_INFO,
    fonte, fonte_titulo, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
    obter_cor
)



class MetaView(ctk.CTkFrame):
    """Tela de Metas Financeiras com dados reais, celebração e modo claro."""

    def __init__(self, parent, dao: Optional[MetaDAO] = None):
        super().__init__(parent, fg_color="transparent")
        self.dao = dao or MetaDAO()
        self.filtro_aba = "Todas"
        self._aguardando_celebracao = []  # IDs de metas para celebrar

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._montar_tela()

    def atualizar_dados(self):
        self._verificar_metas_atingidas()
        self._montar_tela()

    def _verificar_metas_atingidas(self):
        """Verifica metas que atingiram 100% e dispara celebração."""
        try:
            metas = self.dao.listar_todas()
            for m in metas:
                if (
                    m.get("concluida") == 1
                    and m.get("celebracao_exibida") == 0
                ):
                    self._aguardando_celebracao.append(m["id"])
        except Exception:
            pass

    def _montar_tela(self):
        for w in self.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # 1. CABEÇALHO
        self._build_header(scroll)

        # 2. MÉTRICAS (4 CARDS)
        self._build_metricas(scroll)

        # 3. CORPO (MINHAS METAS NA ESQ + NOVA META & PROJEÇÃO NA DIR)
        corpo = ctk.CTkFrame(scroll, fg_color="transparent")
        corpo.pack(fill="both", expand=True, pady=(0, 10))
        corpo.grid_columnconfigure(0, weight=6)
        corpo.grid_columnconfigure(1, weight=4)

        self._build_coluna_metas(corpo)
        self._build_coluna_formulario(corpo)

        # Celebrar metas atingidas (após renderizar)
        if self._aguardando_celebracao:
            self.after(500, self._disparar_proxima_celebracao)

    def _disparar_proxima_celebracao(self):
        if not self._aguardando_celebracao:
            return
        meta_id = self._aguardando_celebracao.pop(0)
        meta = self.dao.buscar_por_id(meta_id)
        if meta:
            self._exibir_celebracao(
                meta_id=meta_id,
                titulo=meta.get("descricao", "Meta"),
                valor=float(meta.get("valor_alvo", 0)),
            )

    def _exibir_celebracao(self, meta_id: int, titulo: str, valor: float):
        from views.celebracao_view import CelebracaoMetaView
        CelebracaoMetaView(
            self.winfo_toplevel(),
            titulo_meta=titulo,
            valor_meta=valor,
            meta_id=meta_id,
            on_aumentar=self._on_aumentar_meta,
            on_recuar=self._on_recuar_meta,
            on_manter=self._on_manter_meta,
            on_excluir=self._on_excluir_meta,
        )

    def _on_aumentar_meta(self, meta_id: int):
        """Abre diálogo para o usuário definir novo valor alvo."""
        # Marca celebração como exibida
        try:
            self.dao.marcar_celebracao_exibida(meta_id)
        except Exception:
            pass
        self._mostrar_dialog_aumentar(meta_id)

    def _mostrar_dialog_aumentar(self, meta_id: int):
        """Janela simples para inserir novo valor alvo."""
        dialog = ctk.CTkToplevel(self.winfo_toplevel())
        dialog.title("Aumentar Meta")
        dialog.geometry("380x200")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        dialog.configure(fg_color="#101C26")

        ctk.CTkLabel(dialog, text="Novo valor alvo da meta (R$)",
            font=fonte(12, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(pady=(20, 8))

        entry = ctk.CTkEntry(dialog, placeholder_text="Ex: 5000.00", height=38,
            fg_color=COR_CARD_INTERNO, border_color=COR_BORDA, font=fonte(12))
        entry.pack(fill="x", padx=30)

        def confirmar():
            try:
                novo = float(entry.get().replace(",", ".").strip())
                if novo > 0:
                    self.dao.aumentar_meta(meta_id, novo)
            except Exception:
                pass
            dialog.destroy()
            self._montar_tela()

        ctk.CTkButton(dialog, text="Confirmar", height=38,
            fg_color="#00D084", hover_color="#00B875", text_color="#0B131B",
            font=fonte(11, "bold"), command=confirmar).pack(pady=14, padx=30, fill="x")


    def _on_recuar_meta(self, meta_id: int):
        """Abre diálogo para o usuário recuar ou reduzir o valor da meta."""
        try:
            self.dao.marcar_celebracao_exibida(meta_id)
        except Exception:
            pass
        self._mostrar_dialog_recuar(meta_id)

    def _mostrar_dialog_recuar(self, meta_id: int):
        """Janela para definir valor recuado da meta."""
        dialog = ctk.CTkToplevel(self.winfo_toplevel())
        dialog.title("Recuar Meta")
        dialog.geometry("380x200")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        dialog.configure(fg_color="#101C26")

        ctk.CTkLabel(dialog, text="Novo valor recuado da meta (R$)",
            font=fonte(12, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(pady=(20, 8))

        entry = ctk.CTkEntry(dialog, placeholder_text="Ex: 2500.00", height=38,
            fg_color=COR_CARD_INTERNO, border_color=COR_BORDA, font=fonte(12))
        entry.pack(fill="x", padx=30)

        def confirmar():
            try:
                novo = float(entry.get().replace(",", ".").strip())
                if novo > 0:
                    self.dao.aumentar_meta(meta_id, novo)
            except Exception:
                pass
            dialog.destroy()
            self._montar_tela()

        ctk.CTkButton(dialog, text="Confirmar Recuo", height=38,
            fg_color="#F59E0B", hover_color="#D97706", text_color="#0B131B",
            font=fonte(11, "bold"), command=confirmar).pack(pady=14, padx=30, fill="x")

    def _on_excluir_meta(self, meta_id: int):
        # A tela de celebração chama o mesmo fluxo de exclusão com confirmação.
        self._confirmar_excluir(meta_id)

    def _on_manter_meta(self, meta_id: int):
        try:
            self.dao.marcar_celebracao_exibida(meta_id)
        except Exception:
            pass
        self._montar_tela()


    # ==============================================================
    # 1. CABEÇALHO
    # ==============================================================
    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)

        tit_box = ctk.CTkFrame(header, fg_color="transparent")
        tit_box.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(tit_box, text="Metas", font=fonte(24, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w")
        ctk.CTkLabel(
            tit_box,
            text="Conquiste seus planos com organização e disciplina.",
            font=fonte(12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Citação no canto superior direito
        citacao_box = ctk.CTkFrame(header, fg_color="transparent")
        citacao_box.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            citacao_box,
            text='“ Grandes conquistas começam com pequenos\npassos, todos os dias. ”',
            font=fonte(11, "italic"),
            text_color="#94A3B8",
            justify="right",
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(citacao_box, text="🏔️", font=fonte(24)).pack(side="left")

    # ==============================================================
    # 2. MÉTRICAS (4 CARDS) — dados reais
    # ==============================================================
    def _build_metricas(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 14))
        for c in range(4):
            grid.grid_columnconfigure(c, weight=1)

        # Dados reais do banco
        reais = self.dao.listar_todas()
        tot_poupado = sum(float(m.get("valor_atual", 0)) for m in reais)
        ativas = [m for m in reais if not m.get("concluida")]
        em_dia = [m for m in ativas if float(m.get("valor_atual", 0)) >= (
            float(m.get("valor_alvo", 1)) * 0.5)]
        atrasadas = [m for m in ativas if m not in em_dia]

        pct_em_dia = (len(em_dia) / len(ativas) * 100) if ativas else 0
        pct_atrasadas = (len(atrasadas) / len(ativas) * 100) if ativas else 0

        cards = [
            ("🐷", "#0D2E2B", "Total poupado", f"R$ {tot_poupado:,.2f}", "Acumulado em metas", "#00D084"),
            ("🎯", "#122538", "Metas ativas", str(len(ativas)), f"{len(reais)} cadastradas", "#38BDF8"),
            ("✔", "#0D2E2B", "Em dia", str(len(em_dia)), f"{pct_em_dia:.0f}% no prazo", "#00D084"),
            ("🕒", "#2E151B", "Atrasadas", str(len(atrasadas)), f"{pct_atrasadas:.0f}% precisam de atenção", "#F43F5E"),
        ]

        for idx, (ic, bg_ic, tit, val, sub, cor_val) in enumerate(cards):
            card = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
            card.grid(row=0, column=idx, padx=4, sticky="nsew")

            topo_c = ctk.CTkFrame(card, fg_color="transparent")
            topo_c.pack(fill="x", padx=14, pady=(12, 4))

            ic_box = ctk.CTkFrame(topo_c, width=34, height=34, corner_radius=10, fg_color=bg_ic)
            ic_box.pack(side="left", padx=(0, 10))
            ic_box.pack_propagate(False)
            ctk.CTkLabel(ic_box, text=ic, font=fonte(13, "bold"), text_color=cor_val).place(relx=0.5, rely=0.5, anchor="center")

            t_box = ctk.CTkFrame(topo_c, fg_color="transparent")
            t_box.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(t_box, text=tit, font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")
            ctk.CTkLabel(t_box, text=val, font=fonte(18, "bold"), text_color=cor_val, anchor="w").pack(anchor="w")

            ctk.CTkLabel(card, text=sub, font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w", padx=14, pady=(0, 10))


    # ==============================================================
    # 3. COLUNA ESQUERDA: LISTA DE METAS (dados reais)
    # ==============================================================
    def _build_coluna_metas(self, parent):
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Topo
        ctk.CTkLabel(col, text="Minhas Metas", font=fonte(14, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", pady=(0, 8))

        # Filtros
        bar_f = ctk.CTkFrame(col, fg_color="transparent")
        bar_f.pack(fill="x", pady=(0, 10))

        abas = ctk.CTkFrame(bar_f, fg_color=COR_CARD_INTERNO, corner_radius=8, height=32)
        abas.pack(side="left")

        # Dados reais
        metas_reais = self.dao.listar_todas()
        total = len(metas_reais)
        andamento = len([m for m in metas_reais if not m.get("concluida")])
        concluidas = len([m for m in metas_reais if m.get("concluida")])

        for aba_txt, aba_key in [
            (f"Todas ({total})", "Todas"),
            (f"Em andamento ({andamento})", "Em andamento"),
            (f"Concluídas ({concluidas})", "Concluídas"),
        ]:
            ativo = (aba_key == self.filtro_aba or (self.filtro_aba == "Todas" and aba_key == "Todas"))
            ctk.CTkButton(
                abas,
                text=aba_txt,
                height=26,
                corner_radius=6,
                fg_color="#00D084" if ativo else "transparent",
                text_color="#0B131B" if ativo else COR_TEXTO_SECUNDARIO,
                font=fonte(10, "bold" if ativo else "normal"),
                command=lambda a=aba_key: self._set_filtro(a),
            ).pack(side="left", padx=2, pady=3)

        # Filtrar metas
        if self.filtro_aba == "Em andamento":
            metas_filtradas = [m for m in metas_reais if not m.get("concluida")]
        elif self.filtro_aba == "Concluídas":
            metas_filtradas = [m for m in metas_reais if m.get("concluida")]
        else:
            metas_filtradas = metas_reais

        # Grid de Cards de Metas
        grid_metas = ctk.CTkFrame(col, fg_color="transparent")
        grid_metas.pack(fill="x")
        grid_metas.grid_columnconfigure((0, 1), weight=1)

        if not metas_filtradas:
            # Mensagem vazia
            vazio = ctk.CTkFrame(grid_metas, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
            vazio.grid(row=0, column=0, columnspan=2, pady=20, padx=4, sticky="ew")
            ctk.CTkLabel(vazio, text="🎯", font=fonte(32)).pack(pady=(20, 4))
            ctk.CTkLabel(vazio, text="Nenhuma meta cadastrada",
                font=fonte(14, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack()
            ctk.CTkLabel(vazio, text="Crie sua primeira meta no painel ao lado!",
                font=fonte(11), text_color=COR_TEXTO_MUTED).pack(pady=(4, 20))
        else:
            emojis = ["🏖️", "🚗", "🏠", "💻", "🐷", "🊲", "🌍", "⭐", "📚", "🌿"]
            for idx, m in enumerate(metas_filtradas):
                r, c = idx // 2, idx % 2
                pct = int(min(100, (float(m.get("valor_atual", 0)) / max(float(m.get("valor_alvo", 1)), 1)) * 100))
                concluida = m.get("concluida", 0)
                cor_prog = "#00D084" if not concluida else "#38BDF8"
                falta = max(0, float(m.get("valor_alvo", 0)) - float(m.get("valor_atual", 0)))
                msg = f"✅ Meta concluída!" if concluida else (f"🚀 Faltam apenas R$ {falta:,.2f}! Quase lá!" if pct >= 80 else f"🌱 Faltam R$ {falta:,.2f} para sua meta.")
                dados = {
                    "emoji": emojis[idx % len(emojis)],
                    "titulo": m.get("descricao", "Meta"),
                    "categoria": m.get("prazo") or "Meta pessoal",
                    "pct": pct,
                    "alvo": f"R$ {float(m.get('valor_alvo', 0)):,.2f}",
                    "guardado": f"R$ {float(m.get('valor_atual', 0)):,.2f}",
                    "prazo": m.get("prazo") or "A definir",
                    "mensal": "A definir",
                    "conclusao": m.get("data_limite") or "A definir",
                    "msg": msg,
                    "atrasada": False,
                    "cor_prog": cor_prog,
                    "meta_id": m["id"],
                }
                self._criar_card_meta(grid_metas, dados, r, c)


    def _criar_card_meta(self, parent, m: dict, row: int, col: int):
        meta_id = m.get("meta_id")
        cor_prog = m.get("cor_prog", "#00D084")
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

        # Topo do card: Imagem/emoji + Título + Opções
        top_f = ctk.CTkFrame(card, fg_color="transparent")
        top_f.pack(fill="x", padx=12, pady=(12, 6))

        img_box = ctk.CTkFrame(top_f, width=54, height=54, corner_radius=8, fg_color="#182A3A")
        img_box.pack(side="left", padx=(0, 10))
        img_box.pack_propagate(False)
        ctk.CTkLabel(img_box, text=m["emoji"], font=fonte(24)).place(relx=0.5, rely=0.5, anchor="center")

        tit_f = ctk.CTkFrame(top_f, fg_color="transparent")
        tit_f.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(tit_f, text=m["titulo"][:20], font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(tit_f, text=m["categoria"][:22], font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        # Botão de excluir meta (se tiver ID real)
        if meta_id:
            ctk.CTkButton(
                top_f, text="×", width=22, height=22, corner_radius=11,
                fg_color="transparent", hover_color="#2A141A",
                text_color=COR_TEXTO_MUTED, font=fonte(12, "bold"),
                command=lambda mid=meta_id: self._confirmar_excluir(mid),
            ).pack(side="right")
        else:
            ctk.CTkLabel(top_f, text="···", font=fonte(14, "bold"), text_color=COR_TEXTO_MUTED).pack(side="right")

        # Donut Canvas
        mid_f = ctk.CTkFrame(card, fg_color="transparent")
        mid_f.pack(fill="x", padx=12, pady=4)

        c_prog = tk.Canvas(mid_f, width=50, height=50, bg=obter_cor(COR_CARD), highlightthickness=0)
        c_prog.pack(side="left", padx=(0, 10))

        c_prog.create_arc(5, 5, 45, 45, start=0, extent=359, outline="#162E35", width=5, style="arc")
        ext = int(m["pct"] * 3.6)
        c_prog.create_arc(5, 5, 45, 45, start=90, extent=-ext, outline=cor_prog, width=5, style="arc")
        c_prog.create_text(25, 25, text=f"{m['pct']}%", fill="#FFFFFF", font=("Segoe UI", 8, "bold"))

        val_f = ctk.CTkFrame(mid_f, fg_color="transparent")
        val_f.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(val_f, text=f"{m['alvo']}  Valor alvo", font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")
        ctk.CTkLabel(val_f, text=f"{m['guardado']}  Já guardado", font=fonte(10, "bold"), text_color=cor_prog, anchor="w").pack(anchor="w")

        det_f = ctk.CTkFrame(card, fg_color="transparent")
        det_f.pack(fill="x", padx=12, pady=4)
        det_f.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(det_f, text=f"📅 {m['prazo']}\nPrazo", font=fonte(8), text_color=COR_TEXTO_MUTED, justify="center").grid(row=0, column=0)
        ctk.CTkLabel(det_f, text=f"💰 {m['mensal']}\nMensal", font=fonte(8), text_color=COR_TEXTO_MUTED, justify="center").grid(row=0, column=1)
        ctk.CTkLabel(det_f, text=f"🚩 {m['conclusao']}\nPrevisão", font=fonte(8), text_color=COR_TEXTO_MUTED, justify="center").grid(row=0, column=2)

        prog = ctk.CTkProgressBar(card, height=6, corner_radius=3, progress_color=cor_prog, fg_color="#1C2F3F")
        prog.set(m["pct"] / 100)
        prog.pack(fill="x", padx=12, pady=(6, 4))

        badge_bg = "#0D2E2B" if cor_prog == "#00D084" else "#12253A"
        badge = ctk.CTkFrame(card, fg_color=badge_bg, corner_radius=6)
        badge.pack(fill="x", padx=12, pady=(0, 10))
        ctk.CTkLabel(badge, text=m["msg"], font=fonte(9), text_color=cor_prog).pack(padx=8, pady=3)

        # Botão de guardar valor (se houver meta_id real)
        if meta_id:
            ctk.CTkButton(
                card, text="+ Guardar valor", height=28, corner_radius=6,
                fg_color="#0D2E2B", hover_color="#134E48", text_color="#00D084",
                font=fonte(9, "bold"),
                command=lambda mid=meta_id, alvo=m["alvo"]: self._guardar_valor_dialog(mid),
            ).pack(fill="x", padx=12, pady=(0, 10))

    def _confirmar_excluir(self, meta_id: int):
        if not messagebox.askyesno(
            "Excluir meta", "Deseja excluir esta meta e todo o histórico de aportes dela?",
            parent=self.winfo_toplevel(),
        ):
            return
        try:
            excluida = self.dao.excluir(meta_id)
        except Exception as exc:
            messagebox.showerror("Erro ao excluir meta", str(exc), parent=self.winfo_toplevel())
            return
        if not excluida:
            messagebox.showwarning("Meta não encontrada", "Esta meta já foi removida ou pertence a outra conta.", parent=self.winfo_toplevel())
            return
        self._aguardando_celebracao = [i for i in self._aguardando_celebracao if i != meta_id]
        self._montar_tela()
        messagebox.showinfo("Meta excluída", "Meta e aportes removidos com sucesso.", parent=self.winfo_toplevel())

    def _guardar_valor_dialog(self, meta_id: int):
        dialog = ctk.CTkToplevel(self.winfo_toplevel())
        dialog.title("Guardar Valor")
        dialog.geometry("360x180")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        dialog.configure(fg_color="#101C26")

        ctk.CTkLabel(dialog, text="Quanto deseja guardar agora? (R$)",
            font=fonte(12, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(pady=(20, 8))

        entry = ctk.CTkEntry(dialog, placeholder_text="Ex: 250.00", height=38,
            fg_color=COR_CARD_INTERNO, border_color=COR_BORDA, font=fonte(12))
        entry.pack(fill="x", padx=30)

        def confirmar():
            try:
                val = float(entry.get().replace(",", ".").strip())
                if val > 0:
                    resultado = self.dao.guardar_valor(meta_id, val)
                    if resultado.get("atingiu_agora"):
                        meta = self.dao.buscar_por_id(meta_id)
                        dialog.destroy()
                        self._exibir_celebracao(
                            meta_id=meta_id,
                            titulo=meta.get("descricao", "Meta"),
                            valor=float(meta.get("valor_alvo", 0)),
                        )
                        self._montar_tela()
                        return
            except Exception:
                pass
            dialog.destroy()
            self._montar_tela()

        ctk.CTkButton(dialog, text="Confirmar", height=38,
            fg_color="#00D084", hover_color="#00B875", text_color="#0B131B",
            font=fonte(11, "bold"), command=confirmar).pack(pady=14, padx=30, fill="x")


    def _criar_card_meta_largo(self, parent, m: dict):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card.pack(fill="x", padx=4, pady=(8, 4))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=10)

        # Emoji / Box
        img_box = ctk.CTkFrame(row, width=44, height=44, corner_radius=8, fg_color="#182A3A")
        img_box.pack(side="left", padx=(0, 10))
        img_box.pack_propagate(False)
        ctk.CTkLabel(img_box, text=m["emoji"], font=fonte(20)).place(relx=0.5, rely=0.5, anchor="center")

        # Título
        tit_f = ctk.CTkFrame(row, fg_color="transparent", width=120)
        tit_f.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(tit_f, text=m["titulo"], font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(tit_f, text=m["categoria"], font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        # Donut de Progresso vermelho
        c_prog = tk.Canvas(row, width=42, height=42, bg=obter_cor(COR_CARD), highlightthickness=0)
        c_prog.pack(side="left", padx=(0, 10))
        c_prog.create_arc(4, 4, 38, 38, start=0, extent=359, outline="#2E151B", width=4, style="arc")
        c_prog.create_arc(4, 4, 38, 38, start=90, extent=-180, outline="#F43F5E", width=4, style="arc")
        c_prog.create_text(21, 21, text="50%", fill="#FFFFFF", font=("Segoe UI", 8, "bold"))

        # Valores
        val_f = ctk.CTkFrame(row, fg_color="transparent")
        val_f.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(val_f, text=f"{m['alvo']}  Alvo", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="w")
        ctk.CTkLabel(val_f, text=f"{m['guardado']}  Guardado", font=fonte(10, "bold"), text_color="#F43F5E").pack(anchor="w")

        # Badge Atrasada
        b_atr = ctk.CTkFrame(row, fg_color="#2E151B", corner_radius=6)
        b_atr.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(b_atr, text="◇ Atrasada", font=fonte(9, "bold"), text_color="#F43F5E").pack(padx=6, pady=2)

        # Mensagem de alerta
        b_msg = ctk.CTkFrame(row, fg_color="#2E151B", corner_radius=6)
        b_msg.pack(side="right", padx=(8, 0))
        ctk.CTkLabel(b_msg, text=m["msg"], font=fonte(9), text_color="#F43F5E").pack(padx=8, pady=3)

    # ==============================================================
    # 4. COLUNA DIREITA: FORMULÁRIO + PROJEÇÃO DE ECONOMIA
    # ==============================================================
    def _build_coluna_formulario(self, parent):
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # 4.1 Card Nova Meta
        self._build_card_nova_meta(col)

        # 4.2 Card Projeção de Economia
        self._build_card_projecao(col)

    def _build_card_nova_meta(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=14, border_width=1, border_color=COR_BORDA)
        card.pack(fill="x", pady=(0, 10))

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 12))

        ic_box = ctk.CTkFrame(topo, width=32, height=32, corner_radius=16, fg_color="#0D2E2B")
        ic_box.pack(side="left", padx=(0, 10))
        ic_box.pack_propagate(False)
        ctk.CTkLabel(ic_box, text="＋", font=fonte(14, "bold"), text_color="#00D084").place(relx=0.5, rely=0.5, anchor="center")

        t_box = ctk.CTkFrame(topo, fg_color="transparent")
        t_box.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(t_box, text="Nova Meta", font=fonte(14, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(t_box, text="Defina um objetivo e comece a construir seu futuro.", font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        # Campo: Objetivo / Descrição
        ctk.CTkLabel(card, text="Objetivo / Descrição", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        self.entry_desc = ctk.CTkEntry(
            card, placeholder_text="Ex: Reserva de Emergência, Viagem, Carro...", height=36, corner_radius=8,
            fg_color=COR_CARD_INTERNO, border_width=1, border_color=COR_BORDA, text_color=COR_TEXTO_PRINCIPAL, font=fonte(11)
        )
        self.entry_desc.pack(fill="x", padx=16, pady=(0, 10))

        # Linha: Valor alvo | Valor já guardado
        l1 = ctk.CTkFrame(card, fg_color="transparent")
        l1.pack(fill="x", padx=16, pady=(0, 10))
        l1.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(l1, text="Valor alvo (R$)", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.entry_alvo = ctk.CTkEntry(
            l1, placeholder_text="R$ 0,00", height=36, corner_radius=8,
            fg_color=COR_CARD_INTERNO, border_width=1, border_color=COR_BORDA, font=fonte(11)
        )
        self.entry_alvo.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(l1, text="Valor já guardado (R$)", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.entry_atual = ctk.CTkEntry(
            l1, placeholder_text="R$ 0,00", height=36, corner_radius=8,
            fg_color=COR_CARD_INTERNO, border_width=1, border_color=COR_BORDA, font=fonte(11)
        )
        self.entry_atual.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # Linha: Prazo estimado | Contribuição mensal
        l2 = ctk.CTkFrame(card, fg_color="transparent")
        l2.pack(fill="x", padx=16, pady=(0, 10))
        l2.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(l2, text="Prazo estimado", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.combo_prazo = ctk.CTkOptionMenu(
            l2, values=["3 meses", "6 meses", "12 meses", "18 meses", "24 meses", "36 meses"],
            height=36, corner_radius=8, fg_color=COR_CARD_INTERNO, button_color=COR_CARD_INTERNO, text_color=COR_TEXTO_PRINCIPAL, font=fonte(11)
        )
        self.combo_prazo.set("6 meses")
        self.combo_prazo.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkLabel(l2, text="Contribuição mensal (R$)", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=1, sticky="w", pady=(0, 4))
        self.entry_mensal = ctk.CTkEntry(
            l2, placeholder_text="R$ 0,00", height=36, corner_radius=8,
            fg_color=COR_CARD_INTERNO, border_width=1, border_color=COR_BORDA, font=fonte(11)
        )
        self.entry_mensal.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # Data limite
        ctk.CTkLabel(card, text="Data limite (opcional)", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        self.entry_data = ctk.CTkEntry(
            card, placeholder_text="dd/mm/aaaa", height=36, corner_radius=8,
            fg_color=COR_CARD_INTERNO, border_width=1, border_color=COR_BORDA, text_color=COR_TEXTO_PRINCIPAL, font=fonte(11)
        )
        self.entry_data.pack(fill="x", padx=16, pady=(0, 16))

        # Botão Criar Meta Teal
        ctk.CTkButton(
            card,
            text="＋  Criar meta",
            height=40,
            corner_radius=10,
            fg_color="#00D084",
            hover_color="#00B875",
            text_color="#0B131B",
            font=fonte(12, "bold"),
            command=self._salvar_meta,
        ).pack(fill="x", padx=16, pady=(0, 16))

    @staticmethod
    def _parse_valor(texto: str) -> float:
        """Converte 'R$ 1.500,50', '1500,50' ou '1500.50' em float."""
        t = (texto or "").replace("R$", "").replace(" ", "").strip()
        if not t:
            return 0.0
        if "," in t:
            t = t.replace(".", "").replace(",", ".")
        elif re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
            t = t.replace(".", "")  # '2.000' → 2000 (separador de milhar pt-BR)
        return float(t)

    def _salvar_meta(self):
        from tkinter import messagebox

        desc = self.entry_desc.get().strip()
        if not desc:
            messagebox.showwarning("Nova meta", "Informe o objetivo / descrição da meta.")
            return

        try:
            alvo = self._parse_valor(self.entry_alvo.get())
            atual = self._parse_valor(self.entry_atual.get())
        except ValueError:
            messagebox.showwarning("Nova meta", "Informe valores numéricos válidos (ex.: 1500,00).")
            return

        if alvo <= 0:
            messagebox.showwarning("Nova meta", "O valor alvo deve ser maior que zero.")
            return
        if atual < 0:
            messagebox.showwarning("Nova meta", "O valor já guardado não pode ser negativo.")
            return

        data_lim = self.entry_data.get().strip() or None
        prazo = self.combo_prazo.get() if hasattr(self, "combo_prazo") else None

        try:
            self.dao.inserir(
                descricao=desc,
                valor_alvo=alvo,
                valor_atual=atual,
                prazo=prazo,
                data_limite=data_lim,
            )
        except ValueError as exc:
            # Data inválida / sem usuário logado
            messagebox.showwarning("Nova meta", str(exc))
            return
        except Exception as exc:
            messagebox.showerror("Nova meta", f"Não foi possível salvar a meta:\n{exc}")
            return

        # Limpar campos
        self.entry_desc.delete(0, "end")
        self.entry_alvo.delete(0, "end")
        self.entry_atual.delete(0, "end")
        self.entry_mensal.delete(0, "end")
        self.entry_data.delete(0, "end")
        self._montar_tela()

    def _build_card_projecao(self, parent):
        """Exibe o progresso real salvo no MySQL sem gráfico ou valores inventados."""
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=14,
                            border_width=1, border_color=COR_BORDA)
        card.pack(fill="x")
        ctk.CTkLabel(card, text="📈  Progresso das suas metas", font=fonte(12, "bold"),
                     text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(15, 4))
        metas = self.dao.listar_todas()
        if not metas:
            ctk.CTkLabel(card, text="Cadastre uma meta para acompanhar o progresso aqui.",
                         font=fonte(11), text_color=COR_TEXTO_SECUNDARIO,
                         wraplength=300, justify="left").pack(anchor="w", padx=16, pady=(6, 18))
            return

        for meta in metas[:4]:
            nome = meta.get("descricao", "Meta")
            atual = float(meta.get("valor_atual", 0) or 0)
            alvo = float(meta.get("valor_alvo", 0) or 0)
            progresso = min(1.0, max(0.0, atual / alvo)) if alvo > 0 else 0.0
            linha = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=9)
            linha.pack(fill="x", padx=14, pady=5)
            ctk.CTkLabel(linha, text=f"{nome}   •   {progresso:.0%}", font=fonte(11, "bold"),
                         text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w", padx=12, pady=(8, 2))
            ctk.CTkLabel(linha, text=f"R$ {atual:,.2f} de R$ {alvo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                         font=fonte(10), text_color=COR_TEXTO_SECUNDARIO,
                         anchor="w").pack(anchor="w", padx=12, pady=(0, 5))
            barra = ctk.CTkProgressBar(linha, progress_color="#00D084", fg_color="#253645")
            barra.set(progresso)
            barra.pack(fill="x", padx=12, pady=(0, 11))
        ctk.CTkLabel(card, text="", height=5).pack()

    def _set_filtro(self, aba: str):
        self.filtro_aba = aba
        self._montar_tela()
