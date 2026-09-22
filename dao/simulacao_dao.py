"""
DAO (Data Access Object) de Simulações Financeiras.
===================================================

Persistência e recuperação de simulações na tabela 'simulacoes' do SQLite.
"""
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from models.database import Database
from models.simulacao import Simulacao


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
        conn = self.db.get_connection()
        params_json = json.dumps(parametros or {}, ensure_ascii=False)
        res_json = json.dumps(resultados or {}, ensure_ascii=False)
        data_criacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = conn.execute(
            """
            INSERT INTO simulacoes (usuario_id, nome, descricao, parametros_json, resultados_json, data_criacao)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                usuario_id,
                nome.strip(),
                descricao.strip(),
                params_json,
                res_json,
                data_criacao,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def buscar_por_id(self, simulacao_id: int) -> Optional[Dict[str, Any]]:
        """Busca uma simulação pelo seu ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            SELECT id, usuario_id, nome, descricao, parametros_json, resultados_json, data_criacao
            FROM simulacoes WHERE id = ?
            """,
            (simulacao_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        d = dict(row)
        try:
            d["parametros"] = json.loads(d.get("parametros_json") or "{}")
        except Exception:
            d["parametros"] = {}
        try:
            d["resultados"] = json.loads(d.get("resultados_json") or "{}")
        except Exception:
            d["resultados"] = {}
        return d

    def listar_todas(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna todas as simulações cadastradas, ordenadas pela mais recente."""
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, nome, descricao, parametros_json, resultados_json, data_criacao
                FROM simulacoes
                WHERE usuario_id = ? OR usuario_id IS NULL
                ORDER BY id DESC
                """,
                (usuario_id,),
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, nome, descricao, parametros_json, resultados_json, data_criacao
                FROM simulacoes
                ORDER BY id DESC
                """
            )

        lista = []
        for row in cursor.fetchall():
            d = dict(row)
            try:
                d["parametros"] = json.loads(d.get("parametros_json") or "{}")
            except Exception:
                d["parametros"] = {}
            try:
                d["resultados"] = json.loads(d.get("resultados_json") or "{}")
            except Exception:
                d["resultados"] = {}
            lista.append(d)
        return lista

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
            UPDATE simulacoes
            SET nome = ?, descricao = ?, parametros_json = ?, resultados_json = ?
            WHERE id = ?
            """,
            (nome.strip(), descricao.strip(), params_json, res_json, simulacao_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def deletar(self, simulacao_id: int) -> bool:
        """Exclui uma simulação pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM simulacoes WHERE id = ?", (simulacao_id,))
        conn.commit()
        return cursor.rowcount > 0
