from enum import Enum, auto
import pandas as pd
import numpy as np


class Oscilloscope(Enum):
    """Formati dati degli oscilloscopi"""

    LabDid = auto()
    """L'oscilloscopio dei laboratori didattici"""
    Elettr = auto()
    """L'oscilloscopio del laboratorio di elettronica"""
    Coassiali = auto()
    """L'oscilloscopio che abbiamo usato per i cavi coassiali"""

    def load_data(
        self,
        idx: int | None = None,
        dir: str = ".",
        *,
        # TODO: Find out automatically when data has to be removed.
        ch1_del_data: float | None = None,
        ch2_del_data: float | None = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Carica i dati acquisiti con questo oscilloscopio.

        `idx`: L'indice del file (default: 0)
        `dir`: La cartella che contiene i file

        Ritorna la tripla `(t, ch1, ch2)`.
        """
        match self:
            case Oscilloscope.LabDid:
                idx = idx or 0
                file1 = pd.read_csv(f"{dir}/F{idx:04}CH1.CSV", header=None)
                file2 = pd.read_csv(f"{dir}/F{idx:04}CH2.CSV", header=None)
                atten1 = float(file1.at[14, 1])
                atten2 = float(file2.at[14, 1])
                t = file1[3].to_numpy(np.float64)
                ch1 = file1[4].to_numpy(np.float64) / atten1
                ch2 = file2[4].to_numpy(np.float64) / atten2
                if ch1_del_data is not None:
                    ch1[ch1 == ch1_del_data] = np.nan
                if ch2_del_data is not None:
                    ch2[ch2 == ch2_del_data] = np.nan
                return (t, ch1, ch2)
            case Oscilloscope.Elettr:
                raise NotImplementedError
            case Oscilloscope.Coassiali:
                raise NotImplementedError
