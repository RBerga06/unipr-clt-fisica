#!/usr/bin/env python3
# pyright: reportConstantRedefinition=false
"""Core data."""
from dataclasses import dataclass
from functools import cache
import math
from typing import Callable, Iterator, Literal, Protocol, Self, cast, final, overload
from typing_extensions import override
from matplotlib import pyplot as plt


def round2sig(x: float, sig: int) -> float:
    """Round the given number to the given significant figure."""
    if x == 0:
        return x
    return round(x, sig - 1 - int(math.floor(math.log10(abs(x)))))


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
            return DataPoint(self.best * other, self.delta * abs(other))
        return DataPoint.from_delta_rel(self.best * other.best, self.delta_rel + other.delta_rel)

    def __rmul__(self, other: "Measure | float", /) -> "Measure":
        return self.__mul__(other)

    def __truediv__(self, other: "Measure | float", /) -> "Measure":
        if isinstance(other, float | int):
            return DataPoint(self.best / other, self.delta / abs(other))
        return DataPoint.from_delta_rel(self.best / other.best, self.delta_rel + other.delta_rel)

    def __rtruediv__(self, other: "Measure | float", /) -> "Measure":
        if isinstance(other, float | int):
            other = DataPoint.from_const(other)
        return other.__truediv__(self)

    def __pow__(self, other: int, /) -> "Measure":
        return DataPoint.from_delta_rel(self.best ** other, self.delta_rel * other)

    # def __repr__(self, /) -> str:
    #     best, delta = self.best, self.delta
    #     delta_factor = 10 ** math.floor(math.log10(delta))
    #     delta_digits = delta / delta_factor
    #     new_delta = delta_factor * (round(delta_digits, 1) if delta_digits < 2 else round(delta_digits))
    #     return f"{best} ± {new_delta}"


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
    def from_measure(cls, x: Measure, /) -> Self:
        if isinstance(x, cls):
            return x
        return cls(x.best, x.delta)

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
    data: tuple[Measure, ...]

    @property
    @cache
    def len(self, /) -> int:
        return len(self.data)

    @property
    @cache
    def bests(self, /) -> tuple[float, ...]:
        return tuple([x.best for x in self.data])

    @property
    @cache
    def deltas(self, /) -> tuple[float, ...]:
        return tuple([x.delta for x in self.data])

    @property
    @cache
    def average(self, /) -> float:
        """The (weighted) average of all data."""
        # $w_i = \frac{1}{(\delta x_i)^2}$
        return sum([m.best * m.delta**-2 for m in self.data])/sum([m.delta**-2 for m in self.data])

    @property
    @cache
    def variance(self, /) -> float:
        return (sum([x.best**2 for x in self.data]) - self.len * self.average**2)/(self.len - 1)

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
        return max(self.deltas)

    @property
    @cache
    def semidispersion(self, /) -> float:
        xs = self.bests
        return (max(xs) - min(xs))/2

    @property
    @cache
    @override
    def delta(self, /) -> float:  # type: ignore
        return max(self.semidispersion, self.delta_data_max)

    def __iter__(self, /) -> Iterator[Measure]:
        return iter(self.data)

    def __len__(self, /) -> int:
        return self.len


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
        return sum([bin.len for bin in self.bins])

    @property
    @cache
    @override
    def average(self, /) -> float:
        return sum(len(bin.data) * bin.best for bin in self.bins)/len(self.bins)

    def histogram(self, /) -> None:
        for bin in self.bins:
            print(f"  - {[x.best for x in bin.data]}")
        plt.bar(  # type: ignore
            [bin.best for bin in self.bins],
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
        if m is None:  m = data_m.best - data_m.delta
        if M is None:  M = data_M.best + data_M.delta
        if n is None:  n = math.floor(math.sqrt(data.len))
        dx = (M - m)/n
        bins: dict[tuple[float, float], list[DataPoint]] = {
            (m+k*dx, m+(k+1)*dx): list() for k in range(n)
        }
        for x in data:
            for (bin_m, bin_M), bin in bins.items():
                if bin_m < x.best < bin_M:
                    bin.append(DataPoint.from_measure(x))
                    continue
                if x.best == (bin_M if sep == "lower" else bin_m):
                    bin.append(DataPoint.from_measure(x))
        return cls(data.data, tuple([
            DistBin(tuple(bin), bin_m, bin_M)
            for (bin_m, bin_M), bin in bins.items()
        ]))


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
    da = math.sqrt((Y.delta**2 * sx2)/delta)
    db = Y.delta * math.sqrt(N/delta)
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
