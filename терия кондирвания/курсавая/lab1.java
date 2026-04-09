import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;
import java.util.Scanner;

public class lab1 {

    public static void main(String[] args) throws Exception {

        String keyString = "1234567890123456"; // 16 символов
        SecretKeySpec secretKey = new SecretKeySpec(keyString.getBytes(), "AES");

        Scanner scan = new Scanner(System.in);
        System.out.println("Введите текст для шифрования:");
        String text = scan.nextLine(); // читаем всю строку

        Cipher cipher = Cipher.getInstance("AES");

        // Шифрование
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        String encryptedText = Base64.getEncoder()
                .encodeToString(cipher.doFinal(text.getBytes()));

        System.out.println("Зашифрованный текст: " + encryptedText);

        // Расшифровка
        cipher.init(Cipher.DECRYPT_MODE, secretKey);
        String decryptedText = new String(cipher.doFinal(
                Base64.getDecoder().decode(encryptedText)));

        System.out.println("Расшифрованный текст: " + decryptedText);

        scan.close();
    }
}