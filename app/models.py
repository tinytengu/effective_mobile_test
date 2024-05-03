import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class TransactionType(Enum):
    INCOME = 1
    EXPENSE = 2
    UNDEFINED = 3


@dataclass(frozen=False, repr=True)
class Transaction:
    id: uuid.UUID
    date: datetime
    type: TransactionType
    amount: float
    description: str | None = None

    @classmethod
    def create(
        cls,
        type: TransactionType,
        amount: float,
        description: str | None = None,
        date: datetime | None = None,
    ) -> "Transaction":
        """
        Create a new ExpensesEvent instance with a unique ID, current date and time, provided type, amount, and optional description.

        Args:
            type (ExpenseType): The type of the expense, either income, expense, or undefined.
            amount (float): The amount of the expense.
            description (str | None): An optional description of the expense.
            date (str | None): An optional date of the expense (current time by default).

        Returns:
            ExpensesEvent: A new instance of ExpensesEvent with the provided parameters.
        """
        return cls(
            id=uuid.uuid4(),
            date=date or datetime.now(tz=timezone.utc),
            type=type,
            amount=amount,
            description=description,
        )

    def clone(
        self,
        type: TransactionType | None = None,
        amount: float | None = 0,
        description: str | None = None,
        date: datetime | None = None,
    ) -> "Transaction":
        """
        Create a clone of the current ExpensesEvent instance with optional updated parameters.

        Args:
            type (ExpenseType | None): The type of the expense, either income, expense, or undefined. Defaults to the current type.
            amount (float | None): The amount of the expense. Defaults to 0.
            description (str | None): An optional description of the expense. Defaults to None.
            date (datetime | None): An optional date of the expense. Defaults to the current time.

        Returns:
            ExpensesEvent: A new instance of ExpensesEvent with the provided parameters or the same parameters as the current instance if no arguments are provided.
        """
        return Transaction(
            id=self.id,
            type=type or self.type,
            amount=amount or self.amount,
            description=description or self.description,
            date=date or self.date,
        )

    def to_dict(self) -> dict:
        """
        Convert the ExpensesEvent instance to a dictionary representation.

        Returns:
            dict: A dictionary containing the id, date, type, amount, and description of the ExpensesEvent instance.
        """
        return {
            "id": str(self.id),
            "date": self.date.isoformat(),
            "type": self.type.name,
            "amount": self.amount,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a new ExpensesEvent instance from a dictionary representation.

        Args:
            data (dict): A dictionary containing the id, date, type, amount, and description of the ExpensesEvent instance.

        Returns:
            ExpensesEvent: A new instance of ExpensesEvent with the provided parameters.
        """
        return cls(
            id=uuid.UUID(data["id"]),
            date=datetime.fromisoformat(data["date"]),
            type=TransactionType[data["type"]],
            amount=data["amount"],
            description=data["description"],
        )
