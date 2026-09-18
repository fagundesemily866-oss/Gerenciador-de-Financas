class TerceiroController:

    def __init__(self, terceiro):
        self.terceiro = terceiro

    def criar_terceiro(self, usuario_id, nome, relacao, data_criacao):

        self.terceiro.usuario_id = usuario_id
        self.terceiro.nome = nome
        self.terceiro.relacao = relacao
        self.terceiro.data_criacao = data_criacao

    def editar_terceiro(self, nome, relacao):
        self.terceiro.nome = nome
        self.terceiro.relacao = relacao

    def validar_terceiro(self):
        return self.terceiro.eh_valido()

    def exibir_terceiro(self):
        return self.terceiro.formartar_exibicao()