#!/usr/bin/env python3
# pyright: reportConstantRedefinition=false
# ruff: noqa: E743
from itertools import chain, zip_longest
from math import log
import math
from pathlib import Path
import sys
from typing import Iterable, NamedTuple
from rberga06.phylab import Datum, Measure
from rberga06.phylab.constants import π

# esponente in base 10: -0.0466661825 ± 1.0861373135E-4
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
        print(G.ε(Datum(84, 1)*1e9))
        print(G.ε(Datum(43, 1)*1e9))

F1 = Filo(Datum(43.3, .1)/100, Datum(0.81, 0.01)/1000, "Filo di acciaio 1")
F2 = Filo(Datum(43.1, .1)/100, Datum(1.20, 0.01)/1000, "Filo di acciaio 2")
F3 = Filo(Datum(43.0, .1)/100, Datum(1.57, 0.01)/1000, "Filo di acciaio 3")
F4 = Filo(Datum(42.7, .1)/100, Datum(1.97, 0.01)/1000, "Filo di rame")


A = Cilindro(m=Datum(344.07, 0.01) / 1000, d=Datum(90.45, 0.05) / 1000)
B = Cilindro(m=Datum(429.65, 0.01) / 1000, d=Datum(59.85, 0.05) / 1000)
C = Cilindro(m=Datum(473.02, 0.01) / 1000, d=Datum(52.00, 0.05) / 1000)
CAMPIONI = [A, B, C]


# --- CSV utility functions ---

def csv_rows_write(*rows: list[str]) -> str:
    return "\n".join(map(",".join, rows))

def csv_cols_write(*cols: list[str]) -> str:
    return csv_rows_write(*zip_longest(*cols, fillvalue=""))  # type: ignore

def csv_rows_read(csv: str, /) -> list[list[str]]:
    return [l.split(",") for l in csv.split("\n")]

def csv_cols_read(csv: str, /) -> list[list[str]]:
    return [*zip_longest(*csv_rows_read(csv), fillvalue="")]  # type: ignore

# ---

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



def find_picchi(X: Iterable[float], Y: Iterable[float]) -> tuple[list[float], list[float]]:
    X1: list[float] = []
    Y1: list[float] = []
    picco: list[tuple[float, float]] = []
    prev: tuple[float, float] = (0, 0)
    for x, y in zip(X, Y):
        if y > prev[1]:
            picco = [(x, y)]
        elif y == prev[1] and picco:
            picco.append((x, y))
        else:
            if picco:
                X1.append(sum([p[0] for p in picco])/len(picco))
                Y1.append(picco[0][1])
            picco = []
        prev = x, y
    return X1, Y1


def main(argv: list[str], /) -> int | None:
    match argv:
        case ["I"]:
            print(A.I, B.I, C.I, sep="\n")

        case ["compile", *args]:
            match args:
                case []:
                    print(compile_csv(Path(DATA_DIR / "timings-raw.csv").read_text()))
                case [src]:
                    print(compile_csv(Path(src).resolve().read_text()))
                case _:
                    raise
        case ["groupcsv"]:
            SRC = Path(__file__).parent/"data/G17-pendolo-di-torsione.csv"
            DST = Path(__file__).parent/"data/tempi.csv"

            col_src = csv_cols_read(SRC.read_text())
            DST.write_text(csv_cols_write(
                max(col_src, key=lambda c: len([*filter(bool, c)])),
                *[col for i, col in enumerate(col_src) if i % 2]
            ))

        case ["picchi"]:
            import pandas as pd

            SRC = Path(__file__).parent/"data/G17-pendolo-di-torsione.csv"
            DST = Path(__file__).parent/"data/picchi.csv"
            src  = pd.read_csv(SRC)  # type: ignore
            cols: list[pd.Series[float]] = [src[c].abs() for c in src.columns]
            picchi = [find_picchi(cols[2*i], cols[2*i+1]) for i in range(len(cols)//2)]
            DST.write_text(
                csv_rows_write(
                    [*src.columns],
                    *csv_rows_read(csv_cols_write(*[[*map(str, col)] for col in chain.from_iterable(picchi)])),
                )
            )

        case ["picchi-log"]:
            import pandas as pd

            def ylog(X: Iterable[float], Y: Iterable[float]) -> tuple[list[float], list[float]]:
                return [*X], [*map(log, Y)]

            SRC = Path(__file__).parent/"data/G17-pendolo-di-torsione.csv"
            DST = Path(__file__).parent/"data/picchi-log.csv"
            src  = pd.read_csv(SRC)  # type: ignore
            cols: list[pd.Series[float]] = [src[c].abs() for c in src.columns]
            picchi = [ylog(*find_picchi(cols[2*i], cols[2*i+1])) for i in range(len(cols)//2)]
            DST.write_text(
                csv_rows_write(
                    [*src.columns],
                    *csv_rows_read(csv_cols_write(*[[*map(str, col)] for col in chain.from_iterable(picchi)])),
                )
            )

        case ["calc"]:
            FILE = Path(__file__).parent/"data/regressioni.csv"
            for F, line in zip([F1, F2, F3, F4], FILE.read_text().splitlines()[1:]):
                _i, m, dm, _q, _dq, *_ = [*map(float, filter(bool, line.split(",")))]
                F.calc(Datum(m, dm))
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
        case ["calc1"]:
            l = (Datum(46.67, 0.11) * math.log(10))/1000
            T = Datum(409.96, 0.04)/1000
            T0 = (1 / (1/T**2 + (l/(2*π))**2))**.5
            print(T)
            print(T0)
        case ["calc-I"]:
            I0m = Cilindro(
                m = Datum(134.92, 0.01) / 1000,  # kg
                d = Datum( 98.45, 0.05) / 1000,  # m
            ).I
            print(I0m)
            for I0c in [
                Datum(1.620, 0.006)/1e4,
                Datum(1.581, 0.006)/1e4,
                Datum(1.582, 0.006)/1e4,
                Datum(1.587, 0.006)/1e4,
            ]:
                print(I0m.ε(I0c))
        case _:
            raise


if __name__ == "__main__":
    main(sys.argv[1:])
