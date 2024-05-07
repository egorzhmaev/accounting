import json
import uuid

from app.models import Transaction


class JsonFileDatabase():

    """
    A database that reads and writes transactions to a JSON file.

    Attributes:
        filename (str): The name of the JSON file to be used as the database.
        _transactions (list[Transaction]): A list of `Transaction` objects, each representing a transaction in the JSON file.
    """

    def __init__(self, filename):
        self.filename = filename
        self._transactions = self.read()

    def read(self) -> list[Transaction]:

        with open(self.filename, "r", encoding="UTF-8") as file:
            data: list[dict] = json.load(file)

        return [Transaction.from_dict(transaction) for transaction in data]

    def write(self, transactions: list[Transaction], read_again: bool = True) -> None:

        with open(self.filename, "w", encoding="UTF-8") as file:
            json.dump(
                [transaction.to_dict() for transaction in transactions],
                file,
                indent=2,
                ensure_ascii=False,
            )

        if read_again:
            self._transactions = self.read()

    def save(self):

        self.write(self._transactions)

    def clear(self) -> None:

        self._transactions = []
        self.save()

    def get_transactions(self) -> list[Transaction]:

        return self._transactions or []

    def get_transaction(self, transaction_id: uuid.UUID) -> Transaction:

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

    def add_transaction(self, transaction: Transaction) -> None:

        self._transactions.append(transaction)

    def delete_transaction(self, transaction_id: uuid.UUID) -> Transaction:

        transaction = self.get_transaction(transaction_id)
        self._transactions.remove(transaction)
        return transaction

    def change_transaction(
        self, transaction_id: uuid.UUID, new_transaction: Transaction
    ):

        self.delete_transaction(transaction_id)
        self.add_transaction(new_transaction)