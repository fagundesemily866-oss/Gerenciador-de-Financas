"""
View de Lançamentos — 
======================================================================

Layout completo para registro e controle de transações:
1. Topo: Cabeçalho com ícone, título, subtítulo e seletor de mês.
2. Linha de Métricas: Total de Receitas, Total de Despesas e Saldo Líquido com mini sparklines.
3. Coluna Esquerda: Formulário moderno "Novo Lançamento" com alternador [Despesa / Receita],
   campos com ícones inline, categorias e beneficiários, e botão de salvar contextual.
4. Coluna Direita: "Lançamentos Recentes" com abas [Todos / Receitas / Despesas], barra de busca,
   tabela refinada com badges de data, ícones de categoria, status de pagamento e menu de ações.

Validações do formulário:
- Valor obrigatório e maior que zero.
- Descrição, data (DD/MM/AAAA) e status obrigatórios.
- Mensagens de erro/sucesso em uma faixa no topo da tela.
- Ao salvar, o novo lançamento aparece na hora em "Lançamentos Recentes".
"""
import math
import tkinter as tk
from datetime import datetime, date
from tkinter import messagebox
from typing import Optional, List, Dict, Any, Tuple
import customtkinter as ctk

from dao.lancamento_dao import LancamentoDAO
from dao.categoria_dao import CategoriaDAO
from dao.terceiro_dao import TerceiroDAO
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_MUTED,
    fonte, obter_cor,
)

MESES_ABREV = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]

ICONES_CATEGORIA = {
    "Alimentação": "🍴", "Moradia": "🏠", "Transporte": "🚗", "Saúde": "🩺",
    "Lazer": "🎮", "Educação": "🎓", "Salário": "💼", "Investimentos": "📈",
    "Contas": "📄", "Serviços": "💼", "Outros": "🏷️",
}

# Status permitidos para cada tipo (o primeiro é o padrão)
STATUS_POR_TIPO = {
    "Despesa": ["Pago", "Pendente"],
    "Receita": ["Recebido", "Pendente"],
}

LIMITE_LINHAS = 30

# Lançamentos serão lidos exclusivamente do MySQL; nenhum exemplo embutido.


# ==================================================================
# Utilitários
# ==================================================================
def _parse_valor(txt: str) -> float:
    """Converte '10', '10,50', '1.200,00' ou '10.50' em float. Levanta ValueError se inválido."""
    txt = (txt or "").replace("R$", "").replace(" ", "").strip()
    if not txt:
        raise ValueError("vazio")
    if "," in txt:  # padrão BR: 1.200,50
        txt = txt.replace(".", "").replace(",", ".")
    elif txt.count(".") > 1:  # 1.200.000
        txt = txt.replace(".", "")
    elif "." in txt and len(txt.split(".")[1]) == 3:  # 1.200 -> 1200
        txt = txt.replace(".", "")
    valor = float(txt)
    if not math.isfinite(valor):
        raise ValueError("inválido")
    return valor


def _fmt_brl(valor: float) -> str:
    """5000 -> '5.000,00'."""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _para_date(valor) -> Optional[date]:
    """Converte str/date/datetime em date (ou None)."""
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        texto = valor.strip()
        for fmt, tam in (("%Y-%m-%d", 10), ("%d/%m/%Y", 10)):
            try:
                return datetime.strptime(texto[:tam], fmt).date()
            except ValueError:
                continue
    return None


