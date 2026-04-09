import heapq
from collections import Counter

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(text):
    frequencies = Counter(text)
    priority_queue = [Node(char, freq) for char, freq in frequencies.items()]
    heapq.heapify(priority_queue)

    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)

        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right

        heapq.heappush(priority_queue, merged)

    return priority_queue[0]

def generate_codes(node, current_code="", codes=None):
    if codes is None:
        codes = {}

    if node is None:
        return

    if node.char is not None:
        codes[node.char] = current_code

    generate_codes(node.left, current_code + "0", codes)
    generate_codes(node.right, current_code + "1", codes)

    return codes


def huffman_encode(text):
    if not text:
        return "", None, None

    root = build_huffman_tree(text)
    codes = generate_codes(root)

    encoded_text = "".join(codes[char] for char in text)

    return encoded_text, root, codes


def huffman_decode(encoded_text, root):
    decoded_text = ""
    current_node = root

    for bit in encoded_text:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right

        if current_node.char is not None:
            decoded_text += current_node.char
            current_node = root

    return decoded_text

if __name__ == "__main__":
    text = "мама мыла раму"

    print("Оригинальный текст:", text)

    encoded, root, codes = huffman_encode(text)

    print("\nТаблица кодов:")
    for char, code in codes.items():
        print(f"{repr(char)}: {code}")

    print("\nЗакодировано:")
    print(encoded)

    decoded = huffman_decode(encoded, root)

    print("\nДекодировано:")
    print(decoded)

    print("\nРазмеры:")
    print("Оригинал:", len(text) * 8, "бит")
    print("Сжато:   ", len(encoded), "бит")