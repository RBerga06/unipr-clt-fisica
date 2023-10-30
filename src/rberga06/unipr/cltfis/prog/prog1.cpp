#include<iostream>
int main() {
    int x, y, z;
    std::cout << "Inserisci 3 numeri interi: ";
    std::cin >> x >> y >> z;
    float m = (x+y+z)/3.;
    std::cout << std::endl << "La media è " << m << std::endl;
}