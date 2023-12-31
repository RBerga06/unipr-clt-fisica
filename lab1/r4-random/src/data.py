#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
from itertools import chain, zip_longest
import sys
from pathlib import Path
from typing import Any, Iterable
from rberga06.phylab.constants import ln2, Th232
from rberga06.phylab import Datum, Measure, MeasureLike, DistributionFit, DataSet, BinSet, Poisson, Bernoulli
type Bins = BinSet[int, DataSet[int]]
type PoissonFit   = DistributionFit[Poisson,   Bins]
type BernoulliFit = DistributionFit[Bernoulli, Bins]


@dataclass(slots=True)
class DiceFile:
    path: Path
    column: int
    results: list[int] = field(default_factory=list, init=False)

    def __post_init__(self, /) -> None:
        for line in map(str.strip, self.path.read_text().splitlines()):
            if line.startswith("#") or (not line):
                pass
            else:
                self.results.append(int(line.split("\t")[self.column]))


@dataclass(slots=True)
class BernoulliFile:
    path: Path
    success: int = 1
    columns: tuple[int, ...] = tuple(range(6))
    fit: BernoulliFit = field(init=False)

    def __post_init__(self, /) -> None:
        data: list[int] = []
        for line in map(str.strip, self.path.read_text().splitlines()):
            if line.startswith("#") or (not line):
                pass
            else:
                rolls = [*map(int, line.split("\t"))]
                data.append([rolls[i] for i in self.columns].count(self.success))
        self.fit = Bernoulli.fit(
            DataSet(data).intbins(),
            n_trials=len(self.columns), p_success=1/6,
        )


@dataclass(slots=True)
class PoissonFile:
    path: Path
    title: str = "<auto>"
    distance: MeasureLike[float] | None = None
    fit: PoissonFit = field(init=False)

    def __post_init__(self, /) -> None:
        data: list[int] = []
        for line in map(str.strip, self.path.read_text().splitlines()):
            if line.startswith("# title:") and (self.title == "<auto>"):
                self.title = line.removeprefix("# title:").strip()
            elif line.startswith("# distance:") and (self.distance is None):
                line = line.removeprefix("# distance:").removesuffix("m").strip()
                if "±" in line:
                    self.distance = Datum(*map(eval, line.split("±")))
                else:
                    self.distance = eval(line)
            elif line.startswith("#") or (not line):
                pass
            else:
                data.append(int(line))
        self.fit = Poisson.fit(DataSet(data[:MAX_DATA_N]).intbins())
        if self.title == "<auto>":
            self.title = self.path.name


def _csv(*data: Iterable[Any]) -> str:
    return "\n".join([",".join([*map(str, line)]) for line in zip_longest(*data, fillvalue="")])


def csv(*files: tuple[str, BernoulliFile | PoissonFile | DiceFile]) -> str:
    return _csv(*chain.from_iterable([
        (
            [title, *file.results],
        ) if isinstance(file, DiceFile) else ((
            [title, *map(len, file.fit.data.bins)],
            ['', *file.fit.dist.bins(
                len(file.fit.data.bins),
                file.fit.data.bins[ 0].left,
                file.fit.data.bins[-1].right,
            )],
        ) if isinstance(file, PoissonFile) else (
            [title, *map(len, file.fit.data.bins)],
            ['', *file.fit.dist.bins(
                len(file.columns) + 1,
                -.5,
                len(file.columns) + .5,
            )],
        ))
        for title, file in files
    ]))


def poisson(file: Path, /) -> PoissonFit:
    return PoissonFile(file).fit

def merge(file1: Path, file2: Path, output: Path, sep: str = "\n") -> None:
    output.write_text(file1.read_text() + sep + file2.read_text())

def massThEstimate(x: MeasureLike[float], R: MeasureLike[float], /) -> Measure[float]:
    # Aa = (4*R**2)/r_geiger**2
    # N = (Th232.T12 * Aa)/ln2 * x
    xi = x*R**2
    N = (4 * Th232.T12 * xi)/(ln2 * r_geiger**2)
    m = Th232.mass * N
    return m

def massTh[M: MeasureLike[float]](xi: M, /) -> M:
    # ξ = (Nr²ln2)/(4T₁₂)
    # 4T₁₂ξ = Nr²ln2
    # (4T₁₂ξ)/(r²ln2) = N
    N = (4 * Th232.T12 * xi)/(ln2 * r_geiger**2)
    print("N =", N)
    m = Th232.mass * N
    return m  # type: ignore


# --- Actual data analysis ---
DATA = Path(__file__).parent.parent/"data"
MAX_DATA_N: int = 3657
d_geiger = Datum(14.00, 0.05)/1000  # m
r_geiger = d_geiger/2

match sys.argv[1:]:
    case ["bernoulli", *argv]:
        match argv:
            case ["merge-files", *_]:
                merge(DATA/"dadi1.txt", DATA/"dadi2.txt", DATA/"dadi.txt", sep="# --- NEW DATA --- #\n")
            case _:
                pass
    case ["poisson", *argv]:
        match argv:
            case ["files", *nums]:
                for n in (nums or range(6)):
                    file = PoissonFile(DATA/f"p{n}.txt")
                    print(f"--- {file.title} ---")
                    print(f"R  = {file.distance} m")
                    # print(f"N  = {file.fit.dist.n}")
                    print(f"µ  = {file.fit.dist.average}")
                    print(f"σ  = {file.fit.dist.sigma}")
                    print(f"σx = {file.fit.dist.sigma_avg}")
                    if file.distance is not None:
                        print(f"m  = {massThEstimate(file.fit.dist, file.distance)*1_000} g")
                print("------------------")
            case ["mass"]:
                print("ε =", Datum(0.19442166, 0.00729138).ε(Datum(0.188200746, 0.0064266811)))
                print("m =", massTh(Datum(.005704, 1.3e-4))*1_000, "g")
            case _:
                pass
    case ["dump"]:
        d = ("Rosso", "Verde", "Blu", "Viola", "Nero", "Bianco")
        print(csv(
            *[(f"Geiger {n}", PoissonFile(DATA/f"p{n}.txt")) for n in range(-1, 6)],
            *[(f"Dadi {i}", BernoulliFile(DATA/"dadi.txt", success=i)) for i in range(1, 7)],
            *[(d[i], DiceFile(DATA/"dadi.txt", i)) for i in range(6)],
        ))
    case _:
        pass
