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
Core function to run the simulation: :py:func:`run_simulation`.

Running the program
-------------------

 It is possible to choose between different approaches for running the simulation:
 - The machine precision can be either double complex "Z" or single complex "C".
 - The device of the simulation can be either "cpu" or "gpu".
 - The number of processes for the MPI simulation. If 1 is passed, then a serial program is run.
 - The approach for the MPI simulation. Either cartesian "CT" or serial "SR".


Serial program
~~~~~~~~~~~~~~

The default way of running this program is to run it serially. While it may be slower than a
parallel implementation it is safer, since the approximation we do on the state is minor.
There are different possibilities to run the program serially:

- Using the CPU backend, which is built in numpy.
- Using the GPU backend (``device='gpu'``).
  The backend is entirely built with cupy,
  runs the simulation on a GPU, giving back the results on the CPU.

Furthermore, there are several options to run the simulation on alternative tensor modules.
Look at the options in :func:`QCBackend <qmatchatea.utils.QCBackend>`.

Parallel program
~~~~~~~~~~~~~~~~

There are three possible algorithm provided to run the program on multiple cores:

- a Cartesian approach (``mpi_approach='CT'``), where the MPS is evenly divided among different
  processes, and each process perform the evolution only on his subsystem
- running multiple independent serial simulations on multiple cores. To know more see
  :doc:`par_simulations`

At the end of the evolution the MPS is brought back together into the master process and the
measurements are performed. The command to call the parallel program should be
:code:`mpirun -np np ./par_main_qmatchatea.exe` where :code:`np` is the
number of processes you will use. It should be given as input to the :class:`IO_INFO`.
For further details on the input class see :doc:`utils`.

Remember that there are communications involved in the MPI parallel program.
You should use it only if your system is large enough or if the bond
dimension used is big enough.

Checking the convergence: Singular values cut
---------------------------------------------

The singular values cut are an indication of the approximation taking place during the
simulation. Indeed, at each application of two-qubit there is an approximation going on,
subject to the *bond_dim* :math:`\\chi` and the *cut_ratio* :math:`\\epsilon` parameters.
Based on the *trunc_tracking_mode* the singular values are reported:

- *trunc_tracking_mode=M*, at each two-site operator we save the maximum of the singular values cut
- *trunc_tracking_mode=C*, at each two-site operator we save the **sum** of the singular values cut

We recall that, given a decreasing-ordered vector of singular values
:math:`S=(s_1, s_2, \\dots, s_n)` we truncate all the singular values:

.. math::

        s_i \\; \\mbox{ is truncated }\\quad \\mbox{if} \\; i>\\chi \\; \\mbox{ or } \\;
        \\frac{s_i}{s_1}<\\epsilon

Observables
-----------

For a detailed description of the observables, i.e. the measurable quantities, please refer
to :doc:`observables`.

