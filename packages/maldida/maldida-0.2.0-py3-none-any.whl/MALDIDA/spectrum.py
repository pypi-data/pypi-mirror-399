"""Spectrum utilities and data loaders for MALDIDA."""

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class SpectrumObject:
    """Container for a single MALDI-TOF spectrum.

    A spectrum is represented by two aligned 1-D numpy arrays: `mz` (mass/charge)
    and `intensity`. Utility constructors are provided to load Bruker outputs or
    plain text/TSV exports.
    """

    def __init__(self, mz: Optional[np.ndarray] = None, intensity: Optional[np.ndarray] = None):
        self.mz = mz
        self.intensity = intensity

        if self.intensity is not None and np.issubdtype(self.intensity.dtype, np.unsignedinteger):
            self.intensity = self.intensity.astype(int)
        if self.mz is not None and np.issubdtype(self.mz.dtype, np.unsignedinteger):
            self.mz = self.mz.astype(int)

    def __getitem__(self, index):
        return SpectrumObject(mz=self.mz[index], intensity=self.intensity[index])

    def __len__(self):
        return 0 if self.mz is None else self.mz.shape[0]

    def plot(self, as_peaks: bool = False, **kwargs):
        """Plot the spectrum using matplotlib."""
        if as_peaks:
            mz_plot = np.stack([self.mz - 1, self.mz, self.mz + 1]).T.reshape(-1)
            int_plot = np.stack(
                [np.zeros_like(self.intensity), self.intensity, np.zeros_like(self.intensity)]
            ).T.reshape(-1)
        else:
            mz_plot, int_plot = self.mz, self.intensity
        plt.plot(mz_plot, int_plot, **kwargs)

    def __repr__(self):
        string_ = np.array2string(
            np.stack([self.mz, self.intensity]), precision=5, threshold=10, edgeitems=2
        )
        mz_string, int_string = string_.split("\n")
        mz_string = mz_string[1:]
        int_string = int_string[1:-1]
        return "SpectrumObject([\n\tmz  = %s,\n\tint = %s\n])" % (mz_string, int_string)

    @staticmethod
    def tof2mass(ML1, ML2, ML3, TOF):
        A = ML3
        B = np.sqrt(1e12 / ML1)
        C = ML2 - TOF

        if A == 0:
            return (C * C) / (B * B)
        return ((-B + np.sqrt((B * B) - (4 * A * C))) / (2 * A)) ** 2

    @classmethod
    def from_bruker(cls, acqu_file: str, fid_file: str) -> "SpectrumObject":
        """Load a spectrum from Bruker output files (`acqu` + `fid`)."""
        with open(acqu_file, "rb") as f:
            lines = [line.decode("utf-8", errors="replace").rstrip() for line in f]

        TD = DELAY = DW = ML1 = ML2 = ML3 = BYTORDA = None
        for line in lines:
            if line.startswith("##$TD"):
                TD = int(line.split("= ")[1])
            if line.startswith("##$DELAY"):
                DELAY = int(line.split("= ")[1])
            if line.startswith("##$DW"):
                DW = float(line.split("= ")[1])
            if line.startswith("##$ML1"):
                ML1 = float(line.split("= ")[1])
            if line.startswith("##$ML2"):
                ML2 = float(line.split("= ")[1])
            if line.startswith("##$ML3"):
                ML3 = float(line.split("= ")[1])
            if line.startswith("##$BYTORDA"):
                BYTORDA = int(line.split("= ")[1])

        if None in (TD, DELAY, DW, ML1, ML2, ML3, BYTORDA):
            raise ValueError("Missing calibration parameters in Bruker acqu file.")

        intensity = np.fromfile(fid_file, dtype={0: "<i", 1: ">i"}[BYTORDA])

        if len(intensity) < TD:
            TD = len(intensity)
        TOF = DELAY + np.arange(TD) * DW

        mass = cls.tof2mass(ML1, ML2, ML3, TOF)

        intensity[intensity < 0] = 0

        return cls(mz=mass, intensity=intensity)

    @classmethod
    def from_tsv(cls, file: str, sep: str = " ") -> "SpectrumObject":
        """Load a spectrum from a two-column text/TSV file."""
        s = pd.read_table(file, sep=sep, index_col=None, comment="#", header=None).values
        mz = s[:, 0]
        intensity = s[:, 1]
        return cls(mz=mz, intensity=intensity)
