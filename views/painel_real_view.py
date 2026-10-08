"""Dashboard e Relatório baseados somente nos dados da conta autenticada."""
from datetime import date
from tkinter import filedialog, messagebox
import customtkinter as ctk

from dao.lancamento_dao import LancamentoDAO
from dao.categoria_dao import CategoriaDAO
from dao.meta_dao import MetaDAO
from services.visao_financeira import resumo, dinheiro, periodo_anterior, campo
from views.tema import COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL, COR_TEXTO_SECUNDARIO, fonte

BG = '#0B131B'
GREEN = '#00D084'
RED = '#FB7185'
BLUE = '#38BDF8'


class _PainelFinanceiro(ctk.CTkFrame):
    titulo = ''

    def __init__(self, parent, dao=None, cat_dao=None, meta_dao=None):
        super().__init__(parent, fg_color='transparent')
        self.dao = dao or LancamentoDAO()
        self.cat_dao = cat_dao or CategoriaDAO()
        self.meta_dao = meta_dao or MetaDAO()
        hoje = date.today()
        self.ano, self.mes = hoje.year, hoje.month
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.atualizar_dados()

    def _navegar(self, tela):
        curr = self.master
        while curr is not None:
            if hasattr(curr, 'selecionar'):
                curr.selecionar(tela)
                return
            curr = getattr(curr, 'master', None)

    def _mudar_mes(self, delta):
        mes = self.mes + delta
        if mes < 1:
            self.ano, self.mes = self.ano - 1, 12
        elif mes > 12:
            self.ano, self.mes = self.ano + 1, 1
        else:
            self.mes = mes
        self.atualizar_dados()

    def _texto(self, parent, valor, size=13, cor=COR_TEXTO_PRINCIPAL, peso='normal', **kw):
        lbl = ctk.CTkLabel(parent, text=str(valor), font=fonte(size, peso), text_color=cor, **kw)
        return lbl

    def _card(self, parent, titulo, valor, detalhe='', cor=GREEN, col=None):
        f = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        if col is None:
            f.pack(fill='x', pady=5)
        else:
            f.grid(row=0, column=col, padx=5, sticky='nsew')
        self._texto(f, titulo, 12, COR_TEXTO_SECUNDARIO).pack(anchor='w', padx=16, pady=(13, 0))
        self._texto(f, valor, 21, cor, 'bold').pack(anchor='w', padx=16, pady=(3, 0))
        self._texto(f, detalhe or ' ', 11, COR_TEXTO_SECUNDARIO).pack(anchor='w', padx=16, pady=(1, 12))
        return f

    def _secao(self, parent, titulo):
        f = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA)
        f.pack(fill='x', pady=(8, 6))
        self._texto(f, titulo, 16, COR_TEXTO_PRINCIPAL, 'bold').pack(anchor='w', padx=17, pady=(15, 7))
        return f

    def _vazio(self, parent, texto, rota=None, botao='Cadastrar lançamento'):
        f = ctk.CTkFrame(parent, fg_color=COR_CARD_INTERNO, corner_radius=10)
        f.pack(fill='x', padx=14, pady=(8, 16))
        self._texto(f, texto, 13, COR_TEXTO_SECUNDARIO, wraplength=780, justify='left').pack(anchor='w', padx=14, pady=13)
        if rota:
            ctk.CTkButton(f, text=botao, fg_color=GREEN, text_color=BG, width=180,
                          command=lambda: self._navegar(rota)).pack(anchor='w', padx=14, pady=(0, 13))

    def _carregar(self):
        self.lancamentos = self.dao.listar_todos()
        self.metas = self.meta_dao.listar_todas()
        self.categorias = self.cat_dao.listar_todas()
        self.atual = resumo(self.lancamentos, self.ano, self.mes)

    def atualizar_dados(self):
        self._carregar()
        for w in self.winfo_children():
            w.destroy()
        scroll = ctk.CTkScrollableFrame(self, fg_color='transparent')
        scroll.grid(row=0, column=0, sticky='nsew')
        topo = ctk.CTkFrame(scroll, fg_color='transparent')
        topo.pack(fill='x', pady=(4, 13))
        self._texto(topo, self.titulo, 23, peso='bold').pack(side='left')
        nav = ctk.CTkFrame(topo, fg_color=COR_CARD, corner_radius=9)
        nav.pack(side='right')
        ctk.CTkButton(nav, text='‹', width=32, fg_color='transparent', hover_color=COR_CARD_INTERNO,
                      command=lambda: self._mudar_mes(-1)).pack(side='left')
        self._texto(nav, f'{self.mes:02d}/{self.ano}', 13, peso='bold').pack(side='left', padx=10)
        ctk.CTkButton(nav, text='›', width=32, fg_color='transparent', hover_color=COR_CARD_INTERNO,
                      command=lambda: self._mudar_mes(1)).pack(side='left')
        ctk.CTkButton(nav, text='↻', width=32, fg_color='transparent', hover_color=COR_CARD_INTERNO,
                      command=self.atualizar_dados).pack(side='left')
        metrics = ctk.CTkFrame(scroll, fg_color='transparent')
        metrics.pack(fill='x', pady=(0, 13))
        for col in range(3):
            metrics.grid_columnconfigure(col, weight=1)
        r = self.atual
        self._card(metrics, 'Receitas do mês', dinheiro(r['receitas']), 'Registradas na sua conta', GREEN, 0)
        self._card(metrics, 'Despesas do mês', dinheiro(r['despesas']), 'Registradas na sua conta', RED, 1)
        self._card(metrics, 'Saldo do mês', dinheiro(r['saldo']), 'Receitas − despesas', BLUE, 2)
        self._conteudo(scroll)

    def _conteudo(self, parent):
        raise NotImplementedError


