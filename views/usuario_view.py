"""
View de Meu Perfil — Redesign Fiel à Referência (09_meu_perfil.png)
===================================================================

Painel completo de dados pessoais, segurança e preferências:
1. Topo: Breadcrumb, título descritivo e card de segurança criptográfica.
2. Banner Hero do Usuário: Avatar circular com troca de foto, nome, e-mail, badges e 4 mini métricas.
3. Grid 2x2:
   - Dados do Perfil (Nome, E-mail, Tipo de Perfil e botão Editar)
   - Segurança da Conta (Senha atual, nova senha, confirmação com visualização e botão Atualizar)
   - Preferências do Aplicativo (Tema da Interface, Idioma e Switch de Notificações)
   - Privacidade e Dados (Meus Dados, Segurança e Excluir Conta)
"""
import tkinter as tk
from datetime import datetime, date
from typing import Optional, Dict, Any, Callable
from PIL import Image, ImageTk
from tkinter import filedialog
import customtkinter as ctk

from dao.usuario_dao import UsuarioDAO
from views.notificacao_toast import GerenciadorNotificacoes
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_SUCESSO, COR_ALERTA, COR_INFO,
    fonte, fonte_titulo, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
)


class UsuarioView(ctk.CTkFrame):
    """Tela de Meu Perfil redesenhada fiel à imagem 09_meu_perfil.png."""

    def __init__(
        self,
        parent,
        dao: Optional[UsuarioDAO] = None,
        usuario_atual: Optional[dict] = None,
        on_foto_atualizada: Optional[Callable] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.dao = dao or UsuarioDAO()
        self.on_foto_atualizada = on_foto_atualizada
        self.usuario_atual = usuario_atual or {
            "id": 1,
            "nome": "Usuário Demo",
            "email": "demo@financeiro.com",
            "tipo_perfil": "PF",
            "data_criacao": "29 de setembro de 2026",
        }

        self.editando_dados = False
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._montar_tela()

    def atualizar_dados(self):
        self._montar_tela()

    def _montar_tela(self):
        for w in self.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # 1. CABEÇALHO & CARD DE SEGURANÇA
        self._build_header(scroll)

        # 2. BANNER HERO DO USUÁRIO
        self._build_hero_banner(scroll)

        # 3. GRID 2X2 DE CARDS
        self._build_grid_cards(scroll)

    # ==============================================================
    # 1. CABEÇALHO
    # ==============================================================
    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 14))
        header.grid_columnconfigure(0, weight=1)

        tit_box = ctk.CTkFrame(header, fg_color="transparent")
        tit_box.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(tit_box, text="🏠  Meu Perfil", font=fonte(10, "bold"), text_color="#00D084", anchor="w").pack(anchor="w")
        ctk.CTkLabel(tit_box, text="Meu Perfil", font=fonte(24, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(
            tit_box,
            text="Gerencie seus dados, segurança e preferências da sua conta.",
            font=fonte(12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Card de Segurança à direita
        seg_box = ctk.CTkFrame(
            header,
            fg_color=("#ECFDF5", "#0D221C"),
            corner_radius=10,
            border_width=1,
            border_color=("#A7F3D0", "#134E48"),
        )
        seg_box.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(seg_box, text="🛡️", font=fonte(16)).pack(side="left", padx=(12, 8), pady=8)

        t_s = ctk.CTkFrame(seg_box, fg_color="transparent")
        t_s.pack(side="left", padx=(0, 14), pady=8)

        ctk.CTkLabel(t_s, text="Seus dados estão seguros", font=fonte(10, "bold"), text_color="#00D084", anchor="w").pack(anchor="w")
        ctk.CTkLabel(
            t_s,
            text="Utilizamos criptografia e boas práticas\nde segurança para proteger sua conta.",
            font=fonte(9),
            text_color=COR_TEXTO_MUTED,
            justify="left",
            anchor="w",
        ).pack(anchor="w")

    # ==============================================================
    # 2. BANNER HERO DO USUÁRIO
    # ==============================================================
    def _build_hero_banner(self, parent):
        card = ctk.CTkFrame(
            parent,
            fg_color=COR_CARD,
            corner_radius=14,
            border_width=1,
            border_color=COR_BORDA,
        )
        card.pack(fill="x", pady=(0, 14))
        card.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=18)
        inner.grid_columnconfigure(1, weight=1)

        # Avatar Circular Grande
        av_box = ctk.CTkFrame(inner, width=80, height=80, corner_radius=40, fg_color="#0F3836", border_width=2, border_color="#00D084")
        av_box.grid(row=0, column=0, rowspan=2, padx=(0, 16))
        av_box.pack_propagate(False)

        ctk.CTkLabel(av_box, text="UD", font=fonte(22, "bold"), text_color="#00D084").place(relx=0.5, rely=0.5, anchor="center")

        # Botão Câmera sobreposto
        btn_cam = ctk.CTkButton(
            av_box, text="📷", width=24, height=24, corner_radius=12,
            fg_color="#102F33", hover_color="#18484E", text_color="#FFFFFF", font=fonte(10),
            command=self._trocar_foto,
        )
        btn_cam.place(relx=0.85, rely=0.85, anchor="center")

        # Dados do Usuário
        info_f = ctk.CTkFrame(inner, fg_color="transparent")
        info_f.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(info_f, text=self.usuario_atual.get("nome", "Usuário Demo"), font=fonte(18, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(info_f, text=self.usuario_atual.get("email", "demo@financeiro.com"), font=fonte(11), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w", pady=(2, 6))

        # Badges em pílula
        b_row = ctk.CTkFrame(info_f, fg_color="transparent")
        b_row.pack(anchor="w")

        b1 = ctk.CTkFrame(b_row, fg_color="#10253B", corner_radius=6)
        b1.pack(side="left", padx=(0, 8))
        tipo = self.usuario_atual.get("tipo_perfil", "PF")
        ctk.CTkLabel(b1, text=f" Pessoa Física ({tipo}) ", font=fonte(9, "bold"), text_color="#38BDF8").pack(padx=6, pady=2)

        b2 = ctk.CTkFrame(b_row, fg_color=COR_CARD_INTERNO, corner_radius=6)
        b2.pack(side="left")
        ctk.CTkLabel(b2, text=" 📅 Membro desde 29 de setembro de 2026 ", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(padx=6, pady=2)

        # 4 Mini Cards Métricas à Direita
        dir_m = ctk.CTkFrame(inner, fg_color="transparent")
        dir_m.grid(row=0, column=2, rowspan=2, sticky="e")

        mini_cards = [
            ("👑", "Tipo de Conta", f"Pessoa Física ({tipo})", COR_TEXTO_PRINCIPAL),
            ("📅", "Membro desde", "29/09/2026", COR_TEXTO_PRINCIPAL),
            ("🛡️", "Status da Conta", "● Ativa", "#00D084"),
            ("📊", "Dados", "Sincronizados", "#00D084"),
        ]

        for ic, lbl, val, cor_v in mini_cards:
            mc = ctk.CTkFrame(dir_m, fg_color=COR_CARD_INTERNO, corner_radius=8, width=110, height=52)
            mc.pack(side="left", padx=4)
            mc.pack_propagate(False)

            ctk.CTkLabel(mc, text=f"{ic} {lbl}", font=fonte(8), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w", padx=8, pady=(6, 1))
            ctk.CTkLabel(mc, text=val, font=fonte(9, "bold"), text_color=cor_v, anchor="w").pack(anchor="w", padx=8)

    # ==============================================================
    # 3. GRID 2X2 DE CARDS PRINCIPAIS
    # ==============================================================
    def _build_grid_cards(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x")
        grid.grid_columnconfigure((0, 1), weight=1)

        # Card 1: Dados do Perfil (Superior Esquerdo)
        self._build_card_dados_perfil(grid)

        # Card 2: Segurança da Conta (Superior Direito)
        self._build_card_seguranca(grid)

        # Card 3: Preferências do Aplicativo (Inferior Esquerdo)
        self._build_card_preferencias(grid)

        # Card 4: Privacidade e Dados (Inferior Direito)
        self._build_card_privacidade(grid)

    def _build_card_dados_perfil(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=14, border_width=1, border_color=COR_BORDA)
        card.grid(row=0, column=0, padx=(0, 6), pady=(0, 12), sticky="nsew")

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 6))

        ic_b = ctk.CTkFrame(topo, width=30, height=30, corner_radius=15, fg_color="#122538")
        ic_b.pack(side="left", padx=(0, 8))
        ic_b.pack_propagate(False)
        ctk.CTkLabel(ic_b, text="👤", font=fonte(12)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(topo, text="Dados do Perfil", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        btn_ed = ctk.CTkButton(
            topo, text="✏  Editar", height=28, width=70, corner_radius=6,
            fg_color=COR_CARD_INTERNO, hover_color="#1E3143", text_color="#38BDF8", font=fonte(10, "bold"),
            command=self._alternar_edicao,
        )
        btn_ed.pack(side="right")

        ctk.CTkLabel(card, text="Mantenha suas informações pessoais sempre atualizadas.", font=fonte(10), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 12))

        # Nome Completo
        ctk.CTkLabel(card, text="Nome Completo", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_n = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        f_n.pack(fill="x", padx=16, pady=(0, 10))
        f_n.pack_propagate(False)
        ctk.CTkLabel(f_n, text="🪪", font=fonte(11)).pack(side="left", padx=8)
        self.entry_nome = ctk.CTkEntry(f_n, fg_color="transparent", border_width=0, font=fonte(11), text_color=COR_TEXTO_PRINCIPAL)
        self.entry_nome.insert(0, self.usuario_atual.get("nome", "Usuário Demo"))
        self.entry_nome.pack(side="left", fill="both", expand=True)

        # E-mail
        ctk.CTkLabel(card, text="E-mail", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_e = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        f_e.pack(fill="x", padx=16, pady=(0, 10))
        f_e.pack_propagate(False)
        ctk.CTkLabel(f_e, text="✉️", font=fonte(11)).pack(side="left", padx=8)
        self.entry_email = ctk.CTkEntry(f_e, fg_color="transparent", border_width=0, font=fonte(11), text_color=COR_TEXTO_PRINCIPAL)
        self.entry_email.insert(0, self.usuario_atual.get("email", "demo@financeiro.com"))
        self.entry_email.pack(side="left", fill="both", expand=True)

        # Tipo de Perfil
        ctk.CTkLabel(card, text="Tipo de Perfil", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_p = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        f_p.pack(fill="x", padx=16, pady=(0, 16))
        f_p.pack_propagate(False)
        ctk.CTkLabel(f_p, text="👥", font=fonte(11)).pack(side="left", padx=8)
        self.combo_perfil = ctk.CTkOptionMenu(
            f_p, values=["Pessoa Física (PF)", "Pessoa Jurídica (PJ)"], height=30,
            fg_color=COR_CARD_INTERNO, button_color=COR_CARD, text_color=COR_TEXTO_PRINCIPAL, font=fonte(11)
        )
        self.combo_perfil.set("Pessoa Física (PF)")
        self.combo_perfil.pack(side="left", fill="both", expand=True)

    def _build_card_seguranca(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=14, border_width=1, border_color=COR_BORDA)
        card.grid(row=0, column=1, padx=(6, 0), pady=(0, 12), sticky="nsew")

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 6))

        ic_b = ctk.CTkFrame(topo, width=30, height=30, corner_radius=15, fg_color="#0D2E2B")
        ic_b.pack(side="left", padx=(0, 8))
        ic_b.pack_propagate(False)
        ctk.CTkLabel(ic_b, text="🛡️", font=fonte(12)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(topo, text="Segurança da Conta", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        ctk.CTkLabel(card, text="Altere sua senha periodicamente para manter sua conta segura.", font=fonte(10), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 12))

        # Senha Atual
        ctk.CTkLabel(card, text="Senha Atual", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_s1 = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        f_s1.pack(fill="x", padx=16, pady=(0, 8))
        f_s1.pack_propagate(False)
        ctk.CTkLabel(f_s1, text="🔒", font=fonte(11)).pack(side="left", padx=8)
        self.entry_senha_atual = ctk.CTkEntry(f_s1, placeholder_text="Digite sua senha atual", show="•", fg_color="transparent", border_width=0, font=fonte(11))
        self.entry_senha_atual.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(f_s1, text="👁", font=fonte(11), text_color=COR_TEXTO_MUTED).pack(side="right", padx=8)

        # Nova Senha
        ctk.CTkLabel(card, text="Nova Senha", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_s2 = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        f_s2.pack(fill="x", padx=16, pady=(0, 8))
        f_s2.pack_propagate(False)
        ctk.CTkLabel(f_s2, text="🔒", font=fonte(11)).pack(side="left", padx=8)
        self.entry_senha_nova = ctk.CTkEntry(f_s2, placeholder_text="Mínimo de 4 caracteres", show="•", fg_color="transparent", border_width=0, font=fonte(11))
        self.entry_senha_nova.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(f_s2, text="👁", font=fonte(11), text_color=COR_TEXTO_MUTED).pack(side="right", padx=8)

        # Confirmar Nova Senha
        ctk.CTkLabel(card, text="Confirmar Nova Senha", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_s3 = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        f_s3.pack(fill="x", padx=16, pady=(0, 12))
        f_s3.pack_propagate(False)
        ctk.CTkLabel(f_s3, text="🔒", font=fonte(11)).pack(side="left", padx=8)
        self.entry_senha_conf = ctk.CTkEntry(f_s3, placeholder_text="Confirme a nova senha", show="•", fg_color="transparent", border_width=0, font=fonte(11))
        self.entry_senha_conf.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(f_s3, text="👁", font=fonte(11), text_color=COR_TEXTO_MUTED).pack(side="right", padx=8)

        # Botão Atualizar Senha
        ctk.CTkButton(
            card,
            text="🔒  Atualizar Senha",
            height=36,
            corner_radius=8,
            fg_color="#1E3A5F",
            hover_color="#2B4D7E",
            text_color="#38BDF8",
            font=fonte(11, "bold"),
            command=self._atualizar_senha,
        ).pack(fill="x", padx=16, pady=(0, 16))

    def _build_card_preferencias(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=14, border_width=1, border_color=COR_BORDA)
        card.grid(row=1, column=0, padx=(0, 6), sticky="nsew")

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 6))

        ic_b = ctk.CTkFrame(topo, width=30, height=30, corner_radius=15, fg_color="#122538")
        ic_b.pack(side="left", padx=(0, 8))
        ic_b.pack_propagate(False)
        ctk.CTkLabel(ic_b, text="⚙", font=fonte(12)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(topo, text="Preferências do Aplicativo", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        ctk.CTkLabel(card, text="Personalize sua experiência no sistema.", font=fonte(10), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 12))

        # 1. Tema da Interface
        r1 = ctk.CTkFrame(card, fg_color="transparent")
        r1.pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(r1, text="🖥️", font=fonte(14)).pack(side="left", padx=(0, 10))
        t1 = ctk.CTkFrame(r1, fg_color="transparent")
        t1.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(t1, text="Tema da Interface", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(t1, text="Escolha o tema visual do aplicativo.", font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        combo_t = ctk.CTkOptionMenu(
            r1, values=["Dark", "Light"], width=90, height=28,
            fg_color=COR_CARD_INTERNO, button_color=COR_CARD_INTERNO, text_color=COR_TEXTO_PRINCIPAL, font=fonte(10),
            command=ctk.set_appearance_mode
        )
        combo_t.set("Dark")
        combo_t.pack(side="right")

        # 2. Idioma
        r2 = ctk.CTkFrame(card, fg_color="transparent")
        r2.pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(r2, text="🌐", font=fonte(14)).pack(side="left", padx=(0, 10))
        t2 = ctk.CTkFrame(r2, fg_color="transparent")
        t2.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(t2, text="Idioma", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(t2, text="Idioma do sistema.", font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        combo_id = ctk.CTkOptionMenu(
            r2, values=["Português (Brasil)", "English (US)"], width=140, height=28,
            fg_color=COR_CARD_INTERNO, button_color=COR_CARD_INTERNO, text_color=COR_TEXTO_PRINCIPAL, font=fonte(10)
        )
        combo_id.set("Português (Brasil)")
        combo_id.pack(side="right")

        # 3. Notificações
        r3 = ctk.CTkFrame(card, fg_color="transparent")
        r3.pack(fill="x", padx=16, pady=(6, 16))

        ctk.CTkLabel(r3, text="🔔", font=fonte(14)).pack(side="left", padx=(0, 10))
        t3 = ctk.CTkFrame(r3, fg_color="transparent")
        t3.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(t3, text="Notificações", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(t3, text="Receba avisos sobre metas e vencimentos.", font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        sw = ctk.CTkSwitch(r3, text="Ativadas", font=fonte(10), progress_color="#00D084")
        sw.select()
        sw.pack(side="right")

    def _build_card_privacidade(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=14, border_width=1, border_color=COR_BORDA)
        card.grid(row=1, column=1, padx=(6, 0), pady=(0, 12), sticky="nsew")

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 6))

        ic_b = ctk.CTkFrame(topo, width=30, height=30, corner_radius=15, fg_color="#0D2E2B")
        ic_b.pack(side="left", padx=(0, 8))
        ic_b.pack_propagate(False)
        ctk.CTkLabel(ic_b, text="🔒", font=fonte(12)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(topo, text="Privacidade e Dados", font=fonte(13, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        ctk.CTkLabel(card, text="Suas informações e dados financeiros estão protegidos.", font=fonte(10), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 12))

        # Itens clicáveis
        itens_priv = [
            ("🗄️", "Meus Dados", "Visualize um resumo dos seus dados armazenados.", COR_TEXTO_PRINCIPAL),
            ("🛡️", "Segurança", "Saiba como mantemos seus dados seguros.", COR_TEXTO_PRINCIPAL),
            ("🗑️", "Excluir Conta", "Solicite a exclusão permanente da sua conta e dados.", "#F43F5E"),
        ]

        for ic, tit, sub, cor_tit in itens_priv:
            btn_item = ctk.CTkFrame(
                card,
                fg_color=COR_CARD_INTERNO,
                corner_radius=8,
                height=48,
                cursor="hand2",
            )
            btn_item.pack(fill="x", padx=16, pady=4)

            in_f = ctk.CTkFrame(btn_item, fg_color="transparent", cursor="hand2")
            in_f.pack(fill="both", expand=True, padx=8, pady=4)

            ctk.CTkLabel(in_f, text=ic, font=fonte(14)).pack(side="left", padx=(0, 8))

            t_box = ctk.CTkFrame(in_f, fg_color="transparent")
            t_box.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(t_box, text=tit, font=fonte(11, "bold"), text_color=cor_tit, anchor="w").pack(anchor="w")
            ctk.CTkLabel(t_box, text=sub, font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

            ctk.CTkLabel(in_f, text="›", font=fonte(16, "bold"), text_color=COR_TEXTO_MUTED).pack(side="right")

        ctk.CTkLabel(card, text="", height=8).pack()

    def _alternar_edicao(self):
        nom = self.entry_nome.get().strip()
        em = self.entry_email.get().strip()
        tp = "PF" if "PF" in self.combo_perfil.get() else "PJ"

        self.usuario_atual["nome"] = nom
        self.usuario_atual["email"] = em
        self.usuario_atual["tipo_perfil"] = tp

        try:
            self.dao.atualizar(
                id_usuario=self.usuario_atual.get("id", 1),
                nome=nom,
                email=em,
                tipo_perfil=tp,
            )
        except Exception:
            pass

        self._montar_tela()

    def _atualizar_senha(self):
        s_atu = self.entry_senha_atual.get().strip()
        s_nov = self.entry_senha_nova.get().strip()
        s_cnf = self.entry_senha_conf.get().strip()

        if s_nov and s_nov == s_cnf:
            try:
                self.dao.atualizar_senha(self.usuario_atual.get("id", 1), s_nov)
            except Exception:
                pass
            self.entry_senha_atual.delete(0, "end")
            self.entry_senha_nova.delete(0, "end")
            self.entry_senha_conf.delete(0, "end")

    def _trocar_foto(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if caminho:
            try:
                img = Image.open(caminho)
                if self.on_foto_atualizada:
                    self.on_foto_atualizada(img)
            except Exception:
                pass