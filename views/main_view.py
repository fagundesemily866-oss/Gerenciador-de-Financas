"""
Camada de View da aplicação.

Contém apenas a interface gráfica (Tkinter/ttk padrão, sem estilização
personalizada). A View não conhece o Model diretamente: toda operação
passa pelo TransactionController, que valida os dados e executa as
regras de negócio.
"""
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk
from typing import Optional

from controllers.transaction_controller import TransactionController
from models.transaction import TransactionModel


def format_currency(value: float) -> str:
    """Formata um número float no padrão monetário brasileiro (R$ 0.000,00)."""
    formatted = f"{value:,.2f}"
    # Troca temporária de separadores para obter o formato "1.234,56"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def parse_currency(text: str) -> str:
    """Converte um texto formatado como moeda (R$ 1.234,56) de volta para '1234.56'."""
    cleaned = text.replace("R$", "").strip()
    cleaned = cleaned.replace(".", "").replace(",", ".")
    return cleaned


class MainView(tk.Frame):
    """Janela principal do Gerenciador de Finanças Pessoais."""

    def __init__(self, master: tk.Tk, controller: TransactionController):
        super().__init__(master)
        self.master = master
        self.controller = controller
        self.selected_id: Optional[int] = None

        self.master.title("Gerenciador de Finanças Pessoais")
        self.master.geometry("840x580")
        self.master.minsize(780, 540)

        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_form_section()
        self._build_buttons_section()
        self._build_filters_section()
        self._build_table_section()
        self._build_summary_section()

        self.refresh()

    # ------------------------------------------------------------------
    # Construção da interface (widgets padrão, sem customização visual)
    # ------------------------------------------------------------------
    def _build_form_section(self) -> None:
        form_frame = tk.LabelFrame(self, text="Dados da Transação")
        form_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form_frame, text="Descrição:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.description_entry = tk.Entry(form_frame, width=32)
        self.description_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Valor (R$):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.value_entry = tk.Entry(form_frame, width=15)
        self.value_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        tk.Label(form_frame, text="Tipo:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.type_combobox = ttk.Combobox(
            form_frame, values=TransactionModel.TYPES, state="readonly", width=15
        )
        self.type_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.type_combobox.current(0)

        tk.Label(form_frame, text="Categoria:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.category_combobox = ttk.Combobox(
            form_frame, values=TransactionModel.CATEGORIES, state="readonly", width=15
        )
        self.category_combobox.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.category_combobox.current(0)

        tk.Label(form_frame, text="Data (AAAA-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = tk.Entry(form_frame, width=15)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.date_entry.insert(0, date.today().isoformat())

    def _build_buttons_section(self) -> None:
        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(button_frame, text="Adicionar", width=14, command=self._on_add).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Atualizar", width=14, command=self._on_update).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Excluir", width=14, command=self._on_delete).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Limpar Campos", width=14, command=self._clear_form).pack(
            side=tk.LEFT, padx=5
        )

    def _build_filters_section(self) -> None:
        filter_frame = tk.LabelFrame(self, text="Filtros")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(filter_frame, text="Tipo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.filter_type_combobox = ttk.Combobox(
            filter_frame, values=("Todos",) + TransactionModel.TYPES, state="readonly", width=15
        )
        self.filter_type_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.filter_type_combobox.current(0)
        self.filter_type_combobox.bind("<<ComboboxSelected>>", lambda event: self.refresh())

        tk.Label(filter_frame, text="Categoria:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.filter_category_combobox = ttk.Combobox(
            filter_frame, values=("Todas",) + TransactionModel.CATEGORIES, state="readonly", width=15
        )
        self.filter_category_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.filter_category_combobox.current(0)
        self.filter_category_combobox.bind("<<ComboboxSelected>>", lambda event: self.refresh())

        tk.Button(filter_frame, text="Limpar Filtros", command=self._clear_filters).grid(
            row=0, column=4, padx=5, pady=5
        )

    def _build_table_section(self) -> None:
        table_frame = tk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ("id", "description", "value", "type", "category", "date")
        headers = {
            "id": "ID",
            "description": "Descrição",
            "value": "Valor",
            "type": "Tipo",
            "category": "Categoria",
            "date": "Data",
        }
        widths = {"id": 40, "description": 230, "value": 110, "type": 90, "category": 130, "date": 100}

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for column in columns:
            self.tree.heading(column, text=headers[column])
            self.tree.column(column, width=widths[column], anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_select_row)

    def _build_summary_section(self) -> None:
        summary_frame = tk.LabelFrame(self, text="Resumo")
        summary_frame.pack(fill=tk.X)

        self.income_label = tk.Label(summary_frame, text="Receitas: R$ 0,00")
        self.income_label.grid(row=0, column=0, padx=15, pady=5)

        self.expense_label = tk.Label(summary_frame, text="Despesas: R$ 0,00")
        self.expense_label.grid(row=0, column=1, padx=15, pady=5)

        self.balance_label = tk.Label(summary_frame, text="Saldo: R$ 0,00")
        self.balance_label.grid(row=0, column=2, padx=15, pady=5)

    # ------------------------------------------------------------------
    # Eventos da interface
    # ------------------------------------------------------------------
    def _on_add(self) -> None:
        success, message = self.controller.add_transaction(
            self.description_entry.get(),
            self.value_entry.get(),
            self.type_combobox.get(),
            self.category_combobox.get(),
            self.date_entry.get(),
        )
        self._handle_result(success, message)

    def _on_update(self) -> None:
        if self.selected_id is None:
            messagebox.showwarning("Atenção", "Selecione uma transação na tabela para atualizar.")
            return

        success, message = self.controller.update_transaction(
            self.selected_id,
            self.description_entry.get(),
            self.value_entry.get(),
            self.type_combobox.get(),
            self.category_combobox.get(),
            self.date_entry.get(),
        )
        self._handle_result(success, message)

    def _on_delete(self) -> None:
        if self.selected_id is None:
            messagebox.showwarning("Atenção", "Selecione uma transação na tabela para excluir.")
            return

        confirmed = messagebox.askyesno(
            "Confirmar exclusão", "Tem certeza de que deseja excluir esta transação?"
        )
        if not confirmed:
            return

        success, message = self.controller.delete_transaction(self.selected_id)
        self._handle_result(success, message)

    def _on_select_row(self, event) -> None:
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.selected_id = int(values[0])

        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, values[1])

        self.value_entry.delete(0, tk.END)
        self.value_entry.insert(0, parse_currency(values[2]))

        self.type_combobox.set(values[3])
        self.category_combobox.set(values[4])

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, values[5])

    # ------------------------------------------------------------------
    # Métodos auxiliares
    # ------------------------------------------------------------------
    def _handle_result(self, success: bool, message: str) -> None:
        if success:
            messagebox.showinfo("Sucesso", message)
            self._clear_form()
            self.refresh()
        else:
            messagebox.showerror("Erro", message)

    def _clear_form(self) -> None:
        self.selected_id = None
        self.description_entry.delete(0, tk.END)
        self.value_entry.delete(0, tk.END)
        self.type_combobox.current(0)
        self.category_combobox.current(0)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().isoformat())

        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def _clear_filters(self) -> None:
        self.filter_type_combobox.current(0)
        self.filter_category_combobox.current(0)
        self.refresh()

    def refresh(self) -> None:
        """Recarrega a tabela e o resumo financeiro a partir do Controller."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        type_filter = self.filter_type_combobox.get()
        category_filter = self.filter_category_combobox.get()

        transactions = self.controller.list_transactions(type_filter, category_filter)
        for transaction in transactions:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    transaction.id,
                    transaction.description,
                    format_currency(transaction.value),
                    transaction.type,
                    transaction.category,
                    transaction.date,
                ),
            )

        total_income, total_expense, balance = self.controller.get_summary(type_filter, category_filter)
        self.income_label.config(text=f"Receitas: {format_currency(total_income)}")
        self.expense_label.config(text=f"Despesas: {format_currency(total_expense)}")
        self.balance_label.config(text=f"Saldo: {format_currency(balance)}")
