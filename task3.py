import time


class Block:
    def _init_(self, data, previous_hash='0'):
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


class Blockchain:
    def _init_(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):

        genesis_block = Block(data="This is the Genesis Block")
        self.chain.append(genesis_block)

    def add_block(self, data):

        previous_block = self.chain[-1]
        new_block = Block(data=data, previous_hash=previous_block.hash)
        self.chain.append(new_block)

    def is_chain_valid(self):

        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.previous_hash != previous_block.hash:
                return False


            if current_block.hash != current_block.calculate_hash():
                return False

        return True

    def print_chain(self):

        for block in self.chain:
            print(f"Timestamp: {block.timestamp}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Own Hash: {block.hash}")
            print(f"Data: {block.data}")
            print("------------------------------")


blockchain = Blockchain()



def add_new_block():
    while True:
        print("\nВведите данные для нового блока (или 'exit' для завершения):")
        data = input("Data: ")
        if data.lower() == 'exit':
            break
        blockchain.add_block(data)
        print("Новый блок добавлен!")
        print("Текущая валидность цепочки:", blockchain.is_chain_valid())
        blockchain.print_chain()


add_new_block()