class UsuarioController:

    def __init__(self, usuario):
        self.usuario = usuario

    def criar_usuario(self, nome, email, senha_hash, tipo_perfil, data_criacao):

        self.usuario.nome = nome
        self.usuario.email = email
        self.usuario.senha_hash = senha_hash
        self.usuario.tipo_perfil = tipo_perfil
        self.usuario.data_criacao = data_criacao

    def editar_usuario(self, nome, email, tipo_perfil):
        self.usuario.nome = nome
        self.usuario.email = email
        self.usuario.tipo_perfil = tipo_perfil

    def alterar_senha(self, nova_senha_hash):
        self.usuario.senha_hash = nova_senha_hash

    def eh_pessoa_juridica(self):
        return self.usuario.tipo_perfil == "PJ"