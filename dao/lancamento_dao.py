"""
DAO (Data Access Object) de Lançamentos — MySQL.

Tabela: lancamento (FK id_categoria → categoria)
Mapeamento: tipo 'Receita'↔'RECEITA', status 'Pago'↔'PAGO' etc.

A interface pública continua recebendo o *nome* da categoria (string).
Internamente o DAO faz o lookup para id_categoria no INSERT e JOIN no SELECT.
"""
from typing import List, Optional, Dict, Any
from models.database import Database
from services.sessao import resolver_usuario


# --------------- helpers de conversão ---------------
def _tipo_db(t: str) -> str:
    return t.upper() if t else "DESPESA"

def _tipo_app(t: str) -> str:
    return t.capitalize() if t else "Despesa"

def _status_db(s: Optional[str]) -> Optional[str]:
    return s.upper() if s else None

def _status_app(s: Optional[str]) -> Optional[str]:
    return s.capitalize() if s else None

def _row(r: Optional[Dict]) -> Optional[Dict]:
    if r is None:
        return None
    if "type" in r and r["type"]:
        r["type"] = _tipo_app(r["type"])
    if "status" in r and r["status"]:
        r["status"] = _status_app(r["status"])
    return r


_SELECT = """
    l.id_lancamento  AS id,
    l.descricao      AS description,
    l.valor          AS value,
    l.tipo           AS type,
    c.nome           AS category,
    l.data_vencimento AS date,
    l.id_usuario     AS usuario_id,
    l.status,
    l.id_terceiro    AS terceiro_id
"""
_FROM = "lancamento l LEFT JOIN categoria c ON l.id_categoria = c.id_categoria"


class LancamentoDAO:
    """Gerencia o acesso a dados dos lançamentos/transações."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------
    def _resolver_categoria(self, conn, nome_categoria: str, usuario_id: Optional[int]) -> int:
        """Busca id_categoria pelo nome. Cria a categoria se não existir."""
        cursor = conn.execute(
            "SELECT id_categoria FROM categoria WHERE nome = %s AND id_usuario = %s LIMIT 1",
            (nome_categoria.strip(), usuario_id),
        )
        row = cursor.fetchone()
        if row:
            return row["id_categoria"]
        # Categoria não existe: cria automaticamente como Despesa/Pessoal
        cursor = conn.execute(
            """
            INSERT INTO categoria (id_usuario, nome, tipo, escopo, limite_orcamento)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (usuario_id, nome_categoria.strip(), "DESPESA", "PESSOAL", 0.0),
        )
        return cursor.lastrowid

    def inserir(
        self,
        descricao: str,
        valor: float,
        tipo: str,
        categoria: str,
        data: str,
        usuario_id: Optional[int] = None,
        status: Optional[str] = None,
        terceiro_id: Optional[int] = None,
    ) -> int:
        """Insere um novo lançamento. 'tipo' deve ser 'Receita' ou 'Despesa'."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        id_categoria = self._resolver_categoria(conn, categoria, usuario_id)
        cursor = conn.execute(
            """
            INSERT INTO lancamento
                (id_usuario, id_categoria, id_terceiro, tipo, valor,
                 descricao, status, data_vencimento)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                usuario_id,
                id_categoria,
                terceiro_id,
                _tipo_db(tipo),
                float(valor),
                descricao.strip(),
                _status_db(status) or "PENDENTE",
                data,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def atualizar(
        self,
        lancamento_id: int,
        descricao: str,
        valor: float,
        tipo: str,
        categoria: str,
        data: str,
    ) -> bool:
        """Atualiza os dados de um lançamento existente."""
        conn = self.db.get_connection()
        # Busca usuario_id do lançamento para resolver a categoria
        cur_usr = conn.execute(
            "SELECT id_usuario FROM lancamento WHERE id_lancamento = %s", (lancamento_id,)
        )
        row_usr = cur_usr.fetchone()
        uid = row_usr["id_usuario"] if row_usr else None
        id_categoria = self._resolver_categoria(conn, categoria, uid)
        cursor = conn.execute(
            """
            UPDATE lancamento
            SET descricao = %s, valor = %s, tipo = %s, id_categoria = %s, data_vencimento = %s
            WHERE id_lancamento = %s
            """,
            (descricao.strip(), float(valor), _tipo_db(tipo), id_categoria, data, lancamento_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def excluir(self, lancamento_id: int) -> bool:
        """Exclui um lançamento pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM lancamento WHERE id_lancamento = %s", (lancamento_id,))
        conn.commit()
        return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------
    def buscar_por_id(self, lancamento_id: int) -> Optional[Dict[str, Any]]:
        """Busca um lançamento pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            f"SELECT {_SELECT} FROM {_FROM} WHERE l.id_lancamento = %s",
            (lancamento_id,),
        )
        return _row(cursor.fetchone())

    def _listar(self, filtro_sql: str = "", params: tuple = (), usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        usuario_id = resolver_usuario(usuario_id)
        condicoes = [filtro_sql] if filtro_sql else []
        parametros = list(params)
        if usuario_id is not None:
            condicoes.append("l.id_usuario = %s")
            parametros.append(usuario_id)
        where = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
        conn = self.db.get_connection()
        cursor = conn.execute(
            f"SELECT {_SELECT} FROM {_FROM} {where} ORDER BY l.data_vencimento ASC, l.id_lancamento ASC",
            tuple(parametros),
        )
        return [_row(r) for r in cursor.fetchall()]

    def listar_todos(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna os lançamentos (do usuário logado) como lista de dicts ordenados por data."""
        return self._listar(usuario_id=usuario_id)

    def listar_por_tipo(self, tipo: str, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna lançamentos filtrados por tipo ('Receita' ou 'Despesa')."""
        return self._listar("l.tipo = %s", (_tipo_db(tipo),), usuario_id)

    def listar_por_categoria(self, categoria: str, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna lançamentos filtrados por categoria."""
        return self._listar("c.nome = %s", (categoria.strip(),), usuario_id)

    def existe_dados(self, usuario_id: Optional[int] = None) -> bool:
        """True se já existir pelo menos um lançamento cadastrado."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                "SELECT COUNT(*) AS total FROM lancamento WHERE id_usuario = %s", (usuario_id,)
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) AS total FROM lancamento")
        return cursor.fetchone()["total"] > 0
