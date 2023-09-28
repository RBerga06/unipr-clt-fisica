# pyright: reportIncompatibleVariableOverride=false
from dataclasses import dataclass
from typing import Protocol
from math import pi as π
from typing_extensions import override
from ...core import DataPoint, Measure, PickBestPointDataSet


class RealObject(Protocol):
    m: Measure
    V: Measure

    @property
    def d(self, /) -> Measure:
        """The density!"""
        return DataPoint.from_const(1_000) * self.m / self.V


@dataclass
class Parallelepiped(RealObject):
    m: Measure
    x: Measure
    y: Measure
    z: Measure

    @property
    @override
    def V(self, /) -> Measure:
        return self.x * self.y * self.z


@dataclass
class Cylinder(RealObject):
    m: Measure
    h: Measure
    ø: Measure

    @property
    @override
    def V(self, /) -> Measure:
        return (π/4) * self.ø ** 2 * self.h


@dataclass
class Sphere(RealObject):
    m: Measure
    ø: Measure

    @property
    @override
    def V(self, /) -> Measure:
        return (π/6) * self.ø ** 3


### Object 01 ###

o1 = Parallelepiped(
    m = PickBestPointDataSet.from_raw([
        (107.40, 0.01),
    ]),
    x = PickBestPointDataSet.from_raw([
        (39.90,0.05),
        (39.90,0.05),
        (39.90,0.05),
    ]),
    y = PickBestPointDataSet.from_raw([
        (64.60, 0.05),
        (64.40, 0.05),
        (64.40, 0.05),
    ]),
    z = PickBestPointDataSet.from_raw([
        (5.00,0.05),
        (5.01,0.01),
        (5.18,0.01),
        (4.99,0.01),
        (4.98,0.01),
    ]),
)
print(o1.d)


### Object 02 ("Cilindro") ###

o2 = Cylinder(
    m = PickBestPointDataSet.from_raw([(41.21, 0.01)]),
    h = PickBestPointDataSet.from_raw([
        (24.83, 0.01),
        (24.82, 0.01),
        (24.83, 0.01),
    ]),
    ø = PickBestPointDataSet.from_raw([
        (27.95, 0.05),
        (28.05, 0.05),
        (28.00, 0.05),
    ]),
)
print(o2.d)


### Object 03 ("Sphere") ###

o3 = Sphere(
    m = DataPoint(35.81, 0.01),
    ø = DataPoint(20.63, 0.01),
)
print(o3.d)

# m (g)
# 35.81,0.01
# 35.81,0.01
#
# ø (mm)
# 20.63,0.01
# 20.63,0.01
# 20.64,0.01


### Object 4 ("Little Cylinder") ###

o4 = Cylinder(
    m = DataPoint( 8.00, 0.01),
    h = DataPoint(77.80, 0.05),
    ø = DataPoint( 6.97, 0.01),
)
print(o4.d)

# m (g)
# 8.00,0.01
# 
# h (mm)
# 77.75,0.05
# 77.80,0.05
# 77.80,0.05
# 
# ø (mm)
# 6.97,0.01
# 6.97,0.01
# 6.98,0.01
