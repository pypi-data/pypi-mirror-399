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

from qiskit import QuantumCircuit
from qtealeaves.observables import TNObservables, TNObsTensorProduct, TNObsWeightedSum

from qmatchatea import QCBackend, QCOperators, run_simulation
from qmatchatea.utils import QCIO
from qmatchatea.utils.qk_utils import GHZ_qiskit, W_qiskit

sys.argv = [""]


class TestObservables(unittest.TestCase):
    def setUp(self):
        if not os.path.isdir("TMP_TEST"):
            os.makedirs("TMP_TEST")
        self.qcio = QCIO("TMP_TEST/data/in", "TMP_TEST/data/out")
        self.backends = self.get_python_backends()

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

    def test_TensorProductOnGHZ(self):
        """
        Test the evaluation of TP observables on GHZ state
        """
        for backend in self.backends:
            approach = backend.identifier

            num_qubits = 16
            qc = QuantumCircuit(num_qubits)
            GHZ_qiskit(qc)

            obs = TNObservables("observables.dat")
            ztp = TNObsTensorProduct(
                "Ztp",
                ["Z" for i in range(num_qubits)],
                [[i] for i in range(num_qubits)],
            )
            xtp = TNObsTensorProduct(
                "Xtp",
                ["X" for i in range(num_qubits)],
                [[i] for i in range(num_qubits)],
            )
            zsingle = TNObsTensorProduct("Zsingle", ["Z"], [[1]])

            obs += xtp
            obs += ztp
            obs += zsingle

            operators = QCOperators()

            res = run_simulation(
                qc,
                io_info=self.qcio,
                observables=obs,
                operators=operators,
                backend=backend,
            )

            obs_res = res.observables
            places = 12 if backend.precision in ("Z", "D") else 5

            self.assertAlmostEqual(
                obs_res["Ztp"],
                1,
                places=places,
                msg=f"Tensor product of ZZ...Z has value 1 on even number of qubits",
            )
            self.assertAlmostEqual(
                obs_res["Xtp"],
                1,
                places=places,
                msg=f"Tensor product of XX...X has value 1",
            )
            self.assertAlmostEqual(
                obs_res["Zsingle"],
                0,
                places=places,
                msg=f"Single Z on second site has value 0",
            )

        return

    def test_TensorProductOnW(self):
        """
        Test the evaluation of TP observables on W state
        """
        for backend in self.backends:
            num_qubits = 16
            qc = QuantumCircuit(num_qubits)
            W_qiskit(qc)

            obs = TNObservables("observables.dat")
            ztp = TNObsTensorProduct(
                "Ztp",
                ["Z" for i in range(num_qubits)],
                [[i] for i in range(num_qubits)],
            )
            xtp = TNObsTensorProduct(
                "Xtp",
                ["X" for i in range(num_qubits)],
                [[i] for i in range(num_qubits)],
            )
            zsingle = TNObsTensorProduct("Zsingle", ["Z"], [[1]])

            obs += xtp
            obs += ztp
            obs += zsingle

            operators = QCOperators()

            res = run_simulation(
                qc,
                io_info=self.qcio,
                observables=obs,
                operators=operators,
                backend=backend,
            )

            obs_res = res.observables

            places = 12 if backend.precision in ("Z", "D") else 5
            self.assertAlmostEqual(
                obs_res["Ztp"],
                -1,
                places=places,
                msg="Tensor product of ZZ...Z has value 0 on even number of qubits",
            )
            self.assertAlmostEqual(
                obs_res["Xtp"],
                0,
                places=places,
                msg="Tensor product of XX...X has value 1",
            )

        return

    def test_WeightedSumOnGHZ(self):
        """
        Test the evaluation of WS observables on GHZ state
        """
        for backend in self.backends:
            num_qubits = 16
            qc = QuantumCircuit(num_qubits)
            GHZ_qiskit(qc)

            obs = TNObservables("observables.dat")
            ztp = TNObsTensorProduct(
                "Ztp",
                ["Z" for i in range(num_qubits - 1)],
                [[i] for i in range(num_qubits - 1)],
            )
            xtp = TNObsTensorProduct(
                "Xtp",
                ["X" for i in range(num_qubits)],
                [[i] for i in range(num_qubits)],
            )

            xx = TNObsWeightedSum("X", xtp, [2], use_itpo=False)
            zz = TNObsWeightedSum("Z", ztp, [3], use_itpo=False)

            obs += xx
            obs += zz

            operators = QCOperators()

            res = run_simulation(
                qc,
                io_info=self.qcio,
                observables=obs,
                operators=operators,
                backend=backend,
            )

            obs_res = res.observables

            places = 12 if backend.precision in ("Z", "D") else 4
            self.assertAlmostEqual(
                obs_res["Z"],
                0,
                places=places,
                msg="Tensor product of ZZ...Z has value 0 on odd number of qubits",
            )
            self.assertAlmostEqual(
                obs_res["X"],
                2,
                places=places,
                msg="Tensor product of XX...X is correct",
            )

        return

    def test_WeightedFromPauli(self):
        """
        Test the evaluation of WS observables on GHZ state
        """
        for backend in self.backends:
            if backend.ansatz == "MPS":
                continue
            num_qubits = 16
            qc = QuantumCircuit(num_qubits)
            GHZ_qiskit(qc)

            obs = TNObservables("observables.dat")
            pauli_dict = {
                "paulis": [
                    {"label": "X" * num_qubits, "coeff": {"real": 1, "imag": 0}},
                    {"label": "Z" * (num_qubits - 1), "coeff": {"real": 1, "imag": 0}},
                ]
            }

            obsw = TNObsWeightedSum.from_pauli_string(
                "test", pauli_dict, use_itpo=False
            )
            obs += obsw

            operators = QCOperators()

            res = run_simulation(
                qc,
                io_info=self.qcio,
                observables=obs,
                operators=operators,
                backend=backend,
            )

            obs_res = res.observables

            places = 12 if backend.precision in ("Z", "D") else 5
            self.assertAlmostEqual(
                obs_res["test"],
                1,
                places=places,
                msg="Tensor product of ZZ...Z + XX...X has value 0 on odd number of qubits",
            )

        return

    def test_WeightedSumOnW(self):
        """
        Test the evaluation of WS observables on W state
        """
        for backend in self.backends:
            num_qubits = 16
            qc = QuantumCircuit(num_qubits)
            W_qiskit(qc)

            obs = TNObservables("observables.dat")
            ztp = TNObsTensorProduct(
                "Ztp",
                ["Z" for i in range(num_qubits)],
                [[i] for i in range(num_qubits)],
            )
            xtp = TNObsTensorProduct(
                "Xtp",
                ["X" for i in range(num_qubits)],
                [[i] for i in range(num_qubits)],
            )

            xx = TNObsWeightedSum("X", xtp, [2])
            zz = TNObsWeightedSum("Z", ztp, [3])
            obs += xx
            obs += zz

            operators = QCOperators()

            res = run_simulation(
                qc,
                io_info=self.qcio,
                observables=obs,
                operators=operators,
                backend=backend,
            )

            obs_res = res.observables

            places = 12 if backend.precision in ("Z", "D") else 5
            self.assertAlmostEqual(
                obs_res["Z"],
                -3,
                places=places,
                msg="Tensor product of ZZ...Z is correct",
            )
            self.assertAlmostEqual(
                obs_res["X"],
                0,
                places=places,
                msg="Tensor product of XX...X is correct",
            )

        return
