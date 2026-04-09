def extract_secret(stego_file):
    with open(stego_file, 'rb') as f:
        data = f.read()
    
    # Разделяем по маркеру конца JPEG
    parts = data.split(b'\xff\xd9')
    
    if len(parts) > 1:
        secret_data = parts[1]
        
        try:
            print("Секретное сообщение:")
            print(secret_data.decode('utf-8'))
        except:
            print("Секрет (в бинарном виде):")
            print(secret_data)
    else:
        print("Секрет не найден!")

# Запуск
extract_secret('stego_result.jpg')