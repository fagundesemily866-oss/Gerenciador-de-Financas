"""
DAO (Data Access Object) de Saúde Financeira — MySQL.

Tabela: saude_financeira
"""
from datetime import date
from typing import List, Optional, Dict, Any
from models.database import Database
from services.sessao import resolver_usuario
from models.saude_financeira import SaudeFinanceira


_SELECT = """
    id_saude          AS id,
    id_usuario        AS usuario_id,
    score,
    plano_acao_json,
    data_calculo      AS data_atualizacao
"""


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
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO saude_financeira (id_usuario, score, plano_acao_json, data_calculo)
            VALUES (%s, %s, %s, %s)
            """,
            (usuario_id, int(score), plano_acao_json, data_atualizacao),
        )
        conn.commit()
        return cursor.lastrowid

    def buscar_ultima_por_usuario(
        self, usuario_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Retorna o registro mais recente de saúde financeira do usuário."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                f"""
                SELECT {_SELECT} FROM saude_financeira
                WHERE id_usuario = %s
                ORDER BY id_saude DESC LIMIT 1
                """,
                (usuario_id,),
            )
        else:
            cursor = conn.execute(
                f"""
                SELECT {_SELECT} FROM saude_financeira
                ORDER BY id_saude DESC LIMIT 1
                """
            )
        return cursor.fetchone()

    def listar_historico(
        self, usuario_id: Optional[int] = None, limite: int = 10
    ) -> List[Dict[str, Any]]:
        """Retorna o histórico de avaliações de saúde financeira."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                f"""
                SELECT {_SELECT} FROM saude_financeira
                WHERE id_usuario = %s
                ORDER BY data_calculo DESC, id_saude DESC
                LIMIT %s
                """,
                (usuario_id, limite),
            )
        else:
            cursor = conn.execute(
                f"""
                SELECT {_SELECT} FROM saude_financeira
                ORDER BY data_calculo DESC, id_saude DESC
                LIMIT %s
                """,
                (limite,),
            )
        return cursor.fetchall()

    def excluir(self, saude_id: int) -> bool:
        """Exclui registro apenas da conta logada."""
        usuario_id = resolver_usuario()
        if usuario_id is None:
            raise ValueError("Faça login para excluir este registro.")
        conn = self.db.get_connection()
        cursor = conn.execute(
            "DELETE FROM saude_financeira WHERE id_saude = %s AND id_usuario = %s",
            (saude_id, usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def existe_dados(self, usuario_id: Optional[int] = None) -> bool:
        """Verifica se há avaliações registradas."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                "SELECT COUNT(*) AS total FROM saude_financeira WHERE id_usuario = %s",
                (usuario_id,),
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) AS total FROM saude_financeira")
        return cursor.fetchone()["total"] > 0
