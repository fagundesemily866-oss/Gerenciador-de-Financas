"""Assistente IA: chat amplo, legível e exclusivamente com dados da conta logada."""
import queue
import threading
from datetime import date, datetime

import customtkinter as ctk

from dao.lancamento_dao import LancamentoDAO
from dao.usuario_dao import UsuarioDAO
from services.sessao import Sessao
from services.visao_financeira import resumo, dinheiro
from views.tema import fonte

BG = '#0B131B'
CARD = '#101E2A'
INNER = '#172837'
BORDER = '#263D50'
WHITE = '#F1F5F9'
MUTED = '#AFC0D0'
GREEN = '#00D084'
PURPLE = '#A78BFA'
RED = '#FB7185'


class AssistenteIAView(ctk.CTkFrame):
    """Conversa ocupando o espaço principal; barra de envio sempre visível."""

    def __init__(self, parent):
        super().__init__(parent, fg_color='transparent')
        self.dao = LancamentoDAO()
        self.usuario_id = Sessao.usuario_id()
        self.nome_usuario = self._buscar_nome()
        self.mensagens = []
        self._aguardando_resposta = False
        self._fila = queue.Queue()
        self._montar_tela()
        self._boas_vindas()

    def _buscar_nome(self):
        if self.usuario_id is None:
            return 'Usuário'
        usuario = UsuarioDAO().buscar_por_id(self.usuario_id)
        return (usuario or {}).get('nome', 'Usuário').split(' ')[0]

    def _navegar_para(self, chave):
        atual = self.master
        while atual is not None:
            if hasattr(atual, 'selecionar'):
                atual.selecionar(chave)
                return
            atual = getattr(atual, 'master', None)

    def atualizar_dados(self):
        """Atualiza somente os valores do resumo, sem apagar a conversa."""
        r = resumo(self.dao.listar_todos())
        self.lbl_receitas.configure(text=dinheiro(r['receitas']))
        self.lbl_despesas.configure(text=dinheiro(r['despesas']))
        self.lbl_saldo.configure(text=dinheiro(r['saldo']))

    def _label(self, parent, texto, tamanho=13, cor=WHITE, negrito=False, **kwargs):
        return ctk.CTkLabel(parent, text=texto, font=fonte(tamanho, 'bold' if negrito else 'normal'),
                            text_color=cor, **kwargs)

    def _montar_tela(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        header = ctk.CTkFrame(self, fg_color='transparent')
        header.grid(row=0, column=0, sticky='ew', padx=8, pady=(4, 12))
        self._label(header, '✦  Assistente IA', 22, WHITE, True).pack(anchor='w')
        self._label(header, 'Converse sobre suas finanças. Os valores abaixo vêm da sua conta.', 12, MUTED).pack(anchor='w', pady=(2, 0))

        topo = ctk.CTkFrame(self, fg_color='transparent')
        topo.grid(row=1, column=0, sticky='ew', padx=3, pady=(0, 12))
        for idx in range(3):
            topo.grid_columnconfigure(idx, weight=1, uniform='metric')
        r = resumo(self.dao.listar_todos())
        for idx, (titulo, chave, cor) in enumerate((('↑ Receitas do mês', 'receitas', GREEN),
                                                     ('↓ Despesas do mês', 'despesas', RED),
                                                     ('Saldo do mês', 'saldo', '#60A5FA'))):
            box = ctk.CTkFrame(topo, fg_color=CARD, corner_radius=12, border_width=1, border_color=BORDER)
            box.grid(row=0, column=idx, sticky='nsew', padx=5)
            self._label(box, titulo, 12, MUTED).pack(anchor='w', padx=14, pady=(9, 2))
            lbl = self._label(box, dinheiro(r[chave]), 18, cor, True)
            lbl.pack(anchor='w', padx=14, pady=(0, 11))
            setattr(self, f'lbl_{chave}', lbl)

        conversa = ctk.CTkFrame(self, fg_color=CARD, corner_radius=14, border_width=1, border_color=BORDER)
        conversa.grid(row=2, column=0, sticky='nsew', padx=8)
        conversa.grid_columnconfigure(0, weight=1)
        conversa.grid_rowconfigure(1, weight=1)
        cab = ctk.CTkFrame(conversa, fg_color='transparent')
        cab.grid(row=0, column=0, sticky='ew', padx=17, pady=(12, 8))
        self._label(cab, '✦  Conversa', 15, WHITE, True).pack(side='left')
        self._label(cab, 'Respostas personalizadas', 11, MUTED).pack(side='right')

        self.chat_scroll = ctk.CTkScrollableFrame(conversa, fg_color='transparent')
        self.chat_scroll.grid(row=1, column=0, sticky='nsew', padx=(12, 7), pady=(0, 7))
        self.chat_scroll.grid_columnconfigure(0, weight=1)
        self.chat_scroll.bind('<Configure>', self._ajustar_largura)
        self._largura_chat = 650

        sugestoes = ctk.CTkFrame(conversa, fg_color='transparent')
        sugestoes.grid(row=2, column=0, sticky='ew', padx=13, pady=(0, 8))
        for idx in range(3):
            sugestoes.grid_columnconfigure(idx, weight=1, uniform='suggest')
        for idx, (titulo, func) in enumerate((
            ('Analisar despesas', self._analisar_despesas),
            ('Criar meta', lambda: self._navegar_para('meta')),
            ('Resumo mensal', lambda: self._navegar_para('relatorio')),
        )):
            ctk.CTkButton(sugestoes, text=titulo, height=35, corner_radius=9, font=fonte(12, 'bold'),
                          fg_color=INNER, hover_color='#253B50', border_width=1, border_color=BORDER,
                          command=func).grid(row=0, column=idx, sticky='ew', padx=4)

        input_area = ctk.CTkFrame(conversa, fg_color=INNER, corner_radius=10, border_width=1, border_color=BORDER)
        input_area.grid(row=3, column=0, sticky='ew', padx=16, pady=(0, 15))
        self.entry_msg = ctk.CTkEntry(input_area, placeholder_text='Escreva sua pergunta aqui...', height=44,
                                      fg_color='transparent', border_width=0, font=fonte(13), text_color=WHITE)
        self.entry_msg.pack(side='left', fill='x', expand=True, padx=(12, 6), pady=5)
        self.entry_msg.bind('<Return>', lambda _e: self._enviar_mensagem())
        self.btn_enviar = ctk.CTkButton(input_area, text='Enviar  ➤', width=102, height=38,
                                        corner_radius=9, fg_color=PURPLE, hover_color='#8B5CF6',
                                        text_color=BG, font=fonte(12, 'bold'), command=self._enviar_mensagem)
        self.btn_enviar.pack(side='right', padx=(0, 6), pady=5)

    def _ajustar_largura(self, e):
        self._largura_chat = max(230, int(e.width) - 110)
        for texto in getattr(self, '_labels_mensagem', []):
            if texto.winfo_exists():
                texto.configure(wraplength=self._largura_chat)

    def _boas_vindas(self):
        self._labels_mensagem = []
        self._balao('ia', f'Hello, {self.nome_usuario}! 👋\nI can help with budgeting, goals and expenses. Your chat starts empty, and all figures are taken from your account.')

    def _balao(self, autor, mensagem):
        usuario = autor == 'usuario'
        wrap = ctk.CTkFrame(self.chat_scroll, fg_color='transparent')
        wrap.pack(fill='x', padx=6, pady=5)
        box = ctk.CTkFrame(wrap, fg_color='#283456' if usuario else INNER,
                           corner_radius=12, border_width=1,
                           border_color='#43517D' if usuario else BORDER)
        box.pack(side='right' if usuario else 'left', fill='x', expand=True, padx=(60, 0) if usuario else (0, 60))
        self._label(box, 'Você' if usuario else '✦ Assistente IA', 11,
                    '#C7D2FE' if usuario else PURPLE, True).pack(anchor='w', padx=15, pady=(12, 2))
        label = self._label(box, str(mensagem), 14, WHITE, wraplength=getattr(self, '_largura_chat', 650), justify='left', anchor='w')
        label.pack(fill='x', anchor='w', padx=15, pady=(0, 5))
        self._labels_mensagem.append(label)
        self._label(box, datetime.now().strftime('%H:%M'), 10, MUTED).pack(anchor='e', padx=15, pady=(0, 10))
        self.mensagens.append((autor, str(mensagem)))
        self.after(40, self._rolar_chat)

    def _rolar_chat(self):
        if self.winfo_exists() and self.chat_scroll.winfo_exists():
            self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def _analisar_despesas(self):
        r = resumo(self.dao.listar_todos())
        self._balao('usuario', 'What were my biggest expenses this month?')
        if not r['categorias']:
            self._balao('ia', 'You have no recorded expenses this month. Add transactions to analyze your spending.')
            return
        linhas = [f'{i}. {nome}: {dinheiro(valor)}' for i, (nome, valor) in enumerate(r['categorias'][:6], 1)]
        self._balao('ia', f"Expenses for {r['mes']:02d}/{r['ano']}: {dinheiro(r['despesas'])}\n" + '\n'.join(linhas))

    def _enviar_mensagem(self):
        texto = self.entry_msg.get().strip()
        if not texto or self._aguardando_resposta:
            return
        self.entry_msg.delete(0, 'end')
        if 'biggest expenses' in texto.lower() or 'my expenses' in texto.lower() or 'maiores gastos' in texto.lower() or 'minhas despesas' in texto.lower():
            self._analisar_despesas()
            return
        self._balao('usuario', texto)
        self._aguardando_resposta = True
        self.btn_enviar.configure(state='disabled', text='Aguarde...')
        def trabalhar():
            try:
                from services.ai_service import AIService
                resposta = AIService().enviar_pergunta(texto)
            except Exception as exc:
                resposta = f'Could not contact the AI service: {exc}'
            self._fila.put(resposta)
        threading.Thread(target=trabalhar, daemon=True).start()
        self.after(150, self._verificar_resposta)

    def _verificar_resposta(self):
        if not self.winfo_exists():
            return
        try:
            resposta = self._fila.get_nowait()
        except queue.Empty:
            self.after(150, self._verificar_resposta)
            return
        self._aguardando_resposta = False
        self.btn_enviar.configure(state='normal', text='Enviar  ➤')
        self._balao('ia', resposta)
