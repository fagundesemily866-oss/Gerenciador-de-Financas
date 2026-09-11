class Meta:
    def __init__(self, id, usuario_id, descricao, valor_alvo, valor_atual,
                 prazo, data_limite):
        self._id = id
        self._usuario_id = usuario_id
        self._descricao = descricao
        self._valor_alvo = valor_alvo
        self._valor_atual = valor_atual
        self._prazo = prazo
        self._data_limite = data_limite

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
    def descricao(self):
        return self._descricao

    @descricao.setter
    def descricao(self, nova_descricao):
        self._descricao = nova_descricao

    @property
    def valor_alvo(self):
        return self._valor_alvo

    @valor_alvo.setter
    def valor_alvo(self, novo_valor_alvo):
        self._valor_alvo = novo_valor_alvo

    @property
    def valor_atual(self):
        return self._valor_atual

    @valor_atual.setter
    def valor_atual(self, novo_valor_atual):
        self._valor_atual = novo_valor_atual

    @property
    def prazo(self):
        return self._prazo

    @prazo.setter
    def prazo(self, novo_prazo):
        self._prazo = novo_prazo

    @property
    def data_limite(self):
        return self._data_limite
    
    @data_limite.setter
    def data_limite(self, nova_data_limite):
        self._data_limite = nova_data_limite
