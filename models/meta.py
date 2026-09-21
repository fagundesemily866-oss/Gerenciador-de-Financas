class Meta:
    """Modelo representando uma Meta Financeira."""

    def __init__(
        self,
        id=None,
        usuario_id=None,
        descricao="",
        valor_alvo=0.0,
        valor_atual=0.0,
        prazo=None,
        data_limite=None,
    ):
        self._id = id
        self._usuario_id = usuario_id
        self._descricao = descricao
        self._valor_alvo = float(valor_alvo) if valor_alvo else 0.0
        self._valor_atual = float(valor_atual) if valor_atual else 0.0
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
        self._valor_alvo = float(novo_valor_alvo)

    @property
    def valor_atual(self):
        return self._valor_atual

    @valor_atual.setter
    def valor_atual(self, novo_valor_atual):
        self._valor_atual = float(novo_valor_atual)

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

    def guardar_valor(self, quantia):
        if quantia <= 0:
            return "A quantia a ser guardada deve ser maior que zero."

        self._valor_atual += quantia
        return f"R$ {quantia:.2f} adicionados à meta '{self._descricao}'!"

    def calcular_progresso(self):
        if self._valor_alvo <= 0:
            return 0.0

        progresso = (self._valor_atual / self._valor_alvo) * 100
        return min(round(progresso, 2), 100.0)

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "usuario_id": self._usuario_id,
            "descricao": self._descricao,
            "valor_alvo": self._valor_alvo,
            "valor_atual": self._valor_atual,
            "prazo": self._prazo,
            "data_limite": self._data_limite,
            "progresso": self.calcular_progresso(),
        }

    def __repr__(self):
        return (
            f"Meta(id={self._id}, descricao='{self._descricao}', "
            f"valor_alvo={self._valor_alvo}, valor_atual={self._valor_atual})"
        )