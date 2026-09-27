#include <stdio.h>

int main(int argc, char **argv) {
    printf("hello from C on lgc-os (argc=%d)\n", argc);
    for (int i = 0; i < argc; i++) {
        printf("  argv[%d]=%s\n", i, argv[i]);
    }
    return argc + 5;
}
