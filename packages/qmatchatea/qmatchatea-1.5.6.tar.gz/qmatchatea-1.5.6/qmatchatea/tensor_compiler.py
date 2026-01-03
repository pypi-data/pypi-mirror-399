# This code is part of qmatchatea.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

r"""
Compiler for a qiskit quantum circuit in an optimized form for a tensor network simulator.
Since the gates are contracted with the MPS the naive structure below consists of 4
contractions with the MPS and 3 SVDs. These operations are done with
:math:`\chi\times\chi\times2` tensors, and such are computationally demanding. Instead,
we first contract all these gates together, performing at most matrix-matrix multiplications
with :math:`4\times4` matrices.

.. code-block::

    q_0 --G--G--G--G--
          |     |  |
    q_1 --G-----G--G--

We indicated with G a generic gate.

Functions and classes
---------------------

"""

from contextlib import suppress

import numpy as np
from qiskit.circuit.library import UnitaryGate
from qiskit.converters import circuit_to_dag, dag_to_circuit

from .utils.qk_utils import get_index

__all__ = ["tensor_compiler"]


# pylint: disable=too-many-boolean-expressions
def are_contractable(this, other, keep_swaps):
    """
    Check if this DagNode and the other DagNode
    are contractable, i.e. if they act on the
    same qubits

    Parameters
    ----------
    this : DagNode
        First node
    other : DagNode
        Second node

    Returns
    -------
    int
        0: they are not contractible
        1: they are contractible and acts on the
        same number of qubits
        2: they are contractible, act on different number of qubits
        and the 2nd gate in the DAG is a one-qubit gate
        3: they are contractible, act on different number of qubits
        and the 1st gate in the DAG is a one-qubit gate
    """
    if (
        (this.op.condition is not None)
        or len(this.cargs)
        or len(other.cargs)
        or (keep_swaps and (this.op.name == "swap" or other.op.name == "swap"))
    ):
        return 0

    # Same number of qubits
    if len(this.qargs) == len(other.qargs):
        if all(qq in other.qargs for qq in this.qargs):
            return 1
    # The second is a one-qubit gate
    elif len(other.qargs) == 1:
        one_qub = other.qargs[0]
        if one_qub in this.qargs:
            return 2
    # The first is a one-qubit gate
    elif len(this.qargs) == 1:
        one_qub = this.qargs[0]
        if one_qub in other.qargs:
            return 3

    return 0


def invert_qiskit_matrix(matrix):
    """
    Invert a matrix between qiskit
    and non-qiskit convention of the
    numbering.
    (qiskit orders qubit opposite to our convention,
    swap inside rows and columns)

    Parameters
    ----------
    matrix : np.ndarray, shape (4,4)
        Matrix in qiskit/non-qiskit format

    Return
    ------
    np.ndarray, shape(4, 4)
        Matrix in non-qiskit/qiskit format
    """
    # Reshape into tensor, perform correct permutation
    matrix = matrix.reshape(2, 2, 2, 2).transpose([1, 0, 3, 2])
    # Return matrix
    return matrix.reshape(4, 4)


