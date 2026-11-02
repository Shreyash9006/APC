class BankAccount:
    account_counter = 1000

    def __init__(self, account_holder):
        self.account_holder = account_holder
        self.balance = 0
        BankAccount.account_counter += 1
        self.account_number = BankAccount.account_counter

    def deposit(self, amount):
        self.balance += amount
        print("Deposited:", amount)

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            print("Withdrawn:", amount)
        else:
            print("Insufficient funds")

    def display_balance(self):
        print("Account Number:", self.account_number)
        print("Account Holder:", self.account_holder)
        print("Balance:", self.balance)

    def transfer(self, amount, other_account):
        if self.balance >= amount:
            self.balance -= amount
            other_account.balance += amount
            print("Transferred:", amount)
        else:
            print("Insufficient funds")


account1 = BankAccount("Rahul")
account2 = BankAccount("Amit")

account1.deposit(5000)
account1.withdraw(1000)
account1.transfer(2000, account2)

account1.display_balance()
account2.display_balance()