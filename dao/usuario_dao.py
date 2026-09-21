"""
DAO (Data Access Object) de Usuários.

Responsável por operações de CRUD e persistência de usuários
na tabela 'usuarios' do SQLite.
"""
from datetime import date
from typing import List, Optional, Dict, Any
from models.database import Database
from models.usuario import Usuario


class UsuarioDAO:
    """Gerencia o acesso a dados da entidade Usuario."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def inserir(
        self,
        nome: str,
        email: str,
        senha_hash: str,
        tipo_perfil: str = "PF",
        data_criacao: Optional[str] = None,
    ) -> int:
        """Insere um novo usuário e retorna o ID gerado."""
        data_criacao = data_criacao or date.today().strftime("%Y-%m-%d")
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash, tipo_perfil, data_criacao)
            VALUES (?, ?, ?, ?, ?)
            """,
            (nome.strip(), email.strip().lower(), senha_hash, tipo_perfil, data_criacao),
        )
        conn.commit()
        return cursor.lastrowid

    def buscar_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Busca um usuário pelo seu ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT id, nome, email, senha_hash, tipo_perfil, data_criacao FROM usuarios WHERE id = ?",
            (usuario_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def buscar_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca um usuário pelo email."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT id, nome, email, senha_hash, tipo_perfil, data_criacao FROM usuarios WHERE email = ?",
            (email.strip().lower(),),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def listar_todos(self) -> List[Dict[str, Any]]:
        """Retorna todos os usuários cadastrados."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT id, nome, email, senha_hash, tipo_perfil, data_criacao FROM usuarios ORDER BY nome ASC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def atualizar(
        self,
        usuario_id: int,
        nome: str,
        email: str,
        tipo_perfil: str,
    ) -> bool:
        """Atualiza informações cadastrais do usuário (exceto senha)."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            UPDATE usuarios
            SET nome = ?, email = ?, tipo_perfil = ?
            WHERE id = ?
            """,
            (nome.strip(), email.strip().lower(), tipo_perfil, usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def alterar_senha(self, usuario_id: int, nova_senha_hash: str) -> bool:
        """Atualiza a senha do usuário."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
            (nova_senha_hash, usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def excluir(self, usuario_id: int) -> bool:
        """Exclui um usuário pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        conn.commit()
        return cursor.rowcount > 0

    def existe_dados(self) -> bool:
        """Verifica se há pelo menos um usuário cadastrado."""
        conn = self.db.get_connection()
        cursor = conn.execute("SELECT COUNT(*) AS total FROM usuarios")
        return cursor.fetchone()["total"] > 0
