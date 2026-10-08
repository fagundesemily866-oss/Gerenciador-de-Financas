"""
View de Meu Perfil —
===================================================================

Painel completo de dados pessoais, segurança e preferências:
1. Topo: Breadcrumb, título descritivo e card de segurança criptográfica.
2. Banner Hero do Usuário: Avatar circular com troca de foto, nome, e-mail, badges e 4 mini métricas.
3. Grid 2x2:
   - Dados do Perfil (Nome, E-mail, Renda, Tipo de Perfil e botão Salvar)
   - Segurança da Conta (Senha atual, nova senha, confirmação com visualização e botão Atualizar)
   - Preferências do Aplicativo (Tema da Interface, Idioma e Switch de Notificações)
   - Privacidade e Dados (Meus Dados, Segurança e Excluir Conta)
"""
from datetime import datetime, date
from math import isfinite
from typing import Optional, Callable, Tuple
from PIL import Image
from tkinter import filedialog
import customtkinter as ctk

from dao.usuario_dao import UsuarioDAO
from services.foto_perfil import avatar_circular, carregar_foto, salvar_foto
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_MUTED,
    fonte,
)

MESES_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]

SENHA_MIN = 4


# ==================================================================
# Utilitários de valor monetário (padrão brasileiro)
# ==================================================================
def _parse_valor(txt: str) -> float:
    """Converte '5.000,00', '5000,00' ou '5000.00' em float. Levanta ValueError se inválido."""
    txt = (txt or "").replace("R$", "").replace(" ", "").strip()
    if not txt:
        return 0.0
    if "," in txt:  # padrão BR: 5.000,00
        txt = txt.replace(".", "").replace(",", ".")
    valor = float(txt)  # padrão 5000.00 passa direto
    if not isfinite(valor) or valor < 0:
        raise ValueError("valor inválido")
    return valor


def _fmt_brl(valor: float) -> str:
    """5000 -> '5.000,00'."""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _formatar_data(valor) -> Tuple[str, str]:
    """Devolve (data longa, data curta). Ex.: ('29 de setembro de 2026', '29/09/2026')."""
    dt = None
    if isinstance(valor, datetime):
        dt = valor.date()
    elif isinstance(valor, date):
        dt = valor
    elif isinstance(valor, str):
        texto = valor.strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                dt = datetime.strptime(texto, fmt).date()
                break
            except ValueError:
                continue
        if dt is None:
            # já pode estar em formato longo ("29 de setembro de 2026"): usa como veio
            return texto or "—", texto or "—"
    if dt is None:
        return "—", "—"
    longa = f"{dt.day} de {MESES_PT[dt.month - 1]} de {dt.year}"
    return longa, dt.strftime("%d/%m/%Y")


