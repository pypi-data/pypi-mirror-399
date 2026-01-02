import numpy as np
import pytest

from MALDIDA import (
    BaselineCorrecter,
    Binner,
    DataAugmenter,
    MaldiDataset,
    Normalizer,
    SequentialPreprocessor,
    SpectrumObject,
    Smoother,
    Trimmer,
    VarStabilizer,
    get_sample_data_path,
)


@pytest.fixture(scope="module")
def sample_dataset():
    pipeline = SequentialPreprocessor(
        VarStabilizer(method="sqrt"),
        Smoother(halfwindow=5),
        BaselineCorrecter(method="SNIP", snip_n_iter=5),
        Normalizer(sum=1.0),
        Trimmer(min=2000, max=20000),
        Binner(step=5),
    )
    dataset = MaldiDataset(get_sample_data_path(), preprocess_pipeline=pipeline, n_samples=2)
    dataset.parse_dataset()
    return dataset


def test_sample_dataset_parses(sample_dataset):
    assert len(sample_dataset) > 0
    sample = sample_dataset.get_data()[0]
    assert sample["spectrum_intensity"].shape == sample["spectrum_mz"].shape
    assert not np.isnan(sample["spectrum_intensity"]).any()


def test_augmenter_preserves_length(sample_dataset):
    spectrum = sample_dataset.get_data()[0]["spectrum"]
    augmenter = DataAugmenter(random_state=42)
    augmented = augmenter.intensity_variability(
        SpectrumObject(mz=spectrum.mz.copy(), intensity=spectrum.intensity.copy()), p1=0.2, v1=0.05
    )
    assert augmented.intensity.shape == spectrum.intensity.shape
    assert np.all(augmented.intensity >= 0)
