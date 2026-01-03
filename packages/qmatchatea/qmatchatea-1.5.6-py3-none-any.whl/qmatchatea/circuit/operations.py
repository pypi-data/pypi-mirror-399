# This code is part of qmatchatea.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

r"""
Operations that can be applied on the Qcircuit class.
The idea of the module is the following:

- An Operation is whichever kind of operation applied to the circuit
- A ClassicalCondition is a condition on the application of an Operation
  based on the measurement of previous qudits

The available operations in the library at the moment are:

- ``QCMeasureProjective``, apply a projective measurement on the system
- ``QCRenormalize``, renormalize the quantum state to :math:`\sqrt{<\psi|\psi>}=1`
- ``QCAddSite``, add a site to the MPS.
- ``QCRemoveSite``, remove a site from the MPS. It must be in a product state with the rest.
- ``QCObservablesStep``, perform a step of measurement of the observables

The available gates instead are:

- ``QCZpauli``,
- ``QCXpauli``,
- ``QCYpauli``,
- ``QCHadamard``,
- ``QCSgate``,
- ``QCTgate``,
- ``QCSadggate``,
- ``QCTadggate``,
- ``QCPgate``,
- ``QCSwap``,
- ``QCCnot``,
- ``QCCz``
- ``QCCp``

You can always define your own gate through :class:`QCOperation`.

In particular, for the definition of noisy gates, the procedure of the definition of a new
operation is to be preferred over modifying an exsisting one.

Then, the list `[QCOperation, sites]` is called **Instruction**.
"""

import numpy as np

__all__ = [
    "QCOperation",
    "ClassicalCondition",
    "QCMeasureProjective",
    "QCRenormalize",
    "QCAddSite",
    "QCRemoveSite",
    "QCZpauli",
    "QCXpauli",
    "QCYpauli",
    "QCSwap",
    "QCCnot",
    "QCCz",
    "QCHadamard",
    "QCSgate",
    "QCTgate",
    "QCSadggate",
    "QCTadggate",
    "QCPgate",
    "QCCp",
]


class ClassicalCondition:
    """
    Class to handle conditions on classically-controlled
    operations

    Parameters
    ----------
    cregister : str, optional
        Name of the classical register relative to the condition
    value : int, optional
        Value that the register should assume
    idx : int, optional
        If provided, the index of the register to check.
        If not provided, the decimal number connected to the
        binary representation of the register is used.
    """

    def __init__(self, cregister=None, value=None, idx=None):
        self.creg = cregister
        self.value = value
        self.idx = idx

        if cregister is None:
            self._is_initialized = False
        else:
            self._is_initialized = True

    @property
    def is_initialized(self):
        """Initialization property"""
        if self.creg is None:
            self._is_initialized = False
        else:
            self._is_initialized = True

        return self._is_initialized

    def is_satisfied(self, qcirc):
        """
        Check if the classical condition is satisfied

        Parameters
        ----------
        qcirc : :py:class:`QCircuit`
            Quantum circuit class

        Returns
        -------
        bool
            True if the condition is satisfied, False otherwise
        """
        # If the condition is not initialized the condition
        # is automatically satisfied
        if self.is_initialized:
            value = qcirc.inspect_cregister(self.creg, self.idx)
            is_satisfied = value == self.value
        else:
            is_satisfied = True

        return is_satisfied


class QCOperation:
    """
    Operation on the circuit class.

    name: str
        Unique name of the operation
    operator: function
        Python function which returns the array of the operator as np.ndarray
    operator_parameters: list, optional
        List of operator parameters if needed. Default to None.
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(
        self, name, operator, operator_parameters=None, conditioned=ClassicalCondition()
    ):
        self._name = name
        self._operator = operator
        self._operator_parameters = (
            [] if operator_parameters is None else operator_parameters
        )
        if np.isscalar(self._operator_parameters):
            self._operator_parameters = [self._operator_parameters]
        self._condition = conditioned

    def __repr__(self):
        """
        Return the class name as representation
        """
        return self.__class__.__name__

    @property
    def operator(self):
        """
        Returns the operator matrix as np.ndarray
        """
        return self._operator(*self._operator_parameters)

    @property
    def name(self):
        """Name property"""
        return self._name

    @property
    def is_conditioned(self):
        """True if there is a classical condition on the application of the gate"""
        return self._condition.is_initialized

    @property
    def c_if(self):
        """True if there is a classical condition on the application of the gate"""
        return self._condition

    def is_parametric(self):
        """Returns True if the operation is parametrized"""
        is_param = len(self._operator_parameters) == 0
        return is_param

    @property
    def string_rep(self):
        """Return the string representation for printing"""
        str_rep = f"─ {self.name} ─"
        void = " " * len(str_rep)
        string = void + "\n" + str_rep + "\n" + void

        return string


class QCRenormalize(QCOperation):
    """
    Renormalize the state when this operation is encountered

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "renormalize", None, conditioned=conditioned)


