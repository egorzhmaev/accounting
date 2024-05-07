import uuid
import random
from datetime import datetime, timezone

import pytest

from app.jsondb import JsonFileDatabase
from app.models import Transaction, TransactionType
from app.utils import calculate_expenses, calculate_incomes

temp_filename = 'db_test.json'


def test_db_read():
    global temp_filename

    db = JsonFileDatabase(temp_filename)

    with open(temp_filename, "w") as file:
        file.write("")

    with pytest.raises(ValueError):
        db.read()

    with open(temp_filename, "w") as file:
        file.write("[]")

    assert len(db.read()) == 0


def test_write_db():
    global temp_filename

    db = JsonFileDatabase(temp_filename)

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

    db.clear()

def test_append_db():
    global temp_filename

    db = JsonFileDatabase(temp_filename)


    db.add_transaction(Transaction.create(type=TransactionType.EXPENSE, amount=777))
    db.add_transaction(Transaction.create(type=TransactionType.INCOME, amount=100))
    db.add_transaction(Transaction.create(type=TransactionType.EXPENSE, amount=1500))
    db.save()

    assert len(db._transactions) == 3

    db.add_transaction(Transaction.create(type=TransactionType.EXPENSE, amount=777, ))
    db.save()

    assert len(db._transactions) == 4




def test_get_transactions():
    global temp_filename

    db = JsonFileDatabase(temp_filename)

    assert len(db._transactions) == 4


def test_get_transaction_by_id():
    global temp_filename

    db = JsonFileDatabase(temp_filename)

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

    db = JsonFileDatabase(temp_filename)

    transaction = random.choice(db._transactions)

    with pytest.raises(ValueError):
        db.delete_transaction(uuid.uuid4())

    assert transaction == db.delete_transaction(transaction.id)


def test_change_transaction():
    global temp_filename

    db = JsonFileDatabase(temp_filename)

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

    db = JsonFileDatabase(temp_filename)

    db.clear()

    assert len(db._transactions) == 0
    assert len(db.read()) == 0


def test_calculate_expenses_incomes():
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

    assert calculate_expenses(transactions) == -5000
    assert calculate_expenses([]) == 0
    assert calculate_incomes(transactions) == 1000
