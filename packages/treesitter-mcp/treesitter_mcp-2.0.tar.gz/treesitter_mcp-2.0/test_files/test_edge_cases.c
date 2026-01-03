#include <stdio.h>

#define _INTERNAL_MACRO(x) (x * 2)
#define TRAILING_ (42)
#define __builtin_expect(x, y) (x)

void normal_func() {
    printf("Normal function\n");
}

int main() {
    // Test various patterns that should be filtered out
    int a = _INTERNAL_MACRO(5);
    int b = TRAILING_;
    int c = __builtin_expect(1, 1);

    // Normal function call (should be included)
    normal_func();
    printf("Done\n");

    return 0;
}
