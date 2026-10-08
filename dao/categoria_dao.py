"""
DAO (Data Access Object) de Categorias — MySQL.

Tabela: categoria
Mapeamento: tipo 'Receita'↔'RECEITA', 'Despesa'↔'DESPESA'
            escopo 'Pessoal'↔'PESSOAL', 'Empresarial'↔'PJ'
"""
from typing import List, Optional, Dict, Any
from models.database import Database
from services.sessao import resolver_usuario
from models.categoria import Categoria


# --------------- helpers de conversão ---------------
def _tipo_db(t: str) -> str:
    return t.upper() if t else "DESPESA"

def _tipo_app(t: str) -> str:
    return t.capitalize() if t else "Despesa"

def _escopo_db(e: str) -> str:
    if e and e.upper() in ("PESSOAL", "PJ"):
        return e.upper()
    if e and "empresa" in e.lower():
        return "PJ"
    return "PESSOAL"

def _escopo_app(e: str) -> str:
    return "Pessoal" if e == "PESSOAL" else "Empresarial"

def _row(r: Optional[Dict]) -> Optional[Dict]:
    if r is None:
        return None
    r["tipo"] = _tipo_app(r.get("tipo", ""))
    r["escopo"] = _escopo_app(r.get("escopo", ""))
    return r

_SELECT = """
    id_categoria      AS id,
    id_usuario        AS usuario_id,
    nome,
    tipo,
    escopo,
    limite_orcamento
"""


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
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO categoria (id_usuario, nome, tipo, escopo, limite_orcamento)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (usuario_id, nome.strip(), _tipo_db(tipo), _escopo_db(escopo), float(limite_orcamento)),
        )
        conn.commit()
        return cursor.lastrowid

    def buscar_por_id(self, categoria_id: int) -> Optional[Dict[str, Any]]:
        """Busca uma categoria pelo seu ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            f"SELECT {_SELECT} FROM categoria WHERE id_categoria = %s",
            (categoria_id,),
        )
        return _row(cursor.fetchone())

    def listar_todas(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna todas as categorias, opcionalmente filtrando por usuário."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                f"""
                SELECT {_SELECT} FROM categoria
                WHERE id_usuario = %s
                ORDER BY nome ASC
                """,
                (usuario_id,),
            )
        else:
            cursor = conn.execute(
                f"SELECT {_SELECT} FROM categoria ORDER BY nome ASC"
            )
        return [_row(r) for r in cursor.fetchall()]

    def listar_por_tipo(
        self, tipo: str, usuario_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retorna categorias filtradas pelo tipo ('Receita' ou 'Despesa')."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                f"""
                SELECT {_SELECT} FROM categoria
                WHERE (id_usuario = %s) AND tipo = %s
                ORDER BY nome ASC
                """,
                (usuario_id, _tipo_db(tipo)),
            )
        else:
            cursor = conn.execute(
                f"""
                SELECT {_SELECT} FROM categoria
                WHERE tipo = %s ORDER BY nome ASC
                """,
                (_tipo_db(tipo),),
            )
        return [_row(r) for r in cursor.fetchall()]

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
            UPDATE categoria
            SET nome = %s, tipo = %s, escopo = %s, limite_orcamento = %s
            WHERE id_categoria = %s
            """,
            (nome.strip(), _tipo_db(tipo), _escopo_db(escopo),
             float(limite_orcamento), categoria_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def atualizar_limite(self, categoria_id: int, novo_limite: float) -> bool:
        """Atualiza somente o limite de orçamento de uma categoria."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "UPDATE categoria SET limite_orcamento = %s WHERE id_categoria = %s",
            (float(novo_limite), categoria_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def excluir(self, categoria_id: int) -> bool:
        """Exclui uma categoria pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM categoria WHERE id_categoria = %s", (categoria_id,))
        conn.commit()
        return cursor.rowcount > 0

    def existe_dados(self, usuario_id: Optional[int] = None) -> bool:
        """Verifica se existem categorias cadastradas."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                "SELECT COUNT(*) AS total FROM categoria WHERE id_usuario = %s",
                (usuario_id,),
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) AS total FROM categoria")
        return cursor.fetchone()["total"] > 0
