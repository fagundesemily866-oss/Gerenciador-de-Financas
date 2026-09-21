"""
DAO (Data Access Object) de Metas Financeiras.

Responsável por operações de persistência e consulta na tabela 'metas' do SQLite.
"""
from typing import List, Optional, Dict, Any
from models.database import Database
from models.meta import Meta


class MetaDAO:
    """Gerencia o acesso a dados da entidade Meta."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def inserir(
        self,
        descricao: str,
        valor_alvo: float,
        valor_atual: float = 0.0,
        prazo: Optional[str] = None,
        data_limite: Optional[str] = None,
        usuario_id: Optional[int] = None,
    ) -> int:
        """Insere uma nova meta financeira e retorna o ID gerado."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO metas (usuario_id, descricao, valor_alvo, valor_atual, prazo, data_limite)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                usuario_id,
                descricao.strip(),
                float(valor_alvo),
                float(valor_atual),
                prazo,
                data_limite,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def buscar_por_id(self, meta_id: int) -> Optional[Dict[str, Any]]:
        """Busca uma meta pelo seu ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            SELECT id, usuario_id, descricao, valor_alvo, valor_atual, prazo, data_limite
            FROM metas WHERE id = ?
            """,
            (meta_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def listar_todas(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna todas as metas, opcionalmente filtrando por usuário."""
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, descricao, valor_alvo, valor_atual, prazo, data_limite
                FROM metas
                WHERE usuario_id = ? OR usuario_id IS NULL
                ORDER BY id DESC
                """,
                (usuario_id,),
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, descricao, valor_alvo, valor_atual, prazo, data_limite
                FROM metas
                ORDER BY id DESC
                """
            )
        return [dict(row) for row in cursor.fetchall()]

    def atualizar(
        self,
        meta_id: int,
        descricao: str,
        valor_alvo: float,
        prazo: Optional[str],
        data_limite: Optional[str],
    ) -> bool:
        """Atualiza informações de uma meta."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            UPDATE metas
            SET descricao = ?, valor_alvo = ?, prazo = ?, data_limite = ?
            WHERE id = ?
            """,
            (descricao.strip(), float(valor_alvo), prazo, data_limite, meta_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def guardar_valor(self, meta_id: int, quantia: float) -> bool:
        """Incrementa o valor atual poupado na meta."""
        if quantia <= 0:
            return False
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            UPDATE metas
            SET valor_atual = valor_atual + ?
            WHERE id = ?
            """,
            (float(quantia), meta_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def excluir(self, meta_id: int) -> bool:
        """Exclui uma meta pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM metas WHERE id = ?", (meta_id,))
        conn.commit()
        return cursor.rowcount > 0

    def existe_dados(self, usuario_id: Optional[int] = None) -> bool:
        """Verifica se existem metas cadastradas."""
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                "SELECT COUNT(*) AS total FROM metas WHERE usuario_id = ? OR usuario_id IS NULL",
                (usuario_id,),
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) AS total FROM metas")
        return cursor.fetchone()["total"] > 0
