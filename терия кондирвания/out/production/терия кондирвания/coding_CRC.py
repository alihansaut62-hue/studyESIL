# CRC (Cyclic Redundancy Check) — обнаружение ошибок передачи данных
# Работает с битовыми строками, например: message="1101011011", poly="10011"
# poly="10011" соответствует x^4 + x + 1 (пример генераторного полинома)

from typing import List, Tuple


def _validate_bits(s: str, name: str) -> None:
    if not s or any(ch not in "01" for ch in s):
        raise ValueError(f"{name} must be a non-empty binary string containing only '0' and '1'.")
    if name == "poly":
        if s[0] != "1":
            raise ValueError("poly must start with '1' (highest degree term).")
        if len(s) < 2:
            raise ValueError("poly length must be >= 2.")


def _mod2_division(dividend_bits: List[int], divisor_bits: List[int]) -> List[int]:
    """
    Деление по модулю 2 (XOR вместо вычитания).
    Возвращает изменённый dividend_bits; остаток будет в последних (len(divisor)-1) битах.
    """
    n = len(dividend_bits)
    m = len(divisor_bits)

    work = dividend_bits[:]
    for i in range(n - m + 1):
        if work[i] == 1:
            for j in range(m):
                work[i + j] ^= divisor_bits[j]
    return work


def crc_remainder(message: str, poly: str) -> str:
    """
    Считает CRC-остаток для message по генераторному полиному poly.
    """
    _validate_bits(message, "message")
    _validate_bits(poly, "poly")

    msg = [int(b) for b in message]
    div = [int(b) for b in poly]
    r = len(div) - 1

    augmented = msg + [0] * r
    divided = _mod2_division(augmented, div)
    remainder_bits = divided[-r:] if r > 0 else []
    return "".join(str(b) for b in remainder_bits)


def crc_encode(message: str, poly: str) -> Tuple[str, str]:
    """
    Возвращает (crc, codeword) где codeword = message + crc.
    """
    crc = crc_remainder(message, poly)
    return crc, message + crc


def crc_check(codeword: str, poly: str) -> bool:
    """
    Проверка принятого слова: True если ошибок не обнаружено (остаток = 0...0).
    """
    _validate_bits(codeword, "codeword")
    _validate_bits(poly, "poly")

    cw = [int(b) for b in codeword]
    div = [int(b) for b in poly]
    r = len(div) - 1

    divided = _mod2_division(cw, div)
    remainder_bits = divided[-r:] if r > 0 else []
    return all(b == 0 for b in remainder_bits)


def flip_bits(bitstring: str, positions: List[int]) -> str:
    """
    Симуляция ошибки: переворачивает биты в указанных позициях (0 = первый бит).
    """
    _validate_bits(bitstring, "bitstring")
    bits = list(bitstring)
    for pos in positions:
        if pos < 0 or pos >= len(bits):
            raise ValueError(f"Position {pos} out of range 0..{len(bits)-1}")
        bits[pos] = "1" if bits[pos] == "0" else "0"
    return "".join(bits)


if __name__ == "__main__":
    message = "1100100101"
    poly = "1000101"

    crc, codeword = crc_encode(message, poly)
    print("Message:  ", message)
    print("Poly:     ", poly)
    print("CRC:      ", crc)
    print("Codeword: ", codeword)
    print("Check OK: ", crc_check(codeword, poly))

    # Симулируем ошибку: перевернём один бит
    corrupted = flip_bits(codeword, [3])
    print("\nCorrupted:", corrupted)
    print("Check OK: ", crc_check(corrupted, poly))