class DashboardRealView(_PainelFinanceiro):
    titulo = 'Dashboard'

    def _conteudo(self, parent):
        if not self.lancamentos and not self.metas:
            self._vazio(parent, 'Sua conta está vazia. Os números aparecerão depois de cadastrar lançamentos ou metas. Nenhum dado fictício é criado automaticamente.', 'lancamento')
            return
        linhas = self._secao(parent, 'Movimentações recentes')
        registros = sorted(self.lancamentos, key=lambda l: str(campo(l, 'date', '')), reverse=True)[:6]
        if not registros:
            self._vazio(linhas, 'Ainda não há lançamentos para mostrar.', 'lancamento')
        for l in registros:
            row = ctk.CTkFrame(linhas, fg_color=COR_CARD_INTERNO, corner_radius=8)
            row.pack(fill='x', padx=14, pady=3)
            tipo = str(campo(l, 'type', '')).upper()
            self._texto(row, campo(l, 'description', 'Lançamento'), 13, peso='bold').pack(side='left', padx=12, pady=9)
            self._texto(row, dinheiro(campo(l, 'value')), 13, GREEN if tipo == 'RECEITA' else RED,
                        'bold').pack(side='right', padx=12)
        self._texto(linhas, ' ', 5).pack()
        box = self._secao(parent, 'Minhas metas')
        if not self.metas:
            self._vazio(box, 'Nenhuma meta cadastrada ainda.', 'meta', 'Criar meta')
        for m in self.metas[:6]:
            alvo = float(campo(m, 'valor_alvo', 0) or 0)
            atual = float(campo(m, 'valor_atual', 0) or 0)
            pct = min(1.0, atual / alvo) if alvo > 0 else 0.0
            f = ctk.CTkFrame(box, fg_color=COR_CARD_INTERNO, corner_radius=8)
            f.pack(fill='x', padx=14, pady=4)
            self._texto(f, f"{campo(m, 'descricao', 'Meta')}  •  {dinheiro(atual)} de {dinheiro(alvo)}", 12).pack(anchor='w', padx=12, pady=(8, 4))
            barra = ctk.CTkProgressBar(f, fg_color='#253645', progress_color=GREEN)
            barra.set(pct)
            barra.pack(fill='x', padx=12, pady=(0, 9))
        self._texto(box, ' ', 5).pack()


class RelatorioRealView(_PainelFinanceiro):
    titulo = 'Relatório Mensal'

    def _conteudo(self, parent):
        top = ctk.CTkFrame(parent, fg_color='transparent')
        top.pack(fill='x')
        ctk.CTkButton(top, text='Exportar relatório (.txt)', width=200,
                      fg_color=GREEN, text_color=BG, command=self._exportar).pack(side='right', pady=(0, 8))
        if not self.lancamentos:
            self._vazio(parent, 'Nenhuma transação cadastrada nesta conta. O relatório será preenchido com seus dados reais.', 'lancamento')
            return
        ap_ano, ap_mes = periodo_anterior(self.ano, self.mes)
        anterior = resumo(self.lancamentos, ap_ano, ap_mes)
        box = self._secao(parent, 'Comparativo com o mês anterior')
        for titulo, key in [('Receitas', 'receitas'), ('Despesas', 'despesas'), ('Saldo', 'saldo')]:
            self._texto(box, f"{titulo}: {dinheiro(self.atual[key])}   |   Anterior: {dinheiro(anterior[key])}", 13).pack(anchor='w', padx=17, pady=6)
        self._texto(box, ' ', 6).pack()
        categorias = self._secao(parent, 'Despesas por categoria')
        if not self.atual['categorias']:
            self._vazio(categorias, 'Sem despesas no período selecionado.')
        for nome, valor in self.atual['categorias']:
            p = valor / self.atual['despesas'] if self.atual['despesas'] else 0
            r = ctk.CTkFrame(categorias, fg_color=COR_CARD_INTERNO, corner_radius=8)
            r.pack(fill='x', padx=15, pady=4)
            self._texto(r, f'{nome}  •  {dinheiro(valor)}  ({p:.0%})', 12).pack(anchor='w', padx=12, pady=(6, 2))
            barra = ctk.CTkProgressBar(r, progress_color=BLUE, fg_color='#253645')
            barra.set(p)
            barra.pack(fill='x', padx=12, pady=(0, 8))
        self._texto(categorias, ' ', 5).pack()

    def _exportar(self):
        caminho = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Texto', '*.txt')],
                                               initialfile=f'relatorio_{self.ano}_{self.mes:02d}.txt')
        if not caminho:
            return
        r = self.atual
        with open(caminho, 'w', encoding='utf-8') as arq:
            arq.write(f'Relatório mensal {self.mes:02d}/{self.ano}\n')
            arq.write(f"Receitas: {dinheiro(r['receitas'])}\nDespesas: {dinheiro(r['despesas'])}\nSaldo: {dinheiro(r['saldo'])}\n")
            for nome, valor in r['categorias']:
                arq.write(f'{nome}: {dinheiro(valor)}\n')
        messagebox.showinfo('Relatório', 'Relatório salvo com sucesso.')
