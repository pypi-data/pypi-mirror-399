# This code is part of qmatchatea.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import pathlib
import shlex
import subprocess
import unittest


class TestFormatting(unittest.TestCase):
    folders = "qmatchatea", "tests"

    def check_ext_util(self, cmd_call):
        # Function to run the command call. Then it checks whether the command's exit code is 0, which means success
        result = subprocess.run(
            shlex.join(cmd_call), stderr=subprocess.PIPE, shell=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_black(self):
        self.check_ext_util(["black", "--check", *self.folders])

    def test_isort(self):
        self.check_ext_util(["isort", *self.folders, "--check", "-v"])
