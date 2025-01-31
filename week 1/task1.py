data = input("Введите текст для хэширования: ")
hash_value = 0
for char in data:
    hash_value += ord(char)
    hash_value = (hash_value * 31) % 1000000007
print("Хэш:", hash_value)