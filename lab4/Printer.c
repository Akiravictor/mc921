#include <stdio.h>
extern int sm_main;
extern void sm_init();

int main() {

    sm_init();
    printf("%d\n",sm_main);
    return 0;
}
