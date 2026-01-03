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
In order to simulate the quantum circuit we first need to preprocess it, to put it in a way
suitable for the MPS simulation.

Preprocessing
~~~~~~~~~~~~~

The tensor network ansatz that is used in the simulator is called Matrix Product States (MPS).
In this ansatz each degree of freedom (qubit, mode, particle) is treated as a rank-3 tensor.
We can only apply operators which are **local** or that applies to **nearest neighbors**.
This means that, when a circuit is passed to the preprocessing it is translated in an equivalent
circuit that follows these two properties. While for quantum optics these properties are already
ensured, for qubits quantum circuit we have to perform some transformations. We use qiskit for them,
and in particular we:

- Map the circuit using a pre-defined set of gates, called basis_gates.
  These gates can be passed to the function, to satisfy
  a particular constraint of a physical machine we want to simulate
- Map the circuit into a linear circuit. By an optimized application of *swap*
  gates we map non-local two-qubit gates into a series
  of local two-qubit gates.

These operations are automatically performed by the higher level function :py:func:`run_simulation`.
However, it is important to take into account that these operations require time, which is
proportional to the size of the circuit. For this reason, if the user has to perform multiple
simulation of the same circuit varing other parameres, e.g. the bond dimension, it is suggested to
perform the preprocessing only once, and then disable the mapping and the linearization of the
function.

.. warning::
    The preprocessing and linearization using qiskit modifies the order of the qubits.
    This is a behavior we don't want to experience, and such inside the preprocessing
    procedure the qubits are again ordered in the initial layout.

"""

from qiskit import QuantumCircuit, transpile, transpiler

from .tensor_compiler import tensor_compiler
from .utils.qk_utils import get_index, qk_transpilation_params

__all__ = ["preprocess"]


def _bubble_sort(nums):
    """Given an integer array sort it by only swapping nearest neighbors elements,
        and return the necessary swaps to bring the array into sorted shape

    Parameters
    ----------
    nums : list of int
        Array of integer to be sorted in ascendant order

    Returns
    -------
    swaps : list of tuples of int
        Indexes of the qubits that has to be swapped
    """
    # We set swapped to True so the loop looks runs at least once
    swapped = True
    swaps = []
    while swapped:
        swapped = False
        for ii in range(len(nums) - 1):
            if nums[ii] > nums[ii + 1]:
                # Swap the elements
                nums[ii], nums[ii + 1] = nums[ii + 1], nums[ii]
                # Set the flag to True so we'll loop again
                swapped = True
                swaps.append((ii, ii + 1))
    return swaps


def _reorder_qk(linearized_qc):
    """Qiskit transpiler does not control the final layout of the qubits, i.e.
        we don't know if they are ordered correctly. It takes care of this problem
        by rearrenging the measurements on the classical register. However, it is
        a problem for the mps simulator. We so reorder the qubit register by applying
        swap gates.

    Parameters
    ----------
    linearized_qc : :py:class:`qiskit.QuantumCircuit`
        Circuit linearized trhough the qiskit transpiler

    Returns
    -------
    linearized_qc : :py:class:`qiskit.QuantumCircuit`
        Circuit with the correct ending qubits
    """
    num_qub = linearized_qc.num_qubits
    # Read the final layout by the rearrengement of the measurements
    final_perm = [0] * num_qub
    for instruction in linearized_qc.data[linearized_qc.size() - num_qub + 1 :]:
        if instruction.operation.name == "measure":
            final_perm[get_index(linearized_qc, instruction.qubits[0])] = get_index(
                linearized_qc, instruction.clbits[0]
            )
    # Get the combination of swaps necessary trhough the bubble_sort algorithm,
    # which is O(num_qub^2)
    swaps = _bubble_sort(final_perm)
    # Perform the swapping operations
    linearized_qc.remove_final_measurements()
    for ii, jj in swaps:
        linearized_qc.swap(ii, jj)

    return linearized_qc


def _preprocess_qk(qc, qk_params=qk_transpilation_params()):
    """Transpile the circuit to adapt it to the linear structure of the MPS, with the constraint
    of having only the gates basis_gates

     Parameters
    ----------
    qc: QuantumCircuit
         qiskit quantum circuit
    linearize: bool, optional
        If True use qiskit transpiler to linearize the circuit. Default to True.
    basis_gate: list, optional
        If not empty decompose using qiskit transpiler into basis gate set
    optimization: intger, optional
        Level of optimization in qiskit transpiler. Default to 3.

    Returns
    -------
    linear_qc: QuantumCircuit
        Linearized quantum circuit
    """
    # Empty circuit case
    if len(qc.data) == 0:
        return qc
    basis_gates = [] if qk_params.basis_gates is None else qk_params.basis_gates
    n_qub = qc.num_qubits
    linear_map = transpiler.CouplingMap.from_line(n_qub)
    # Assure that final measurements are present, by first eliminating and adding them
    qc.remove_final_measurements()
    qc.measure_all()
    # Transpile the circuit
    if len(basis_gates) > 0 and qk_params.linearize:
        linear_qc = transpile(
            qc,
            coupling_map=linear_map,
            optimization_level=qk_params.optimization,
            basis_gates=basis_gates,
            initial_layout=list(range(n_qub)),
        )
    elif len(basis_gates) == 0 and qk_params.linearize:
        linear_qc = transpile(
            qc,
            coupling_map=linear_map,
            optimization_level=qk_params.optimization,
            initial_layout=list(range(n_qub)),
        )
    elif len(basis_gates) > 0:
        linear_qc = transpile(
            qc,
            optimization_level=qk_params.optimization,
            basis_gates=basis_gates,
            initial_layout=list(range(n_qub)),
        )
    else:
        linear_qc = qc

    # Reorder the circuit
    linear_qc = _reorder_qk(linearized_qc=linear_qc)

    # Use the tensor compiler if requested
    if qk_params.tensor_compiler:
        linear_qc = tensor_compiler(linear_qc)

    return linear_qc


def preprocess(circ, **kwargs):
    """
    Interface for the preprocessing of qiskit circuits

    Parameters
    ----------
    circ: qiskit.circuit.quantumcircuit.QuantumCircuit
        Quantum circuit instance
    **kwargs:
        linearize: bool, optional
            If True use qiskit transpiler to linearize the circuit. Default to True.
        basis_gate: list, optional
            If not empty decompose using qiskit transpiler into basis gate set
        optimization: integer, optional
            Level of optimization in qiskit transpiler. Default to 3.

    Returns
    -------
    preprocessed_circ: qiskit.circuit.quantumcircuit.QuantumCircuit
        Preprocessed quantum circuit instance
    """

    if isinstance(circ, QuantumCircuit):
        preprocessed_circ = _preprocess_qk(circ, **kwargs)

    else:
        raise TypeError(
            "Only qiskit quantum circuit are implemented. Your circuit is of type:"
            + str(type(circ))
        )

    return preprocessed_circ
