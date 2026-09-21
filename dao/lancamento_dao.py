"""
DAO (Data Access Object) de Lançamentos.

Responsável por gravar e consultar os lançamentos (receitas/despesas)
na tabela 'transactions' do SQLite (ver models/database.py).

É essa camada que dá "vida real" aos dados: sem ela, os lançamentos
digitados na tela nunca eram salvos em lugar nenhum.
"""
from typing import List, Optional, Dict, Any
from models.database import Database


class LancamentoDAO:
    """Gerencia o acesso a dados dos lançamentos/transações."""

    def __init__(self, db: Optional[Database] = None):
        # Permite injetar um Database já existente (útil em testes)
        self.db = db or Database()

    def inserir(
        self,
        descricao: str,
        valor: float,
        tipo: str,
        categoria: str,
        data: str,
    ) -> int:
        """Insere um novo lançamento. 'tipo' deve ser 'Receita' ou 'Despesa'."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO transactions (description, value, type, category, date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (descricao.strip(), float(valor), tipo, categoria.strip(), data),
        )
        conn.commit()
        return cursor.lastrowid

    def buscar_por_id(self, lancamento_id: int) -> Optional[Dict[str, Any]]:
        """Busca um lançamento pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            SELECT id, description, value, type, category, date
            FROM transactions WHERE id = ?
            """,
            (lancamento_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def listar_todos(self) -> List[Dict[str, Any]]:
        """Retorna todos os lançamentos como lista de dicts ordenados por data."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            SELECT id, description, value, type, category, date
            FROM transactions ORDER BY date ASC
            """
        )
        return [dict(linha) for linha in cursor.fetchall()]

    def listar_por_tipo(self, tipo: str) -> List[Dict[str, Any]]:
        """Retorna lançamentos filtrados por tipo ('Receita' ou 'Despesa')."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            SELECT id, description, value, type, category, date
            FROM transactions
            WHERE type = ?
            ORDER BY date ASC
            """,
            (tipo,),
        )
        return [dict(linha) for linha in cursor.fetchall()]

    def listar_por_categoria(self, categoria: str) -> List[Dict[str, Any]]:
        """Retorna lançamentos filtrados por categoria."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            SELECT id, description, value, type, category, date
            FROM transactions
            WHERE category = ?
            ORDER BY date ASC
            """,
            (categoria.strip(),),
        )
        return [dict(linha) for linha in cursor.fetchall()]

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

    def existe_dados(self) -> bool:
        """True se já existir pelo menos um lançamento cadastrado."""
        conn = self.db.get_connection()
        cursor = conn.execute("SELECT COUNT(*) AS total FROM transactions")
        return cursor.fetchone()["total"] > 0
