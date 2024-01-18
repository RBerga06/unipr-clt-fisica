from dataclasses import dataclass
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


@dataclass(slots=True, frozen=True)
class Die:
    data: tuple[float, ...]
    color: str

    @cache
    def epsilon(self, t: int, /) -> float:
        return 1 / 36

    @cache
    def count(self, x: int, /, *, n: int = 400) -> int:
        return self.data[:n].count(x)

    @cache
    def counts(self, /, *, n: int = 400) -> list[int]:
        return [self.count(i, n=n) for i in range(1, 7)]

    @cache
    def old_probability(self, x: int, /, *, n: int = 400) -> float:
        a = self.count(x, n=n)
        e = self.epsilon(n)
        return bernoulli(a, n - a).Fin(1 / 6 - e, 1 / 6 + e)

    @cache
    def old_probabilities(self, /, *, n: int = 400) -> list[float]:
        e = self.epsilon(n)
        return [bernoulli(a, n - a).Fin(1 / 6 - e, 1 / 6 + e) for a in self.counts(n=n)]

    @cache
    def probability(self, x: int, /, *, n: int = 400) -> float:
        a = self.count(x, n=n)
        return bernoulli(a, n - a).Fworse(1 / 6)

    @cache
    def probabilities(self, /, *, n: int = 400) -> list[float]:
        return [bernoulli(a, n - a).Fworse(1 / 6) for a in self.counts(n=n)]

    @cache
    def fairness(self, /, *, n: int = 400) -> float:
        return reduce(mul, self.old_probabilities(n=n), 1) ** (1 / 6)

    @cache
    def chi_square(self, /, *, n: int = 400) -> float:
        e = n / 6
        return sum([(a - e) ** 2 / e for a in self.counts(n=n)])

    def analysis(self, /, *, n: int = 400, plots: bool = False, log: bool = False) -> tuple[list[float], float]:
        """Note: returns (probabilities, fairness)."""
        probs = self.probabilities(n=n)
        fair = self.fairness(n=n)
        if log:
            print(f"{self.color:<6}", "".join([f"{p:>9.3%}" for p in probs]), " ->", f"{fair:>8.3%}")
        if plots:
            for a in self.counts(n=n):
                try:
                    plotdist(a, n - a)
                except KeyboardInterrupt:
                    print()
                    break
        return probs, fair


def load_data(file: Path, /) -> tuple6[Die]:
    rows: list[list[int]] = [
        [*map(int, line.split("\t"))]
        for line in map(str.strip, file.read_text().strip().splitlines())
        if line and not line.startswith("#")
    ]
    return tuple([Die(tuple(col), color) for color, *col in zip(COLORS, *rows)])  # type: ignore


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
    def avg(self, /) -> float:
        return (self.a + 1) / (self.a + self.b + 2)

    @cache
    def f(self, x: float, /) -> float:
        a, b = self.a, self.b
        return (a + b + 1) * binom(a + b, a) * pow(x, a) * pow(1 - x, b)

    @cache
    # @printcalls(lambda __f__, __r__, *args, **kwargs: f"F {args[1]:.2f} -> {__r__}")  #  type: ignore
    def F(self, x: float, /) -> float:
        return riemann(self.f, 0, x)

    @cache
    def Fin(self, x1: float, x2: float, /) -> float:
        return riemann(self.f, max(x1, 0), min(x2, 1))

    @cache
    def Fworse(self, x: float, /) -> float:
        m = self.avg()
        d = abs(x - m)
        return 1 - self.Fin(m - d, m + d)


@cache
def bernoulli(a: int, b: int, /) -> _bernoulli:
    return _bernoulli(a, b)


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


def plotdist(a: int, b: int, *vlines: float) -> None:
    X1 = 0  # 0.075
    X2 = 1  # 0.2
    N = 1_000
    B = bernoulli(a, b)
    avg = B.avg()
    dx = abs(avg - 1 / 6)
    _Xs, Ys = fplot(B.f, X1, X2, N)
    # fplot(B.F, X1, X2, N)
    # ifplot(B.Pin, X1, X2, 1, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 2, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 3, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 10, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 20, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 30, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 40, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 50, norm=False, hist=True)
    # ifplot(B.Pin, X1, X2, 100, norm=False, hist=True)
    for vline in [avg, avg - dx, avg + dx, *vlines]:
        vlineplot([min(Ys), max(Ys)], vline)
    plt.show()  # type: ignore


class Data(NamedTuple):
    n: int
    data: tuple6[tuple6[int]]

    @cache
    def dice(self, /) -> tuple6[Die]:
        return tuple([Die(self.n, self.data[i], COLORS[i]) for i in range(6)])  # type: ignore


def timeAnalysis(d: Die, /, *, plot: bool = False) -> tuple[tuple6[list[float]], list[float]]:
    """Note: Return (probabilities, fairness)"""
    probabilities: tuple6[list[float]] = ([], [], [], [], [], [])
    fairness: list[float] = []
    for t in range(1, 401):
        print(f"Analyzing {t}...")
        fairness.append(d.fairness(n=t))
        for j, prob in enumerate(d.old_probabilities(n=t)):
            probabilities[j].append(prob)
    if plot:
        for j in range(6):
            plt.plot(probabilities[j])  # type: ignore
        # plt.plot([sum(prbs) for prbs in zip(*probs[0])])
        plt.plot(fairness)  # type: ignore
        plt.show()  # type: ignore
    return probabilities, fairness


FILE = Path(__file__).parent.parent / "data/dadi.txt"
COLORS = "Rosso Verde Blu Viola Nero Bianco".split(" ")

dice = load_data(FILE)
for die in dice:
    print(die.counts())
for die in dice:
    die.analysis(log=True)  # , plots=True)
for die in dice:
    print(die.chi_square())
# timeAnalysis(dice[0], plot=True)
