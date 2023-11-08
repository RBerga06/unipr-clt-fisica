# pyright: reportIncompatibleVariableOverride=false
from dataclasses import dataclass
from typing import Protocol
from typing_extensions import override
from ...datum import Measure, Datum as DataPoint
from ...core import π


class RealObject(Protocol):
    m: Measure
    V: Measure

    @property
    def d(self, /) -> Measure:
        """The density!"""
        return 1_000 * self.m / self.V


@dataclass(slots=True, frozen=True)
class Parallelepiped(RealObject):
    m: Measure
    x: Measure
    y: Measure
    z: Measure

    @property
    @override
    def V(self, /) -> Measure:
        return self.x * self.y * self.z


@dataclass(slots=True, frozen=True)
class Cylinder(RealObject):
    m: Measure
    h: Measure
    ø: Measure

    @property
    @override
    def V(self, /) -> Measure:
        return (π/4) * self.ø ** 2 * self.h


@dataclass(slots=True, frozen=True)
class Sphere(RealObject):
    m: Measure
    ø: Measure

    @property
    @override
    def V(self, /) -> Measure:
        return (π/6) * self.ø ** 3


### Data ###

o1 = Parallelepiped(
    m = DataPoint(107.40, 0.01),
    x = PickBestPoint(data_points([
        (39.90,0.05),
        (39.90,0.05),
        (39.90,0.05),
    ])),
    y = PickBestPoint(data_points([
        (64.60, 0.05),
        (64.40, 0.05),
        (64.40, 0.05),
    ])),
    z = PickBestPoint(data_points([
        (5.00, 0.05),
        (5.01, 0.01),
        (5.18, 0.01),
        (4.99, 0.01),
        (4.98, 0.01),
    ])),
)
print(o1.V)
print(o1.d)

o2 = Cylinder(
    m = DataPoint(41.21, 0.01),
    h = PickBestPoint(data_points([
        (24.83, 0.01),
        (24.82, 0.01),
        (24.83, 0.01),
    ])),
    ø = PickBestPoint(data_points([
        (27.95, 0.05),
        (28.05, 0.05),
        (28.00, 0.05),
    ])),
)
print(o2.V)
print(o2.d)

o3 = Sphere(
    m = PickBestPoint(data_points([
        (35.81, 0.01),
        (35.81, 0.01),
    ])),
    ø = PickBestPoint(data_points([
        (20.63, 0.01),
        (20.63, 0.01),
        (20.64, 0.01),
    ])),
)
print(o3.V)
print(o3.d)

o4 = Cylinder(
    m = DataPoint(8.00, 0.01),
    h = PickBestPoint(data_points([
        (77.75, 0.05),
        (77.80, 0.05),
        (77.80, 0.05),
    ])),
    ø = PickBestPoint(data_points([
        (6.97, 0.01),
        (6.97, 0.01),
        (6.98, 0.01),
    ])),
)
print(o4.V)
print(o4.d)
