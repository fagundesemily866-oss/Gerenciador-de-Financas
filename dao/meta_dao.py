from datetime import date
from typing import List, Optional, Dict, Any
from models.database import Database
from services.sessao import resolver_usuario
from models.meta import Meta


class MetaDAO:
    """Gerencia o acesso a dados da entidade Meta e seus aportes."""

    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def inserir(
        self,
        descricao: str,
        valor_alvo: float,
        valor_atual: float = 0.0,
        prazo: Optional[str] = None,
        data_limite: Optional[str] = None,
        usuario_id: Optional[int] = None,
        data_criacao: Optional[str] = None,
    ) -> int:
        """Insere uma nova meta financeira e retorna o ID gerado."""
        data_criacao = data_criacao or date.today().strftime("%Y-%m-%d")
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        valor_atual_f = float(valor_atual or 0.0)
        valor_alvo_f = float(valor_alvo or 0.0)
        atingiu = 1 if (valor_atual_f >= valor_alvo_f and valor_alvo_f > 0) else 0

        cursor = conn.execute(
            """
            INSERT INTO metas (usuario_id, descricao, valor_alvo, valor_atual, prazo, data_limite, concluida, data_conclusao, celebracao_exibida)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                usuario_id,
                descricao.strip(),
                valor_alvo_f,
                valor_atual_f,
                prazo,
                data_limite,
                atingiu,
                data_criacao if atingiu else None,
                atingiu,  # Se já foi criada concluída, não dispara celebração
            ),
        )
        meta_id = cursor.lastrowid
        # Se começou com valor_atual > 0, registrar o aporte inicial
        if valor_atual_f > 0:
            conn.execute(
                """
                INSERT INTO meta_aportes (meta_id, valor, data)
                VALUES (?, ?, ?)
                """,
                (meta_id, valor_atual_f, data_criacao),
            )
        conn.commit()
        return meta_id

    def buscar_por_id(self, meta_id: int) -> Optional[Dict[str, Any]]:
        """Busca uma meta pelo seu ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            SELECT id, usuario_id, descricao, valor_alvo, valor_atual, prazo, data_limite,
                   concluida, data_conclusao, celebracao_exibida
            FROM metas WHERE id = ?
            """,
            (meta_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def listar_todas(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna todas as metas, opcionalmente filtrando por usuário."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, descricao, valor_alvo, valor_atual, prazo, data_limite,
                       concluida, data_conclusao, celebracao_exibida
                FROM metas
                WHERE usuario_id = ? OR usuario_id IS NULL
                ORDER BY concluida ASC, id DESC
                """,
                (usuario_id,),
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, usuario_id, descricao, valor_alvo, valor_atual, prazo, data_limite,
                       concluida, data_conclusao, celebracao_exibida
                FROM metas
                ORDER BY concluida ASC, id DESC
                """
            )
        return [dict(row) for row in cursor.fetchall()]

    def atualizar(
        self,
        meta_id: int,
        descricao: str,
        valor_alvo: float,
        prazo: Optional[str],
        data_limite: Optional[str],
    ) -> bool:
        """Atualiza informações de uma meta."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            UPDATE metas
            SET descricao = ?, valor_alvo = ?, prazo = ?, data_limite = ?
            WHERE id = ?
            """,
            (descricao.strip(), float(valor_alvo), prazo, data_limite, meta_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def guardar_valor(self, meta_id: int, quantia: float, data_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Incrementa o valor atual poupado na meta e registra o aporte.
        Retorna dicionário com status e se a meta atingiu 100% pela primeira vez.
        """
        if quantia <= 0:
            return {"sucesso": False, "atingiu_agora": False}

        data_aporte = data_str or date.today().strftime("%Y-%m-%d")
        conn = self.db.get_connection()

        # Busca estado atual
        meta_atual = self.buscar_por_id(meta_id)
        if not meta_atual:
            return {"sucesso": False, "atingiu_agora": False}

        novo_valor = float(meta_atual["valor_atual"]) + float(quantia)
        valor_alvo = float(meta_atual["valor_alvo"])
        atingiu_100 = (novo_valor >= valor_alvo) and (valor_alvo > 0)
        atingiu_agora = atingiu_100 and (int(meta_atual.get("celebracao_exibida", 0)) == 0)

        # Atualiza a meta
        if atingiu_agora:
            conn.execute(
                """
                UPDATE metas
                SET valor_atual = ?, concluida = 1, data_conclusao = ?
                WHERE id = ?
                """,
                (novo_valor, data_aporte, meta_id),
            )
        else:
            conn.execute(
                """
                UPDATE metas
                SET valor_atual = ?
                WHERE id = ?
                """,
                (novo_valor, meta_id),
            )

        # Registra histórico de aporte
        conn.execute(
            """
            INSERT INTO meta_aportes (meta_id, valor, data)
            VALUES (?, ?, ?)
            """,
            (meta_id, float(quantia), data_aporte),
        )
        conn.commit()

        meta_atualizada = self.buscar_por_id(meta_id)
        return {
            "sucesso": True,
            "atingiu_agora": atingiu_agora,
            "meta": meta_atualizada,
        }

    def marcar_celebracao_exibida(self, meta_id: int, data_conclusao: Optional[str] = None) -> bool:
        """Registra no banco que a comemoração daquela conclusão já foi exibida."""
        dt = data_conclusao or date.today().strftime("%Y-%m-%d")
        conn = self.db.get_connection()
        cursor = conn.execute(
            """
            UPDATE metas
            SET concluida = 1, celebracao_exibida = 1, data_conclusao = COALESCE(data_conclusao, ?)
            WHERE id = ?
            """,
            (dt, meta_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def aumentar_meta(self, meta_id: int, novo_valor_alvo: float) -> bool:
        """
        Aumenta o objetivo da meta. Se o novo valor for maior que o valor atual,
        a meta volta ao estado de 'em andamento' e reseta a celebração.
        """
        conn = self.db.get_connection()
        meta = self.buscar_por_id(meta_id)
        if not meta:
            return False

        valor_atual = float(meta["valor_atual"])
        novo_alvo = float(novo_valor_alvo)

        if novo_alvo > valor_atual:
            concluida = 0
            celebracao = 0
            data_conclusao = None
        else:
            concluida = 1
            celebracao = meta.get("celebracao_exibida", 1)
            data_conclusao = meta.get("data_conclusao")

        cursor = conn.execute(
            """
            UPDATE metas
            SET valor_alvo = ?, concluida = ?, celebracao_exibida = ?, data_conclusao = ?
            WHERE id = ?
            """,
            (novo_alvo, concluida, celebracao, data_conclusao, meta_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def listar_aportes_mes(self, ano: int, mes: int, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna todos os aportes feitos em metas em um determinado mês/ano."""
        prefixo = f"{ano:04d}-{mes:02d}"
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                """
                SELECT a.id, a.meta_id, a.valor, a.data, m.descricao, m.valor_alvo, m.valor_atual, m.concluida
                FROM meta_aportes a
                JOIN metas m ON a.meta_id = m.id
                WHERE a.data LIKE ? AND (m.usuario_id = ? OR m.usuario_id IS NULL)
                ORDER BY a.data ASC
                """,
                (f"{prefixo}%", usuario_id),
            )
        else:
            cursor = conn.execute(
                """
                SELECT a.id, a.meta_id, a.valor, a.data, m.descricao, m.valor_alvo, m.valor_atual, m.concluida
                FROM meta_aportes a
                JOIN metas m ON a.meta_id = m.id
                WHERE a.data LIKE ?
                ORDER BY a.data ASC
                """,
                (f"{prefixo}%",),
            )
        return [dict(row) for row in cursor.fetchall()]

    def obter_resumo_metas_mes(self, ano: int, mes: int, usuario_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Calcula o resumo completo de metas para o relatório mensal, incluindo:
        - Total guardado para cada meta no mês
        - Progresso mensal (%) e acumulado
        - Quanto falta
        - Metas concluídas no mês
        - Frases amigáveis inteligentes geradas a partir de dados reais.
        """
        todas_metas = self.listar_todas(usuario_id)
        aportes_mes = self.listar_aportes_mes(ano, mes, usuario_id)

        # Mapeia aportes por meta_id
        aportes_por_meta: Dict[int, float] = {}
        for ap in aportes_mes:
            mid = ap["meta_id"]
            aportes_por_meta[mid] = aportes_por_meta.get(mid, 0.0) + float(ap["valor"])

        prefixo_mes = f"{ano:04d}-{mes:02d}"
        metas_detalhadas = []
        total_guardado_mes = 0.0
        concluidas_mes = []
        frases = []

        for m in todas_metas:
            mid = m["id"]
            guardado_m = aportes_por_meta.get(mid, 0.0)
            total_guardado_mes += guardado_m

            valor_alvo = float(m["valor_alvo"] or 0.0)
            valor_atual = float(m["valor_atual"] or 0.0)
            progresso_total_pct = (valor_atual / valor_alvo * 100) if valor_alvo > 0 else 0.0
            progresso_mes_pct = (guardado_m / valor_alvo * 100) if valor_alvo > 0 else 0.0
            falta = max(0.0, valor_alvo - valor_atual)

            data_conc = m.get("data_conclusao") or ""
            foi_concluida_no_mes = (m.get("concluida") == 1) and (data_conc.startswith(prefixo_mes))
            if foi_concluida_no_mes:
                concluidas_mes.append(m["descricao"])

            # Gera frases amigáveis
            if foi_concluida_no_mes:
                frases.append(f"Parabéns! A meta '{m['descricao']}' foi concluída com sucesso! 🎉")
            elif guardado_m > 0:
                frases.append(f"Neste mês você conseguiu guardar R$ {guardado_m:,.2f} para sua meta '{m['descricao']}'.")
                if progresso_mes_pct >= 5.0:
                    frases.append(f"Você avançou {progresso_mes_pct:.1f}% na meta '{m['descricao']}' neste mês.")

            metas_detalhadas.append({
                "id": mid,
                "descricao": m["descricao"],
                "guardado_mes": guardado_m,
                "progresso_mes_pct": round(progresso_mes_pct, 1),
                "valor_atual": valor_atual,
                "valor_alvo": valor_alvo,
                "progresso_total_pct": round(progresso_total_pct, 1),
                "falta": falta,
                "concluida": m.get("concluida", 0),
                "foi_concluida_no_mes": foi_concluida_no_mes,
            })

        if not frases:
            if todas_metas:
                frases.append("Nenhum aporte foi registrado para suas metas neste mês. Que tal planejar uma reserva para o próximo mês?")
            else:
                frases.append("Você ainda não possui metas cadastradas. Acesse a aba 'Metas' e defina seus objetivos!")

        return {
            "ano": ano,
            "mes": mes,
            "total_guardado_mes": total_guardado_mes,
            "metas": metas_detalhadas,
            "concluidas_mes": concluidas_mes,
            "qtd_concluidas_mes": len(concluidas_mes),
            "frases": frases,
        }

    def excluir(self, meta_id: int) -> bool:
        """Exclui uma meta pelo ID."""
        conn = self.db.get_connection()
        cursor = conn.execute("DELETE FROM metas WHERE id = ?", (meta_id,))
        conn.commit()
        return cursor.rowcount > 0

    def existe_dados(self, usuario_id: Optional[int] = None) -> bool:
        """Verifica se existem metas cadastradas."""
        usuario_id = resolver_usuario(usuario_id)
        conn = self.db.get_connection()
        if usuario_id is not None:
            cursor = conn.execute(
                "SELECT COUNT(*) AS total FROM metas WHERE usuario_id = ? OR usuario_id IS NULL",
                (usuario_id,),
            )
        else:
            cursor = conn.execute("SELECT COUNT(*) AS total FROM metas")
        return cursor.fetchone()["total"] > 0
