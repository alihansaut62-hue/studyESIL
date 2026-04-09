//import javax.crypto.Cipher;
//import javax.crypto.spec.SecretKeySpec;
//import java.util.Base64;
//import java.util.Scanner;
//
////public class AESDecryptor {
//
//    public static void main(String[] args) throws Exception {
//
//        // 16 байт = 128 бит (ключ должен быть ровно 16 символов)
//        String keyString = "1234567890123456";
//
//        // Зашифрованный текст в Base64
////        String encryptedText = "UbTEdLgjnk55IUMsrM35kg==";
//        Scanner scan = new Scanner(System.in);
//        System.out.println("Введите текст для шифрования:");
//        String encryptedText = scan.nextLine(); // читаем всю строку
//
//        // Создание ключа
//        SecretKeySpec secretKey = new SecretKeySpec(keyString.getBytes(), "AES");
//
//        // Настройка шифра
//        Cipher cipher = Cipher.getInstance("AES");
//        cipher.init(Cipher.DECRYPT_MODE, secretKey);
//
//        // Расшифровка
//        byte[] decryptedBytes = cipher.doFinal(Base64.getDecoder().decode(encryptedText));
//
//        String decryptedText = new String(decryptedBytes);
//
//        System.out.println("Расшифрованный текст: " + decryptedText);
//    }
//}