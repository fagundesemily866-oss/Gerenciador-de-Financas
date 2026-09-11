"""
Camada de Modelo (Model) da aplicação.

Contém:
    - Transaction: estrutura de dados que representa uma transação financeira.
    - TransactionModel: repositório responsável pelas operações de
      persistência (CRUD) da entidade Transaction no banco de dados.
"""
from dataclasses import dataclass
from typing import List, Optional

from models.database import Database


@dataclass
class Transaction:
    """Representa uma única transação financeira (receita ou despesa)."""

    description: str
    value: float
    type: str       # 'Receita' ou 'Despesa'
    category: str
    date: str        # formato ISO: 'AAAA-MM-DD'
    id: Optional[int] = None


class TransactionModel:
    """Repositório responsável pela persistência de objetos Transaction."""

    # Constantes de domínio, centralizadas aqui para serem reutilizadas
    # tanto pelo Controller (validação) quanto pela View (comboboxes).
    TYPES = ("Receita", "Despesa")
    CATEGORIES = (
        "Alimentação",
        "Transporte",
        "Moradia",
        "Lazer",
        "Saúde",
        "Educação",
        "Salário",
        "Outros",
    )

    def __init__(self, database: Database):
        self.database = database

    # ------------------------------------------------------------------
    # Operações de escrita
    # ------------------------------------------------------------------
    def add(self, transaction: Transaction) -> int:
        """Insere uma nova transação e retorna o ID gerado."""
        connection = self.database.get_connection()
        cursor = connection.execute(
            """
            INSERT INTO transactions (description, value, type, category, date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                transaction.description,
                transaction.value,
                transaction.type,
                transaction.category,
                transaction.date,
            ),
        )
        connection.commit()
        return cursor.lastrowid

    def update(self, transaction: Transaction) -> None:
        """Atualiza uma transação existente com base no seu ID."""
        if transaction.id is None:
            raise ValueError("Não é possível atualizar uma transação sem ID.")

        connection = self.database.get_connection()
        connection.execute(
            """
            UPDATE transactions
            SET description = ?, value = ?, type = ?, category = ?, date = ?
            WHERE id = ?
            """,
            (
                transaction.description,
                transaction.value,
                transaction.type,
                transaction.category,
                transaction.date,
                transaction.id,
            ),
        )
        connection.commit()

    def delete(self, transaction_id: int) -> None:
        """Remove uma transação pelo ID."""
        connection = self.database.get_connection()
        connection.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        connection.commit()

    # ------------------------------------------------------------------
    # Operações de leitura
    # ------------------------------------------------------------------
    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Busca uma transação específica pelo ID. Retorna None se não existir."""
        connection = self.database.get_connection()
        row = connection.execute(
            "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
        ).fetchone()
        return self._row_to_transaction(row) if row else None

    def get_all(
        self,
        type_filter: Optional[str] = None,
        category_filter: Optional[str] = None,
    ) -> List[Transaction]:
        """
        Retorna todas as transações, podendo ser filtradas por tipo e/ou
        categoria. Os valores 'Todos' e 'Todas' são tratados como "sem filtro".
        """
        connection = self.database.get_connection()
        query = "SELECT * FROM transactions WHERE 1=1"
        params: list = []

        if type_filter and type_filter != "Todos":
            query += " AND type = ?"
            params.append(type_filter)

        if category_filter and category_filter != "Todas":
            query += " AND category = ?"
            params.append(category_filter)

        query += " ORDER BY date DESC, id DESC"

        rows = connection.execute(query, params).fetchall()
        return [self._row_to_transaction(row) for row in rows]

    @staticmethod
    def _row_to_transaction(row) -> Transaction:
        """Converte uma linha (sqlite3.Row) em um objeto Transaction."""
        return Transaction(
            id=row["id"],
            description=row["description"],
            value=row["value"],
            type=row["type"],
            category=row["category"],
            date=row["date"],
        )
