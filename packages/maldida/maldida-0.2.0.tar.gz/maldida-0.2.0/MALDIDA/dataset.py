"""Dataset utilities for MALDI-TOF experiments."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, Union

import h5py
import numpy as np
from tqdm import tqdm

from .preprocess import SequentialPreprocessor
from .spectrum import SpectrumObject


def get_sample_data_path() -> Path:
    """Return the path to the bundled MARISMA sample spectra."""
    return Path(__file__).resolve().parent / "data" / "MARISMA"


class MaldiDataset:
    """Reader for directory-based MALDI-TOF datasets."""

    def __init__(
        self,
        root_dir: Union[str, Path],
        preprocess_pipeline: Optional[SequentialPreprocessor] = None,
        genus: Optional[str] = None,
        species: Optional[str] = None,
        n_samples: Optional[int] = None,
    ):
        self.root_dir = Path(root_dir)
        self.preprocess_pipeline = preprocess_pipeline
        self.genus = genus
        self.species = species
        self.n_samples = n_samples
        self.data = []

    def parse_dataset(self):
        """Traverse the directory tree and collect spectra into `self.data`."""
        print(f"Reading dataset from {self.root_dir}")
        total_replicates = sum(
            1
            for year_path in self.root_dir.iterdir()
            if year_path.is_dir()
            for genus_path in year_path.iterdir()
            if genus_path.is_dir()
            for species_path in genus_path.iterdir()
            if species_path.is_dir()
            for _ in species_path.iterdir()
            if _.is_dir()
        )

        with tqdm(total=total_replicates or None, desc="Processing Dataset", unit="folder") as pbar:
            for year_path in sorted(self.root_dir.iterdir()):
                if not year_path.is_dir():
                    continue
                year_label = year_path.name
                for genus_path in sorted(year_path.iterdir()):
                    if not genus_path.is_dir():
                        continue
                    genus_label = genus_path.name
                    for species_path in sorted(genus_path.iterdir()):
                        if not species_path.is_dir():
                            continue
                        species_label = species_path.name
                        if not self._filter_conditions(genus_label, species_label):
                            continue

                        genus_species_label = f"{genus_label} {species_label}"
                        for replicate_path in sorted(species_path.iterdir()):
                            if not replicate_path.is_dir():
                                continue
                            for lecture_path in sorted(replicate_path.iterdir()):
                                if not lecture_path.is_dir():
                                    continue
                                acqu_file, fid_file = self._find_acqu_fid_files(lecture_path)
                                if acqu_file and fid_file:
                                    spectrum = SpectrumObject.from_bruker(str(acqu_file), str(fid_file))
                                    if self.preprocess_pipeline:
                                        spectrum = self.preprocess_pipeline(spectrum)
                                    if np.isnan(spectrum.intensity).any():
                                        continue
                                    self.data.append(
                                        {
                                            "spectrum": spectrum,
                                            "spectrum_intensity": spectrum.intensity,
                                            "spectrum_mz": spectrum.mz,
                                            "year_label": year_label,
                                            "genus_label": genus_label,
                                            "genus_species_label": genus_species_label,
                                        }
                                    )
                            pbar.update(1)

        if self.n_samples and len(self.data) > self.n_samples:
            np.random.shuffle(self.data)
            self.data = self.data[: self.n_samples]

    def _filter_conditions(self, genus_label: str, species_label: str) -> bool:
        if self.genus and genus_label != self.genus:
            return False
        if self.species and species_label != self.species:
            return False
        return True

    def _find_acqu_fid_files(self, directory: Path) -> Tuple[Optional[Path], Optional[Path]]:
        acqu_file = next(directory.rglob("acqu"), None)
        fid_file = next(directory.rglob("fid"), None)
        return acqu_file, fid_file

    def save_to_hdf5(self, file_name: str):
        """Persist the collected spectra to an HDF5 file."""
        with h5py.File(file_name, "w") as h5f:
            spectra = np.array([d["spectrum_intensity"] for d in self.data])
            mz_values = np.array([d["spectrum_mz"] for d in self.data])
            year_labels = np.array([d["year_label"] for d in self.data])
            genus_labels = np.array([d["genus_label"] for d in self.data])
            genus_species_labels = np.array([d["genus_species_label"] for d in self.data])

            h5f.create_dataset("spectra", data=spectra, chunks=True, compression="gzip")
            h5f.create_dataset("mz_values", data=mz_values, chunks=True, compression="gzip")
            h5f.create_dataset("year_labels", data=year_labels.astype("S"), chunks=True, compression="gzip")
            h5f.create_dataset("genus_labels", data=genus_labels.astype("S"), chunks=True, compression="gzip")
            h5f.create_dataset(
                "genus_species_labels",
                data=genus_species_labels.astype("S"),
                chunks=True,
                compression="gzip",
            )

    def load_from_hdf5(self, file_name: str):
        """Load spectra previously stored with `save_to_hdf5`."""
        with h5py.File(file_name, "r") as h5f:
            self.data = [
                {
                    "spectrum": SpectrumObject(
                        mz=h5f["mz_values"][i],
                        intensity=h5f["spectra"][i],
                    ),
                    "spectrum_intensity": h5f["spectra"][i],
                    "spectrum_mz": h5f["mz_values"][i],
                    "year_label": h5f["year_labels"][i].decode("utf-8"),
                    "genus_label": h5f["genus_labels"][i].decode("utf-8"),
                    "genus_species_label": h5f["genus_species_labels"][i].decode("utf-8"),
                }
                for i in range(len(h5f["spectra"]))
            ]

    def get_data(self):
        """Return the collected spectra as a list of dictionaries."""
        return self.data

    def __len__(self):
        return len(self.data)
