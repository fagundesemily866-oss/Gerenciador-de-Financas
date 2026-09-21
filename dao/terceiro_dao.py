"""
DAO (Data Access Object) de Terceiros.

Responsável por operações de persistência e consulta na tabela 'terceiros' do SQLite.
"""
from datetime import date
from typing import List, Optional, Dict, Any
from models.database import Database
from models.terceiro import Terceiro


class TerceiroDAO:
    """Gerencia o acesso a dados da entidade Terceiro."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def inserir(
        self,
        nome: str,
        relacao: str,
        data_criacao: Optional[str] = None,
        usuario_id: Optional[int] = None,
    ) -> int:
        """Insere um novo terceiro e retorna o ID gerado."""
        data_criacao = data_criacao or date.today().strftime("%Y-%m-%d")
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO terceiros (usuario_id, nome, relacao, data_criacao)
            VALUES (?, ?, ?, ?)
            """,
            (usuario_id, nome.strip(), relacao.strip(), data_criacao),
        )
        conn.commit()
        return cursor.lastrowid

    def buscar_por_id(self, terceiro_id: int) -> Optional[Dict[str, Any]]:
        """Busca um terceiro pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT id, usuario_id, nome, relacao, data_criacao FROM terceiros WHERE id = ?",
            (terceiro_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def listar_todos(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna todos os terceiros cadastrados."""
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, nome, relacao, data_criacao
                FROM terceiros
                WHERE usuario_id = ? OR usuario_id IS NULL
                ORDER BY nome ASC
                """,
                (usuario_id,),
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, nome, relacao, data_criacao
                FROM terceiros
                ORDER BY nome ASC
                """
            )
        return [dict(row) for row in cursor.fetchall()]

    def atualizar(self, terceiro_id: int, nome: str, relacao: str) -> bool:
        """Atualiza informações do terceiro."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            UPDATE terceiros
            SET nome = ?, relacao = ?
            WHERE id = ?
            """,
            (nome.strip(), relacao.strip(), terceiro_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def excluir(self, terceiro_id: int) -> bool:
        """Exclui um terceiro pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM terceiros WHERE id = ?", (terceiro_id,))
        conn.commit()
        return cursor.rowcount > 0

    def existe_dados(self, usuario_id: Optional[int] = None) -> bool:
        """Verifica se existem terceiros cadastrados."""
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                "SELECT COUNT(*) AS total FROM terceiros WHERE usuario_id = ? OR usuario_id IS NULL",
                (usuario_id,),
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) AS total FROM terceiros")
        return cursor.fetchone()["total"] > 0
