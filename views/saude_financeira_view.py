import customtkinter as ctk

# Configuração global de aparência
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class SaudeFinanceiraView(ctk.CTkFrame):

    def __init__(self, parent, data_mock=None):
        super().__init__(parent, fg_color="transparent")

        # Dados de teste (Mock)
        self.data = data_mock or {
            "score": 720,
            "status_texto": "Saúde Financeira Boa",
            "vazamento": {
                "categoria": "Alimentação",
                "limite": 800.00,
                "atual": 850.00,
            },
            "plano_acao": [
                {
                    "missao": "Reduzir gastos com Alimentação em R$ 50",
                    "pontos": "+30 pts",
                    "concluida": False,
                },
                {
                    "missao": "Receber pagamento pendente de João Santos",
                    "pontos": "+50 pts",
                    "concluida": False,
                },
                {
                    "missao": "Guardar R$ 200 na Reserva de Emergência",
                    "pontos": "+20 pts",
                    "concluida": True,
                },
            ],
            "metas": [
                {
                    "nome": "Reserva de Emergência",
                    "prazo": "CURTO",
                    "atual": 2500,
                    "alvo": 5000,
                },
                {
                    "nome": "Novo Notebook PJ",
                    "prazo": "MÉDIO",
                    "atual": 1000,
                    "alvo": 4000,
                },
                {
                    "nome": "Entrada do Imóvel",
                    "prazo": "LONGO",
                    "atual": 5000,
                    "alvo": 30000,
                },
            ],
        }

        # Configuração do Grid Principal
        self.grid_columnconfigure((0, 1), weight=1, pad=15)
        self.grid_rowconfigure((0, 1), weight=1, pad=15)

        # Inicialização dos Componentes
        self._build_hero_score()
        self._build_alerta_vazamento()
        self._build_plano_acao()
        self._build_metas_prazos()

    def _build_hero_score(self):
        """Card Principal: Score de Saúde (Hero)"""
        frame_score = ctk.CTkFrame(
            self, corner_radius=15, fg_color="#1E1E2E", border_width=1, border_color="#313244"
        )
        frame_score.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        title = ctk.CTkLabel(
            frame_score,
            text="SAÚDE FINANCEIRA",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        )
        title.pack(anchor="w", padx=20, pady=(15, 5))

        # Valor do Score
        score_val = ctk.CTkLabel(
            frame_score,
            text=str(self.data["score"]),
            font=ctk.CTkFont(size=56, weight="bold"),
            text_color="#A6E3A1",  # Verde suave
        )
        score_val.pack(anchor="w", padx=20, pady=0)

        # Barra de Progresso
        progresso = ctk.CTkProgressBar(
            frame_score,
            height=12,
            corner_radius=6,
            progress_color="#A6E3A1",
            fg_color="#313244",
        )
        progresso.set(self.data["score"] / 1000)
        progresso.pack(fill="x", padx=20, pady=(5, 10))

        status_lbl = ctk.CTkLabel(
            frame_score,
            text=f"• {self.data['status_texto']} (Escala 0-1000)",
            font=ctk.CTkFont(size=13),
            text_color="#BAC2DE",
        )
        status_lbl.pack(anchor="w", padx=20, pady=(0, 15))

    def _build_alerta_vazamento(self):
        """Card do Alerta de Vazamento de Orçamento"""
        frame_vaz = ctk.CTkFrame(
            self, corner_radius=15, fg_color="#2A1B28", border_width=1, border_color="#F38BA8"
        )
        frame_vaz.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        title = ctk.CTkLabel(
            frame_vaz,
            text="⚠️ ALERTA DE VAZAMENTO",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#F38BA8",
        )
        title.pack(anchor="w", padx=20, pady=(15, 5))

        vaz = self.data["vazamento"]
        msg = f"Sua categoria '{vaz['categoria']}' estourou o limite!"
        detalhe = f"Gasto Atual: R$ {vaz['atual']:.2f} | Limite: R$ {vaz['limite']:.2f}"

        lbl_msg = ctk.CTkLabel(
            frame_vaz,
            text=msg,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#CDD6F4",
            justify="left",
        )
        lbl_msg.pack(anchor="w", padx=20, pady=(5, 2))

        lbl_detalhes = ctk.CTkLabel(
            frame_vaz,
            text=detalhe,
            font=ctk.CTkFont(size=13),
            text_color="#A6ADC8",
        )
        lbl_detalhes.pack(anchor="w", padx=20, pady=(0, 15))

    def _build_plano_acao(self):
        """Card do Plano de Ação (Missões)"""
        frame_plano = ctk.CTkFrame(
            self, corner_radius=15, fg_color="#1E1E2E", border_width=1, border_color="#313244"
        )
        frame_plano.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        title = ctk.CTkLabel(
            frame_plano,
            text="🎯 PLANO DE AÇÃO (DIRECIONAMENTO)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        for item in self.data["plano_acao"]:
            item_frame = ctk.CTkFrame(frame_plano, fg_color="#181825", corner_radius=8)
            item_frame.pack(fill="x", padx=15, pady=4)

            chk = ctk.CTkCheckBox(
                item_frame,
                text=item["missao"],
                font=ctk.CTkFont(size=13),
                text_color="#CDD6F4" if not item["concluida"] else "#585B70",
                checkbox_height=18,
                checkbox_width=18,
            )
            if item["concluida"]:
                chk.select()
            chk.pack(side="left", padx=10, pady=8)

            badge = ctk.CTkLabel(
                item_frame,
                text=item["pontos"],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#89B4FA",
            )
            badge.pack(side="right", padx=10)

    def _build_metas_prazos(self):
        """Card de Metas por Prazo"""
        frame_metas = ctk.CTkFrame(
            self, corner_radius=15, fg_color="#1E1E2E", border_width=1, border_color="#313244"
        )
        frame_metas.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        title = ctk.CTkLabel(
            frame_metas,
            text="🚀 METAS POR PRAZO",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A6ADC8",
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        for m in self.data["metas"]:
            m_frame = ctk.CTkFrame(frame_metas, fg_color="transparent")
            m_frame.pack(fill="x", padx=20, pady=5)

            # Linha de Texto (Nome e Prazo)
            header = ctk.CTkFrame(m_frame, fg_color="transparent")
            header.pack(fill="x")

            lbl_nome = ctk.CTkLabel(
                header,
                text=m["nome"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#CDD6F4",
            )
            lbl_nome.pack(side="left")

            lbl_prazo = ctk.CTkLabel(
                header,
                text=f"[{m['prazo']}]",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#F9E2AF",
            )
            lbl_prazo.pack(side="right")

            # Barra de progresso individual
            pct = m["atual"] / m["alvo"]
            bar = ctk.CTkProgressBar(
                m_frame,
                height=8,
                corner_radius=4,
                progress_color="#89B4FA",
                fg_color="#313244",
            )
            bar.set(pct)
            bar.pack(fill="x", pady=(2, 2))


# =====================================================================
# CÓDIGO PARA EXECUÇÃO ISOLADA / TESTE DA VIEW
# =====================================================================
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Testando View - Saúde Financeira")
    app.geometry("900x520")
    app.resizable(False, False)

    # Instancia a View diretamente na janela principal
    view = SaudeFinanceiraView(app)
    view.pack(expand=True, fill="both", padx=20, pady=20)

    app.mainloop()