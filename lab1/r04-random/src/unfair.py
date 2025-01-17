from collections.abc import Iterable
from dataclasses import dataclass
from functools import reduce, wraps
from itertools import count
from operator import mul
import matplotlib.pyplot as plt
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Concatenate, NamedTuple, Any
from math import factorial, pow
from rich import print, reconfigure

reconfigure(highlight=False)

if TYPE_CHECKING:

    def cache[F: Callable[..., Any]](f: F) -> F:
        ...
else:
    from functools import cache


def hsv2rgb(h: float, s: float, v: float, /) -> tuple[float, float, float]:
    c = v * s
    h1 = h * 6
    x = c * (1 - abs(h1 % 2 - 1))
    r1, g1, b1 = (
        (c, x, 0)
        if 0 <= h1 < 1
        else (x, c, 0)
        if 1 <= h1 < 2
        else (0, c, x)
        if 2 <= h1 < 3
        else (0, x, c)
        if 3 <= h1 < 4
        else (x, 0, c)
        if 4 <= h1 < 5
        else (c, 0, x)
    )
    m = v - c
    return r1 + m, g1 + m, b1 + m


def rich_hsv(h: float, s: float, v: float, /) -> str:
    r, g, b = hsv2rgb(h, s, v)
    return f"rgb({int(r * 255)},{int(g * 255)},{int(b * 255)})"


def pfmt(p: float, /) -> str:
    s = f"{p:>9.3%}"
    return f"[{rich_hsv((p**.5)/3, 1, 1)}]{s}[/]"


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
    def probabilities_add1(self, /, *, n: int = 400) -> list[float]:
        return [bernoulli(a + 1, n - (a + 1)).Fworse(1 / 6) for a in self.counts(n=n)]

    @cache
    def probabilities_sub1(self, /, *, n: int = 400) -> list[float]:
        return [bernoulli(a - 1, n - (a - 1)).Fworse(1 / 6) for a in self.counts(n=n)]

    @cache
    def fairness(self, /, *, n: int = 400) -> float:
        return reduce(mul, self.old_probabilities(n=n), 1) ** (1 / 6)

    @cache
    def chi_square(self, /, *, n: int = 400) -> float:
        e = n / 6
        return sum([(a - e) ** 2 / e for a in self.counts(n=n)])

    def analysis(self, /, *, n: int = 400, plots: bool = False, log: bool = False, log_alt: bool = False) -> None:
        """Note: returns (probabilities, fairness)."""
        probs = self.probabilities(n=n)
        avg = sum(probs) / 6
        avg_geo = reduce(mul, probs) ** (1 / 6)
        avg_harm = 1 / sum([1 / x for x in probs])
        if log_alt:
            print(f"{self.color}+\t" + "".join(map(pfmt, self.probabilities_add1(n=n))))
        if log:
            print(f"{self.color}\t" + "".join(map(pfmt, probs)), f" ->{pfmt(avg)} {pfmt(avg_geo)} {pfmt(avg_harm)}")
        if log_alt:
            print(f"{self.color}-\t" + "".join(map(pfmt, self.probabilities_sub1(n=n))))
        if plots:
            for a in self.counts(n=n):
                try:
                    plotdist(a, n - a)
                except KeyboardInterrupt:
                    print()
                    break


def load_data(file: Path, colors: Iterable[str], /) -> tuple[Die, ...]:
    rows: list[list[int]] = [
        [*map(int, line.split("\t"))]
        for line in map(str.strip, file.read_text().strip().splitlines())
        if line and not line.startswith("#")
    ]
    return tuple([Die(tuple(col), color) for color, *col in zip(colors, *rows)])


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


def mini_simulation(dice: int = 1, /, *, n: int = 400):
    """Run a mini simulation."""
    from random import randint

    rolls = [[randint(1, 6) for _j in range(n)] for _i in range(dice)]
    FILE_MINI_SIMUL.write_text("\n".join(["\t".join(map(str, row)) for row in zip(*rolls)]))


FILE = Path(__file__).parent.parent / "data/dadi.txt"
FILE_MINI_SIMUL = Path(__file__).parent.parent / "data/dadi-mini-simul.txt"
COLORS = "Rosso Verde Blu Viola Nero Bianco".split(" ")
COLORS_MINI_SIMUL = (f"👾 {n}" for n in count())

# mini_simulation(360)

dice0, dice1 = load_data(FILE, COLORS), load_data(FILE_MINI_SIMUL, COLORS_MINI_SIMUL)
dice = dice0 + dice1
# for die in dice:
#     print(die.color, *die.counts(), sep="\t")
for die in dice0:
    print(*die.counts(), sep="\t")
    # die.analysis(log=True, log_alt=True)  # , plots=True)
# print("—" * 95)
# for die in dice1:
#     die.analysis(log=True)  # , plots=die.color == "👾 3")
# for die in dice:
#     print(die.chi_square())
# timeAnalysis(dice[0], plot=True)
