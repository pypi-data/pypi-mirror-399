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
Circuit class used for the simulations.

The circuit is defined as a list of layers, and each layer is a list of
**Instructions**, i.e. a list [QCOperation, sites]. This structure ensures
a simplified analysis of which operations could be executed in parallel.
Furthermore, we point out a couple of further important elements of the
class:

- qregisters: the quantum registers are a way of keeping track of
    "temporary" qubits, that can be added and removed at will. With
    the class methods :func:`add_qregister` and :func:`remove_qregister`
    it is possible to apply such operations. Then, when you apply an operation
    you can always specify to which register you are referring, without having
    to worry about the indexing. In particular, qubits in the same register
    are naturally ordered from left to right. So, if you want to apply a not
    gate to the left-most qubit of the register a1 you will have to call
    `qcirc.x(0, 'a1')`, since the left-most has index 0 for the register 'a1';
- cregisters: the classical registers, where you store the information of
    projective mesurements happened previously on the system and their probability.
    So, the position `idx` of the cregister will hold the tuple
    ``(meas_result, meas_prob``. Each operation
    can be conditioned on the value of a classical register. By calling the
    method :func:`inspect_cregister(creg, idx)` where `creg` is the name of your
    classical register, you can have access to the value of the bit at the
    index idx. If idx=None instead, the full register is treated as the binary
    representation of a decimal number, and that decimal number is given by
    the function. Remember to add the classical registers you need beforehand,
    using :func:`add_cregister`: the quantum circuit start without any of them!

To add operations to the circuit there are three main ways:

- the :func:`add`, to append the operation at the end of the circuit
- some methods to apply widely-used operations to the circuit with a simplified
    notation.
- the :func:`insert` method, to insert an operation at any given layer of the circuit.
    However, this method is dangerous and is not recommended.

The :func:`str_repr` is meant to give a way to visualize the circuit, but is not needed
for the functioning of the class, and it is still under development.
"""

# pylint: disable=too-many-lines

from copy import deepcopy

import numpy as np
import scipy.sparse as sp
from qiskit import QuantumCircuit

from qmatchatea.utils.tn_utils import QCOperators

from .observables import QCObservableStep

# Gates
# Operations
from .operations import (
    ClassicalCondition,
    QCAddSite,
    QCCnot,
    QCCp,
    QCCz,
    QCHadamard,
    QCMeasureProjective,
    QCOperation,
    QCPgate,
    QCRemoveSite,
    QCRenormalize,
    QCSadggate,
    QCSgate,
    QCSwap,
    QCTadggate,
    QCTgate,
    QCXpauli,
    QCYpauli,
    QCZpauli,
)

__all__ = ["Qcircuit"]


# pylint: disable-next=too-many-public-methods, too-many-instance-attributes
class Qcircuit:
    """
    Class used to represent a quantum circuit in
    the qmatchatea library.
    Each layer of the circuit is a list containing
    instructions, i.e. lists [QCOperation, sites].

    - When iterating over the class the iterators returns
      the layers.
    - Iterating over the layer returns the instructions,
      with all permutations of indexes already taken care
      of, based on the quantum registers.

    This means that, once you obtain the operation, you
    simply need to apply it on the defined sites of the mps,
    without further complexity.

    However, you should not run it by yourself, it is
    preferred to use the :func:`QcMps.run_from_qcirc()`.


    Parameters
    ----------
    num_sites: int
        Number of sites in the circuit
    local_dim: int, optional
        Local dimension of the single site. Default to 2.
    """

    def __init__(self, num_sites, local_dim=2) -> None:
        self._num_sites = num_sites
        self._local_dim = local_dim

        # Registers are a way of keeping track of ancilla sites,
        # i.e. sites that get added and removed in runtime.
        # The structure is a name connected to a np.ndarray. The
        # ndarray has as values the true position of the flattened
        # chain. Sites in a register are always ordered in
        # increasing order from left to right
        self._qregisters = {"default": np.arange(num_sites)}

        # Classical registers keep tracks of the result of projective
        # measurement and their probability along the simulation.
        # They are represented as a two-dimensional vector, with the
        # row being the index of the register and the column either
        # the measurement outcome (index=0) or their probability (index=1)
        # They are all initialized to 0, and when retrieved through
        # the cregister function returns the decimal value of their
        # binary representation
        self._cregisters = {}
        self._cl_occupation_map = {}

        # Circuit list. The outer list contains the full circuit,
        # and then each list is a layer. If no operation is applied
        # on a qubit a "wait" operation is applied. To take into
        # account multiple gates and make the wait management easier
        # we encode a logical ndarray where True means occupied and
        # False empty (wait)
        self._data = []
        self._occupation_map = []
        self._add_layer()

        # Number of one-site operations in the circuit
        self._num_one_site_operations = 0
        # Number of two-site operations in the circuit
        self._num_two_site_operations = 0

        # Used in the writing operation for the 1-1 mapping
        self._namelist = []

    def __len__(self):
        """
        Provide number of operations in the circuit
        """
        return self._num_one_site_operations + self._num_two_site_operations

    def __getitem__(self, key):
        """Overwrite the call for lists, you can access the circuit layers using

        .. code-block::
            circ[0]
            >>>  [QCOperation, [0]], [QCOperation, [1, 2]]

        Parameters
        ----------
        key : int
            index of the circuit layer you are interested in

        Returns
        -------
        list
            list of instructions [Operation, sites]
        """
        return self._data[key]

    def __setitem__(self, *args):
        """
        Raise a Not-implemented error, since this is not the way operations
        should be modified.
        """
        raise NotImplementedError(
            "Elements of the circuit cannot be substituted this way"
        )

    def __iter__(self):
        """Iterator protocol"""
        return iter(self._data)

    @property
    def num_sites(self):
        """Number of sites property"""
        return self._num_sites

    @property
    def num_qubits(self):
        """Number of sites property, with another name for simplicity of interfaces"""
        return self._num_sites

    @property
    def local_dim(self):
        """Local dimension property"""
        return self._local_dim

    @property
    def num_layers(self):
        """Number of layers in the circuit"""
        return len(self._data)

    @property
    def num_classical_sites(self):
        """Number of classical sites, i.e. bits"""
        num_cl = 0
        for _, item in self._cregisters.items():
            num_cl += len(item)
        return num_cl

    @property
    def cregisters(self):
        """Return the full list of classical registers"""
        return self._cregisters

    def _add_layer(self):
        """
        Add an empty layer to the circuit, so filled with wait operations
        """
        if len(self._occupation_map) == 0:
            self._occupation_map = np.zeros((self._num_sites, 1), dtype=bool)
        else:
            self._occupation_map = np.hstack(
                (self._occupation_map, np.zeros((self._num_sites, 1), dtype=bool))
            )
        self._data.append([])

    def inspect_cregister(self, register, idx=None):
        """
        Retrieve the decimal value of the binary number
        stored in the classical register `register` if idx=None,
        otherwise it returns the value of the bit at position idx

        Parameters
        ----------
        register : str
            Name of the classical register
        idx : int, optional
            Index of the bit you want to recover. If None, you will
            recover the decimal representation of the full register.
            Default to None.
        """
        if idx is None:
            binary_str = np.array2string(
                self._cregisters[register][:, 0][::-1].astype(int), separator=""
            )
            binary_str = binary_str.replace("[", "").replace("]", "")
            out = int(binary_str, 2)
        else:
            out = int(self._cregisters[register][idx, 0])

        return out

    def add_cregister(self, name, num_bits):
        """
        Add a classical register with name `name` and
        length `num_bits`

        Parameters
        ----------
        name : str
            Name of the classical register
        num_bits : int
            Number of bits the register can store
        """
        self._cregisters[name] = np.zeros((num_bits, 2), dtype=float)
        self._cl_occupation_map[name] = np.zeros(num_bits, dtype=int)

    def modify_cregister(self, value, name, idx):
        """
        Modify the value of a measured bit in the classical register

        Parameters
        ----------
        value : tuple of (int, float)
            Value of the measured qubit to be saved in the classical register
            and of the probability of that outcome
        name : str
            Name of the classical register
        idx : int
            Index of the bit where to save value
        """
        self._cregisters[name][idx, 0] = value[0]
        self._cregisters[name][idx, 1] = np.real(value[1])

    def add_site(self, new_register, position, reference_register="default"):
        """
        Add a site to the circuit, in a specific
        position. The position is the index of the link where
        the site will be added, so 0 is attached to the left,
        num_sites is attached to the right. An intermediate
        number attaches it in the middle.

        Parameters
        ----------
        new_register : str
            Name of the register that will track the index of
            the new site
        position : int
            Index of the link where the new site should be
            added in the register
        reference_register: str
            Register with respect to which the position is
            taken. Default to 'default'.
        """
        if not 0 <= position <= len(self._qregisters[reference_register]):
            raise ValueError(
                f"Site cannot be inserted in position {position}"
                + f" of register {reference_register} with"
                + f" num_sites={len(self._qregisters[reference_register])}"
            )

        # Recover true position on the MPS chain from the position in the register
        if position < len(self._qregisters[reference_register]):
            true_pos = self._qregisters[reference_register][position]
        else:
            true_pos = self._qregisters[reference_register][position - 1] + 1

        # Update all the values after that one, adding one to their
        # relative position
        for idxs in self._qregisters.values():
            mask = idxs >= true_pos
            idxs[mask] += 1

        # Insert the new site in the register
        if new_register in self._qregisters:
            idx = np.nonzero(self._qregisters[new_register] > true_pos)[0]
            if len(idx) == 0:
                self._qregisters[new_register] = np.append(
                    self._qregisters[new_register], true_pos
                )
            else:
                idx = idx[0]
                self._qregisters[new_register] = np.insert(
                    self._qregisters[new_register], idx[0], true_pos
                )
        # Add new register with the new index if it is next
        else:
            self._qregisters[new_register] = np.array([true_pos])

        # Insert a new row in the occupation map and update num_sites
        om_shape = self._occupation_map.shape[1]
        self._occupation_map = np.insert(
            self._occupation_map, true_pos, np.zeros(om_shape), axis=0
        )
        self._num_sites += 1

        # Put the information in the data
        self.add(QCAddSite(position), np.arange(self.num_sites), None)

    def remove_site(self, register, position):
        """
        Remove a site from the circuit. The site to be removed is
        identified by its register and the position in the register.

        Parameters
        ----------
        register : str
            Name of the register where the site to remove is
        position : int
            Index of the site to remove
        """
        if not 0 <= position < len(self._qregisters[register]):
            raise ValueError(
                f"Site cannot be removed in position {position}"
                + f" of register {register} with"
                + f" num_sites={len(self._qregisters[register])}"
            )

        # Put the information in the data
        self.add(QCRemoveSite(position), np.arange(self.num_sites), None)

        # Recover true position on the MPS chain from the position in the register
        true_pos = self._qregisters[register][position]

        # Update all the values after that one, subtracting one to their
        # relative position
        for idxs in self._qregisters.values():
            mask = idxs > true_pos
            idxs[mask] -= 1

        # Remove the site from the register
        self._qregisters[register] = np.delete(self._qregisters[register], position)

        # Remove row from the occupation map and update num_sites
        self._num_sites -= 1
        self._occupation_map = np.delete(self._occupation_map, true_pos, axis=0)

    def add_qregister(self, new_register, positions, reference_register="default"):
        """
        Add a new register to the circuit, in a specific
        positions. The positions is the index of the link where
        the site will be added, so 0 is attached to the left,
        num_sites is attached to the right. An intermediate
        number attaches it in the middle.
        This link number is taken with respect to the
        reference register.

        This function is a simple loop over add_site, but we expect
        it to be a very useful function in runtime

        Parameters
        ----------
        new_register : str
            Name of the register that will track the index of
            the new site
        positions : array-like of ints
            Index of the link where the new site should be
            added in the register
        reference_register: str
            Register with respect to which the position is
            taken. Default to 'default'.
        """
        for position in positions:
            self.add_site(new_register, position, reference_register)

    def remove_qregister(self, register):
        """
        Remove a register from the circuit.

        Parameters
        ----------
        register : str
            Name of the register to be removed
        """
        num_reps = len(self._qregisters[register])
        for _ in range(num_reps):
            self.remove_site(register, 0)

        # Remove the key from the dictionary
        del self._qregisters[register]

    # pylint: disable-next=too-many-branches
    def add(self, operation, sites, register="default"):
        """
        Add an operation to the circuit

        Parameters
        ----------
        operation : :class:`QCOperation`
            Operation to be added to the
        sites : integer of array-like of integers
            Qubits to which the operation is applied
        register : str or array of str
            Register to which the operations are applied.
            Default are both to default.
        """
        if not issubclass(type(operation), QCOperation):
            raise TypeError(
                f"operation must be of type QCOperation, not {type(operation)}"
            )
        if isinstance(sites, int):  # Trasnsfor integer in array-like list
            sites = [sites]
            self._num_one_site_operations += 1
        else:
            self._num_two_site_operations += 1
        if isinstance(register, str):
            register = [register] * len(sites)

        if register is not None:
            for idx, site in enumerate(sites):
                sites[idx] = self._qregisters[register[idx]][site]

        sites = list(sites)
        last_occupied = -1
        for site in sites:
            temp = np.where(self._occupation_map[site, :])[0]
            temp = [-1] if len(temp) == 0 else temp
            last_occupied = max(last_occupied, temp[-1])

        # Check for classical dependencies
        if operation.is_conditioned:
            if operation.c_if.idx is None:
                for occ in self._cl_occupation_map[operation.c_if.creg]:
                    last_occupied = max(last_occupied, occ)
                self._cl_occupation_map[operation.c_if.creg] = last_occupied + 1
            else:
                last_occupied = max(
                    last_occupied,
                    self._cl_occupation_map[operation.c_if.creg][operation.c_if.idx],
                )
                self._cl_occupation_map[operation.c_if.creg][operation.c_if.idx] = (
                    last_occupied + 1
                )
        # Check for measures
        if hasattr(operation, "cregister"):
            occ = self._cl_occupation_map[operation.cregister][operation.cl_idx]
            last_occupied = max(last_occupied, occ)
            self._cl_occupation_map[operation.cregister][operation.cl_idx] = (
                last_occupied + 1
            )

        # Check if the last occupied is on the last layer,
        # and add a layer if True
        if last_occupied == self._occupation_map.shape[1] - 1:
            self._add_layer()

        # Add the operation on data and occupation map
        instruction = [operation, sites]
        self._data[last_occupied + 1].append(instruction)
        self._occupation_map[sites, last_occupied + 1] = True
        # print(self._occupation_map)

    # pylint: disable-next=too-many-arguments
    def insert(self, operation, sites, layer, register="default", inlayer=True):
        """
        Insert an operation after a specific layer on the sites
        If inlayer is True simply add it into the layer without
        checking if an operation is already there, otherwise check
        for the operation and insert a new layer

        Parameters
        ----------
        operation : :class:`QCOperation`
            Operation to be added to the
        sites : int of array-like of integers
            Qubits to which the operation is applied
        layer: int
            integer identifying the layer after which we want to
            insert the operation
        register : str or array of str
            Register to which the operations are applied.
            Default are both to default.
        inlayer: bool, optional
            If False, and the position in the layer is already occupied,
            add a new layer. Otherwise add it to that layer nevertheless.
            Default to True.
        """
        if not issubclass(type(operation), QCOperation):
            raise TypeError(
                f"operation must be of type QCOperation, not {type(operation)}"
            )
        if np.isscalar(sites):  # Trasnsfor integer in array-like list
            sites = [sites]
        if isinstance(register, str):
            register = [register] * len(sites)

        for idx, site in enumerate(sites):
            sites[idx] = self._qregisters[register[idx]][site]

        instruction = [operation, sites]
        # Check if the positions sites in layer is occupied
        is_occupied = self._occupation_map[sites, layer]
        if not np.isscalar(is_occupied):
            is_occupied = any(is_occupied)

        if (not inlayer) and is_occupied:
            # Insert new layer in occupation map and data
            self._occupation_map = np.insert(
                self._occupation_map, layer + 1, False, axis=1
            )
            self._data.insert(layer + 1, [])
            self._occupation_map[sites, layer + 1] = True
            layer += 1
        elif not inlayer and not is_occupied:
            self._occupation_map[sites, layer] = True
        # Insert instruction
        self._data[layer].append(instruction)

    @classmethod
    def from_qiskit(cls, qc):
        """
        Initialize the Qcircuit class from a qiskit quantum circuit

        Parameters
        ----------
        qc : :class:`QuantumCircuit`
            qiskit QuantumCircuit that will initialize the Qcircuit
        """
        if not isinstance(qc, QuantumCircuit):
            raise TypeError(f"qc must be of type QuantumCircuit, not {type(qc)}")

        # Reinitialize values
        qcirc = cls(qc.num_qubits)

        for instance in qc.data:
            gate = instance[0]
            if gate.name == "barrier":
                pass
            elif gate.name == "measure":
                qcirc.measure_projective(
                    [qub.index for qub in instance[1]],
                    [cl_idx.index for cl_idx in instance[2]],
                )
            else:
                operation = QCOperation(gate.name, gate.to_matrix)
                qcirc.add(operation, sites=[qub.index for qub in instance[1]])

        return qcirc

    def fill_qcoperators(self, operators):
        """
        Fill the QCoperators dictionary with all the operators
        in the Qcircuit

        Parameters
        ----------
        operators: :class:`QCOperators`
            operators class to fill
        """
        if not isinstance(operators, QCOperators):
            raise TypeError(f"qc must be of type QuantumCircuit, not {type(operators)}")

        for layer in self._data:
            for instruction in layer:
                operation = instruction[0]
                sites = instruction[1]
                name = operation.name
                matrix = operation.operator
                search = True
                while search:
                    # If the operator has already been written, even if parametric,
                    # don't add it again. Instead, if it has sufficiently different
                    # parameters, add it with a new name
                    if name in operators:
                        ii = 0
                        if np.allclose(matrix, operators[name]):
                            search = False
                        else:
                            name = operation.name + str(ii)
                            ii += 1
                    else:
                        search = False
                        operators[name] = matrix.reshape([self.local_dim] * len(sites))
                        self._namelist.append(name)

    def write(self, dest, id_mapping):
        """
        Write on file (originally written for the Fortran simulator), with the correct formatting

        Parameters
        ----------
        dest: str or filehandle
            If str, write on that file. Otherwise, write using that filehandle
        id_mapping: dict
            Mapping from the operator name to the operator id
        """
        if isinstance(dest, str):
            fh = open(dest, "w+")
        elif hasattr(dest, "write"):
            fh = dest
        else:
            raise TypeError("`dest` for `write` neither str nor writeable.")

        fh.write(str(self.num_sites) + "\n")
        fh.write(str(self.num_classical_sites) + "\n")
        fh.write(str(len(self) + len(self._data)) + "\n")

        ii = 0
        for layer in self._data:
            for instruction in layer:
                operation = instruction[0]
                sites = instruction[1]
                fh.write(
                    operation.name, id_mapping(self._namelist[ii]), len(sites), 0, "\n"
                )
                fh.write("\t")
                for site in sites:
                    fh.write(str(site + 1) + " ")  # Qubit numbers
                for clbit in range(0):
                    fh.write(str(clbit + 1) + " ")  # Classical bit numbers
                fh.write("\n")
                ii += 1
            fh.write("barrier", "1", "1", "1", "\n", "\n")

    # pylint: disable-next=too-many-branches
    def to_matrix(self, sparse=False, max_qubit_equivalent=20, qiskit_order=True):
        """
        Return the matrix representation of the circuit.
        It is a unitary matrix if no noise/non-unitary matrix
        has been applied. Notice that this computation scales as
        :math:`d^{2n}`, where :math:`d` is the local dimension of the
        single degree of freedom and :math:`n` the number of sites.
        Furthermore, the function is not optimized and might take long.

        Parameters
        ----------
        sparse : bool, optional
            If True, return a csr sparse matrix instead of a numpy array.
            Default to False.
        max_qubit_equivalent: int, optional
            Maximum number of qubit sites the MPS can have and still be
            transformed into a matrix.
            If the number of sites is greater, it will throw an exception.
            Default to 20.
        qiskit_order : bool, optional
            If True, return the matrix using qiskit ordering. Default to
            True.

        Returns
        -------
        matrix : np.ndarray or sp.csr_matrix
            Numpy array or sparse matrix representing the system unitary
        """
        if self.local_dim**self.num_sites > 2**max_qubit_equivalent:
            raise RuntimeError(
                "Maximum number of sites for the matrix is "
                + f"fixed to the equivalent of {max_qubit_equivalent} qubit sites"
            )

        # Define the identity call based on the sparse flag
        if sparse:
            iden = sp.identity
            kron = sp.kron
            swap = sp.csr_matrix(QCSwap().operator)
        else:
            iden = np.identity
            kron = np.kron
            swap = QCSwap().operator

        matrix = iden(self.local_dim**self.num_sites)

        for layer in self._data:
            for instruction in layer:
                op_mat = instruction[0].operator
                if sparse:
                    op_mat = sp.csr_matrix(op_mat)
                sites = instruction[1]
                diff = max(sites) - min(sites)

                if len(sites) == 2:
                    # Create matrix if non adjacent
                    if diff > 1:
                        circ = Qcircuit(diff + 1, self.local_dim)
                        for ii in range(diff - 1):
                            circ.add(QCSwap(), [ii, ii + 1])
                        if sites[0] < sites[1]:
                            circ.add(instruction[0], [diff - 1, diff])
                        else:
                            circ.add(instruction[0], [diff, diff - 1])
                        for ii in range(diff - 1, 0, -1):
                            circ.add(QCSwap(), [ii, ii - 1])
                        op_mat = circ.to_matrix(sparse=sparse)

                    # Revert the direction if target is above control
                    elif sites[0] < sites[1]:
                        op_mat = swap @ op_mat @ swap

                # Reverse all the indexing if the qiskit order is required
                if qiskit_order:
                    sites = self.num_sites - 1 - np.array(sites)
                    if op_mat.shape == (4, 4):
                        op_mat = swap @ op_mat @ swap

                if min(sites) > 0:
                    op_mat = kron(iden(2 ** (min(sites))), op_mat)
                if max(sites) < self.num_sites - 1:
                    op_mat = kron(op_mat, iden(2 ** (self.num_sites - max(sites) - 1)))

                matrix = op_mat @ matrix

        return matrix

    # pylint: disable-next=too-many-locals
    def str_repr(self):
        """
        Get the string representation of the circuit
        """

        # Initialization
        str_repr = []
        biggest_idx_len = len(f"q_{self.num_sites-1} ")
        for idx in range(self.num_sites):
            str_idx = f"q_{idx} "
            str_idx += " " * (biggest_idx_len - len(str_idx))
            void = " " * biggest_idx_len

            str_repr.append([void, str_idx, void])

        for layer in self._data:
            used_sites = []
            max_len = 0
            for instruction in layer:
                op_str = instruction[0].string_rep.split("\n")
                sites = instruction[1]
                used_sites += list(sites)

                for idx, site in enumerate(sites):
                    current_str = op_str[idx * 3 : (idx + 1) * 3]
                    if len(current_str) == 0:
                        current_str = op_str[:3]

                    for idx_str, str1 in enumerate(current_str):
                        str_repr[site][idx_str] += str1
                        max_len = max(max_len, len(str1))

            empty_idxs = np.setdiff1d(np.arange(self.num_sites), np.array(used_sites))
            for site in empty_idxs:
                str_repr[site][0] += " " * max_len
                str_repr[site][1] += "─" * max_len
                str_repr[site][2] += " " * max_len
        circ_rep = ""
        for site in str_repr:
            circ_rep += "\n".join(site)

        return circ_rep

    ################################################################
    ## Dummy methods for the most used operations to simplify the ##
    ## life of the programmer. You could still use the add method ##
    ## since this is simply a dummy rewriting.                    ##
    ################################################################

    def x(self, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply a x gate in the position pos in the qregister qreg

        Parameters
        ----------
        pos : int
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : str or None, optional
            Quantum register where you want to apply the operation.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCXpauli(c_if), pos, qreg)

    def y(self, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply a y gate in the position pos in the qregister qreg

        Parameters
        ----------
        pos : int
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : str or None, optional
            Quantum register where you want to apply the operation.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCYpauli(c_if), pos, qreg)

    def z(self, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply a z gate in the position pos in the qregister qreg

        Parameters
        ----------
        pos : int
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : str or None, optional
            Quantum register where you want to apply the operation.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCZpauli(c_if), pos, qreg)

    def h(self, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply a hadamard gate in the position pos in the qregister qreg

        Parameters
        ----------
        pos : int
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : str or None, optional
            Quantum register where you want to apply the operation.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCHadamard(c_if), pos, qreg)

    def s(self, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply a S gate in the position pos in the qregister qreg

        Parameters
        ----------
        pos : int
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : str or None, optional
            Quantum register where you want to apply the operation.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCSgate(c_if), pos, qreg)

    def sadg(self, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply the adjoint of an S gate in the position pos
        in the qregister qreg

        Parameters
        ----------
        pos : int
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : str or None, optional
            Quantum register where you want to apply the operation.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCSadggate(c_if), pos, qreg)

    def t(self, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply a T gate in the position pos in the qregister qreg

        Parameters
        ----------
        pos : int
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : str or None, optional
            Quantum register where you want to apply the operation.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCTgate(c_if), pos, qreg)

    def tadg(self, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply the adjoint of an T gate in the position pos
        in the qregister qreg

        Parameters
        ----------
        pos : int
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : str or None, optional
            Quantum register where you want to apply the operation.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCTadggate(c_if), pos, qreg)

    def p(self, theta, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply a Phase gate in the position pos in the qregister qreg
        with a phase theta

        Parameters
        ----------
        theta : float
            Rotation angle for the phase gate
        pos : int
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : str or None, optional
            Quantum register where you want to apply the operation.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCPgate(theta, c_if), pos, qreg)

    def cx(self, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply a controlled not gate in the position pos
        in the qregisters qreg. pos should be an array, qreg should
        be an array if the qubits are in different qregisters

        Parameters
        ----------
        pos : list of two ints
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : list of str, str or None, optional
            Quantum registers where you want to apply the operation.
            If only a str is provided, the program assumes you want to
            apply the gate inside the same quantum register. If a list of
            two strings is provided, the gate is applied between different
            quantum registers.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'.
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCCnot(c_if), pos, qreg)

    def cz(self, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply a controlled z gate in the position pos
        in the qregisters qreg. pos should be an array, qreg should
        be an array if the qubits are in different qregisters

        Parameters
        ----------
        pos : list of two ints
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : list of str, str or None, optional
            Quantum registers where you want to apply the operation.
            If only a str is provided, the program assumes you want to
            apply the gate inside the same quantum register. If a list of
            two strings is provided, the gate is applied between different
            quantum registers.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'.
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCCz(c_if), pos, qreg)

    def cp(self, theta, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply a controlled phase gate in the position pos
        in the qregisters qreg. pos should be an array, qreg should
        be an array if the qubits are in different qregisters

        Parameters
        ----------
        theta : float
            Rotation angle for controlled phase gate
        pos : list of two ints
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : list of str, str or None, optional
            Quantum registers where you want to apply the operation.
            If only a str is provided, the program assumes you want to
            apply the gate inside the same quantum register. If a list of
            two strings is provided, the gate is applied between different
            quantum registers.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'.
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCCp(theta, c_if), pos, qreg)

    def swap(self, pos, qreg="default", c_if=ClassicalCondition()):
        """
        Apply a swap gate in the position pos
        in the qregisters qreg. pos should be an array, qreg should
        be an array if the qubits are in different qregisters

        Parameters
        ----------
        pos : list of two ints
            Index, relative to the quantum register, where you want to
            apply the operation
        qreg : list of str, str or None, optional
            Quantum registers where you want to apply the operation.
            If only a str is provided, the program assumes you want to
            apply the gate inside the same quantum register. If a list of
            two strings is provided, the gate is applied between different
            quantum registers.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'.
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCSwap(c_if), pos, qreg)

    # pylint: disable-next=too-many-arguments
    def gate(self, gate, pos, name="op", qreg="default", c_if=ClassicalCondition()):
        """
        Apply a matrix to the circuit. The dimensions of
        the matrix should be consistent with the number of
        qubits to which it should be applied

        Parameters
        ----------
        gate : np.ndarray
            gate matrix
        pos : int or array-like of ints
            Indexes of the sites to which it should be applied
        name : str, optional
            Unique identifier of the gate. Default to 'op'
        qreg : str or array-like of str, optional
            qregister to which the gate should be applied
        """
        if isinstance(pos, int):
            pos = [pos]

        if gate.shape[1] != self.local_dim ** len(pos):
            raise ValueError(
                f"Gate shape {gate.shape[1]} is incompatible "
                + "with the local dimension and the number of sites to which "
                + f"it is applied. Should be {self.local_dim**len(pos)}"
            )
        op = QCOperation(name, lambda: gate, conditioned=c_if)
        self.add(op, pos, qreg)

    # pylint: disable-next=too-many-arguments
    def measure_projective(
        self,
        pos,
        cl_idx,
        qreg="default",
        creg="default",
        selected_output=None,
        c_if=ClassicalCondition(),
    ):
        """
        Apply a projective measurement in the position pos
        in the qregister qreg. You can choose the output of
        the measure. The result is stored in the classical
        qregister creg at index cl_idx

        Parameters
        ----------
        pos : int
            Index, relative to the quantum register, where you want to
            apply the operation
        cl_idx : int
            Index of the classical register where to store the result
            of the measurement
        qreg : str or None, optional
            Quantum register where you want to apply the operation.
            If None, the "raw index" is considered, i.e. without taking
            into account the quantum register reindexing.
            Default to 'default'
        cregister : str, optional
            Classical register where the result of the measurement
            is stored. Default to 'default'
        selected_output : int, optional
            Output selected a priori. Default to None.
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation
            on the simulation.
        """
        self.add(QCMeasureProjective(cl_idx, selected_output, creg, c_if), pos, qreg)

    def renormalize(self, c_if=ClassicalCondition()):
        """
        Renormalize the state

        Parameters
        ----------
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation on the
            simulation
        """
        self.insert(QCRenormalize(c_if), 0, -1)

    # pylint: disable-next=too-many-arguments
    def measure_observables(
        self, name, observables, operators, qreg=None, c_if=ClassicalCondition()
    ):
        """
        Perform a measurement step of all the observables defined in
        the observable parameter.

        Parameters
        ----------
        name : str
            Name of the observables step
        observables: :class:`TNObservables`
            Observables to be measured at this step
        operators: :class:`QCOperators`
            Class containing the operators present in the Observables
        qreg : str or None, optional
            Quantum register where the observables should be measured.
            If None, they are measured on the FULL circuit, regardless
            of the registers
        c_if : :py:class:`ClassicalCondition`, optional
            Classical condition to be checked for applying the operation on the
            simulation
        """
        obs = QCObservableStep(name, observables, operators, c_if)
        obs.num_sites = self.num_sites

        # We want to apply the measurement to the whole circuit regardless
        # of the register
        if qreg is None:
            obs.snap_current_qregisters(self._qregisters)
            self.add(obs, np.arange(self.num_sites - 1), register=qreg)
        # We want to apply the measurements to a single part of the circuit
        else:
            qreg_val = deepcopy(self._qregisters[qreg])
            obs.snap_current_qregisters({qreg: qreg_val})
            # Adjust the index of the observables based on specific sites
            obs.adjust_obs_indexing()
            # Add occupying the whole interested quantum register
            self.add(obs, np.arange(self.num_sites - 1), register=None)
