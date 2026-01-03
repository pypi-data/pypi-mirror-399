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
General utility functions and classes for the simulation
"""

import json

# Import necessary packages
import os
import pickle
import time
from typing import OrderedDict

import numpy as np
import qiskit.qpy as qpy_serialization
from qiskit.circuit import QuantumCircuit
from qtealeaves.abstracttns.abstract_tn import _AbstractTN
from qtealeaves.convergence_parameters import TNConvergenceParameters
from qtealeaves.observables import TNObservables

from .tn_utils import QCOperators

__all__ = [
    "print_state",
    "fidelity",
    "QCCheckpoints",
    "QCIO",
    "QCConvergenceParameters",
    "SimpleHamiltonian",
]


class SimpleHamiltonian(dict):
    """
    Simple class for an Hamiltonian that extends a normal dictionary.
    The keys are the pauli strings, the values the coefficients.
    It is used for simplicity, since it has a `to_pauli_dict` method
    equivalent to qiskit and other methods to ease the construction.
    """

    def set_num_qubits(self, num_qubits):
        """
        Set the number of qubits the Hamiltonian is describing

        Parameters
        ----------
        num_qubits : int
            Number of qubits
        """
        self["num_qubits"] = num_qubits

    def add_term(self, hterms, qubits, coeff):
        """
        Add a term to the Hamiltonian acting on the
        qubits qubits. You do not need to specify the identities

        Parameters
        ----------
        hterms : str or array-like
            Pauli matrices to apply
        qubits : int or array-like
            Qubits where the terms acts
        coeff : complex
            Coefficient of the term

        Returns
        -------
        None
        """
        if np.isscalar(qubits):
            qubits = np.array([qubits])
            hterms = np.array([hterms])
        ordering = np.argsort(qubits)
        qubits = qubits[ordering]
        hterms = hterms[ordering]

        pauli_string = ""
        for hterm, qubit in zip(hterms, qubits):
            last_qubit = len(pauli_string)
            pauli_string += "I" * (qubit - last_qubit)
            pauli_string += hterm
        last_qubit = len(pauli_string)
        pauli_string += "I" * (self["num_qubits"] - last_qubit)

        self[pauli_string[::-1]] = coeff

    def to_pauli_dict(self):
        """
        Get the qiskit pauli dict representation, that can be later
        used in the observable class

        Returns
        -------
        dict
            dictionary with qiskit pauli_dict old format
        """
        pauli_dict = {"paulis": []}
        for key, val in self.items():
            if key == "num_qubits":
                continue

            pauli_dict["paulis"].append(
                {"label": key, "coeff": {"real": np.real(val), "imag": np.imag(val)}}
            )
        return pauli_dict


class QCCheckpoints:
    """
    Class to handle checkpoint parameters

    Parameters
    ----------
    PATH: str, optional
        PATH to the checkpoint directory. Default `data/checkpoints/`.
    frequency: float, optional
        Decide the frequency, in **hours**, of the checkpoints.
        If negative no checkpoints are present. Default to -1.
    input_nml: str, optional
        Name of the input namelist. Default 'input.nml'
    restart: int, optional
        If an int is provided, it is the checkpoint counter from which the user wants to restart.
        Default to None.
    """

    def __init__(
        self,
        PATH="data/checkpoints/",
        frequency=-1,
        input_nml="input.nml",
        restart=None,
    ):
        # pylint: disable-next=invalid-name
        self._PATH = PATH if (PATH.endswith("/")) else PATH + "/"
        self._frequency = frequency
        self._input_nml = input_nml
        self.restart = restart
        self._checkpoint_cnt = 0
        self._initial_line = 0
        self._initial_time = -1

    def set_up(
        self,
        input_dict,
        operators=QCOperators(),
        observables=TNObservables(),
        circ="",
    ):
        """Set up the checkpoints directory

        Parameters
        ----------
        input_dict : dict
            Input parameter dictionary
        operators : :py:class:`QCOperators`, optional
            Tensor operators
        obervables : :py:class: `TNObservables`, optional
            Tensor observables
        circ_str: str or QuantumCircuit
            String representing the qiskit quantum circuit
        """
        if not isinstance(operators, QCOperators):
            raise TypeError("Operators must be QCOperators type")
        if not isinstance(observables, TNObservables):
            raise TypeError("observables must be TNObservables type")

        if not os.path.isdir(self.PATH):
            os.mkdir(self.PATH)

        # Modify for new PATH
        input_dict["inPATH"] = self.PATH

        # Write files that can be already written
        with open(os.path.join(self.PATH, "observables.pk"), "wb") as fh:
            pickle.dump(observables, fh)

        # We save extra infos for checkpoints, i.e. the quantum circuit
        if isinstance(circ, str):
            with open(os.path.join(self.PATH, "circuit.dat"), "w") as fh:
                fh.write(circ)
        elif isinstance(circ, QuantumCircuit):
            with open(os.path.join(self.PATH, "circuit.qpy"), "wb") as fd:
                qpy_serialization.dump(circ, fd)
        else:
            raise ValueError(f"Impossible to handle circuit of type {type(circ)}")

        self._initial_time = time.time()

    @property
    def PATH(self):
        """PATH property"""
        return self._PATH

    @property
    def frequency(self):
        """Checkpoint frequency property"""
        return self._frequency

    @property
    def input_nml(self):
        """Input namelist property"""
        return self._input_nml

    def save_checkpoint(self, operation_idx, emulator):
        """
        Save the state for the checkpoint if the
        `operation_idx` exceeded the frequency of the
        checkpoints

        Parameters
        ----------
        operation_idx : int
            Index of the current operation in the quantum circuit
        emulator: _AbstractTN
            Tensor network class

        Returns
        -------
        None
        """
        elapsed_time = (time.time() - self._initial_time) / 3600
        if elapsed_time > self.frequency > 0:
            dir_path = os.path.join(self.PATH, str(self._checkpoint_cnt))

            # Create directory if not accessible
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)

            # Save the TN state on file.
            file_path = os.path.join(dir_path, "tn_state.npy")
            tensor_list = emulator.to_tensor_list()
            np.save(file_path, np.array(tensor_list, dtype=object), allow_pickle=True)

            # Save the index of the line on file
            # The +1 is because that operation has already been applied
            with open(os.path.join(dir_path, "index.txt"), "w") as fh:
                fh.write(str(operation_idx + 1))

            # Update the counter
            self._checkpoint_cnt += 1

            # Restart the countdown to the next checkpoint
            self._initial_time = time.time()

    def restart_from_checkpoint(self, initial_state):
        """
        Restart from the checkpoint passed in the initialization.

        Parameters
        ----------
        initial_state: str | List[Tensors] | _AbstractTN
            The initial state of the simulation. Might be overwritten on exit.

        Returns
        -------
        str | List[Tensors] | _AbstractTN
            The new initial state. If `self.restart` is None, it is the old
            initial state.
        """
        # Default value, no restart was requested
        if self.restart is None:
            return initial_state

        # If the value is -1, restart from the last one
        if self.restart == -1:
            self.restart = 0
            while os.path.isdir(os.path.join(self.PATH, str(self.restart))):
                self.restart += 1
            self.restart -= 1

        dir_path = os.path.join(self.PATH, str(self.restart))

        # Save the index of the line on file
        with open(os.path.join(dir_path, "index.txt"), "r") as fh:
            self._initial_line = int(fh.read())

        # Read the TN state
        initial_state = np.load(
            os.path.join(dir_path, "tn_state.npy"), allow_pickle=True
        )

        return initial_state

    def to_dict(self):
        """
        Return the ordered dictionary of the properties of the class.

        Returns
        -------
        dictionary: OrderedDict
            Ordered dictionary of the class properties

        """
        dictionary = OrderedDict()

        dictionary["checkpoint_PATH"] = self.PATH
        dictionary["checkpoint_frequency"] = self.frequency
        dictionary["initial_line"] = 1

        return dictionary

    def to_json(self, path):
        """
        Write the class as a json on file
        """
        path = os.path.join(path, "checkpoints.json")
        with open(path, "w") as fp:
            json.dump(self.to_dict(), fp, indent=4)

    @classmethod
    def from_json(cls, path):
        """
        Initialize the class from a json file
        """
        path = os.path.join(path, "checkpoints.json")
        with open(path, "r") as fp:
            dictionary = json.load(fp)[0]

        return cls(**dictionary)


class QCIO:
    """
    Class to handle Input/Output parameters

    Parameters
    ----------
    inPATH: str, optional
        PATH to the directory containing the input files.
        Default to 'data/in/'
    outPATH: str, optional
        PATH to the directory containing the output files.
        Default to 'data/out/'
    initial_state: str or :py:class:`MPS`, optional
        If an MPS, then the list of tensors is used as initial state for
        a starting point of the simulation.
        If 'Vacuum' start from |000...0>. Default to 'Vacuum'.
        If a PATH it is a PATH to a saved MPS.
    """

    initial_states_keywords = ("vacuum", "random")

    def __init__(
        self,
        inPATH="data/in/",
        outPATH="data/out/",
        initial_state="Vacuum",
    ):
        # pylint: disable-next=invalid-name
        self._inPATH = inPATH if inPATH.endswith("/") else inPATH + "/"
        # pylint: disable-next=invalid-name
        self._outPATH = outPATH if outPATH.endswith("/") else outPATH + "/"
        self._initial_state = initial_state

    def setup(self):
        """
        Setup the io files
        """

        # Directories
        if not os.path.isdir(self.inPATH):
            os.makedirs(self.inPATH)
        if not os.path.isdir(self.outPATH):
            os.makedirs(self.outPATH)

        # Initial state

        # First, check if it is a string.
        if isinstance(self.initial_state, str):
            if self.initial_state.lower() not in self.initial_states_keywords:
                # Handle the string case assuming it is a path
                if not os.path.isfile(self.initial_state):
                    raise FileNotFoundError("Path to input file does not exist.")

        else:
            # Assume it is an _AbstractTN that we can write in a formatted way
            if hasattr(self.initial_state, "write"):
                self.initial_state.write(os.path.join(self.inPATH, "initial_state"))
            elif hasattr(self.initial_state, "save_pickle"):
                self.initial_state.save_pickle(
                    os.path.join(self.inPATH, "initial_state")
                )
            # Assume it is a list and use numpy save
            else:
                np.save(
                    os.path.join(self.inPATH, "initial_state"),
                    np.array(self.initial_state, dtype=object),
                    allow_pickle=True,
                )

    @property
    def inPATH(self):
        """Input PATH property"""
        return self._inPATH

    @property
    def outPATH(self):
        """Output PATH property"""
        return self._outPATH

    @property
    def initial_state(self):
        """Initial state property"""
        return self._initial_state

    # @initial_state.setter
    def set_initial_state(self, initial_state):
        """Modify the initial state property"""
        if not isinstance(initial_state, str):
            if not isinstance(initial_state, _AbstractTN):
                raise TypeError(
                    "A non-str initial state must be initialized as an _AbstractTN class"
                )
        self._initial_state = initial_state

    def to_dict(self):
        """
        Return the ordered dictionary of the properties of the class.

        Returns
        -------
        dictionary: OrderedDict
            Ordered dictionary of the class properties
        """
        dictionary = OrderedDict()
        for prop, value in vars(self).items():
            if prop == "_initial_state" and not isinstance(value, str):
                # do not write the tensor to json,
                # just write the type as a placeholder
                value = type(value).__name__
            dictionary[prop[1:]] = value

        return dictionary

    def to_json(self, path):
        """
        Write the class as a json on file
        """
        path = os.path.join(path, "io_info.json")
        with open(path, "w") as fp:
            json.dump(self.to_dict(), fp, indent=4)

    @classmethod
    def from_json(cls, path):
        """
        Initialize the class from a json file
        """
        path = os.path.join(path, "io_info.json")
        with open(path, "r") as fp:
            dictionary = json.load(fp)[0]

        return cls(**dictionary)


class QCConvergenceParameters(TNConvergenceParameters):
    """Convergence parameter class, inhereting from the
    more general Tensor Network type. Here the convergence
    parameters are only the bond dimension and the cut ratio.

    Parameters
    ----------
    max_bond_dimension : int, optional
        Maximum bond dimension of the problem. Default to 10.
    cut_ratio : float, optional
        Cut ratio for singular values. If :math:`\\lambda_n/\\lambda_1 <` cut_ratio then
        :math:`\\lambda_n` is neglected. Default to 1e-9.
    trunc_tracking_mode : str, optional
        Modus for storing truncation, 'M' for maximum, 'C' for
        cumulated (default).
    svd_ctrl : character, optional
        Control for the SVD algorithm. Available:
        - "A" : automatic. Some heuristic is run to choose the best mode for the algorithm.
        The heuristic can be seen in qtealeaves/tensors/tensors.py
        in the function _process_svd_ctrl.
        - "V" : gesvd. Safe but slow method.
        - "D" : gesdd. Fast iterative method. It might fail. Resort to gesvd if it fails
        - "E" : eigenvalue decomposition method. Faster on GPU. Available only when
        contracting the singular value to left or right
        - "X" : sparse eigenvalue decomposition method. Used when you reach the maximum
        bond dimension.
        - "R" : random svd method. Used when you reach the maximum bond dimension.
        Default to 'A'.
    ini_bond_dimension: int, optional
        Initial bond dimension of the simulation. It is used if the initial state is random.
        Default to 1.

    """

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        max_bond_dimension=10,
        cut_ratio=1e-9,
        trunc_tracking_mode="C",
        svd_ctrl="A",
        ini_bond_dimension=1,
    ):
        TNConvergenceParameters.__init__(
            self,
            max_bond_dimension=max_bond_dimension,
            cut_ratio=cut_ratio,
            trunc_tracking_mode=trunc_tracking_mode,
            svd_ctrl=svd_ctrl,
            ini_bond_dimension=ini_bond_dimension,
        )

    def to_dict(self):
        """Return the ordered dictionary of the properties of
        the class

        Returns
        -------
        dictionary: OrderedDict
            Ordered dictionary of the class properties
        """
        dictionary = OrderedDict()
        dictionary["max_bond_dimension"] = self.max_bond_dimension
        dictionary["cut_ratio"] = self.cut_ratio
        dictionary["trunc_tracking_mode"] = self.trunc_tracking_mode

        return dictionary

    def pretty_print(self):
        """
        Print the convergence parameters.
        (Implemented to avoid too few public methods)
        """
        print("-" * 50)
        print(
            "-" * 10 + f" Maximum bond dimension: {self.max_bond_dimension} " + "-" * 10
        )
        print("-" * 10 + f" Cut ratio: {self.cut_ratio} " + "-" * 10)
        print(
            "-" * 10
            + f" Truncation tracking mode: {self.trunc_tracking_mode} "
            + "-" * 10
        )
        print("-" * 50)

    def to_json(self, path):
        """
        Write the class as a json on file
        """
        path = os.path.join(path, "convergence_parameters.json")
        with open(path, "w") as fp:
            dictionary = self.to_dict()
            dictionary["svd_ctrl"] = self.svd_ctrl
            json.dump(dictionary, fp, indent=4)

    @classmethod
    def from_json(cls, path):
        """
        Initialize the class from a json file
        """
        path = os.path.join(path, "convergence_parameters.json")
        with open(path, "r") as fp:
            dictionary = json.load(fp)[0]

        return cls(**dictionary)


def merge_ordered_dicts(dicts):
    """Merge ordered dicts together, concatenating them in the order provided in the list

    Parameters
    ----------
    dicts : list of OrderedDict
        OrderedDict to concatenate

    Return
    ------
    final_dict: OrderedDict
        Concatenated OrderedDict
    """
    for dictionary in dicts:
        if not isinstance(dictionary, OrderedDict):
            raise TypeError("Only OrderedDict can be concatenated using this function")

    final_dict = dicts[0]
    for dictionary in dicts[1:]:
        final_dict.update(dictionary)

    return final_dict


def print_state(dense_state):
    """
    Prints a *dense_state* with kets. Compatible with quimb states.

    Parameters
    ----------
    dense_state: array_like
            Dense representation of a quantum state

    Returns
    -------
    None: None
    """

    nn = int(np.log2(len(dense_state)))

    binaries = [bin(ii)[2:] for ii in range(2**nn)]
    binaries = ["0" * (nn - len(a)) + a for a in binaries]  # Pad with 0s

    ket = []
    for ii, coef in enumerate(dense_state):
        if not np.isclose(np.abs(coef), 0.0):
            if np.isclose(np.imag(coef), 0.0):
                if np.isclose(np.real(coef), 1.0):
                    ket.append("|{}>".format(binaries[ii]))
                else:
                    ket.append("{:.3f}|{}>".format(np.real(coef), binaries[ii]))
            else:
                ket.append("{:.3f}|{}>".format(coef, binaries[ii]))
    print(" + ".join(ket))


def fidelity(psi, phi):
    """
    Returns the fidelity bewteen two quantum states *psi*, *phi* defined as
    :math:`|\\langle\\psi|phi\\rangle|^2`

    Parameters
    ----------
    psi: complex np.array or quimb.core.qarray
            Quantum state
    phi: complex np.array or quimb.core.qarray
            Quantum state

    Returns
    -------
    Fidelity: double real
            Fidelity of the two quantum states
    """

    # Enforcing normalization
    psi /= np.sqrt(np.abs(np.sum(psi.conj() * psi)))
    phi /= np.sqrt(np.abs(np.sum(phi.conj() * phi)))

    return np.abs(np.vdot(psi, phi)) ** 2
