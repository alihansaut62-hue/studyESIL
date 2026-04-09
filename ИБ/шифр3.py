import string

# Алфавит
alphabet = string.ascii_uppercase

# Данные
text = "PASS"
text1 = "PASS"
vigenere_key = "PASS"
vigenere_key1 = "ESIL"

# Функция шифрования
def vigenere_encrypt(text, key):
    result = ""
    key = key.upper()
    text = text.upper()
    key_index = 0

    for char in text:
        if char in alphabet:
            shift = alphabet.index(key[key_index % len(key)])
            index = alphabet.index(char)
            new_index = (index + shift) % 26
            result += alphabet[new_index]
            key_index += 1
        else:
            result += char

    return result


# Вывод результатов
print("Исходный текст:", text)
print("Ключ:", vigenere_key)
print("Шифр:", vigenere_encrypt(text, vigenere_key))

print()

print("Исходный текст:", text1)
print("Ключ:", vigenere_key1)
print("Шифр:", vigenere_encrypt(text1, vigenere_key1))