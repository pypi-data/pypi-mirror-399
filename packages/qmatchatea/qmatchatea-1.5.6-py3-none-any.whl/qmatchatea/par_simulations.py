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
In this module we add another level of parallelization on the library.
You can run multiple **independent** simulations in parallel, using the mpi4py library.
To fully understand which are the parameters needed by the function refer to :doc:`interface`.

You should be a little more careful if you want to run simulations this way, since the input
parameters are handled through a list of dictionaries and not singularly. Furthermore,
the way you ran your program is different.
To run a script called `sample.py` with `4` processes you will write on yout shell:

.. code-block::

  mpiexec -n 4 python3 sample.py

.. note::

    Consider that the parallilazion scheme is up to the user, the program will run from the first
    to the last. You should so place first the more computationally demanding simulations to ensure
    an effective parallelization.

"""


import inspect

# Numpy
import os
import os.path
from shutil import rmtree
from typing import OrderedDict

from qmatchatea.utils import QCIO

from .interface import run_simulation
from .utils import SimulationResults

__all__ = ["run_parallel_simulations", "MASTER"]

FREETAG = 0  # Tag to say that the workers are free
WORKTAG = 1  # Tag to send the working parameters to the workers
DIETAG = 2  # Tag to break the MW communications

MASTER = 0


# pylint: disable-next=invalid-name
def run_parallel_simulations(params, MPI):
    """Run multiple simulations in parallel

    Parameters
    ----------
    params : OrderedDict
        Ordered dict where the key is the simulation ID and the value is a dictionary
        with the parameters of the function :py:func:`run_simulation`
    MPI: MPI module
        MPI module to perform the MPI calls

    Returns
    -------
    results : OrderedDict
        Ordered dict where the key is the simulation ID and the value the corresponding
        :py:class:`SimulationResults`

    Raises
    ------
    TypeError
        If the input parameters are not an ordered dict
    """
    if not isinstance(params, OrderedDict):
        raise TypeError("Input parameters must be provided through an OrderedDict")

    # Initialize MPI variables for communications
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:
        if not os.path.isdir("TMP_MPI"):
            os.makedirs("TMP_MPI")
        results = _master(params, MPI)

        if os.path.isdir("TMP_MPI"):
            rmtree("TMP_MPI")
        return results

    _worker(MPI)
    return None


# pylint: disable-next=invalid-name
def _master(params, MPI):
    comm = MPI.COMM_WORLD
    results = OrderedDict()
    requests = []
    error_count = 0
    for sim_id, sim_param in zip(params.keys(), params.values()):
        print(f"**** Done ID={sim_id} *****")
        # Initialize results
        # results[ID] = SimulationResults()

        # Check which process is free
        free_process = comm.recv(buf=None, source=MPI.ANY_SOURCE, tag=FREETAG)

        # Send the data to the worker
        comm.send(obj=sim_param, dest=free_process, tag=WORKTAG)
        comm.send(obj=sim_id, dest=free_process, tag=WORKTAG)

        # Receive the data from the workers with NON-BLOCKING communications
        req = comm.irecv(buf=None, source=free_process, tag=WORKTAG)
        requests.append(req)

    print("----- Finished sending out circuits -----")

    # When you finished wait for all the results
    for sim_id, req in zip(params.keys(), requests):
        path = req.wait()
        if path is None:
            error_count += 1
            results[sim_id] = None
        else:
            results[sim_id] = SimulationResults.read_pickle(path)

    # Send the DIETAG to the workers
    for ii in range(comm.Get_size()):
        if ii == MASTER:
            continue
        comm.send(obj=None, dest=ii, tag=DIETAG)

    # Distribute if any errors occured, raise most recent in each process
    error_count = comm.bcast(error_count, root=MASTER)
    if error_count > 0:
        raise RuntimeError(
            "At least one of the workers failed; "
            "reporting only most recent exception in each worker."
        )

    return results


# pylint: disable-next=invalid-name
def _worker(MPI):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    comm.send(obj=rank, dest=MASTER, tag=FREETAG)
    status = MPI.Status()

    # Store exception if needed
    exc = None

    while True:
        simulation_parameters = comm.recv(
            buf=None, source=MASTER, tag=MPI.ANY_TAG, status=status
        )
        if status.Get_tag() == DIETAG:
            break

        # Perform the simulation
        sim_id = comm.recv(buf=None, source=MASTER, tag=WORKTAG)
        try:
            simulation_parameters = _check_parameters(simulation_parameters, rank)
            # pylint: disable-next=no-value-for-parameter
            results = run_simulation(*simulation_parameters)

            # Save the results
            path = os.path.join("TMP_MPI", f"{sim_id}.pkl")
            results.save_pickle(path)
            # Send back the results
            comm.send(obj=path, dest=MASTER, tag=WORKTAG)

            # Send the I'm FREE message to the MASTER
            comm.send(obj=rank, dest=MASTER, tag=FREETAG)

        # pylint: disable-next=broad-exception-caught
        except Exception as e:
            # Need to handle any error in the simulation
            exc = e

            # Send back None to signal error to master
            comm.send(None, dest=MASTER, tag=WORKTAG)

            # Send the I'm FREE message to the MASTER
            comm.send(obj=rank, dest=MASTER, tag=FREETAG)

    # Get status if any errors occured, raise most recent in each process
    error_count = 0
    error_count = comm.bcast(error_count, root=MASTER)
    if error_count > 0:
        if exc is None:
            raise RuntimeError("This worker had no problem, but neighboring workers.")
        # Will raise most recent or runtime error no active exception
        raise exc

    return


def _check_parameters(simulation_parameters, rank):
    """Given a dictionary where the keys are the parameter names and the values their values
    returns an ordered tuple of parameters that can directly fit into :py:func:`run_simulation`
    and raises errors if the parameters are not corrected.

    Parameters
    ----------
    simulation_parameters : dict
        Dictionary of the input parameters for the :py:func:`run_simulation` function.
        Notice that the parameters `circ` and `bond_dim` are non-optional, and must so
        be provided, while all the optional parameters can remain non-indicated
    rank : int
        Rank of the process

    Returns
    -------
    params: tuple
        ordered tuple of the parameters for the :py:func:`run_simulation`

    Raises
    ------
    RuntimeError
        If a non-optional parameter of :py:func:`run_simulation` is not provided
    ValueError
        If the chosen parallel approach is not serial
    """

    # Setting for the current simulation
    keys = simulation_parameters.keys()
    params = []

    # Parse default arguments
    sim_info = inspect.getfullargspec(run_simulation)
    arg_names = sim_info.args
    default_values = sim_info.defaults
    num_non_optional_args = len(arg_names) - len(default_values)

    for ii, name in enumerate(arg_names):
        if name in keys:
            # Parameter provided in input_simulation
            value = simulation_parameters[name]
        elif ii < num_non_optional_args:
            # Parameter not provided, but it was non-optional
            raise RuntimeError(
                f"Parameter {name} is a non-optional parameter and must \
                be provided"
            )
        else:
            # Parameter not provided, set default
            value = default_values[ii - num_non_optional_args]

        # Raise exception if the chosen parallel approach is not 'SR', since not implemented yet
        if name == "approach" and value != "SR":
            raise ValueError(
                "Only the serial par_approach can be used when parallelizing \
                over different simulations"
            )

        # Special case for the input/output PATHs if they are not provided, to skip problems
        # of reading/writing from the same file from multiple processes
        if (name == "io_info") and (name not in keys):
            value = QCIO(f"data/in/rank_{rank}", f"data/out/rank_{rank}")

        params.append(value)

    assert len(params) == len(
        arg_names
    ), "Number of parameter not equal to number of arguments"
    params = tuple(params)
    return params
