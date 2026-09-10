class LancamentoController:
    def __init__(self, lancamento):
        self.lancamento = lancamento

    def criar_lancamento(self, descricao, valor, tipo):
        self.lancamento.descricao = descricao
        self.lancamento.valor = valor
        self.lancamento.tipo = tipo