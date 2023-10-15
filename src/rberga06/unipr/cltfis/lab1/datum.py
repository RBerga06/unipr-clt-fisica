#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measures and basic Data."""
from dataclasses import dataclass
from typing import Protocol, Self, final


class Measure(Protocol):
    best: float
    delta: float

    @property
    def delta_rel(self, /) -> float:
        return self.delta / self.best

    def __add__(self, other: "Measure | float", /) -> "Measure":
        if isinstance(other, float | int):
            return Datum(self.best + other, self.delta)
        return Datum(self.best + other.best, self.delta + other.delta)

    def __radd__(self, other: "Measure | float", /) -> "Measure":
        return self.__add__(other)

    def __sub__(self, other: "Measure | float", /) -> "Measure":
        if isinstance(other, float | int):
            return Datum(self.best - other, self.delta)
        return Datum(self.best - other.best, self.delta + other.delta)

    def __rsub__(self, other: "Measure | float", /) -> "Measure":
        return self.__sub__(other)

    def __mul__(self, other: "Measure | float", /) -> "Measure":
        if isinstance(other, float | int):
            return Datum(self.best * other, self.delta * abs(other))
        return Datum.from_delta_rel(self.best * other.best, self.delta_rel + other.delta_rel)

    def __rmul__(self, other: "Measure | float", /) -> "Measure":
        return self.__mul__(other)

    def __truediv__(self, other: "Measure | float", /) -> "Measure":
        if isinstance(other, float | int):
            return Datum(self.best / other, self.delta / abs(other))
        return Datum.from_delta_rel(self.best / other.best, self.delta_rel + other.delta_rel)

    def __rtruediv__(self, other: "Measure | float", /) -> "Measure":
        if isinstance(other, float | int):
            other = Datum.from_const(other)
        return other.__truediv__(self)

    def __pow__(self, other: int, /) -> "Measure":
        return Datum.from_delta_rel(self.best ** other, self.delta_rel * other)


@final
@dataclass(slots=True, frozen=True)
class Datum(Measure):
    """A minimal `Measure` implementaion."""
    best: float
    delta: float

    @classmethod
    def new(cls, x: Measure | tuple[float, float] | float, /, *, delta: float = 0) -> Self:
        if isinstance(x, cls):
            return x
        if isinstance(x, tuple):
            return cls(*x)
        if isinstance(x, float | int):
            return cls(x, delta)
        return cls(x.best, x.delta)

    @classmethod
    def from_const(cls, const: float, /) -> Self:
        return cls(const, 0)

    @classmethod
    def from_delta_rel(cls, best: float, delta_rel: float, /) -> Self:
        return cls(best, delta_rel * best)


__all__ = ["Measure", "Datum"]
