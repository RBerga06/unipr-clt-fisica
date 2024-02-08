#!/usr/bin/env python3
# ruff: noqa: E743
from itertools import chain
from pathlib import Path
import sys
from typing import NamedTuple
from rberga06.phylab import Datum, Measure
from rberga06.phylab.constants import π

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


class Filo(NamedTuple):
    l: Measure[float]
    """Lunghezza"""
    d: Measure[float]
    """Diametro"""
    name: str = ""
    """Nome del filo"""

    @property
    def r(self, /):
        return self.d / 2

    def calc(self, m: Measure[float]):
        print(f"{self.name}:")
        C = m * 4 * (π**2)  # costante torsionale
        print(f"- C = {C * 1000} mJ")
        G = C * self.l * 2 / (π * self.r**4)  # modulo di scorrimento
        print(f"- G = {G * 1e-9} GPa")

F1 = Filo(Datum(43.3, .1)/100, Datum(0.81, 0.01)/1000, "Filo di acciaio 1")
F2 = Filo(Datum(43.1, .1)/100, Datum(1.20, 0.01)/1000, "Filo di acciaio 2")
F3 = Filo(Datum(43.0, .1)/100, Datum(1.57, 0.01)/1000, "Filo di acciaio 3")
F4 = Filo(Datum(42.7, .1)/100, Datum(1.97, 0.01)/1000, "Filo di rame")


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
        # m = sum([x.m for x in objs], start=Datum(0.0, 0.0))
        i = sum([x.I for x in objs], start=Datum(0.0, 0.0))
        compiled.append(
            [
                # m.best,
                # m.delta,
                i.best,
                i.delta,
                *chain.from_iterable(
                    [(d.best, d.delta) for d in [(Datum(float(T), 0.001) / f)**2 for T, f in zip(periods, factors)]]
                ),
            ]
        )
    return "\n".join(['I,,T1^2,,T2^2,,T3^2,,T4^2,'] + [",".join(map(str, line)) for line in compiled] + [""])


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
        case ["calc"]:
            FILE = Path(__file__).parent/"data/regressioni.csv"
            for F, line in zip([F1, F2, F3, F4], FILE.read_text().splitlines()[1:]):
                _i, m, dm, _q, _dq, *_ = [*map(float, filter(bool, line.split(",")))]
                F.calc(Datum(m, dm))
                print()
            # # FORMULE:
            # # I = C/(4π^2) T^2
            # # C = ( π R^4 G )/( 2L )
            # # q = Datum(-1.9220914099e-4, 5.5612196683e-6)
            # C = m * 4 * (π**2)  # costante torsionale
            # L = Datum(43.3, .1)/100
            # R = Datum(.81, .01)/2000
            # G = C * L * 2 / (π * R**4)
            # print(C * 1000, "mJ")
            # print(G * 1e-9, "GPa")
            #
            # F1.calc(Datum(1.9587349547e-4, 5.3156106851e-6))
            # F1.calc(Datum(2.1835799471e-4, 2.4403249662e-6))
            # print()
            # F2.calc(Datum(2.1835799471e-4, 2.4403249662e-6))
            # print()
            # F3.calc(Datum(2.1835799471e-4, 2.4403249662e-6))
            # print()
            # F4.calc(Datum(2.1835799471e-4, 2.4403249662e-6))
            # print()
        case _:
            raise


if __name__ == "__main__":
    main(sys.argv[1:])
