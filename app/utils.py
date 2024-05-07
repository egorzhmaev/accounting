from app.models import Transaction, TransactionType


def click_enter(func):
    def wrapped(*args, **kwargs):
        print('\n[Список транзакций]')
        func(*args, **kwargs)
        print('\n[Enter чтобы продолжить]')
        input("> ")
    return wrapped

def transaction_print(idx, transaction):

    print(
        "{}. [{}] {}{:.02f} руб. {}".format(
            idx + 1,
            transaction.date.strftime("%d.%m.%Y %H:%M:%S"),
            "+" if transaction.type == TransactionType.INCOME else "-",
            transaction.amount,
            f"({transaction.description})" if transaction.description else "",
        )
    )

def calculate_expenses(transactions: list[Transaction]) -> float:

    return float(
        sum(
            [
                -abs(transaction.amount)
                for transaction in transactions
                if transaction.type == TransactionType.EXPENSE
            ]
        )
    )

def calculate_incomes(transactions: list[Transaction]) -> float:

    return float(
        sum(
            [
                abs(transaction.amount)
                for transaction in transactions
                if transaction.type == TransactionType.INCOME
            ]
        )
    )

@click_enter
def category_search(choice, transactions: list[Transaction]):

    for idx, transaction in enumerate(transactions):
        if transaction.type == choice:
            transaction_print(idx, transaction)

@click_enter
def date_search(date, transactions: list[Transaction]):

    for idx, transaction in enumerate(transactions):
        if transaction.date.strftime("%d.%m.%Y") == date:
            transaction_print(idx, transaction)

@click_enter
def amount_search(value, transactions: list[Transaction]):

    for idx, transaction in enumerate(transactions):
        if transaction.amount == float(value):
            transaction_print(idx, transaction)




