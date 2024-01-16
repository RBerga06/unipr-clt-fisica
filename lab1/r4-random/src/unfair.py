# Bro, it's unfair! We don't have the tools...
# ... so let's make them ourselves!
from functools import reduce, wraps
from operator import mul
import matplotlib.pyplot as plt
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Concatenate, NamedTuple, Any
from math import factorial, pow

if TYPE_CHECKING:

    def cache[F: Callable[..., Any]](f: F) -> F:
        ...
else:
    from functools import cache


type tuple6[T] = tuple[T, T, T, T, T, T]


def load_data(file: Path, /, *, n: int = 400) -> tuple[int, tuple6[tuple6[int]]]:
    rows: list[list[int]] = [
        [*map(int, line.split("\t"))]
        for line in map(str.strip, file.read_text().strip().splitlines())
        if line and not line.startswith("#")
    ][:n]
    cols: list[tuple[int, ...]] = [*map(tuple, zip(*rows))]
    return len(rows), tuple([tuple([col.count(i) for i in range(1, 7)]) for col in cols])  # type: ignore


def nicecallrepr[**P, R](__f__: Callable[P, R], __r__: R, *args: P.args, **kwargs: P.kwargs) -> str:
    return f"{__f__.__qualname__}({f'{args!r}'[1:-1]}{', ' if (args and kwargs) else ''}{f'{kwargs!r}'[1:-1]}) -> {__r__!r}"


