import math
from rberga06.phylab import Datum, Measure

def ln(d: Measure[float]):
  return Datum(math.log(d.best), d.delta/d.best)

a = Datum(-71.785524864, 4.2047211397)
b = Datum(-24.6907231365, 0.6571863538)
c = Datum(13.1964752899, 2.4802492685)
x = Datum(992, 1)  # hPa
Teb = a - b * ln(x + c)  # °C
Teb = Datum(Teb.best, 0)  # °C
