"""
Gerador de Finanças Aleatórias (modo demonstração)
==================================================

Cria, para um usuário já existente, um conjunto de dados FICTÍCIOS porém coerentes
entre si, pensado para apresentações e demonstrações do sistema:

* renda mensal do usuário;
* categorias (de receita e de despesa) com limites de orçamento;
* terceiros (fornecedores, clientes, familiares...);
* ~6 meses de lançamentos, cada um apontando para uma categoria e um terceiro do
  MESMO usuário, com status e datas válidos;
* metas com aportes datados, valores matematicamente consistentes
  (valor atual = soma dos aportes) e prazos variados;
* histórico de saúde financeira calculado a partir dos próprios lançamentos.

Todo o conteúdo é gerado via DAOs, portanto aparece normalmente no Dashboard,
Lançamentos, Metas, Categorias, Terceiros, Relatório, Simulador e Assistente IA.
Cada chamada usa sorteios novos (a menos que um ``random.Random`` com semente seja
injetado, o que é útil nos testes).
"""
import calendar
import json
import random
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from controllers.saude_financeira_controller import SaudeFinanceiraController
from dao.categoria_dao import CategoriaDAO
from dao.lancamento_dao import LancamentoDAO
from dao.meta_dao import MetaDAO
from dao.saude_financeira_dao import SaudeFinanceiraDAO
from dao.terceiro_dao import TerceiroDAO
from dao.usuario_dao import UsuarioDAO
from models.database import Database

MESES_HISTORICO = 6

# ----------------------------------------------------------------------
# Catálogos de apoio (apenas rótulos; os VALORES são sempre sorteados)
# ----------------------------------------------------------------------
# categoria -> (faixa da fatia da renda, descrições possíveis, nº de lançamentos no mês)
_DESPESAS: Dict[str, Tuple[Tuple[float, float], List[str], Tuple[int, int]]] = {
    "Moradia": ((0.24, 0.32), ["Aluguel", "Condomínio", "Financiamento do imóvel"], (1, 2)),
    "Alimentação": ((0.12, 0.18), ["Supermercado", "Padaria", "Restaurante", "Feira", "Delivery"], (3, 5)),
    "Transporte": ((0.06, 0.10), ["Combustível", "Aplicativo de transporte", "Passagem", "Estacionamento"], (2, 3)),
    "Saúde": ((0.03, 0.06), ["Farmácia", "Plano de saúde", "Consulta médica"], (1, 2)),
    "Lazer": ((0.04, 0.08), ["Cinema", "Show", "Bar com amigos", "Passeio"], (1, 3)),
    "Educação": ((0.02, 0.06), ["Curso online", "Mensalidade", "Material de estudo"], (1, 2)),
    "Contas e Serviços": ((0.04, 0.07), ["Energia elétrica", "Internet", "Água", "Telefone"], (2, 3)),
    "Assinaturas": ((0.01, 0.02), ["Streaming de vídeo", "Streaming de música", "Armazenamento em nuvem"], (1, 2)),
    "Outros": ((0.02, 0.05), ["Presente", "Manutenção", "Compra diversa"], (1, 2)),
}
_RECEITAS_EXTRAS = {
    "Freelance": ["Projeto freelance", "Serviço avulso", "Consultoria"],
    "Rendimentos": ["Rendimento de investimentos", "Dividendos", "Juros de aplicação"],
}
_NOME_RECEITA_PRINCIPAL = {"PF": ("Salário", "Salário mensal"), "PJ": ("Faturamento", "Faturamento de clientes")}

_TERCEIROS_DESPESA = [
    ("Mercado Bom Preço", "Fornecedor"), ("Posto Estrela", "Fornecedor"),
    ("Farmácia Saúde Total", "Fornecedor"), ("Imobiliária Central", "Fornecedor"),
    ("Escola de Idiomas Alfa", "Fornecedor"), ("Companhia de Energia", "Fornecedor"),
    ("Padaria Pão Quente", "Fornecedor"), ("Clínica Vida", "Fornecedor"),
]
_TERCEIROS_RECEITA = [
    ("Tech Soluções Ltda", "Cliente"), ("Estúdio Criativo", "Cliente"),
    ("Grupo Horizonte", "Empregador"), ("Corretora Investe Mais", "Fornecedor"),
]
_TERCEIROS_PESSOAIS = [("Maria", "Familiar"), ("Carlos", "Amigo"), ("Ana", "Familiar")]

