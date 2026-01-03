# This code is part of qmatchatea.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import os
import os.path
import sys
import unittest
from shutil import rmtree

import numpy as np

# Try to import cupy
try:
    import cupy as cp
    from cupy_backends.cuda.api.runtime import CUDARuntimeError

    try:
        _ = cp.cuda.Device()
        GPU_AVAILABLE = True
    except CUDARuntimeError:
        GPU_AVAILABLE = False
except ImportError:
    cp = None
    GPU_AVAILABLE = False

from qiskit import ClassicalRegister, QuantumCircuit, transpile, transpiler
from qiskit.circuit.library import QuantumVolume
from qtealeaves.observables import TNObservables, TNObsProjective, TNState2File

from qmatchatea import QCBackend, run_simulation
from qmatchatea.circuit import Qcircuit
from qmatchatea.utils import QCIO, QCConvergenceParameters, fidelity
from qmatchatea.utils.mpi_utils import to_layered_circ
from qmatchatea.utils.qk_utils import (
    GHZ_qiskit,
    W_qiskit,
    qiskit_get_statevect,
    qk_transpilation_params,
)

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
    qc = QuantumVolume(num_qub)
    qc = qc.decompose()
    lin_map = transpiler.CouplingMap.from_line(num_qub)
    qc = transpile(qc, coupling_map=lin_map, basis_gates=avail_gates)
    qc = to_layered_circ(qc)
    # qc.add_register(creg)

    return qc


class TestBasicCircuits(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir("TMP_TEST"):
            os.makedirs("TMP_TEST")
        self.qcio = QCIO("TMP_TEST/data/in", "TMP_TEST/data/out")
        self.backends = self.get_python_backends()
        self.obs = TNObservables()
        self.obs += TNObsProjective(16)
        self.obs += TNState2File("TMP_TEST/data/out/statevector.txt", "F")
        np.random.seed(123)

    @staticmethod
    def get_python_backends():
        """
        Generate all possible backends for python.
        """
        backends = (
            {
                "precision": "C",
                "device": "cpu",
                "ansatz": "MPS",
            },
            {
                "precision": "Z",
                "device": "cpu",
                "ansatz": "MPS",
            },
            {
                "precision": "C",
                "device": "cpu",
                "ansatz": "TTN",
            },
            {
                "precision": "Z",
                "device": "cpu",
                "ansatz": "TTN",
            },
            {
                "precision": "C",
                "device": "gpu",
                "ansatz": "MPS",
            },
            {
                "precision": "Z",
                "device": "gpu",
                "ansatz": "MPS",
            },
        )

        if GPU_AVAILABLE:
            pass
        else:
            backends = (backends[0], backends[1], backends[2], backends[3])

        backends = [QCBackend(**elem) for elem in backends]

        return backends

    def tearDown(self):
        if os.path.isdir("TMP_TEST"):
            rmtree("TMP_TEST")
        return

    def test_GHZ(self):
        """
        Check that the GHZ circuit is reproduced correctly
        """
        for backend in self.backends:
            num_qubits = 8
            qc = QuantumCircuit(num_qubits)
            GHZ_qiskit(qc)
            true_state = qiskit_get_statevect(qc)
            res = run_simulation(
                qc, io_info=self.qcio, backend=backend, observables=self.obs
            )
            statevect = res.statevector
            fid = fidelity(statevect, true_state)
            self.assertAlmostEqual(
                fid, 1, places=12, msg="GHZ state not described correctly"
            )

        return

    def test_GHZ_qcircuit(self):
        """
        Check that the GHZ circuit is reproduced correctly
        """
        num_qubits = 8
        true_state = np.zeros(2**num_qubits)
        true_state[[0, -1]] = 1 / np.sqrt(2)
        for backend in self.backends:
            qc = Qcircuit(num_qubits)
            qc.h(0)
            for ii in range(0, num_qubits - 1):
                qc.cx([ii, ii + 1])
            res = run_simulation(
                qc, io_info=self.qcio, backend=backend, observables=self.obs
            )
            statevect = res.statevector
            fid = fidelity(statevect, true_state)
            self.assertAlmostEqual(
                fid, 1, places=12, msg="GHZ state not described correctly with Qcircuit"
            )

        return

    def test_W(self):
        """
        Check that the W circuit is reproduced correctly
        """
        for backend in self.backends:
            num_qubits = 8
            qc = QuantumCircuit(num_qubits)
            W_qiskit(qc)
            true_state = qiskit_get_statevect(qc)
            res = run_simulation(
                qc, io_info=self.qcio, backend=backend, observables=self.obs
            )
            statevect = res.statevector
            fid = fidelity(statevect, true_state)
            self.assertAlmostEqual(
                fid, 1, places=12, msg="W state not described correctly"
            )

        return

    def test_QVOLUME(self):
        """
        Check that the QVOLUME circuit is reproduced correctly
        """
        for backend in self.backends:
            approach = backend.identifier

            num_qubits = 8
            transpilation_params = qk_transpilation_params(linearize=True)
            convergence_params = QCConvergenceParameters(max_bond_dimension=50)
            qc = qvol_circ(num_qubits)
            true_state = qiskit_get_statevect(qc)
            res = run_simulation(
                qc,
                convergence_parameters=convergence_params,
                io_info=self.qcio,
                transpilation_parameters=transpilation_params,
                backend=backend,
                observables=self.obs,
            )
            statevect = res.statevector
            fid = fidelity(statevect, true_state)
            tol_places = 12 if (backend.precision == "Z") else 5
            self.assertAlmostEqual(
                fid,
                1,
                places=tol_places,
                msg=f"QVOLUME state not described correctly with {approach}.",
            )

        return
