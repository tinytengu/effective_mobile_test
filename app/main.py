import os
import argparse
from datetime import datetime, timezone
from contextlib import contextmanager

import colorama  # type: ignore
from colorama import Fore, Back, Style


from app.db.jsonfile import JsonFileDatabase
from app.models import TransactionType, Transaction
from app.utils import calculate_expenses, term_clear

colorama.init(autoreset=True)

DB_FILENAME: str | None = None
TEXT_CHOOSE = Back.LIGHTBLUE_EX + "\n[Выберите действие]" + Style.RESET_ALL


@contextmanager
def get_db():
    """Database context manager. Provides an instance of JsonFileDatabase to a view functions."""
    global DB_FILENAME

    db = JsonFileDatabase()
    db.connect(filename=DB_FILENAME)

    try:
        yield db
    finally:
        db.disconnect()


def view(func):
    """Simple wrapper for view functions.

    It resets terminal styles and clears the terminal before calling the decorated function.
    """

    def wrapper(*args, **kwargs):
        print(Style.RESET_ALL)
        term_clear()

        return func(*args, **kwargs)

    return wrapper


def main():
    global DB_FILENAME

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", type=str, required=True)
    parser.add_argument("--create", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.filename):
        if args.create:
            with open(args.filename, "w") as file:
                file.write("[]")
        else:
            print("Файл {} не найден".format(args.filename))
            exit()

    print("SET DB_FILENAME")
    DB_FILENAME = args.filename

    home_view()


@view
def home_view() -> None:
    """
    Displays the main menu for the application.
    """
    print(TEXT_CHOOSE)
    print("1. Посмотреть баланс")
    print("2. Посмотреть транзакции")
    print("3. Добавить транзакцию")
    print("q. Выйти")

    choice = input("> ")
    if choice == "1":
        balance_view()
    elif choice == "2":
        transactions_view()
    elif choice == "3":
        transaction_add_view()
    elif choice == "q":
        exit()
    else:
        home_view()


@view
def balance_view():
    """
    Displays user balance view.
    """
    with get_db() as database:
        balance = calculate_expenses(database.get_transactions())

    print(
        "Ваш баланс: {}{:.02f} руб.".format(
            (Fore.GREEN if balance >= 0 else Fore.RED), balance
        )
    )
    input()
    home_view()


@view
def transactions_view():
    """
    Displays user transactions view.
    """
    with get_db() as database:
        transactions = sorted(
            database.get_transactions(),
            key=lambda transaction: transaction.date,
            reverse=True,
        )
    expenses_amount = calculate_expenses(transactions)

    print(
        "Транзакции ({}) {}[{}{:.02f} руб.]".format(
            len(transactions),
            Fore.GREEN if expenses_amount > 0 else Fore.RED,
            "+" if expenses_amount > 0 else "",
            expenses_amount,
        )
    )

    for idx, transaction in enumerate(transactions):
        print(
            (Fore.GREEN if transaction.type == TransactionType.INCOME else Fore.RED)
            + "{}. [{}] {}{:.02f} руб. {}".format(
                idx + 1,
                transaction.date.strftime("%d.%m.%Y %H:%M:%S"),
                "+" if transaction.type == TransactionType.INCOME else "-",
                transaction.amount,
                f"({transaction.description})" if transaction.description else "",
            )
        )

    print(TEXT_CHOOSE)
    if len(transactions) > 0:
        print(
            "{}. Посмотреть детали транзакции".format(
                "1" if len(transactions) == 1 else f"1-{len(transactions)}"
            )
        )
    print("+. Добавить транзакцию")
    print("<. Назад")
    print("q. Выход")

    choice = input("> ")
    if choice.isnumeric():
        transaction_idx = int(choice)
        if transaction_idx < 1 or transaction_idx > len(transactions):
            print("Некорректный ввод")
            transactions_view()
        else:
            transaction_detail_view(transaction=transactions[transaction_idx - 1])
    elif choice == "+":
        transaction_add_view()
    elif choice == "<":
        home_view()
    elif choice == "q":
        exit()
    else:
        transactions_view()


@view
def transaction_detail_view(transaction: Transaction):
    """
    Displays detailed information about a specific transaction.

    Parameters:
        - transaction (Transaction): The specific transaction object whose details are to be displayed.
    """
    print(
        Back.LIGHTBLUE_EX
        + "[Транзакция #{}]".format(str(transaction.id))
        + Style.RESET_ALL,
        f"Дата: {transaction.date.strftime('%d.%m.%Y %H:%M:%S')}",
        f"Сумма: {"-" if transaction.type == TransactionType.EXPENSE else ""}{transaction.amount:.02f} руб.",
        f"Описание: {transaction.description}",
        sep="\n",
    )

    print(TEXT_CHOOSE)
    print(Fore.YELLOW + "1. Изменить дату")
    print(Fore.YELLOW + "2. Изменить сумму")
    print(Fore.YELLOW + "3. Изменить описание")
    print(Fore.RED + "4. Удалить")
    print(Style.RESET_ALL + "<. Назад")
    print("q. Выход")

    choice = input("> ")
    if choice == "1":
        transaction_edit_date_view(transaction=transaction)
    elif choice == "2":
        transaction_edit_amount_view(transaction=transaction)
    elif choice == "3":
        transaction_edit_description_view(transaction=transaction)
    elif choice == "4":
        with get_db() as database:
            database.delete_transaction(transaction.id)
            database.save()
        transactions_view()
    elif choice == "<":
        transactions_view()
    elif choice == "q":
        exit()
    else:
        transaction_detail_view(transaction=transaction)


