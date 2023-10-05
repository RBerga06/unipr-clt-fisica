#!/usr/bin/env python3
"""Core data."""
from dataclasses import dataclass
from functools import cache
from typing import Callable, Protocol, Self, cast, final, overload
from typing_extensions import override
import math


class Measure(Protocol):
    best: float
    delta: float

    @property
    def delta_rel(self, /) -> float:
        return self.delta / self.best

    def __add__(self, other: "Measure | float", /) -> "Measure":
        if isinstance(other, float | int):
            return DataPoint(self.best + other, self.delta)
        return DataPoint(self.best + other.best, self.delta + other.delta)

    def __radd__(self, other: "Measure | float", /) -> "Measure":
        return self.__add__(other)

    def __sub__(self, other: "Measure | float", /) -> "Measure":
        if isinstance(other, float | int):
            return DataPoint(self.best + other, self.delta)
        return DataPoint(self.best + other.best, self.delta + other.delta)

    def __rsub__(self, other: "Measure | float", /) -> "Measure":
        return self.__sub__(other)

    def __mul__(self, other: "Measure | float", /) -> "Measure":
        if isinstance(other, float | int):
            other = DataPoint.from_const(other)
        return DataPoint.from_delta_rel(self.best * other.best, self.delta_rel + other.delta_rel)

    def __rmul__(self, other: "Measure | float", /) -> "Measure":
        return self.__mul__(other)

    def __truediv__(self, other: "Measure | float", /) -> "Measure":
        if isinstance(other, float | int):
            other = DataPoint.from_const(other)
        return DataPoint.from_delta_rel(self.best / other.best, self.delta_rel + other.delta_rel)

    def __pow__(self, other: int, /) -> "Measure":
        return DataPoint.from_delta_rel(self.best ** other, self.delta_rel * other)


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


@final
@dataclass(slots=True, frozen=True)
class DataPoint(Measure):
    best: float
    delta: float

    @classmethod
    def from_const(cls, const: float, /) -> Self:
        return cls(const, 0)

    @classmethod
    def from_delta_rel(cls, best: float, delta_rel: float, /) -> Self:
        return cls(best, delta_rel * best)


@overload
def data_points(raw: list[tuple[float, float]], delta: None = None, /) -> tuple[DataPoint, ...]: ...
@overload
def data_points(raw: list[float], delta: list[float] | float, /) -> tuple[DataPoint, ...]: ...
def data_points(
    raw: list[tuple[float, float]] | list[float],
    delta: list[float] | float | None = None,
    /,
) -> tuple[DataPoint, ...]:
    match delta:
        case None:
            data = cast(list[tuple[float, float]], raw)
        case float() | int():
            data = zip(cast(list[float], raw), [delta]*len(raw))
        case _:
            data = zip(cast(list[float], raw), delta)
    return tuple([DataPoint(x, d) for x, d in data])


@dataclass(slots=True, frozen=True)
class DataSet(Measure):
    data: tuple["Measure", ...]

    @property
    @cache
    def len(self, /) -> int:
        return len(self.data)

    @property
    @cache
    def average(self, /) -> float:
        return sum([m.best for m in self.data])/len(self.data)

    @property
    @cache
    def variance(self, /) -> float:
        return (sum([x.best**2 for x in self.data]) - len(self.data) * self.average**2)/(len(self.data) - 1)

    @property
    @cache
    def std_dev(self, /) -> float:
        return math.sqrt(self.variance)

    @property
    @cache
    @override
    def best(self, /) -> float:  # type: ignore
        return self.average

    @property
    @cache
    def delta_data_max(self, /) -> float:
        return max([m.delta for m in self.data])

    @property
    @cache
    def semidispersion(self, /) -> float:
        xs = [m.best for m in self.data]
        return (max(xs) - min(xs))/2

    @property
    @cache
    @override
    def delta(self, /) -> float:  # type: ignore
        return max(self.semidispersion, self.delta_data_max)


@dataclass(slots=True, frozen=True)
class Distribution(DataSet):
    bins_min: float = 0.
    bins_max: float = 1.
    bin_sep_down: bool = True  # if x == sep, x in the lower bin
    nbins_manual: int | None = None

    @property
    def nbins(self, /) -> int:
        """Actual number of bins."""
        if self.nbins_manual is None:
            return math.floor(math.sqrt(len(self.data)))
        return self.nbins_manual

    @property
    def bins(self, /) -> tuple[DataSet, ...]:
        m = self.bins_min
        dx = (self.bins_max - m)/self.nbins
        bins = {
            (m+n*dx, m+(n+1)*dx): list[Measure]()
            for n in range(self.nbins)
        }
        for x in self.data:
            for (bin_m, bin_M), bin in bins.items():
                if self.bin_sep_down:
                    if bin_m < x.best <= bin_M:
                        bin.append(x)
                else:
                    if bin_m <= x.best < bin_M:
                        bin.append(x)
        return tuple([DataSet(tuple(bin)) for bin in bins.values()])

    @property
    @cache
    @override
    def average(self, /) -> float:
        return sum(len(bin.data) * bin.average for bin in self.bins)/len(self.data)

    def histogram(self, /, *, bins: int | None = None) -> None:
        if bins is None:
            bins = math.floor(math.sqrt(len(self.data)))
        from matplotlib import pyplot as plt
        plt.hist([x.best for x in self.data], bins=bins)  # type: ignore


@dataclass(slots=True, frozen=True)
class PickBestPoint(DataSet):
    @property
    def best_point(self, /) -> Measure:
        avg = self.average
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
    @property
    @cache
    @override
    def best(self, /) -> float:
        return self.average

    @property
    @cache
    @override
    def delta(self, /) -> float:
        return self.std_dev / math.sqrt(len(self.data))


def linear_regression(X: DataSet, Y: DataSet) -> tuple[DataPoint, DataPoint]:
    N = len(X.data)
    sx2 = sum([x.best**2 for x in X.data])
    sxy = sum([x.best * y.best for x, y in zip(X.data, Y.data)])
    sx = sum([x.best for x in X.data])
    sy = sum([y.best for y in Y.data])
    delta = N*sx2 - sx**2
    a = (sx2*sy - sx*sxy)/delta
    b = (N*sxy - sx*sy)/delta
    da = math.sqrt(Y.delta**2 * sx2/delta)
    db = math.sqrt(Y.delta**2 * N/delta)
    return DataPoint(a, da), DataPoint(b, db)


# Constants & standard functions
g = DataPoint(9.806, 0.001)
π = math.pi
ln = Function(math.log, lambda x: 1/x)
exp = Function(math.exp, math.exp)
sin = Function(math.sin, math.cos)
cos = Function(math.cos, lambda x: -math.sin(x))
tan = Function(math.tan, lambda x: 1 + (math.tan(x))**2)
sinh = Function(math.sinh, math.cosh)
cosh = Function(math.cosh, math.sinh)
