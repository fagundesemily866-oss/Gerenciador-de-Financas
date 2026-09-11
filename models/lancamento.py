from datetime import date


class Lancamento:

    def __init__(
        self,
        id,
        usuario_id,
        categoria_id,
        terceiro_id,
        descricao,
        valor,
        tipo,
        status,
        data_vencimento,
        data_pagamento=None,
        comprovante_url=None,
        data_criacao=None,
    ):
        self._id = id
        self._usuario_id = usuario_id
        self._categoria_id = categoria_id
        self._terceiro_id = terceiro_id
        self._descricao = descricao
        self._valor = valor
        self._tipo = tipo
        self._status = status
        self._data_vencimento = data_vencimento
        self._data_pagamento = data_pagamento
        self._comprovante_url = comprovante_url
        self._data_criacao = data_criacao or date.today()

    # --- PROPERTIES (GETTERS / SETTERS) ---
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, novo_id):
        self._id = novo_id

    @property
    def usuario_id(self):
        return self._usuario_id

    @usuario_id.setter
    def usuario_id(self, novo_usuario_id):
        self._usuario_id = novo_usuario_id

    @property
    def categoria_id(self):
        return self._categoria_id

    @categoria_id.setter
    def categoria_id(self, nova_categoria_id):
        self._categoria_id = nova_categoria_id

    @property
    def terceiro_id(self):
        return self._terceiro_id

    @terceiro_id.setter
    def terceiro_id(self, novo_terceiro_id):
        self._terceiro_id = novo_terceiro_id

    @property
    def descricao(self):
        return self._descricao

    @descricao.setter
    def descricao(self, nova_descricao):
        self._descricao = nova_descricao

    @property
    def valor(self):
        return self._valor

    @valor.setter
    def valor(self, novo_valor):
        self._valor = novo_valor

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, novo_tipo):
        self._tipo = novo_tipo

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, novo_status):
        self._status = novo_status

    @property
    def data_vencimento(self):
        return self._data_vencimento

    @data_vencimento.setter
    def data_vencimento(self, nova_data_vencimento):
        self._data_vencimento = nova_data_vencimento

    @property
    def data_pagamento(self):
        return self._data_pagamento

    @data_pagamento.setter
    def data_pagamento(self, nova_data_pagamento):
        self._data_pagamento = nova_data_pagamento

    @property
    def comprovante_url(self):
        return self._comprovante_url

    @comprovante_url.setter
    def comprovante_url(self, nova_comprovante_url):
        self._comprovante_url = nova_comprovante_url

    @property
    def data_criacao(self):
        return self._data_criacao

    @data_criacao.setter
    def data_criacao(self, nova_data_criacao):
        self._data_criacao = nova_data_criacao

    # --- MÉTODOS DE NEGÓCIO ---
    def efetuar_pagamento(
        self, data_pagamento=None, comprovante_url=None
    ):
        """Atualiza o status, data de pagamento e salva o comprovante."""
        self._status = "PAGO" if self._tipo == "DESPESA" else "RECEBIDO"
        self._data_pagamento = data_pagamento or date.today()

        if comprovante_url:
            self._comprovante_url = comprovante_url

        return (
            f"Lançamento '{self._descricao}' atualizado para {self._status}."
        )

    def verificar_atraso(self):
        """Verifica se a conta venceu sem ser paga."""
        if self._status == "PENDENTE" and self._data_vencimento < date.today():
            self._status = "ATRASADO"
            return True
        return False

    def __repr__(self):
        return (
            f"Lancamento(id={self._id}, usuario_id={self._usuario_id}, "
            f"categoria_id={self._categoria_id}, terceiro_id={self._terceiro_id}, "
            f"descricao='{self._descricao}', valor={self._valor}, tipo='{self._tipo}', "
            f"status='{self._status}', data_vencimento={self._data_vencimento}, "
            f"data_pagamento={self._data_pagamento}, comprovante_url='{self._comprovante_url}', "
            f"data_criacao={self._data_criacao})"
        )