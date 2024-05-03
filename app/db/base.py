import uuid
from abc import ABC, abstractmethod

from app.models import Transaction


class BaseDatabase(ABC):
    @abstractmethod
    def connect(self, **kwargs): ...

    @abstractmethod
    def disconnect(self): ...

    @abstractmethod
    def read(self) -> list[Transaction]: ...

    @abstractmethod
    def write(self, data: list[Transaction]): ...

    @abstractmethod
    def get_transactions(self) -> list[Transaction]: ...

    @abstractmethod
    def get_transaction(self, transaction_id: uuid.UUID) -> Transaction: ...

    @abstractmethod
    def add_transaction(self, transaction: Transaction): ...

    @abstractmethod
    def delete_transaction(self, transaction_id: uuid.UUID) -> Transaction: ...

    @abstractmethod
    def change_transaction(
        self, transaction_id: uuid.UUID, new_transaction: Transaction
    ) -> Transaction: ...
