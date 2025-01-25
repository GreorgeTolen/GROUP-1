import time


class Block:
    def _init_(self, data, previous_hash='0'):
        self.timestamp = time.time()  # Текущее время (timestamp)
        self.data = data  # Данные блока
        self.previous_hash = previous_hash  # Хэш предыдущего блока
        self.hash = self.calculate_hash()  # Хэш текущего блока

    def calculate_hash(self):
        # Простейший алгоритм для хэширования данных блока
        block_string = f"{self.timestamp}{self.data}{self.previous_hash}"
        hash_value = 0
        for char in block_string:
            hash_value += ord(char)
            hash_value = (hash_value * 31) % 1000000007
        return hash_value


class Blockchain:
    def _init_(self):
        self.chain = []  # Список блоков в блокчейне
        self.create_genesis_block()  # Создаем первый (генезисный) блок

    def create_genesis_block(self):
        # Генезисный блок, его предыдущий хэш = '0'
        genesis_block = Block(data="This is the Genesis Block")
        self.chain.append(genesis_block)

    def add_block(self, data):
        # Добавляем новый блок в цепочку
        previous_block = self.chain[-1]  # Получаем последний блок
        new_block = Block(data=data, previous_hash=previous_block.hash)
        self.chain.append(new_block)

    def is_chain_valid(self):
        # Проверка валидности всей цепочки
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Проверяем, что хэш предыдущего блока совпадает с ссылкой на previous_hash
            if current_block.previous_hash != previous_block.hash:
                return False

            # Проверяем, что хэш текущего блока действителен
            if current_block.hash != current_block.calculate_hash():
                return False

        return True

    def print_chain(self):
        # Выводим все блоки в цепочке
        for block in self.chain:
            print(f"Timestamp: {block.timestamp}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Own Hash: {block.hash}")
            print(f"Data: {block.data}")
            print("------------------------------")


# Создание блокчейна и добавление блоков
blockchain = Blockchain()


# Функция для добавления новых блоков через консоль
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


# Запуск функции для добавления блоков
add_new_block()