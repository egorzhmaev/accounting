from __future__ import annotations

from datetime import datetime, timezone

from app.jsondb import JsonFileDatabase
from app.models import TransactionType, Transaction
from app.utils import calculate_expenses, calculate_incomes, category_search, amount_search, date_search, \
    transaction_print

TEXT_CHOOSE = "\n[Выберите действие]"
DB_FILENAME = 'app/db.json'
db = JsonFileDatabase(DB_FILENAME)

def home_view() -> None:

    """
    Displays home view.
    """

    print(TEXT_CHOOSE)
    print("1. Посмотреть баланс")
    print("2. Добавить транзакцию")
    print("3. Посмотреть транзакции")
    print("4. Поиск")
    print("q. Выйти")

    choice = input("> ")
    if choice == "1":
        balance_view()
    elif choice == "2":
        transaction_add_view()
    elif choice == "3":
        transactions_view()
    elif choice == "4":
        transactions_search()
    elif choice == "q":
        exit()
    else:
        home_view()


def balance_view():

    """
    Displays balance view.
    """

    incomes = calculate_incomes(db.get_transactions())
    expenses = calculate_expenses(db.get_transactions())
    balance = expenses + incomes
    print('1. Баланс')
    print('2. Общий доход')
    print('3. Общий расход')
    print("<. Назад")
    choice = input("> ")
    if choice == "1":
        print(f"\nВаш баланс: {balance} руб.")
    elif choice == "2":
        print(f"\nДоход: {incomes} руб.")
    elif choice == "3":
        print(f"\nРасход: {expenses} руб.")
    elif choice == "<":
        home_view()

    balance_view()


def transactions_view():

    """
    Displays transaction view.
    """

    transactions = sorted(
        db.get_transactions(),
        key=lambda transaction: transaction.date,
        reverse=True,
    )


    print('\n[Список транзакций]')
    for idx, transaction in enumerate(transactions):
        transaction_print(idx, transaction)


    print(TEXT_CHOOSE)
    if len(transactions) > 0:
        print(
            "{}. Посмотреть детали транзакции[введи номер]".format(
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


def transaction_detail_view(transaction: Transaction):

    """
    Displays transaction edit detail view.
    """

    print(
        "[Транзакция #{}]".format(str(transaction.id)),
        f"Дата: {transaction.date.strftime('%d.%m.%Y %H:%M:%S')}",
        f"Сумма: {transaction.amount:.02f} руб.",
        f"Описание: {transaction.description}",
        sep="\n",
    )

    print(TEXT_CHOOSE)
    print("1. Изменить дату")
    print("2. Изменить сумму")
    print("3. Изменить описание")
    print("4. Удалить")
    print("<. Назад")
    print("q. Выход")

    choice = input("> ")
    if choice == "1":
        transaction_edit_date_view(transaction=transaction)
    elif choice == "2":
        transaction_edit_amount_view(transaction=transaction)
    elif choice == "3":
        transaction_edit_description_view(transaction=transaction)
    elif choice == "4":
        db.delete_transaction(transaction.id)
        db.save()
        transactions_view()
    elif choice == "<":
        transactions_view()
    elif choice == "q":
        exit()
    else:
        transaction_detail_view(transaction=transaction)


def transaction_edit_date_view(transaction: Transaction):

    """
    Displays transaction edit date view.
    """

    print(
        "[Транзакция #{}]".format(str(transaction.id))
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

    db.change_transaction(
        transaction.id, transaction.clone(date=expense_date)
    )
    db.save()
    transaction = db.get_transaction(transaction.id)

    transaction_detail_view(transaction=transaction)



def transaction_edit_amount_view(transaction: Transaction):

    """
    Displays transaction edit amount view.
    """

    print(
        "[Транзакция #{}]".format(str(transaction.id))
    )

    value = input("Введите сумму (отрицательное значение для расходов): ")
    if not value.isnumeric() and not value[0] == "-":
        return transaction_edit_amount_view(transaction=transaction)

    expense_amount = int(value)
    if expense_amount == 0:
        return transaction_edit_amount_view(transaction=transaction)

    db.change_transaction(
        transaction.id, transaction.clone(amount=expense_amount)
    )
    db.save()
    transaction = db.get_transaction(transaction.id)

    transaction_detail_view(transaction=transaction)



def transaction_edit_description_view(transaction: Transaction):

    """
    Displays transaction edit description view.
    """

    print(
        "[Транзакция #{}]".format(str(transaction.id))
    )

    expense_description = input("Введите описание: ")

    db.change_transaction(
        transaction.id, transaction.clone(description=expense_description)
    )
    db.save()
    transaction = db.get_transaction(transaction.id)

    transaction_detail_view(transaction=transaction)



def transaction_add_view():

    """
    Displays transaction add view.
    """

    print("[Добавление транзакции]")

    expense_amount = 0
    expense_date = None

    while True:
        value = input("Введите сумму (минус для расходов): ")
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
        date = input("Введите дату (ДД.ММ.ГГГГ ЧЧ:ММ:СС) или оставить пустым: ")
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


def add_transaction_check_view(
    expense_type: TransactionType,
    expense_amount: float,
    expense_description: str,
    expense_date: datetime,
):

    """
    Displays transaction add view confirmation.
    """
    print('\n[Проверьте данные]')
    print(f'Тип: {expense_type}')
    print("Сумма: {:.02f} руб.".format(expense_amount))
    print("Дата: {}.".format(expense_date.strftime("%d.%m.%Y %H:%M:%S")))
    print("Описание: {}".format(expense_description))

    answer = input("Создать? (y/n) ")
    if answer == "y":
        db.add_transaction(
            Transaction.create(expense_type, expense_amount, expense_description, expense_date)
        )
        db.save()

    transactions_view()

def transactions_search():

    """
    Display transaction search
    """

    print('1. Поиск по категории')
    print('2. Поиск по дате')
    print('3. Поиск по сумме')
    print("<. Назад")
    print("q. Выход")

    choice = input("> ")
    if choice == "1":
        category()
    elif choice == "2":
        date = input("Введите дату (ДД.ММ.ГГГГ): ")
        date_search(date, db.get_transactions())
    elif choice == "3":
        value = input("Введите сумму: ")
        amount_search(value, db.get_transactions())
    elif choice == "<":
        home_view()
    elif choice == "q":
        exit()

    transactions_search()

def category():

    """
    Display category search
    """

    print('1. Все доходы')
    print('2. Все расходы')

    choice = input("> ")
    if choice == "1":
        category_search(TransactionType.INCOME, db.get_transactions())
    elif choice == "2":
        category_search(TransactionType.EXPENSE, db.get_transactions())



