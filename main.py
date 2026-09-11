"""
Gerenciador de Finanças Pessoais
=================================

Ponto de entrada da aplicação. Responsável apenas por "montar" as três
camadas do padrão MVC e iniciar o loop principal da interface gráfica.

Arquitetura MVC:
    Model      -> models/database.py, models/transaction.py
    View       -> views/main_view.py
    Controller -> controllers/transaction_controller.py

Como executar:
    python main.py

Requisitos:
    Apenas a biblioteca padrão do Python (Tkinter + sqlite3).
"""
import tkinter as tk

from controllers.transaction_controller import TransactionController
from models.database import Database
from models.transaction import TransactionModel
from views.main_view import MainView


def main() -> None:
    # ---- Model: conexão com o banco de dados e repositório ----
    database = Database(db_path="data/finance.db")
    transaction_model = TransactionModel(database)

    # ---- Controller: regras de negócio, injeta o Model ----
    controller = TransactionController(transaction_model)

    # ---- View: interface gráfica, injeta o Controller ----
    root = tk.Tk()
    MainView(root, controller)

    try:
        root.mainloop()
    finally:
        database.close()


if __name__ == "__main__":
    main()
