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
import subprocess
import unittest
from shutil import rmtree

try:
    import mpi4py

    mpi_is_present = True
except ModuleNotFoundError:
    mpi_is_present = False


class TestSimulationParallelization(unittest.TestCase):
    """
    Since it is not possible to directly run this test we perform a workaround:
    through subprocess the unittest calls the actual test
    """

    def setUp(self):
        self.mpi_command = os.environ.get("QMATCHATEA_MPI_COMMAND", "mpiexec")

    def base_mpi_test(self, filename, msg):
        """Run an MPI example as unittest."""
        cmd = [self.mpi_command, "-n", "4", "python3", filename]
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

    @unittest.skipIf(not mpi_is_present, "MPI is not present")
    def test_mpi_data_parallelism(self):
        """
        Test if the parallelization of multiple simulations is working using GHZ states.
        """
        filename = "tests/mpi/_testmpi_data_parallelism.py"
        msg = ("Data parallelism simulated parallely on multiple processes correts",)

        self.base_mpi_test(filename, msg)
        return

    @unittest.skipIf(not mpi_is_present, "MPI is not present")
    def test_mpimps_ghz(self):
        """
        Test if the parallelization of multiple simulations is working using GHZ states.
        """
        filename = "tests/mpi/_testmpimps_ghz.py"
        msg = "GHZ circuits simulated parallely on multiple processes correts"

        self.base_mpi_test(filename, msg)
        return

    @unittest.skipIf(not mpi_is_present, "MPI is not present")
    def test_mpimps_qft(self):
        """
        Test if the parallelization of multiple simulations is working using GHZ states.
        """
        filename = "tests/mpi/_testmpimps_qft.py"
        msg = "QFT circuits simulated parallely on multiple processes correts"

        self.base_mpi_test(filename, msg)
        return

    @unittest.skipIf(not mpi_is_present, "MPI is not present")
    def test_example_a(self):
        filename = "examples/mpi/data_parallelism_mpi_example.py"
        msg = "Example data parallelism fails."

        self.base_mpi_test(filename, msg)
        return

    @unittest.skipIf(not mpi_is_present, "MPI is not present")
    def test_example_b(self):
        filename = "examples/mpi/mpi_mps.py"
        msg = "Example MPI MPS fails."

        self.base_mpi_test(filename, msg)
        return