def printcalls[**P, R](
    repr: Callable[Concatenate[Callable[P, R], R, P], str] = nicecallrepr,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(f: Callable[P, R], /) -> Callable[P, R]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            r = f(*args, **kwargs)
            print(repr(f, r, *args, **kwargs))
            return r

        return wrapper

    return decorator


@cache
def binom(n: int, k: int, /) -> int:
    return factorial(n) // (factorial(k) * factorial(n - k))


@cache
def riemann(f: Callable[[float], float], x1: float, x2: float, /) -> float:
    """Calculate a Riemann integral."""
    Dx = x2 - x1
    n = max(1, int(round(Dx * RIEMANN_N_PER_UNIT)))
    dx = Dx / n
    return sum([f(x1 + i * dx) * dx for i in range(n)])


RIEMANN_N_PER_UNIT = 100_000


class _bernoulli(NamedTuple):
    a: int
    b: int

    @cache
    def f(self, x: float, /) -> float:
        a, b = self.a, self.b
        return binom(a + b, a) * pow(x, a) * pow(1 - x, b)

    @cache
    # @printcalls(lambda __f__, __r__, *args, **kwargs: f"F {args[1]:.2f} -> {__r__}")  #  type: ignore
    def F(self, x: float, /) -> float:
        return riemann(self.f, 0, x)

    @cache
    def Fin(self, x1: float, x2: float, /) -> float:
        return riemann(self.f, x1, x2)

    @cache
    def P(self, x: float, /) -> float:
        return self.F(x) * (self.a + self.b + 1)

    @cache
    def Pin(self, x1: float, x2: float, /) -> float:
        return self.Fin(x1, x2) * (self.a + self.b + 1)


@cache
def bernoulli(a: int, b: int, /) -> _bernoulli:
    return _bernoulli(a, b)


# @cache
# def RecursiveIntegral(a: int, b: int, x1: float, x2: float) -> float:
#     np1 = a + b + 1
#     if b == 0:
#         return (pow(x2, np1) - pow(x1, np1)) / np1
#     contrib = f(a + 1, b, x2) - f(a + 1, b, x1)
#     return (contrib - b * RecursiveIntegral(a + 1, b - 1, x1, x2)) / (a + 1)


@cache
def p(n: int, a: int, x1: float, x2: float) -> float:
    return (n + 1) * bernoulli(a, n - a).Fin(x1, x2)


def splitrange(x1: float, x2: float, n: int) -> list[tuple[float, float]]:
    dx = (x2 - x1) / n
    return [(x1 + i * dx, x1 + (i + 1) * dx) for i in range(n)]


def linspace(x1: float, x2: float, n: int, /, *, end: bool = True) -> list[float]:
    dx = (x2 - x1) / (n if end else n + 1)
    return [x1 + i * dx for i in range(n + 1)]


def fplot(f: Callable[[float], float], x1: float, x2: float, n: int, /) -> tuple[list[float], list[float]]:
    Xs = linspace(x1, x2, n, end=True)
    Ys = [f(x) for x in Xs]
    plt.plot(Xs, Ys)  # type: ignore
    return Xs, Ys


def ifplot(
    f: Callable[[float, float], float], X1: float, X2: float, n: int, /, *, norm: bool = True, hist: bool = False
) -> None:
    Xs: list[float] = []
    Ys: list[float] = []
    factor = n / (X2 - X1) if norm else 1.0
    for x1, x2 in splitrange(X1, X2, n):
        y = f(x1, x2) * factor
        Xs.append((x1 + x2) / 2)
        Ys.append(y)
    if hist:
        plt.bar(Xs, Ys, width=(X2 - X1) / n)  # type: ignore
    else:
        plt.plot(Xs, Ys)  # type: ignore


def vlineplot(Ys: list[float], x: float) -> None:
    plt.plot([x, x], [min(Ys), max(Ys)])  # type: ignore


def _fixparams(n: int, a: int, /) -> tuple[int, int]:
    b = n - a
    if b > a:
        return a, b
    return b, a


def plotdist(a: int, b: int, *vlines: float) -> None:
    X1 = 0  # 0.075
    X2 = 1  # 0.2
    N = 1_000
    B = bernoulli(a, b)
    fplot(B.f, X1, X2, N)
    fplot(B.P, X1, X2, N)
    # ifplot(B.Pin, X1, X2, 1, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 2, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 3, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 10, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 20, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 30, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 40, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 50, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 100, norm=False, hist=True)
    for vline in vlines:
        vlineplot([0, 1], vline)
    plt.show()  # type: ignore


e = 1 / 36


class Die(NamedTuple):
    n: int
    data: tuple6[int]
    color: str

    @cache
    def probabilities(self, /) -> tuple6[float]:
        return tuple([bernoulli(*_fixparams(self.n, a)).Pin(1 / 6 - e, 1 / 6 + e) for a in self.data])  #  type: ignore

    @cache
    def fairness(self, /) -> float:
        return reduce(mul, self.probabilities(), 1)

    def analysis(self, *, plots: bool = False, log: bool = False) -> tuple[tuple6[float], float]:
        probs = self.probabilities()
        fair = self.fairness()
        if log:
            print(f"{self.color:<6}", "".join([f"{p:>9.3%}" for p in probs]), " ->", f"{fair:>8.3%}")
        if plots:
            for j in range(6):
                try:
                    plotdist(*_fixparams(self.n, self.data[j]), 1 / 6, 1 / 6 - e, 1 / 6 + e)
                except KeyboardInterrupt:
                    print()
                    plots = False
                break
        return probs, fair


class Data(NamedTuple):
    n: int
    data: tuple6[tuple6[int]]

    @cache
    def dice(self, /) -> tuple6[Die]:
        return tuple([Die(self.n, self.data[i], COLORS[i]) for i in range(6)])  # type: ignore


FILE = Path(__file__).parent.parent / "data/dadi.txt"
COLORS = "Rosso Verde Blu Viola Nero Bianco".split(" ")

alldata: list[Data] = [Data(*load_data(FILE, n=n)) for n in range(1, 401)]
fairnesses: tuple6[list[float]] = ([], [], [], [], [], [])
probs: tuple6[tuple6[list[float]]] = (
    ([], [], [], [], [], []),
    ([], [], [], [], [], []),
    ([], [], [], [], [], []),
    ([], [], [], [], [], []),
    ([], [], [], [], [], []),
    ([], [], [], [], [], []),
)
for data in alldata:
    print(f"Analyzing {data.n}...")
    for i, die in enumerate(data.dice()):
        fairnesses[i].append(die.fairness())
        for j, prob in enumerate(die.probabilities()):
            probs[i][j].append(prob)

for j in range(6):
    plt.plot(probs[0][j])  # type: ignore
# plt.plot([sum(prbs) for prbs in zip(*probs[0])])
plt.plot(fairnesses[0])  # type: ignore
plt.show()  # type: ignore
