# --- СТЕГАНОГРАФИЯ "МАТРЁШКА" ---

# 1. СКРЫТИЕ (картинка + любой файл)
def hide_data(image_path, secret_path, result_path):
    with open(image_path, 'rb') as f_img:
        image_data = f_img.read()

    with open(secret_path, 'rb') as f_secret:
        secret_data = f_secret.read()

    with open(result_path, 'wb') as f_res:
        f_res.write(image_data + secret_data)

    print(f"[OK] Данные скрыты в {result_path}")


# 2. ИЗВЛЕЧЕНИЕ (Задание Б)
def extract_data(stego_path, output_path):
    with open(stego_path, 'rb') as f:
        data = f.read()

    # Разделяем по маркеру конца JPEG (FF D9)
    parts = data.split(b'\xff\xd9')

    if len(parts) > 1:
        secret_data = parts[1]  # всё после FF D9

        with open(output_path, 'wb') as f_out:
            f_out.write(secret_data)

        print(f"[OK] Секрет извлечён в {output_path}")
    else:
        print("[!] Секрет не найден")


# 3. ОЧИСТКА (Задание В)
def clean_image(stego_path, clean_path):
    with open(stego_path, 'rb') as f:
        data = f.read()

    parts = data.split(b'\xff\xd9')

    if len(parts) > 1:
        clean_data = parts[0] + b'\xff\xd9'

        with open(clean_path, 'wb') as f_out:
            f_out.write(clean_data)

        print(f"[OK] Картинка очищена: {clean_path}")
    else:
        print("[!] Лишних данных не найдено")


# -------------------------------
# МЕНЮ (удобно для запуска)
# -------------------------------
if __name__ == "__main__":
    print("1 - Скрыть файл")
    print("2 - Извлечь файл")
    print("3 - Очистить картинку")

    choice = input("Выбери действие: ")

    if choice == "1":
        img = input("Путь к картинке: ")
        secret = input("Путь к секрету (txt/zip/rar): ")
        result = input("Имя результата: ")
        hide_data(img, secret, result)

    elif choice == "2":
        stego = input("Путь к stego-файлу: ")
        output = input("Куда сохранить секрет: ")
        extract_data(stego, output)

    elif choice == "3":
        stego = input("Путь к картинке: ")
        clean = input("Имя очищенного файла: ")
        clean_image(stego, clean)

    else:
        print("Неверный выбор")