from ...datum import Datum

t1 = Datum(503619.48, 256.71/10)/1_000_000
t2 = Datum(503908.47, 270.92/10)/1_000_000

ø1 = Datum(24.62, 0.01)/1_000
ø2 = Datum(22.23, 0.01)/1_000
x = Datum(125.9, 0.3)/100

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