class LancamentoView(ctk.CTkFrame):
    """Tela de Lançamentos redesenhada fiel à imagem 03_lancamentos.png."""

    def __init__(
        self,
        parent,
        dao: Optional[LancamentoDAO] = None,
        cat_dao: Optional[CategoriaDAO] = None,
        ter_dao: Optional[TerceiroDAO] = None,
    ):
        super().__init__(parent, fg_color="transparent")

        self.dao = dao or LancamentoDAO()
        self.cat_dao = cat_dao or CategoriaDAO()
        self.ter_dao = ter_dao or TerceiroDAO()

        self.tipo_selecionado = "Despesa"  # "Despesa" ou "Receita"
        self.filtro_aba = "Todos"          # "Todos", "Receitas", "Despesas"
        self.busca_texto = ""

        self._itens: List[Dict[str, Any]] = []
        self._usando_demo = False

        self._scroll = None
        self._aviso_job = None
        self._campos: Dict[str, Any] = {}
        self.botoes_abas: Dict[str, Any] = {}
        self.frame_lista = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Faixa de aviso (erro/sucesso). Fica fora do scroll, então continua visível
        # mesmo quando a tela é reconstruída depois de salvar.
        self.lbl_aviso = ctk.CTkLabel(
            self, text="", font=fonte(12, "bold"), corner_radius=8,
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

        self._nomes_terceiros = {tid: n for tid, n in self._listar_terceiros()}
        self._itens, self._usando_demo = self._carregar_itens()

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.grid(row=1, column=0, sticky="nsew")
        self._scroll.grid_columnconfigure(0, weight=1)

        # 1. CABEÇALHO
        self._build_header(self._scroll)

        # 2. MÉTRICAS (3 CARDS COM MINI GRÁFICOS)
        self._build_metricas(self._scroll)

        # 3. CORPO: FORMULÁRIO (ESQ) + HISTÓRICO (DIR)
        corpo = ctk.CTkFrame(self._scroll, fg_color="transparent")
        corpo.pack(fill="both", expand=True, pady=(0, 10))
        corpo.grid_columnconfigure(0, weight=4)
        corpo.grid_columnconfigure(1, weight=6)

        self._build_formulario(corpo)
        self._build_painel_historico(corpo)

    # ==============================================================
    # DADOS
    # ==============================================================
    def _carregar_itens(self) -> Tuple[List[Dict[str, Any]], bool]:
        """Lê somente os lançamentos do usuário autenticado, sem amostras fictícias."""
        try:
            reais = self.dao.listar_todos() or []
        except Exception:
            reais = []

        if not reais:
            return [], False

        itens = [self._normalizar(r) for r in reais]
        itens.sort(key=lambda i: (i["data"] or date.min, i["id"] or 0), reverse=True)
        return itens, False

    def _listar_terceiros(self) -> List[Tuple[Any, str]]:
        """Lista (id, nome) dos terceiros cadastrados."""
        for metodo in ("listar_todos", "listar_todas", "listar"):
            fn = getattr(self.ter_dao, metodo, None) if self.ter_dao else None
            if not callable(fn):
                continue
            try:
                resultado = []
                for t in fn() or []:
                    if isinstance(t, dict):
                        resultado.append((t.get("id"), str(t.get("nome") or "")))
                    else:
                        resultado.append((getattr(t, "id", None), str(getattr(t, "nome", "") or "")))
                return resultado
            except Exception:
                return []
        return []

    def _buscar_terceiro_id(self, nome: str) -> Optional[Any]:
        """Procura o id do terceiro pelo nome. Retorna None se não achar."""
        nome = (nome or "").strip().lower()
        if not nome:
            return None
        for tid, n in self._listar_terceiros():
            if n.strip().lower() == nome:
                return tid
        return None

    def _normalizar(self, r) -> Dict[str, Any]:
        """Converte uma linha do banco (dict com colunas em inglês) no formato da tela."""
        def campo(*nomes, padrao=None):
            for n in nomes:
                v = r.get(n) if isinstance(r, dict) else getattr(r, n, None)
                if v not in (None, ""):
                    return v
            return padrao

        tipo = campo("type", "tipo", padrao="Despesa")
        eh_rec = tipo == "Receita"
        try:
            valor = float(campo("value", "valor", padrao=0))
        except (TypeError, ValueError):
            valor = 0.0

        beneficiario = campo("beneficiario") or self._nomes_terceiros.get(campo("terceiro_id"), "")

        return {
            "id": campo("id"),
            "descricao": campo("description", "descricao", padrao="Item"),
            "sub": beneficiario or tipo,
            "categoria": campo("category", "categoria", padrao="Geral"),
            "tipo": tipo,
            "valor": valor,
            "data": _para_date(campo("date", "data")),
            "status": campo("status", padrao="Recebido" if eh_rec else "Pago"),
            "icone": "💼" if eh_rec else "🛒",
        }

    # ==============================================================
    # FEEDBACK (FAIXA DE AVISO)
    # ==============================================================
    def _notificar(self, mensagem: str, ok: bool = True):
        """Mostra uma faixa verde (sucesso) ou vermelha (erro) por alguns segundos."""
        cor = ("#D1FAE5", "#0D3B2E") if ok else ("#FEE2E2", "#4C1D24")
        txt = ("#065F46", "#34D399") if ok else ("#991B1B", "#FB7185")
        self.lbl_aviso.configure(
            text=("  ✔  " if ok else "  ✖  ") + mensagem,
            fg_color=cor, text_color=txt, height=38,
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

    def _marcar_erro(self, *chaves: str):
        for k in chaves:
            frame = self._campos.get(k)
            if frame is not None:
                frame.configure(border_color="#F43F5E")

    def _limpar_erros(self):
        for frame in self._campos.values():
            try:
                frame.configure(border_color=COR_BORDA)
            except Exception:
                pass

    # ==============================================================
    # 1. CABEÇALHO
    # ==============================================================
    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)

        tit_box = ctk.CTkFrame(header, fg_color="transparent")
        tit_box.grid(row=0, column=0, sticky="w")

        tit_row = ctk.CTkFrame(tit_box, fg_color="transparent")
        tit_row.pack(anchor="w")

        # Ícone de documento
        ic_box = ctk.CTkFrame(tit_row, width=32, height=32, corner_radius=8, fg_color="#182A3A")
        ic_box.pack(side="left", padx=(0, 10))
        ic_box.pack_propagate(False)
        ctk.CTkLabel(ic_box, text="📄", font=fonte(14)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(tit_row, text="Lançamentos", font=fonte(22, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        ctk.CTkLabel(
            tit_box,
            text="Registre e acompanhe todas as suas receitas, despesas e mantenha suas finanças em dia.",
            font=fonte(12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Seletor de mês
        nav_mes = ctk.CTkFrame(header, fg_color=COR_CARD, corner_radius=10, border_width=1, border_color=COR_BORDA)
        nav_mes.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(nav_mes, text="📅", font=fonte(12)).pack(side="left", padx=(10, 4))

        # Histórico completo, sem seletor de meses fictício/inativo.
        ctk.CTkLabel(nav_mes, text="Histórico completo", font=fonte(12),
                     text_color=COR_TEXTO_SECUNDARIO).pack(side="left", padx=(2, 10), pady=8)
        ctk.CTkButton(
            nav_mes, text="↻", width=32, height=28, corner_radius=6,
            fg_color="transparent", hover_color=COR_CARD_INTERNO,
            text_color=COR_TEXTO_SECUNDARIO, command=self.atualizar_dados
        ).pack(side="left", padx=(0, 8), pady=3)

    # ==============================================================
    # 2. MÉTRICAS (3 CARDS COM MINI GRÁFICOS)
    # ==============================================================
    def _build_metricas(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 14))
        grid.grid_columnconfigure((0, 1, 2), weight=1)

        rec_tot = sum(i["valor"] for i in self._itens if i["tipo"] == "Receita")
        desp_tot = sum(i["valor"] for i in self._itens if i["tipo"] == "Despesa")
        saldo_tot = rec_tot - desp_tot

        cards_data = [
            ("↑", "#0D2E2B", "#00D084", "Total de Receitas", f"R$ {_fmt_brl(rec_tot)}", "Registros da conta", "barras", "#00D084"),
            ("↓", "#2E151B", "#F43F5E", "Total de Despesas", f"R$ {_fmt_brl(desp_tot)}", "Registros da conta", "barras", "#F43F5E"),
            ("💳", "#122538", "#38BDF8", "Saldo Líquido", f"R$ {_fmt_brl(saldo_tot)}", "Receitas menos despesas", "linha", "#38BDF8"),
        ]

        for idx, (ic, bg_ic, cor_ic, tit, val, foot, tipo_spark, cor_spark) in enumerate(cards_data):
            card = ctk.CTkFrame(grid, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
            card.grid(row=0, column=idx, padx=4, sticky="nsew")

            row_top = ctk.CTkFrame(card, fg_color="transparent")
            row_top.pack(fill="x", padx=14, pady=(12, 4))

            # Ícone
            ic_box = ctk.CTkFrame(row_top, width=34, height=34, corner_radius=17, fg_color=bg_ic)
            ic_box.pack(side="left", padx=(0, 10))
            ic_box.pack_propagate(False)
            ctk.CTkLabel(ic_box, text=ic, font=fonte(14, "bold"), text_color=cor_ic).place(relx=0.5, rely=0.5, anchor="center")

            # Título e Valor
            t_box = ctk.CTkFrame(row_top, fg_color="transparent")
            t_box.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(t_box, text=tit, font=fonte(11), text_color=COR_TEXTO_SECUNDARIO, anchor="w").pack(anchor="w")
            ctk.CTkLabel(t_box, text=val, font=fonte(18, "bold"), text_color=cor_ic, anchor="w").pack(anchor="w")

            # Não desenhar sparklines inventadas: os totais vêm do MySQL.

            # Footer
            ctk.CTkLabel(
                card,
                text=foot,
                font=fonte(10),
                text_color=cor_ic,
                anchor="w",
            ).pack(anchor="w", padx=14, pady=(2, 12))

    # ==============================================================
    # 3. FORMULÁRIO (COLUNA ESQUERDA)
    # ==============================================================
    def _build_formulario(self, parent):
        self._campos = {}

        card = ctk.CTkFrame(
            parent,
            fg_color=COR_CARD,
            corner_radius=14,
            border_width=1,
            border_color=COR_BORDA,
        )
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Topo
        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 12))

        ic_box = ctk.CTkFrame(topo, width=32, height=32, corner_radius=16, fg_color="#0D2E2B")
        ic_box.pack(side="left", padx=(0, 10))
        ic_box.pack_propagate(False)
        ctk.CTkLabel(ic_box, text="＋", font=fonte(14, "bold"), text_color="#00D084").place(relx=0.5, rely=0.5, anchor="center")

        tit_box = ctk.CTkFrame(topo, fg_color="transparent")
        tit_box.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(tit_box, text="Novo Lançamento", font=fonte(14, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(tit_box, text="Registre uma receita ou despesa de forma rápida e organizada.", font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        # Pílulas Seletoras: [- Despesa] e [+ Receita]
        pilula_box = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=10, height=42)
        pilula_box.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_tipo_despesa = ctk.CTkButton(
            pilula_box,
            text="⛔  Despesa",
            height=34,
            corner_radius=8,
            fg_color="#F43F5E" if self.tipo_selecionado == "Despesa" else "transparent",
            text_color="#FFFFFF" if self.tipo_selecionado == "Despesa" else COR_TEXTO_SECUNDARIO,
            hover_color="#E11D48",
            font=fonte(12, "bold"),
            command=lambda: self._set_tipo("Despesa"),
        )
        self.btn_tipo_despesa.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        self.btn_tipo_receita = ctk.CTkButton(
            pilula_box,
            text="＋  Receita",
            height=34,
            corner_radius=8,
            fg_color="#00D084" if self.tipo_selecionado == "Receita" else "transparent",
            text_color="#0B131B" if self.tipo_selecionado == "Receita" else COR_TEXTO_SECUNDARIO,
            hover_color="#00B875",
            font=fonte(12, "bold"),
            command=lambda: self._set_tipo("Receita"),
        )
        self.btn_tipo_receita.pack(side="right", fill="both", expand=True, padx=4, pady=4)

        # Campo: Valor (R$) *
        ctk.CTkLabel(card, text="Valor (R$) *", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_val = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=38)
        f_val.pack(fill="x", padx=16, pady=(0, 12))
        f_val.pack_propagate(False)
        self._campos["valor"] = f_val

        ctk.CTkLabel(f_val, text="💰", font=fonte(13)).pack(side="left", padx=10)
        self.entry_valor = ctk.CTkEntry(
            f_val, placeholder_text="0,00", font=fonte(13, "bold"), fg_color="transparent", border_width=0, text_color=COR_TEXTO_PRINCIPAL
        )
        self.entry_valor.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Campo: Descrição *
        ctk.CTkLabel(card, text="Descrição *", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(anchor="w", padx=16, pady=(0, 4))
        f_desc = ctk.CTkFrame(card, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=38)
        f_desc.pack(fill="x", padx=16, pady=(0, 12))
        f_desc.pack_propagate(False)
        self._campos["desc"] = f_desc

        ctk.CTkLabel(f_desc, text="📄", font=fonte(13)).pack(side="left", padx=10)
        self.entry_desc = ctk.CTkEntry(
            f_desc, placeholder_text="Ex: Aluguel, Supermercado, Conta de Luz...", font=fonte(11), fg_color="transparent", border_width=0, text_color=COR_TEXTO_PRINCIPAL
        )
        self.entry_desc.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Linha dupla: Categoria e Beneficiário
        grid_campos = ctk.CTkFrame(card, fg_color="transparent")
        grid_campos.pack(fill="x", padx=16, pady=(0, 12))
        grid_campos.grid_columnconfigure((0, 1), weight=1)

        # Categoria
        ctk.CTkLabel(grid_campos, text="Categoria *", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=0, sticky="w", pady=(0, 4))
        f_cat = ctk.CTkFrame(grid_campos, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=38)
        f_cat.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        f_cat.pack_propagate(False)

        ctk.CTkLabel(f_cat, text="🍴", font=fonte(12)).pack(side="left", padx=(8, 4))

        cats = []
        if self.cat_dao:
            try:
                for c in self.cat_dao.listar_todas():
                    cats.append(c["nome"] if isinstance(c, dict) else getattr(c, "nome", str(c)))
            except Exception:
                pass
        if not cats:
            cats = ["Alimentação", "Moradia", "Transporte", "Saúde", "Lazer", "Educação", "Salário", "Investimentos", "Outros"]

        self.combo_categoria = ctk.CTkOptionMenu(
            f_cat,
            values=cats,
            height=30,
            fg_color=COR_CARD_INTERNO,
            button_color=COR_CARD,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(11),
        )
        self.combo_categoria.set(cats[0])
        self.combo_categoria.pack(side="left", fill="both", expand=True)

        # Beneficiário / Fornecedor
        ctk.CTkLabel(grid_campos, text="Beneficiário / Fornecedor", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=1, sticky="w", pady=(0, 4))
        f_ter = ctk.CTkFrame(grid_campos, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=38)
        f_ter.grid(row=1, column=1, sticky="ew", padx=(6, 0))
        f_ter.pack_propagate(False)

        ctk.CTkLabel(f_ter, text="👤", font=fonte(12)).pack(side="left", padx=(8, 4))
        self.entry_beneficiario = ctk.CTkEntry(
            f_ter, placeholder_text="Ex: Pão de Açúcar", font=fonte(11), fg_color="transparent", border_width=0, text_color=COR_TEXTO_PRINCIPAL
        )
        self.entry_beneficiario.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Linha dupla: Data e Status
        grid_campos2 = ctk.CTkFrame(card, fg_color="transparent")
        grid_campos2.pack(fill="x", padx=16, pady=(0, 6))
        grid_campos2.grid_columnconfigure((0, 1), weight=1)

        # Data
        ctk.CTkLabel(grid_campos2, text="Data *", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=0, sticky="w", pady=(0, 4))
        f_dat = ctk.CTkFrame(grid_campos2, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=38)
        f_dat.grid(row=1, column=0, sticky="ew", padx=(0, 6))
        f_dat.pack_propagate(False)
        self._campos["data"] = f_dat

        ctk.CTkLabel(f_dat, text="📅", font=fonte(12)).pack(side="left", padx=(8, 4))
        self.entry_data = ctk.CTkEntry(
            f_dat, font=fonte(11), fg_color="transparent", border_width=0, text_color=COR_TEXTO_PRINCIPAL
        )
        self.entry_data.insert(0, date.today().strftime("%d/%m/%Y"))
        self.entry_data.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Status
        ctk.CTkLabel(grid_campos2, text="Status do Pagamento *", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).grid(row=0, column=1, sticky="w", pady=(0, 4))
        f_stat = ctk.CTkFrame(grid_campos2, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=38)
        f_stat.grid(row=1, column=1, sticky="ew", padx=(6, 0))
        f_stat.pack_propagate(False)
        self._campos["status"] = f_stat

        ctk.CTkLabel(f_stat, text="💳", font=fonte(12)).pack(side="left", padx=(8, 4))
        status_validos = STATUS_POR_TIPO[self.tipo_selecionado]
        self.combo_status = ctk.CTkOptionMenu(
            f_stat,
            values=status_validos,
            height=30,
            fg_color=COR_CARD_INTERNO,
            button_color=COR_CARD,
            text_color=COR_TEXTO_PRINCIPAL,
            font=fonte(11),
        )
        self.combo_status.set(status_validos[0])
        self.combo_status.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(card, text="ⓘ Formato da data: DD/MM/AAAA", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="w", padx=16, pady=(0, 14))

        # Botões Salvar e Limpar
        botoes_box = ctk.CTkFrame(card, fg_color="transparent")
        botoes_box.pack(fill="x", padx=16, pady=(0, 16))

        cor_btn_salvar = "#F43F5E" if self.tipo_selecionado == "Despesa" else "#00D084"
        self.btn_salvar = ctk.CTkButton(
            botoes_box,
            text="＋  Salvar Lançamento",
            height=40,
            corner_radius=10,
            fg_color=cor_btn_salvar,
            hover_color="#E11D48" if self.tipo_selecionado == "Despesa" else "#00B875",
            text_color="#FFFFFF" if self.tipo_selecionado == "Despesa" else "#0B131B",
            font=fonte(12, "bold"),
            command=self._salvar_lancamento,
        )
        self.btn_salvar.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            botoes_box,
            text="🔄  Limpar Campos",
            height=40,
            width=130,
            corner_radius=10,
            fg_color=COR_CARD_INTERNO,
            hover_color="#1E2F40",
            text_color=COR_TEXTO_SECUNDARIO,
            font=fonte(11),
            command=self._limpar_formulario,
        ).pack(side="right")

    def _set_tipo(self, novo_tipo: str):
        self.tipo_selecionado = novo_tipo
        if novo_tipo == "Despesa":
            self.btn_tipo_despesa.configure(fg_color="#F43F5E", text_color="#FFFFFF")
            self.btn_tipo_receita.configure(fg_color="transparent", text_color=COR_TEXTO_SECUNDARIO)
            self.btn_salvar.configure(fg_color="#F43F5E", hover_color="#E11D48", text_color="#FFFFFF")
        else:
            self.btn_tipo_despesa.configure(fg_color="transparent", text_color=COR_TEXTO_SECUNDARIO)
            self.btn_tipo_receita.configure(fg_color="#00D084", text_color="#0B131B")
            self.btn_salvar.configure(fg_color="#00D084", hover_color="#00B875", text_color="#0B131B")

        status_validos = STATUS_POR_TIPO[novo_tipo]
        self.combo_status.configure(values=status_validos)
        self.combo_status.set(status_validos[0])

    def _limpar_formulario(self):
        self.entry_valor.delete(0, "end")
        self.entry_desc.delete(0, "end")
        self.entry_beneficiario.delete(0, "end")
        self.entry_data.delete(0, "end")
        self.entry_data.insert(0, date.today().strftime("%d/%m/%Y"))
        self.combo_status.set(STATUS_POR_TIPO[self.tipo_selecionado][0])
        self._limpar_erros()

    def _salvar_lancamento(self):
        self._limpar_erros()

        tipo = self.tipo_selecionado
        val_txt = self.entry_valor.get().strip()
        desc = self.entry_desc.get().strip()
        data_txt = self.entry_data.get().strip()
        status = self.combo_status.get().strip()
        cat = self.combo_categoria.get().strip() or "Outros"
        beneficiario = self.entry_beneficiario.get().strip()

        # 1) Campos obrigatórios
        faltando = []
        if not val_txt:
            faltando.append(("valor", "Valor"))
        if not desc:
            faltando.append(("desc", "Descrição"))
        if not data_txt:
            faltando.append(("data", "Data"))
        if not status or status not in STATUS_POR_TIPO[tipo]:
            faltando.append(("status", "Status do Pagamento"))

        if faltando:
            self._marcar_erro(*[k for k, _ in faltando])
            nomes = ", ".join(n for _, n in faltando)
            self._notificar(f"Preencha os campos obrigatórios: {nomes}.", ok=False)
            return

        # 2) Valor válido e maior que zero
        try:
            valor = _parse_valor(val_txt)
        except ValueError:
            self._marcar_erro("valor")
            self._notificar("Valor inválido. Digite apenas números, por exemplo 150,00.", ok=False)
            return

        if valor <= 0:
            self._marcar_erro("valor")
            self._notificar("O valor deve ser maior que zero.", ok=False)
            return

        # 3) Data válida
        try:
            d_obj = datetime.strptime(data_txt, "%d/%m/%Y")
        except ValueError:
            self._marcar_erro("data")
            self._notificar("Data inválida. Use o formato DD/MM/AAAA.", ok=False)
            return
        data_sql = d_obj.strftime("%Y-%m-%d")

        # 4) Salvar (LancamentoDAO.inserir recebe os campos separados)
        try:
            self.dao.inserir(
                descricao=desc,
                valor=valor,
                tipo=tipo,
                categoria=cat,
                data=data_sql,
                status=status,
                terceiro_id=self._buscar_terceiro_id(beneficiario),
            )
        except Exception as exc:
            self._notificar(f"Não foi possível salvar o lançamento: {exc}", ok=False)
            return

        # 5) Mostra o novo item na lista (volta para "Todos" e limpa a busca)
        self.filtro_aba = "Todos"
        self.busca_texto = ""
        self._montar_tela()
        self._notificar(f"{tipo} registrada com sucesso!  {desc} · R$ {_fmt_brl(valor)}")

    # ==============================================================
    # 4. HISTÓRICO RECENTE (COLUNA DIREITA)
    # ==============================================================
    def _build_painel_historico(self, parent):
        card = ctk.CTkFrame(
            parent,
            fg_color=COR_CARD,
            corner_radius=14,
            border_width=1,
            border_color=COR_BORDA,
        )
        card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Topo
        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=16, pady=(16, 10))

        ic_box = ctk.CTkFrame(topo, width=32, height=32, corner_radius=16, fg_color="#0D2E2B")
        ic_box.pack(side="left", padx=(0, 10))
        ic_box.pack_propagate(False)
        ctk.CTkLabel(ic_box, text="🕒", font=fonte(13)).place(relx=0.5, rely=0.5, anchor="center")

        tit_box = ctk.CTkFrame(topo, fg_color="transparent")
        tit_box.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(tit_box, text="Lançamentos Recentes", font=fonte(14, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
        ctk.CTkLabel(tit_box, text="Acompanhe, edite ou filtre seus lançamentos.", font=fonte(10), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        ctk.CTkButton(
            topo, text="Ver todos →", fg_color="transparent", hover_color=COR_CARD_INTERNO, text_color="#00D084", font=fonte(11), width=70
        ).pack(side="right")

        # Barra de Filtros em Abas e Busca
        barra_busca = ctk.CTkFrame(card, fg_color="transparent")
        barra_busca.pack(fill="x", padx=16, pady=(0, 12))
        barra_busca.grid_columnconfigure(1, weight=1)

        # Abas de filtro (contagens calculadas a partir dos lançamentos)
        abas_frame = ctk.CTkFrame(barra_busca, fg_color=COR_CARD_INTERNO, corner_radius=8, height=34)
        abas_frame.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.botoes_abas = {}
        for nome in ("Todos", "Receitas", "Despesas"):
            b = ctk.CTkButton(
                abas_frame,
                text=nome,
                height=26,
                corner_radius=6,
                fg_color="transparent",
                font=fonte(10),
                command=lambda a=nome: self._filtrar_aba(a),
            )
            b.pack(side="left", padx=2, pady=4)
            self.botoes_abas[nome] = b
        self._atualizar_abas()

        # Campo de busca
        f_busca = ctk.CTkFrame(barra_busca, fg_color=COR_CARD_INTERNO, corner_radius=8, border_width=1, border_color=COR_BORDA, height=34)
        f_busca.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        f_busca.pack_propagate(False)

        ctk.CTkLabel(f_busca, text="🔍", font=fonte(11)).pack(side="left", padx=8)
        self.entry_busca = ctk.CTkEntry(
            f_busca, placeholder_text="Buscar por descrição, categoria...", font=fonte(11), fg_color="transparent", border_width=0, text_color=COR_TEXTO_PRINCIPAL
        )
        self.entry_busca.pack(side="left", fill="both", expand=True)
        if self.busca_texto:
            self.entry_busca.insert(0, self.busca_texto)
        self.entry_busca.bind("<KeyRelease>", self._ao_buscar)

        # Botão de sliders de filtro
        ctk.CTkButton(
            barra_busca, text="🎛️", width=34, height=34, corner_radius=8, fg_color=COR_CARD_INTERNO, hover_color="#1E2F40", text_color=COR_TEXTO_PRINCIPAL
        ).grid(row=0, column=2, sticky="e")

        # Cabeçalho da Tabela
        th = ctk.CTkFrame(card, fg_color="transparent")
        th.pack(fill="x", padx=16, pady=(0, 6))

        ctk.CTkLabel(th, text="Data ↕", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=60, anchor="w").pack(side="left")
        ctk.CTkLabel(th, text="Descrição", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=150, anchor="w").pack(side="left", padx=(10, 0))
        ctk.CTkLabel(th, text="Categoria", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=100, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(th, text="Status", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=80, anchor="w").pack(side="left")
        ctk.CTkLabel(th, text="Ações", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=40, anchor="center").pack(side="right", padx=(4, 6))
        ctk.CTkLabel(th, text="Valor (R$)", font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, anchor="e").pack(side="right", padx=(0, 10))

        # Lista (re-renderizada sem reconstruir a tela inteira)
        self.frame_lista = ctk.CTkFrame(card, fg_color="transparent")
        self.frame_lista.pack(fill="x")
        self._render_lista()

        ctk.CTkLabel(card, text="", height=8).pack()

    # ---------------- abas / busca / lista ----------------
    def _atualizar_abas(self):
        contagem = {
            "Todos": len(self._itens),
            "Receitas": sum(1 for i in self._itens if i["tipo"] == "Receita"),
            "Despesas": sum(1 for i in self._itens if i["tipo"] == "Despesa"),
        }
        for nome, btn in self.botoes_abas.items():
            ativo = nome == self.filtro_aba
            btn.configure(
                text=f"{nome} ({contagem[nome]})",
                fg_color="#00D084" if ativo else "transparent",
                text_color="#0B131B" if ativo else COR_TEXTO_SECUNDARIO,
                font=fonte(10, "bold" if ativo else "normal"),
            )

    def _filtrar_aba(self, aba: str):
        self.filtro_aba = aba
        self._atualizar_abas()
        self._render_lista()

    def _ao_buscar(self, _event=None):
        self.busca_texto = self.entry_busca.get()
        self._render_lista()

    def _itens_filtrados(self) -> List[Dict[str, Any]]:
        itens = self._itens
        if self.filtro_aba == "Receitas":
            itens = [i for i in itens if i["tipo"] == "Receita"]
        elif self.filtro_aba == "Despesas":
            itens = [i for i in itens if i["tipo"] == "Despesa"]

        termo = self.busca_texto.strip().lower()
        if termo:
            itens = [
                i for i in itens
                if any(termo in str(i.get(k, "")).lower() for k in ("descricao", "sub", "categoria", "status"))
            ]
        return itens

    def _render_lista(self):
        if self.frame_lista is None:
            return
        for w in self.frame_lista.winfo_children():
            w.destroy()

        itens = self._itens_filtrados()

        if not itens:
            ctk.CTkLabel(
                self.frame_lista, text="Nenhum lançamento encontrado.",
                font=fonte(11), text_color=COR_TEXTO_MUTED,
            ).pack(pady=24)
            return

        for item in itens[:LIMITE_LINHAS]:
            self._build_linha(item)

        if len(itens) > LIMITE_LINHAS:
            ctk.CTkLabel(
                self.frame_lista,
                text=f"Mostrando os {LIMITE_LINHAS} mais recentes de {len(itens)} lançamentos.",
                font=fonte(9), text_color=COR_TEXTO_MUTED,
            ).pack(pady=(6, 0))

    def _build_linha(self, item: Dict[str, Any]):
        eh_rec = item["tipo"] == "Receita"
        cor_val = "#00D084" if eh_rec else "#F43F5E"
        bg_ic = "#102E24" if eh_rec else "#2E151B"
        sinal = "+ " if eh_rec else "- "

        d = item["data"]
        d_badge = f"{d.day:02d}\n{MESES_ABREV[d.month - 1]}" if d else "--\n---"

        cat = item["categoria"]
        cat_b = f"{ICONES_CATEGORIA.get(cat, '🏷️')} {cat}"

        st = item["status"]
        st_b = f"● {st}"
        st_cor = "#F59E0B" if st == "Pendente" else "#00D084"

        linha = ctk.CTkFrame(self.frame_lista, fg_color=COR_CARD_INTERNO, corner_radius=8, height=48)
        linha.pack(fill="x", padx=16, pady=3)
        linha.pack_propagate(False)

        # Badge Data
        d_box = ctk.CTkFrame(linha, width=32, height=32, corner_radius=6, fg_color="#182A3A")
        d_box.pack(side="left", padx=(8, 8))
        d_box.pack_propagate(False)
        ctk.CTkLabel(d_box, text=d_badge, font=fonte(8, "bold"), text_color="#CBD5E1").place(relx=0.5, rely=0.5, anchor="center")

        # Ícone
        ic_box = ctk.CTkFrame(linha, width=30, height=30, corner_radius=6, fg_color=bg_ic)
        ic_box.pack(side="left", padx=(0, 8))
        ic_box.pack_propagate(False)
        ctk.CTkLabel(ic_box, text=item["icone"], font=fonte(12)).place(relx=0.5, rely=0.5, anchor="center")

        # Título e Subtítulo
        t_box = ctk.CTkFrame(linha, fg_color="transparent", width=140)
        t_box.pack(side="left", fill="y", padx=(0, 8))
        t_box.pack_propagate(False)

        ctk.CTkLabel(t_box, text=item["descricao"][:18], font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w", pady=(6, 0))
        ctk.CTkLabel(t_box, text=str(item["sub"])[:20], font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

        # Badge Categoria
        cat_box = ctk.CTkFrame(linha, fg_color="#182836", corner_radius=6, height=24)
        cat_box.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(cat_box, text=f" {cat_b} ", font=fonte(9), text_color=COR_TEXTO_SECUNDARIO).pack(padx=4, pady=2)

        # Status
        ctk.CTkLabel(linha, text=st_b, font=fonte(10, "bold"), text_color=st_cor, width=70, anchor="w").pack(side="left")

        # Botão Apagar / Excluir
        ctk.CTkButton(
            linha,
            text="🗑️",
            width=28,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#3E1A23",
            text_color="#F43F5E",
            font=fonte(11),
            command=lambda it=item: self._apagar_lancamento(it),
        ).pack(side="right", padx=(4, 6))

        # Valor
        ctk.CTkLabel(
            linha, text=f"{sinal}R$ {_fmt_brl(item['valor'])}",
            font=fonte(11, "bold"), text_color=cor_val, anchor="e",
        ).pack(side="right", padx=6)

    # ==============================================================
    # EXCLUSÃO
    # ==============================================================
    def _apagar_lancamento(self, item: Dict[str, Any]):
        """Exclui exclusivamente lançamentos que existem no MySQL."""
        descricao = item.get("descricao", "")
        if not messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente apagar o lançamento '{descricao}'?"):
            return

        if item.get("id") is not None:
            try:
                self.dao.excluir(item["id"])
            except Exception as exc:
                self._notificar(f"Não foi possível excluir: {exc}", ok=False)
                return
        else:
            self._notificar("Lançamento sem identificador no banco; exclusão cancelada.", ok=False)
            return

        self._montar_tela()
        self._notificar("Lançamento excluído.")