# «Программирование - это круто»; ключ 10.
def encrypt_caesar(text, shift):
    result = ""

    for char in text:
        if 'a' <= char <= 'z':
            new_index = (ord(char) - ord('a') + shift) % 26
            result += chr(new_index + ord('a'))

        elif 'A' <= char <= 'Z':
            new_index = (ord(char) - ord('A') + shift) % 26
            result += chr(new_index + ord('A'))

        elif 'а' <= char <= 'я':
            result += chr((ord(char) - ord('а') + shift) % 32 + ord('а'))

        elif 'А' <= char <= 'Я':
            result += chr((ord(char) - ord('А') + shift) % 32 + ord('А'))

        else:
            result += char

    return result


user_text = input("Введите текст для шифрования: ")
user_key = int(input("Введите числовой ключ (сдвиг): "))

encrypted = encrypt_caesar(user_text, user_key)
print(f"Результат: {encrypted}")