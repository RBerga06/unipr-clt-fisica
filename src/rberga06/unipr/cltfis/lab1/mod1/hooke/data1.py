#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from ...core import *


@dataclass(slots=True)
class Spring:
    Ms: DataSet
    Xs: DataSet


s = Spring(
    Ms=DataSet((
        DataPoint(0, 0.01),
        DataPoint(407.73, 0.01),
        DataPoint(542.47, 0.01),
        DataPoint(667.82, 0.01),
        DataPoint(950.22, 0.01),
        DataPoint(1085.56, 0.01),
        DataPoint(1220.28, 0.01),
        DataPoint(1628.02, 0.01),
    )),
    Xs=DataSet((
        PickBestPoint(data_points([
            (3.3, 0.1),
            (3.3, 0.1),
            (3.4, 0.1),
        ])),
        PickBestPoint(data_points([
            (7.9, 0.1),
            (8.0, 0.1),
            (7.9, 0.1),
        ])),
        PickBestPoint(data_points([
            (9.5, 0.1),
            (9.6, 0.1),
            (9.6, 0.1),
        ])),
        PickBestPoint(data_points([
            (11.3, 0.1),
            (11.3, 0.1),
            (11.2, 0.1),
        ])),
        PickBestPoint(data_points([
            (14.3, 0.1),
            (14.4, 0.1),
            (14.5, 0.1),
        ])),
        PickBestPoint(data_points([
            (15.9, 0.1),
            (15.9, 0.1),
            (15.8, 0.1),
        ])),
        PickBestPoint(data_points([
            (17.5, 0.1),
            (17.4, 0.1),
            (17.5, 0.1),
        ])),
        PickBestPoint(data_points([
            (22.1, 0.1),
            (22.2, 0.1),
            (22.2, 0.1),
        ])),
    )),
)


X = s.Ms.map(lambda m: m/1000)
Y = s.Xs

a, b = linear_regression_plot(X, Y, yshift=True)
plt.show()  # type: ignore

print(a)
print(b*g)
