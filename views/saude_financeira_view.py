"""Tela independente de Saúde Financeira: sempre exibe o estado atual do mês."""
from datetime import date

import customtkinter as ctk

from dao.lancamento_dao import LancamentoDAO
from services.saude_mensal import analisar_saude_mensal
from services.visao_financeira import dinheiro
from views.tema import (
    COR_BORDA, COR_CARD, COR_CARD_INTERNO, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, fonte,
)

VERDE = '#00D084'
VERMELHO = '#FB7185'
AZUL = '#38BDF8'
FUNDO = '#0B131B'


class SaudeFinanceiraView(ctk.CTkFrame):
    """Diagnóstico mensal com score e orientações baseadas só na conta logada."""

    def __init__(self, parent, dao=None):
        super().__init__(parent, fg_color='transparent')
        self.dao = dao if dao is not None else LancamentoDAO()
        hoje = date.today()
        self.ano, self.mes = hoje.year, hoje.month
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.atualizar_dados()

    def _label(self, pai, texto, tamanho=13, cor=COR_TEXTO_PRINCIPAL,
               peso='normal', **kwargs):
        return ctk.CTkLabel(pai, text=texto, font=fonte(tamanho, peso),
                            text_color=cor, **kwargs)

    def _navegar(self, rota):
        pai = self.master
        while pai is not None:
            if hasattr(pai, 'selecionar'):
                pai.selecionar(rota)
                break
            pai = getattr(pai, 'master', None)

    def _mudar_mes(self, incremento):
        novo = self.mes + incremento
        if novo < 1:
            self.ano, self.mes = self.ano - 1, 12
        elif novo > 12:
            self.ano, self.mes = self.ano + 1, 1
        else:
            self.mes = novo
        self.atualizar_dados()

    def _secao(self, pai, titulo):
        caixa = ctk.CTkFrame(pai, fg_color=COR_CARD, corner_radius=12,
                              border_width=1, border_color=COR_BORDA)
        caixa.pack(fill='x', pady=(4, 12))
        self._label(caixa, titulo, 16, peso='bold').pack(anchor='w', padx=20, pady=(17, 10))
        return caixa

    def _cartao_valor(self, pai, coluna, titulo, valor, detalhe, cor):
        card = ctk.CTkFrame(pai, fg_color=COR_CARD, corner_radius=12,
                            border_width=1, border_color=COR_BORDA)
        card.grid(row=0, column=coluna, padx=(0 if coluna == 0 else 5,
                                             0 if coluna == 2 else 5), sticky='nsew')
        self._label(card, titulo, 12, COR_TEXTO_SECUNDARIO).pack(anchor='w', padx=17, pady=(14, 1))
        self._label(card, dinheiro(valor), 20, cor, 'bold').pack(anchor='w', padx=17, pady=(2, 3))
        self._label(card, detalhe, 11, COR_TEXTO_SECUNDARIO).pack(anchor='w', padx=17, pady=(0, 15))

    def atualizar_dados(self):
        """Relê lançamentos reais e redesenha a tela, inclusive quando não há dados."""
        lancamentos = self.dao.listar_todos()
        diagnostico = analisar_saude_mensal(lancamentos, self.ano, self.mes)
        dados = diagnostico['resumo']
        for widget in self.winfo_children():
            widget.destroy()

        scroll = ctk.CTkScrollableFrame(self, fg_color='transparent')
        scroll.grid(row=0, column=0, sticky='nsew')

        topo = ctk.CTkFrame(scroll, fg_color='transparent')
        topo.pack(fill='x', pady=(4, 15))
        titulos = ctk.CTkFrame(topo, fg_color='transparent')
        titulos.pack(side='left', fill='x', expand=True)
        self._label(titulos, 'Saúde Financeira', 24, peso='bold').pack(anchor='w')
        self._label(titulos, 'Seu diagnóstico mensal, com base nas movimentações cadastradas.',
                    12, COR_TEXTO_SECUNDARIO).pack(anchor='w', pady=(4, 0))
        seletor = ctk.CTkFrame(topo, fg_color=COR_CARD, corner_radius=9)
        seletor.pack(side='right')
        for texto, acao in (
            ('‹', lambda: self._mudar_mes(-1)),
            ('›', lambda: self._mudar_mes(1)),
            ('↻', self.atualizar_dados),
        ):
            if texto == '›':
                self._label(seletor, f'{self.mes:02d}/{self.ano}', 13, peso='bold').pack(side='left', padx=10)
            ctk.CTkButton(seletor, text=texto, width=33, fg_color='transparent',
                          hover_color=COR_CARD_INTERNO, command=acao).pack(side='left')

        # O diagnóstico aparece SEMPRE. Na conta vazia, não há score inventado.
        principal = ctk.CTkFrame(scroll, fg_color=COR_CARD, corner_radius=14,
                                 border_width=1, border_color=COR_BORDA)
        principal.pack(fill='x', pady=(0, 13))
        principal.grid_columnconfigure(0, weight=1)
        principal.grid_columnconfigure(1, weight=1)
        esquerda = ctk.CTkFrame(principal, fg_color='transparent')
        esquerda.grid(row=0, column=0, sticky='nsew', padx=24, pady=23)
        self._label(esquerda, 'DIAGNÓSTICO DO MÊS', 11, COR_TEXTO_SECUNDARIO,
                    'bold').pack(anchor='w', pady=(0, 7))
        self._label(esquerda, diagnostico['situacao'], 25,
                    diagnostico['cor'], 'bold').pack(anchor='w', pady=(0, 6))
        self._label(esquerda, diagnostico['mensagem'], 13,
                    COR_TEXTO_SECUNDARIO, wraplength=320, justify='left',
                    anchor='w').pack(anchor='w', fill='x')

        direita = ctk.CTkFrame(principal, fg_color=COR_CARD_INTERNO, corner_radius=11)
        direita.grid(row=0, column=1, sticky='nsew', padx=(0, 22), pady=20)
        pontuacao = (f"{diagnostico['score']} / 1000"
                     if diagnostico['score'] is not None else '— / 1000')
        self._label(direita, 'Pontuação financeira', 12, COR_TEXTO_SECUNDARIO).pack(anchor='w', padx=18, pady=(16, 4))
        self._label(direita, pontuacao, 25, diagnostico['cor'], 'bold').pack(anchor='w', padx=18)
        barra = ctk.CTkProgressBar(direita, height=11, fg_color='#283948',
                                   progress_color=diagnostico['cor'])
        barra.pack(fill='x', padx=18, pady=(12, 8))
        barra.set((diagnostico['score'] or 0) / 1000)
        self._label(direita, 'Calculada com os dados do período selecionado',
                    10, COR_TEXTO_SECUNDARIO).pack(anchor='w', padx=18, pady=(0, 15))

        valores = ctk.CTkFrame(scroll, fg_color='transparent')
        valores.pack(fill='x', pady=(0, 12))
        for coluna in range(3):
            valores.grid_columnconfigure(coluna, weight=1, uniform='saude')
        self._cartao_valor(valores, 0, 'Receitas do mês', dados['receitas'],
                           'Entradas registradas', VERDE)
        self._cartao_valor(valores, 1, 'Despesas do mês', dados['despesas'],
                           'Saídas registradas', VERMELHO)
        self._cartao_valor(valores, 2, 'Saldo do mês', dados['saldo'],
                           'Receitas menos despesas', AZUL if dados['saldo'] >= 0 else VERMELHO)

        informacao = self._secao(scroll, 'Comprometimento da renda')
        percentual = diagnostico['percentual_gastos']
        if percentual is None:
            descricao = 'Sem receita cadastrada para calcular o comprometimento da renda.'
            fracao = 0
        else:
            descricao = f'{percentual:.1f}% da renda deste mês está comprometida com despesas.'
            fracao = max(0, min(1, percentual / 100))
        self._label(informacao, descricao, 13, COR_TEXTO_SECUNDARIO).pack(anchor='w', padx=20, pady=(0, 10))
        barra_renda = ctk.CTkProgressBar(informacao, height=12, fg_color='#283948',
                                         progress_color=VERMELHO if fracao > .8 else VERDE)
        barra_renda.pack(fill='x', padx=20, pady=(0, 19))
        barra_renda.set(fracao)

        orientacoes = self._secao(scroll, 'Orientações para este mês')
        for indice, orientacao in enumerate(diagnostico['orientacoes'], 1):
            linha = ctk.CTkFrame(orientacoes, fg_color=COR_CARD_INTERNO, corner_radius=9)
            linha.pack(fill='x', padx=17, pady=(0, 8))
            self._label(linha, f'{indice:02d}', 13, VERDE, 'bold').pack(side='left', padx=(14, 12), pady=12)
            self._label(linha, orientacao, 12, COR_TEXTO_PRINCIPAL,
                        wraplength=700, anchor='w', justify='left').pack(side='left', padx=(0, 14), pady=12)
        acoes = ctk.CTkFrame(orientacoes, fg_color='transparent')
        acoes.pack(anchor='w', padx=17, pady=(7, 17))
        ctk.CTkButton(acoes, text='+ Adicionar lançamento', width=175,
                      fg_color=VERDE, text_color=FUNDO,
                      command=lambda: self._navegar('lancamento')).pack(side='left', padx=(0, 10))
        ctk.CTkButton(acoes, text='Ver categorias', width=142,
                      fg_color=COR_CARD_INTERNO,
                      command=lambda: self._navegar('categoria')).pack(side='left')

        categorias = self._secao(scroll, 'Maiores despesas por categoria')
        if not dados['categorias']:
            self._label(categorias, 'Nenhuma despesa registrada neste mês.',
                        13, COR_TEXTO_SECUNDARIO).pack(anchor='w', padx=20, pady=(0, 20))
        for categoria, gasto in dados['categorias'][:4]:
            linha = ctk.CTkFrame(categorias, fg_color=COR_CARD_INTERNO, corner_radius=8)
            linha.pack(fill='x', padx=18, pady=(0, 7))
            self._label(linha, categoria, 12, peso='bold').pack(side='left', padx=14, pady=12)
            self._label(linha, dinheiro(gasto), 12, VERMELHO, 'bold').pack(side='right', padx=14)
        self._label(categorias, ' ', 4).pack()
