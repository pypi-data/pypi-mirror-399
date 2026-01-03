# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from pathlib import Path
from setuptools import find_packages, setup


def _read_readme() -> str:
    return Path("README.MIRROR.md").read_text(encoding="utf-8")


setup(
    name="mobilesam-mirror",
    version="1.0.0",
    description="Packaging mirror of MobileSAM",
    long_description=_read_readme(),
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    url="https://github.com/Artificial-Sweetener/MobileSAM-Mirror",
    python_requires=">=3.8",
    install_requires=[],
    packages=find_packages(exclude=("notebooks",)),
    extras_require={
        "all": ["matplotlib", "pycocotools", "opencv-python", "onnx", "onnxruntime"],
        "dev": ["flake8", "isort", "black", "mypy"],
    },
)
