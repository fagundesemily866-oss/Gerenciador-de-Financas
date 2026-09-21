import customtkinter as ctk
from typing import Optional
from dao.meta_dao import MetaDAO
from models.meta import Meta
from views.notificacao_toast import GerenciadorNotificacoes


class MetaView(ctk.CTkFrame):
    """Tela de acompanhamento e criação de Metas Financeiras."""

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
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        card_form.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        titulo = ctk.CTkLabel(
            card_form,
            text="🎯  NOVA META FINANCEIRA",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#A6ADC8",
        )
        titulo.pack(anchor="w", padx=20, pady=(20, 15))

        # Descrição
        ctk.CTkLabel(card_form, text="Objetivo / Descrição:", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.entry_desc = ctk.CTkEntry(
            card_form,
            placeholder_text="Ex: Reserva de Emergência, Viagem...",
            fg_color="#181825",
            border_color="#313244",
        )
        self.entry_desc.pack(fill="x", padx=20, pady=(0, 10))

        # Valor Alvo
        ctk.CTkLabel(card_form, text="Valor Alvo (R$):", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.entry_alvo = ctk.CTkEntry(
            card_form,
            placeholder_text="Ex: 5000.00",
            fg_color="#181825",
            border_color="#313244",
        )
        self.entry_alvo.pack(fill="x", padx=20, pady=(0, 10))

        # Valor Inicial Guardado
        ctk.CTkLabel(
            card_form, text="Valor Já Guardado (R$):", font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=20, pady=(5, 2))
        self.entry_atual = ctk.CTkEntry(
            card_form,
            placeholder_text="0.00 (opcional)",
            fg_color="#181825",
            border_color="#313244",
        )
        self.entry_atual.pack(fill="x", padx=20, pady=(0, 10))

        # Prazo Estimado
        ctk.CTkLabel(card_form, text="Prazo Estimado:", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.entry_prazo = ctk.CTkEntry(
            card_form,
            placeholder_text="Ex: 6 meses, 1 ano, 18 meses...",
            fg_color="#181825",
            border_color="#313244",
        )
        self.entry_prazo.pack(fill="x", padx=20, pady=(0, 4))

        # Hint prazo
        ctk.CTkLabel(
            card_form,
            text="💡 Descreva livremente o prazo desejado",
            font=ctk.CTkFont(size=10),
            text_color="#585B70",
            anchor="w",
        ).pack(anchor="w", padx=20, pady=(0, 8))

        # Data Limite
        ctk.CTkLabel(card_form, text="Data Limite (opcional):", font=ctk.CTkFont(size=13)).pack(
            anchor="w", padx=20, pady=(5, 2)
        )
        self.entry_data_limite = ctk.CTkEntry(
            card_form,
            placeholder_text="DD/MM/AAAA",
            fg_color="#181825",
            border_color="#313244",
        )
        self.entry_data_limite.pack(fill="x", padx=20, pady=(0, 4))

        # Hint data
        ctk.CTkLabel(
            card_form,
            text="📅 Formato: DD/MM/AAAA",
            font=ctk.CTkFont(size=10),
            text_color="#585B70",
            anchor="w",
        ).pack(anchor="w", padx=20, pady=(0, 12))

        # Feedback
        self.lbl_feedback = ctk.CTkLabel(
            card_form,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.lbl_feedback.pack(fill="x", padx=20, pady=(0, 10))

        # Botão Criar Meta
        btn_criar = ctk.CTkButton(
            card_form,
            text="Criar Meta Financeira",
            fg_color="#A6E3A1",
            text_color="#1E1E2E",
            hover_color="#89D584",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._criar_meta,
        )
        btn_criar.pack(fill="x", padx=20, pady=(0, 20))

    # ==========================================================
    # LISTA DE METAS (DIREITA)
    # ==========================================================
    def _criar_painel_lista(self):
        card_lista = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="#1E1E2E",
            border_width=1,
            border_color="#313244",
        )
        card_lista.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        card_lista.grid_columnconfigure(0, weight=1)
        card_lista.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(card_lista, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))

        self.lbl_total_metas = ctk.CTkLabel(
            header,
            text="Minhas Metas Financeiras",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#CDD6F4",
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
            self._mostrar_feedback("O objetivo/descrição é obrigatório!", "#F38BA8")
            return

        if not alvo_str:
            self._mostrar_feedback("Informe o valor alvo!", "#F38BA8")
            return

        try:
            val_alvo = float(alvo_str)
            if val_alvo <= 0:
                self._mostrar_feedback("O valor alvo deve ser maior que zero!", "#F38BA8")
                return
        except ValueError:
            self._mostrar_feedback("Valor alvo inválido!", "#F38BA8")
            return

        val_atual = 0.0
        if atual_str:
            try:
                val_atual = float(atual_str)
            except ValueError:
                self._mostrar_feedback("Valor guardado inválido!", "#F38BA8")
                return

        try:
            self.dao.inserir(
                descricao=desc,
                valor_alvo=val_alvo,
                valor_atual=val_atual,
                prazo=prazo if prazo else None,
                data_limite=data_limite if data_limite else None,
            )
            self._mostrar_feedback(f"✓ Meta '{desc}' criada com sucesso!", "#A6E3A1")
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
            self._mostrar_feedback(f"Erro ao salvar: {e}", "#F38BA8")
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
            ctk.CTkLabel(
                self.scroll_metas,
                text="Nenhuma meta cadastrada ainda.\nDefina seu primeiro objetivo financeiro! 🎯",
                font=ctk.CTkFont(size=13),
                text_color="#6C7086",
                justify="center",
            ).pack(pady=40)
            return

        for m_dict in metas:
            self._renderizar_card_meta(m_dict)

    def _renderizar_card_meta(self, m_dict: dict):
        card = ctk.CTkFrame(
            self.scroll_metas,
            fg_color="#181825",
            corner_radius=12,
            border_width=1,
            border_color="#313244",
        )
        card.pack(fill="x", padx=5, pady=6)
        card.grid_columnconfigure(0, weight=1)

        # Header do card: Título e Botão Excluir
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(12, 4))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=m_dict["descricao"],
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#CDD6F4",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        btn_del = ctk.CTkButton(
            header,
            text="🗑️",
            width=28,
            height=28,
            fg_color="transparent",
            hover_color="#3E2633",
            text_color="#F38BA8",
            command=lambda mid=m_dict["id"]: self._excluir_meta(mid),
        )
        btn_del.grid(row=0, column=1, sticky="e")

        # Cálculo de progresso
        meta_obj = Meta(**m_dict)
        progresso = meta_obj.calcular_progresso()
        atingida = progresso >= 100.0

        cor_progresso = "#A6E3A1" if atingida else "#89B4FA"
        texto_status = "🎉 META ATINGIDA!" if atingida else f"{progresso:.1f}% concluído"

        sub_info = ctk.CTkFrame(card, fg_color="transparent")
        sub_info.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=2)
        sub_info.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            sub_info,
            text=f"R$ {m_dict['valor_atual']:.2f} de R$ {m_dict['valor_alvo']:.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#BAC2DE",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            sub_info,
            text=texto_status,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=cor_progresso,
        ).grid(row=0, column=1, sticky="e")

        # Barra de Progresso
        progress_bar = ctk.CTkProgressBar(
            card,
            progress_color=cor_progresso,
            fg_color="#313244",
            height=10,
            corner_radius=5,
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
            cor_falta = "#A6E3A1"
        else:
            info_falta = f"Faltam: R$ {falta:.2f}"
            cor_falta = "#F9E2AF"

        ctk.CTkLabel(
            sub_falta,
            text=info_falta,
            font=ctk.CTkFont(size=11, weight="bold"),
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
                        font=ctk.CTkFont(size=11),
                        text_color="#89B4FA",
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
            font=ctk.CTkFont(size=11),
            text_color="#6C7086",
        ).grid(row=0, column=0, sticky="w")

        # Botões de aporte rápido
        aportes_box = ctk.CTkFrame(footer, fg_color="transparent")
        aportes_box.grid(row=0, column=1, sticky="e")

        for valor, label in [(50.0, "+R$50"), (100.0, "+R$100")]:
            ctk.CTkButton(
                aportes_box,
                text=label,
                width=56,
                height=26,
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color="#313244",
                hover_color="#45475A",
                text_color="#A6E3A1",
                command=lambda mid=m_dict["id"], v=valor: self._aporte_rapido(mid, v),
            ).pack(side="left", padx=2)

        ctk.CTkButton(
            aportes_box,
            text="+ Outro",
            width=60,
            height=26,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#313244",
            hover_color="#45475A",
            text_color="#89B4FA",
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
