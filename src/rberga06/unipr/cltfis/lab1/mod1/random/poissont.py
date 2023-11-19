#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass
from functools import cache
from math import exp, factorial
from pathlib import Path
from typing import Iterator, final


@final
@dataclass(slots=True, frozen=True)
class Poissont:
    bins: tuple[int, ...] = ()

    @property
    @cache
    def tot(self, /) -> int:
        return sum(self.bins)

    @property
    @cache
    def avg(self, /) -> float:
        if not self.bins:
            return 0
        return sum([])/self.tot

    def p(self, x: int, /) -> float:
        return exp(-self.avg)*pow(self.avg, x)/factorial(x)

    def expected(self, x: int, /) -> float:
        return self.p(x) * self.tot

    @classmethod
    def load(cls, file: Path, /) -> "Poissont":
        return [*cls.open(file)][-1]

    @classmethod
    def open(cls, file: Path, /) -> Iterator["Poissont"]:
        self = cls()
        yield self
        for line in map(str.strip, file.read_text().splitlines()):
            if (not line) or line.startswith("#"):
                continue  # skip comments and blank lines
            yield self.add(int(line))

    def add(self, point: int, /) -> "Poissont":
        bins = [*self.bins]
        while point >= len(bins):
            bins.append(0)
        bins[point] += 1
        return Poissont(tuple(bins))

    def __add__(self, point: int, /) -> "Poissont":
        return self.add(point)

    def __iter__(self, /) -> Iterator[int]:
        return iter(self.bins)


__all__ = ["Poissont"]
