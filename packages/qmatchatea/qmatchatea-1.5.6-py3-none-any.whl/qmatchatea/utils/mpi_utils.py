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
Function to help in the MPI protocol. Here you insert barriers, which means
canonization of the state each `where_barriers` layers. In particular, it is
important because at each layer in the circuit description is connected a
canonization in the MPS simulation. If the canonization are not often enough
the simulation might not converge.

Functions and classes
---------------------

"""

# pylint: disable=ungrouped-imports, too-many-arguments

import numpy as np
from qiskit import QuantumCircuit

try:
    from qiskit.visualization.utils import _get_layered_instructions
except ImportError:
    # This try except makes the code compatible also with the latest version of
    # qiskit, where the _get_layered_instructions changed path
    from qiskit.visualization.circuit._utils import _get_layered_instructions

__all__ = ["MPISettings", "to_layered_circ"]


class MPISettings:
    """
    Settings for using the library on multiple processes using MPI.
    The default settings use no MPI, i.e. a serial execution of the algorithm.

    Parameters
    ----------
    mpi_approach: str, optional
        Approach for the MPI simulation.
        Available:
        - "SR": serial, the algorithm is run serially on the TN ansatz
        - "CT": cartesian, the MPS is divided between different processes,
                and the algorithm is done in parallel. MPS ONLY.
        Default to "SR".
    isometrization: int | List[int], optional
        How to perform the isometrization.
        - `-1` is a serial isometrization step
        - A `int` is a parallel isometrization step with that number of layers
        - A `List[int]` is a parallel isometrization step where each entry is
          the number of layers for the `i`-th isometrization. If the number of
          isometrization steps is greater than the length of the array, the array
          is repeated.
        Default to `-1`
    num_procs: int, optional
        Number of processes for the MPI simulation. Default to 1.
    mpi_command : List[str], optional
        MPI command that should be called when launching MPI.
        The "-n" for the number of processes is already taken into account.
        Default to ["mpi_exec"].
    where_barriers: int, optional
        This parameter is important only if you want to use MPI parallelization.
        If where_barriers > 0 then the circuit gets ordered in layers and a barrier is applyed
        each where_barriers layers. We recall that a barrier is equivalent to a canonization in
        the MPS simulation. Default to -1.

    """

    def __init__(
        self,
        mpi_approach="SR",
        isometrization=-1,
        num_procs=1,
        mpi_command=None,
        where_barriers=-1,
    ):
        self.num_procs = num_procs
        self.mpi_approach = mpi_approach.upper()
        self.isometrization = isometrization
        if mpi_command is None:
            mpi_command = ["mpiexec"]
        self.mpi_command = list(mpi_command)
        self.where_barriers = where_barriers

    def __getitem__(self, idx):
        """
        Get the settings of the isometrization for the idx-th isometrization
        """
        if np.isscalar(self.isometrization):
            return self.isometrization

        return self.isometrization[idx % len(self.isometrization)]

    def print_isometrization_type(self, idx):
        """
        print which type of isometrization we have at index idx

        Parameters
        ----------
        idx : int
            Index of the isometrization
        """

        iso_type = self[idx]
        if iso_type < 0:
            print(f"At step {idx} serial isometrization")
        else:
            print(f"At step {idx} parallel isometrization with {iso_type} layers")


def _to_layered_circ_qk(qc, where_barriers=1):
    """
    Transform a quantum circuit in another, where the instruction are ordered by layers.
    Apply a barrier every where_barriers layers.

    Parameters
    ----------
    qc: qiskit.QuantumCircuit
        Quantum circuit
    where_barriers: int
        Apply a barrier every where_barriers layers.

    Returns
    -------
    layered_qc: qiskit.QuantumCircuit
            Ordered quantum circuit with barriers
    """
    layered_qc = QuantumCircuit(qc.num_qubits)

    layered_instructions = _get_layered_instructions(qc)[2]
    for ii, layer in enumerate(layered_instructions):
        for instruction in layer:
            layered_qc.append(instruction.op, instruction.qargs, instruction.cargs)
        if ii % where_barriers == 0:
            layered_qc.barrier()

    return layered_qc


def to_layered_circ(circ, where_barriers=1):
    """
    Interface for the transformation of qiskit circuit
    into layered ones, the correct order for the MPI protocols.
    You also insert barriers, i.e. canonization procedures

    Parameters
    ----------
    circ: qiskit.circuit.quantumcircuit.QuantumCircuit
        Quantum circuit instance
    where_barriers: int
        Apply a barrier every where_barriers layers.

    Returns
    -------
    layered_circ: qiskit.circuit.quantumcircuit.QuantumCircuit
        Ordered circuit program with barriers
    """

    if isinstance(circ, QuantumCircuit):
        layered_circ = _to_layered_circ_qk(circ, where_barriers)
    else:
        raise TypeError(
            "Only qiskit quantum circuit is implemented. Your circuit is of type:"
            + str(type(circ))
        )

    return layered_circ
