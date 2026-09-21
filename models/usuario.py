from datetime import date


class Usuario:
    """Modelo representando o Usuário do sistema."""

    def __init__(
        self,
        id=None,
        nome="",
        email="",
        senha_hash="",
        tipo_perfil="PF",
        data_criacao=None,
    ):
        self._id = id
        self._nome = nome
        self._email = email
        self._senha_hash = senha_hash
        self._tipo_perfil = tipo_perfil
        self._data_criacao = data_criacao or date.today().strftime("%Y-%m-%d")

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
    def email(self):
        return self._email

    @email.setter
    def email(self, novo_email):
        self._email = novo_email

    @property
    def senha_hash(self):
        return self._senha_hash

    @senha_hash.setter
    def senha_hash(self, nova_senha_hash):
        self._senha_hash = nova_senha_hash

    @property
    def tipo_perfil(self):
        return self._tipo_perfil

    @tipo_perfil.setter
    def tipo_perfil(self, novo_tipo_perfil):
        self._tipo_perfil = novo_tipo_perfil

    @property
    def data_criacao(self):
        return self._data_criacao

    @data_criacao.setter
    def data_criacao(self, nova_data_criacao):
        self._data_criacao = nova_data_criacao

    def eh_pj(self) -> bool:
        return self._tipo_perfil == "PJ"

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "nome": self._nome,
            "email": self._email,
            "tipo_perfil": self._tipo_perfil,
            "data_criacao": str(self._data_criacao),
        }

    def __repr__(self):
        return (
            f"Usuario(id={self._id}, nome='{self._nome}', "
            f"email='{self._email}', tipo_perfil='{self._tipo_perfil}')"
        )


# Alias para manter compatibilidade com nomes legados
usuario = Usuario
