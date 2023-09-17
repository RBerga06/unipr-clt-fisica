"""Programmi per controllare i risultati degli esercizi di combinatoria."""
from itertools import permutations

def es4(n: int = 10, /) -> int:
    # $n\in\mathbb{N}_{\ge 3}$
    return len({tuple(p)[:3] for p in permutations(range(n), n)})

class es5:
    @staticmethod
    def a() -> int:
        return NotImplemented


def main() -> None:
    print("Combinatoria:")
    for f in [
        es4, es5.a,
    ]:
        print(f"- {f.__qualname__}\t-> ", end="")
        print(f())


if __name__ == "__main__":
    main()
