class CategoriaController:

    def __init__(self, categoria):
        self.categoria = categoria

    def criar_categoria(self, usuario, nome, tipo, escopo, limite_orcamento):

        self.categoria.usuario = usuario
        self.categoria.nome = nome
        self.categoria.tipo = tipo
        self.categoria.escopo = escopo
        self.categoria.limite_orcamento = limite_orcamento

    def editar_categoria(self, nome, tipo, escopo, limite_orcamento):

        self.categoria.nome = nome
        self.categoria.tipo = tipo
        self.categoria.escopo = escopo
        self.categoria.limite_orcamento = limite_orcamento

    def atualizar_limite_orcamento(self, novo_limite):
        self.categoria.limite_orcamento = novo_limite

    def verificar_alerta_vazamento(self):
        return self.categoria.emitir_alerta_vazamento()