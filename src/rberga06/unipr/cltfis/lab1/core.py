#!/usr/bin/env python3
"""Core data."""
from dataclasses import dataclass
from typing import Callable, Protocol, Self, overload
from typing_extensions import override


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


@dataclass(slots=True, frozen=True)
class Function:
    f: Callable[[float], float]
    f1: Callable[[float], float]

    @overload
    def __call__(self, argument: float, /) -> float: ...
    @overload
    def __call__(self, argument: "Measure", /) -> "Measure": ...
    def __call__(self, x: "float | Measure", /) -> "float | Measure":
        if isinstance(x, float):
            return self.f(x)
        return DataPoint(self.f(x.best), abs(self.f1(x.best)) * x.delta)


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


@dataclass(slots=True)
class DataSet(Measure):
    data: list["Measure"]

    @property
    def average(self, /) -> float:
        return sum([m.best for m in self.data])/len(self.data)

    @property
    @override
    def best(self, /) -> float:  # type: ignore
        return self.average

    @property
    def delta_data_max(self, /) -> float:
        return max([m.delta for m in self.data])

    @property
    def semidispersion(self, /) -> float:
        xs = [m.best for m in self.data]
        return (max(xs) - min(xs))/2

    @property
    @override
    def delta(self, /) -> float:  # type: ignore
        return max(self.semidispersion, self.delta_data_max)

    @classmethod
    def from_raw(cls, data: list[tuple[float, float]], /) -> Self:
        return cls([DataPoint(best, delta) for best, delta in data])


@dataclass(slots=True)
class PickBestPointDataSet(DataSet):
    @property
    def best_point(self, /) -> Measure:
        avg = self.average
        return min(self.data, key=lambda m: m.best - avg)

    @property
    @override
    def best(self) -> float:
        return self.best_point.best

    @property
    @override
    def delta(self) -> float:
        return self.best_point.delta
