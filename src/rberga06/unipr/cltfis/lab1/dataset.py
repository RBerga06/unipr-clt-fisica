#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lists of Measures and Data set."""
from functools import cache
from dataclasses import dataclass
import math
from typing import Callable, Iterable, Iterator, Protocol, Self, Sequence, overload
from typing_extensions import override
from .datum import Datum, Measure


class DataSetProto(Protocol):
    data: Sequence[Measure]
    _: Measure

    @overload
    def __getitem__(self, i: int, /) -> Measure: ...
    @overload
    def __getitem__(self, i: slice, /) -> tuple[Measure, ...]: ...
    def __getitem__(self, i: int | slice, /) -> Measure | Sequence[Measure]:
        return self.data[i]

    def __iter__(self, /) -> Iterator[Measure]:
        return iter(self.data)

    def __len__(self, /) -> int:
        return len(self.data)


@dataclass(slots=True, frozen=True)
class DataSet(DataSetProto):
    data: tuple[Measure, ...]  # type: ignore[reportIncompatibleVariableOverride]
    label: str = ""

    @property
    @cache
    @override
    def _(self, /) -> Measure:
        return self.avg

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
    def weights(self, /) -> tuple[float, ...]:
        # $w_i = \frac{1}{(\delta x_i)^2}$
        return tuple([d**-2 for d in self.deltas])

    @property
    @cache
    @override
    def avg(self, /) -> Measure:
        """The (weighted) average of all data."""
        return Datum(
            sum(w * x for x, w in zip(self.bests, self.weights))/sum(self.weights),
            1/math.sqrt(sum(self.weights)),
        )

    def chlabel(self, label: str, /) -> Self:
        return type(self)(
            self.data,
            label=label,
        )

    def chdata(self, data: tuple[Measure, ...], /) -> Self:
        """To be overridden by subclasses that implement configuration parameters."""
        return type(self)(
            data,
            label=self.label
        )

    def map(self, f: Callable[[Measure], Measure], /) -> Self:
        """Apply the given operation to all measures."""
        return self.chdata(tuple([f(x) for x in self.data]))

    @classmethod
    def new(
        cls,
        data: Iterable[Measure] | Iterable[tuple[float, float]] | Iterable[float],
        /, *,
        delta: float = 0,
    ) -> Self:
        return cls(tuple(Datum.new(best, delta=delta) for best in data))


__all__ = [
    "DataSetProto",
    "DataSet",
]
