#include <iostream>
using namespace std;

namespace es1{  // Euclide

int euclide(int a, int b) {
    if (b > a) {
        int tmp = b;
        b = a;
        a = tmp;
    }
    int r = a % b;
    while (r != 0) {
        a = b;
        b = r;
        r = a % b;
    }
    return b;
}

void main() {
    cout << "--- Algoritmo di Euclide ---" << endl;
    int a, b, r;
    cout << "a = ";
    cin >> a;
    cout << "b = ";
    cin >> b;
    cout << "MCD("<<a<<", "<<b<<") = "<<es1::euclide(a,b);
}

} // Euclide


namespace es2 {
    int main() {
        int N, n = 12;
        cout << "--- Potenze di "<< n <<" minori di N ---" << endl << "\tN = ";
        cin >> N;
        int x = 1, y;
        while (x < N) {
            cout << x << endl;
            y = x * n;
            if (y < x) {
                cout << "{!} ERROR: OVERFLOW. ABORTING. {!}" << endl;
                return -1;
            }
            x = y;
        }
        return 0;
    }
}


namespace es3 {
    int main() {
        cout << "--- Le cinque operazioni (+, -, *, /, %) ---"<<endl;
        cout << "Calcola a @ b"<<endl;
        int a, b, n;
        char op;
        cout << "\ta = ";
        cin >> a;
        cout << "\tb = ";
        cin >> b;
        cout << "\t@ = ";
        cin >> op;
        cout << "=>\t";
        switch (op) {
            case '+':
                n = a + b;
                break;
            case '-':
                n = a - b;
                break;
            case '*':
                n = a * b;
                break;
            case '/':
                if (b == 0) {
                    cout << "Error: Division by 0!"<<endl<<"\t(no, that's not a factorial, sorry!)"<<endl;
                    return -1;
                }
                n = a / b;
                break;
            default:
                cout << "Unsupported operation: '" << op << "'." << endl;
                return -1;
        }
        cout << n;
        return 0;
    }
}


int main() {
    return es3::main();
}
