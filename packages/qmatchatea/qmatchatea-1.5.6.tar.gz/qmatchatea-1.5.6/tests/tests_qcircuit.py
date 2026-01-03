# This code is part of qmatchatea.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import unittest

import numpy as np
import qtealeaves.observables as obs
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

from qmatchatea import run_simulation
from qmatchatea.circuit import Qcircuit, observables
from qmatchatea.circuit.observables import QCObservableStep
from qmatchatea.circuit.operations import QCZpauli
from qmatchatea.py_emulator import QCEmulator
from qmatchatea.utils.tn_utils import QCOperators


class TestQcircuit(unittest.TestCase):
    """Test basic feature of Qcircuit without simulations"""

    def setUp(self):
        """Define 'global' variables"""
        self.num_sites = 4
        # Set seed
        np.random.seed(123)

    def test_addlayer(self):
        """
        Test if adding a layer is working
        """

        qcirc = Qcircuit(self.num_sites)
        qcirc._add_layer()
        self.assertEqual(2, qcirc.num_layers, "Number of layers is 2")

    def test_cregister(self):
        """
        test if the functions connected  to the classical register works
        """
        qcirc = Qcircuit(self.num_sites)
        qcirc.add_cregister("classical", 4)

        self.assertIn("classical", qcirc._cregisters, "classical cregister is created")

        # Fake a measure putting 1 in the 3rd place, with probability 0.5
        qcirc.modify_cregister((1, 0.5), "classical", 2)

        # Check if we can retrive the 1
        self.assertEqual(
            1,
            qcirc.inspect_cregister("classical", 2),
            "Check if we retrieve the 1 in 0100",
        )

        # Check if the relative decimal number is correct
        self.assertEqual(
            4,
            qcirc.inspect_cregister("classical"),
            "Check if we retrieve the decimal" + " number associated with 0100",
        )

    def test_qregister(self):
        """
        Test if the addition/remotion of quantum register works
        This also check for the single site add/remove
        """
        qcirc = Qcircuit(self.num_sites)

        # Add the register
        qcirc.add_qregister("q1", [1, 2, 4])
        self.assertIn("q1", qcirc._qregisters, "q1 qregister is created")

        # Since it has been added in position 1 the first member of the
        # qregister 'q1' should be 1, while the second should be 2+1=3
        # (since it was previously inserted another site)
        self.assertEqual(
            qcirc._qregisters["q1"][0], 1, "First added site is in index 1"
        )
        self.assertEqual(
            qcirc._qregisters["q1"][1], 3, "Second added site is in index 3"
        )

        # Remove the register
        qcirc.remove_qregister("q1")
        self.assertNotIn("q1", qcirc._qregisters, "q1 qregister is removed")

    def test_to_matrix(self):
        """Test the transformation to a matrix in dense and sparse form"""
        num_qubs = 10
        rand_params = np.random.uniform(0, 6, 9)

        # Prepare a qiskit circuit
        qc_qk = QuantumCircuit(num_qubs)
        qc_qk.h(0)
        for ii in range(num_qubs - 1):
            qc_qk.cp(rand_params[ii], ii, ii + 1)
        qc_qk.cx(0, num_qubs - 1)
        qc_qk.cx(1, 4)

        mat = Operator(qc_qk).data

        # And the same as Qcircuit
        qc = Qcircuit(num_qubs)
        qc.h(0)
        for ii in range(num_qubs - 1):
            qc.cp(rand_params[ii], [ii, ii + 1])
        qc.cx([0, num_qubs - 1])
        qc.cx([1, 4])

        qc_mat = qc.to_matrix()
        matrix_is_same = np.isclose(mat, qc_mat).all()

        self.assertTrue(matrix_is_same, "Dense matrix is retrieved correctly")

        qc_mat_sparse = qc.to_matrix(sparse=True).toarray()
        sparse_matrix_is_same = np.isclose(qc_mat_sparse, mat).all()

        self.assertTrue(sparse_matrix_is_same, "Sparse matrix is retrieved correctly")


