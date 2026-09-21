class SaudeFinanceira:
    """Modelo representando o diagnóstico de Saúde Financeira do Usuário."""

    def __init__(self, id=None, usuario_id=None, score=0, plano_acao_json="", data_atualizacao=None):
        self._id = id
        self._usuario_id = usuario_id
        self._score = score
        self._plano_acao_json = plano_acao_json
        self._data_atualizacao = data_atualizacao

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
    def score(self):
        return self._score

    @score.setter
    def score(self, novo_score):
        self._score = novo_score

    @property
    def plano_acao_json(self):
        return self._plano_acao_json

    @plano_acao_json.setter
    def plano_acao_json(self, novo_plano_acao_json):
        self._plano_acao_json = novo_plano_acao_json

    @property
    def data_atualizacao(self):
        return self._data_atualizacao

    @data_atualizacao.setter
    def data_atualizacao(self, nova_data_atualizacao):
        self._data_atualizacao = nova_data_atualizacao

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "usuario_id": self._usuario_id,
            "score": self._score,
            "plano_acao_json": self._plano_acao_json,
            "data_atualizacao": str(self._data_atualizacao),
        }

    def __repr__(self):
        return (
            f"SaudeFinanceira(id={self._id}, usuario_id={self._usuario_id}, "
            f"score={self._score}, data_atualizacao='{self._data_atualizacao}')"
        )
