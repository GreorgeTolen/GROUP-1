import hashlib
import time
import tkinter as tk
from tkinter import messagebox


# Класс для транзакций
class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = int(time.time())
        self.tx_hash = self.calculate_tx_hash()

    def calculate_tx_hash(self):
        data = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def __repr__(self):
        return f"Transaction({self.sender}, {self.receiver}, {self.amount}, {self.tx_hash})"


# Функции для Merkle Root
def calculate_hash(data):
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def build_merkle_tree(tx_hashes):
    while len(tx_hashes) > 1:
        if len(tx_hashes) % 2 != 0:
            tx_hashes.append(tx_hashes[-1])
        tx_hashes = [
            calculate_hash(tx_hashes[i] + tx_hashes[i + 1])
            for i in range(0, len(tx_hashes), 2)
        ]
    return tx_hashes[0]


# Класс блока
class Block:
    def __init__(self, transactions, previous_hash="0"):
        self.timestamp = time.ctime()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.calculate_hash()

    def calculate_merkle_root(self):
        tx_hashes = [tx.tx_hash for tx in self.transactions]
        return build_merkle_tree(tx_hashes)

    def calculate_hash(self):
        block_string = f"{self.timestamp}{self.merkle_root}{self.previous_hash}"
        return hashlib.sha256(block_string.encode("utf-8")).hexdigest()

    def __repr__(self):
        return (
            f"Block(Hash: {self.hash}, Merkle Root: {self.merkle_root}, "
            f"Previous Hash: {self.previous_hash})"
        )


# Класс блокчейна
class Blockchain:
    def __init__(self):
        self.chain = []
        self.utxo = {}
        self.create_genesis_block()

    def create_genesis_block(self):
        # Инициализация начального баланса для 'System'
        self.utxo["System"] = 1000  # Устанавливаем начальный баланс
        genesis_transactions = [
            Transaction("System", "Era", 100),
            Transaction("System", "Tolik", 100),
            Transaction("System", "Kuka", 100),
        ]
        genesis_block = Block(transactions=genesis_transactions)
        self.chain.append(genesis_block)
        self.update_utxo(genesis_transactions)

    def add_block(self, transactions):
        previous_block = self.chain[-1]
        new_block = Block(transactions=transactions, previous_hash=previous_block.hash)
        self.chain.append(new_block)
        self.update_utxo(transactions)

    def update_utxo(self, transactions):
        for tx in transactions:
            self.utxo[tx.receiver] = self.utxo.get(tx.receiver, 0) + tx.amount
            if tx.sender != "System":  # Исключение проверки отрицательного баланса для System
                self.utxo[tx.sender] = self.utxo.get(tx.sender, 0) - tx.amount
                if self.utxo[tx.sender] < 0:
                    raise ValueError(f"Negative balance detected for {tx.sender}!")

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.previous_hash != previous_block.hash:
                return False
            if current_block.hash != current_block.calculate_hash():
                return False
        return True


blockchain = Blockchain()


# Функции для GUI
def add_new_block_gui():
    sender = sender_entry.get()
    receiver = receiver_entry.get()
    amount = amount_entry.get()

    if not sender or not receiver or not amount.isdigit():
        messagebox.showwarning("Input Error", "Please fill all fields correctly!")
        return

    amount = int(amount)
    if blockchain.utxo.get(sender, 0) < amount:
        messagebox.showwarning("Balance Error", "Insufficient balance!")
        return

    transaction = Transaction(sender, receiver, amount)
    blockchain.add_block([transaction])
    update_gui()
    clear_inputs()


def clear_inputs():
    sender_entry.delete(0, tk.END)
    receiver_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)


def update_gui():
    for widget in block_list_frame.winfo_children():
        widget.destroy()

    for block in blockchain.chain:
        valid = "Valid" if blockchain.is_chain_valid() else "Invalid"
        transactions_info = "\n".join(
            [
                f"Sender: {tx.sender}, Receiver: {tx.receiver}, Amount: {tx.amount}"
                for tx in block.transactions
            ]
        )
        block_label = tk.Label(
            block_list_frame,
            text=(
                f"Block Hash: {block.hash}\n"
                f"Timestamp: {block.timestamp}\n"
                f"Merkle Root: {block.merkle_root}\n"
                f"Previous Hash: {block.previous_hash}\n"
                f"Transactions:\n{transactions_info}\n"
                f"Status: {valid}"
            ),
            justify="left",
            anchor="w",
            borderwidth=2,
            relief="groove",
            padx=5,
            pady=5,
        )
        block_label.pack(fill=tk.X, pady=2)


def check_balances():
    balances = "\n".join([f"{user}: {balance} coins" for user, balance in blockchain.utxo.items()])
    messagebox.showinfo("Balances", f"Current balances:\n{balances}")


# Создание GUI
root = tk.Tk()
root.title("Blockchain Explorer")

input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Sender Address:").grid(row=0, column=0, padx=5, pady=5)
sender_entry = tk.Entry(input_frame, width=30)
sender_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Receiver Address:").grid(row=1, column=0, padx=5, pady=5)
receiver_entry = tk.Entry(input_frame, width=30)
receiver_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5)
amount_entry = tk.Entry(input_frame, width=30)
amount_entry.grid(row=2, column=1, padx=5, pady=5)

add_block_button = tk.Button(root, text="Add Block", command=add_new_block_gui)
add_block_button.pack(pady=10)

check_balance_button = tk.Button(root, text="Check Balances", command=check_balances)
check_balance_button.pack(pady=5)

block_list_frame = tk.Frame(root)
block_list_frame.pack(pady=20, fill=tk.BOTH, expand=True)

update_gui()

root.mainloop()
