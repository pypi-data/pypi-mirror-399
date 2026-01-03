# This code is part of qmatchatea.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Backend of the simulation controlling:

- Precision
- Device
- Tensor network ansatz
- Settings for the MPI (if any)
- Tensor class used in the simulation
"""
import importlib
import json
import os
from typing import OrderedDict

from qtealeaves.tensors.tensor import GPU_AVAILABLE

from .mpi_utils import MPISettings

__all__ = ["QCBackend"]

# pylint: disable=too-many-arguments


class QCBackend:
    """
    Backend for the simulation. Contains all the informations about
    which executable you want to run.

    Parameters
    ----------
    precision: str, optional
        Precision of the simulation.
        Select a real precision ONLY if you use ONLY real gates.
        Available:
        - "A": automatic. For the heuristic see `self.resolve_precision`.
        - "Z": double precision complex;
        - "C": single precision complex;
        - "D": double precision real;
        - "S": single precision real.
        Default to "A".
    device: str, optional
        Device of the simulation.
        Available:
        - "A" : automatic. For the heuristic see `self.resolve_device`
        - "cpu": use the cpu
        - "gpu": use the gpu if it is available
        - "cpu+gpu": use the device-mixed mode (if gpu is available)
        Default to "A".
    ansatz : str, optional
        Whether to run the circuit with MPS or TTN tensor network ansatz.
        Default to "MPS".
    mpi_settings : MPISettings | None, optional
        Settings for running the simulation multi-node.
        Default to None, i.e. no MPI.
    tensor_module : str, optional
        Module used to perform the computations. Available:
        - `"numpy"` (Default, uses cupy for the GPU)
        - `"torch"`, uses pytorch;
        - `"tensorflow"`
        - `"jax"`.
        Default to `"numpy"`
    """

    def __init__(
        self,
        precision="A",
        device="cpu",
        ansatz="MPS",
        mpi_settings=None,
        tensor_module="numpy",
    ):
        self._precision = precision.upper()
        self._device = device
        self._ansatz = ansatz.upper()
        self.mpi_settings = MPISettings() if mpi_settings is None else mpi_settings
        self.tensor_module = tensor_module.lower()

        if importlib.util.find_spec(self.tensor_module) is None:
            raise ValueError(f"Module {self.tensor_module} is not installed.")

    def to_dict(self):
        """
        Map the backend to a dictionary.
        """

        dictionary = OrderedDict({})
        mpi = "T" if self.num_procs > 1 else "F"
        gpu = "T" if self.device == "gpu" else "F"
        dictionary["simulation_mode"] = self.precision + mpi + gpu
        dictionary["approach"] = self.mpi_approach

        return dictionary

    def resolve_precision(self, min_fidelity, tol=1e-7):
        """
        Resolve the precision of the simulation.
        Heuristic if `self._precision="A"`.

        Parameters
        ----------
        min_fidelity: float
            Lower bound of the fidelity of the simulation at the moment
        tol: float, optional
            Tolerance after which you switch to single precision.
            Default to 1e-7

        Returns
        -------
        str
            The selected precision
        """
        if self._precision != "A":
            return self.precision

        # The lower bound of the fidelity of our state is
        # below the number of digits of a single
        # precision
        if 1 - min_fidelity > tol:
            return "C"

        return "Z"

    def resolve_device(self, bond_dimension, previous_device, exp_gpu=7):
        """
        Resolve the device if it set on automatic.

        Parameters
        ----------
        bond_dimension : int
            Maximum bond dimension of the system
        previous_device : str
            Device where the system is currently. This is used
            to ensure we do not keep exchanging data back and
            forth.
        exp_gpu : int, optional
            Exponent of the bond dimension after which you switch
            to the gpu, i.e:
            - if chi >= 2**exp_gpu -> use gpu
            - if chi <= 2**(exp_gpu-1) -> use cpu
            Default to 7. (switch at 128)

        Returns
        -------
        str
            Device where to move (or keep) the system
        """
        if self._device != "A":
            return self._device

        if bond_dimension >= 2**exp_gpu and GPU_AVAILABLE:
            return "gpu"
        # The condition on the CPU is here because we want
        # to avoid keep exchanging informations if the bond
        # dimension oscillates between 129 and 120
        if bond_dimension <= 2 ** (exp_gpu - 1):
            return "cpu"

        return previous_device

    @property
    def where_barriers(self):
        """
        This parameter is important only if you want to use MPI parallelization,
        where a barrier is equivalent to a canonization in the MPS simulation.
        Default to -1.
        """
        return self.mpi_settings.where_barriers

    @property
    def precision(self):
        """Precision property"""
        return self._precision

    @property
    def device(self):
        """Device property"""
        return self._device

    @property
    def num_procs(self):
        """Number of processes property"""
        return self.mpi_settings.num_procs

    @property
    def mpi_approach(self):
        """mpi_approach property (inherited from `mpi_settings`)"""
        return self.mpi_settings.mpi_approach.upper()

    @property
    def ansatz(self):
        """ansatz property"""
        return self._ansatz

    @property
    def mpi_command(self):
        """mpi_command property"""
        return self.mpi_settings.mpi_command

    @property
    def identifier(self):
        """Identifier combining all properties."""
        return ":".join(
            [
                self.resolve_precision(1),
                self.resolve_device(1, "cpu"),
                str(self.num_procs),
                self.mpi_approach,
                self.ansatz,
            ]
        )

    def to_json(self, path):
        """
        Write the class as a json on file as
        backend.json in the folder path
        """
        path = os.path.join(path, "backend.json")
        dictionary = OrderedDict()
        dictionary["device"] = self.device
        dictionary["precision"] = self.precision
        dictionary["num_procs"] = self.num_procs
        dictionary["ansatz"] = self.ansatz
        dictionary["mpi_approach"] = self.mpi_approach
        dictionary["mpi_command"] = self.mpi_command

        with open(path, "w") as fhandle:
            json.dump(dictionary, fhandle, indent=4)

    @classmethod
    def from_json(cls, path):
        """
        Initialize the class from a json file called
        "backend.json" in the folder path
        """
        path = os.path.join(path, "backend.json")
        with open(path, "r") as fhandle:
            dictionary = json.load(fhandle)[0]

        return cls(**dictionary)
