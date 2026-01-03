# This code is part of qmatchatea.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import io
import os
import subprocess
import unittest
import warnings
from contextlib import redirect_stdout
from pathlib import Path
from shutil import copy, rmtree

import numpy as np
from qtealeaves.tensors.tensor import GPU_AVAILABLE

from examples.advanced.checkpoints import main as checkpoints
from examples.advanced.io_settings import main as io_settings
from examples.advanced.qcemulator import main as qcemulator
from examples.advanced.qudits import main as qudits
from examples.backend.argparse_selector import main as argparse_selector
from examples.backend.device import main as device
from examples.backend.mps_ttn_comparison import main as mps_ttn_comparison
from examples.backend.precisions import main as precisions
from examples.backend.tensor_mods import main as tensor_mods
from examples.circuits.quantum_fourier_transform import (
    main as quantum_fourier_transform,
)
from examples.circuits.random_quantum_circuit import main as random_quantum_circuit
from examples.circuits.teleportation import main as teleportation
from examples.circuits.variational_quantum_eigensolver import (
    main as variational_quantum_eigensolver,
)
from examples.convergence.bond_dimension import main as bond_dimension
from examples.convergence.convergence_analysis import main as convergence_analysis
from examples.convergence.svd_methods import main as svd_methods
from examples.get_started import main as get_started
from examples.observables.bond_entropy import main as bond_entropy
from examples.observables.local import main as local
from examples.observables.mid_circuit_measurement import main as mid_circuit_measurement
from examples.observables.probabilities import main as probabilities
from examples.observables.projective import main as projective
from examples.observables.save_read_results import main as save_read_results
from examples.observables.save_state import main as save_state
from examples.observables.tensor_product import main as tensor_product
from examples.observables.weighted_sum import main as weighted_sum

try:
    import mpi4py

    has_mpi = True
except ImportError:
    has_mpi = False

warnings.filterwarnings("ignore")


