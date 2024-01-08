#include <iostream>
using namespace std;

namespace es1{
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

int main() {
    es1::main();
}
