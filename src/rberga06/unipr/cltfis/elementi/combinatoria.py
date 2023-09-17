"""Programmi per controllare i risultati degli esercizi di combinatoria."""
from itertools import permutations
from typing import Callable, Iterator

def es4(n: int = 10, /) -> int:
    # $n\in\mathbb{N}_{\ge 3}$
    return len({tuple(p)[:3] for p in permutations(range(n), n)})

class es5:
    @staticmethod
    def _all() -> Iterator[str]:
        return filter(lambda x: "0" not in x, map(str, range(1_000, 10_000)))

    @staticmethod
    def a() -> int:
        return len([n for n in es5._all() if len(set(n)) == 4])

    @staticmethod
    def b() -> int:
        nums: list[str] = []
        for n in es5._all():
            last = -1
            ok = True
            for digit in map(int, n):
                if digit <= last:
                    ok = False
                    break
                last = digit
            if not ok:
                continue
            nums.append(n)
        return len(nums)

    @staticmethod
    def c() -> int:
        nums: list[str] = []
        for n in es5._all():
            last = -1
            ok = True
            for digit in map(int, n):
                if digit < last:
                    ok = False
                    break
                last = digit
            nums.append(n)
            if not ok:
                continue
            nums.append(n)
        return len(nums)

    @staticmethod
    def d() -> int:
        nums: list[str] = []
        for n in es5._all():
            odd = 0
            for digit in n:
                if int(digit) % 2:
                    odd += 1
            if odd > 2:
                continue
            nums.append(n)
        return len(nums)

    @staticmethod
    def e() -> int:
        nums: list[str] = []
        for n in es5._all():
            odd = 0
            for digit in n:
                if int(digit) % 2:
                    odd += 1
            if odd > 2:
                continue
            nums.append(n)
        return len(nums)

    @staticmethod
    def f() -> int:
        nums: list[str] = []
        for n in map(str, range(10_000)):
            if len(set(n)) != 4:
                continue  # not all digits are distinct
            if n[0] == "0":
                continue
            nums.append(n)
        return len(nums)

    def __iter__(self, /) -> Iterator[Callable[[], int]]:
        yield from (self.a, self.b, self.c, self.d, self.e, self.f)


def main() -> None:
    print("Combinatoria:")
    for f in [es4, *es5()]:
        print(f"- {f.__qualname__}\t-> ", end="", flush=True)
        print(f(), flush=True)


if __name__ == "__main__":
    main()
