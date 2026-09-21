class SaudeFinanceiraController:

    def __init__(self, saude_financeira=None):
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

    # ------------------------------------------------------------------
    # CÁLCULO DA SAÚDE FINANCEIRA A PARTIR DOS LANÇAMENTOS REAIS
    # ------------------------------------------------------------------
    @staticmethod
    def calcular_saude(lancamentos):
        """
        Recebe a lista de lançamentos vindos do banco (LancamentoDAO.listar_todos())
        e devolve um dicionário pronto para a tela, ou None se não houver
        nenhum lançamento cadastrado ainda.

        Cada lançamento é um dict com: description, value, type ('Receita'
        ou 'Despesa'), category, date.
        """
        if not lancamentos:
            return None

        total_receitas = sum(l["value"] for l in lancamentos if l["type"] == "Receita")
        total_despesas = sum(l["value"] for l in lancamentos if l["type"] == "Despesa")
        saldo = total_receitas - total_despesas

        score = SaudeFinanceiraController._calcular_score(total_receitas, total_despesas, saldo)
        status_texto = SaudeFinanceiraController._status_por_score(score)

        gastos_por_categoria = {}
        for l in lancamentos:
            if l["type"] == "Despesa":
                gastos_por_categoria[l["category"]] = (
                    gastos_por_categoria.get(l["category"], 0) + l["value"]
                )

        vazamento = SaudeFinanceiraController._detectar_vazamento(
            gastos_por_categoria, total_receitas
        )

        plano_acao = SaudeFinanceiraController._montar_plano_acao(
            saldo, total_receitas, vazamento
        )

        resumo = {
            "total_receitas": total_receitas,
            "total_despesas": total_despesas,
            "saldo": saldo,
            "qtd_lancamentos": len(lancamentos),
            "gastos_por_categoria": gastos_por_categoria,
        }

        return {
            "score": score,
            "status_texto": status_texto,
            "vazamento": vazamento,
            "plano_acao": plano_acao,
            "resumo": resumo,
        }

    @staticmethod
    def _calcular_score(total_receitas, total_despesas, saldo):
        """Score de 0 a 1000 baseado na taxa de poupança (saldo / receitas)."""
        if total_receitas > 0:
            taxa_poupanca = saldo / total_receitas
            score = 500 + (taxa_poupanca * 500)
        elif total_despesas > 0:
            # Só há despesas registradas, nenhuma receita: saúde ruim.
            score = 150
        else:
            score = 500

        return max(0, min(1000, round(score)))

    @staticmethod
    def _status_por_score(score):
        if score >= 800:
            return "Saúde Financeira Excelente"
        if score >= 600:
            return "Saúde Financeira Boa"
        if score >= 400:
            return "Saúde Financeira Regular"
        if score >= 200:
            return "Saúde Financeira em Atenção"
        return "Saúde Financeira Crítica"

    @staticmethod
    def _detectar_vazamento(gastos_por_categoria, total_receitas):
        """
        Regra simples de orçamento: nenhuma categoria de despesa deveria
        consumir mais que 30% da renda total. Se consumir, é um 'vazamento'.
        """
        if not gastos_por_categoria or total_receitas <= 0:
            return None

        categoria_top = max(gastos_por_categoria, key=gastos_por_categoria.get)
        valor_top = gastos_por_categoria[categoria_top]
        limite = total_receitas * 0.3

        if valor_top > limite:
            return {
                "categoria": categoria_top,
                "limite": limite,
                "atual": valor_top,
            }
        return None

    @staticmethod
    def _montar_plano_acao(saldo, total_receitas, vazamento):
        plano = []

        if saldo < 0:
            plano.append({
                "missao": f"Reduza despesas: você está R$ {abs(saldo):.2f} no vermelho",
                "pontos": "+50 pts",
                "concluida": False,
            })

        if vazamento:
            excedente = vazamento["atual"] - vazamento["limite"]
            plano.append({
                "missao": f"Corte cerca de R$ {excedente:.2f} em '{vazamento['categoria']}'",
                "pontos": "+30 pts",
                "concluida": False,
            })

        if total_receitas == 0:
            plano.append({
                "missao": "Registre suas receitas para uma análise mais precisa",
                "pontos": "+20 pts",
                "concluida": False,
            })

        if saldo > 0:
            plano.append({
                "missao": f"Guarde parte do seu saldo positivo (R$ {saldo:.2f}) em uma reserva",
                "pontos": "+20 pts",
                "concluida": False,
            })

        if not plano:
            plano.append({
                "missao": "Continue registrando seus lançamentos regularmente",
                "pontos": "+10 pts",
                "concluida": True,
            })

        return plano