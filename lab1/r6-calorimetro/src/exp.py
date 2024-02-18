from rberga06.phylab import Datum
__import__("sys").path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from Teb import Teb
q = Datum(87.288, 0.007)
k = Datum(-0.004796, 4e-6)
Tamb = Datum(24.1, 0.1)
# k = (Tamb - Taq)/tau
# tau = (Tamb - Taq)/k
tau = (Tamb - Teb)/k
print(tau/3600, "h")
