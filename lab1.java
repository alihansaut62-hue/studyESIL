import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.util.Base64;
import java.util.Scanner;
import java.io.File;

public class AESExample {

    public static void main(String[] args) throws Exception {

        String keyString = "1234567890123456";
        SecretKeySpec secretKey = new SecretKeySpec(keyString.getBytes(), "AES");

        String text = "";   // объявляем заранее

        try {
            File file = new File("higaa.txt");
            Scanner scanner = new Scanner(file);

            while (scanner.hasNextLine()) {
                text += scanner.nextLine();   // читаем файл
            }

            scanner.close();

        } catch (Exception e) {
            System.out.println("Ошибка: " + e);
        }

        Cipher cipher = Cipher.getInstance("AES");

        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        String encryptedText = Base64.getEncoder()
                .encodeToString(cipher.doFinal(text.getBytes()));

        System.out.println("Зашифрованный текст: " + encryptedText);

        cipher.init(Cipher.DECRYPT_MODE, secretKey);
        String decryptedText = new String(cipher.doFinal(
                Base64.getDecoder().decode(encryptedText)));

        System.out.println("Расшифрованный текст: " + decryptedText);
    }
}