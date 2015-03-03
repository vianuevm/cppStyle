#include <iostream>
using namespace std;

int main() {
    int x = 0;
    // check compound operators
    x += 1;
    x *= 1;
    x /= 1;
    x %= 2;
    x != 1;
    x >= 2;
    x <= 2;
    x && false;
    x || true;

    // normal operators
    x + 1;
    x - 1;
    x * 2;
    x / 1;
    x % 2;
    x > 1;
    x < 1;
    x = 1;
    !x;
    -x;
    +x;

    return 0;
}