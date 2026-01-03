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
The :py:class:`QCEmulator` class enables full-python simulations.

Functions and classes
~~~~~~~~~~~~~~~~~~~~~

"""

# pylint: disable=protected-access, bare-except

import os
import time
import warnings
from copy import deepcopy

import numpy as np
import psutil
import qredtea as qrt
import qtealeaves.tensors as qtt
from qiskit import QuantumCircuit
from qtealeaves.abstracttns.abstract_tn import _AbstractTN
from qtealeaves.convergence_parameters import TNConvergenceParameters
from qtealeaves.emulator import MPIMPS, MPS, TTN
from qtealeaves.mpos import DenseMPO
from qtealeaves.observables import TNObservables
from qtealeaves.simulation.tn_simulation import run_tn_measurements

from .circuit import Qcircuit
from .circuit.observables import QCObservableStep
from .utils import QCBackend, SimulationResults
from .utils.tn_utils import QCOperators
from .utils.utils import QCCheckpoints, QCConvergenceParameters

__all__ = ["QCEmulator", "run_py_simulation"]


class QCEmulator:
    """
    Emulator class to run quantum circuits, powered by either
    TTNs or MPS.


    Parameters
    ----------

    num_sites: int
        Number of sites
    convergence_parameters: :py:class:`QCConvergenceParameters`
        Class for handling convergence parameters. In particular, in the MPS simulator we are
        interested in:
        - the *maximum bond dimension* :math:`\\chi`;
        - the *cut ratio* :math:`\\epsilon` after which the singular values are neglected, i.e.
        if :math:`\\lambda_1` is the bigger singular values then after an SVD we neglect all the
        singular values such that :math:`\\frac{\\lambda_i}{\\lambda_1}\\leq\\epsilon`
    local_dim: int, optional
        Local dimension of the degrees of freedom. Default to 2.
    tensor_backend: TensorBackend, optional
        Contains all the information on the tensors, such as dtype and device.
        Default to TensorBackend() (dtype=np.complex128, device="cpu").
    qc_backend: QCBackend, optional
        Backend for the qmatchatea emulation, containing the backend and other important infos.
        Default to QCBackend() (ansatz="MPS", precision="A", device="cpu")
    initialize: str, optional
        Initialization procedure.
        Default to "vacuum", the 0000...0 state.
        Available: "random", "vacuum", path_to_file
    """

    ansatzes = {"MPS": MPS, "TTN": TTN, "MPIMPS": MPIMPS}

    # pylint: disable-next=too-many-arguments
    def __init__(
        self,
        num_sites,
        convergence_parameters=QCConvergenceParameters(),
        local_dim=2,
        tensor_backend=qtt.TensorBackend(),
        qc_backend=QCBackend(),
        initialize="vacuum",
    ):
        if not isinstance(convergence_parameters, TNConvergenceParameters):
            raise TypeError(
                "convergence_parameters must be of the QCConvergenceParameters class"
            )
        if qc_backend.device != tensor_backend.device:
            raise ValueError(
                "Tensor backend and QCBackend have different devices, "
                + f"{tensor_backend.device} and {qc_backend.device} respectively."
            )

        self._trunc_tracking_mode = convergence_parameters.trunc_tracking_mode
        self._qc_backend = qc_backend

        # Classical registers to hold qiskit informations
        self.cl_regs = {}

        # Observables measured
        self.is_measured = [
            True,
            False,
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            False,
            False,
        ]

        # If a TTN, pad with empty sites until you get to a power of 2 sites
        if self.ansatz == "TTN":
            if num_sites & (num_sites - 1) == 0:
                exponent = np.ceil(np.log2(num_sites))
                num_sites = int(2**exponent)

        # Initialize based on the intialized keyword
        if os.path.isfile(initialize):
            if initialize.endswith(
                "pkl" + self.ansatzes[qc_backend.ansatz.upper()].extension
            ):
                self.emulator = self.ansatzes[qc_backend.ansatz.upper()].read_pickle(
                    filename=initialize
                )
            elif initialize.endswith(
                self.ansatzes[qc_backend.ansatz.upper()].extension
            ):
                self.emulator = self.ansatzes[qc_backend.ansatz.upper()].read(
                    filename=initialize,
                    tensor_backend=tensor_backend,
                    cmplx=np.iscomplex(np.empty(1, dtype=tensor_backend.dtype))[0],
                    order="F",
                )
            else:
                raise IOError(f"Extension {initialize} not supported by QCEmulator")

            self.emulator._tensor_backend = tensor_backend
            self.emulator._convergence_parameters = convergence_parameters
        else:
            self.emulator = self.ansatzes[qc_backend.ansatz.upper()](
                num_sites=num_sites,
                convergence_parameters=convergence_parameters,
                local_dim=local_dim,
                initialize=initialize,
                tensor_backend=tensor_backend,
            )

    @property
    def tensor_backend(self):
        """Tensor backend of the simulation"""
        return self.emulator._tensor_backend

    @property
    def ansatz(self):
        """Ansatz of the emulator"""
        return self._qc_backend.ansatz

    def __getattr__(self, __name: str):
        """
        Check for the attribute in emulator, i.e. the QCEmulator inherits all
        the emulator calls.
        This call is for convenience and for retrocompatibility

        .. warning::
            The method `__getattr__` is called when `__getattribute__` fails,
            so it already covers the possibility of the attribute being in the
            base class
        """
        return self.emulator.__getattribute__(__name)

    @classmethod
    def from_emulator(
        cls, emulator, conv_params=None, tensor_backend=None, qc_backend=QCBackend()
    ):
        """
        Initialize the QCEmulator class starting from an emulator class, i.e. either
        MPS or TTN

        Parameters
        ----------
        emulator : :class:`_AbstractTN`
            Either an MPS or TTN emulator
        conv_params : :class:`TNConvergenceParameters`, optional
            Convergence parameters. If None, the convergence parameters of the emulator
            are used
        tensor_backend: TensorBackend, optional
            Contains all the information on the tensors, such as dtype and device.
            Default to TensorBackend() (dtype=np.complex128, device="cpu").
        qc_backend : QCBackend(), optional
            Backend of the qmatchatea simulation

        Return
        ------
        QCEmulator
            The quantum circuit emulator class
        """
        if not isinstance(emulator, _AbstractTN):
            raise TypeError("The emulator should be a TN emulator class")
        if conv_params is None:
            conv_params = emulator._convergence_parameters
        if tensor_backend is None:
            tensor_backend = emulator._tensor_backend

        simulator = cls(
            emulator.num_sites,
            conv_params,
            emulator.local_dim,
            tensor_backend=tensor_backend,
            qc_backend=qc_backend,
        )
        emulator._convergence_parameters = conv_params
        emulator._tensor_backend = tensor_backend
        simulator.emulator = emulator
        simulator.emulator.convert(
            device=tensor_backend.device, dtype=tensor_backend.dtype
        )

        return simulator

    @classmethod
    def from_tensor_list(
        cls, tensor_list, conv_params=None, tensor_backend=None, qc_backend=QCBackend()
    ):
        """
        Initialize the QCEmulator class starting from a tensor list, i.e. either
        MPS or TTN

        Parameters
        ----------
        tensor_list : list of tensors
            Either an MPS or TTN list of tensors
        conv_params : :class:`TNConvergenceParameters`, optional
            Convergence parameters. If None, the convergence parameters of the emulator
            are used
        tensor_backend: TensorBackend, optional
            Contains all the information on the tensors, such as dtype and device.
            Default to TensorBackend() (dtype=np.complex128, device="cpu").
        qc_backend : QCBackend(), optional
            Backend of the qmatchatea simulation

        Return
        ------
        QCEmulator
            The quantum circuit emulator class
        """
        # A list of lists is a TTN, while a list of tensors is an MPS
        initial_state = cls.ansatzes[qc_backend.ansatz].from_tensor_list(
            tensor_list, conv_params=conv_params, tensor_backend=tensor_backend
        )

        simulator = cls.from_emulator(
            initial_state,
            conv_params=conv_params,
            tensor_backend=tensor_backend,
            qc_backend=qc_backend,
        )

        return simulator

    def meas_projective(
        self, nmeas=1024, qiskit_convention=True, seed=None, unitary_setup=None
    ):
        """See the parent method"""
        return self.emulator.meas_projective(
            nmeas=nmeas,
            qiskit_convention=qiskit_convention,
            seed=seed,
            unitary_setup=unitary_setup,
        )

    def to_statevector(self, qiskit_order=True, max_qubit_equivalent=20):
        """See the parent method"""
        return self.emulator.to_statevector(qiskit_order, max_qubit_equivalent)

    def apply_two_site_gate(self, operator, control, target):
        """Apply a two-site gate, regardless of the position on the chain

        Parameters
        ----------
        operator : QTeaTensor
            Gate to be applied
        control : int
            control qubit index
        target : int
            target qubit index

        Returns
        -------
        singvals_cut
            singular values cut in the process
        """
        local_dim = self.local_dim[0]
        if operator.shape == (local_dim**2, local_dim**2):
            operator = operator.reshape([local_dim] * 4)
        # Reorder for qiskit convention on the two-qubits gates
        if control < target or self.ansatz == "TTN":
            operator = operator.transpose([1, 0, 3, 2])

        singvals_cut = self.apply_two_site_operator(operator, [control, target])

        # Trunc tracking mode is stored in self.emulator._convergence_parameters
        singvals_cut = self.emulator._postprocess_singvals_cut(singvals_cut)

        # Bring to CPU/host if attribute available via some example tensor; must be
        # iso center in case of mixed device
        if isinstance(self.emulator, MPIMPS):
            # Will have problems with mixed-device MPI-MPS, but we can live
            # with this for now. Overwriting `get_tensor_of_site` in MPIMPS
            # is definitely necessary
            tensor = self.emulator[0]
        else:
            # in MPS, iso moves to the right and stays on device, TTN is less
            # obvious
            idx = max([control, target])
            tensor = self.emulator.get_tensor_of_site(idx)

        singvals_cut = tensor.get_of(singvals_cut)

        return [singvals_cut]

    def apply_multi_site_gate(self, operator, sites):
        """
        Apply a n-sites gate, regardless of the position on the chain

        Parameters
        ----------
        operator : QTeaTensor | List[QTeaTensor]
            If a single QTeaTensor, it is the unitary matrix of the
            n-qubits gate. If a List[QTeaTensor] it is already
            written in the MPO form
        sites : List[int]
            Sites to which the operator should be applied

        Returns
        -------
        singvals_cut
            singular values cut in the process
        """
        # This site order could be reversed for the qiskit convention
        site_order = np.argsort(sites)
        local_dim = self.local_dim[sites[0]]
        if isinstance(operator, self.tensor_backend.tensor_cls):
            operator = operator.reshape([local_dim] * len(sites) * 2)
            transpose_idxs = np.arange(operator.ndim).reshape(2, -1)
            transpose_idxs[0, :] = transpose_idxs[0, site_order]
            transpose_idxs[1, :] = transpose_idxs[1, site_order]
            operator.transpose_update(transpose_idxs.reshape(-1))
            operator = DenseMPO.from_matrix(
                operator, sites, local_dim, self._convergence_parameters
            )

        singvals_cut = self.apply_mpo(operator)

        # Avoid errors due to no singv cut
        singvals_cut = np.append(singvals_cut, 0)
        if self._trunc_tracking_mode == "M":
            singvals_cut = max(0, singvals_cut.max())
        elif self._trunc_tracking_mode == "C":
            singvals_cut = (singvals_cut**2).sum()

        if hasattr(singvals_cut, "get"):
            singvals_cut = singvals_cut.get()

        return [singvals_cut]

    def meas_observables(self, observables, operators):
        """Measure all the observables

        Parameters
        ----------
        observables : :py:class:`TNObservables`
            All the observables to be measured
        oeprators : :py:class:`TNOperators`
            List of operators that form the circuit stored in THE CORRECT DEVICE.
            If you are running on GPU the operators should be on the GPU.

        Returns
        -------
        TNObservables
            Observables with the results in results_buffer
        """
        if not isinstance(observables, TNObservables):
            raise TypeError("observables must be TNObservables")

        with warnings.catch_warnings():
            # We use a function that raises a warning for a specific thing we are not interested in.
            # So we filter it out.
            warnings.filterwarnings(
                "ignore",
                message="Tried to compute energy with no effective operators. Returning nan",
            )
            # At the moment, observables are only measured serially
            if self.ansatz == "MPIMPS":
                if self._qc_backend.mpi_settings[-1] < 0:
                    self.emulator.reinstall_isometry_serial()
                else:
                    self.emulator.reinstall_isometry_parallel(
                        self._qc_backend.mpi_settings[-1]
                    )
                rank = self.emulator.rank
                tensor_list = self.emulator.mpi_gather_tn()
                if rank != 0:
                    return observables
                emulator = MPS.from_tensor_list(
                    tensor_list,
                    self.emulator._convergence_parameters,
                    self.tensor_backend,
                )
            else:
                rank = 0
                emulator = self.emulator

            if rank == 0:
                emulator.normalize()
                observables = run_tn_measurements(
                    state=emulator,
                    observables=observables,
                    operators=operators,
                    params={},
                    tensor_backend=self.tensor_backend,
                    tn_type=6 if self.ansatz in ("MPS", "MPSMPI") else 5,
                )

        return observables

    def run_circuit_from_instruction(self, op_list, instr_list):
        """
        Run a circuit from the istructions.

        Parameters
        ----------
        op_list : list of tensors
            List of operators that form the circuit
        instr_list : list of instructions
            Instruction for the circuit, i.e. [op_name, op_idx, [sites] ]

        Return
        ------
        singvals_cut : list of float
            Singular values cutted, selected through the _trunc_tracking_mode
        """
        singvals_cut = []
        for instr in instr_list:
            sites = instr[2]
            num_sites = len(sites)
            idx = instr[1]
            if instr[0] == "barrier":
                continue

            if num_sites == 1:
                self.emulator.apply_one_site_operator(op_list[idx], *sites)

            elif num_sites == 2:
                singv_cut = self.apply_two_site_gate(op_list[idx], sites[0], sites[1])

                # Avoid errors due to no singv cut
                singv_cut = np.append(singv_cut, 0)
                if self._trunc_tracking_mode == "M":
                    singvals_cut.append(np.max(singv_cut, initial=0.0))
                elif self._trunc_tracking_mode == "C":
                    singvals_cut.append(np.sum(singv_cut**2))

            else:
                raise ValueError("Only one and two-site operations are implemented")
        return singvals_cut

    # pylint: disable-next=too-many-statements, too-many-branches, too-many-locals
    def run_from_qk(self, circuit, operators=None, checkpoints=QCCheckpoints()):
        """
        Run a qiskit quantum circuit on the simulator

        Parameters
        ----------
        circuit : :py:class:`QuantumCircuit`
            qiskit quantum circuit
        operators : TNOperators
            Operators class
        checkpoints : QCCheckpoints
            Checkpoints class

        Returns
        -------
        List[float]
            singular values cutted in the simulation
        Dictionary[TNObservables]
            The dictionary with the observables measured mid circuit
        List[float]
            Memory used in the simulation in bytes
        """
        # data structure of the quantum circuit
        data = circuit.data[checkpoints._initial_line :]
        process = psutil.Process()
        memory = np.zeros(len(data))
        obs_dict = {}
        singvals_cut = []
        for creg in circuit.cregs:
            self.cl_regs[creg.name] = np.zeros(creg.size)

        start_time = time.time()
        barrier_cnt = 0
        # Run over instances
        for idx, instance in enumerate(data):
            operation = instance.operation
            qubits = instance.qubits
            clbits = instance.clbits
            gate_name = operation.name
            num_qubits = len(qubits)
            qubits = [circuit.find_bit(qub).index for qub in qubits]

            # Checking for classical conditions on this gate.
            #
            #  NOTE: Gate.condition will be deprecated in Qiskit 2.0.0
            #  so we need to find an alternative way to make this work.
            #  (https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.Gate#condition)

            if operation.condition is None:
                apply_gate = True
            else:
                # NOTE: condition should be a tuple (classical_bit, bit_value)
                bit_idx = [clbit.index for clbit in operation.condition[0]]
                bit_value = self.cl_regs[operation.condition[0].name][bit_idx[0]]
                # ^^ possible warning here: we are checking only the first bit_idx

                # Apply the gate only if condition is met:
                apply_gate = bit_value == operation.condition[1]

            # Handling special circuit elements.
            if gate_name == "barrier":
                if self._qc_backend.mpi_settings[barrier_cnt] < 0:
                    self.emulator.reinstall_isometry_serial()
                else:
                    self.emulator.reinstall_isometry_parallel(
                        self._qc_backend.mpi_settings[barrier_cnt]
                    )
                barrier_cnt += 1
                continue
            if gate_name == "measure":
                meas_state, _ = self.apply_projective_operator(*qubits)
                self.cl_regs[clbits[0].register.name][0] = meas_state
                apply_gate = False
            elif gate_name == "reset":
                self.reset(qubits)
                apply_gate = False
            elif gate_name == "MeasureObservables":
                tic = time.time()
                obs = self.meas_observables(operation.observables, operators)
                toc = time.time()
                obs.results_buffer["time"] = tic - start_time
                obs.results_buffer["energy"] = None
                obs.results_buffer["norm"] = self.norm()
                obs.results_buffer["measurement_time"] = toc - tic
                obs_dict[operation.label] = obs
                continue
            if gate_name in ("id", "identity"):
                apply_gate = False
            # possible bug warning:
            # Check that the previous if/elif return either `apply_gate=False`
            # or `continue`. Otherwise, it is expected that `operation` has a
            # method to_matrix(), which is used to apply the gate if apply_gate==True.

            if apply_gate:
                # Grab the operator matrix and move it to the correct device
                gate_mat = operation.to_matrix()
                gate = self.tensor_backend.tensor_cls.from_elem_array(
                    gate_mat, self.tensor_backend.dtype, self.tensor_backend.device
                )
                if num_qubits == 1:
                    self.emulator.apply_one_site_operator(gate, *qubits)
                elif num_qubits == 2:
                    singv_cut = self.apply_two_site_gate(gate, *qubits)
                    singvals_cut += singv_cut
                else:
                    singv_cut = self.apply_multi_site_gate(gate, qubits)
                    singvals_cut += singv_cut

            memory[idx] = process.memory_info().rss
            # Check if you can change settings every n iterations
            self._runtime_checks_updates(idx, self.num_sites, singvals_cut)
            # Save checkpoints if needed
            checkpoints.save_checkpoint(idx, self.emulator)

        return singvals_cut, obs_dict, memory

    # pylint: disable-next=too-many-statements, too-many-branches, too-many-locals
    def run_from_qcirc(self, qcirc, starting_idx=0, checkpoints=QCCheckpoints()):
        """
        Run a simulation starting from a Qcircuit on a portion of the TN state

        Parameters
        ----------
        qcirc : :class:`Qcircuit`
            Quantum circuit
        starting_idx : int, optional
            MPS index that correspond to the index 0 of the Qcircuit. Default to 0.
        checkpoints : QCCheckpoints, optional
            Checkpoints in the simulation

        Returns
        -------
        List[float]
            singular values cutted in the simulation
        Dictionary[TNObservables]
            The dictionary with the observables measured mid circuit
        List[float]
            Memory used in the simulation in bytes
        """
        if not isinstance(qcirc, Qcircuit):
            raise TypeError(f"qcirc must be of type Qcircuit, not {type(qcirc)}")

        process = psutil.Process()
        memory = np.zeros(len(qcirc))
        obs_dict = {}
        singvals_cut = []
        start_time = time.time()
        cnt = -1
        for layer in qcirc:
            for instruction in layer:
                cnt += 1
                if cnt < checkpoints._initial_line:
                    continue
                sites = [ss + starting_idx for ss in instruction[1]]
                operation = instruction[0]

                # Check for classical conditioning
                appy_operation = operation.c_if.is_satisfied(qcirc)
                if appy_operation:
                    # First, check for particular keywords
                    if isinstance(operation, QCObservableStep):
                        operators = (
                            self.tensor_backend.base_tensor_cls.convert_operator_dict(
                                operation.operators,
                                params={},
                                symmetries=[],
                                generators=[],
                                base_tensor_cls=self.tensor_backend.base_tensor_cls,
                                dtype=self.tensor_backend.dtype,
                                device=self.tensor_backend.device,
                            )
                        )
                        tic = time.time()
                        obs = self.meas_observables(
                            operation.observables,
                            operators,
                        )
                        toc = time.time()
                        obs.results_buffer["time"] = tic - start_time
                        obs.results_buffer["norm"] = self.norm()
                        obs.results_buffer["measurement_time"] = toc - tic
                        operation.observables = obs
                        operation.postprocess_obs_indexing()  # Postprocess for qregisters
                        for elem in obs.obs_list:
                            obs.results_buffer.update(obs.obs_list[elem].results_buffer)
                        obs_dict[operation.name] = deepcopy(
                            operation.observables.results_buffer
                        )
                        del obs

                    # Check for particular keywords
                    elif operation.name == "renormalize":
                        self.normalize()
                    elif operation.name == "measure":
                        res = self.emulator.apply_projective_operator(
                            *sites, operation.selected_output
                        )
                        # Update measured value
                        qcirc.modify_cregister(
                            res, operation.cregister, operation.cl_idx
                        )
                    elif operation.name == "add_site":
                        self.emulator.add_site(operation.position)
                    elif operation.name == "remove_site":
                        self.apply_projective_operator(operation.position, remove=True)

                    # Apply gates
                    elif len(sites) == 1:
                        gate = self.tensor_backend.tensor_cls.from_elem_array(
                            operation.operator,
                            self.tensor_backend.dtype,
                            self.tensor_backend.device,
                        )
                        self.site_canonize(*sites, keep_singvals=True)
                        self.apply_one_site_operator(gate, *sites)
                    elif len(sites) == 2:
                        gate = self.tensor_backend.tensor_cls.from_elem_array(
                            operation.operator,
                            self.tensor_backend.dtype,
                            self.tensor_backend.device,
                        )
                        svd_cut = self.apply_two_site_gate(gate, *sites)
                        singvals_cut += svd_cut
                    else:
                        gate = self.tensor_backend.tensor_cls.from_elem_array(
                            operation.operator,
                            self.tensor_backend.dtype,
                            self.tensor_backend.device,
                        )
                        svd_cut = self.apply_multi_site_gate(gate, sites)
                        singvals_cut += svd_cut

                # Check if you can change settings every n iterations
                self._runtime_checks_updates(cnt, self.num_sites, singvals_cut)
                # Save checkpoints if needed
                checkpoints.save_checkpoint(cnt, self.emulator)
                memory[cnt] = process.memory_info().rss

        return singvals_cut, obs_dict, memory

    def _runtime_checks_updates(self, idx, frequency, norm_cut):
        """
        Perform the checks to change the device and the precision if
        idx%frequency is 0.

        Parameters
        ----------
        idx : int
            Index of the current operation of the quantum circuit
        frequency: int
            The checks are done every frequency operations
        norm_cut: float
            The norm cut in the last simulation
        """
        if idx % frequency == 0:
            device = self._qc_backend.resolve_device(
                self.emulator.current_max_bond_dim, self.tensor_backend.device
            )
            precision = self._qc_backend.resolve_precision(
                (1 - np.array(norm_cut)).prod()
            )
            self.emulator.convert(device=device, dtype=precision)


# pylint: disable-next=too-many-statements, too-many-branches, too-many-locals, too-many-arguments
def run_py_simulation(
    circ,
    local_dim=2,
    convergence_parameters=QCConvergenceParameters(),
    operators=QCOperators(),
    observables=TNObservables(),
    initial_state=None,
    backend=QCBackend(),
    checkpoints=QCCheckpoints(),
):
    """
    Transpile the circuit to adapt it to the linear structure of the MPS and run the circuit,
    obtaining in output the measurements.

    Parameters
    ----------
    circ: QuantumCircuit
        qiskit quantum circuit object to simulate
    local_dim: int, optional
        Local dimension of the single degree of freedom. Default is 2, for qubits
    convergence_parameters: :py:class:`QCConvergenceParameters`, optional
        Maximum bond dimension and cut ratio. Default to max_bond_dim=10, cut_ratio=1e-9.
    operators: :py:class:`QCOperators`, optional
        Operator class with the observables operators ALREADY THERE. If None, then it is
        initialized empty. Default to None.
    observables: :py:class:`TNObservables`, optional
        The observables to be measured at the end of the simulation. Default to TNObservables(),
        which contains no observables to measure.
    initial_state : list of ndarray, optional
        Initial state of the simulation. If None, ``|00...0>`` is considered. Default to None.
    backend: :py:class:`QCBackend`, optional
        Backend containing all the information for where to run the simulation
    checkpoints: :py:class:`QCCheckpoints`, optional
        Class to handle checkpoints in the simulation

    Returns
    -------
    result: qmatchatea.SimulationResults
        Results of the simulation, containing the following data:
        - Measures
        - Statevector
        - Computational time
        - Singular values cut
        - Entanglement
        - Measure probabilities
        - MPS state
        - MPS file size
        - Observables measurements
    """
    if isinstance(circ, (QuantumCircuit, Qcircuit)):
        num_qubits = circ.num_qubits
    else:
        raise TypeError(
            "Only qiskit Quantum Circuits and Qcircuit are implemented for"
            + f" simulation, not {type(circ)}"
        )
    start = time.time()
    tensor_backend = _resolve_tensor_backend(
        tensor_module=backend.tensor_module,
        device=backend.resolve_device(1, "cpu"),
        dtype=backend.resolve_precision(1),
    )

    if backend.mpi_approach != "SR" and backend.ansatz == "MPS":
        backend._ansatz = "MPIMPS"

    operators = tensor_backend.base_tensor_cls.convert_operator_dict(
        operators,
        params={},
        symmetries=[],
        generators=[],
        base_tensor_cls=tensor_backend.base_tensor_cls,
        dtype=tensor_backend.dtype,
        device=tensor_backend.device,
    )
    # Check if you selected restart from a checkpoint
    initial_state = checkpoints.restart_from_checkpoint(initial_state)

    # The scalar check is to avoid a warning
    if np.isscalar(initial_state):
        if initial_state is None:
            initial_state = "vacuum"
        simulator = QCEmulator(
            num_qubits,
            convergence_parameters,
            local_dim=local_dim,
            tensor_backend=tensor_backend,
            qc_backend=backend,
            initialize=initial_state.lower(),
        )
    elif isinstance(initial_state, _AbstractTN):
        simulator = QCEmulator.from_emulator(
            initial_state,
            conv_params=convergence_parameters,
            tensor_backend=tensor_backend,
            qc_backend=backend,
        )
    else:
        simulator = QCEmulator.from_tensor_list(
            initial_state,
            conv_params=convergence_parameters,
            tensor_backend=tensor_backend,
            qc_backend=backend,
        )
    if isinstance(circ, QuantumCircuit):
        singvals_cut, obs_dict, memory = simulator.run_from_qk(
            circ, operators, checkpoints=checkpoints
        )
    elif isinstance(circ, Qcircuit):
        singvals_cut, obs_dict, memory = simulator.run_from_qcirc(
            circ, checkpoints=checkpoints
        )
    else:
        # Duplicate from above, but makes linter happy
        raise TypeError(
            "Only qiskit Quantum Circuits and Qcircuit are implemented for pure python"
            + f" simulation, not {type(circ)}"
        )

    end = time.time()

    tic = time.time()
    observables = simulator.meas_observables(observables, operators)
    toc = time.time()

    observables.results_buffer["time"] = end - start
    observables.results_buffer["energy"] = None
    observables.results_buffer["norm"] = simulator.norm()
    observables.results_buffer["measurement_time"] = toc - tic
    observables.results_buffer["memory"] = memory / (1024**3)

    result_dict = observables.results_buffer

    # Observables postprocessing
    postprocess = False
    if simulator.ansatz == "MPIMPS":
        if simulator.rank == 0:
            postprocess = True
    else:
        postprocess = True

    if postprocess:
        for elem in observables.obs_list:
            result_dict.update(observables.obs_list[elem].results_buffer)
            # Special treatment for TNState2file
            if str(elem) == "TNState2File":
                for value in observables.obs_list[elem].name:
                    result_dict["tn_state_path"] = observables.obs_list[
                        elem
                    ].results_buffer[value]

        # Storing the results of measurement happened mid-circuit
        # under their label
        # pylint: disable-next=consider-using-dict-items
        for label in obs_dict:
            obs_values = obs_dict[label]
            tmp = obs_values.results_buffer
            for elem in obs_values.obs_list:
                tmp.update(obs_values.obs_list[elem].results_buffer)
                # Special treatment for TNState2file
                if str(elem) == "TNState2File":
                    for value in obs_values.obs_list[elem].name:
                        tmp["tn_state_path"] = observables.obs_list[
                            elem
                        ].results_buffer[value]

            result_dict[label] = tmp

    results = SimulationResults()
    results.set_results(result_dict, singvals_cut)

    return results


def _resolve_tensor_backend(tensor_module, device, dtype):
    """
    Resolve the string name of the module used for the tensor
    operations.

    Parameters
    ----------
    tensor_module : str
        Name of the module used for the tensor operations

    Returns
    -------
    qtealeaves.tensors._AbstractTensor
    """

    # First fake initialization, to have access to the tensor_cls for
    # the correct dtype
    if tensor_module == "numpy":
        tensor_backend = qtt.TensorBackend()
    elif tensor_module == "torch":
        tensor_backend = qrt.torchapi.default_pytorch_backend()
    elif tensor_module == "tensorflow":
        tensor_backend = qrt.tensorflowapi.default_tensorflow_backend()
    elif tensor_module == "jax":
        tensor_backend = qrt.jaxapi.default_jax_backend()
    else:
        raise ValueError(f"Tensor class with {tensor_module} is not available.")

    # Get the correct dtype
    tmp_tensor = tensor_backend([1, 1])
    dtype = tmp_tensor.dtype_from_char(dtype)

    # Return real tensor backend with correct dtype
    if tensor_module == "numpy":
        return qtt.TensorBackend(device=device, dtype=dtype)
    if tensor_module == "torch":
        return qrt.torchapi.default_pytorch_backend(device=device, dtype=dtype)
    if tensor_module == "tensorflow":
        return qrt.tensorflowapi.default_tensorflow_backend(device=device, dtype=dtype)
    if tensor_module == "jax":
        return qrt.jaxapi.default_jax_backend(device=device, dtype=dtype)

    # Makes linter happy
    raise ValueError(f"Tensor class with {tensor_module} is not available.")
