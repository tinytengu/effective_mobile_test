import os
import uuid
import random
import tempfile

import pytest  # type: ignore


from app.db.jsonfile import JsonFileDatabase
from app.models import Transaction, TransactionType

temp_filename: str = ""


@pytest.fixture(scope="session", autouse=True)
def setup_before_tests():
    global temp_filename
    temp_file = tempfile.NamedTemporaryFile(delete=False, dir=".")
    temp_filename = temp_file.name

    yield

    temp_file.close()
    os.remove(temp_file.name)


def test_db_create():
    global temp_filename

    db = JsonFileDatabase()

    with pytest.raises(AttributeError):
        db.connect()

    with pytest.raises(FileNotFoundError):
        db.connect(filename="-{}InValidFil#name.json")

    with open(temp_filename, "w") as file:
        file.write("")

    with pytest.raises(ValueError):
        db.connect(filename=temp_filename)

    with open(temp_filename, "w") as file:
        file.write("[]")

    db.connect(filename=temp_filename)

    with open(temp_filename, "w") as file:
        file.write("")

    with pytest.raises(ValueError):
        db.read()

    with open(temp_filename, "w") as file:
        file.write("[]")


def test_db_disconnect():
    global temp_filename

    db = JsonFileDatabase()
    db.connect(filename=temp_filename)

    assert isinstance(db.filename, str)
    assert isinstance(db._transactions, list)

    db.disconnect()

    assert db.filename is None
    assert db._transactions is None


def test_db_read():
    global temp_filename

    db = JsonFileDatabase()
    db.connect(filename=temp_filename)

    with open(temp_filename, "w") as file:
        file.write("")

    with pytest.raises(ValueError):
        db.read()

    with open(temp_filename, "w") as file:
        file.write("[]")

    assert len(db.read()) == 0


def test_write_db():
    global temp_filename

    db = JsonFileDatabase()
    db.connect(filename=temp_filename)

    db.write(
        [
            Transaction.create(type=TransactionType.INCOME, amount=100),
            Transaction.create(type=TransactionType.EXPENSE, amount=1500),
        ],
        read_again=True,
    )
    assert len(db._transactions) == 2

    db.write([], read_again=False)
    assert len(db._transactions) == 2

    db.write([], read_again=True)
    assert len(db._transactions) == 0


def test_append_db():
    global temp_filename

    db = JsonFileDatabase()
    db.connect(filename=temp_filename)

    db.write(
        [
            Transaction.create(type=TransactionType.INCOME, amount=100),
            Transaction.create(type=TransactionType.EXPENSE, amount=1500),
        ],
    )

    db.add_transaction(Transaction.create(type=TransactionType.EXPENSE, amount=777))

    assert len(db._transactions) == 3
    assert len(db.read()) == 2

    db.save()
    assert len(db._transactions) == 3
    assert len(db.read()) == len(db._transactions)

    db.add_transaction(Transaction.create(type=TransactionType.EXPENSE, amount=777))
    db.save()

    assert len(db._transactions) == 4


def test_get_transactions():
    global temp_filename

    db = JsonFileDatabase()
    db.connect(filename=temp_filename)

    assert len(db._transactions) == 4


def test_get_transaction_by_id():
    global temp_filename

    db = JsonFileDatabase()
    db.connect(filename=temp_filename)

    transaction = random.choice(db._transactions)
    assert transaction == db.get_transaction(transaction.id)

    db._transactions.append(transaction)
    with pytest.raises(ValueError):
        assert transaction == db.get_transaction(transaction.id)

    db._transactions.remove(transaction)

    with pytest.raises(ValueError):
        db.get_transaction(uuid.uuid4())


def test_delete_transaction():
    global temp_filename

    db = JsonFileDatabase()
    db.connect(filename=temp_filename)

    transaction = random.choice(db._transactions)

    with pytest.raises(ValueError):
        db.delete_transaction(uuid.uuid4())

    assert transaction == db.delete_transaction(transaction.id)


def test_change_transaction():
    global temp_filename

    db = JsonFileDatabase()
    db.connect(filename=temp_filename)

    transaction = random.choice(db._transactions)
    new_transaction = transaction.clone(
        amount=12345678,
        description="New description",
    )

    db.change_transaction(transaction.id, new_transaction)
    assert db.get_transaction(transaction.id).amount == 12345678
    assert db.get_transaction(transaction.id).description == "New description"


def test_clear_db():
    global temp_filename

    db = JsonFileDatabase()
    db.connect(filename=temp_filename)

    db.clear()

    assert len(db._transactions) == 0
    assert len(db.read()) == 0
