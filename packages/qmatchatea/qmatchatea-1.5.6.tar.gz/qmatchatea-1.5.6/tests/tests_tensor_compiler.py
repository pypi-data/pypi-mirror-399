# This code is part of qmatchatea.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import sys
import unittest

import numpy as np
from qiskit import QuantumCircuit, transpile, transpiler
from qiskit.circuit.library import QuantumVolume

from qmatchatea import tensor_compiler
from qmatchatea.preprocessing import preprocess, qk_transpilation_params
from qmatchatea.utils.qk_utils import GHZ_qiskit, W_qiskit, qiskit_get_statevect
from qmatchatea.utils.utils import fidelity

sys.argv = [""]
avail_gates = [
    "x",
    "y",
    "z",
    "h",
    "id",
    "s",
    "sdg",
    "sx",
    "sxdg",
    "t",
    "tdg",
    "swap",
    "dcx",
    "ecr",
    "iswap",
    "ch",
    "cx",
    "cy",
    "cz",
    "p",
    "r",
    "rx",
    "ry",
    "rz",
    "u",
    "u1",
    "u2",
    "rxx",
    "ryy",
    "rzx",
    "rzz",
    "cp",
    "cry",
    "crz",
    "cu",
    "cu1",
]


def qvol_circ(num_qub=3):
    """
    Using a CouplingMap shuffles the wires of the circuit to maintain nearest neighbour gates; difficult
    for the tensor compiler to track the wires

    Using the preprocess function linearizes the circuit without shuffling the wires which makes
    it possible for the tensor compiler to keep track while removing and substituting nodes

    """

    qc = QuantumVolume(num_qub)
    qc = qc.decompose().decompose()
    qc = preprocess(qc, qk_params=qk_transpilation_params(basis_gates=avail_gates))

    return qc


class TestTensorCompiler(unittest.TestCase):
    def setUp(self):
        np.random.seed(123)

    def test_GHZ(self):
        """
        Check that the GHZ circuit is compiled correctly
        """
        num_qubits = 10
        qc = QuantumCircuit(num_qubits)
        GHZ_qiskit(qc)
        true_state = qiskit_get_statevect(qc)
        compiled_qc = tensor_compiler(qc)
        statevect = qiskit_get_statevect(compiled_qc)
        fid = fidelity(statevect, true_state)
        self.assertAlmostEqual(
            fid, 1, places=12, msg="GHZ state not compiled correctly"
        )

        return

    def test_W(self):
        """
        Check that the W circuit is compiled correctly
        """
        num_qubits = 10
        qc = QuantumCircuit(num_qubits)
        W_qiskit(qc)
        true_state = qiskit_get_statevect(qc)
        compiled_qc = tensor_compiler(qc)
        statevect = qiskit_get_statevect(compiled_qc)
        fid = fidelity(statevect, true_state)
        self.assertAlmostEqual(fid, 1, places=12, msg="W state not compiled correctly")

        return

    def test_QVOLUME(self):
        """
        Check that the QVOLUME circuit is compiled correctly
        """
        num_qubits = 10
        qc = qvol_circ(num_qubits)
        true_state = qiskit_get_statevect(qc)
        compiled_qc = tensor_compiler(qc)
        statevect = qiskit_get_statevect(compiled_qc)
        fid = fidelity(statevect, true_state)
        self.assertAlmostEqual(
            fid, 1, places=12, msg=f"QVOLUME state not compiled correctly"
        )

        return
