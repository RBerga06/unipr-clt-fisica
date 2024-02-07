#!/usr/bin/env python3
# ruff: noqa: E743
from itertools import chain
from pathlib import Path
import sys
from typing import NamedTuple
from rberga06.phylab import Datum, Measure

DATA_DIR = Path(__file__).parent / "data"


class Cilindro(NamedTuple):
    m: Measure[float]
    """Massa"""
    d: Measure[float]
    """Diametro"""

    @property
    def r(self, /):
        """Raggio"""
        return self.d / 2

    @property
    def I(self, /):
        """Momento d'inerzia"""
        return self.m * self.r**2 / 2


A = Cilindro(m=Datum(344.07, 0.01) / 1000, d=Datum(9.45, 0.05) / 100)
B = Cilindro(m=Datum(429.65, 0.01) / 1000, d=Datum(5.85, 0.05) / 100)
C = Cilindro(m=Datum(473.02, 0.01) / 1000, d=Datum(5.20, 0.05) / 100)
CAMPIONI = [A, B, C]


def compile_csv(csv: str, /) -> str:
    lines = csv.splitlines()
    factors = [int(s.split("T")[0] or "1") for s in lines[0].split(",")[1:]]
    compiled: list[list[float]] = []
    for line in lines[1:]:
        sobjs, *periods = line.split(",")
        objs = [CAMPIONI[i] for i in range(3) if int(sobjs[i])]
        m = sum([x.m for x in objs], start=Datum(0.0, 0.0))
        i = sum([x.I for x in objs], start=Datum(0.0, 0.0))
        compiled.append(
            [
                m.best,
                m.delta,
                i.best,
                i.delta,
                *chain.from_iterable(
                    [(d.best, d.delta) for d in [Datum(float(T), 0.001) / f for T, f in zip(periods, factors)]]
                ),
            ]
        )
    return "\n".join(["m,,I,,T1,,T2,,T3,,T4,"] + [",".join(map(str, line)) for line in compiled] + [""])


def main(argv: list[str], /) -> int | None:
    match argv:
        case ["compile", *args]:
            match args:
                case []:
                    print(compile_csv(Path(DATA_DIR / "timings-raw.csv").read_text()))
                case [src]:
                    print(compile_csv(Path(src).resolve().read_text()))
                case _:
                    raise
        case _:
            raise


if __name__ == "__main__":
    main(sys.argv[1:])
