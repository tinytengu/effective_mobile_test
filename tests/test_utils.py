import platform
from datetime import datetime, timezone

import pytest  # type: ignore

from app.utils import calculate_expenses, term_clear
from app.models import Transaction, TransactionType


def test_calculate_expenses():
    transactions = [
        Transaction(
            id=1,
            type=TransactionType.INCOME,
            amount=1000,
            date=datetime.now(timezone.utc),
        ),
        Transaction(
            id=2,
            type=TransactionType.EXPENSE,
            amount=2000,
            date=datetime.now(timezone.utc),
        ),
        Transaction(
            id=3,
            type=TransactionType.EXPENSE,
            amount=3000,
            date=datetime.now(timezone.utc),
        ),
    ]

    assert calculate_expenses(transactions) == -4000
    assert calculate_expenses([]) == 0


@pytest.mark.parametrize(
    "system, expected_command", [("Windows", "cls"), ("Linux", "clear")]
)
def test_term_clear(monkeypatch, system, expected_command):
    monkeypatch.setattr(platform, "system", lambda: system)
    assert term_clear() == expected_command
