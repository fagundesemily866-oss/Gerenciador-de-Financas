class Terceiro:

    def __init__(self, id, usuario_id, nome, relacao, data_criacao):
        self._id = id
        self._usuario_id = usuario_id
        self._nome = nome
        self._relacao = relacao
        self._data_criacao = data_criacao

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
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, novo_nome):
        self._nome = novo_nome

    @property
    def relacao(self):
        return self._relacao

    @relacao.setter
    def relacao(self, nova_relacao):
        self._relacao = nova_relacao

    @property
    def data_criacao(self):
        return self._data_criacao

    @data_criacao.setter
    def data_criacao(self, nova_data_criacao):
        self._data_criacao = nova_data_criacao


    def eh_valido(self):
        if not self._nome or not self._nome.strip():
            return false,
        if not self._relacao or not self._relacao.strip():
            return false,
        return True,

    def formartar_exibicao(self):
        return f"{self._nome} ({self._relacao})"
        return True,

    def __repr__(self):
        return f"Terceiro(id={self._id}, nome='{self._nome}', relacao='{self._relacao}')"