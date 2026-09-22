import customtkinter as ctk
from typing import Optional
from dao.meta_dao import MetaDAO
from models.meta import Meta
from views.notificacao_toast import GerenciadorNotificacoes
from views.tema import (
    COR_CARD, COR_CARD_INTERNO, COR_BORDA, COR_TEXTO_PRINCIPAL,
    COR_TEXTO_SECUNDARIO, COR_TEXTO_TERCIARIO, COR_TEXTO_MUTED,
    COR_ACENTO_PRIMARIO, COR_ACENTO_HOVER, COR_SUCESSO, COR_SUCESSO_HOVER,
    COR_ALERTA, COR_AVISO, COR_INFO, COR_PROGRESSO, COR_PROGRESSO_BG,
    COR_BOTAO_SECUNDARIO, COR_BOTAO_SECUNDARIO_HOVER,
    COR_EXCLUIR_HOVER, COR_EXCLUIR_TEXTO,
    fonte, fonte_subtitulo, fonte_corpo, fonte_pequena, fonte_hint,
)


class MetaView(ctk.CTkFrame):
    """Tela de acompanhamento e criação de Metas Financeiras — Visual Premium."""

    def __init__(self, parent, dao: Optional[MetaDAO] = None):
        super().__init__(parent, fg_color="transparent")
        self.dao = dao or MetaDAO()

        # Grid principal: 2 colunas
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._criar_painel_formulario()
        self._criar_painel_lista()
        self.atualizar_dados()

    # ==========================================================
    # FORMULÁRIO (ESQUERDA)
    # ==========================================================
    def _criar_painel_formulario(self):
        card_form = ctk.CTkFrame(
            self,
            corner_radius=18,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
        )
        card_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        # Cabeçalho decorativo com ícone grande
        header_frame = ctk.CTkFrame(card_form, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 5))

        ctk.CTkLabel(
            header_frame,
            text="🎯",
            font=fonte(28),
        ).pack(side="left", padx=(0, 8))

        header_text = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_text.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            header_text,
            text="NOVA META FINANCEIRA",
            font=fonte(14, "bold"),
            text_color=COR_ACENTO_PRIMARIO,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_text,
            text="Defina seu próximo objetivo",
            font=fonte_hint(),
            text_color=COR_TEXTO_TERCIARIO,
            anchor="w",
        ).pack(anchor="w")

        # Separador visual sutil
        ctk.CTkFrame(card_form, fg_color=COR_BORDA, height=1).pack(
            fill="x", padx=20, pady=(10, 15)
        )

        # Descrição
        ctk.CTkLabel(
            card_form, text="✨ Objetivo / Descrição:", font=fonte_corpo()
        ).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_desc = ctk.CTkEntry(
            card_form,
            placeholder_text="Ex: Reserva de Emergência, Viagem...",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            font=fonte_corpo(),
            height=36,
        )
        self.entry_desc.pack(fill="x", padx=20, pady=(0, 10))

        # Valor Alvo
        ctk.CTkLabel(
            card_form, text="💰 Valor Alvo (R$):", font=fonte_corpo()
        ).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_alvo = ctk.CTkEntry(
            card_form,
            placeholder_text="Ex: 5000.00",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            font=fonte(14, "bold"),
            height=36,
        )
        self.entry_alvo.pack(fill="x", padx=20, pady=(0, 10))

        # Valor Inicial Guardado
        ctk.CTkLabel(
            card_form, text="🏦 Valor Já Guardado (R$):", font=fonte_corpo()
        ).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_atual = ctk.CTkEntry(
            card_form,
            placeholder_text="0.00 (opcional)",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            font=fonte_corpo(),
            height=36,
        )
        self.entry_atual.pack(fill="x", padx=20, pady=(0, 10))

        # Prazo Estimado
        ctk.CTkLabel(
            card_form, text="⏳ Prazo Estimado:", font=fonte_corpo()
        ).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_prazo = ctk.CTkEntry(
            card_form,
            placeholder_text="Ex: 6 meses, 1 ano, 18 meses...",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            font=fonte_corpo(),
            height=36,
        )
        self.entry_prazo.pack(fill="x", padx=20, pady=(0, 4))

        # Hint prazo
        ctk.CTkLabel(
            card_form,
            text="💡 Descreva livremente o prazo desejado",
            font=fonte_hint(),
            text_color=COR_TEXTO_MUTED,
            anchor="w",
        ).pack(anchor="w", padx=20, pady=(0, 8))

        # Data Limite
        ctk.CTkLabel(
            card_form, text="📅 Data Limite (opcional):", font=fonte_corpo()
        ).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_data_limite = ctk.CTkEntry(
            card_form,
            placeholder_text="DD/MM/AAAA",
            fg_color=COR_CARD_INTERNO,
            border_color=COR_BORDA,
            font=fonte_corpo(),
            height=36,
        )
        self.entry_data_limite.pack(fill="x", padx=20, pady=(0, 4))

        # Hint data
        ctk.CTkLabel(
            card_form,
            text="📅 Formato: DD/MM/AAAA",
            font=fonte_hint(),
            text_color=COR_TEXTO_MUTED,
            anchor="w",
        ).pack(anchor="w", padx=20, pady=(0, 12))

        # Feedback
        self.lbl_feedback = ctk.CTkLabel(
            card_form,
            text="",
            font=fonte(12, "bold"),
        )
        self.lbl_feedback.pack(fill="x", padx=20, pady=(0, 10))

        # Botão Criar Meta — visual premium
        btn_criar = ctk.CTkButton(
            card_form,
            text="🚀  Criar Meta Financeira",
            fg_color=COR_SUCESSO,
            text_color="#0B1D1F",
            hover_color=COR_SUCESSO_HOVER,
            font=fonte(13, "bold"),
            height=42,
            corner_radius=10,
            command=self._criar_meta,
        )
        btn_criar.pack(fill="x", padx=20, pady=(0, 20))

    # ==========================================================
    # LISTA DE METAS (DIREITA)
    # ==========================================================
    def _criar_painel_lista(self):
        card_lista = ctk.CTkFrame(
            self,
            corner_radius=18,
            fg_color=COR_CARD,
            border_width=1,
            border_color=COR_BORDA,
        )
        card_lista.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        card_lista.grid_columnconfigure(0, weight=1)
        card_lista.grid_rowconfigure(1, weight=1)

        # Header com ícone
        header = ctk.CTkFrame(card_lista, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="🏆",
            font=fonte(22),
        ).pack(side="left", padx=(0, 8))

        self.lbl_total_metas = ctk.CTkLabel(
            header,
            text="Minhas Metas Financeiras",
            font=fonte_subtitulo(),
            text_color=COR_TEXTO_PRINCIPAL,
        )
        self.lbl_total_metas.pack(side="left")

        # ScrollFrame para os cards
        self.scroll_metas = ctk.CTkScrollableFrame(
            card_lista,
            fg_color="transparent",
            corner_radius=10,
        )
        self.scroll_metas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.scroll_metas.grid_columnconfigure(0, weight=1)

    # ==========================================================
    # AÇÕES
    # ==========================================================
    def _criar_meta(self):
        desc = self.entry_desc.get().strip()
        alvo_str = self.entry_alvo.get().strip().replace(",", ".").replace("R$", "")
        atual_str = self.entry_atual.get().strip().replace(",", ".").replace("R$", "")
        prazo = self.entry_prazo.get().strip()
        data_limite = self.entry_data_limite.get().strip()

        if not desc:
            self._mostrar_feedback("O objetivo/descrição é obrigatório!", COR_ALERTA)
            return

        if not alvo_str:
            self._mostrar_feedback("Informe o valor alvo!", COR_ALERTA)
            return

        try:
            val_alvo = float(alvo_str)
            if val_alvo <= 0:
                self._mostrar_feedback("O valor alvo deve ser maior que zero!", COR_ALERTA)
                return
        except ValueError:
            self._mostrar_feedback("Valor alvo inválido!", COR_ALERTA)
            return

        val_atual = 0.0
        if atual_str:
            try:
                val_atual = float(atual_str)
            except ValueError:
                self._mostrar_feedback("Valor guardado inválido!", COR_ALERTA)
                return

        try:
            self.dao.inserir(
                descricao=desc,
                valor_alvo=val_alvo,
                valor_atual=val_atual,
                prazo=prazo if prazo else None,
                data_limite=data_limite if data_limite else None,
            )
            self._mostrar_feedback(f"✓ Meta '{desc}' criada com sucesso!", COR_SUCESSO)
            self.entry_desc.delete(0, "end")
            self.entry_alvo.delete(0, "end")
            self.entry_atual.delete(0, "end")
            self.entry_prazo.delete(0, "end")
            self.entry_data_limite.delete(0, "end")
            try:
                notif = GerenciadorNotificacoes.obter_instancia()
                if notif:
                    notif.sucesso(f"Meta '{desc}' criada!")
            except Exception:
                pass
        except Exception as e:
            self._mostrar_feedback(f"Erro ao salvar: {e}", COR_ALERTA)
            try:
                notif = GerenciadorNotificacoes.obter_instancia()
                if notif:
                    notif.erro(f"Erro ao salvar meta: {e}")
            except Exception:
                pass

    def _mostrar_feedback(self, texto: str, cor: str):
        self.lbl_feedback.configure(text=texto, text_color=cor)

    def _guardar_aporte(self, meta_id: int, descricao: str):
        dialog = ctk.CTkInputDialog(
            text=f"Quanto você deseja guardar para '{descricao}'?\n(Digite apenas o valor numérico)",
            title="Adicionar Aporte à Meta",
        )
        valor_str = dialog.get_input()
        if valor_str:
            try:
                quantia = float(valor_str.replace(",", ".").replace("R$", "").strip())
                if quantia > 0:
                    self.dao.guardar_valor(meta_id, quantia)
                    self.atualizar_dados()
            except ValueError:
                pass

    def _excluir_meta(self, meta_id: int):
        self.dao.excluir(meta_id)
        self.atualizar_dados()
        notif = GerenciadorNotificacoes.obter_instancia()
        if notif:
            notif.sucesso("Meta excluída com sucesso!")

    def atualizar_dados(self):
        """Recarrega as metas do banco SQLite — não atingidas primeiro."""
        for widget in self.scroll_metas.winfo_children():
            widget.destroy()

        metas = self.dao.listar_todas()

        # Ordenar: não concluídas primeiro, concluídas ao final
        def _chave_ordenacao(m):
            meta_obj = Meta(**m)
            return meta_obj.calcular_progresso() >= 100.0

        metas = sorted(metas, key=_chave_ordenacao)

        self.lbl_total_metas.configure(text=f"Minhas Metas Financeiras ({len(metas)})")

        if not metas:
            # Card vazio motivacional
            empty_frame = ctk.CTkFrame(
                self.scroll_metas,
                fg_color=COR_CARD_INTERNO,
                corner_radius=15,
            )
            empty_frame.pack(fill="x", padx=5, pady=20)

            ctk.CTkLabel(
                empty_frame,
                text="🎯",
                font=fonte(36),
            ).pack(pady=(25, 5))

            ctk.CTkLabel(
                empty_frame,
                text="Nenhuma meta cadastrada ainda",
                font=fonte(14, "bold"),
                text_color=COR_TEXTO_SECUNDARIO,
            ).pack()

            ctk.CTkLabel(
                empty_frame,
                text="Defina seu primeiro objetivo financeiro\ne comece a construir seu futuro!",
                font=fonte_corpo(),
                text_color=COR_TEXTO_TERCIARIO,
                justify="center",
            ).pack(pady=(5, 25))
            return

        for m_dict in metas:
            self._renderizar_card_meta(m_dict)

    def _renderizar_card_meta(self, m_dict: dict):
        # Cálculo de progresso (antecipado para estilizar o card)
        meta_obj = Meta(**m_dict)
        progresso = meta_obj.calcular_progresso()
        atingida = progresso >= 100.0

        # Cor de borda dinâmica baseada no progresso
        if atingida:
            borda_cor = COR_SUCESSO
        elif progresso >= 75:
            borda_cor = COR_ACENTO_PRIMARIO
        elif progresso >= 40:
            borda_cor = COR_INFO
        else:
            borda_cor = COR_BORDA

        card = ctk.CTkFrame(
            self.scroll_metas,
            fg_color=COR_CARD_INTERNO,
            corner_radius=14,
            border_width=1,
            border_color=borda_cor,
        )
        card.pack(fill="x", padx=5, pady=6)
        card.grid_columnconfigure(0, weight=1)

        # Header do card: Ícone + Título e Botão Excluir
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(12, 4))
        header.grid_columnconfigure(1, weight=1)

        # Ícone de status
        icone_status = "🏆" if atingida else ("🔥" if progresso >= 75 else ("📈" if progresso >= 40 else "🎯"))
        ctk.CTkLabel(
            header,
            text=icone_status,
            font=fonte(20),
        ).grid(row=0, column=0, padx=(0, 8))

        ctk.CTkLabel(
            header,
            text=m_dict["descricao"],
            font=fonte(15, "bold"),
            text_color=COR_TEXTO_PRINCIPAL,
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        btn_del = ctk.CTkButton(
            header,
            text="🗑️",
            width=28,
            height=28,
            fg_color="transparent",
            hover_color=COR_EXCLUIR_HOVER,
            text_color=COR_EXCLUIR_TEXTO,
            command=lambda mid=m_dict["id"]: self._excluir_meta(mid),
        )
        btn_del.grid(row=0, column=2, sticky="e")

        cor_progresso = COR_SUCESSO if atingida else COR_ACENTO_PRIMARIO
        texto_status = "🎉 META ATINGIDA!" if atingida else f"{progresso:.1f}% concluído"

        sub_info = ctk.CTkFrame(card, fg_color="transparent")
        sub_info.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=2)
        sub_info.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            sub_info,
            text=f"R$ {m_dict['valor_atual']:.2f} de R$ {m_dict['valor_alvo']:.2f}",
            font=fonte(13, "bold"),
            text_color=COR_TEXTO_SECUNDARIO,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            sub_info,
            text=texto_status,
            font=fonte(12, "bold"),
            text_color=cor_progresso,
        ).grid(row=0, column=1, sticky="e")

        # Barra de Progresso
        progress_bar = ctk.CTkProgressBar(
            card,
            progress_color=cor_progresso,
            fg_color=COR_PROGRESSO_BG,
            height=12,
            corner_radius=6,
        )
        progress_bar.set(min(progresso / 100.0, 1.0))
        progress_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=(4, 6))

        # Indicador de quanto falta + valor/mês estimado
        falta = max(0.0, m_dict["valor_alvo"] - m_dict["valor_atual"])
        sub_falta = ctk.CTkFrame(card, fg_color="transparent")
        sub_falta.grid(row=3, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 4))
        sub_falta.grid_columnconfigure(0, weight=1)

        if atingida:
            info_falta = "🏆 Objetivo alcançado!"
            cor_falta = COR_SUCESSO
        else:
            info_falta = f"Faltam: R$ {falta:.2f}"
            cor_falta = COR_AVISO

        ctk.CTkLabel(
            sub_falta,
            text=info_falta,
            font=fonte(11, "bold"),
            text_color=cor_falta,
        ).grid(row=0, column=0, sticky="w")

        # Valor/mês estimado com base no prazo textual (se contiver número)
        if not atingida and m_dict.get("prazo"):
            prazo_txt = m_dict["prazo"]
            # tenta extrair número do prazo (ex: "6 meses" → 6)
            import re
            nums = re.findall(r"\d+", prazo_txt)
            if nums:
                meses = int(nums[0])
                if meses > 0:
                    val_mes = falta / meses
                    ctk.CTkLabel(
                        sub_falta,
                        text=f"≈ R$ {val_mes:.2f}/mês",
                        font=fonte_pequena(),
                        text_color=COR_INFO,
                    ).grid(row=0, column=1, sticky="e")

        # Footer com Prazo e Aportes Rápidos
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.grid(row=4, column=0, columnspan=2, sticky="ew", padx=15, pady=(4, 12))
        footer.grid_columnconfigure(0, weight=1)

        prazo_txt = []
        if m_dict.get("prazo"):
            prazo_txt.append(m_dict["prazo"])
        if m_dict.get("data_limite"):
            prazo_txt.append(f"Até {m_dict['data_limite']}")
        info_prazo = " • ".join(prazo_txt) if prazo_txt else "Sem prazo definido"

        ctk.CTkLabel(
            footer,
            text=f"📅 {info_prazo}",
            font=fonte_pequena(),
            text_color=COR_TEXTO_MUTED,
        ).grid(row=0, column=0, sticky="w")

        # Botões de aporte rápido — visual premium
        aportes_box = ctk.CTkFrame(footer, fg_color="transparent")
        aportes_box.grid(row=0, column=1, sticky="e")

        for valor, label in [(50.0, "+R$50"), (100.0, "+R$100")]:
            ctk.CTkButton(
                aportes_box,
                text=label,
                width=60,
                height=28,
                font=fonte(10, "bold"),
                fg_color=COR_BOTAO_SECUNDARIO,
                hover_color=COR_BOTAO_SECUNDARIO_HOVER,
                text_color=COR_SUCESSO,
                corner_radius=8,
                command=lambda mid=m_dict["id"], v=valor: self._aporte_rapido(mid, v),
            ).pack(side="left", padx=2)

        ctk.CTkButton(
            aportes_box,
            text="+ Outro",
            width=64,
            height=28,
            font=fonte(10, "bold"),
            fg_color=COR_BOTAO_SECUNDARIO,
            hover_color=COR_BOTAO_SECUNDARIO_HOVER,
            text_color=COR_ACENTO_PRIMARIO,
            corner_radius=8,
            command=lambda mid=m_dict["id"], d=m_dict["descricao"]: self._guardar_aporte(mid, d),
        ).pack(side="left", padx=2)

    def _aporte_rapido(self, meta_id: int, quantia: float):
        self.dao.guardar_valor(meta_id, quantia)
        self.atualizar_dados()


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Testando MetaView")
    app.geometry("950x600")
    view = MetaView(app)
    view.pack(expand=True, fill="both", padx=20, pady=20)
    app.mainloop()
