#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from ...core import *


@dataclass(slots=True)
class Object:
    m: Measure
    x: Measure


@dataclass(slots=True)
class Spring:
    objs: list[Object]


s = Spring(
    [
        Object(
            DataPoint(0, 0.01),
            PickBestPoint(data_points([
                (3.3, 0.1),
                (3.3, 0.1),
                (3.4, 0.1),
            ])),
        ),
        Object(
            DataPoint(407.73, 0.01),
            PickBestPoint(data_points([
                (7.9, 0.1),
                (8.0, 0.1),
                (7.9, 0.1),
            ])),
        ),
        Object(
            DataPoint(542.47, 0.01),
            PickBestPoint(data_points([
                (9.5, 0.1),
                (9.6, 0.1),
                (9.6, 0.1),
            ])),
        ),
        Object(
            DataPoint(667.82, 0.01),
            PickBestPoint(data_points([
                (11.3, 0.1),
                (11.3, 0.1),
                (11.2, 0.1),
            ])),
        ),
        Object(
            DataPoint(950.22, 0.01),
            PickBestPoint(data_points([
                (14.3, 0.1),
                (14.4, 0.1),
                (14.5, 0.1),
            ])),
        ),
        Object(
            DataPoint(1085.56, 0.01),
            PickBestPoint(data_points([
                (15.9, 0.1),
                (15.9, 0.1),
                (15.8, 0.1),
            ])),
        ),
        Object(
            DataPoint(1220.28, 0.01),
            PickBestPoint(data_points([
                (17.5, 0.1),
                (17.4, 0.1),
                (17.5, 0.1),
            ])),
        ),
        Object(
            DataPoint(1628.02, 0.01),
            PickBestPoint(data_points([
                (22.1, 0.1),
                (22.2, 0.1),
                (22.2, 0.1),
            ])),
        ),
    ],
)


X = DataSet(tuple([o.m/1000 for o in s.objs]))
Y = DataSet(tuple([o.x for o in s.objs]))

a, b = linear_regression(X, Y)



# y0 = s.objs[0].x.best
# Ys = [y - y0 for y in Y.bests]

plt.errorbar(  # type: ignore
    X.bests, Y.bests,
    xerr=X.deltas,
    yerr=Y.deltas,
    fmt=".",
)
# plt.plot(  # type: ignore
#     [s.objs[0].m.best, s.objs[-1].m.best],
#     [a.best+b.best*s.objs[0].m.best - y0, a.best+b.best*s.objs[-1].m.best - y0],
# )
plt.show()  # type: ignore

print(a)
print(b*g)
