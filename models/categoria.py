class Categoria:
    """Modelo representando uma Categoria de Lançamentos."""

    def __init__(
        self,
        id=None,
        nome="",
        usuario=None,
        tipo="Despesa",
        escopo="Pessoal",
        limite_orcamento=0.0,
        usuario_id=None,
    ):
        self._id = id
        self._nome = nome
        self._usuario = usuario_id if usuario_id is not None else usuario
        self._tipo = tipo
        self._escopo = escopo
        self._limite_orcamento = float(limite_orcamento) if limite_orcamento else 0.0

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, novo_id):
        self._id = novo_id

    @property
    def nome(self):
        return self._nome

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
    def usuario_id(self):
        return self._usuario

    @usuario_id.setter
    def usuario_id(self, novo_usuario_id):
        self._usuario = novo_usuario_id

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
        self._limite_orcamento = float(novo_limite) if novo_limite is not None else 0.0

    def emitir_alerta_vazamento(self):
        if self._limite_orcamento is not None and self._limite_orcamento < 0:
            return f"Alerta: O limite de orçamento para a categoria '{self._nome}' foi ultrapassado!"
        return None

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "usuario_id": self._usuario,
            "nome": self._nome,
            "tipo": self._tipo,
            "escopo": self._escopo,
            "limite_orcamento": self._limite_orcamento,
        }

    def __repr__(self):
        return (
            f"Categoria(id={self._id}, nome='{self._nome}', "
            f"tipo='{self._tipo}', escopo='{self._escopo}', limite={self._limite_orcamento})"
        )
