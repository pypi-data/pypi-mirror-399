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
Utility functions to generate common quantum circuits and have
a convenient visualization of the quantum state
"""
from copy import deepcopy

import numpy as np
from qiskit.circuit import Barrier
from qiskit.quantum_info import Statevector

__all__ = ["qiskit_get_statevect", "W_qiskit", "GHZ_qiskit", "QFT_qiskit", "get_index"]


class MeasureObservables(Barrier):
    """
    Class to apply mid-circuit observables measurements with qmatchatea.

    Parameters
    ----------

    label: str
        Name of the observable. It will be used to recover the information
        at the end of the simulation.
    num_qubits: int
        Number of qubits on which the observable is defined. It should be
        the number of qubits in the quantum circuit.
    observables: TNObservables
        The observable class with the information about what you want to
        measure. The input observables will be copied, and it is thus NOT
        modified in place.
    """

    def __init__(self, label, num_qubits, observables):
        self._obs = deepcopy(observables)
        # pylint: disable-next=unexpected-keyword-arg
        super().__init__(num_qubits)
        self._name = "MeasureObservables"
        self._label = label

    @property
    def observables(self):
        """Observables property"""
        return self._obs

    @property
    def label(self):
        """Return the label of the observable"""
        return self._label

    def inverse(self, annotated: bool = False):
        """Special case. Return self."""
        return self


# pylint: disable-next=invalid-name
class qk_transpilation_params:
    """Class to contain the
    transpilation parameters used to map
    a qiskit circuit

    Parameters
    ----------
    linearize: bool, optional
        If True use qiskit transpiler to linearize the circuit. Default to True.
    basis_gates: list, optional
        If not empty decompose using qiskit transpiler into basis gate set
    optimization: integer, optional
        Level of optimization in qiskit transpiler. Default to 1. See
        https://docs.quantum.ibm.com/guides/set-optimization for more details
        about the qiskit transpiler.
    tensor_compiler: bool, optional
        If True, contract all the two-qubit gates before running the experiment.
        Default to False.
    """

    def __init__(
        self, linearize=True, basis_gates=None, optimization=1, tensor_compiler=False
    ):
        self._linearize = linearize
        self._basis_gates = [] if basis_gates is None else basis_gates
        self._optimization = optimization
        self._tensor_compiler = tensor_compiler

    @property
    def linearize(self):
        """linearize property"""
        return self._linearize

    @property
    def basis_gates(self):
        """basis_gates property"""
        return self._basis_gates

    @property
    def optimization(self):
        """optimization property"""
        return self._optimization

    @property
    def tensor_compiler(self):
        """tensor_compiler property"""
        return self._tensor_compiler


def get_index(qc, qubit):
    """
    Get the index of the qubit/bit of a quantum
    circuit.

    Parameters
    ----------
    qc : QuantumCircuit
        qiskit quantum circuit where the qubit is defined
    qubit : Qubit/Bit
        Qubit of which you want to know the index

    Returns
    -------
    int
        Index of the qubit
    """
    return qc.find_bit(qubit)[0]


def qiskit_get_statevect(qc):
    """
    Returns the statevector of the qiskit quantum circuit *qc*

    Parameters
    ----------
    qc: Quantum circuit
        Quantum circuit of which we want the statevector

    Returns
    -------
    st: array_like
        Statevector of the quantum circuit after the application
        of the reverse operation on the qubit's ordering
    """
    qc = deepcopy(qc)

    return Statevector(qc).data


def cphase_swap_qiskit(circuit, control, target, phase):
    """
    Apply to a quantum circuit *circuit* the cphase and swap gate. Acts in place.

    Parameters
    ----------
    circuit: Quantum Circuit
        Qiskit quantum circuit
    control: int
        Index of the control qubit for the controlled phase
    target: int
        Index of the target qubit for the controlled phase
    phase: double
        Phase to apply in the controlled phase in radiants

    Returns
    -------
    None: None
        Acts in place
    """
    circuit.cp(phase, control, target)
    circuit.swap(control, target)


# pylint: disable-next=invalid-name
def F_gate(circuit, kk):
    """
    Apply to a quantum circuit *circuit* the F gate, composed by Ry, CZ, Ry Acts in place.

    Parameters
    ----------
    circuit: Quantum Circuit
        Qiskit quantum circuit
    k: int
        Index of the control qubit for the controlled phase

    Returns
    -------
    None: None
        Acts in place
    """
    nn = circuit.num_qubits
    theta = np.arccos(np.sqrt(1 / (nn - kk)))
    circuit.ry(-theta, kk + 1)
    circuit.cz(kk + 1, kk)
    circuit.ry(theta, kk + 1)


# pylint: disable-next=invalid-name
def QFT_qiskit(circuit, nn):
    """
    Apply the QFT to a qiskit quantum circuit *circuit* in a recursive way

    Parameters
    ----------
        circuit : quantum circuit
            quantum circuit where we want to apply the QFT
        nn       : int
            number of qubits in *circuit*

    Returns
    -------
        None: None
                Acts in place
    """
    # pylint: disable-next=no-else-return
    if nn == 0:
        return circuit
    elif nn == 1:
        circuit.h(0)
        return circuit

    circuit.h(0)
    for ii in range(nn - 1):
        cphase_swap_qiskit(circuit, ii, ii + 1, np.pi * 1 / 2 ** (ii + 1))

    return QFT_qiskit(circuit, nn - 1)


# pylint: disable-next=invalid-name
def GHZ_qiskit(circ):
    """
    Generates a GHZ state in the quantum circuit *circ* composed by n qubits. Acts in place.

    Parameters
    ----------
    circ: Quantum Circuit
        The quantum circuit in the state '00...0' where to build the GHZ

    Returns
    -------
    None: None
        Acts in place.
    """
    nn = circ.num_qubits
    circ.h(0)
    for ii in range(1, nn):
        circ.cx(ii - 1, ii)


# pylint: disable-next=invalid-name
def W_qiskit(circ):
    """
    Generates a W state in the quantum circuit *circ* composed by n qubits. Acts in place.

    Parameters
    ----------
    circ: Quantum Circuit
        The quantum circuit in the state '00...0' where to build the W

    Returns
    -------
    None: None
        Acts in place.
    """
    nn = circ.num_qubits
    circ.x(0)
    for ii in range(nn - 1):
        F_gate(circ, ii)
        circ.barrier()

    for ii in range(nn - 1):
        circ.cx(ii + 1, ii)
        circ.barrier()
