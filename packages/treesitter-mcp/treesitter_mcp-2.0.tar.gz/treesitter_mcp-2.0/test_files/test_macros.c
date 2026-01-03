#include <stdio.h>

#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define DEBUG_LOG(msg) printf(msg)

void helper() {
    printf("Helper function\n");
}

int main() {
    int x = 5;
    int y = 10;
    int max_val = MAX(x, y);
    int min_val = MIN(x, y);
    DEBUG_LOG("Debug message\n");
    helper();
    printf("Result: %d %d\n", max_val, min_val);
    return 0;
}
