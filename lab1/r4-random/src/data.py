#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
import sys
from pathlib import Path
from rberga06.phylab.constants import ln2, Th232
from rberga06.phylab import Datum, Measure, MeasureLike, DistributionFit, DataSet, Poisson
type PoissonFit = DistributionFit[Poisson, DataSet[int]]

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
        self.fit = Poisson.fit(DataSet(data[:MAX_DATA_N]))
        if self.title == "<auto>":
            self.title = self.path.name

def poisson(file: Path, /) -> PoissonFit:
    return PoissonFile(file).fit

def merge(file1: Path, file2: Path, output: Path, sep: str = "\n") -> None:
    output.write_text(file1.read_text() + sep + file2.read_text())

def massThEstimate(x: MeasureLike[float], R: MeasureLike[float], /) -> Measure[float]:
    Aa = (4*R**2)/r**2
    N = (Th232.T12 * Aa)/ln2 * x
    return Th232.mass * N

def massTh[M: MeasureLike[float]](b: M, /) -> M:
    # x = Nr²ln2/4T₁₂ · R⁻²
    # b = Nr²ln2/4T₁₂
    # N = b·4T₁₂/r²ln2
    N = b * (Th232.T12*4)/(ln2*r**2)
    m = Th232.mass * N
    return m  # type: ignore


# --- Actual data analysis ---
DATA = Path(__file__).parent.parent/"data"
MAX_DATA_N: int = 3657
r = Datum(7.00, 0.05)/1000  # m

match sys.argv[1:]:
    case ["bernoulli", *argv]:
        match argv:
            case ["merge-files", *_]:
                merge(DATA/"dadi1.txt", DATA/"dadi2.txt", DATA/"dadi.txt", sep="# --- NEW DATA --- #\n")
            case _:
                pass
    case ["poisson", *argv] | argv:
        match argv:
            case ["files", *nums]:
                for n in nums:
                    file = PoissonFile(DATA/f"p{n}.txt")
                    print(f"--- {file.title} ---")
                    print(f"R  = {file.distance}")
                    print(f"N  = {file.fit.dist.n}")
                    print(f"µ  = {file.fit.dist.average}")
                    print(f"σ  = {file.fit.dist.sigma}")
                    print(f"σx = {file.fit.dist.sigma_avg}")
                    if file.distance is not None:
                        print(f"m  = {massThEstimate(file.fit.dist, file.distance)}")
                print("------------------")
            case ["mass"] | _:
                print("m =", massTh(Datum(.00571, 1.3e-4))*1_000, "g")
