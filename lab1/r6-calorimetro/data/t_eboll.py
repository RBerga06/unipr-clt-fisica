import math
from rberga06.phylab import Datum, Measure

# def ln(d: Measure[float]):
#   return Datum(math.log(d.best), d.delta/d.best)

# a = Datum(-71.785524864, 4.2047211397)
# b = Datum(-24.6907231365, 0.6571863538)
# c = Datum(13.1964752899, 2.4802492685)
q = Datum(71.0157894737, 0.4481164955)
m = Datum(0.0285964912, 4.5431085042E-4)
x = Datum(992, 1)  # hPa
Teb = m * x + q # a - b * ln(x + c)  # °C
# Teb = Datum(Teb.best, 0)  # °C
