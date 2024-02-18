from rberga06.phylab import Datum
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from t_eboll import Teb

q1 = Datum(55.1660457307, 0.004603675)
xi1 = Datum(-0.0027120068, 1.6298245602E-5)
Teq = xi1 * Datum(69.5, 24.7) + q1  # °C
m_H2O_eb  = Datum(85.12, 0.03)  # g
m_H2O_amb = Datum(99.35, 0.02)  # g
Tamb = Datum(24.7, 0.2)  # °C
m_eq = m_H2O_eb * (Teb - Teq) / (Teq - Tamb) - m_H2O_amb  # g
print(m_eq, "g")