class TestExamples(unittest.TestCase):
    """Test that all the examples works correctly"""

    def setUp(self):
        """Define 'global' variables"""
        self.mpi_command = os.environ.get("QMATCHATEA_MPI_COMMAND", "mpiexec")
        self.examples_folder = "examples/"
        if not os.path.isdir(self.examples_folder):
            os.makedirs(self.examples_folder)
        self.num_sites = 4
        # Set seed
        np.random.seed(123)

        self.data_dir = "data"
        if os.path.isdir(self.data_dir):
            rmtree(self.data_dir)

    def tearDown(self):
        if os.path.isdir("TMP_TEST"):
            rmtree("TMP_TEST")
        if os.path.isdir("TMP_MPI"):
            rmtree("TMP_MPI")
        if os.path.isdir("mpi"):
            rmtree("mpi")
        if os.path.isdir(self.data_dir):
            rmtree(self.data_dir)
        return

    def base_mpi(self, filepath, msg):
        """Execute a test with an MPI example."""
        cmd = [self.mpi_command, "-n", "4", "python3", filepath]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=os.environ,
            cwd=os.getcwd(),
        )

        success = result.returncode == 0
        if not success:
            print("Was running", " ".join(cmd), "in", os.getcwd())
            print("Stdout", result.stdout)
            print("Stderr", result.stderr)
            print("Return code", result.returncode)

        self.assertTrue(success, msg=msg)

    def base_example(self, func):
        """Wrapper for example redirecting output."""
        f = io.StringIO()
        exc = None
        result = None
        with redirect_stdout(f):
            try:
                result = func()
            except Exception as e:
                exc = e

        if exc is not None:
            print("stdout:\n", f.getvalue())
            raise exc

        return result

    def test_check_completeness(self):
        """
        Test whether all the example from the examples folder have been included in the unittest
        """

        this_path = Path(os.path.abspath(__file__))
        examples_path = this_path.parent.parent.absolute() / "examples"
        whitelist = [
            "mpi/data_parallelism_mpi_example.py",  # skipping due to MPI requirement, tested elsewhere
            "mpi/mpi_mps.py",  # skipping due to MPI requirement, tested elsewhere
        ]

        no_missing = True
        missing_list = []

        for file in examples_path.rglob("*.py"):
            file_relative_to_examples = file.relative_to(examples_path)
            file_POSIX_string = str(file_relative_to_examples.as_posix())
            file_as_python_import = ".".join(
                file_relative_to_examples.with_suffix("").parts
            )

            with open(os.path.abspath(__file__), "r") as current_file:
                found = False
                for line in current_file:
                    if line.startswith("from examples." + file_as_python_import):
                        found = True
                        break
                if file_POSIX_string in whitelist:
                    pass
                elif not found:
                    no_missing = False
                    missing_list.append(file_POSIX_string)

        self.assertTrue(
            no_missing,
            "Missing unittest for the following examples files: " + str(missing_list),
        )

    def test_advanced_checkpoints(self):
        """
        Test the checkpoints example
        """
        self.base_example(checkpoints)

    def test_advanced_io_settings(self):
        """
        Test the io_settings example
        """
        self.base_example(io_settings)

    def test_advanced_qcemulator(self):
        """
        Test the qcemulator example
        """
        self.base_example(qcemulator)

    def test_advanced_qudits(self):
        """
        Test the qudits example
        """
        self.base_example(qudits)

    def test_backend_argparse_selector(self):
        """
        Test the argparse_selector example
        """
        self.base_example(argparse_selector)

    @unittest.skipIf(not GPU_AVAILABLE, "GPU is not available")
    def test_backend_device(self):
        """
        Test the device example
        """
        self.base_example(device)

    def test_backend_mps_ttn_comparison(self):
        """
        Test the mps_ttn_comparison example
        """
        self.base_example(mps_ttn_comparison)

    def test_backend_precisions(self):
        """
        Test the precisions example
        """
        self.base_example(precisions)

    def test_backend_tensor_mods(self):
        """
        Test the tensor mods example (numpy, torch, tensorflow, jax).
        Ignore errors if you get the number of backends you expect based
        on your installation, e.g., 2 not equal to 4 if you did install
        only numpy and torch.
        """
        counter = self.base_example(tensor_mods)
        self.assertEqual(
            counter, 4, msg="Failed loading at least one of the four backends."
        )

    def test_circuits_quantum_fourier_transform(self):
        """
        Test the quantum_fourier_transform example
        """
        self.base_example(quantum_fourier_transform)

    def test_circuits_random_quantum_circuit(self):
        """
        Test the random_quantum_circuit example
        """
        self.base_example(random_quantum_circuit)

    def test_circuits_teleportation(self):
        """
        Test the teleportation example
        """
        self.base_example(teleportation)

    def test_circuits_variational_quantum_eigensolver(self):
        """
        Test the variational_quantum_eigensolver example
        """
        self.base_example(variational_quantum_eigensolver)

    def test_convergence_bond_dimension(self):
        """
        Test the bond_dimension example
        """
        self.base_example(bond_dimension)

    def test_convergence_convergence_analysis(self):
        """
        Test the convergence_analysis example
        """
        self.base_example(convergence_analysis)

    def test_convergence_svd_methods(self):
        """
        Test the svd_methods example
        """
        self.base_example(svd_methods)

    # Not sure why the two MPI did have problems, but in the `tests_mpi4py.py`
    # they are tested for now. Ticket is open.

    @unittest.skipIf(not has_mpi, "mpi4py not installed")
    def disabled_mpi_data_parallelism(self):
        """
        Test the mpi_example example
        """
        msg = "mpi data parallelism example simulated parallely fails."
        self.base_mpi(f"{self.examples_folder}mpi/data_parallelism_mpi_example.py", msg)

    @unittest.skipIf(not has_mpi, "mpi4py not installed")
    def disabled_mpi_mpi_mps(self):
        """
        Test the mpi_example example
        """
        msg = "mpi_mpi example simulated parallely on multiple processes fails."
        self.base_mpi(f"{self.examples_folder}mpi/mpi_mps.py", msg)

    def test_observables_bond_entropy(self):
        """
        Test the bond_entropy example
        """
        self.base_example(bond_entropy)

    def test_observables_local(self):
        """
        Test the local example
        """
        self.base_example(local)

    def test_observables_mid_circuit_measurement(self):
        """
        Test the mid_circuit_measurement example
        """
        self.base_example(mid_circuit_measurement)

    def test_observables_probabilities(self):
        """
        Test the probabilities example
        """
        self.base_example(probabilities)

    def test_observables_projective(self):
        """
        Test the projective example
        """
        self.base_example(projective)

    def test_observables_save_read_results(self):
        """
        Test the save_read_results example
        """
        self.base_example(save_read_results)

    def test_observables_save_state(self):
        """
        Test the save_state example
        """
        self.base_example(save_state)

    def test_observables_tensor_product(self):
        """
        Test the tensor_product example
        """
        self.base_example(tensor_product)

    def test_observables_weighted_sum(self):
        """
        Test the weighted_sum example
        """
        self.base_example(weighted_sum)

    def test_get_started(self):
        """
        Test the get_started example
        """
        self.base_example(get_started)