class TestQcircuitObservables(unittest.TestCase):
    """Test basic feature of Qcircuit without simulations"""

    def setUp(self):
        """Define 'global' variables"""
        self.num_sites = 4
        # Set seed
        np.random.seed(123)
        self.sz = QCZpauli().operator

    def _make_ghz(self, qregs=None):
        qc = Qcircuit(self.num_sites)
        qc.h(0)
        for ii in range(self.num_sites - 1):
            qc.cx([ii, ii + 1])

        if qregs is not None:
            for idx, qreg in enumerate(qregs):
                qc.add_qregister(qreg, np.repeat(idx, idx))

        obsv = obs.TNObservables()
        ops = QCOperators()

        return qc, obsv, ops

    def test_local(self):
        """test local observables"""
        qc, obsv, ops = self._make_ghz()
        sim = QCEmulator(self.num_sites)

        obsv += obs.TNObsLocal("sz", "sz")
        ops["sz"] = self.sz

        qc.measure_observables("step1", obsv, ops, "default")

        qc.add_qregister("new", [0])
        qc.x(0, qreg="new")
        qc.measure_observables("step2", obsv, ops)

        _, results, _ = sim.run_from_qcirc(qc)

        step1_res = results["step1"]["sz"]["default"]
        step2_res = results["step2"]

        expected = np.zeros(4)

        self.assertTrue(
            np.isclose(step1_res, expected).all(),
            "Local measurement on single" + " register correct",
        )

        conds = np.isclose(step2_res["sz"]["default"], expected).all()
        conds = conds and np.isclose(step2_res["sz"]["new"], [-1]).all()
        self.assertTrue(conds, "Local measurement on multiple" + " registers correct")

    def test_projective(self):
        """test projective observables"""
        qc, obsv, ops = self._make_ghz()
        sim = QCEmulator(self.num_sites)

        obsv += obs.TNObsProjective(1024, True)

        qc.measure_observables("step1", obsv, ops, "default")

        qc.add_qregister("new", [0])
        qc.x(0, qreg="new")
        qc.measure_observables("step2", obsv, ops)

        _, results, _ = sim.run_from_qcirc(qc)

        step1_res = results["step1"]["projective_measurements"]["default"]
        step2_res = results["step2"]["projective_measurements"]["new"]

        self.assertIn(
            "1111", step1_res, "Projective measurement on single" + " register correct"
        )

        self.assertEqual(
            step2_res["1"],
            1024,
            "Projective measurement on multiple" + " registers correct",
        )

    def test_probabilities(self):
        """test local probabilities"""
        prob_type = ("U", "E")  # , "G")
        prob_threshold = (0, 0.1)  # , 0.9)
        num_samples = (100, 0)  # , 0) # How does zero samples make sense?
        prob_names = (
            "unbiased_probability",
            "even_probability",
        )  # , "greedy_probability")

        for pn, pb, pt, ns in zip(prob_names, prob_type, prob_threshold, num_samples):
            qc, obsv, ops = self._make_ghz()
            sim = QCEmulator(self.num_sites)

            obsv += obs.TNObsProbabilities(pb, ns, pt)

            qc.measure_observables("step1", obsv, ops, "default")

            qc.add_qregister("new", [0])
            qc.x(0, qreg="new")
            qc.measure_observables("step2", obsv, ops)

            _, results, _ = sim.run_from_qcirc(qc)

            step1_res = results["step1"][pn]["default"]
            step2_res = results["step2"][pn]["new"]

            if pn == "unbiased_probability":
                step2_res["1"] = step2_res["1"][1] - step2_res["1"][0]
                step2_res["0"] = step2_res["0"][1] - step2_res["0"][0]

            step2_res = np.sum(list(step2_res.values()))

            self.assertIn(
                "1111",
                step1_res,
                pb + " probability measurement on single" + " register correct",
            )

            self.assertAlmostEqual(
                step2_res,
                1,
                msg=pb + " probability measurement on multiple" + " registers correct",
            )

    def test_bondentropy(self):
        """test bond entropy observables"""
        qc, obsv, ops = self._make_ghz()
        sim = QCEmulator(self.num_sites)

        obsv += obs.TNObsBondEntropy()

        qc.add_qregister("new", [0])
        qc.x(0, qreg="new")
        qc.cx([0, 0], qreg=["new", "default"])
        qc.measure_observables("step1", obsv, ops)

        _, results, _ = sim.run_from_qcirc(qc)
        bd = results["step1"]["bond_entropy"]

        res = np.array(list(bd.values()))[1:]

        self.assertAlmostEqual(bd[(0, 1)], 0, msg="No entanglement in tensor product")
        self.assertTrue(
            (res == 0.6931471805599454).all(),
            msg="Same GHZ entanglement in all the rest",
        )

    def test_tensor_product(self):
        """test tensor product observables"""
        qc, obsv, ops = self._make_ghz()
        sim = QCEmulator(self.num_sites)
        obsv += obs.TNObsTensorProduct("sz", "sz", 1)
        ops["sz"] = self.sz

        qc.add_qregister("new", [0])
        qc.x(0, qreg="new")
        qc.measure_observables("step1", obsv, ops, qreg="new")

        _, results, _ = sim.run_from_qcirc(qc)

        step2_res = np.real(results["step1"]["sz"])

        self.assertAlmostEqual(
            step2_res, -1, msg="Tensor product operator correctly broadcasted"
        )

    def test_weighted_sum(self):
        """test weighted sum observables"""
        qc, obsv, ops = self._make_ghz()
        sim = QCEmulator(self.num_sites)
        tp = obs.TNObsTensorProduct("sz", ["sz", "id"], [[0], [1]])
        tp += obs.TNObsTensorProduct("sz", ["sz", "id"], [[1], [0]])

        obsv += obs.TNObsWeightedSum("szz", tp, [5, 10])
        ops["sz"] = self.sz
        ops["id"] = np.eye(2)

        qc.add_qregister("new", [0, 0])
        qc.x(0, qreg="new")
        qc.measure_observables("step1", obsv, ops, qreg="new")

        _, results, _ = sim.run_from_qcirc(qc)

        res = np.real(results["step1"]["szz"])

        self.assertAlmostEqual(
            res, 5, msg="Weighted sum operator correctly broadcasted"
        )
