import json
import uuid
from typing import override

from .base import BaseDatabase
from app.models import Transaction


class JsonFileDatabase(BaseDatabase):
    """
    A database that reads and writes transactions to a JSON file.

    Attributes:
        filename (str): The name of the JSON file to be used as the database.
        _transactions (list[Transaction]): A list of `Transaction` objects, each representing a transaction in the JSON file.
    """

    @override
    def connect(self, **kwargs):
        """
        Connects to the database by reading the JSON file specified by the 'filename' parameter.

        Parameters:
            **kwargs: A dictionary of keyword arguments. The 'filename' key is required.

        Raises:
            AttributeError: If 'filename' is not provided in the kwargs dictionary.
        """
        if not (filename := kwargs.get("filename")):
            raise AttributeError("No filename provided")

        self.filename = filename
        self._transactions = self.read()

    @override
    def disconnect(self) -> None:
        """
        Disconnects from the database by setting the filename and transactions attributes to None.

        This method is called when the database connection needs to be closed. It ensures that the filename and transactions attributes are properly cleaned up to avoid memory leaks or other issues.
        """
        self.filename = None
        self._transactions = None

    @override
    def read(self) -> list[Transaction]:
        """
        Reads the transactions from the JSON file specified by the 'filename' attribute.

        Returns:
            A list of `Transaction` objects, each representing a transaction in the JSON file.
        """
        with open(self.filename, "r", encoding="UTF-8") as file:
            data: list[dict] = json.load(file)

        return [Transaction.from_dict(transaction) for transaction in data]

    @override
    def write(self, transactions: list[Transaction], read_again: bool = True) -> None:
        """
        Writes the transactions to the JSON file specified by the 'filename' attribute.

        Parameters:
            - transactions (list[Transaction]): A list of `Transaction` objects, each representing a transaction to be written to the JSON file.
            - read_again (bool, optional): If True, the transactions will be re-read from the JSON file after writing. Default is True.

        Raises:
            - ValueError: If the JSON file cannot be written to.
        """
        with open(self.filename, "w", encoding="UTF-8") as file:
            json.dump(
                [transaction.to_dict() for transaction in transactions],
                file,
                indent=2,
                ensure_ascii=False,
            )

        if read_again:
            self._transactions = self.read()

    @override
    def save(self):
        """
        Saves the transactions to the JSON file specified by the 'filename' attribute.

        This method is called when the database connection needs to be saved. It ensures that the transactions are properly written to the JSON file to avoid data loss.

        Raises:
            ValueError: If the JSON file cannot be written to.
        """
        self.write(self._transactions)

    def clear(self) -> None:
        """
        Clears all transactions from the database.

        This method removes all transactions from the JSON file and saves the changes.
        """
        self._transactions = []
        self.save()

    @override
    def get_transactions(self) -> list[Transaction]:
        """
        Retrieves all transactions from the database.

        Returns:
            A list of `Transaction` objects, each representing a transaction in the JSON file.
        """
        return self._transactions or []

    @override
    def get_transaction(self, transaction_id: uuid.UUID) -> Transaction:
        """
        Retrieves a specific transaction from the database.

        Parameters:
            - transaction_id (uuid.UUID): The unique identifier of the transaction to be retrieved.

        Returns:
            - Transaction: The requested transaction object.

        Raises:
            - ValueError: If the transaction with the given id is not found in the JSON file.
            - ValueError: If there are multiple transactions with the same id in the JSON file.
        """
        transactions = [
            transaction
            for transaction in self.get_transactions()
            if transaction.id == transaction_id
        ]

        if not transactions:
            raise ValueError(f"Transaction with id {transaction_id} not found")

        if len(transactions) > 1:
            raise ValueError(f"Multiple transactions with id {transaction_id} found")

        return transactions[0]

    @override
    def add_transaction(self, transaction: Transaction) -> None:
        """
        Adds a new transaction to the database.

        Parameters:
            - transaction (Transaction): The new transaction to be added to the database.

        Raises:
            - ValueError: If the transaction cannot be added to the database.
        """
        self._transactions.append(transaction)

    @override
    def delete_transaction(self, transaction_id: uuid.UUID) -> Transaction:
        """
        Deletes a specific transaction from the database.

        Parameters:
            - transaction_id (uuid.UUID): The unique identifier of the transaction to be deleted.

        Returns:
            - Transaction: The deleted transaction object.

        Raises:
        -    ValueError: If the transaction with the given id is not found in the JSON file.
        """
        transaction = self.get_transaction(transaction_id)
        self._transactions.remove(transaction)
        return transaction

    @override
    def change_transaction(
        self, transaction_id: uuid.UUID, new_transaction: Transaction
    ):
        """
        Changes the details of a specific transaction in the database.

        Parameters:
            - transaction_id (uuid.UUID): The unique identifier of the transaction to be changed.
            - new_transaction (Transaction): The new details of the transaction to be updated.

        Raises:
            - ValueError: If the transaction with the given id is not found in the JSON file.
        """
        self.delete_transaction(transaction_id)
        self.add_transaction(new_transaction)
