#include <vector>
#include <iostream>

/*** Insiemi numerici ***/
typedef unsigned long long Nat;  // Naturali
typedef long long Int;           // Interi
typedef long double Real;        // Reali


/*** Successioni generiche ***/
template<typename T>
class Successione {
    private:
        T(*_f)(Successione<T> s, Nat n);
    public:
        T empty;
        std::vector<T> values;
        Successione(T empty, T(*f)(Successione<T> s, Nat n)) { this->_f = f; this->empty = empty; }
        T f(Nat n) { return this->_f(*this, n); }
        T at(Nat n) {
            while (values.size() <= n) { values.push_back(empty); };
            T value = values[n];
            if (value == empty) {
                value = f(n);
                values[n] = value;
            };
            return value;
        };
        std::vector<T> upTo(Nat max) { return inRange(0, max); }
        std::vector<T> inRange(Nat min, Nat max) {
            std::vector<T> v;
            for (Nat i = min; i<=max; i++) { v.push_back(at(i)); }
            return v;
        }
        T operator[](Nat n) { return at(n); }
};


/*** Stampa a schermo un vettore ***/
template<typename T>
std::ostream &operator<<(std::ostream &os, std::vector<T> const &v) {
    os << "[";
    if (v.size() == 0) { return os << "]"; }
    os << v[0];
    for (int i = 1; i < v.size(); i++) {
        os << ", " << v[i];
    }
    return os << "]";
}


/*** Utility per numeri primi ***/
bool is_prime(Successione<Nat> P, Nat x) {
    Real stop = sqrt(x);
    Int i = 1;
    Int p = P[1];
    while (p <= stop) {
        if (x % p == 0) { return false; }
        i++;
        p = P[i];
    }
    return true;
}


/*** Programma principale ***/
int main() {

    // Successione di Fibonacci (def. ricorsiva)
    auto *fibonacci = new Successione<Nat>(0, [](auto s, Nat n) -> Nat {
        switch (n) {
            case 0:  return 1;
            case 1:  return 1;
            default: return s[n-1]+s[n-2];
        };
    });

    // Successione dei fattoriali (def. ricorsiva)
    auto *factorials = new Successione<Nat>(0, [](auto s, Nat n) -> Nat {
        switch (n) {
            case 0: return 1;
            default: return s[n-1]*n;
        }
    });

    // Funzione seno valutata sui naturali
    auto *sine = new Successione<Real>(0, [](auto, Nat n) -> Real { return sin(n) });

    // Successione dei numeri primi
    auto *primes = new Successione<Nat>(0, [](auto P, Nat n) -> Nat {
        switch (n) {
            case 0: return 2;
            case 1: return 3;
            default: {
                Nat x = P[n-1] + 2;
                while (true) {
                    if (is_prime(P, x)) {
                        return x;
                    }
                    x += 2;
                }
            };
        }
    });

    Nat N = 20;
    std::cout << "Fibonacci:" << fibonacci->upTo(N) << std::endl;
    std::cout << "Fattoriali:" << factorials->upTo(N) << std::endl;
    std::cout << "Funzione seno:" << sine->upTo(N) << std::endl;
    std::cout << "Numeri primi:" << primes->upTo(N) << std::endl;
}
