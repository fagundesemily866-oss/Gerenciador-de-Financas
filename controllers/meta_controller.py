class MetaController:

    def __init__(self, meta):
        self.meta = meta

    def criar_meta(self, usuario_id, descricao, valor_alvo, valor_atual,
                    prazo, data_limite):

        self.meta.usuario_id = usuario_id
        self.meta.descricao = descricao
        self.meta.valor_alvo = valor_alvo
        self.meta.valor_atual = valor_atual
        self.meta.prazo = prazo
        self.meta.data_limite = data_limite

    def editar_meta(self, descricao, valor_alvo, prazo, data_limite):

        self.meta.descricao = descricao
        self.meta.valor_alvo = valor_alvo
        self.meta.prazo = prazo
        self.meta.data_limite = data_limite

    def guardar_valor(self, quantia):
        return self.meta.guardar_valor(quantia)

    def calcular_progresso(self):
        return self.meta.calcular_progresso()