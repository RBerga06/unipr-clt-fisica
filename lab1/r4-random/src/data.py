from math import log as ln
from pathlib import Path
DIR = Path(__file__).parent

NA = int(6.022e23)
T12 = 14.5e9 * 365 * 24 * 60 * 60
Mn = 1.68e-27
r = 0.007

def merge(file1: Path, file2: Path, output: Path, sep: str = "\n") -> None:
    output.write_text(file1.read_text() + sep + file2.read_text())

def geiger(file: Path, R: float, /) -> float:
    bins: list[int] = []
    for line in file.read_text().splitlines():
        if (not line) or line.startswith("#"):
            continue
        x = int(line.strip())
        while len(bins) <= x:
            bins.append(0)
        bins[x] += 1
    avg = sum(i*b for i, b in enumerate(bins))/sum(bins)
    Aa = (4*R**2)/r**2
    N = (T12 * Aa)/ln(2) * avg
    print(f"{N=} {Aa=}")
    return N * 232 * Mn

print(T12)
print(geiger(DIR/"G171.txt", 0.103))
print(geiger(DIR/"G171.txt", 0.103))
# merge(DIR/"dadi1.txt", DIR/"dadi2.txt", DIR/"dadi.txt", sep="# --- NEW DATA --- #\n")
