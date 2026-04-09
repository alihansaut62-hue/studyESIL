import java.security.MessageDigest;

public class HashExample {

    public static void main(String[] args) throws Exception {

        String password = "MyStrongPassword";

        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] hash = md.digest(password.getBytes());

        StringBuilder hexString = new StringBuilder();
        for (byte b : hash) {
            hexString.append(String.format("%02x", b));
        }

        System.out.println("SHA-256 hash: " + hexString.toString());
    }
}