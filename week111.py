import tkinter as tk
from tkinter import ttk
import hashlib
import time


class Block:
    def __init__(self, index, timestamp, data, previous_hash=""):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        to_hash = str(self.index) + self.timestamp + self.data + self.previous_hash
        return hashlib.sha256(to_hash.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, time.ctime(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        previous_block = self.get_latest_block()
        new_block = Block(len(self.chain), time.ctime(), data, previous_block.hash)
        self.chain.append(new_block)


class BlockchainExplorer:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def show_gui(self):
        root = tk.Tk()
        root.title("Blockchain Explorer")

        tree = ttk.Treeview(root, columns=("Address", "Timestamp", "Data", "Validation"), show="headings")
        tree.heading("Address", text="Block Address")
        tree.heading("Timestamp", text="Timestamp")
        tree.heading("Data", text="Data")
        tree.heading("Validation", text="Validation Status")

        for block in self.blockchain.chain:
            validation = "Valid" if block.hash == block.calculate_hash() else "Invalid"
            tree.insert("", "end", values=(block.hash, block.timestamp, block.data, validation))

        tree.pack(expand=True, fill=tk.BOTH)
        root.mainloop()


# Example Usage
if __name__ == "__main__":
    bc = Blockchain()
    bc.add_block("Block 1 Data")
    bc.add_block("Block 2 Data")
    bc.add_block("Block 3 Data")

    explorer = BlockchainExplorer(bc)
    explorer.show_gui()
