class LancamentoController:

    def __init__(self, lancamento):
        self.lancamento = lancamento

    def criar_lancamento(self, usuario_id, categoria_id, terceiro_id,
                         descricao, valor, tipo, status, data_vencimento):

        self.lancamento.usuario_id = usuario_id
        self.lancamento.categoria_id = categoria_id
        self.lancamento.terceiro_id = terceiro_id
        self.lancamento.descricao = descricao
        self.lancamento.valor = valor
        self.lancamento.tipo = tipo
        self.lancamento.status = status
        self.lancamento.data_vencimento = data_vencimento

    def editar_lancamento(self, descricao, valor, tipo, status,
                          data_vencimento):

        self.lancamento.descricao = descricao
        self.lancamento.valor = valor
        self.lancamento.tipo = tipo
        self.lancamento.status = status
        self.lancamento.data_vencimento = data_vencimento

    def atualizar_status(self, status):
        self.lancamento.status = status

    def adicionar_pagamento(self, data_pagamento):
        self.lancamento.data_pagamento = data_pagamento

    def adicionar_comprovante(self, comprovante_url):
        self.lancamento.comprovante_url = comprovante_url