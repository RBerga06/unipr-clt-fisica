from rberga06.phylab import Measure, Datum
__import__("sys").path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from Teb import Teb
from regressioni import m_eq

c_aq = 4186  # J/(kg · K)

def c(Teq: Measure[float], Taq: Measure[float], m_met: Measure[float], m_aq: Measure[float]):
    ms = (m_aq + m_eq) / m_met
    Ts = (Teq - Taq) / (Teb - Teq)
    return ms * c_aq * Ts

cs = [
    c(
        Teq=Datum(),
        Taq=Datum(),
        m_met=Datum(),
        m_aq=Datum()
    ),
    c(
        Teq=Datum(),
        Taq=Datum(),
        m_met=Datum(),
        m_aq=Datum()
    ),
    c(
        Teq=Datum(),
        Taq=Datum(),
        m_met=Datum(),
        m_aq=Datum()
    ),
]
