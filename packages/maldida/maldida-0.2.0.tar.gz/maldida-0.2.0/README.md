# MALDIDA

MALDIDA provides lightweight preprocessing and augmentation utilities for MALDI-TOF spectra. It includes a simple dataset reader, common preprocessing steps, augmentation helpers, and two bundled MARISMA samples so you can try the pipeline without additional data.

## Features
- Spectrum loader (`SpectrumObject`) with Bruker (`acqu`/`fid`) and TSV readers
- Composable preprocessing (variance stabilisation, smoothing, baseline correction, trimming, binning, normalisation, noise filters)
- Data augmentation helpers to simulate experimental variability
- Dataset parser with optional HDF5 persistence
- Bundled MARISMA samples plus ready-to-run example and tests

## Installation
```bash
pip install -e .
```

Python 3.8+ is recommended. Dependencies are installed automatically from `setup.py`.

## Quickstart with the bundled MARISMA samples
```python
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

# Locate the two MARISMA example spectra shipped with the package
sample_root = get_sample_data_path()

preprocess_pipeline = SequentialPreprocessor(
    VarStabilizer(method="sqrt"),
    Smoother(halfwindow=5),
    BaselineCorrecter(method="SNIP", snip_n_iter=5),
    Normalizer(sum=1.0),
    Trimmer(min=2000, max=20000),
    Binner(step=3),
)

dataset = MaldiDataset(sample_root, preprocess_pipeline=preprocess_pipeline, n_samples=2)
dataset.parse_dataset()
print(f"Loaded {len(dataset)} spectra")

# Grab the first processed spectrum and augment it
first = dataset.get_data()[0]["spectrum"]
augmenter = DataAugmenter(random_state=0)
augmented = augmenter.proportional_shifting(
    SpectrumObject(mz=first.mz.copy(), intensity=first.intensity.copy()), p0=0.3
)
print(f"Original peaks: {len(first)}, Augmented peaks: {len(augmented)}")
```

## Build spectra manually
You can also construct a spectrum directly:
```python
import numpy as np
from MALDIDA import SpectrumObject, SequentialPreprocessor, Binner, Normalizer

toy = SpectrumObject(
    mz=np.array([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]),
    intensity=np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100]),
)

pipeline = SequentialPreprocessor(
    Normalizer(sum=1.0),
    Binner(step=50),
)
processed = pipeline(toy)
```

## Examples and tests
- Run the ready-to-use MARISMA example:
  ```bash
  python examples/marisma_example.py
  ```
- Execute the tests (requires `pytest`):
  ```bash
  pip install pytest
  pytest
  ```

## License
Licensed under the GNU Lesser General Public License v3.0 or later (see `LICENSE`).

## Contact
For feedback or questions, open an issue or reach out at `alguerre@pa.uc3m.es`.
