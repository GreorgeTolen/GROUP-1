import time
import tkinter as tk
from tkinter import messagebox

class Block:
    def __init__(self, data: str, previous_hash: str = '0'):
        self.timestamp = time.ctime()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        # Simple hash function
        block_string = f"{self.timestamp}{self.data}{self.previous_hash}"
        hash_value = 0
        for char in block_string:
            hash_value += ord(char)
            hash_value = (hash_value * 31) % 1000000007
        return str(hash_value)


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(data="This is the Genesis Block")
        self.chain.append(genesis_block)

    def add_block(self, data: str):
        # Add a new block to the chain
        previous_block = self.chain[-1]
        new_block = Block(data=data, previous_hash=previous_block.hash)
        self.chain.append(new_block)

    def is_chain_valid(self) -> bool:

        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.previous_hash != previous_block.hash:
                return False

            if current_block.hash != current_block.calculate_hash():
                return False

        return True


blockchain = Blockchain()


def add_new_block(data: str):
    blockchain.add_block(data)
    update_gui()


def update_gui():
    for widget in block_list_frame.winfo_children():
        widget.destroy()

    for block in blockchain.chain:
        valid = "Valid" if blockchain.is_chain_valid() else "Invalid"
        block_label = tk.Label(
            block_list_frame,
            text=(
                f"Address: {block.hash}\n"
                f"Timestamp: {block.timestamp}\n"
                f"Data: {block.data}\n"
                f"Previous Hash: {block.previous_hash}\n"
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


def add_block_from_entry():
    data = block_data_entry.get()
    if data:
        add_new_block(data)
        block_data_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please enter data for the block!")


root = tk.Tk()
root.title("Blockchain Explorer")

block_data_label = tk.Label(root, text="Enter data for the new block:")
block_data_label.pack()

block_data_entry = tk.Entry(root, width=50)
block_data_entry.pack()

add_block_button = tk.Button(root, text="Add Block", command=add_block_from_entry)
add_block_button.pack()

block_list_frame = tk.Frame(root)
block_list_frame.pack(pady=20, fill=tk.BOTH, expand=True)

update_gui()

root.mainloop()
