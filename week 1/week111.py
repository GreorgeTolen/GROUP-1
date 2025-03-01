import hashlib
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import random

# Константы
DIFFICULTY = 4         # Используется для PoW (остается для сравнения, но для PoS не применяется)
MINING_REWARD = 50     # Вознаграждение за майнинг (для PoS – staking reward)

# --- Класс транзакции ---
class Transaction:
    def __init__(self, sender, receiver, amount, signature=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = int(time.time())
        self.tx_hash = self.calculate_tx_hash()
        self.signature = signature  # Цифровая подпись транзакции

    def calculate_tx_hash(self):
        data = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def __repr__(self):
        return f"Transaction({self.sender}, {self.receiver}, {self.amount}, {self.tx_hash})"

# --- Класс блока ---
class Block:
    def __init__(self, transactions, previous_hash="0", miner="unknown", difficulty=DIFFICULTY, pos=False):
        self.timestamp = time.ctime()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.merkle_root = self.calculate_merkle_root()
        self.nonce = 0
        self.miner = miner
        self.difficulty = difficulty
        # Если PoS, сразу вычисляем хэш, иначе выполняем PoW
        if pos:
            self.hash = self.calculate_hash()
        else:
            self.hash = self.mine_block()

    def calculate_merkle_root(self):
        tx_hashes = [tx.tx_hash for tx in self.transactions]
        return self.build_merkle_tree(tx_hashes)

    def build_merkle_tree(self, tx_hashes):
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 != 0:
                tx_hashes.append(tx_hashes[-1])
            tx_hashes = [
                hashlib.sha256((tx_hashes[i] + tx_hashes[i + 1]).encode("utf-8")).hexdigest()
                for i in range(0, len(tx_hashes), 2)
            ]
        return tx_hashes[0]

    def calculate_hash(self):
        block_string = f"{self.timestamp}{self.merkle_root}{self.previous_hash}{self.nonce}{self.miner}"
        return hashlib.sha256(block_string.encode("utf-8")).hexdigest()

    def mine_block(self):
        computed_hash = self.calculate_hash()
        target = "0" * self.difficulty
        while not computed_hash.startswith(target):
            self.nonce += 1
            computed_hash = self.calculate_hash()
        print(f"Block mined: {computed_hash} with nonce: {self.nonce}")
        return computed_hash

    def __repr__(self):
        return (
            f"Block(Hash: {self.hash}, Miner: {self.miner}, Nonce: {self.nonce}, "
            f"Merkle Root: {self.merkle_root}, Previous Hash: {self.previous_hash})"
        )

# --- Класс блокчейна ---
class Blockchain:
    def __init__(self):
        self.chain = []
        self.utxo = {}
        self.public_keys = {}
        self.stakes = {}         # Словарь: адрес -> количество застейканных монет
        self.create_genesis_block()

    def create_genesis_block(self):
        self.utxo["System"] = 1000
        genesis_transactions = [
            Transaction("System", "Tolik", 100),
            Transaction("System", "Ernar", 100),
        ]
        genesis_block = Block(transactions=genesis_transactions, miner="System", difficulty=DIFFICULTY, pos=True)
        self.chain.append(genesis_block)
        self.update_utxo(genesis_transactions)

    def add_block_pos(self, transactions, validator_address):
        # Добавляем транзакцию вознаграждения за блок (staking reward)
        reward_tx = Transaction("System", validator_address, MINING_REWARD)
        # Создаем копию списка, чтобы не изменять исходный список транзакций
        txs = [reward_tx] + transactions
        previous_block = self.chain[-1]
        new_block = Block(transactions=txs, previous_hash=previous_block.hash,
                          miner=validator_address, difficulty=DIFFICULTY, pos=True)
        self.chain.append(new_block)
        self.update_utxo(new_block.transactions)
        return new_block

    def update_utxo(self, transactions):
        for tx in transactions:
            self.utxo[tx.receiver] = self.utxo.get(tx.receiver, 0) + tx.amount
            if tx.sender != "System":
                self.utxo[tx.sender] = self.utxo.get(tx.sender, 0) - tx.amount
                if self.utxo[tx.sender] < 0:
                    raise ValueError(f"Negative balance detected for {tx.sender}!")

    def stake_coins(self, address, amount):
        if self.utxo.get(address, 0) < amount:
            raise ValueError("Insufficient balance to stake")
        self.utxo[address] -= amount
        self.stakes[address] = self.stakes.get(address, 0) + amount

    def select_validator(self):
        total_stake = sum(self.stakes.values())
        if total_stake == 0:
            return None  # Нет застейканных монет
        r = random.uniform(0, total_stake)
        cumulative = 0
        for validator, stake in self.stakes.items():
            cumulative += stake
            if cumulative >= r:
                return validator
        return None

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.previous_hash != previous_block.hash:
                return False
            if current_block.hash != current_block.calculate_hash():
                return False
        return True

# --- Класс узла (Node) ---
class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.blockchain = Blockchain()

    def update_chain(self, new_chain):
        if len(new_chain) > len(self.blockchain.chain):
            self.blockchain.chain = new_chain.copy()
            self.blockchain.utxo = {}
            for block in self.blockchain.chain:
                self.blockchain.update_utxo(block.transactions)

# --- Класс сети узлов (NodeNetwork) ---
class NodeNetwork:
    def __init__(self):
        self.nodes = []

    def add_node(self, node: Node):
        self.nodes.append(node)

    def broadcast_block(self, new_block, originating_node_id):
        for node in self.nodes:
            if node.node_id != originating_node_id:
                if len(primary_node.blockchain.chain) > len(node.blockchain.chain):
                    node.update_chain(primary_node.blockchain.chain)

# --- RSA Key Pair Management ---
def generate_key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

def sign_data(private_key, data):
    return private_key.sign(
        data.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )

def verify_signature(public_key, data, signature):
    try:
        public_key.verify(
            signature,
            data.encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

# --- Инициализация децентрализованной сети ---
node_network = NodeNetwork()
primary_node = Node("primary")
node_network.add_node(primary_node)
node_network.add_node(Node("node2"))
node_network.add_node(Node("node3"))

# --- GUI Functions ---
def add_new_block_pos_gui():
    sender = sender_entry.get()
    receiver = receiver_entry.get()
    amount = amount_entry.get()

    if not sender or not receiver or not amount.isdigit():
        messagebox.showwarning("Input Error", "Please fill all fields correctly!")
        return

    amount = int(amount)
    if primary_node.blockchain.utxo.get(sender, 0) < amount:
        messagebox.showwarning("Balance Error", "Insufficient balance!")
        return

    private_key = private_keys.get(sender)
    if not private_key:
        messagebox.showwarning("Key Error", f"No private key found for {sender}!")
        return

    transaction_data = f"{sender}{receiver}{amount}"
    signature = sign_data(private_key, transaction_data)
    transaction = Transaction(sender, receiver, amount, signature)

    # Выбор валидатора на основе ставки
    validator = primary_node.blockchain.select_validator()
    if not validator:
        messagebox.showwarning("Validator Error", "No validator available. Stake coins first!")
        return

    new_block = primary_node.blockchain.add_block_pos([transaction], validator_address=validator)
    node_network.broadcast_block(new_block, primary_node.node_id)
    update_gui()
    clear_inputs()

def generate_keys_gui():
    user = user_entry.get()
    if not user:
        messagebox.showwarning("Input Error", "Please enter a username!")
        return

    private_key, public_key = generate_key_pair()
    private_keys[user] = private_key
    primary_node.blockchain.public_keys[user] = public_key
    messagebox.showinfo("Keys Generated", f"Keys for {user} have been generated!")

def stake_coins_gui():
    user = user_entry.get()
    stake_amount = stake_entry.get()
    if not user or not stake_amount.isdigit():
        messagebox.showwarning("Input Error", "Please enter a valid username and stake amount!")
        return
    stake_amount = int(stake_amount)
    try:
        primary_node.blockchain.stake_coins(user, stake_amount)
        messagebox.showinfo("Staking", f"{stake_amount} coins staked for {user}!")
        update_gui()
    except ValueError as ve:
        messagebox.showwarning("Staking Error", str(ve))
    stake_entry.delete(0, tk.END)

def clear_inputs():
    sender_entry.delete(0, tk.END)
    receiver_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    user_entry.delete(0, tk.END)

def update_gui():
    # Очищаем содержимое фрейма блоков
    for widget in block_list_frame.winfo_children():
        widget.destroy()

    for block in primary_node.blockchain.chain:
        transactions_info = "\n".join(
            [f"Sender: {tx.sender}, Receiver: {tx.receiver}, Amount: {tx.amount}" for tx in block.transactions]
        )
        block_text = (
            f"Block Hash: {block.hash}\n"
            f"Timestamp: {block.timestamp}\n"
            f"Validator: {block.miner}\n"
            f"Nonce: {block.nonce}\n"
            f"Merkle Root: {block.merkle_root}\n"
            f"Previous Hash: {block.previous_hash}\n"
            f"Transactions:\n{transactions_info}\n"
        )
        label = ttk.Label(block_list_frame, text=block_text, justify="left",
                          background="#e1e1e1", relief="ridge", padding=5)
        label.pack(fill=tk.X, pady=2)

    # Обновляем область прокрутки
    canvas.configure(scrollregion=canvas.bbox("all"))
    root.after(1000, update_gui)

def check_balances():
    balances = "\n".join([f"{user}: {balance} coins" for user, balance in primary_node.blockchain.utxo.items()])
    stakes = "\n".join([f"{user}: {amount} coins staked" for user, amount in primary_node.blockchain.stakes.items()])
    messagebox.showinfo("Balances & Stakes", f"Current balances:\n{balances}\n\nStakes:\n{stakes}")

# --- GUI Setup ---
private_keys = {}

root = tk.Tk()
root.title("Decentralized Blockchain Explorer with PoS")
root.configure(bg="#f5f5f5")
style = ttk.Style(root)
style.theme_use("clam")
style.configure("TLabel", background="#f5f5f5", font=("Helvetica", 10))
style.configure("TButton", font=("Helvetica", 10, "bold"))

# Header Frame
header_frame = ttk.Frame(root, padding=10)
header_frame.pack(fill=tk.X)
header_label = ttk.Label(header_frame, text="Blockchain Explorer with PoS", font=("Helvetica", 16, "bold"))
header_label.pack()

# Input Frame
input_frame = ttk.Frame(root, padding=10)
input_frame.pack(pady=5, fill=tk.X)

ttk.Label(input_frame, text="Sender Address:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
sender_entry = ttk.Entry(input_frame, width=30)
sender_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Receiver Address:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
receiver_entry = ttk.Entry(input_frame, width=30)
receiver_entry.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
amount_entry = ttk.Entry(input_frame, width=30)
amount_entry.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="User for Keys/Staking:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
user_entry = ttk.Entry(input_frame, width=30)
user_entry.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Stake Amount:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
stake_entry = ttk.Entry(input_frame, width=30)
stake_entry.grid(row=4, column=1, padx=5, pady=5)

# Buttons Frame
buttons_frame = ttk.Frame(root, padding=10)
buttons_frame.pack(pady=5, fill=tk.X)

ttk.Button(buttons_frame, text="Submit Transaction & Validate Block (PoS)", command=add_new_block_pos_gui).pack(side=tk.LEFT, padx=5)
ttk.Button(buttons_frame, text="Generate Keys", command=generate_keys_gui).pack(side=tk.LEFT, padx=5)
ttk.Button(buttons_frame, text="Stake Coins", command=stake_coins_gui).pack(side=tk.LEFT, padx=5)
ttk.Button(buttons_frame, text="Check Balances & Stakes", command=check_balances).pack(side=tk.LEFT, padx=5)

# Scrollable Block List Frame
canvas = tk.Canvas(root, height=300, bg="#f5f5f5")
canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
block_list_frame = ttk.Frame(canvas)
canvas.create_window((0,0), window=block_list_frame, anchor="nw")

update_gui()
root.mainloop()