def contract(qc, this, other, keep_swaps):
    """
    Contract this DagNode and the other DagNode
    in the quantum circuit qc

    Parameters
    ----------
    qc : QuantumCircuit
        Quantum circuit where the DagNodes are defined
    this : DagNode
        First node
    other : DagNode
        Second node

    Returns
    -------
    int
        The contraction flag
    DagNode
        The contraction of this and other
    """

    # Check if the two instructions are contractible
    flag = are_contractable(this, other, keep_swaps)

    # No contraction allowed
    if flag == 0:
        return flag, this.op

    # Contraction allowed
    this_tens = this.op.to_matrix()
    other_tens = other.op.to_matrix()
    this_qargs = [get_index(qc, qub) for qub in this.qargs]
    other_qargs = [get_index(qc, qub) for qub in other.qargs]

    # This and other have same number of qubits
    if flag == 1:
        # Two one-qubit gates
        if len(this.qargs) == 1:
            final_tens = other_tens @ this_tens

        # Two two-qubits gates
        else:
            if this_qargs[0] != other_qargs[0]:
                other_tens = invert_qiskit_matrix(other_tens)

            final_tens = other_tens @ this_tens

    # This and other acts on a different number of qubits
    elif flag == 2:
        # True if one qubit gate is on the first qubit
        gate_on_first_qub = other_qargs[0] == min(this_qargs)
        # True if the control qubit is the first
        up_down = this_qargs[0] < this_qargs[1]
        # Promote single qubit to single qubit tensor identity
        if gate_on_first_qub ^ up_down:  # Logical xor
            other_tens = np.kron(other_tens, np.eye(2, 2))
        else:
            other_tens = np.kron(np.eye(2, 2), other_tens)

        final_tens = other_tens @ this_tens

    elif flag == 3:
        # True if one qubit gate is on the first qubit
        gate_on_first_qub = this_qargs[0] == min(other_qargs)
        # True if the control qubit is the first
        up_down = other_qargs[0] < other_qargs[1]
        # Promote single qubit to single qubit tensor identity
        if gate_on_first_qub ^ up_down:  # Logical xor
            this_tens = np.kron(this_tens, np.eye(2, 2))
        else:
            this_tens = np.kron(np.eye(2, 2), this_tens)

        final_tens = other_tens @ this_tens
    else:
        raise ValueError(f"Value for flag={flag}, but not implemented.")

    return flag, UnitaryGate(final_tens)


def contract_1q_runs(qc, dag, keep_swaps):
    """
    Contract subsequent one qubit
    gates in the quantum circuit qc

    Parameters
    ----------
    qc : QuantumCircuit
        quantum circuit of interest
    dag : DagCircuit
        Dag representation of qc

    Returns
    -------
    DagCircuit
        new dag circuit with the single qubit gates
        contracted
    """
    for run in dag.collect_1q_runs():
        new_node = run[0]

        for node in run[1:]:
            flag, instr = contract(qc, new_node, node, keep_swaps)

            if flag == 1:
                dag.remove_op_node(node)
                new_node = dag.substitute_node(new_node, instr, True)
    return dag


# pylint: disable-next=multiple-statements
def contract_2q_runs(qc, dag, keep_swaps):
    """
    Contract subsequent two qubit
    gates or consecutive one and
    two qubit gates in the
    quantum circuit qc

    Parameters
    ----------
    qc : QuantumCircuit
        quantum circuit of interest
    dag : DagCircuit
        Dag representation of qc

    Returns
    -------
    DagCircuit
        new dag circuit with the two qubit gates
        contracted
    """
    for run in dag.collect_2q_runs():
        idx = 0
        while idx < len(run) - 1:
            new_node = run[idx]
            jdx = idx + 1
            while jdx < len(run):
                node = run[jdx]
                flag, instr = contract(qc, new_node, node, keep_swaps)
                # NOTE: if flag = 0, nothing changes
                with suppress(KeyError):
                    if flag in [1, 2]:
                        dag.remove_op_node(node)
                        new_node = dag.substitute_node(new_node, instr, True)
                        # update run by removing node from Python list as well
                        run.pop(jdx)
                        # recheck at same jdx, since run[jdx] is now the next node
                        continue
                    if flag == 3:
                        dag.remove_op_node(new_node)
                        new_node = dag.substitute_node(node, instr, True)
                        run.pop(idx)
                        # For now reduce idx by 1, increment idx back inside the outer loop
                        idx -= 1
                        # restart inner loop on new run[idx]
                        break
                jdx += 1
            idx += 1

    return dag


def tensor_compiler(qc, keep_swaps=False):
    """
    Compile a quantum circuit for a tensor network simulator,
    i.e. contract all two-qubit gates that are subsequent and
    acts on the same qubits

    Parameters
    ----------
    qc : QuantumCircuit
        quantum circuit to compile

    Return
    ------
    QuantumCircuit
        Compiled quantum circuit
    """
    # Represent the circuit as a directed acyclic graph
    dag = circuit_to_dag(qc)
    # Contract all subsequent 1-qubit gates
    dag = contract_1q_runs(qc, dag, keep_swaps)
    # Contract all subsequent 1-qubit and 2-qubits gate
    final_dag = contract_2q_runs(qc, dag, keep_swaps)
    # Go back to a quantum circuit
    compiled_qc = dag_to_circuit(final_dag)

    return compiled_qc
