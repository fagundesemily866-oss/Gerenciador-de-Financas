"""
View do Assistente de IA — Redesign Fiel à Referência (02_assistente_ia.png)
=============================================================================

Interface moderna de consultoria financeira com IA:
1. Topo: Busca rápida, notificações e status.
2. Cabeçalho com banner de IA e ações rápidas clicáveis.
3. Coluna Principal de Chat com balões estilizados, sugestões rápidas em cards,
   respostas analíticas com barras e input moderno (clip, mic, send).
4. Coluna Lateral Direita com Resumo do Mês, Alertas e Ações Sugeridas.
"""
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List
import customtkinter as ctk

from services.ai_service import AIService
from dao.lancamento_dao import LancamentoDAO
from dao.categoria_dao import CategoriaDAO
from dao.meta_dao import MetaDAO
from views.notificacao_toast import GerenciadorNotificacoes
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_ACENTO_ROXO, COR_ACENTO_ROXO_HOVER,
    COR_SUCESSO, COR_ALERTA, COR_AVISO, COR_INFO,
    COR_BOTAO_SECUNDARIO, COR_PROGRESSO, COR_PROGRESSO_BG,
    fonte, fonte_titulo, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
)


class AssistenteIAView(ctk.CTkFrame):
    """Tela do Assistente IA redesenhada conforme a imagem 02_assistente_ia.png."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.ai_service = AIService()
        self.dao_lancamento = LancamentoDAO()
        self.dao_categoria = CategoriaDAO()
        self.dao_meta = MetaDAO()
        self._aguardando_resposta = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._montar_tela()

    def _navegar_para(self, chave: str):
        curr = self.master
        while curr:
            if hasattr(curr, "selecionar"):
                curr.selecionar(chave)
                break
            curr = getattr(curr, "master", None)

    def atualizar_dados(self):
        # Atualiza métricas na barra lateral
        pass

    def _montar_tela(self):
        for w in self.winfo_children():
            w.destroy()

        main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_scroll.grid(row=0, column=0, sticky="nsew")
        main_scroll.grid_columnconfigure(0, weight=1)

        # 1. TOP BAR GLOBAL
        self._build_top_bar(main_scroll)

        # 2. CABEÇALHO + BANNER IA
        self._build_header_ia(main_scroll)

        # 3. AÇÕES RÁPIDAS
        self._build_acoes_rapidas(main_scroll)

        # 4. GRID DE 2 COLUNAS: CHAT (ESQ) + INSIGHTS & ALERTAS (DIR)
        corpo = ctk.CTkFrame(main_scroll, fg_color="transparent")
        corpo.pack(fill="both", expand=True, pady=(0, 10))
        corpo.grid_columnconfigure(0, weight=7)
        corpo.grid_columnconfigure(1, weight=3)

        self._build_coluna_chat(corpo)
        self._build_coluna_lateral(corpo)

    # ==============================================================
    # 1. TOP BAR GLOBAL
    # ==============================================================
    def _build_top_bar(self, parent):
        top_bar = ctk.CTkFrame(parent, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))
        top_bar.grid_columnconfigure(0, weight=1)

        # Busca rápida
        busca_box = ctk.CTkFrame(
            top_bar,
            fg_color=COR_CARD,
            corner_radius=10,
            border_width=1,
            border_color=COR_BORDA,
            height=38,
        )
        busca_box.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        busca_box.pack_propagate(False)

        ctk.CTkLabel(busca_box, text="🔍", font=fonte(12)).pack(side="left", padx=(12, 6))

        entry_busca = ctk.CTkEntry(
            busca_box,
            placeholder_text="Buscar transações, metas, categorias...",
            fg_color="transparent",
            border_width=0,
            font=fonte(11),
            text_color=COR_TEXTO_PRINCIPAL,
        )
        entry_busca.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Ações do topo direito: sino de notificação e avatar
        acoes_dir = ctk.CTkFrame(top_bar, fg_color="transparent")
        acoes_dir.grid(row=0, column=1, sticky="e")

        btn_sino = ctk.CTkButton(
            acoes_dir,
            text="🔔",
            width=36,
            height=36,
            corner_radius=18,
            fg_color=COR_CARD,
            hover_color=COR_CARD_INTERNO,
            font=fonte(13),
        )
        btn_sino.pack(side="left", padx=(0, 10))

        btn_user_top = ctk.CTkFrame(
            acoes_dir,
            fg_color=COR_CARD,
            corner_radius=18,
            border_width=1,
            border_color=COR_BORDA,
            height=36,
        )
        btn_user_top.pack(side="left")

        ctk.CTkLabel(
            btn_user_top,
            text=" UD ",
            font=fonte(10, "bold"),
            text_color="#00D084",
        ).pack(side="left", padx=(8, 4), pady=4)

        ctk.CTkLabel(
            btn_user_top,
            text="Usuário Demo",
            font=fonte(11, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
        ).pack(side="left", padx=(0, 8), pady=4)

    # ==============================================================
    # 2. CABEÇALHO + BANNER IA
    # ==============================================================
    def _build_header_ia(self, parent):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        header.grid_columnconfigure(0, weight=1)

        # Esquerda
        tit_box = ctk.CTkFrame(header, fg_color="transparent")
        tit_box.grid(row=0, column=0, sticky="w")

        tit_row = ctk.CTkFrame(tit_box, fg_color="transparent")
        tit_row.pack(anchor="w")

        ctk.CTkLabel(tit_row, text="✨", font=fonte(22), text_color="#A855F7").pack(side="left", padx=(0, 6))
        ctk.CTkLabel(tit_row, text="Assistente IA", font=fonte(22, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")

        ctk.CTkLabel(
            tit_box,
            text="Seu consultor financeiro pessoal, sempre ao seu lado.",
            font=fonte(12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Direita: Banner informativo lilás
        banner = ctk.CTkFrame(
            header,
            fg_color=("#F3E8FF", "#1C142E"),
            corner_radius=12,
            border_width=1,
            border_color=("#E9D5FF", "#3B2562"),
        )
        banner.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(banner, text="🤖", font=fonte(18)).pack(side="left", padx=(12, 8), pady=10)
        ctk.CTkLabel(
            banner,
            text="Tire dúvidas, receba insights e tome\nmelhores decisões com base nos seus dados.",
            font=fonte(10),
            text_color=("#6B21A8", "#D8B4FE"),
            justify="left",
            anchor="w",
        ).pack(side="left", padx=(0, 14), pady=8)

    # ==============================================================
    # 3. AÇÕES RÁPIDAS
    # ==============================================================
    def _build_acoes_rapidas(self, parent):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(fill="x", pady=(0, 14))
        for c in range(4):
            box.grid_columnconfigure(c, weight=1)

        acoes = [
            ("📊", "Analisar despesas", "Entenda seus gastos", "lancamento"),
            ("🎯", "Criar meta", "Defina um objetivo", "meta"),
            ("📄", "Resumo mensal", "Veja um panorama", "relatorio"),
            ("📈", "Simular cenário", "Projete o futuro", "simulador"),
        ]

        for i, (ic, tit, sub, rota) in enumerate(acoes):
            card = ctk.CTkFrame(
                box,
                fg_color=COR_CARD,
                corner_radius=10,
                border_width=1,
                border_color=COR_BORDA,
                height=56,
                cursor="hand2",
            )
            card.grid(row=0, column=i, padx=3, sticky="nsew")

            inner = ctk.CTkFrame(card, fg_color="transparent", cursor="hand2")
            inner.pack(fill="both", expand=True, padx=10, pady=6)

            ic_box = ctk.CTkFrame(inner, width=32, height=32, corner_radius=8, fg_color="#182A3A", cursor="hand2")
            ic_box.pack(side="left", padx=(0, 8))
            ic_box.pack_propagate(False)

            lbl_i = ctk.CTkLabel(ic_box, text=ic, font=fonte(13), cursor="hand2")
            lbl_i.place(relx=0.5, rely=0.5, anchor="center")

            txt_box = ctk.CTkFrame(inner, fg_color="transparent", cursor="hand2")
            txt_box.pack(side="left", fill="both", expand=True)

            lbl_t = ctk.CTkLabel(txt_box, text=tit, font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w", cursor="hand2")
            lbl_t.pack(anchor="w")
            lbl_s = ctk.CTkLabel(txt_box, text=sub, font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w", cursor="hand2")
            lbl_s.pack(anchor="w")

            def _bind_rota(w_list, r=rota):
                for w in w_list:
                    w.bind("<Button-1>", lambda e, target=r: self._navegar_para(target))

            _bind_rota([card, inner, ic_box, lbl_i, txt_box, lbl_t, lbl_s])

    # ==============================================================
    # 4. CHAT (COLUNA ESQUERDA)
    # ==============================================================
    def _build_coluna_chat(self, parent):
        container = ctk.CTkFrame(
            parent,
            fg_color=COR_CARD,
            corner_radius=14,
            border_width=1,
            border_color=COR_BORDA,
        )
        container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Área de mensagens rolável
        self.chat_scroll = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            height=460,
        )
        self.chat_scroll.pack(fill="both", expand=True, padx=14, pady=14)
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        # Montar conversa demonstrativa inicial
        self._carregar_mensagens_iniciais()

        # Barra inferior de Input do Chat
        input_container = ctk.CTkFrame(
            container,
            fg_color=COR_CARD_INTERNO,
            corner_radius=12,
            border_width=1,
            border_color=COR_BORDA,
            height=54,
        )
        input_container.pack(fill="x", padx=14, pady=(0, 14))
        input_container.pack_propagate(False)

        # Botão Clip
        ctk.CTkLabel(input_container, text="📎", font=fonte(15), text_color=COR_TEXTO_MUTED).pack(side="left", padx=(12, 6))

        # Campo de entrada
        self.entry_msg = ctk.CTkEntry(
            input_container,
            placeholder_text="Digite sua mensagem...",
            fg_color="transparent",
            border_width=0,
            font=fonte(12),
            text_color=COR_TEXTO_PRINCIPAL,
        )
        self.entry_msg.pack(side="left", fill="both", expand=True, padx=4)
        self.entry_msg.bind("<Return>", lambda e: self._enviar_mensagem())

        ctk.CTkLabel(input_container, text="Enter para enviar", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(side="left", padx=8)

        # Botão Microfone
        ctk.CTkLabel(input_container, text="🎙️", font=fonte(14), text_color=COR_TEXTO_MUTED).pack(side="left", padx=6)

        # Botão Enviar Lilás
        self.btn_enviar = ctk.CTkButton(
            input_container,
            text="➤",
            width=38,
            height=34,
            corner_radius=8,
            fg_color=COR_ACENTO_ROXO,
            hover_color=COR_ACENTO_ROXO_HOVER,
            text_color="#FFFFFF",
            font=fonte(14, "bold"),
            command=self._enviar_mensagem,
        )
        self.btn_enviar.pack(side="right", padx=(4, 8), pady=8)

    def _carregar_mensagens_iniciais(self):
        # 1. Boas-vindas IA
        self._add_balao_ia_inicial()

        # 2. Pergunta de exemplo do usuário
        self._add_balao_usuario("Quais foram meus maiores gastos neste mês?")

        # 3. Resposta rica da IA com gráfico horizontal
        self._add_balao_ia_resposta_gastos()

    def _add_balao_ia_inicial(self):
        wrap = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        wrap.pack(fill="x", pady=6)

        # Avatar IA
        av = ctk.CTkFrame(wrap, width=32, height=32, corner_radius=16, fg_color="#3B2562")
        av.pack(side="left", anchor="n", padx=(0, 10))
        av.pack_propagate(False)
        ctk.CTkLabel(av, text="✨", font=fonte(13), text_color="#D8B4FE").place(relx=0.5, rely=0.5, anchor="center")

        balao = ctk.CTkFrame(wrap, fg_color=COR_CARD_INTERNO, corner_radius=12, border_width=1, border_color=COR_BORDA)
        balao.pack(side="left", fill="x", expand=True)

        txt = (
            "Olá, Usuário Demo! 👋\n"
            "Sou o seu Assistente Financeiro com IA. Posso analisar seus dados, responder dúvidas "
            "e ajudar você a tomar melhores decisões com o seu dinheiro.\n"
            "Como posso te ajudar hoje?"
        )
        ctk.CTkLabel(
            balao,
            text=txt,
            font=fonte(11),
            text_color=COR_TEXTO_PRINCIPAL,
            justify="left",
            wraplength=480,
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(10, 4))

        ctk.CTkLabel(balao, text="09:14", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="e", padx=12, pady=(0, 6))

        # Sugestões rápidas
        sug_box = ctk.CTkFrame(balao, fg_color="transparent")
        sug_box.pack(fill="x", padx=10, pady=(0, 10))
        sug_box.grid_columnconfigure((0, 1), weight=1)

        perguntas = [
            "Quais foram meus maiores gastos neste mês?",
            "Estou dentro do meu orçamento?",
            "Como posso economizar mais?",
            "Qual a projeção do meu patrimônio em 12 meses?",
        ]
        for idx, p in enumerate(perguntas):
            r, c = idx // 2, idx % 2
            b = ctk.CTkButton(
                sug_box,
                text=f"{p}  ↗",
                fg_color=COR_CARD,
                hover_color="#1F2F40",
                text_color=COR_TEXTO_SECUNDARIO,
                font=fonte(10),
                corner_radius=8,
                border_width=1,
                border_color=COR_BORDA,
                anchor="w",
                command=lambda msg=p: self._usar_sugestao(msg),
            )
            b.grid(row=r, column=c, padx=3, pady=3, sticky="ew")

    def _add_balao_usuario(self, texto: str):
        wrap = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        wrap.pack(fill="x", pady=6)

        # Avatar Usuário à direita
        av = ctk.CTkFrame(wrap, width=32, height=32, corner_radius=16, fg_color="#102F33")
        av.pack(side="right", anchor="n", padx=(10, 0))
        av.pack_propagate(False)
        ctk.CTkLabel(av, text="UD", font=fonte(10, "bold"), text_color="#00D084").place(relx=0.5, rely=0.5, anchor="center")

        balao = ctk.CTkFrame(wrap, fg_color="#1E274A", corner_radius=12, border_width=1, border_color="#2D3B6B")
        balao.pack(side="right")

        ctk.CTkLabel(
            balao,
            text=texto,
            font=fonte(11),
            text_color="#FFFFFF",
            anchor="e",
        ).pack(padx=14, pady=(8, 2))

        ctk.CTkLabel(balao, text=datetime.now().strftime("%H:%M"), font=fonte(9), text_color="#899ECF").pack(anchor="e", padx=14, pady=(0, 6))

    def _add_balao_ia_resposta_gastos(self):
        wrap = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        wrap.pack(fill="x", pady=6)

        av = ctk.CTkFrame(wrap, width=32, height=32, corner_radius=16, fg_color="#3B2562")
        av.pack(side="left", anchor="n", padx=(0, 10))
        av.pack_propagate(False)
        ctk.CTkLabel(av, text="✨", font=fonte(13), text_color="#D8B4FE").place(relx=0.5, rely=0.5, anchor="center")

        balao = ctk.CTkFrame(wrap, fg_color=COR_CARD_INTERNO, corner_radius=12, border_width=1, border_color=COR_BORDA)
        balao.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            balao,
            text="Aqui estão seus maiores gastos em abril de 2026:",
            font=fonte(11, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(10, 6))

        # Tabela com barras
        tabela = ctk.CTkFrame(balao, fg_color="transparent")
        tabela.pack(fill="x", padx=12, pady=(0, 6))

        gastos = [
            ("1", "🏠", "Moradia", "R$ 1.850,00", "32%", 0.32, "#F43F5E"),
            ("2", "🍴", "Alimentação", "R$ 980,00", "17%", 0.17, "#F59E0B"),
            ("3", "🚗", "Transporte", "R$ 620,00", "11%", 0.11, "#EAB308"),
            ("4", "🎮", "Lazer", "R$ 420,00", "7%", 0.07, "#10B981"),
            ("5", "💳", "Assinaturas", "R$ 320,00", "6%", 0.06, "#34D399"),
        ]

        for num, ic, cat, val, pct, p_prog, cor in gastos:
            row = ctk.CTkFrame(tabela, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=num, font=fonte(10, "bold"), text_color=COR_TEXTO_MUTED, width=15).pack(side="left")
            ctk.CTkLabel(row, text=ic, font=fonte(11), width=24).pack(side="left")
            ctk.CTkLabel(row, text=cat, font=fonte(10), text_color=COR_TEXTO_PRINCIPAL, width=90, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=val, font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL, width=80, anchor="e").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=pct, font=fonte(9), text_color=COR_TEXTO_MUTED, width=32, anchor="e").pack(side="left", padx=4)

            # Barra
            prog = ctk.CTkProgressBar(
                row,
                height=6,
                corner_radius=3,
                progress_color=cor,
                fg_color="#1C2F3F",
                width=110,
            )
            prog.set(p_prog)
            prog.pack(side="left", padx=8)

        ctk.CTkLabel(
            balao,
            text="Esses 5 itens representam 73% dos seus gastos totais de abril (R$ 4.190,00).",
            font=fonte(10),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(4, 4))

        ctk.CTkLabel(balao, text="09:15", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="e", padx=12, pady=(0, 6))

    def _usar_sugestao(self, pergunta: str):
        self.entry_msg.delete(0, "end")
        self.entry_msg.insert(0, pergunta)
        self._enviar_mensagem()

    def _enviar_mensagem(self):
        msg = self.entry_msg.get().strip()
        if not msg or self._aguardando_resposta:
            return

        self.entry_msg.delete(0, "end")
        self._add_balao_usuario(msg)

        self._aguardando_resposta = True
        self.btn_enviar.configure(state="disabled", text="⏳")

        threading.Thread(target=self._processar_resposta_ia, args=(msg,), daemon=True).start()

    def _processar_resposta_ia(self, prompt: str):
        resp = self.ai_service.enviar_pergunta(prompt)
        self.after(0, self._receber_resposta_ia, resp)

    def _receber_resposta_ia(self, resposta: str):
        self._aguardando_resposta = False
        self.btn_enviar.configure(state="normal", text="➤")

        wrap = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        wrap.pack(fill="x", pady=6)

        av = ctk.CTkFrame(wrap, width=32, height=32, corner_radius=16, fg_color="#3B2562")
        av.pack(side="left", anchor="n", padx=(0, 10))
        av.pack_propagate(False)
        ctk.CTkLabel(av, text="✨", font=fonte(13), text_color="#D8B4FE").place(relx=0.5, rely=0.5, anchor="center")

        balao = ctk.CTkFrame(wrap, fg_color=COR_CARD_INTERNO, corner_radius=12, border_width=1, border_color=COR_BORDA)
        balao.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            balao,
            text=resposta,
            font=fonte(11),
            text_color=COR_TEXTO_PRINCIPAL,
            justify="left",
            wraplength=480,
            anchor="w",
        ).pack(anchor="w", padx=12, pady=(10, 4))

        ctk.CTkLabel(balao, text=datetime.now().strftime("%H:%M"), font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="e", padx=12, pady=(0, 6))

    # ==============================================================
    # 5. SIDEBAR DE INSIGHTS & ALERTAS (COLUNA DIREITA)
    # ==============================================================
    def _build_coluna_lateral(self, parent):
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=1, sticky="nsew")

        # 5.1 Card Resumo do Mês
        self._build_card_resumo_mes(col)

        # 5.2 Card Alertas
        self._build_card_alertas(col)

        # 5.3 Card Ações Sugeridas
        self._build_card_acoes_sugeridas(col)

    def _build_card_resumo_mes(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card.pack(fill="x", pady=(0, 10))

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(topo, text="📅  Resumo do mês", font=fonte(12, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")
        ctk.CTkLabel(topo, text="Abril de 2026", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(side="right")

        # Linhas de valores
        linhas = [
            ("↑", "Receitas", "R$ 7.200,00", "#00D084"),
            ("↓", "Despesas", "R$ 4.190,00", "#F43F5E"),
        ]
        for ic, lbl, val, cor in linhas:
            r = ctk.CTkFrame(card, fg_color="transparent")
            r.pack(fill="x", padx=12, pady=2)
            ctk.CTkLabel(r, text=f"{ic}  {lbl}", font=fonte(11), text_color=COR_TEXTO_SECUNDARIO).pack(side="left")
            ctk.CTkLabel(r, text=val, font=fonte(11, "bold"), text_color=cor).pack(side="right")

        # Saldo
        r_saldo = ctk.CTkFrame(card, fg_color="transparent")
        r_saldo.pack(fill="x", padx=12, pady=(6, 4))
        ctk.CTkLabel(r_saldo, text="Saldo do mês", font=fonte(11, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")
        ctk.CTkLabel(r_saldo, text="R$ 3.010,00", font=fonte(12, "bold"), text_color="#00D084").pack(side="right")

        # Execução do orçamento
        r_prog = ctk.CTkFrame(card, fg_color="transparent")
        r_prog.pack(fill="x", padx=12, pady=(4, 10))

        top_p = ctk.CTkFrame(r_prog, fg_color="transparent")
        top_p.pack(fill="x", pady=(0, 2))
        ctk.CTkLabel(top_p, text="Execução do orçamento", font=fonte(10), text_color=COR_TEXTO_MUTED).pack(side="left")
        ctk.CTkLabel(top_p, text="58%", font=fonte(10, "bold"), text_color="#00D084").pack(side="right")

        prog = ctk.CTkProgressBar(r_prog, height=6, corner_radius=3, progress_color="#00D084", fg_color="#1C2F3F")
        prog.set(0.58)
        prog.pack(fill="x")

        ctk.CTkLabel(r_prog, text="R$ 4.190,00 de R$ 7.200,00", font=fonte(9), text_color=COR_TEXTO_MUTED).pack(anchor="w", pady=(2, 0))

    def _build_card_alertas(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card.pack(fill="x", pady=(0, 10))

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(topo, text="🔔  Alertas", font=fonte(12, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")
        ctk.CTkButton(
            topo,
            text="Ver todos",
            fg_color="transparent",
            text_color="#8B5CF6",
            font=fonte(10),
            width=50,
            hover_color=COR_CARD_INTERNO,
        ).pack(side="right")

        alertas = [
            ("📈", "#2E151B", "Gastos com Lazer", "12% acima da sua média"),
            ("💳", "#291E10", "Assinaturas em alta", "+28% em relação ao mês anterior"),
            ("ℹ️", "#122538", "Boa evolução nas metas!", "Você já alcançou 40% da meta de Viagem"),
        ]

        for ic, bg_ic, tit, desc in alertas:
            b_item = ctk.CTkFrame(
                card,
                fg_color=COR_CARD_INTERNO,
                corner_radius=8,
                height=44,
                cursor="hand2",
            )
            b_item.pack(fill="x", padx=8, pady=2)

            in_item = ctk.CTkFrame(b_item, fg_color="transparent", cursor="hand2")
            in_item.pack(fill="both", expand=True, padx=4, pady=3)

            ic_b = ctk.CTkFrame(in_item, width=28, height=28, corner_radius=6, fg_color=bg_ic, cursor="hand2")
            ic_b.pack(side="left", padx=(0, 8))
            ic_b.pack_propagate(False)
            ctk.CTkLabel(ic_b, text=ic, font=fonte(10)).place(relx=0.5, rely=0.5, anchor="center")

            tx = ctk.CTkFrame(in_item, fg_color="transparent", cursor="hand2")
            tx.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(tx, text=tit, font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
            ctk.CTkLabel(tx, text=desc, font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w").pack(anchor="w")

            ctk.CTkLabel(in_item, text="›", font=fonte(14), text_color=COR_TEXTO_MUTED).pack(side="right")

    def _build_card_acoes_sugeridas(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        card.pack(fill="x")

        topo = ctk.CTkFrame(card, fg_color="transparent")
        topo.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(topo, text="✨  Ações sugeridas", font=fonte(12, "bold"), text_color=COR_TEXTO_PRINCIPAL).pack(side="left")
        ctk.CTkButton(
            topo,
            text="Ver todas",
            fg_color="transparent",
            text_color="#8B5CF6",
            font=fonte(10),
            width=50,
            hover_color=COR_CARD_INTERNO,
        ).pack(side="right")

        acoes = [
            ("🐷", "#1C142E", "Criar uma reserva de emergência", "Com base no seu perfil, o ideal é 6 meses das suas despesas."),
            ("🎯", "#0D2E2B", "Revisar seus gastos com assinaturas", "Você pode economizar até R$ 120,00/mês."),
            ("📈", "#122538", "Simular cenário de investimento", "Veja quanto pode acumular em 2 anos."),
        ]

        for ic, bg_ic, tit, desc in acoes:
            b_item = ctk.CTkFrame(
                card,
                fg_color=COR_CARD_INTERNO,
                corner_radius=8,
                height=48,
                cursor="hand2",
            )
            b_item.pack(fill="x", padx=8, pady=2)

            in_item = ctk.CTkFrame(b_item, fg_color="transparent", cursor="hand2")
            in_item.pack(fill="both", expand=True, padx=4, pady=3)

            ic_b = ctk.CTkFrame(in_item, width=28, height=28, corner_radius=6, fg_color=bg_ic, cursor="hand2")
            ic_b.pack(side="left", padx=(0, 8))
            ic_b.pack_propagate(False)
            ctk.CTkLabel(ic_b, text=ic, font=fonte(11)).place(relx=0.5, rely=0.5, anchor="center")

            tx = ctk.CTkFrame(in_item, fg_color="transparent", cursor="hand2")
            tx.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(tx, text=tit, font=fonte(10, "bold"), text_color=COR_TEXTO_PRINCIPAL, anchor="w").pack(anchor="w")
            ctk.CTkLabel(tx, text=desc, font=fonte(9), text_color=COR_TEXTO_MUTED, anchor="w", wraplength=190, justify="left").pack(anchor="w")

            ctk.CTkLabel(in_item, text="›", font=fonte(14), text_color=COR_TEXTO_MUTED).pack(side="right")
