from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class TransactionType(Enum):
    """
    The model of expenses and income
    """
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
        Create a new Transaction
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
        Create a clone of the current Transaction instance with optional updated parameters.
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
        Convert the Transaction instance to a dictionary representation.
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
        Create a new Transaction instance from a dictionary representation.
        """

        return cls(
            id=uuid.UUID(data["id"]),
            date=datetime.fromisoformat(data["date"]),
            type=TransactionType[data["type"]],
            amount=data["amount"],
            description=data["description"],
        )
