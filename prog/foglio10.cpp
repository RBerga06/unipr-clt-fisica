#include <iostream>
using namespace std;

namespace es2{
    void main() {
        int A[4];
        A[0] = 0;
        A[1] = 0;
        cout << "Ecco cosa c'è in memoria: '" << A[2] << "', '" << A[3] << "'" << endl;
    }
}

namespace es3 {
    void main() {
        cout << "Temperature in una settimana (°C): ";
        int T[7];
        for (int i = 0; i<7; i++) cin >> T[i];
        cout << "Temperature acquisite: ";
        for (int i = 0; i<7; i++) cout << T[i] << " ";
        cout << endl;
        int t = T[0], M = t, m = t;
        for (int i = 1; i < 7; i++) {
            int t = T[i];
            if (t > M) M = t;
            if (t < m) m = t;
        }
        cout << "Massima: " << M << "°C" << endl;
        cout << "Minima: " << m << "°C" << endl;
    }
}

int main() {
    es3::main();
}
