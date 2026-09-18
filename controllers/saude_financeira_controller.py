class SaudeFinanceiraController:

 def __init__(self, saude_financeira):
        self.saude_financeira = saude_financeira

 def criar_saude_financeira(self, usuario_id, score, plano_acao_json, data_atualizacao):
        self.saude_financeira.usuario_id = usuario_id
        self.saude_financeira.score = score
        self.saude_financeira.plano_acao_json = plano_acao_json
        self.saude_financeira.data_atualizacao = data_atualizacao

 def atualizar_score(self, novo_score, data_atualizacao):
        self.saude_financeira.score = novo_score
        self.saude_financeira.data_atualizacao = data_atualizacao

 def atualizar_plano_acao(self, novo_plano_acao_json, data_atualizacao):
        self.saude_financeira.plano_acao_json = novo_plano_acao_json
        self.saude_financeira.data_atualizacao = data_atualizacao

 def adicionar_pontos(self, pontos, data_atualizacao):
        self.saude_financeira.score += pontos
        self.saude_financeira.data_atualizacao = data_atualizacao


