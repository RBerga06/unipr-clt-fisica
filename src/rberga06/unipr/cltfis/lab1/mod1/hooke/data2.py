#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Generic, TypeVar, cast
from matplotlib import pyplot as plt
from ...datum import Datum
# from ...core import *

# _M1 = TypeVar("_M1", bound=Measure)
# _M2 = TypeVar("_M2", bound=Measure)

# Masses
MM = Datum(24.31, 0.01)
M0 = Datum(18.84, 0.01) + MM/3
print(M0 + Datum(407.73, 0.01))
print(M0 + Datum(542.47, 0.01))
print(M0 + Datum(667.82, 0.01))
print(M0 + Datum(950.22, 0.01))
raise

@dataclass(slots=True, frozen=True)
class Spring(Generic[_M1, _M2]):
    Ms: _M1
    Ts: _M2


s = Spring(
    Ms=DataSet((

        # DataPoint(1085.56, 0.01),
        # DataPoint(1085.56, 0.01),
        # DataPoint(1220.28, 0.01),
    )),
    Ts=DataSet((
        DataSet(data_points([

        ], 0.000_001)),
        DataSet(data_points([
        ], 0.000_001)),
        DataSet(data_points([

            # 11.420_629,
        ], 0.000_001)),
        DataSet(data_points([
        ], 0.000_001)),
        # DataSet(data_points([
        #     14.311_381, 14.310_335, 14.316_397, 14.310_612, 14.310_951,
        #     14.311_313, 14.310_335, 14.311_249, 14.310_933, 14.311_243,
        #     14.313_426, 14.313_858, 14.311_980, 14.311_940, 14.312_760,
        #     14.312_551, 14.313_116, 14.311_970, 14.316_335, 14.313_692,
        #     14.315_488, 14.311_734, 14.313_830, 14.312_901, 14.311_869,
        #     # ----
        #     14.301_708, 14.302_173, 14.304_290, 14.304_782, 14.302_205,
        #     14.302_005, 14.307_075, 14.304_369, 14.310_311, 14.301_111,
        # ], 0.000_001)),
    )),
)

dist = NormalDistribution.from_dataset(cast(DataSet, s.Ts[0]), n=7)

Y = s.Ts.map(lambda t: (t/20)**2)   # convert 20T -> T^2
X = s.Ms.map(lambda m: m/1000)      # convert g -> kg

a, b = linear_regression_plot(X, Y)

print(b)
print((4 * π**2) / b)

# $a = -\omega^2 \Delta x$
# $- m \omega^2 = k$
# $\frac{4\pi^2}{k} m = T^2$
# $\frac{4\pi^2}{k} = b$

plt.show()  # type: ignore
#