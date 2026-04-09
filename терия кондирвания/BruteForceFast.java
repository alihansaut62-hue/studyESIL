import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;

public class BruteForceFast {

    private static final String REAL_PASSWORD = "7410";
    private static final int PASSWORD_LENGTH = 8;
    private static final char[] CHARS =
            "0123456789abcdefghijklmnopqrstuvwxyz".toCharArray();

    private static final int BASE = CHARS.length;

    private static AtomicBoolean found = new AtomicBoolean(false);
    private static AtomicLong attempts = new AtomicLong(0);

    public static void main(String[] args) throws InterruptedException {

        int threads = Runtime.getRuntime().availableProcessors();
        ExecutorService executor = Executors.newFixedThreadPool(threads);

        long totalCombinations = (long) Math.pow(BASE, PASSWORD_LENGTH);
        long rangePerThread = totalCombinations / threads;

        long startTime = System.nanoTime();

        System.out.println("[*] Используется ядер: " + threads);
        System.out.println("[*] Всего комбинаций: " + totalCombinations);

        for (int t = 0; t < threads; t++) {

            long start = t * rangePerThread;
            long end = (t == threads - 1)
                    ? totalCombinations
                    : start + rangePerThread;

            executor.submit(() ->
                    bruteForceRange(start, end, startTime));
        }

        executor.shutdown();
        executor.awaitTermination(Long.MAX_VALUE, TimeUnit.NANOSECONDS);
    }

    private static void bruteForceRange(long start,
                                        long end,
                                        long startTime) {

        char[] guess = new char[PASSWORD_LENGTH];

        for (long i = start; i < end && !found.get(); i++) {

            long temp = i;

            for (int pos = PASSWORD_LENGTH - 1; pos >= 0; pos--) {
                guess[pos] = CHARS[(int)(temp % BASE)];
                temp /= BASE;
            }

            long current = attempts.incrementAndGet();

            if (checkPassword(guess)) {
                found.set(true);

                long endTime = System.nanoTime();
                double seconds =
                        (endTime - startTime) / 1_000_000_000.0;

                System.out.println("\n[+] Пароль найден: " +
                        new String(guess));
                System.out.println("[+] Попыток: " + current);
                System.out.println("[+] Время: " +
                        seconds + " сек");
                System.out.println("[+] Скорость: " +
                        (current / seconds) + " попыток/сек");
            }
        }
    }

    private static boolean checkPassword(char[] guess) {

        for (int i = 0; i < PASSWORD_LENGTH; i++) {
            if (guess[i] != REAL_PASSWORD.charAt(i))
                return false;
        }

        return true;
    }
}