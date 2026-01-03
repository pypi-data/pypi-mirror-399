#include <stdio.h>
#include "stdlib.h"

int global_counter = 0;

/* Calculate factorial */
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

/* Main function */
int main() {
    int x = 5;
    int result = factorial(x);
    printf("Factorial of %d is %d\n", x, result);
    global_counter = global_counter + 1;
    return 0;
}

struct Point {
    int x;
    int y;
};