class QCAddSite(QCOperation):
    """
    Add a site to the Qcircuit

    Parameters
    ----------
    position : int
        Position of the link where the site will be added
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, position, conditioned=ClassicalCondition()):
        self.position = position
        QCOperation.__init__(self, "add_site", None, conditioned=conditioned)


class QCRemoveSite(QCOperation):
    """
    Remove a site to the Qcircuit

    Parameters
    ----------
    position : int
        Position of the site to remove
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, position, conditioned=ClassicalCondition()):
        self.position = position
        QCOperation.__init__(self, "remove_site", None, conditioned=conditioned)


class QCMeasureProjective(QCOperation):
    """
    Apply a projective measurement to the circuit, possibly
    selecting its output

    Parameters
    ----------
    cl_idx : int
        Position of the classical register where the measurement
        will be stored
    selected_output : int, optional
        Output selected a priori. Default to None
    cregister : str, optional
        Classical register where the result of the measurement
        is stored. Default to 'default'
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(
        self,
        cl_idx,
        selected_output=None,
        cregister="default",
        conditioned=ClassicalCondition(),
    ):
        QCOperation.__init__(self, "measure", None, conditioned=conditioned)
        self._selected_output = selected_output
        self.cregister = cregister
        self.cl_idx = cl_idx

    @property
    def selected_output(self):
        """A priori selected output"""
        return self._selected_output


class QCSwap(QCOperation):
    """
    Swap operation between adjacent qubits.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{SWAP} =
        \\begin{pmatrix}
        1 & 0 & 0 & 0 \\\\
        0 & 0 & 1 & 0 \\\\
        0 & 1 & 0 & 0 \\\\
        0 & 0 & 0 & 1 \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "swap", None, conditioned=conditioned)

    @property
    def operator(self):
        """
        Overwriting operator with swap
        """
        return np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])


class QCCnot(QCOperation):
    """
    Cnot operation between adjacent qubits.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{CNOT} =
        \\begin{pmatrix}
        1 & 0 & 0 & 0 \\\\
        0 & 1 & 0 & 0 \\\\
        0 & 0 & 0 & 1 \\\\
        0 & 0 & 1 & 0 \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, swap=True, conditioned=ClassicalCondition()):
        self.swap = swap
        QCOperation.__init__(self, "cx", None, conditioned=conditioned)

    @property
    def operator(self):
        """
        Overwriting operator with cnot
        """
        cnot = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])
        if self.swap:
            swap = QCSwap().operator
            cnot = swap @ cnot @ swap
        return cnot


class QCCz(QCOperation):
    """
    Cz operation between adjacent qubits.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{CZ} =
        \\begin{pmatrix}
        1 & 0 & 0 & 0 \\\\
        0 & 1 & 0 & 0 \\\\
        0 & 0 & 1 & 0 \\\\
        0 & 0 & 0 & -1 \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "cz", None, conditioned=conditioned)

    @property
    def operator(self):
        """
        Overwriting operator with cz
        """
        cz_op = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]])
        return cz_op

    @property
    def string_rep(self):
        """Return the string representation for printing"""
        str_rep = f"─ {self.name} ─"
        void = " " * len(str_rep)
        string = void + "\n" + str_rep + "\n" + void + "\n"
        string += void + "\n" + str_rep + "\n" + void

        return string


