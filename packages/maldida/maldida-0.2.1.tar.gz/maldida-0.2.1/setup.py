from pathlib import Path

from setuptools import find_packages, setup


BASE_DIR = Path(__file__).parent

setup(
    name="maldida",
    version="0.2.1",
    author="Alejandro Guerrero-Lopez",
    author_email="aguerrero@imm.uzh.ch",
    description="Preprocessing and augmentation utilities for MALDI-TOF spectra.",
    long_description=(BASE_DIR / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/aguerrerolopez/MALDIDA",
    license="LGPL-3.0-or-later",
    packages=find_packages(include=["MALDIDA"]),
    install_requires=[
        "numpy>=1.20.0",
        "pandas",
        "scipy",
        "matplotlib",
        "tqdm",
        "h5py",
        "scikit-learn",
    ],
    package_data={"MALDIDA": ["data/**/*"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    include_package_data=True,
)
