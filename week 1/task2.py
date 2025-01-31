import time

class Block:
    def __init__(self, data, previous_hash='0'):
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.timestamp}{self.data}{self.previous_hash}"
        hash_value = 0
        for char in block_string:
            hash_value += ord(char)
            hash_value = (hash_value * 31) % 1000000007
        return hash_value

genesis_block = Block(data="This is the Genesis Block")
print("Генезисный блок:")
print("Timestamp:", genesis_block.timestamp)
print("Previous hash:", genesis_block.previous_hash)
print("Own hash:", genesis_block.hash)

new_block = Block(data="This is the second block", previous_hash=genesis_block.hash)
print("\nНовый блок:")
print("Timestamp:", new_block.timestamp)
print("Previous hash:", new_block.previous_hash)
print("Own hash:", new_block.hash)
