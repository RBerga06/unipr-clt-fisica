import math
def ln(d):
  return Datum(math.log(d.best), d.delta_rel)

a = Datum(-71.785524864, 4.2047211397)
b = Datum(-24.6907231365, 0.6571863538)
c = Datum(13.1964752899, 2.4802492685)
x = Datum(992, 1)
Teb = a - b * ln(x + c)
