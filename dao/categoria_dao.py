"""
DAO (Data Access Object) de Categorias.

Responsável por operações de persistência e consulta na tabela 'categorias' do SQLite.
"""
from typing import List, Optional, Dict, Any
from models.database import Database
from models.categoria import Categoria


class CategoriaDAO:
    """Gerencia o acesso a dados da entidade Categoria."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def inserir(
        self,
        nome: str,
        tipo: str,
        escopo: str = "Pessoal",
        limite_orcamento: float = 0.0,
        usuario_id: Optional[int] = None,
    ) -> int:
        """Insere uma nova categoria e retorna o ID gerado."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO categorias (usuario_id, nome, tipo, escopo, limite_orcamento)
            VALUES (?, ?, ?, ?, ?)
            """,
            (usuario_id, nome.strip(), tipo, escopo, float(limite_orcamento)),
        )
        conn.commit()
        return cursor.lastrowid

    def buscar_por_id(self, categoria_id: int) -> Optional[Dict[str, Any]]:
        """Busca uma categoria pelo seu ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            SELECT id, usuario_id, nome, tipo, escopo, limite_orcamento
            FROM categorias WHERE id = ?
            """,
            (categoria_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def listar_todas(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna todas as categorias, opcionalmente filtrando por usuário."""
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, nome, tipo, escopo, limite_orcamento
                FROM categorias
                WHERE usuario_id = ? OR usuario_id IS NULL
                ORDER BY nome ASC
                """,
                (usuario_id,),
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, nome, tipo, escopo, limite_orcamento
                FROM categorias
                ORDER BY nome ASC
                """
            )
        return [dict(row) for row in cursor.fetchall()]

    def listar_por_tipo(
        self, tipo: str, usuario_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retorna categorias filtradas pelo tipo ('Receita' ou 'Despesa')."""
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, nome, tipo, escopo, limite_orcamento
                FROM categorias
                WHERE (usuario_id = ? OR usuario_id IS NULL) AND tipo = ?
                ORDER BY nome ASC
                """,
                (usuario_id, tipo),
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, nome, tipo, escopo, limite_orcamento
                FROM categorias
                WHERE tipo = ?
                ORDER BY nome ASC
                """,
                (tipo,),
            )
        return [dict(row) for row in cursor.fetchall()]

    def atualizar(
        self,
        categoria_id: int,
        nome: str,
        tipo: str,
        escopo: str,
        limite_orcamento: float,
    ) -> bool:
        """Atualiza todos os dados de uma categoria."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            UPDATE categorias
            SET nome = ?, tipo = ?, escopo = ?, limite_orcamento = ?
            WHERE id = ?
            """,
            (nome.strip(), tipo, escopo, float(limite_orcamento), categoria_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def atualizar_limite(self, categoria_id: int, novo_limite: float) -> bool:
        """Atualiza somente o limite de orçamento de uma categoria."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "UPDATE categorias SET limite_orcamento = ? WHERE id = ?",
            (float(novo_limite), categoria_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def excluir(self, categoria_id: int) -> bool:
        """Exclui uma categoria pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
        conn.commit()
        return cursor.rowcount > 0

    def existe_dados(self, usuario_id: Optional[int] = None) -> bool:
        """Verifica se existem categorias cadastradas."""
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                "SELECT COUNT(*) AS total FROM categorias WHERE usuario_id = ? OR usuario_id IS NULL",
                (usuario_id,),
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) AS total FROM categorias")
        return cursor.fetchone()["total"] > 0
