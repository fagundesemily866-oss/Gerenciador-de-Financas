class Categoria:

    def __init__(self, id, nome, usuario, tipo, escopo, limite_orcamento):
        self._id = id
        self._nome = nome
        self._usuario = usuario
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

    @property 
    def usuario(self): 
        return self._usuario
    
    @usuario.setter
    def usuario(self, novo_usuario):
        self._usuario = novo_usuario  

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, novo_tipo):
        self._tipo = novo_tipo

    @property
    def escopo(self):
        return self._escopo

    @escopo.setter
    def escopo(self, novo_escopo):
        self._escopo = novo_escopo

    @property
    def limite_orcamento(self):
        return self._limite_orcamento

    @limite_orcamento.setter
    def limite_orcamento(self, novo_limite):
        self._limite_orcamento = novo_limite

    def emitir_alerta_vazamento(self):
        if self._limite_orcamento is not None and self._limite_orcamento <0:
            return f"Alerta: O limite de orçamento para a categoria '{self._nome}' foi ultrapassado!"

    