class QCHadamard(QCOperation):
    """
    Hadamard operation.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{H} =\\frac{1}{\\sqrt{2}}
        \\begin{pmatrix}
        1 & 1  \\\\
        1 & -1  \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "h", None, conditioned=conditioned)

    @property
    def operator(self):
        """
        Overwriting operator with hadamard
        """
        return np.array([[1, 1], [1, -1]]) / np.sqrt(2)


class QCZpauli(QCOperation):
    """
    Pauli Z operation.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{Z} =
        \\begin{pmatrix}
        1 & 0  \\\\
        0 & -1  \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "z", None, conditioned=conditioned)

    @property
    def operator(self):
        """
        Overwriting operator with sigma_z
        """
        return np.array([[1, 0], [0, -1]])


class QCXpauli(QCOperation):
    """
    Pauli X operation.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{X} =
        \\begin{pmatrix}
        0 & 1  \\\\
        1 & 0  \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "x", None, conditioned=conditioned)

    @property
    def operator(self):
        """
        Overwriting operator with sigma_x
        """
        return np.array([[0, 1], [1, 0]])


class QCYpauli(QCOperation):
    """
    Pauli Y operation.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{Y} =
        \\begin{pmatrix}
        0 & -i  \\\\
        i & 0  \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "y", None, conditioned=conditioned)

    @property
    def operator(self):
        """
        Overwriting operator with sigma_y
        """
        return np.array([[0, -1j], [1j, 0]])


class QCSgate(QCOperation):
    """
    Phase gate with phase :math:`\\pi/2`.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{S} =
        \\begin{pmatrix}
        1 & 0  \\\\
        0 & i  \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "s", None, conditioned=conditioned)

    @property
    def operator(self):
        """
        Overwriting operator with phase gate
        """
        return np.array([[1, 0], [0, 1j]])


class QCTgate(QCOperation):
    """
    Phase gate with phase :math:`\\pi/4`.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{T} =
        \\begin{pmatrix}
        1 & 0  \\\\
        0 & \\frac{1}{\\sqrt{2}}(1+i)  \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "t", None, conditioned=conditioned)

    @property
    def operator(self):
        """
        Overwriting operator with phase gate
        """
        return np.array([[1, 0], [0, (1 + 1j) / np.sqrt(2)]])


class QCTadggate(QCOperation):
    """
    Phase gate with phase :math:`-\\pi/4`.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{T}^\\dagger =
        \\begin{pmatrix}
        1 & 0  \\\\
        0 & \\frac{1}{\\sqrt{2}}(1-i)  \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "tdg", None, conditioned=conditioned)

    @property
    def operator(self):
        """
        Overwriting operator with adjoint t gate
        """
        return np.array([[1, 0], [0, (1 - 1j) / np.sqrt(2)]])


class QCSadggate(QCOperation):
    """
    Adjoint of the phase gate with phase :math:`3\\pi/2`.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{S}^\\dagger =
        \\begin{pmatrix}
        1 & 0  \\\\
        0 & -i  \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "sadg", None, conditioned=conditioned)

    @property
    def operator(self):
        """
        Overwriting operator with adjoint s gate
        """
        return np.array([[1, 0], [0, -1j]])


class QCPgate(QCOperation):
    """
    Phase gate with phase :math:`\\theta`.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{P}(\\theta) =
        \\begin{pmatrix}
        1 & 0  \\\\
        0 & e^{i\\theta}  \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, theta, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "p", self.matrix, theta, conditioned=conditioned)

    @staticmethod
    def matrix(theta):
        """
        Overwriting operator with phase gate
        """
        return np.array([[1, 0], [0, np.exp(theta * 1j)]])


class QCCp(QCOperation):
    """
    Controlled Phase gate with phase :math:`\\theta`.
     Its matrix representation is as follows:

    .. math::

        \\mathrm{CP}(\\theta) =
        \\begin{pmatrix}
        1 & 0 & 0 & 0 \\\\
        0 & 1 & 0 & 0 \\\\
        0 & 0 & 1 & 0 \\\\
        0 & 0 & 0 & e^{i\\theta} \\\\
        \\end{pmatrix}

    Parameters
    ----------
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.
    """

    def __init__(self, theta, conditioned=ClassicalCondition()):
        QCOperation.__init__(self, "cp", self.matrix, theta, conditioned=conditioned)

    @staticmethod
    def matrix(theta):
        """
        Overwriting operator with controlled phase gate
        """
        cz_op = np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, np.exp(theta * 1j)]]
        )

        return cz_op
