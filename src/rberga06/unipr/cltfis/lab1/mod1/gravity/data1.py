from math import erf
from ...datum import Datum

t1 = Datum(503629.15, 225.71/10)/1_000_000
t2 = Datum(503929.60, 246.21/10)/1_000_000

ø1 = Datum(24.62, 0.01)/1_000
ø2 = Datum(22.23, 0.01)/1_000
x = Datum(125.8, 0.3)/100

g  = Datum(9.805, 0.001)
g1 = (2*x-ø1)/(t1**2)
g2 = (2*x-ø2)/(t2**2)

e1 = abs(g.best - g1.best)/(g.delta + g1.delta)
e2 = abs(g.best - g2.best)/(g.delta + g2.delta)

print(f"{ø1=}")
print(f"{t1=}")
print(f"{g1=}")
print(f"{e1=}")
print("---")
print(f"{ø2=}")
print(f"{t2=}")
print(f"{g2=}")
print(f"{e2=}")

d2 = 30.5
d3 = 53.3
d4 = 68.4
d1 = 83.6
d5 = 106.5

### Chauvenet ###
def chauvenet(N: int, µ: float, s: float, sosp: float) -> bool:
    t = abs(sosp - µ)/s
    p = 1 - erf(t)
    n = N * p
    return n < .5

# --- t1 --- #
print(chauvenet(100, 503619.48, 256.71, 502791))
print(chauvenet(100, 503619.48, 256.71, 502882))
print(chauvenet(100, 503619.48, 256.71, 504247))
# --- t2 ---- #
print(chauvenet(100, 503908.47, 270.92, 503250))
print(chauvenet(100, 503908.47, 270.92, 503178))
print(chauvenet(100, 503908.47, 270.92, 503248))
# ----------- #
