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
Class to handle the results of a qmatchatea simulation
"""

# pylint: disable=too-many-instance-attributes
import pickle
from datetime import datetime

import numpy as np
from qtealeaves.emulator import MPS, TTN
from qtealeaves.tensors import TensorBackend

__all__ = ["SimulationResults"]


class SimulationResults:
    """
    Class to store and retrieve the result of a qmatchatea simulation
    """

    def __init__(self, observables=None):
        """
        Initialization.
        If you want to load previous results, just initialize the class
        without parameters.

        Parameters
        ----------
        observables: TNObservables, optional
            observables used in the simulation
        """

        self._datetime = datetime.today().strftime("%Y-%m-%d-%H:%M:%S")

        # Set to None all the variables
        self._initial_state = None
        self._observables = {} if observables is None else observables
        self._singular_values_cut = None
        self._statevector = None

    # ----------------------------
    # Methods to save/load results
    # ----------------------------
    def _store_attr_for_pickle(self):
        """Return dictionary with attributes that cannot be pickled and unset them."""
        storage = {
            "tn_state": self._observables.get("tn_state", None),
            "initial_state": self._initial_state,
            "statevector": self._statevector,
        }

        self._observables["tn_state"] = None
        self._initial_state = None
        self._statevector = None

        return storage

    def _restore_attr_for_pickle(self, storage):
        """Restore attributed removed for pickle from dictionary."""
        # Reset temporary removed attributes
        self._observables["tn_state"] = storage["tn_state"]
        self._initial_state = storage["initial_state"]
        self._statevector = storage["statevector"]

    def save_pickle(self, filename):
        """
        Save class via pickle-module.

        Parameters
        ----------
        filename : str
            path where to save the file

        **Details**

        The following attributes have a special treatment and are not present
        in the copied object.

        * initial state tensor network
        * final state tensor network
        * statevector
        """
        # Temporary remove objects which cannot be pickled which
        # included convergence parameters for lambda function and
        # parameterized variables, the log file as file handle and
        # the MPI communicator
        storage = self._store_attr_for_pickle()

        ext = "pkl"
        if not filename.endswith(ext):
            filename += "." + ext

        with open(filename, "wb") as fh:
            pickle.dump(self, fh)

        self._restore_attr_for_pickle(storage)

    @classmethod
    def read_pickle(cls, filename):
        """
        Load the results of a previous simulation

        Parameters
        ----------
        path: str
            PATH to the file from which we want to load the results

        Returns
        -------
        readme: str
            The text contained in the readme file inside the folder
        """
        ext = "pkl"
        if not filename.endswith(ext):
            raise ValueError(
                f"Filename {filename} not valid, extension should be {ext}."
            )

        with open(filename, "rb") as fh:
            obj = pickle.load(fh)

        if not isinstance(obj, cls):
            raise TypeError(
                f"Loading wrong type as simulation result: {type(obj)} vs {cls}."
            )

        return obj

    def set_results(self, result_dict, singvals_cut):
        """Set the results of a simulation

        Parameters
        ----------
        result_dict: dict
            Dictionary of the attribute to be set
        singvals_cut: array-like
            Array of singular values cut through the simulation
        """
        self._observables = result_dict.copy()
        self._singular_values_cut = np.array(singvals_cut)

        tn_state_path = None
        for key, value in result_dict.items():
            # The only key with the '.' is the MPS state
            if "/" in key:
                tn_state_path = value

        if tn_state_path is not None:
            self._observables["tn_state_path"] = tn_state_path
        self.load_state()

    def load_state(self, tensor_backend=TensorBackend()):
        """
        Loads the state located in `tn_state_path`,
        saving it in `tn_state`

        Parameters
        ----------
        tensor_backend : TensorBackend, optional
            Tensor backend of the state if it is
            saved in a formatted format.
            Default to TensorBackend().
        """
        key = self.observables.get("tn_state_path", None)
        if key is None:
            return

        if key.endswith("pklmps"):
            state = MPS.read_pickle(key)
        elif key.endswith("mps"):
            state = MPS.read(key, tensor_backend=tensor_backend)
        elif key.endswith("pklttn"):
            state = TTN.read_pickle(key)
        elif key.endswith("ttn"):
            state = TTN.read(key, tensor_backend=tensor_backend)
        else:
            raise IOError(f"File extension {key} not supported")

        self._observables["tn_state"] = state

    # -----------------------------
    # Methods to access the results
    # -----------------------------
    @property
    def fidelity(self):
        """
        Return the lower bound for the fidelity of the simulation,
        using the method described in
        If you are interested in the evolution of the fidelity through
        the simulation compute it yourself using `np.cumprod(1-self.singular_values_cut)`.

        Returns
        -------
        float
            fidelity of the final state
        """

        fid = np.prod(1 - np.array(self.singular_values_cut))
        return fid

    @property
    def measures(self):
        """Obtain the measures of the simulation as a dictionary.
        The keys are the measured states, the values the number of occurrencies

        Returns
        -------
        measures: dict
            Measures of the simulation
        """
        return self.observables.get("projective_measurements", None)

    @property
    def statevector(self):
        """Obtain the statevector as a complex numpy array

        Returns
        -------
        statevector: np.array or None
            The statevector of the simulation
        """
        if self._statevector is None:
            if "tn_state" in self.observables.keys():
                tn_state = self.observables["tn_state"]
                if tn_state is None:
                    self.load_state()
                    tn_state = self.observables["tn_state"]
                if tn_state.num_sites < 30:
                    self._statevector = tn_state.to_statevector(
                        qiskit_order=True, max_qubit_equivalent=30
                    )
        return self._statevector.elem

    @property
    def singular_values_cut(self):
        """Obtain the singular values cutted through the simulation, depending on the mode
        chosen. If 'M' for maximum (default), 'C' for cumulated.

        Returns
        -------
        np.ndarray[float]
            Singular values cut during the simulation
        """
        return self._singular_values_cut

    @property
    def computational_time(self):
        """Obtain the computational time of the simulation

        Returns
        -------
        float
            computational time of the simulation
        """
        return self.observables.get("time", None)

    @property
    def entanglement(self):
        """Obtain the bond entanglement entropy measured along each bond of the MPS at
        the end of the simulation

        Returns
        -------
        entanglement: np.array or None
            Bond entanglement entropy
        """
        if "bond_entropy" in self.observables.keys():
            entanglement = self.observables["bond_entropy"]
        elif "bond_entropy0" in self.observables.keys():
            entanglement = self.observables["bond_entropy0"]
        else:
            entanglement = None
        return entanglement

    @property
    def measure_probabilities(self):
        """Return the probability of measuring a given state, which is computed using a
        binary tree by eliminating all the branches with probability under a certain threshold.

        Returns
        -------
        measure_probabilities: Dict[Dict | None]
            probability of measuring a certain state if it is greater than a threshold
        """
        keys = ["unbiased_probability", "even_probability", "greedy_probability"]
        new_keys = ["U", "E", "G"]
        probs = {}
        for key, new_key in zip(keys, new_keys):
            if key in self.observables.keys():
                probs[new_key] = self.observables[key]
            else:
                probs[new_key] = [None]
        return probs

    @property
    def date_time(self):
        """Obtain the starting date and time of the simulation, in the format
        ``Year-month-day-Hour:Minute:Second``

        Returns
        -------
        datetime: string
            The date-time when the simulation started
        """
        return self._datetime

    @property
    def tn_state(self):
        """
        Returns the tensor network class, either TTN or MPS

        Returns
        -------
        _AbstractTN
            The tensor network class
        """
        return self.observables.get("tn_state", None)

    @property
    def tn_state_path(self):
        """
        Returns the tensor list in row-major format.
        The indexing of the single tensor is as follows:

        .. code-block::

            1-o-3
             2|

        Returns
        -------
        mps: list
            list of np.array tensors
        """
        return self.observables.get("tn_state_path", None)

    @property
    def initial_state(self):
        """Returns the initial state of the simulation, as an MPS in row-major format or as
        a string if starting from the Vacuum state

        Returns
        -------
        initial_state: list or str
            list of np.array tensors or Vacuum
        """
        return self._initial_state

    @property
    def observables(self):
        """Returns the expectation values of the observables as a dict with the format
            observable_name : observable_expectation_value

        Returns
        -------
        observables: dict or None
            Expectation values of the observables
        """
        return self._observables
