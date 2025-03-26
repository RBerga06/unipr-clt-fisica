from enum import Enum, auto
import pandas as pd
import numpy as np
from numpy import typing as npt
from matplotlib import pyplot as plt
from typing import Literal, cast
from collections.abc import Sequence


def _pd2np(pd: pd.Series[float]) -> npt.NDArray[np.float64]:
    return cast(npt.NDArray[np.float64], pd.to_numpy(np.float64))


class Oscilloscope(Enum):
    """Formati dati degli oscilloscopi"""

    LabDid = auto()
    """L'oscilloscopio dei laboratori didattici"""
    Elettr = auto()
    """L'oscilloscopio del laboratorio di elettronica"""
    Coassiali = auto()
    """L'oscilloscopio che abbiamo usato per i cavi coassiali"""

    def load_channel(
        self,
        ch: Literal[1, 2] = 1,
        idx: int | None = None,
        dir: str = ".",
        *,
        del_data: float | None = None,
        del_data_slices: Sequence[slice] = (),
        plot_dir: str | None = None,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """
        Carica i dati di un solo canale, acquisiti con questo oscilloscopio.

        `ch`: Il canale in questione (0 o 1)
        `idx`: L'indice del file (default: 0)
        `dir`: La cartella che contiene i file

        Ritorna la tripla `(t, ch1, ch2)`.
        """
        match self:
            case Oscilloscope.LabDid:
                idx = idx or 0
                file = pd.read_csv(f"{dir}/F{idx:04}CH{ch}.CSV", header=None)
                atten = np.float64(file.at[14, 1])
                t = _pd2np(file[3])
                data = _pd2np(file[4]) / atten
                if del_data is not None:
                    data[data == del_data] = np.nan
                for del_data_slice in del_data_slices:
                    data[del_data_slice] = np.nan
                if plot_dir is not None:
                    plot_data(t, data, to_file=f"{plot_dir}/{idx}.png")
                return t, data
            case Oscilloscope.Elettr:
                idx = idx or 0
                file = pd.read_csv(f"{dir}/TEK{idx:05}.CSV", skiprows=15)
                t = _pd2np(file["TIME"])
                data = _pd2np(file[f"CH{ch}"])
                if del_data is not None:
                    data[data == del_data] = np.nan
                for del_data_slice in del_data_slices:
                    data[del_data_slice] = np.nan
                if plot_dir is not None:
                    plot_data(t, data, to_file=f"{plot_dir}/{idx}.png")
                return (t, data)
            case Oscilloscope.Coassiali:
                raise NotImplementedError

    def load_data(
        self,
        idx: int | None = None,
        dir: str = ".",
        *,
        # TODO: Find out automatically when data has to be removed.
        ch1_del_data: float | None = None,
        ch2_del_data: float | None = None,
        del_data_slices: Sequence[slice] = (),
        plot_dir: str | None = None,
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """
        Carica i dati acquisiti con questo oscilloscopio.

        `idx`: L'indice del file (default: 0)
        `dir`: La cartella che contiene i file

        Ritorna la tripla `(t, ch1, ch2)`.
        """
        match self:
            case Oscilloscope.LabDid:
                t1, ch1 = self.load_channel(1, idx, dir, del_data=ch1_del_data, del_data_slices=del_data_slices)
                t2, ch2 = self.load_channel(2, idx, dir, del_data=ch2_del_data, del_data_slices=del_data_slices)
                assert np.array_equal(t1, t2, equal_nan=True)
                if plot_dir is not None:
                    plot_data(t1, ch1, ch2, to_file=f"{plot_dir}/{idx}.png")
                return (t1, ch1, ch2)
            case Oscilloscope.Elettr:
                idx = idx or 0
                file = pd.read_csv(f"{dir}/TEK{idx:05}.CSV", skiprows=15)
                t = _pd2np(file["TIME"])
                ch1 = _pd2np(file["CH1"])
                ch2 = _pd2np(file["CH2"])
                if ch1_del_data is not None:
                    ch1[ch1 == ch1_del_data] = np.nan
                if ch2_del_data is not None:
                    ch2[ch2 == ch2_del_data] = np.nan
                for del_data_slice in del_data_slices:
                    ch1[del_data_slice] = np.nan
                    ch2[del_data_slice] = np.nan
                if plot_dir is not None:
                    plot_data(t, ch1, ch2, to_file=f"{plot_dir}/{idx}.png")
                return (t, ch1, ch2)
            case Oscilloscope.Coassiali:
                raise NotImplementedError


def plot_data(
    t: npt.NDArray[np.float64],
    ch1: npt.NDArray[np.float64],
    ch2: npt.NDArray[np.float64] | None = None,
    /,
    *,
    to_file: str | None = None,
    same_axis: bool = False,
):
    _, ax1 = plt.subplots()
    if ch2 is None or same_axis:
        ax2 = ax1
    else:
        ax2 = ax1.twinx()
    _ = ax1.plot(t, ch1, color="C0")
    if ch2 is not None:
        _ = ax2.plot(t, ch2, color="C1")
    if to_file is not None:
        plt.savefig(to_file)
        plt.close()
    else:
        plt.show()
