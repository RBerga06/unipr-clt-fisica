from math import log as ln
from pathlib import Path
from typing import Iterator
from rberga06.phylab import DataSet, Poisson, MeasureLike
from rberga06.phylab.distribution import DistFit
DIR = Path(__file__).parent

MAX_DATA_N: int = 3657
NA = int(6.022e23)
T12 = 14.5e9 * 365 * 24 * 60 * 60
Mn = 1.68e-27
r = 0.007

def read(file: Path) -> Iterator[int]:
    return (
        int(s) for s in map(str.strip, file.read_text().splitlines())
        if s and not s.startswith("#")
    )

def poisson(file: Path, /) -> DistFit[Poisson, DataSet[int]]:
    return Poisson.fit(DataSet([*read(file)][:MAX_DATA_N]))

def merge(file1: Path, file2: Path, output: Path, sep: str = "\n") -> None:
    output.write_text(file1.read_text() + sep + file2.read_text())

def massTh1file(file: Path, R: float, /) -> float:
    x = poisson(file).dist.average
    Aa = (4*R**2)/r**2
    N = (T12 * Aa)/ln(2) * x
    print(f"{N=} {Aa=}")
    return N * 232 * Mn

def massTh[M: MeasureLike[float]](b: M, /) -> M:
    # x = Nr²ln2/4T₁₂ · R⁻²
    # b = Nr²ln2/4T₁₂
    # N = b·4T₁₂/r²ln2
    N = b * (T12*4)/(ln(2)*r**2)
    m = N * 232 * Mn
    return m  # type: ignore

# merge(DIR/"dadi1.txt", DIR/"dadi2.txt", DIR/"dadi.txt", sep="# --- NEW DATA --- #\n")
# print(T12)
# print(massTh1file(DIR/"G171.txt", 0.103))

DATA = Path(__file__).parent.parent/"data"

for n in range(6):
    data = DataSet([*read(DATA/f"p{n}.txt")][:3657])
    fit = Poisson.fit(data)
    print(f"--- File {n} ---")
    print(f"N  = {fit.dist.n}")
    print(f"µ  = {fit.dist.average}")
    print(f"σ  = {fit.dist.sigma}")
    print(f"σx = {fit.dist.sigma_avg}")
print("---------------")

print("m =", massTh(.00571), "g")
