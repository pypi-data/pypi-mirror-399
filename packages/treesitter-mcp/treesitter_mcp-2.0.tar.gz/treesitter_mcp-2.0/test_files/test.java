import java.util.List;
import java.util.ArrayList;

public class Calculator {
    private static final int MAX_SIZE = 100;

    public static int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }

    public static void main(String[] args) {
        int x = 5;
        int result = factorial(x);
        System.out.println("Factorial of " + x + " is " + result);
    }
}
