import java.util.Scanner;

    public class CaesarCipher {

        // Универсальная функция шифрования
        public static String encrypt(String text, int shift) {
            StringBuilder result = new StringBuilder(text.length());

            for (char c : text.toCharArray()) {
                if (c >= 'a' && c <= 'z') {               // латиница строчные
                    result.append((char) ((c - 'a' + shift) % 26 + 'a'));
                } else if (c >= 'A' && c <= 'Z') {        // латиница заглавные
                    result.append((char) ((c - 'A' + shift) % 26 + 'A'));
                } else if (c >= 'а' && c <= 'я') {        // кириллица строчные
                    result.append((char) ((c - 'а' + shift) % 32 + 'а'));
                } else if (c >= 'А' && c <= 'Я') {        // кириллица заглавные
                    result.append((char) ((c - 'А' + shift) % 32 + 'А'));
                } else {                                  // прочие символы
                    result.append(c);
                }
            }

            return result.toString();
        }

        public static void main(String[] args) {
            Scanner scanner = new Scanner(System.in);

            System.out.print("Введите текст для шифрования: ");
            String userText = scanner.nextLine();

            System.out.print("Введите числовой ключ (сдвиг): ");
            int userKey = scanner.nextInt();

            String encrypted = encrypt(userText, userKey);
            System.out.println("Результат шифрования: " + encrypted);
        }
    }

