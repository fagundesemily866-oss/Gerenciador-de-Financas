"""
DAO (Data Access Object) de Usuários — MySQL.

Tabela: usuario
Mapeamento de tipos: tipo_perfil 'PF' ↔ 'PESSOAL', 'PJ' ↔ 'PJ'
"""
from datetime import date
from typing import List, Optional, Dict, Any
from models.database import Database
from models.usuario import Usuario
from services.seguranca import hash_senha, verificar_senha as _verificar_hash, precisa_atualizar


# --------------- helpers de conversão ---------------
def _perfil_para_db(perfil: str) -> str:
    return "PESSOAL" if perfil == "PF" else "PJ"

def _perfil_para_app(perfil: str) -> str:
    return "PF" if perfil == "PESSOAL" else "PJ"

def _row_para_app(row: Optional[Dict]) -> Optional[Dict]:
    if row is None:
        return None
    row["tipo_perfil"] = _perfil_para_app(row.get("tipo_perfil", "PESSOAL"))
    # criado_em é DATETIME; views esperam apenas a data YYYY-MM-DD
    dc = row.get("data_criacao")
    if dc and len(str(dc)) > 10:
        row["data_criacao"] = str(dc)[:10]
    return row


_SELECT = """
    id_usuario    AS id,
    nome,
    email,
    senha_hash,
    tipo_perfil,
    criado_em     AS data_criacao,
    foto_perfil,
    renda_mensal,
    modo_demo
"""


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
        foto_perfil: Optional[str] = None,
        renda_mensal: float = 0.0,
        modo_demo: bool = False,
    ) -> int:
        """Insere um novo usuário e retorna o ID gerado."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO usuario
                (nome, email, senha_hash, tipo_perfil, foto_perfil, renda_mensal, modo_demo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                nome.strip(),
                email.strip().lower(),
                senha_hash,
                _perfil_para_db(tipo_perfil),
                foto_perfil,
                float(renda_mensal or 0.0),
                1 if modo_demo else 0,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def buscar_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Busca um usuário pelo seu ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            f"SELECT {_SELECT} FROM usuario WHERE id_usuario = %s",
            (usuario_id,),
        )
        return _row_para_app(cursor.fetchone())

    def buscar_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca um usuário pelo email."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            f"SELECT {_SELECT} FROM usuario WHERE email = %s",
            (email.strip().lower(),),
        )
        return _row_para_app(cursor.fetchone())

    def listar_todos(self) -> List[Dict[str, Any]]:
        """Retorna todos os usuários cadastrados."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            f"SELECT {_SELECT} FROM usuario ORDER BY nome ASC"
        )
        return [_row_para_app(r) for r in cursor.fetchall()]

    def atualizar(
        self,
        usuario_id: int,
        nome: str,
        email: str,
        tipo_perfil: str,
        renda_mensal: Optional[float] = None,
    ) -> bool:
        """Atualiza informações cadastrais do usuário (exceto senha)."""
        conn = self.db.get_connection()
        if renda_mensal is not None:
            cursor = conn.execute(
                """
                UPDATE usuario
                SET nome = %s, email = %s, tipo_perfil = %s, renda_mensal = %s
                WHERE id_usuario = %s
                """,
                (nome.strip(), email.strip().lower(), _perfil_para_db(tipo_perfil),
                 float(renda_mensal), usuario_id),
            )
        else:
            cursor = conn.execute(
                """
                UPDATE usuario
                SET nome = %s, email = %s, tipo_perfil = %s
                WHERE id_usuario = %s
                """,
                (nome.strip(), email.strip().lower(), _perfil_para_db(tipo_perfil), usuario_id),
            )
        conn.commit()
        return cursor.rowcount > 0

    def atualizar_foto(self, usuario_id: int, caminho_foto: Optional[str]) -> bool:
        """Atualiza ou remove a foto de perfil do usuário."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "UPDATE usuario SET foto_perfil = %s WHERE id_usuario = %s",
            (caminho_foto, usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def atualizar_renda(self, usuario_id: int, renda_mensal: float) -> bool:
        """Atualiza a renda mensal cadastrada para o usuário."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "UPDATE usuario SET renda_mensal = %s WHERE id_usuario = %s",
            (float(renda_mensal or 0.0), usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def autenticar(self, email: str, senha: str) -> Optional[Dict[str, Any]]:
        """Valida e-mail + senha. Retorna o usuário ou None.

        Contas antigas (senha em texto puro) são migradas para hash no primeiro login.
        """
        usuario = self.buscar_por_email(email)
        if not usuario or not _verificar_hash(senha, usuario["senha_hash"]):
            return None
        if precisa_atualizar(usuario["senha_hash"]):
            self.alterar_senha(usuario["id"], hash_senha(senha))
        return usuario

    def verificar_senha(self, usuario_id: int, senha: str) -> bool:
        """Confere se a senha informada é a senha atual do usuário."""
        usuario = self.buscar_por_id(usuario_id)
        return bool(usuario) and _verificar_hash(senha, usuario["senha_hash"])

    def atualizar_senha(self, usuario_id: int, nova_senha: str) -> bool:
        """Define uma nova senha (recebe o texto puro e grava somente o hash)."""
        return self.alterar_senha(usuario_id, hash_senha(nova_senha))

    def alterar_senha(self, usuario_id: int, nova_senha_hash: str) -> bool:
        """Atualiza a senha do usuário."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "UPDATE usuario SET senha_hash = %s WHERE id_usuario = %s",
            (nova_senha_hash, usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def excluir(self, usuario_id: int) -> bool:
        """Exclui um usuário pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM usuario WHERE id_usuario = %s", (usuario_id,))
        conn.commit()
        return cursor.rowcount > 0

    def existe_dados(self) -> bool:
        """Verifica se há pelo menos um usuário cadastrado."""
        conn = self.db.get_connection()
        cursor = conn.execute("SELECT COUNT(*) AS total FROM usuario")
        return cursor.fetchone()["total"] > 0
