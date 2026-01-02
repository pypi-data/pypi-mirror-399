"""Example: load the bundled MARISMA samples and run a preprocessing/augmentation pipeline."""

from MALDIDA import (
    Binner,
    BaselineCorrecter,
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


def build_preprocess_pipeline() -> SequentialPreprocessor:
    return SequentialPreprocessor(
        VarStabilizer(method="sqrt"),
        Smoother(halfwindow=5),
        BaselineCorrecter(method="SNIP", snip_n_iter=5),
        Normalizer(sum=1.0),
        Trimmer(min=2000, max=20000),
        Binner(step=3),
    )


def main():
    sample_root = get_sample_data_path()
    print(f"Using MARISMA sample data at: {sample_root}")

    preprocess_pipeline = build_preprocess_pipeline()

    dataset = MaldiDataset(sample_root, preprocess_pipeline=preprocess_pipeline, n_samples=2)
    dataset.parse_dataset()
    print(f"Loaded {len(dataset)} spectra from the sample bundle.")

    first_spectrum = dataset.get_data()[0]["spectrum"]
    augmenter = DataAugmenter(random_state=0)
    augmented = augmenter.proportional_shifting(
        SpectrumObject(mz=first_spectrum.mz.copy(), intensity=first_spectrum.intensity.copy()),
        p0=0.3,
    )

    print(f"Original peaks: {len(first_spectrum)}, Augmented peaks: {len(augmented)}")


if __name__ == "__main__":
    main()
