#include <iostream>

int main() {
	int a = 0;
	a++;
	int *p = &a;
	std::cout << "Value: " << a << std::endl;
	std::cout << "Pointer: " << p << std::endl;
}
