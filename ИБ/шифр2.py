import string

alphabet = string.ascii_uppercase

text = "PASS"
text1 = "WORD"
vigenere_key = "ESIL"




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

def vigenere_encrypt(text1, key):
    result = ""
    key = key.upper()
    key_index = 0

    for char in text1:
        if char in alphabet:
            shift = alphabet.index(key[key_index % len(key)])
            index = alphabet.index(char)
            new_index = (index + shift) % 26
            result += alphabet[new_index]
            key_index += 1
        else:
            result += char
    return result





print("Исходный текст:", text)



vigenere_result = vigenere_encrypt(text, vigenere_key)
print(vigenere_result)

vigenere_result = vigenere_encrypt(text1, vigenere_key)
print(vigenere_result)

