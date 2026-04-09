public class BruteForceNumeric {

    private static final String REAL_PASSWORD = "74108520";

    public static void main(String[] args) {

        long startTime = System.nanoTime();
        long attempts = 0;

        int max = 100_000_000; // 10^8 (8 цифр)

        for (int i = 0; i < max; i++) {

            String guess = String.format("%08d", i);
            attempts++;

            if (guess.equals(REAL_PASSWORD)) {
                long endTime = System.nanoTime();

                System.out.println("Пароль найден: " + guess);
                System.out.println("Попыток: " + attempts);
                System.out.println("Время: " +
                        (endTime - startTime) / 1_000_000 + " мс");
                return;
            }
        }

        System.out.println("Пароль не найден.");
    }
}
