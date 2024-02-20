from rberga06.phylab import Datum
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from Teb import Teb

intercetta = Datum(55.1825093636, 0.00147224629)
coeff = Datum(-0.0027656105, 5.0117286396E-5)
Teq = coeff * Datum(69.5, 0.5) + intercetta  # °C
# Teq = Datum(Teq.best, 0.1)  # °C
print("(m_eq) Teq  =", Teq, "°C")
m_H2O_eb  = Datum(85.12, 0.03)  # g
m_H2O_amb = Datum(99.35, 0.02)  # g
Tamb = Datum(24.7, 0.1)  # °C
m_eq = m_H2O_eb * (Teb - Teq) / (Teq - Tamb) - m_H2O_amb  # g
print("m_eq =", m_eq, "g")
