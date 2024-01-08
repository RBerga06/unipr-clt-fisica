#include <iostream>
using namespace std;

namespace es1 {
    void main() {
        int A[4][5];
        cout << "Inserisci una tabella di 4x5 interi:" << endl;
        for (int i = 0; i < 4; i++) for (int j = 0; j < 5; j++) cin >> A[i][j];
        cout << endl << "Ecco cosa hai inserito:" << endl;
        for (int i = 0; i < 4; i++) {
            for (int j = 0; j < 5; j++) cout << " " << A[i][j];
            cout << endl;
        }
    }
}

namespace es2 {
    void main() {
        int n;
        cout << "Inserisci la dimensione della matrice quadrata: " << endl;
        cin >> n;
        int A[n][n];
        cout << "Inserisci i valori della matrice " << n << "x" << n << ":" << endl;
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) cin >> A[i][j];
        bool simm = true;
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (A[i][j] != A[j][i]) simm = false;
        cout << endl << "La matrice che hai inserito ";
        if (!simm) cout << "NON ";
        cout << "è simmetrica." << endl;
    }
}

int main() {
    es2::main();
}
