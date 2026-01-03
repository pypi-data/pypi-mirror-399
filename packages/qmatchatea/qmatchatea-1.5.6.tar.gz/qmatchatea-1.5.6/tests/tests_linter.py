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
import unittest
from io import StringIO

import pylint.lint
from pylint.reporters.text import ParseableTextReporter


class TestPylint(unittest.TestCase):
    """
    Run pylint to check syntax in source files.

    **Details**

    We disable globally:

    * C0325: superfluous parenthesis
    * C0209: consider using fstring
    * W1514: unspecified encoding
    * R1711: useless returns (for allowing empty iterators with
      return-yield)
    * R1732: consider using with
    * Skip Unused argument errors when args
    * Skip Unused argument errors when kargs

    """

    def setUp(self):
        """
        Provide the test setup.
        """
        pattern_1 = (
            "[E0611(no-name-in-module), ] No name '_TNObsBase' in module"
            + " 'qtealeaves'"
        )
        self.default_patterns = [pattern_1]
        self.pylint_args = {
            "good-names": "ii,jj,kk,nn,mm,fh,dx,dy,dz,dt,hh,qc,dl,gh,xp,PATH,inPATH,outPATH",
            "disable": "C0325,C0209,W1514,R1711,R1732",
            "known-third-party": "qtealeaves,qredtea",
            #'ignore_in_line' : pattern_1
        }

    def run_pylint(self, filename, local_settings={}):
        """
        Run linter test with our unit test settings for one specific
        filename.
        """
        args = []

        ignore_in_line = self.default_patterns
        if "ignore_in_line" in local_settings:
            ignore_in_line += local_settings["ignore_in_line"]
            del local_settings["ignore_in_line"]

        for elem in self.pylint_args.keys():
            args += ["--" + elem + "=" + self.pylint_args[elem]]

            if elem in local_settings:
                args[-1] = args[-1] + "," + local_settings[elem]
                del local_settings[elem]

        for elem in local_settings.keys():
            args += ["--" + elem + "=" + local_settings[elem]]

        args += [filename]

        obj = StringIO()
        reporter = pylint.reporters.text.ParseableTextReporter(obj)
        pylint.lint.Run(args, reporter=reporter, exit=False)

        error_list = []
        for elem in obj.getvalue().split("\n"):
            tmp = elem.replace("\n", "")

            if len(tmp) == 0:
                continue
            if tmp.startswith("***"):
                continue
            if tmp.startswith("---"):
                continue
            if tmp.startswith("Your code"):
                continue
            if "Unused argument 'args'" in tmp:
                continue
            if "Unused argument 'kwargs'" in tmp:
                continue

            do_continue = False
            for pattern in ignore_in_line:
                if pattern in tmp:
                    do_continue = True

            if do_continue:
                continue

            error_list.append(tmp)

        return error_list

    def test_folders_recursively(self):
        """
        Recursively run python linter test on all .py files of
        specified folders.
        """
        parent_folders = ["qmatchatea"]
        skip_files = []
        error_list = []

        for elem in parent_folders:
            for root, dirnames, filenames in os.walk(elem):
                for filename in filenames:
                    if not filename.endswith(".py"):
                        continue

                    if filename in skip_files:
                        continue

                    target_file = os.path.join(root, filename)

                    target_attr = "get_settings_" + filename.replace(".py", "")
                    if hasattr(self, target_attr):
                        target_setting = self.__getattribute__(target_attr)()
                    else:
                        target_setting = {}

                    error_list_ii = self.run_pylint(
                        target_file, local_settings=target_setting
                    )

                    error_list += error_list_ii

        if len(error_list) > 0:
            print("\n".join(error_list))

        self.assertEqual(len(error_list), 0, "\n".join(error_list))
