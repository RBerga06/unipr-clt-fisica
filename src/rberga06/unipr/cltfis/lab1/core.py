#!/usr/bin/env python3
# pyright: reportConstantRedefinition=false
"""Core data."""
from dataclasses import dataclass
from functools import cache
import math
from typing import Callable, Literal, Self, final, overload
from typing_extensions import override
from matplotlib import pyplot as plt
from .datum import Measure, Datum as DataPoint, π, g
from .dataset import DataSet


def plotf(f: Callable[[float], float], min: float, max: float, /, *, n: int = 1000) -> None:
    dx = (max - min)/n
    xs = [min + i*dx for i in range(n)]
    ys = [f(x) for x in xs]
    plt.plot(xs, ys, "")  # type: ignore


@final
@dataclass(slots=True, frozen=True, repr=False)
class Function:
    f: Callable[[float], float]
    f1: Callable[[float], float]

    @overload
    def __call__(self, x: float, /) -> float: ...
    @overload
    def __call__(self, x: "Measure", /) -> "Measure": ...
    def __call__(self, x: "float | Measure", /) -> "float | Measure":
        if isinstance(x, float | int):
            return self.f(x)
        return DataPoint(self.f(x.best), abs(self.f1(x.best)) * x.delta)

    def __rmul__(self, k: float, /) -> "Function":
        return Function(lambda x: k*self.f(x), lambda x: k*self.f1(x))

    def __neg__(self, /) -> "Function":
        return self.__rmul__(-1)


@dataclass(slots=True, frozen=True)
class DistBin(Measure):
    data: tuple[DataPoint, ...]
    min: float
    max: float

    @property
    @cache
    def len(self, /) -> int:  # type: ignore
        return len(self.data)

    @property
    @cache
    @override
    def best(self, /) -> float:  # type: ignore
        return (self.max + self.min)/2

    @property
    @cache
    @override
    def delta(self, /) -> float:  # type: ignore
        return self.width / 2

    @property
    @cache
    def width(self, /) -> float:
        return self.max - self.min


@dataclass(slots=True, frozen=True)
class Distribution(DataSet):
    bins: tuple[DistBin, ...]

    @property
    @cache
    @override
    def len(self, /) -> int:
        return sum(bin.len for bin in self.bins)

    @property
    @cache
    @override
    def avg(self, /) -> float:
        return sum(len(bin.data) * bin.best for bin in self.bins)/self.len

    def histogram(self, /) -> None:
        for bin in self.bins:
            print(f"  - {[x.best for x in bin.data]}")
        plt.bar(  # type: ignore
            [bin.best for bin in self.bins],
            # [bin.len/(self.len*bin.width) for bin in self.bins],
            [bin.len for bin in self.bins],
            [bin.width for bin in self.bins],
        )

    @classmethod
    def from_dataset(
        cls,
        data: DataSet,
        /, *,
        m: float | None = None,
        M: float | None = None,
        n: int   | None = None,
        sep: Literal["lower", "upper"] = "lower",
    ) -> Self:
        data_m = min(data.data, key=lambda x: x.best)
        data_M = max(data.data, key=lambda x: x.best)
        if m is None:
            m = data_m.best - data_m.delta
        if M is None:
            M = data_M.best + data_M.delta
        if n is None:
            n = math.floor(math.sqrt(len(data)))
        dx = (M - m)/n
        bins: dict[tuple[float, float], list[DataPoint]] = {
            (m+k*dx, m+(k+1)*dx): list() for k in range(n)
        }
        for x in data:
            for (bin_m, bin_M), bin in bins.items():
                if bin_m < x.best < bin_M:
                    bin.append(DataPoint.new(x))
                    continue
                if x.best == (bin_M if sep == "lower" else bin_m):
                    bin.append(DataPoint.new(x))
        return cls(data.data, tuple([
            DistBin(tuple(bin), bin_m, bin_M)
            for (bin_m, bin_M), bin in bins.items()
        ]))


@dataclass(slots=True, frozen=True)
class PickBestPoint(DataSet):
    @property
    def best_point(self, /) -> Measure:
        avg = self.avg
        return min(self.data, key=lambda m: abs(m.best - avg))

    @property
    @cache
    @override
    def best(self) -> float:
        return self.best_point.best

    @property
    @cache
    @override
    def delta(self) -> float:
        return self.best_point.delta


@dataclass(slots=True, frozen=True)
class NormalDistribution(Distribution):
    # @override
    # def histogram(self, /) -> None:
    #     super(NormalDistribution, self).histogram()
    #     m, s = self.avg, self.delta
    #     plotf(
    #         lambda x: exp(-(((x-m)/s)**2)/2)/(math.sqrt(2*math.pi)*s),
    #         min(self.bests), max(self.bests),
    #     )

    @property
    @cache
    @override
    def best(self, /) -> float:
        return self.avg

    @property
    @cache
    @override
    def delta(self, /) -> float:
        return self.std_dev / math.sqrt(len(self.data))


def linear_regression(X: DataSet, Y: DataSet, /) -> tuple[DataPoint, DataPoint]:
    if len(X) != len(Y):
        raise ValueError("X and Y need the same ding.")
    N = len(X.data)
    sx2 = sum([x.best**2 for x in X.data])
    sxy = sum([x.best * y.best for x, y in zip(X.data, Y.data)])
    sx = sum(X.bests)
    sy = sum(Y.bests)
    delta = N*sx2 - sx**2
    a = (sx2*sy - sx*sxy)/delta
    b = (N*sxy - sx*sy)/delta
    da = math.sqrt((Y.delta**2 * sx2)/delta)
    db = Y.delta * math.sqrt(N/delta)
    return DataPoint(a, da), DataPoint(b, db)

def linear_regression_plot(
    X: DataSet, Y: DataSet,
    ab: tuple[DataPoint, DataPoint] | None = None,
    /, *,
    yshift: bool = False,
) -> tuple[DataPoint, DataPoint]:
    a, b = linear_regression(X, Y) if ab is None else ab
    x0, x1 = X[0].best, X[-1].best
    y0 = Y[0].best if yshift else 0
    plt.errorbar(  # type: ignore
        X.bests, Y.map(lambda y: (y - y0)).bests,
        xerr=X.deltas,
        yerr=Y.deltas,
        fmt=".",
    )
    plt.plot(  # type: ignore
        [x0, x1],
        [a.best+b.best*x0 - y0, a.best+b.best*x1 - y0],
    )
    return a, b


# Constants & standard functions
ln = Function(math.log, lambda x: 1/x)
exp = Function(math.exp, math.exp)
sin = Function(math.sin, math.cos)
cos = Function(math.cos, lambda x: -math.sin(x))
tan = Function(math.tan, lambda x: 1 + (math.tan(x))**2)
sinh = Function(math.sinh, math.cosh)
cosh = Function(math.cosh, math.sinh)
