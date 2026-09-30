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

            CREATE TABLE IF NOT EXISTS simulacoes (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id       INTEGER,
                nome             TEXT    NOT NULL,
                descricao        TEXT,
                parametros_json  TEXT    NOT NULL,
                resultados_json  TEXT,
                data_criacao     TEXT    NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS meta_aportes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                meta_id     INTEGER NOT NULL,
                valor       REAL    NOT NULL,
                data        TEXT    NOT NULL,
                FOREIGN KEY (meta_id) REFERENCES metas (id) ON DELETE CASCADE
            );
            """
        )
        connection.commit()
        self._apply_migrations(connection)

    def _apply_migrations(self, connection: sqlite3.Connection) -> None:
        """Aplica alterações incrementais nas tabelas existentes preservando os dados."""
        # 1. Tabela usuarios: foto_perfil e renda_mensal
        cursor = connection.execute("PRAGMA table_info(usuarios)")
        colunas_usuarios = [row["name"] for row in cursor.fetchall()]
        if "foto_perfil" not in colunas_usuarios:
            connection.execute("ALTER TABLE usuarios ADD COLUMN foto_perfil TEXT")
        if "renda_mensal" not in colunas_usuarios:
            connection.execute("ALTER TABLE usuarios ADD COLUMN renda_mensal REAL DEFAULT 0.0")

        # 2. Tabela terceiros: foto_perfil
        cursor = connection.execute("PRAGMA table_info(terceiros)")
        colunas_terceiros = [row["name"] for row in cursor.fetchall()]
        if "foto_perfil" not in colunas_terceiros:
            connection.execute("ALTER TABLE terceiros ADD COLUMN foto_perfil TEXT")

        # 3. Tabela metas: concluida, data_conclusao, celebracao_exibida
        cursor = connection.execute("PRAGMA table_info(metas)")
        colunas_metas = [row["name"] for row in cursor.fetchall()]
        if "concluida" not in colunas_metas:
            connection.execute("ALTER TABLE metas ADD COLUMN concluida INTEGER DEFAULT 0")
        if "data_conclusao" not in colunas_metas:
            connection.execute("ALTER TABLE metas ADD COLUMN data_conclusao TEXT")
        if "celebracao_exibida" not in colunas_metas:
            connection.execute("ALTER TABLE metas ADD COLUMN celebracao_exibida INTEGER DEFAULT 0")

        connection.commit()

    def close(self) -> None:
        """Encerra a conexão com o banco de dados, se estiver aberta."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
