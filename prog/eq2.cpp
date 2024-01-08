/* Solutore equazioni di secondo grado a coefficienti reali */
#include <iostream>
#include "math.h"
using namespace std;

bool cout_monomio(bool isfirst, bool force0, bool skip1, double a, const char *x) {
    // Stampa a schermo un monomio, preceduto da uno spazio se necessario
    //   Se il valore è proprio 0, non stamparlo a schermo (a meno che force0). Ritorna a != 0.
    if (force0 && a == 0) {
        if (isfirst) cout << "0" << x << " ";
        else cout << "+ 0" << x << "";
        return true;
    }
    if (isfirst) {
        if (skip1) {
            if (a == 1) {
                cout << x << " ";
                return true;
            } else if (a == -1) {
                cout << "-" << x << " ";
                return true;
            }
        }
        if (a != 0) {
            cout << a << x << " ";
            return true;
        }
    } else if (a > 0) {
        if (skip1 && a == 1) cout << "+ " << x << " ";
        else cout << "+ " << a << x << " ";
        return true;
    } else if (a < 0) {
        if (skip1 && a == -1) cout << "- " << x << " ";
        else cout << "- " << -a << x << " ";
        return true;
    }
    return false;
}

int main() {
    // Acquisizione input
    cout << "--- Solutore equazioni di secondo grado a coefficienti reali ---"<<endl;
    cout << "Inserisci i coefficienti dell'equazione"<<endl;
    cout << "\tax² + bx + c = 0"<<endl;
    double a, b, c;
    cout << ">>\ta = ";
    cin >> a;
    cout << ">>\tb = ";
    cin >> b;
    cout << ">>\tc = ";
    cin >> c;
    // Restituzione a schermo dell'input acquisito
    cout << "Risolvo l'equazione:" << endl << "\t";
    bool b_first = !cout_monomio(true, false, true, a, "x²");
    bool c_first = (!cout_monomio(b_first, false, true, b, "x")) && b_first;
    if ((!cout_monomio(c_first, false, false, c, "")) && c_first) cout << "0 ";
    cout << "= 0" << endl;
    // Calcolo delle soluzioni e restituzione output a schermo
    cout << "Soluzioni:" << endl << "=>\t";
    if (a == 0) {
        if (b == 0) {
            if (c == 0) cout << "tutti i numeri complessi (reali compresi)!" << endl;
            else cout << "nessuna soluzione!" << endl;
        } else {
            cout_monomio(true, true, false, -c/b, "");
            cout << "(reale, molteplicità 1)" << endl;
        }
    } else {
        double delta = b*b - 4*a*c;
        double sq = sqrt(abs(delta))/(2*a);
        double pr = -b/2;
        if (delta > 0) {
            cout_monomio(true, true, false, pr-sq, "");
            cout << "(reale, molteplicità 1)" << endl << "=>\t";
            cout_monomio(true, true, false, pr+sq, "");
            cout << "(reale, molteplicità 1)" << endl;
        } else if (delta == 0) {
            cout_monomio(true, true, false, pr, "");
            cout << "(reale, molteplicità 2)" << endl;
        } else {
            cout_monomio(!cout_monomio(true, false, false, pr, ""), false, true, sq, "i");
            cout << "(complessa [non reale], molteplicità 1)" << endl << "=>\t";
            cout_monomio(!cout_monomio(true, false, false, pr, ""), false, true, -sq, "i");
            cout << "(complessa [non reale], molteplicità 1)" << endl;
        }
    }
}
