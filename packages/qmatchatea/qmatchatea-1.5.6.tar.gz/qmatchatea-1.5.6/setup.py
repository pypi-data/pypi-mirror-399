# This code is part of qmatchatea.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import importlib.util
import os
import os.path

import setuptools

# Parse the version file
spec = importlib.util.spec_from_file_location("qmatchatea", "./qmatchatea/version.py")
version_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version_module)

# Define requirements
install_requires = [
    "numpy>=1.26.0",
    "scipy>=1.4.1",
    "matplotlib>=3.1.3",
    "qtealeaves>=1.7.21,<1.8.0",
    "qredtea>=0.3.13,<0.4.0",
    "qiskit>=1.0.0,<2.0.0",
    "joblib",
    "psutil",
]

# Get the readme file
if os.path.isfile("README.md"):
    with open("README.md", "r") as fh:
        long_description = fh.read()
else:
    long_description = ""

setuptools.setup(
    name="qmatchatea",
    version=version_module.__version__,
    # Authors alphabetically last name
    author=", ".join(
        [
            "Marco Ballarin",
            "Francesco Pio Barone",
            "Alberto Coppi",
            "Daniel Jaschke",
            "Guillermo Muñoz Menés",
            "Davide Rattacaso",
            "Nora Reinić",
        ]
    ),
    author_email="quantumtea@lists.infn.it",
    description="Quantum matcha TEA python library for tensor network emulation of quantum circuits.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://baltig.infn.it/quantum_matcha_tea/py_api_quantum_matcha_tea",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={
        "qmatchatea": "qmatchatea",
        "qmatchatea.circuit": "qmatchatea/circuit",
        "qmatchatea.utils": "qmatchatea/utils",
    },
    packages=["qmatchatea", "qmatchatea.circuit", "qmatchatea.utils"],
    python_requires=">=3.11",
    install_requires=install_requires,
)