# nome -> (base do alvo: "renda" ou "despesa", faixa do múltiplo)
_METAS_MODELO: Dict[str, Tuple[str, Tuple[float, float]]] = {
    "Reserva de emergência": ("despesa", (3.0, 6.0)),
    "Viagem dos sonhos": ("renda", (0.8, 2.0)),
    "Entrada do carro": ("renda", (3.0, 6.0)),
    "Notebook novo": ("renda", (0.4, 0.9)),
    "Curso de especialização": ("renda", (0.3, 0.7)),
    "Troca de móveis": ("renda", (0.6, 1.5)),
}
_PRAZOS_VALIDOS = [3, 6, 12, 18, 24, 36]


def _arredondar(valor: float, base: float = 10.0) -> float:
    return float(round(valor / base) * base)


def _ultimo_dia(ano: int, mes: int) -> int:
    return calendar.monthrange(ano, mes)[1]


def _somar_meses(ano: int, mes: int, delta: int) -> Tuple[int, int]:
    total = ano * 12 + (mes - 1) + delta
    return total // 12, total % 12 + 1


class GeradorFinancasAleatorias:
    """Popula o banco com um ambiente de demonstração coerente para um usuário."""

    def __init__(
        self,
        db: Optional[Database] = None,
        rng: Optional[random.Random] = None,
        hoje: Optional[date] = None,
    ):
        self.db = db or Database()
        self.rng = rng or random.Random()
        self.hoje = hoje or date.today()

        self.usuario_dao = UsuarioDAO(self.db)
        self.categoria_dao = CategoriaDAO(self.db)
        self.terceiro_dao = TerceiroDAO(self.db)
        self.lancamento_dao = LancamentoDAO(self.db)
        self.meta_dao = MetaDAO(self.db)
        self.saude_dao = SaudeFinanceiraDAO(self.db)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def gerar(self, usuario_id: int) -> Dict[str, Any]:
        """
        Gera todos os dados fictícios para ``usuario_id`` e devolve um resumo
        (contagens e totais) útil para mostrar ao usuário e para os testes.
        """
        usuario = self.usuario_dao.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError(f"Usuário {usuario_id} não existe.")
        perfil = usuario.get("tipo_perfil") or "PF"
        escopo = "Empresarial" if perfil == "PJ" else "Pessoal"

        renda = self._sortear_renda(perfil)
        taxa_poupanca = self._sortear_taxa_poupanca()

        cats_despesa = self._criar_categorias(usuario_id, renda, taxa_poupanca, escopo)
        cats_receita = self._criar_categorias_receita(usuario_id, perfil, escopo)
        terceiros = self._criar_terceiros(usuario_id)
        saldos_mensais = self._criar_lancamentos(
            usuario_id, perfil, renda, cats_despesa, cats_receita, terceiros
        )
        despesa_mensal = sum(c["alvo_mensal"] for c in cats_despesa.values())
        metas = self._criar_metas(usuario_id, saldos_mensais, renda, despesa_mensal)
        self._criar_historico_saude(usuario_id)

        self.usuario_dao.atualizar_renda(usuario_id, renda)
        self._marcar_modo_demo(usuario_id)

        lancs = self.lancamento_dao.listar_todos(usuario_id)
        rec = sum(l["value"] for l in lancs if l["type"] == "Receita")
        desp = sum(l["value"] for l in lancs if l["type"] == "Despesa")
        return {
            "usuario_id": usuario_id,
            "renda_mensal": renda,
            "categorias": len(cats_despesa) + len(cats_receita),
            "terceiros": sum(len(v) for v in terceiros.values()),
            "lancamentos": len(lancs),
            "metas": len(metas),
            "total_receitas": round(rec, 2),
            "total_despesas": round(desp, 2),
            "saldo": round(rec - desp, 2),
        }

    # ------------------------------------------------------------------
    # Passos internos
    # ------------------------------------------------------------------
    def _sortear_renda(self, perfil: str) -> float:
        faixa = (9000, 28000) if perfil == "PJ" else (3200, 11500)
        return _arredondar(self.rng.uniform(*faixa), 50.0)

    def _sortear_taxa_poupanca(self) -> float:
        """Perfil financeiro da demonstração: maioria saudável, alguns apertados."""
        perfil = self.rng.choices(
            ["saudavel", "equilibrado", "apertado"], weights=[45, 40, 15]
        )[0]
        faixa = {"saudavel": (0.20, 0.32), "equilibrado": (0.08, 0.16), "apertado": (0.00, 0.05)}[perfil]
        return self.rng.uniform(*faixa)

    def _criar_categorias(
        self, usuario_id: int, renda: float, taxa_poupanca: float, escopo: str
    ) -> Dict[str, Dict[str, Any]]:
        """Cria categorias de despesa. Os alvos mensais somam renda * (1 - poupança)."""
        nomes = list(_DESPESAS.keys())
        # Educação é opcional para variar os exemplos
        if self.rng.random() < 0.3:
            nomes.remove("Educação")

        pesos = {n: self.rng.uniform(*_DESPESAS[n][0]) for n in nomes}
        soma = sum(pesos.values())
        orcamento_total = renda * (1.0 - taxa_poupanca)

        categorias: Dict[str, Dict[str, Any]] = {}
        for nome in nomes:
            alvo_mensal = orcamento_total * pesos[nome] / soma
            # O limite cadastrado fica um pouco acima do gasto típico (algumas categorias estouram)
            limite = _arredondar(alvo_mensal * self.rng.uniform(0.95, 1.20), 10.0)
            cid = self.categoria_dao.inserir(
                nome=nome, tipo="Despesa", escopo=escopo,
                limite_orcamento=limite, usuario_id=usuario_id,
            )
            categorias[nome] = {"id": cid, "alvo_mensal": alvo_mensal, "limite": limite}
        return categorias

    def _criar_categorias_receita(
        self, usuario_id: int, perfil: str, escopo: str
    ) -> Dict[str, Dict[str, Any]]:
        nome_principal = _NOME_RECEITA_PRINCIPAL[perfil][0]
        nomes = [nome_principal] + list(_RECEITAS_EXTRAS.keys())
        categorias = {}
        for nome in nomes:
            cid = self.categoria_dao.inserir(
                nome=nome, tipo="Receita", escopo=escopo,
                limite_orcamento=0.0, usuario_id=usuario_id,
            )
            categorias[nome] = {"id": cid}
        return categorias

    def _criar_terceiros(self, usuario_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Cria terceiros do usuário e os separa por papel (despesa/receita)."""
        sel_desp = self.rng.sample(_TERCEIROS_DESPESA, k=self.rng.randint(4, 6))
        sel_rec = self.rng.sample(_TERCEIROS_RECEITA, k=self.rng.randint(2, 3))
        sel_pes = self.rng.sample(_TERCEIROS_PESSOAIS, k=self.rng.randint(1, 2))

        resultado: Dict[str, List[Dict[str, Any]]] = {"despesa": [], "receita": [], "outros": []}
        for chave, lista in (("despesa", sel_desp), ("receita", sel_rec), ("outros", sel_pes)):
            for nome, relacao in lista:
                tid = self.terceiro_dao.inserir(
                    nome=nome, relacao=relacao, usuario_id=usuario_id,
                    data_criacao=self.hoje.strftime("%Y-%m-%d"),
                )
                resultado[chave].append({"id": tid, "nome": nome})
        return resultado

    def _datas_mes(self, ano: int, mes: int, quantidade: int) -> List[date]:
        """Sorteia datas ordenadas dentro do mês, nunca depois de hoje."""
        ultimo = _ultimo_dia(ano, mes)
        if (ano, mes) == (self.hoje.year, self.hoje.month):
            ultimo = min(ultimo, self.hoje.day)
        ultimo = max(1, ultimo)
        return sorted(date(ano, mes, self.rng.randint(1, ultimo)) for _ in range(quantidade))

    def _dividir(self, total: float, partes: int) -> List[float]:
        """Divide ``total`` em ``partes`` valores (centavos) cuja soma é exatamente o total."""
        if partes <= 1:
            return [round(total, 2)]
        pesos = [self.rng.uniform(0.5, 1.5) for _ in range(partes)]
        soma = sum(pesos)
        valores = [round(total * p / soma, 2) for p in pesos]
        valores[-1] = round(total - sum(valores[:-1]), 2)
        return valores

    def _criar_lancamentos(
        self,
        usuario_id: int,
        perfil: str,
        renda: float,
        cats_despesa: Dict[str, Dict[str, Any]],
        cats_receita: Dict[str, Dict[str, Any]],
        terceiros: Dict[str, List[Dict[str, Any]]],
    ) -> List[float]:
        """Gera lançamentos dos últimos meses. Retorna o saldo (receita - despesa) de cada mês."""
        nome_rec_principal, desc_rec_principal = _NOME_RECEITA_PRINCIPAL[perfil]
        saldos: List[float] = []
        pendentes_restantes = self.rng.randint(1, 2)

        for i in range(MESES_HISTORICO - 1, -1, -1):
            ano, mes = _somar_meses(self.hoje.year, self.hoje.month, -i)
            mes_atual = (ano, mes) == (self.hoje.year, self.hoje.month)
            total_rec = 0.0
            total_desp = 0.0

            # --- Receita principal (dia útil próximo ao 5) ---
            dia_rec = min(self.rng.randint(4, 8), _ultimo_dia(ano, mes))
            if mes_atual:
                dia_rec = min(dia_rec, self.hoje.day)
            valor_rec = _arredondar(renda * self.rng.uniform(0.98, 1.04), 1.0)
            tid_rec = self.rng.choice(terceiros["receita"])["id"] if terceiros["receita"] else None
            self.lancamento_dao.inserir(
                descricao=desc_rec_principal, valor=valor_rec, tipo="Receita",
                categoria=nome_rec_principal, data=date(ano, mes, dia_rec).strftime("%Y-%m-%d"),
                usuario_id=usuario_id, status="Recebido", terceiro_id=tid_rec,
            )
            total_rec += valor_rec

            # --- Receitas extras (nem todo mês) ---
            for nome_extra, descricoes in _RECEITAS_EXTRAS.items():
                if self.rng.random() < 0.40:
                    valor_extra = _arredondar(renda * self.rng.uniform(0.03, 0.12), 5.0)
                    d = self._datas_mes(ano, mes, 1)[0]
                    tid = self.rng.choice(terceiros["receita"])["id"] if terceiros["receita"] else None
                    self.lancamento_dao.inserir(
                        descricao=self.rng.choice(descricoes), valor=valor_extra, tipo="Receita",
                        categoria=nome_extra, data=d.strftime("%Y-%m-%d"),
                        usuario_id=usuario_id, status="Recebido", terceiro_id=tid,
                    )
                    total_rec += valor_extra

            # --- Despesas por categoria ---
            for nome_cat, info in cats_despesa.items():
                _, descricoes, (qmin, qmax) = _DESPESAS[nome_cat]
                alvo_mes = info["alvo_mensal"] * self.rng.uniform(0.88, 1.12)
                quantidade = self.rng.randint(qmin, qmax)
                valores = self._dividir(alvo_mes, quantidade)
                datas = self._datas_mes(ano, mes, quantidade)
                for valor, d in zip(valores, datas):
                    if valor <= 0:
                        continue
                    status = "Pago"
                    # Poucas contas a vencer no mês corrente (datas já ≤ hoje, então ficam Pendentes)
                    if mes_atual and pendentes_restantes > 0 and d.day >= max(1, self.hoje.day - 2) \
                            and self.rng.random() < 0.5:
                        status = "Pendente"
                        pendentes_restantes -= 1
                    tid = self.rng.choice(terceiros["despesa"])["id"] if terceiros["despesa"] else None
                    self.lancamento_dao.inserir(
                        descricao=self.rng.choice(descricoes), valor=valor, tipo="Despesa",
                        categoria=nome_cat, data=d.strftime("%Y-%m-%d"),
                        usuario_id=usuario_id, status=status, terceiro_id=tid,
                    )
                    total_desp += valor
            saldos.append(round(total_rec - total_desp, 2))
        return saldos

    def _criar_metas(
        self,
        usuario_id: int,
        saldos_mensais: List[float],
        renda: float,
        despesa_mensal: float,
    ) -> List[int]:
        """
        Cria metas com aportes datados. Garantias de coerência:
        * valor_atual = soma dos aportes (feito via MetaDAO.guardar_valor);
        * a soma de todos os aportes nunca passa de ~70% da poupança real gerada;
        * o valor alvo é sempre maior que o valor atual (meta em andamento).
        """
        qtd = self.rng.randint(3, 4)
        nomes = self.rng.sample(list(_METAS_MODELO.keys()), k=qtd)
        if "Reserva de emergência" not in nomes and self.rng.random() < 0.7:
            nomes[0] = "Reserva de emergência"

        poupanca_mensal = [max(0.0, s) for s in saldos_mensais]
        total_poupado = sum(poupanca_mensal)
        disponivel = 0.70 * total_poupado

        alvos: Dict[str, float] = {}
        progresso: Dict[str, float] = {}
        for nome in nomes:
            base, (fmin, fmax) = _METAS_MODELO[nome]
            referencia = despesa_mensal if base == "despesa" else renda
            alvos[nome] = referencia * self.rng.uniform(fmin, fmax)
            progresso[nome] = self.rng.uniform(0.20, 0.75)

        # Se a poupança real não comporta os alvos, reduz os alvos (e não o progresso),
        # mantendo metas plausíveis para o que o usuário realmente consegue guardar.
        desejado_total = sum(alvos[n] * progresso[n] for n in nomes)
        if desejado_total > disponivel > 0:
            fator = max(disponivel / desejado_total, 0.30)
            alvos = {n: v * fator for n, v in alvos.items()}
        alvos = {n: max(500.0, _arredondar(v, 100.0)) for n, v in alvos.items()}
        desejado = {n: alvos[n] * progresso[n] for n in nomes}
        escala = min(1.0, disponivel / sum(desejado.values())) if total_poupado > 0 else 0.0

        meta_ids: List[int] = []
        for nome in nomes:
            alvo = alvos[nome]
            acumulado_meta = _arredondar(desejado[nome] * escala, 10.0)
            mid = self.meta_dao.inserir(
                descricao=nome, valor_alvo=10_000_000.0, valor_atual=0.0,
                prazo="12 meses", data_limite=None, usuario_id=usuario_id,
                data_criacao=self._primeiro_dia_historico().strftime("%Y-%m-%d"),
            )
            # Distribui o acumulado nos meses proporcionalmente à poupança de cada mês
            restante_a_aportar = acumulado_meta
            meses_com_poupanca = [i for i, v in enumerate(poupanca_mensal) if v > 0]
            for pos, idx in enumerate(meses_com_poupanca):
                if restante_a_aportar <= 0:
                    break
                ultimo = pos == len(meses_com_poupanca) - 1
                parte = restante_a_aportar if ultimo else _arredondar(
                    acumulado_meta * poupanca_mensal[idx] / total_poupado * self.rng.uniform(0.8, 1.2), 10.0
                )
                parte = min(parte, restante_a_aportar)
                if parte <= 0:
                    continue
                ano, mes = _somar_meses(self.hoje.year, self.hoje.month, -(MESES_HISTORICO - 1 - idx))
                dia = min(self.rng.randint(8, 25), _ultimo_dia(ano, mes))
                if (ano, mes) == (self.hoje.year, self.hoje.month):
                    dia = min(dia, self.hoje.day)
                self.meta_dao.guardar_valor(mid, parte, date(ano, mes, dia).strftime("%Y-%m-%d"))
                restante_a_aportar = round(restante_a_aportar - parte, 2)

            atual = self.meta_dao.buscar_por_id(mid)["valor_atual"]
            alvo = max(alvo, _arredondar(atual * 1.15, 100.0) + 100.0)   # garante alvo > atual
            ritmo = max(50.0, atual / MESES_HISTORICO)
            meses_necessarios = (alvo - atual) / ritmo
            # Prazos variados: alguns folgados, outros apertados (ficam atrasados no simulador)
            desejo = meses_necessarios * self.rng.uniform(0.75, 1.5)
            prazo = min(_PRAZOS_VALIDOS, key=lambda p: abs(p - desejo))
            ano_lim, mes_lim = _somar_meses(self.hoje.year, self.hoje.month, prazo)
            data_limite = date(ano_lim, mes_lim, min(self.hoje.day, _ultimo_dia(ano_lim, mes_lim)))
            self.meta_dao.atualizar(mid, nome, alvo, f"{prazo} meses", data_limite.strftime("%d/%m/%Y"))
            meta_ids.append(mid)
        return meta_ids

    def _primeiro_dia_historico(self) -> date:
        ano, mes = _somar_meses(self.hoje.year, self.hoje.month, -(MESES_HISTORICO - 1))
        return date(ano, mes, 1)

    def _criar_historico_saude(self, usuario_id: int) -> None:
        """Registra o diagnóstico de saúde financeira de cada mês (cumulativo até o fim do mês)."""
        lancs = self.lancamento_dao.listar_todos(usuario_id)
        for i in range(2, -1, -1):  # últimos 3 meses
            ano, mes = _somar_meses(self.hoje.year, self.hoje.month, -i)
            fim = date(ano, mes, _ultimo_dia(ano, mes))
            if fim > self.hoje:
                fim = self.hoje
            ate_aqui = [l for l in lancs if l["date"] <= fim.strftime("%Y-%m-%d")]
            diag = SaudeFinanceiraController.calcular_saude(ate_aqui)
            if not diag:
                continue
            self.saude_dao.salvar_diagnostico(
                usuario_id=usuario_id,
                score=diag["score"],
                plano_acao_json=json.dumps(diag["plano_acao"], ensure_ascii=False),
                data_atualizacao=fim.strftime("%Y-%m-%d"),
            )

    def _marcar_modo_demo(self, usuario_id: int) -> None:
        conn = self.db.get_connection()
        conn.execute("UPDATE usuarios SET modo_demo = 1 WHERE id = ?", (usuario_id,))
        conn.commit()
