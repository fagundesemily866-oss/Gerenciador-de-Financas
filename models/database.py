"""
Camada de infraestrutura de dados — MySQL.
==========================================

Responsável por abrir/gerenciar a conexão com o banco de dados MySQL
``gerenciador_financeiro`` e garantir que tabelas auxiliares do app existam.

Configuração via variáveis de ambiente (.env):
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
"""
import os
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

import mysql.connector


# ======================================================================
# Conversão de tipos MySQL → tipos Python compatíveis com a interface
# que as views esperam (strings para datas, float para decimais).
# ======================================================================

def _convert_row(row):
    """Converte uma linha (dict) retornada pelo MySQL para tipos Python simples."""
    if row is None:
        return None
    result = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            result[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, date):
            result[key] = value.strftime("%Y-%m-%d")
        elif isinstance(value, Decimal):
            result[key] = float(value)
        elif isinstance(value, (bytearray, bytes)):
            result[key] = value.decode("utf-8")
        else:
            result[key] = value
    return result


class _CursorProxy:
    """Proxy que converte tipos e devolve dicts (mesma interface do sqlite3.Row)."""

    def __init__(self, cursor):
        self._cursor = cursor

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def fetchone(self):
        row = self._cursor.fetchone()
        return _convert_row(row)

    def fetchall(self):
        return [_convert_row(r) for r in self._cursor.fetchall()]


class _ConnectionProxy:
    """Wrapper que expõe conn.execute()/conn.commit() no estilo SQLite."""

    def __init__(self, mysql_conn):
        self._conn = mysql_conn

    def execute(self, query, params=None):
        cursor = self._conn.cursor(dictionary=True, buffered=True)
        cursor.execute(query, params or ())
        return _CursorProxy(cursor)

    def commit(self):
        self._conn.commit()
        Database._versao_contador += 1

    def rollback(self):
        """Reverte mudanças não confirmadas (exclusões compostas de conta)."""
        self._conn.rollback()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass


