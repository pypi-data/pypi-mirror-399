[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

# Quantum Matcha Tea

Quantum Matcha Tea is a Tensor Network emulator for quantum circuits and linear optics circuits.
You can define your circuits either in [qiskit](https://github.com/Qiskit), or using Matcha's internal circuit interface `Qcircuit`.

If you use another quantum information library (such as [cirq](https://quantumai.google/cirq)) we suggest to save your circuit in `qasm`
format and then load it in qiskit.

The circuits ca be ran using the following backends:

- [numpy](https://numpy.org/), using the CPU in python;
- [cupy](https://cupy.dev/), using the GPU in python.

## Documentation

[Here](https://quantum_matcha_tea.baltig-pages.infn.it/py_api_quantum_matcha_tea) is the documentation.
The documentation can also be built locally with sphinx with the following python packages:

- `sphinx`
- `sphinx_rtd_theme`

and running the command `make html` in the `docs/` folder.

## Installation

Independent of the use-case, you have to install the dependencies. 
Installing the optional dependencies will enable the use of more 
tensor modules (for instance, supporting GPUs).

### Installation via pip

The package is available via PyPi and `pip install qmatchatea`.
After cloning the repository, a local installation via pip is
also possible via `pip install .`.

### Optional dependencies

The following optional dependencies are not installed by default.

- `cupy`: necessary to run on the GPU with the `tensor_module="numpy"`. The installation guide can be found
  at the [cupy website](https://docs.cupy.dev/en/stable/install.html).
- `torch`: necessary to run simulation with the `tensor_module="torch"`. The installation guide can be found
  at the [pytorch website](https://pytorch.org/get-started/locally/).
- `tensorflow`: necessary to run simulation with the `tensor_module="tensorflow"`. The installation guide can be found
  at the [tensorflow website](https://www.tensorflow.org/install).
- `jax`: necessary to run simulation with the `tensor_module="jax"`. The installation guide can be found
  at the [jax website](https://jax.readthedocs.io/en/latest/installation.html).

MPI simulations also require the package [`mpi4py`](https://mpi4py.readthedocs.io/en/stable/).

## Testing the package

To test the python package `qmatchatea` simply run from the command:
``
python3 -m unittest
``

## License

The project `qmatchatea` from the repository `py_api_quantum_matcha_tea`
is licensed under the following license:

[Apache License 2.0](LICENSE)

The license applies to the files of this project as indicated
in the header of each file, but not its dependencies.
