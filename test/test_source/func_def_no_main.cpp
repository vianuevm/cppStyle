#include <iostream>
using namespace std;

void myFunc() {
	cout << "I am some code";
}

int myBar(char c) {
	if (c >= '0' && c <= '9')
		return c - '0';
	return -1;
}