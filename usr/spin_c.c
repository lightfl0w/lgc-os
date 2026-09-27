#include <stdio.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    char tag = 'A';
    if (argc > 1) { tag = argv[1][0]; }

    setvbuf(stdout, 0, _IONBF, 0);
    printf("spin %c start\n", tag);

    volatile long i;
    for (i = 0; i < 30000000L; i++) {
        if ((i & 0x3FFFFF) == 0) { putchar(tag); }
    }

    printf("\nspin %c done\n", tag);
    return tag - 'A' + 1;
}
