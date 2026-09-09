"""
Camada de Controller da aplicação.

Faz a mediação entre a View e o Model: recebe dados brutos da interface
(strings vindas de campos de texto), valida e converte esses dados,
aplica as regras de negócio e delega a persistência ao Model.

A View nunca deve falar diretamente com o Model — sempre passa pelo
Controller. Isso mantém a lógica de validação centralizada e reutilizável.
"""
from datetime import datetime
from typing import List, Optional, Tuple

from models.transaction import Transaction, TransactionModel


class TransactionController:
    """Contém as regras de negócio para manipulação de transações financeiras."""

    def __init__(self, model: TransactionModel):
        self.model = model

    # ------------------------------------------------------------------
    # Validação
    # ------------------------------------------------------------------
    @staticmethod
    def _validate(
        description: str,
        value_str: str,
        type_: str,
        category: str,
        date_str: str,
    ) -> Tuple[bool, str, Optional[float]]:
        """
        Valida os dados de entrada de uma transação.
        Retorna (é_válido, mensagem_de_erro, valor_convertido).
        """
        if not description or not description.strip():
            return False, "A descrição não pode estar vazia.", None

        if len(description.strip()) > 120:
            return False, "A descrição deve ter no máximo 120 caracteres.", None

        try:
            # Aceita tanto '.' quanto ',' como separador decimal.
            value = float(str(value_str).strip().replace(",", "."))
        except (ValueError, AttributeError):
            return False, "O valor informado é inválido. Utilize apenas números.", None

        if value <= 0:
            return False, "O valor deve ser maior que zero.", None

        if type_ not in TransactionModel.TYPES:
            return False, "Selecione um tipo de transação válido (Receita ou Despesa).", None

        if category not in TransactionModel.CATEGORIES:
            return False, "Selecione uma categoria válida.", None

        try:
            datetime.strptime(date_str.strip(), "%Y-%m-%d")
        except (ValueError, AttributeError):
            return False, "Data inválida. Utilize o formato AAAA-MM-DD.", None

        return True, "", value

    # ------------------------------------------------------------------
    # Operações expostas para a View
    # ------------------------------------------------------------------
    def add_transaction(
        self, description: str, value_str: str, type_: str, category: str, date_str: str
    ) -> Tuple[bool, str]:
        """Valida e cadastra uma nova transação."""
        is_valid, message, value = self._validate(description, value_str, type_, category, date_str)
        if not is_valid:
            return False, message

        transaction = Transaction(
            description=description.strip(),
            value=value,
            type=type_,
            category=category,
            date=date_str.strip(),
        )
        self.model.add(transaction)
        return True, "Transação adicionada com sucesso."

    def update_transaction(
        self,
        transaction_id: int,
        description: str,
        value_str: str,
        type_: str,
        category: str,
        date_str: str,
    ) -> Tuple[bool, str]:
        """Valida e atualiza uma transação existente."""
        if self.model.get_by_id(transaction_id) is None:
            return False, "Transação não encontrada. Ela pode já ter sido excluída."

        is_valid, message, value = self._validate(description, value_str, type_, category, date_str)
        if not is_valid:
            return False, message

        transaction = Transaction(
            id=transaction_id,
            description=description.strip(),
            value=value,
            type=type_,
            category=category,
            date=date_str.strip(),
        )
        self.model.update(transaction)
        return True, "Transação atualizada com sucesso."

    def delete_transaction(self, transaction_id: int) -> Tuple[bool, str]:
        """Remove uma transação, validando previamente sua existência."""
        if self.model.get_by_id(transaction_id) is None:
            return False, "Transação não encontrada. Ela pode já ter sido excluída."

        self.model.delete(transaction_id)
        return True, "Transação excluída com sucesso."

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """Recupera uma transação específica pelo ID."""
        return self.model.get_by_id(transaction_id)

    def list_transactions(
        self, type_filter: Optional[str] = None, category_filter: Optional[str] = None
    ) -> List[Transaction]:
        """Lista as transações, aplicando filtros opcionais de tipo e categoria."""
        return self.model.get_all(type_filter, category_filter)

    def get_summary(
        self, type_filter: Optional[str] = None, category_filter: Optional[str] = None
    ) -> Tuple[float, float, float]:
        """
        Calcula o resumo financeiro (total de receitas, total de despesas e saldo)
        respeitando os filtros aplicados na listagem.
        """
        transactions = self.list_transactions(type_filter, category_filter)
        total_income = sum(t.value for t in transactions if t.type == "Receita")
        total_expense = sum(t.value for t in transactions if t.type == "Despesa")
        balance = total_income - total_expense
        return total_income, total_expense, balance
