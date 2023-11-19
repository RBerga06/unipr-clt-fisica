#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# import matplotlib.pyplot as plt

from rberga06.phylab import Datum, π, g
# from ...core import *


# @dataclass(slots=True)
# class Spring:
#     Ms: DataSet
#     Xs: DataSet
#
#
# s = Spring(
#     Ms=DataSet.new([
#         0.0,
#         407.73,
#         542.47,
#         667.82,
#         950.22,
#         1085.56,
#         1220.28,
#         1628.02,
#     ], delta=0.01),
#     Xs=DataSet((
#         PickBestPoint.new([
#             (3.3, 0.1),
#             (3.3, 0.1),
#             (3.4, 0.1),
#         ])),
#         PickBestPoint.new([
#             (7.9, 0.1),
#             (8.0, 0.1),
#             (7.9, 0.1),
#         ])),
#         PickBestPoint.new([
#             (9.5, 0.1),
#             (9.6, 0.1),
#             (9.6, 0.1),
#         ])),
#         PickBestPoint(data_points([
#             (11.3, 0.1),
#             (11.3, 0.1),
#             (11.2, 0.1),
#         ])),
#         PickBestPoint(data_points([
#             (14.3, 0.1),
#             (14.4, 0.1),
#             (14.5, 0.1),
#         ])),
#         PickBestPoint(data_points([
#             (15.9, 0.1),
#             (15.9, 0.1),
#             (15.8, 0.1),
#         ])),
#         PickBestPoint(data_points([
#             (17.5, 0.1),
#             (17.4, 0.1),
#             (17.5, 0.1),
#         ])),
#         PickBestPoint(data_points([
#             (22.1, 0.1),
#             (22.2, 0.1),
#             (22.2, 0.1),
#         ])),
#     )),
# )


# X = s.Ms.map(lambda m: m/1000)
# Y = s.Xs
#
# a, b = linear_regression_plot(X, Y, yshift=True)
# plt.show()  # type: ignore

#b1 = Datum(0.01162, 1e-4)
#b2 = Datum(4.604e-4, 0.002e-4)
b1 = Datum(11.62,0.12)/100
b2 = Datum(4.604,0.002)/10
k1 = g/b1
k2 = 4*π**2/b2
print(k1)
print(k2)
print(abs(k1.best - k2.best)/(k1.delta + k2.delta))

# k ∆x = m g
# ∆x/m = g/k = b
# k = g/b

# cm / g = (10^-2 m)/(10^-3 kg) = 10 m/kg