class Database:
    """Gerencia a conexão com o banco de dados MySQL."""

    _versao_contador: int = 0

    def __init__(self):
        self._proxy: Optional[_ConnectionProxy] = None

    # ------------------------------------------------------------------
    # Conexão
    # ------------------------------------------------------------------
    @staticmethod
    def _params() -> dict:
        return dict(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            charset="utf8mb4",
        )

    @staticmethod
    def _nome_banco() -> str:
        return os.getenv("MYSQL_DATABASE", "gerenciador_financeiro")

    @classmethod
    def _criar_banco_se_necessario(cls) -> None:
        """Cria o schema (database) caso ele ainda não exista no servidor."""
        raw = mysql.connector.connect(**cls._params())
        try:
            nome = cls._nome_banco().replace("`", "")
            cur = raw.cursor()
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{nome}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            raw.commit()
        finally:
            raw.close()

    @staticmethod
    def _configurar_sessao(raw) -> None:
        """Faz cada consulta enxergar o que já foi gravado por outras conexões.

        Cada DAO abre a sua própria conexão. No isolamento padrão do MySQL
        (REPEATABLE READ) uma conexão que já leu dados continua vendo o "retrato"
        antigo do banco até dar commit — então uma meta/lançamento criado em outra
        tela não aparecia no Simulador. Com READ COMMITTED cada SELECT lê o dado
        mais recente já confirmado.
        """
        cur = raw.cursor()
        try:
            cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
        finally:
            cur.close()

    @classmethod
    def _connect(cls):
        try:
            raw = mysql.connector.connect(
                database=cls._nome_banco(), autocommit=False, **cls._params()
            )
        except mysql.connector.Error as exc:
            if getattr(exc, "errno", None) != 1049:  # 1049 = banco desconhecido
                raise
            cls._criar_banco_se_necessario()
            raw = mysql.connector.connect(
                database=cls._nome_banco(), autocommit=False, **cls._params()
            )
        cls._configurar_sessao(raw)
        return raw

    def get_connection(self) -> _ConnectionProxy:
        """Retorna a conexão ativa, reconectando se necessário."""
        if self._proxy is not None:
            try:
                self._proxy._conn.ping(reconnect=False)
            except Exception:
                self._proxy = None
        if self._proxy is None:
            raw = self._connect()
            self._proxy = _ConnectionProxy(raw)
            self._ensure_schema()
            self._ensure_extras()
        return self._proxy

    # ------------------------------------------------------------------
    # Estrutura principal (usuario, categoria, lancamento, meta_reserva...)
    # ------------------------------------------------------------------
    @staticmethod
    def _comandos_ddl() -> list:
        """Lê migrations/ddl/*.sql e devolve os CREATE TABLE de forma idempotente."""
        raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pasta = os.path.join(raiz, "migrations", "ddl")
        if not os.path.isdir(pasta):
            return []
        comandos = []
        for nome in sorted(os.listdir(pasta)):
            if not nome.lower().endswith(".sql"):
                continue
            with open(os.path.join(pasta, nome), encoding="utf-8") as fh:
                texto = fh.read()
            texto = re.sub(r"--[^\n]*", "", texto)  # remove comentários de linha
            for cmd in texto.split(";"):
                cmd = cmd.strip()
                if not cmd or re.match(r"(?i)^(CREATE\s+DATABASE|USE)\b", cmd):
                    continue
                cmd = re.sub(
                    r"(?i)^CREATE\s+TABLE\s+(?!IF\s+NOT\s+EXISTS)",
                    "CREATE TABLE IF NOT EXISTS ",
                    cmd,
                )
                comandos.append(cmd)
        return comandos

    def _ensure_schema(self):
        """Garante que as tabelas existam — contas e dados persistem sem passo manual."""
        conn = self._proxy
        for cmd in self._comandos_ddl():
            conn.execute(cmd)
        conn.commit()

    # ------------------------------------------------------------------
    # Tabelas auxiliares que o app precisa mas não estão no DDL original
    # ------------------------------------------------------------------
    def _ensure_extras(self):
        conn = self._proxy

        # meta_aporte — histórico de aportes em metas
        conn.execute("""
            CREATE TABLE IF NOT EXISTS meta_aporte (
                id_aporte    INT AUTO_INCREMENT,
                id_meta      INT NOT NULL,
                valor        DECIMAL(10,2) NOT NULL,
                data_aporte  DATE NOT NULL,
                PRIMARY KEY (id_aporte),
                FOREIGN KEY (id_meta) REFERENCES meta_reserva(id_meta) ON DELETE CASCADE
            )
        """)

        # simulacao — cenários do simulador
        conn.execute("""
            CREATE TABLE IF NOT EXISTS simulacao (
                id_simulacao    INT AUTO_INCREMENT,
                id_usuario      INT NOT NULL,
                nome            VARCHAR(100) NOT NULL,
                descricao       VARCHAR(255),
                parametros_json JSON,
                resultados_json JSON,
                criado_em       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id_simulacao),
                FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
            )
        """)

        # modo_demo em usuario (pode já existir; ignora o erro se existir)
        try:
            cursor = conn.execute("""
                SELECT COUNT(*) AS cnt
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME   = 'usuario'
                  AND COLUMN_NAME  = 'modo_demo'
            """)
            if cursor.fetchone()["cnt"] == 0:
                conn.execute(
                    "ALTER TABLE usuario ADD COLUMN modo_demo BOOLEAN NOT NULL DEFAULT FALSE"
                )
        except Exception:
            pass

        # Migração não destrutiva: categorias utilizadas continuam associadas
        # aos lançamentos, mas podem sumir das listas após arquivamento.
        ativo = conn.execute("""
            SELECT COUNT(*) AS total FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'categoria'
              AND COLUMN_NAME = 'ativa'
        """).fetchone()["total"]
        if not ativo:
            conn.execute(
                "ALTER TABLE categoria ADD COLUMN ativa BOOLEAN NOT NULL DEFAULT TRUE"
            )
        conn.commit()

    # ------------------------------------------------------------------
    # Versão de dados (para saber se as views precisam recarregar)
    # ------------------------------------------------------------------
    @staticmethod
    def versao_dados(**_kwargs) -> Optional[tuple]:
        """Retorna um identificador que muda a cada commit."""
        return (Database._versao_contador,)

    def close(self) -> None:
        """Encerra a conexão com o banco de dados."""
        if self._proxy is not None:
            self._proxy.close()
            self._proxy = None
