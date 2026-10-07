"""
DAO (Data Access Object) de Lançamentos.

Responsável por gravar e consultar os lançamentos (receitas/despesas)
na tabela 'transactions' do SQLite (ver models/database.py).

Cada lançamento pertence a um usuário. Quando nenhum 'usuario_id' é informado,
usa-se o usuário logado (services.sessao); sem sessão ativa (ex.: testes) não há
filtro por usuário, preservando o comportamento anterior.
"""
from typing import List, Optional, Dict, Any
from models.database import Database
from services.sessao import resolver_usuario

_COLUNAS = "id, description, value, type, category, date, usuario_id, status, terceiro_id"


class LancamentoDAO:
    """Gerencia o acesso a dados dos lançamentos/transações."""

    def __init__(self, db: Optional[Database] = None):
        # Permite injetar um Database já existente (útil em testes)
        self.db = db or Database()

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------
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
        cursor = conn.execute(
            """
            INSERT INTO transactions (description, value, type, category, date, usuario_id, status, terceiro_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (descricao.strip(), float(valor), tipo, categoria.strip(), data, usuario_id, status, terceiro_id),
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
        cursor = conn.execute(
            """
            UPDATE transactions
            SET description = ?, value = ?, type = ?, category = ?, date = ?
            WHERE id = ?
            """,
            (descricao.strip(), float(valor), tipo, categoria.strip(), data, lancamento_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def excluir(self, lancamento_id: int) -> bool:
        """Exclui um lançamento pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM transactions WHERE id = ?", (lancamento_id,))
        conn.commit()
        return cursor.rowcount > 0

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------
    def buscar_por_id(self, lancamento_id: int) -> Optional[Dict[str, Any]]:
        """Busca um lançamento pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            f"SELECT {_COLUNAS} FROM transactions WHERE id = ?",
            (lancamento_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def _listar(self, filtro_sql: str = "", params: tuple = (), usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        usuario_id = resolver_usuario(usuario_id)
        condicoes = [filtro_sql] if filtro_sql else []
        parametros = list(params)
        if usuario_id is not None:
            condicoes.append("usuario_id = ?")
            parametros.append(usuario_id)
        where = f"WHERE {' AND '.join(condicoes)}" if condicoes else ""
        conn = self.db.get_connection()
        cursor = conn.execute(
            f"SELECT {_COLUNAS} FROM transactions {where} ORDER BY date ASC, id ASC",
            tuple(parametros),
        )
        return [dict(linha) for linha in cursor.fetchall()]

    def listar_todos(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna os lançamentos (do usuário logado) como lista de dicts ordenados por data."""
        return self._listar(usuario_id=usuario_id)

    def listar_por_tipo(self, tipo: str, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna lançamentos filtrados por tipo ('Receita' ou 'Despesa')."""
        return self._listar("type = ?", (tipo,), usuario_id)

    def listar_por_categoria(self, categoria: str, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna lançamentos filtrados por categoria."""
        return self._listar("category = ?", (categoria.strip(),), usuario_id)

    def existe_dados(self, usuario_id: Optional[int] = None) -> bool:
        """True se já existir pelo menos um lançamento cadastrado."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                "SELECT COUNT(*) AS total FROM transactions WHERE usuario_id = ?", (usuario_id,)
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) AS total FROM transactions")
        return cursor.fetchone()["total"] > 0
