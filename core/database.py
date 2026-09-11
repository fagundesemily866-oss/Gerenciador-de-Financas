"""
Camada de infraestrutura de dados.

Responsável por abrir/gerenciar a conexão com o banco de dados SQLite
e garantir que o schema (estrutura de tabelas) exista antes de qualquer uso.
"""
import os
import sqlite3
from typing import Optional


class Database:
    """Gerencia a conexão e a estrutura do banco de dados SQLite."""

    def __init__(self, db_path: str = "data/finance.db"):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
        self._ensure_directory_exists()
        self._create_schema()

    def _ensure_directory_exists(self) -> None:
        """Cria o diretório do banco de dados caso ele ainda não exista."""
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """
        Retorna a conexão ativa com o banco de dados.
        A conexão é criada de forma "lazy" (apenas na primeira chamada).
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.execute("PRAGMA foreign_keys = ON")
            # Permite acessar colunas por nome (ex.: row["description"])
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def _create_schema(self) -> None:
        """Cria as tabelas necessárias caso ainda não existam."""
        connection = self.get_connection()
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT    NOT NULL,
                value       REAL    NOT NULL,
                type        TEXT    NOT NULL CHECK (type IN ('Receita', 'Despesa')),
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL
            )
            """
        )
        connection.commit()

    def close(self) -> None:
        """Encerra a conexão com o banco de dados, se estiver aberta."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
