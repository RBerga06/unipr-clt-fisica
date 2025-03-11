import numpy as np
from numpy import typing as npt
from typing import NamedTuple, final, Self, overload
from scipy.optimize import curve_fit


@overload
def sine_func(x: float, ampl: float, freq: float, phase: float, /) -> float: ...
@overload
def sine_func(x: npt.NDArray[np.float64], ampl: float, freq: float, phase: float, /) -> npt.NDArray[np.float64]: ...
def sine_func(x, ampl: float, freq: float, phase: float, /):
    return ampl * np.sin(2 * np.pi * freq * x + phase)


@final
class Sine(NamedTuple):
    """A sine function with amplitude, frequency and phase."""

    ampl: float
    """The amplitude"""
    freq: float
    """The frequency"""
    phase: float
    """The phase"""

    @property
    def period(self) -> float:
        return 1 / self.freq

    @overload
    def __call__(self, x: float) -> float: ...
    @overload
    def __call__(self, x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]: ...
    def __call__(self, x):
        return sine_func(x, *self)

    def __repr__(self) -> str:
        return f"sin[ampl = {self.ampl}, freq = {self.freq}, phase = {self.phase}]"

    @classmethod
    def fit(
        cls,
        x: npt.NDArray[np.float64],
        y: npt.NDArray[np.float64],
        /,
        *,
        ampl0: float | None = None,
        freq0: float | None = None,
        phase0: float | None = None,
    ) -> Self:
        params, cov = curve_fit(
            sine_func,
            x,
            y,
            p0=[
                np.nanmax(y) - np.nanmin(y) if ampl0 is None else ampl0,
                (2 * np.pi / ((x[np.nanargmax(y)] - x[np.nanargmin(y)]) * 2) if freq0 is None else freq0),
                0.0 if phase0 is None else phase0,
            ],
            nan_policy="omit",
        )
        return cls(*params)
