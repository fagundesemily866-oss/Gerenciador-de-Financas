"""
DAO (Data Access Object) de Terceiros — MySQL.

Tabela: terceiro
"""
from datetime import date
from typing import List, Optional, Dict, Any
from models.database import Database
from services.sessao import resolver_usuario
from models.terceiro import Terceiro


_SELECT = """
    id_terceiro  AS id,
    id_usuario   AS usuario_id,
    nome,
    relacao,
    criado_em    AS data_criacao,
    foto_perfil
"""


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
        foto_perfil: Optional[str] = None,
    ) -> int:
        """Insere um novo terceiro e retorna o ID gerado."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO terceiro (id_usuario, nome, relacao, foto_perfil)
            VALUES (%s, %s, %s, %s)
            """,
            (usuario_id, nome.strip(), relacao.strip(), foto_perfil),
        )
        conn.commit()
        return cursor.lastrowid

    def buscar_por_id(self, terceiro_id: int) -> Optional[Dict[str, Any]]:
        """Busca um terceiro pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            f"SELECT {_SELECT} FROM terceiro WHERE id_terceiro = %s",
            (terceiro_id,),
        )
        return cursor.fetchone()

    def listar_todos(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna todos os terceiros cadastrados."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                f"""
                SELECT {_SELECT} FROM terceiro
                WHERE id_usuario = %s
                ORDER BY nome ASC
                """,
                (usuario_id,),
            )
        else:
            cursor = conn.execute(
                f"SELECT {_SELECT} FROM terceiro ORDER BY nome ASC"
            )
        return cursor.fetchall()

    def atualizar(self, terceiro_id: int, nome: str, relacao: str, foto_perfil: Optional[str] = None) -> bool:
        """Atualiza informações do terceiro."""
        conn = self.db.get_connection()
        if foto_perfil is not None:
            cursor = conn.execute(
                """
                UPDATE terceiro SET nome = %s, relacao = %s, foto_perfil = %s
                WHERE id_terceiro = %s
                """,
                (nome.strip(), relacao.strip(), foto_perfil, terceiro_id),
            )
        else:
            cursor = conn.execute(
                """
                UPDATE terceiro SET nome = %s, relacao = %s
                WHERE id_terceiro = %s
                """,
                (nome.strip(), relacao.strip(), terceiro_id),
            )
        conn.commit()
        return cursor.rowcount > 0

    def atualizar_foto(self, terceiro_id: int, caminho_foto: Optional[str]) -> bool:
        """Atualiza ou remove a foto do terceiro."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "UPDATE terceiro SET foto_perfil = %s WHERE id_terceiro = %s",
            (caminho_foto, terceiro_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def excluir(self, terceiro_id: int) -> bool:
        """Exclui um terceiro pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM terceiro WHERE id_terceiro = %s", (terceiro_id,))
        conn.commit()
        return cursor.rowcount > 0

    def existe_dados(self, usuario_id: Optional[int] = None) -> bool:
        """Verifica se existem terceiros cadastrados."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                "SELECT COUNT(*) AS total FROM terceiro WHERE id_usuario = %s",
                (usuario_id,),
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) AS total FROM terceiro")
        return cursor.fetchone()["total"] > 0
