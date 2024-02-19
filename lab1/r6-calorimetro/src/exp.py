import math
from rberga06.phylab import Datum, Measure
__import__("sys").path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from regressioni import m_eq
c_aq = Datum(4186, 0)
# q = Datum(87.288, 0.007)
# k = Datum(-0.004796, 4e-6)
Tamb = Datum(24.1, 0.1)

def exp(d: Measure[float]):
    return Datum.from_delta_rel(math.exp(d.best), d.delta)

print(exp(Datum(4.153871158, 1.880090193E-4)) + Tamb)
tau = -1/Datum(-8.6879351535E-5, 1.0683807428E-7) # s
print(tau, "s")
k = (c_aq * m_eq)/tau
print(k, "W/K")

# k = (Tamb - Taq)/tau
# tau = (Tamb - Taq)/k
# tau = (Tamb - Teb)/k
# print(tau/3600, "h")
