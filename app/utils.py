import os
import platform

from app.models import Transaction, TransactionType


def calculate_expenses(transactions: list[Transaction]) -> float:
    """
    Calculates the total expenses from a list of ExpensesTransaction objects.

    Parameters:
        transactions (list[ExpensesEvent]): A list of ExpensesEvent objects containing the transactions to be considered.

    Returns:
        float: The total expenses calculated from the given transactions.
    """
    return float(
        sum(
            [
                abs(transaction.amount)
                if transaction.type == TransactionType.INCOME
                else -abs(transaction.amount)
                for transaction in transactions
            ]
        )
    )


def term_clear():
    """
    Clears the terminal screen.

    Returns:
        str: The command used to clear the terminal.

    Raises:
        Exception: If the platform is neither Windows nor Unix-based.

    This function checks the platform's system and sets the command to either "cls" for Windows or "clear" for Unix-based systems. It then uses the os.system() function to execute the command and clear the terminal. The function finally returns the command used to clear the terminal.

    """
    command = "cls" if platform.system() == "Windows" else "clear"
    os.system(command)
    return command
