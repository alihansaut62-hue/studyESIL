import string

alphabet = string.ascii_uppercase

text = "MIHAEL"
caesar_key = 6
vigenere_key = "BABYDOLL"
a = 11
b = 4


# Шифр Цезаря
def caesar_encrypt(text, key):
    result = ""
    for char in text:
        if char in alphabet:
            index = alphabet.index(char)
            new_index = (index + key) % 26
            result += alphabet[new_index]
        else:
            result += char
    return result


# Шифр Виженера
def vigenere_encrypt(text, key):
    result = ""
    key = key.upper()
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


# Аффинный шифр
def affine_encrypt(text, a, b):
    result = ""
    for char in text:
        if char in alphabet:
            x = alphabet.index(char)
            new_index = (a * x + b) % 26
            result += alphabet[new_index]
        else:
            result += char
    return result


print("Исходный текст:", text)

caesar_result = caesar_encrypt(text, caesar_key)
print("Цезарь:", caesar_result)

vigenere_result = vigenere_encrypt(text, vigenere_key)
print("Виженер:", vigenere_result)

affine_result = affine_encrypt(text, a, b)
print("Аффинный:", affine_result)