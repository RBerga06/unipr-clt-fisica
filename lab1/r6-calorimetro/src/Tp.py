from rberga06.phylab import Measure, Datum
__import__("sys").path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from Teb import Teb
from regressioni import m_eq

c_aq = 4186  # J/(kg · K)

def c(Teq: Measure[float], Taq: Measure[float], m_met: Measure[float], m_aq: Measure[float]):
    ms = (m_aq + m_eq) / m_met
    Ts = (Teq - Taq) / (Teb - Teq)
    print("* Teq - Taq:", (Teq - Taq).delta_rel)
    print("* Teb - Teq:", (Teb - Teq).delta_rel)
    c_met = ms * c_aq * Ts
    print("-> c_met:", c_met)
    return c_met

cs = [
    c(  # grigio chiaro => acciaio inox
        Teq=Datum(25.2, 0.1),   # ± 0.2
        Taq=Datum(24.7, 0.1),
        m_met=Datum(12.43, 0.01),  # ± 0.02
        m_aq=Datum(197.54, 0.02),
    ),
    c(  # color ottone => ottone (Cu + Zn)
        Teq=Datum(25.9, 0.1),
        Taq=Datum(25.1, 0.1),
        m_met=Datum(28.73, 0.01),
        m_aq=Datum(194.81, 0.02),
    ),
    c(  # grigio scuro => piombo (Pb)
        Teq=Datum(26.0, 0.1),
        Taq=Datum(25.6, 0.1),
        m_met=Datum(44.86, 0.01),
        m_aq=Datum(194.00, 0.02),
    ),
]
