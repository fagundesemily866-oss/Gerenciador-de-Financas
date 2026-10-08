"""
DAO (Data Access Object) de Simulações Financeiras — MySQL.

Tabela: simulacao
"""
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from models.database import Database
from services.sessao import resolver_usuario
from models.simulacao import Simulacao


_SELECT = """
    id_simulacao    AS id,
    id_usuario      AS usuario_id,
    nome,
    descricao,
    parametros_json,
    resultados_json,
    criado_em       AS data_criacao
"""


class SimulacaoDAO:
    """Gerencia o acesso a dados da entidade Simulacao."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def inserir(
        self,
        nome: str,
        descricao: str = "",
        parametros: Optional[Dict[str, Any]] = None,
        resultados: Optional[Dict[str, Any]] = None,
        usuario_id: Optional[int] = None,
    ) -> int:
        """Insere uma nova simulação salva e retorna o ID gerado."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        params_json = json.dumps(parametros or {}, ensure_ascii=False)
        res_json = json.dumps(resultados or {}, ensure_ascii=False)

        cursor = conn.execute(
            """
            INSERT INTO simulacao (id_usuario, nome, descricao, parametros_json, resultados_json)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (usuario_id, nome.strip(), descricao.strip(), params_json, res_json),
        )
        conn.commit()
        return cursor.lastrowid

    def _parse_json_fields(self, d: Dict) -> Dict:
        """Decodifica campos JSON armazenados como string."""
        for campo in ("parametros_json", "resultados_json"):
            raw = d.get(campo)
            chave = campo.replace("_json", "")  # parametros / resultados
            if isinstance(raw, str):
                try:
                    d[chave] = json.loads(raw)
                except Exception:
                    d[chave] = {}
            elif isinstance(raw, dict):
                d[chave] = raw
            else:
                d[chave] = {}
        return d

    def buscar_por_id(self, simulacao_id: int) -> Optional[Dict[str, Any]]:
        """Busca uma simulação pelo seu ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            f"SELECT {_SELECT} FROM simulacao WHERE id_simulacao = %s",
            (simulacao_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._parse_json_fields(row)

    def listar_todas(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna todas as simulações cadastradas, ordenadas pela mais recente."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                f"""
                SELECT {_SELECT} FROM simulacao
                WHERE id_usuario = %s
                ORDER BY id_simulacao DESC
                """,
                (usuario_id,),
            )
        else:
            cursor = conn.execute(
                f"SELECT {_SELECT} FROM simulacao ORDER BY id_simulacao DESC"
            )
        return [self._parse_json_fields(r) for r in cursor.fetchall()]

    def atualizar(
        self,
        simulacao_id: int,
        nome: str,
        descricao: str = "",
        parametros: Optional[Dict[str, Any]] = None,
        resultados: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Atualiza uma simulação existente."""
        conn = self.db.get_connection()
        params_json = json.dumps(parametros or {}, ensure_ascii=False)
        res_json = json.dumps(resultados or {}, ensure_ascii=False)

        cursor = conn.execute(
            """
            UPDATE simulacao
            SET nome = %s, descricao = %s, parametros_json = %s, resultados_json = %s
            WHERE id_simulacao = %s
            """,
            (nome.strip(), descricao.strip(), params_json, res_json, simulacao_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def deletar(self, simulacao_id: int) -> bool:
        """Exclui uma simulação pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM simulacao WHERE id_simulacao = %s", (simulacao_id,))
        conn.commit()
        return cursor.rowcount > 0
