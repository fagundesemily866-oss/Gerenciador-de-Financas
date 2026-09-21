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
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT    NOT NULL,
                value       REAL    NOT NULL,
                type        TEXT    NOT NULL CHECK (type IN ('Receita', 'Despesa')),
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS usuarios (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                nome         TEXT    NOT NULL,
                email        TEXT    NOT NULL UNIQUE,
                senha_hash   TEXT    NOT NULL,
                tipo_perfil  TEXT    NOT NULL DEFAULT 'PF',
                data_criacao TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS categorias (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id       INTEGER,
                nome             TEXT    NOT NULL,
                tipo             TEXT    NOT NULL,
                escopo           TEXT,
                limite_orcamento REAL    DEFAULT 0.0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS metas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id  INTEGER,
                descricao   TEXT    NOT NULL,
                valor_alvo  REAL    NOT NULL,
                valor_atual REAL    DEFAULT 0.0,
                prazo       TEXT,
                data_limite TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS terceiros (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id   INTEGER,
                nome         TEXT    NOT NULL,
                relacao      TEXT    NOT NULL,
                data_criacao TEXT    NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS saude_financeira (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id       INTEGER,
                score            INTEGER NOT NULL,
                plano_acao_json  TEXT,
                data_atualizacao TEXT    NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            );
            """
        )
        connection.commit()

    def close(self) -> None:
        """Encerra a conexão com o banco de dados, se estiver aberta."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