"""

import os
import os.path
from typing import OrderedDict

from qtealeaves.observables import TNObservables

from qmatchatea.circuit import Qcircuit
from qmatchatea.py_emulator import run_py_simulation

from .preprocessing import preprocess
from .utils import QCBackend
from .utils.mpi_utils import to_layered_circ
from .utils.qk_utils import qk_transpilation_params
from .utils.tn_utils import QCOperators
from .utils.utils import QCIO, QCCheckpoints, QCConvergenceParameters

__all__ = ["run_simulation"]


# pylint: disable-next=too-many-branches, too-many-arguments
def run_simulation(
    circ,
    local_dim=2,
    convergence_parameters=QCConvergenceParameters(),
    operators=QCOperators(),
    io_info=QCIO(),
    observables=TNObservables(),
    transpilation_parameters=qk_transpilation_params(),
    checkpoints=QCCheckpoints(),
    backend=QCBackend(),
):
    """
    Transpile the circuit to adapt it to the linear structure of the MPS and run the circuit,
    obtaining in output the measurements.

    Parameters
    ----------
    circ: QuantumCircuit | Qcircuit
        Quantum circuit object to simulate.
        Be careful, if one passes a Qcircuit **no check** is done on the quantum circuit, i.e.
        it is not linearized and no barriers are added automatically.
    local_dim: int, optional
        Local dimension of the single degree of freedom. Default is 2, for qubits
    convergence_parameters: :py:class:`QCConvergenceParameters`, optional
        Maximum bond dimension and cut ratio. Default to max_bond_dim=10, cut_ratio=1e-9.
    operators: :py:class:`QCOperators`, optional
        Operator class with the observables operators ALREADY THERE. If None, then it is
        initialized empty. Default to None.
    io_info: :py:class:`QCIO`, optional
        Informations about input/output files.
    observables: :py:class:`TNObservables`, optional
        The observables to be measured at the end of the simulation. Default to TNObservables(),
        which contains no observables to measure.
    transpilation_parameters: :py:class:`qk_transpilation_params`, optional
        Parameters used in the qiskit transpilation phase. Default to qk_transpilation_params().
    checkpoints: :py:class:`QCCheckpoints`, optional
        Class to handle checkpoints in the simulation.
    backend: :py:class:`QCBackend`, optional
        Backend containing all the information for where to run the simulation.

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
        - Observables measurements
    """
    # Checks on input parameters
    if not isinstance(convergence_parameters, QCConvergenceParameters):
        raise TypeError(
            "convergence_parameters must be of type QCConvergenceParameters"
        )
    if not isinstance(operators, QCOperators):
        raise TypeError("operators must be of type QCOperators")
    if not isinstance(io_info, QCIO):
        raise TypeError("io_info must be of type QCIO")
    if not isinstance(observables, TNObservables):
        raise TypeError("observables must be of type TNObservables")
    if not isinstance(transpilation_parameters, qk_transpilation_params):
        raise TypeError(
            "transpilation_parameters must be of type qk_transpilation_params"
        )
    if not isinstance(checkpoints, QCCheckpoints):
        raise TypeError("checkpoints must be of type QCCheckpoints")
    if not isinstance(backend, QCBackend):
        raise TypeError("backend must be of type QCBackend")

    # Ensure observables output folders is present and set IO
    io_info.setup()

    # Set the PATH to the saved files into the output folder
    for ii in range(len(observables.obs_list["TNState2File"])):
        if "/" not in observables.obs_list["TNState2File"].name[ii]:
            observables.obs_list["TNState2File"].name[ii] = os.path.join(
                io_info.outPATH, observables.obs_list["TNState2File"].name[ii]
            )

    # Preprocess the circuit to adapt it to the MPS constraints (linearity)
    if not isinstance(circ, Qcircuit):
        # Inside the preprocessing, flag the swaps with another name
        # to avoid problems. We don't want the swaps added for keeping
        # the layout linear to be affecting the results of the circuit

        circ = preprocess(circ, qk_params=transpilation_parameters)

        if backend.where_barriers > 0:
            circ = to_layered_circ(circ, where_barriers=backend.where_barriers)

    # Prepare input dictionary
    input_dict = OrderedDict()
    input_dict["num_sites"] = circ.num_qubits
    input_dict["local_dim"] = local_dim
    input_dict["observables_filename"] = os.path.join(observables.filename_observables)

    # Setting checkpoints if required
    if checkpoints.frequency > 0:
        checkpoints.set_up(input_dict, operators, observables, circ)

    # Write all the information of the simulation as json
    to_write = [convergence_parameters, backend, io_info, checkpoints]
    for cls_to_write in to_write:
        cls_to_write.to_json(io_info.inPATH)

    result = run_py_simulation(
        circ,
        local_dim,
        convergence_parameters,
        operators,
        observables,
        backend=backend,
        initial_state=io_info.initial_state,
        checkpoints=checkpoints,
    )

    return result
