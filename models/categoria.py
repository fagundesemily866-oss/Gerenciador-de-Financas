class Categoria:

    def __init__(self, id, nome, usuario_id, tipo, escopo, limite_orcamento):
        self._id = id
        self._nome = nome
        self._usuario = usuario_id
        self._tipo = tipo
        self._escopo = escopo
        self._limite_orcamento = limite_orcamento

    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, novo_id):
        self._id = novo_id

    @property
    def nome(self):
        return self._nome.upper()
    
    @nome.setter
    def nome(self, novo_nome):
        self._nome = novo_nome

    
