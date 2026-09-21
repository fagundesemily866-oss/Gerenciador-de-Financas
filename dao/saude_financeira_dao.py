"""
DAO (Data Access Object) de Saúde Financeira.

Responsável por registrar diagnósticos e histórico da saúde financeira
na tabela 'saude_financeira' do SQLite.
"""
from datetime import date
from typing import List, Optional, Dict, Any
from models.database import Database
from models.saude_financeira import SaudeFinanceira


class SaudeFinanceiraDAO:
    """Gerencia o acesso a dados da entidade SaudeFinanceira."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def salvar_diagnostico(
        self,
        usuario_id: Optional[int],
        score: int,
        plano_acao_json: str,
        data_atualizacao: Optional[str] = None,
    ) -> int:
        """Registra uma nova avaliação de saúde financeira."""
        data_atualizacao = data_atualizacao or date.today().strftime("%Y-%m-%d")
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO saude_financeira (usuario_id, score, plano_acao_json, data_atualizacao)
            VALUES (?, ?, ?, ?)
            """,
            (usuario_id, int(score), plano_acao_json, data_atualizacao),
        )
        conn.commit()
        return cursor.lastrowid

    def buscar_ultima_por_usuario(
        self, usuario_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Retorna o registro mais recente de saúde financeira do usuário."""
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, score, plano_acao_json, data_atualizacao
                FROM saude_financeira
                WHERE usuario_id = ?
                ORDER BY id DESC LIMIT 1
                """,
                (usuario_id,),
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, score, plano_acao_json, data_atualizacao
                FROM saude_financeira
                ORDER BY id DESC LIMIT 1
                """
            )
        row = cursor.fetchone()
        return dict(row) if row else None

    def listar_historico(
        self, usuario_id: Optional[int] = None, limite: int = 10
    ) -> List[Dict[str, Any]]:
        """Retorna o histórico de avaliações de saúde financeira."""
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, score, plano_acao_json, data_atualizacao
                FROM saude_financeira
                WHERE usuario_id = ?
                ORDER BY data_atualizacao DESC, id DESC
                LIMIT ?
                """,
                (usuario_id, limite),
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, score, plano_acao_json, data_atualizacao
                FROM saude_financeira
                ORDER BY data_atualizacao DESC, id DESC
                LIMIT ?
                """,
                (limite,),
            )
        return [dict(row) for row in cursor.fetchall()]

    def excluir(self, saude_id: int) -> bool:
        """Exclui um registro de saúde financeira pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM saude_financeira WHERE id = ?", (saude_id,))
        conn.commit()
        return cursor.rowcount > 0

    def existe_dados(self, usuario_id: Optional[int] = None) -> bool:
        """Verifica se há avaliações registradas."""
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                "SELECT COUNT(*) AS total FROM saude_financeira WHERE usuario_id = ?",
                (usuario_id,),
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) AS total FROM saude_financeira")
        return cursor.fetchone()["total"] > 0