@view
def transaction_edit_date_view(transaction: Transaction):
    """
    Displays transaction date edit view.

    Parameters:
        - transaction (Transaction): The specific transaction object whose details are to be displayed.
    """
    print(
        Back.LIGHTBLUE_EX
        + "[Транзакция #{}]".format(str(transaction.id))
        + Style.RESET_ALL
    )

    expense_date = None

    date = input("Введите дату (ДД.ММ.ГГГГ ЧЧ:ММ:СС) или оставьте пустым: ")
    if len(date) == 0:
        expense_date = datetime.now(tz=timezone.utc)
    else:
        try:
            expense_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
            expense_date = expense_date.replace(tzinfo=timezone.utc)
        except ValueError:
            print("Некорректный ввод")
            transaction_edit_date_view(transaction=transaction)
            return

    with get_db() as database:
        database.change_transaction(
            transaction.id, transaction.clone(date=expense_date)
        )
        database.save()
        transaction = database.get_transaction(transaction.id)

    transaction_detail_view(transaction=transaction)


@view
def transaction_edit_amount_view(
    transaction: Transaction,
):
    """
    Displays transaction amount edit view.

    Parameters:
        - transaction (Transaction): The specific transaction object whose details are to be displayed.
    """
    print(
        Back.LIGHTBLUE_EX
        + "[Транзакция #{}]".format(str(transaction.id))
        + Style.RESET_ALL
    )

    value = input("Введите сумму (отрицательное значение для расходов): ")
    if not value.isnumeric() and not value[0] == "-":
        return transaction_edit_amount_view(transaction=transaction)

    expense_amount = int(value)
    if expense_amount == 0:
        return transaction_edit_amount_view(transaction=transaction)

    with get_db() as database:
        database.change_transaction(
            transaction.id, transaction.clone(amount=expense_amount)
        )
        database.save()
        transaction = database.get_transaction(transaction.id)

    transaction_detail_view(transaction=transaction)


@view
def transaction_edit_description_view(
    database: JsonFileDatabase, transaction: Transaction
):
    """
    Displays transaction description edit view.

    Parameters:
        - transaction (Transaction): The specific transaction object whose details are to be displayed.
    """
    print(
        Back.LIGHTBLUE_EX
        + "[Транзакция #{}]".format(str(transaction.id))
        + Style.RESET_ALL
    )

    expense_description = input("Введите описание: ")

    with get_db() as database:
        database.change_transaction(
            transaction.id, transaction.clone(description=expense_description)
        )
        database.save()
        transaction = database.get_transaction(transaction.id)

    transaction_detail_view(transaction=transaction)


@view
def transaction_add_view():
    """
    Displays transaction add view.
    """
    print("[Добавление транзакции]")

    expense_amount = 0
    expense_date = None

    while True:
        value = input("Введите сумму (отрицательное значение для расходов): ")
        if len(value) == 0:
            print("Некорректный ввод")
            continue

        if not value.isnumeric() and not value[0] == "-":
            print("Некорректный ввод")
            continue

        expense_amount = int(value)
        if expense_amount == 0:
            print("Некорректный ввод")
            continue
        break

    while True:
        date = input("Введите дату (ДД.ММ.ГГГГ ЧЧ:ММ:СС) или оставьте пустым: ")
        if len(date) == 0:
            expense_date = None
            break

        try:
            expense_date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
            expense_date = expense_date.replace(tzinfo=timezone.utc)
        except ValueError:
            print("Некорректный ввод")
            continue
        break

    expense_type = (
        TransactionType.EXPENSE if expense_amount < 0 else TransactionType.INCOME
    )
    expense_amount = abs(expense_amount)
    expense_date = expense_date or datetime.now(tz=timezone.utc)
    expense_description = input("Введите описание: ")

    add_transaction_check_view(
        expense_type=expense_type,
        expense_amount=expense_amount,
        expense_description=expense_description,
        expense_date=expense_date,
    )


@view
def add_transaction_check_view(
    expense_type: TransactionType,
    expense_amount: float,
    expense_description: str,
    expense_date: datetime,
    database=get_db,
):
    """
    Displays transaction add view confirmation.

    Parameters:
        - expense_type (TransactionType)
        - expense_amount (float)
        - expense_description (str)
        - expense_date (datetime)
    """
    print(
        "Тип: {}".format(
            (Fore.GREEN if expense_type == TransactionType.INCOME else Fore.RED)
            + ("Доход" if expense_type == TransactionType.INCOME else "Расход")
        )
    )
    print(Style.RESET_ALL)
    print("Сумма: {:.02f} руб.".format(expense_amount))
    print("Дата: {}.".format(expense_date.strftime("%d.%m.%Y %H:%M:%S")))
    print("Описание: {}".format(expense_description))

    answer = input("Создать? (y/n) ")
    if answer == "y":
        with get_db() as database:
            database.add_transaction(
                Transaction.create(expense_type, expense_amount, expense_description)
            )
            database.save()

    transactions_view()
