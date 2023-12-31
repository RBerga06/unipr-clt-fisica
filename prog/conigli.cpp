#include<iostream>
#include<array>
#define N_GENERATIONS 10

typedef unsigned long long Nat;

// Decide how many children bunnies of age t make
Nat n_babies(int t, Nat n) {
    switch (t) {
        case 0:  return 0;
        default: return n;
    };
};

// Decide how many bunnies of age t die
//   (all bunnies of age N_GENERATIONS-2 die)
Nat n_die(int t, Nat n) {
    return n * pow(2, (t-N_GENERATIONS)/2);
}


class Population {
    public:
        Nat babies() { return generations[0]; }
        Nat adult() {
            Nat total = 0;
            for (int i=1; i<N_GENERATIONS; i++) {
                total += generations[i];
            }
            return total;
        }
        Nat dead() { return _dead; }
        Nat alive() { return babies() + adult(); }
        Nat ever_existed() { return alive() + dead(); }
        Nat operator[](int age) { return generations[age]; }
        void inject(Nat n, int age) { generations[age] += n; }
        void inject(Nat n) { inject(n, 0); }
        void next() {
            Nat tot_babies = 0;
            // Shift all bunnies by 1 month, starting from the oldest ones
            for (int t=N_GENERATIONS-2; t>=0; t--) {
                Nat bunnies = generations[t];
                Nat dead = n_die(t, bunnies);
                tot_babies += n_babies(t, bunnies);
                generations[t+1] += (bunnies - dead);
                generations[t] = 0;
                this->_dead += dead;
            }
            generations[0] = tot_babies;
        }
    private:
        // index:   0    1    2   ...    N_GENERATIONS-2,   N_GENERATIONS-1
        // array: [#0m, #1m, #2m, ..., #(N_GENERATIONS-2)m, "infinitely old"]
        std::array<Nat, N_GENERATIONS> generations;
        Nat _dead = 0;
};


void printPop(int t, Population *p) {
    std::cout << t
      << '\t' << p->babies()
      << '\t' << p->adult()
      << '\t' << p->alive()
      << '\t' << p->dead()
      << '\t' << p->ever_existed()
      << std::endl;
}


int main() {
    const int T = 1000;
    std::cout << "months\tbabies\tadult\talive\tdead\ttotal" << std::endl;
    auto *p = new Population;
    p->inject(1);
    printPop(0, p);
    for (int t=1; t<T; t++) {
        p->next();
        printPop(t, p);
    }
}