class UsuarioView(ctk.CTkFrame):
    """Tela de Meu Perfil redesenhada fiel à imagem 09_meu_perfil.png."""

    # Tamanho (em pixels) da foto dentro do círculo grande do perfil
    AVATAR_TAMANHO = 72

    def __init__(
        self,
        parent,
        dao: Optional[UsuarioDAO] = None,
        usuario_atual: Optional[dict] = None,
        on_foto_atualizada: Optional[Callable] = None,
        on_conta_excluida: Optional[Callable] = None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.dao = dao or UsuarioDAO()
        self.on_foto_atualizada = on_foto_atualizada
        self.on_conta_excluida = on_conta_excluida
        self.usuario_atual = usuario_atual or {
            "id": 1,
            "nome": "Usuário",
            "email": "",
            "tipo_perfil": "PF",
            "data_criacao": date.today().strftime("%Y-%m-%d"),
        }

        # Avatar grande do perfil (label do círculo + imagem; a referência da imagem
        # precisa ficar guardada, senão o Python a descarta e o círculo fica vazio)
        self.lbl_avatar_perfil = None
        self.avatar_perfil_image = None

        self._scroll = None
        self._aviso_job = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Faixa de aviso (feedback ao usuário). Fica fora do scroll para sobreviver
        # à reconstrução da tela depois de salvar.
        self.lbl_aviso = ctk.CTkLabel(
            self, text="", font=fonte(11, "bold"), corner_radius=8,
            fg_color="transparent", anchor="w",
        )
        self.lbl_aviso.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.lbl_aviso.grid_remove()

        self._montar_tela()

    def atualizar_dados(self):
        self._montar_tela()

    def _montar_tela(self):
        if self._scroll is not None:
            try:
                self._scroll.destroy()
            except Exception:
                pass

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.grid(row=1, column=0, sticky="nsew")
        self._scroll.grid_columnconfigure(0, weight=1)

        # 1. CABEÇALHO & CARD DE SEGURANÇA
        self._build_header(self._scroll)

        # 2. BANNER HERO DO USUÁRIO
        self._build_hero_banner(self._scroll)

        # 3. GRID 2X2 DE CARDS
        self._build_grid_cards(self._scroll)

    # ==============================================================
    # FEEDBACK
    # ==============================================================
    def _notificar(self, mensagem: str, ok: bool = True):
        """Mostra uma faixa verde (sucesso) ou vermelha (erro) por alguns segundos."""
        cor = ("#D1FAE5", "#0D3B2E") if ok else ("#FEE2E2", "#4C1D24")
        txt = ("#065F46", "#34D399") if ok else ("#991B1B", "#FB7185")
        self.lbl_aviso.configure(
            text=("  ✔  " if ok else "  ✖  ") + mensagem,
            fg_color=cor, text_color=txt, height=34,
        )
        self.lbl_aviso.grid()

        if self._aviso_job is not None:
            try:
                self.after_cancel(self._aviso_job)
            except Exception:
                pass
        self._aviso_job = self.after(5000, self._limpar_aviso)

    def _limpar_aviso(self):
        self._aviso_job = None
        try:
            self.lbl_aviso.grid_remove()
        except Exception:
            pass

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
    def _iniciais_usuario(self) -> str:
        """Iniciais do nome (ex.: 'Usuário Demo' -> 'UD')."""
        nome = (self.usuario_atual.get("nome") or "Usuário").strip()
        partes = nome.split()
        if not partes:
            return "U"
        if len(partes) == 1:
            return partes[0][0].upper()
        return (partes[0][0] + partes[-1][0]).upper()

    def _aplicar_foto_no_avatar(self, imagem_pil: Image.Image):
        """Recorta a imagem em círculo e coloca no avatar grande do perfil."""
        if self.lbl_avatar_perfil is None:
            return
        try:
            if not self.lbl_avatar_perfil.winfo_exists():
                return
        except Exception:
            return

        tamanho = self.AVATAR_TAMANHO
        img = avatar_circular(imagem_pil, tamanho)

        self.avatar_perfil_image = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(tamanho, tamanho),
        )
        self.lbl_avatar_perfil.configure(image=self.avatar_perfil_image, text="")

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

        self.lbl_avatar_perfil = ctk.CTkLabel(
            av_box,
            text=self._iniciais_usuario(),
            font=fonte(22, "bold"),
            text_color="#00D084",
            width=self.AVATAR_TAMANHO,
            height=self.AVATAR_TAMANHO,
            fg_color="transparent",
        )
        self.lbl_avatar_perfil.place(relx=0.5, rely=0.5, anchor="center")

        # Botão Câmera sobreposto
        btn_cam = ctk.CTkButton(
            av_box, text="📷", width=24, height=24, corner_radius=12,
            fg_color="#102F33", hover_color="#18484E", text_color="#FFFFFF", font=fonte(10),
            command=self._trocar_foto,
        )
        btn_cam.place(relx=0.85, rely=0.85, anchor="center")

        # Recupera a foto do MySQL/disco mesmo após fechar e reabrir o aplicativo.
        foto_salva = carregar_foto(self.usuario_atual.get("foto_perfil"))
        if foto_salva is not None:
            self._aplicar_foto_no_avatar(foto_salva)

        # Dados do Usuário
        info_f = ctk.CTkFrame(inner, fg_color="transparent")
        info_f.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(info_f, text=self.usuario_atual.get("nome", "Usuário"), font=fonte(18, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(info_f, text=self.usuario_atual.get("email", ""), font=fonte(11), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w", pady=(2, 6))

        data_longa, data_curta = _formatar_data(self.usuario_atual.get("data_criacao"))

        # Badges em pílula
        b_row = ctk.CTkFrame(info_f, fg_color="transparent")
        b_row.pack(anchor="w")

        b1 = ctk.CTkFrame(b_row, fg_color="#10253B", corner_radius=6)
        b1.pack(side="left", padx=(0, 8))
        tipo = self.usuario_atual.get("tipo_perfil", "PF")
        nome_tipo = "Pessoa Jurídica" if tipo == "PJ" else "Pessoa Física"
        ctk.CTkLabel(b1, text=f" {nome_tipo} ({tipo}) ", font=fonte(9, "bold"), text_color="#38BDF8").pack(padx=6, pady=2)

        b2 = ctk.CTkFrame(b_row, fg_color=COR_CARD_INTERNO, corner_radius=6)
        b2.pack(side="left")
        ctk.CTkLabel(b2, text=f" 📅 Membro desde {data_longa} ", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(padx=6, pady=2)

        # 4 Mini Cards Métricas à Direita
        dir_m = ctk.CTkFrame(inner, fg_color="transparent")
        dir_m.grid(row=0, column=2, rowspan=2, sticky="e")

        mini_cards = [
            ("👑", "Tipo de Conta", f"{nome_tipo} ({tipo})", COR_TEXTO_PRINCIPAL),
            ("📅", "Membro desde", data_curta, COR_TEXTO_PRINCIPAL),
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

        self._build_card_dados_perfil(grid)   # superior esquerdo
        self._build_card_seguranca(grid)      # superior direito
        self._build_card_preferencias(grid)   # inferior esquerdo
        self._build_card_privacidade(grid)    # inferior direito

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

        btn_sv = ctk.CTkButton(
            topo, text="💾  Salvar", height=28, width=80, corner_radius=6,
            fg_color=COR_CARD_INTERNO, hover_color=("#CBD5E1", "#1E3143"), text_color="#38BDF8", font=fonte(10, "bold"),
            command=self._salvar_dados,
        )
        btn_sv.pack(side="right")

        ctk.CTkLabel(card, text="Mantenha suas informações pessoais sempre atualizadas.", font=fonte(10), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 12))

        # Nome Completo
        ctk.CTkLabel(card, text="Nome Completo", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_n = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        f_n.pack(fill="x", padx=16, pady=(0, 10))
        f_n.pack_propagate(False)
        ctk.CTkLabel(f_n, text="🢪", font=fonte(11)).pack(side="left", padx=8)
        self.entry_nome = ctk.CTkEntry(f_n, fg_color="transparent", border_width=0, font=fonte(11), text_color=COR_TEXTO_PRINCIPAL)
        self.entry_nome.insert(0, self.usuario_atual.get("nome", "Usuário"))
        self.entry_nome.pack(side="left", fill="both", expand=True)

        # E-mail
        ctk.CTkLabel(card, text="E-mail", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_e = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        f_e.pack(fill="x", padx=16, pady=(0, 10))
        f_e.pack_propagate(False)
        ctk.CTkLabel(f_e, text="✉️", font=fonte(11)).pack(side="left", padx=8)
        self.entry_email = ctk.CTkEntry(f_e, fg_color="transparent", border_width=0, font=fonte(11), text_color=COR_TEXTO_PRINCIPAL)
        self.entry_email.insert(0, self.usuario_atual.get("email", ""))
        self.entry_email.pack(side="left", fill="both", expand=True)

        # Renda Mensal
        ctk.CTkLabel(card, text="Renda Mensal (R$)", font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_r = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        f_r.pack(fill="x", padx=16, pady=(0, 10))
        f_r.pack_propagate(False)
        ctk.CTkLabel(f_r, text="💰", font=fonte(11)).pack(side="left", padx=8)
        self.entry_renda = ctk.CTkEntry(f_r, placeholder_text="Ex: 5.000,00", fg_color="transparent", border_width=0, font=fonte(11), text_color=COR_TEXTO_PRINCIPAL)
        try:
            renda_atual = float(self.usuario_atual.get("renda_mensal", 0) or 0)
        except (TypeError, ValueError):
            renda_atual = 0.0
        if renda_atual:
            self.entry_renda.insert(0, _fmt_brl(renda_atual))
        self.entry_renda.pack(side="left", fill="both", expand=True)

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
        # respeita o valor salvo (antes sempre voltava para PF)
        if self.usuario_atual.get("tipo_perfil") == "PJ":
            self.combo_perfil.set("Pessoa Jurídica (PJ)")
        else:
            self.combo_perfil.set("Pessoa Física (PF)")
        self.combo_perfil.pack(side="left", fill="both", expand=True)

    def _campo_senha(self, card, titulo: str, placeholder: str, pady_final):
        """Campo de senha com ícone 👁 que alterna mostrar/ocultar."""
        ctk.CTkLabel(card, text=titulo, font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        frame = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=36)
        frame.pack(fill="x", padx=16, pady=(0, pady_final))
        frame.pack_propagate(False)
        ctk.CTkLabel(frame, text="🔒", font=fonte(11)).pack(side="left", padx=8)

        entry = ctk.CTkEntry(frame, placeholder_text=placeholder, show="•", fg_color="transparent", border_width=0, font=fonte(11))
        entry.pack(side="left", fill="both", expand=True)

        olho = ctk.CTkLabel(frame, text="👁", font=fonte(11), text_color=COR_TEXTO_MUTED, cursor="hand2")
        olho.pack(side="right", padx=8)

        def alternar(_event=None):
            visivel = entry.cget("show") == ""
            entry.configure(show="•" if visivel else "")
            olho.configure(text_color=COR_TEXTO_MUTED if visivel else "#00D084")

        olho.bind("<Button-1>", alternar)
        return entry

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

        self.entry_senha_atual = self._campo_senha(card, "Senha Atual", "Digite sua senha atual", 8)
        self.entry_senha_nova = self._campo_senha(card, "Nova Senha", f"Mínimo de {SENHA_MIN} caracteres", 8)
        self.entry_senha_conf = self._campo_senha(card, "Confirmar Nova Senha", "Confirme a nova senha", 12)

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
        # reflete o tema realmente ativo (antes voltava sempre para "Dark")
        modo = ctk.get_appearance_mode()  # "Dark" ou "Light"
        combo_t.set(modo if modo in ("Dark", "Light") else "Dark")
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
            ("🗄️", "Meus Dados", "Visualize um resumo dos seus dados armazenados.", COR_TEXTO_PRINCIPAL, self._abrir_meus_dados),
            ("🛡️", "Segurança", "Saiba como mantemos seus dados seguros.", COR_TEXTO_PRINCIPAL, self._abrir_seguranca),
            ("🗑️", "Excluir Conta", "Solicite a exclusão permanente da sua conta e dados.", "#F43F5E", self._confirmar_exclusao),
        ]

        for ic, tit, sub, cor_tit, acao in itens_priv:
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

            self._tornar_clicavel(btn_item, acao)

        ctk.CTkLabel(card, text="", height=8).pack()

    def _tornar_clicavel(self, widget, acao: Callable):
        """Liga o clique do mouse ao widget e a todos os seus filhos."""
        widget.bind("<Button-1>", lambda _e: acao())
        for filho in widget.winfo_children():
            self._tornar_clicavel(filho, acao)

    # ==============================================================
    # AÇÕES — DADOS DO PERFIL
    # ==============================================================
    def _salvar_dados(self):
        nom = self.entry_nome.get().strip()
        em = self.entry_email.get().strip()
        tp = "PJ" if "PJ" in self.combo_perfil.get() else "PF"

        if not nom:
            self._notificar("Informe o nome completo.", ok=False)
            return
        if "@" not in em or "." not in em.split("@")[-1]:
            self._notificar("Informe um e-mail válido.", ok=False)
            return
        try:
            renda = _parse_valor(self.entry_renda.get())
        except ValueError:
            self._notificar("Renda mensal inválida. Use o formato 5.000,00.", ok=False)
            return

        try:
            self.dao.atualizar(
                usuario_id=self.usuario_atual.get("id", 1),
                nome=nom,
                email=em,
                tipo_perfil=tp,
                renda_mensal=renda,
            )
        except Exception as e:
            # não altera o dicionário local se o banco recusou
            self._notificar(f"Não foi possível salvar: {e}", ok=False)
            return

        self.usuario_atual["nome"] = nom
        self.usuario_atual["email"] = em
        self.usuario_atual["tipo_perfil"] = tp
        self.usuario_atual["renda_mensal"] = renda

        self._montar_tela()
        self._notificar("Dados do perfil atualizados com sucesso.")

    # ==============================================================
    # AÇÕES — SENHA
    # ==============================================================
    def _atualizar_senha(self):
        s_atu = self.entry_senha_atual.get()
        s_nov = self.entry_senha_nova.get()
        s_cnf = self.entry_senha_conf.get()

        if not s_atu:
            self._notificar("Digite sua senha atual.", ok=False)
            return
        if len(s_nov) < SENHA_MIN:
            self._notificar(f"A nova senha deve ter no mínimo {SENHA_MIN} caracteres.", ok=False)
            return
        if s_nov != s_cnf:
            self._notificar("A confirmação não confere com a nova senha.", ok=False)
            return
        if s_nov == s_atu:
            self._notificar("A nova senha deve ser diferente da atual.", ok=False)
            return

        uid = self.usuario_atual.get("id", 1)

        # Confere a senha atual, se o DAO oferecer esse método
        verificar = getattr(self.dao, "verificar_senha", None)
        if callable(verificar):
            try:
                if not verificar(uid, s_atu):
                    self._notificar("Senha atual incorreta.", ok=False)
                    return
            except Exception as e:
                self._notificar(f"Não foi possível verificar a senha: {e}", ok=False)
                return

        try:
            self.dao.atualizar_senha(uid, s_nov)
        except Exception as e:
            self._notificar(f"Não foi possível atualizar a senha: {e}", ok=False)
            return

        for entry in (self.entry_senha_atual, self.entry_senha_nova, self.entry_senha_conf):
            entry.delete(0, "end")
        self._notificar("Senha atualizada com sucesso.")

    # ==============================================================
    # AÇÕES — PRIVACIDADE
    # ==============================================================
    def _dialogo(self, titulo: str, texto: str, confirmar: Optional[Callable] = None,
                 texto_confirmar: str = "Confirmar", perigo: bool = False):
        """Janela modal simples. Se 'confirmar' for passado, mostra Cancelar + Confirmar."""
        win = ctk.CTkToplevel(self)
        win.title(titulo)
        win.geometry("420x280")
        win.resizable(False, False)
        win.transient(self.winfo_toplevel())
        win.after(100, lambda: win.winfo_exists() and win.grab_set())

        ctk.CTkLabel(win, text=titulo, font=fonte(15, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=20, pady=(18, 8))
        ctk.CTkLabel(
            win, text=texto, font=fonte(11), text_color=COR_TEXTO_SECUNDARIO,
            justify="left", anchor="nw", wraplength=380,
        ).pack(fill="both", expand=True, padx=20)

        botoes = ctk.CTkFrame(win, fg_color="transparent")
        botoes.pack(fill="x", padx=20, pady=16)

        if confirmar is None:
            ctk.CTkButton(botoes, text="Fechar", width=100, command=win.destroy).pack(side="right")
            return

        def ok():
            win.destroy()
            confirmar()

        ctk.CTkButton(
            botoes, text=texto_confirmar, width=120,
            fg_color="#F43F5E" if perigo else "#1E3A5F",
            hover_color="#E11D48" if perigo else "#2B4D7E",
            command=ok,
        ).pack(side="right")
        ctk.CTkButton(
            botoes, text="Cancelar", width=100,
            fg_color=COR_CARD_INTERNO, hover_color=("#CBD5E1", "#1E3143"),
            text_color=COR_TEXTO_PRINCIPAL, command=win.destroy,
        ).pack(side="right", padx=(0, 8))

    def _abrir_meus_dados(self):
        u = self.usuario_atual
        tipo = "Pessoa Jurídica (PJ)" if u.get("tipo_perfil") == "PJ" else "Pessoa Física (PF)"
        try:
            renda = _fmt_brl(float(u.get("renda_mensal", 0) or 0))
        except (TypeError, ValueError):
            renda = "0,00"
        data_longa, _ = _formatar_data(u.get("data_criacao"))
        texto = (
            f"Nome: {u.get('nome', '—')}\n"
            f"E-mail: {u.get('email', '—')}\n"
            f"Tipo de perfil: {tipo}\n"
            f"Renda mensal: R$ {renda}\n"
            f"Membro desde: {data_longa}"
        )
        self._dialogo("Meus Dados", texto)

    def _abrir_seguranca(self):
        texto = (
            "• Sua senha é armazenada de forma protegida, nunca em texto puro.\n"
            "• Seus dados financeiros ficam salvos apenas neste aplicativo.\n"
            "• Altere a senha periodicamente e não a compartilhe com ninguém.\n"
            "• Encerre a sessão ao usar um computador compartilhado."
        )
        self._dialogo("Segurança", texto)

    def _confirmar_exclusao(self):
        self._dialogo(
            "Excluir Conta",
            "Esta ação é permanente: sua conta e todos os dados financeiros "
            "associados serão apagados e não poderão ser recuperados.\n\n"
            "Deseja continuar?",
            confirmar=self._excluir_conta,
            texto_confirmar="Excluir",
            perigo=True,
        )

    def _excluir_conta(self):
        excluir = getattr(self.dao, "excluir", None) or getattr(self.dao, "deletar", None)
        if not callable(excluir):
            self._notificar("Exclusão de conta ainda não disponível no UsuarioDAO.", ok=False)
            return
        try:
            excluir(self.usuario_atual.get("id", 1))
        except Exception as e:
            self._notificar(f"Não foi possível excluir a conta: {e}", ok=False)
            return

        if self.on_conta_excluida:
            self.on_conta_excluida()
        else:
            self._notificar("Conta excluída.")

    # ==============================================================
    # AÇÕES — FOTO
    # ==============================================================
    def _trocar_foto(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp *.gif *.webp")]
        )
        if not caminho:
            return
        try:
            uid = self.usuario_atual["id"]
            novo_caminho, imagem = salvar_foto(uid, caminho, self.dao)
        except Exception as exc:
            self._notificar(f"Não foi possível salvar a foto: {exc}", ok=False)
            return

        # Atualizar somente DEPOIS de o MySQL confirmar a gravação.
        self.usuario_atual["foto_perfil"] = novo_caminho
        self._aplicar_foto_no_avatar(imagem)
        if self.on_foto_atualizada:
            self.on_foto_atualizada(imagem)
        self._notificar("Foto salva! Ela aparecerá também nos próximos acessos.")
