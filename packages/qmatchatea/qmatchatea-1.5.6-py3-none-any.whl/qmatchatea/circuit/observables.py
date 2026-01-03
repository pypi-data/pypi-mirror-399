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
Class to handle the intermediate measurement of observables.

It also handles the indexing of quantum registers and observables.
"""
from copy import deepcopy

import numpy as np
from qtealeaves.observables import TNObservables

from qmatchatea.utils.tn_utils import QCOperators

from .operations import ClassicalCondition, QCOperation


class QCObservableStep(QCOperation):
    """
    Perform a measurement of the observables TNObservables.
    The observables are applied on the **WHOLE** circuit,
    regardless of the register. Thus, this class also
    takes a snapshot of the current quantum registers,
    in such a way to be able to recover the desired
    indexes.

    Parameters
    ----------
    name : str
        Name of the observables step
    observables: :class:`TNObservables`
        Observables to be measured at this step
    operators: :class:`QCOperators`, optional
        Class containing the operators present in the Observables
    conditioned : :py:class:`ClassicalCondition`, optional
        Classical condition to be checked for applying the operation on the
        simulation.

    Examples
    --------

    For a detailed explanation of how the observable structure will
    change adapting to the qregisters see:

    - `LocalObs`_.
    - `ProjectiveObs`_.
    - `ProbabilityObs`_.
    """

    def __init__(
        self,
        name,
        observables,
        operators=QCOperators(),
        conditioned=ClassicalCondition(),
    ):
        if isinstance(observables, TNObservables):
            self.observables = deepcopy(observables)
            self.operators = operators
            self.qregisters = np.repeat(None, 2)
            self.num_sites = 0
            super().__init__(name, None, None, conditioned)
        else:
            raise TypeError(
                f"observables is type {type(observables)}, not TNObservables"
            )

    @property
    def has_single_qreg(self):
        """True if the observable is specific to a single register, False otherwise"""
        return len(self.qregisters) == 1

    def snap_current_qregisters(self, qregisters):
        """
        Save the current quantum registers in the quantum circuit
        to recover the correct pattern of observable-register
        afterwards

        Parameters
        ----------
        qregisters : dict
            Dictionaty of the quantum registers
        """
        self.qregisters = qregisters

    def adjust_obs_indexing(self):
        """
        Modify the indexing of the observables
        that targets a specific site index, such
        as the TNObsTensorProduct and TNObsWeightedSum.
        """

        # Adjust TP observables
        tensor_prod = self.observables.obs_list["TNObsTensorProduct"]
        if len(tensor_prod) > 0:
            self.observables.obs_list["TNObsTensorProduct"] = self._adjust_tp_indexing(
                tensor_prod
            )

        # Adjust weighted sum observables
        weight_s = self.observables.obs_list["TNObsWeightedSum"]
        if len(weight_s) > 0:
            new_tp_ops = []
            for tp_obs in weight_s.tp_operators:
                new_tp_ops.append(self._adjust_tp_indexing(tp_obs))
            weight_s.tp_operators = new_tp_ops
            self.observables.obs_list["TNObsWeightedSum"] = weight_s

    def postprocess_obs_indexing(self):
        """
        Postprocess the indexing of the observables, after the computation,
        due to the quantum registers.
        """
        # Adjust local observables
        local = self.observables.obs_list["TNObsLocal"]
        if len(local) > 0:
            local = self._postprocess_local(local)
            self.observables.obs_list["TNObsLocal"] = local

        # Adjust projective observables
        proj = self.observables.obs_list["TNObsProjective"]
        if proj.num_shots > 0:
            proj = self._postprocess_projective(proj)
            self.observables.obs_list["TNObsProjective"] = proj

        # Adjust probabilities observables
        prob = self.observables.obs_list["TNObsProbabilities"]
        if len(prob) > 0:
            prob = self._postprocess_probabilities(prob)
            self.observables.obs_list["TNObsProbabilities"] = prob

    def _adjust_tp_indexing(self, tp_obs):
        """
        Adjust the indexing of a TNObsTensorProduct observable.
        This procedure works only if we have a single register
        in the snapshot.

        Parameters
        ----------
        tp_obs : :class:`TNObsTensorProduct`
            Tensor product observable

        Returns
        -------
        :class:`TNObsTensorProduct`
            The new observable with the correct indexing
        """
        if not self.has_single_qreg:
            raise RuntimeError(
                "Cannot adjust indexing when more than" + " a register is involved"
            )

        new_indexing = list(self.qregisters.values())[0]

        new_sites = []
        for idx, obs in enumerate(tp_obs.sites):
            new_sites.append([])
            for site in obs:
                new_sites[idx].append(new_indexing[site])
        tp_obs.sites = new_sites

        return tp_obs

    def _postprocess_local(self, local):
        """
        Postprocess local observables. In input, you get a
        vector of local observables, one for each site.
        In output, the vector of local observable is transformed
        into a dictionary, where the key is the quantum register
        and the value the local measurement corresponding to
        that register

        .. _LocalObs:

        Example
        -------
        Let us suppose that we have a chain of 4 qubits, and we
        want to measure :math:`\\sigma_z` locally. Qubits 0,1 are
        part of register ``'default'``, while qubits 2,3 of
        ``'ancilla'``. Then:

        .. code-block:: python

            # local is the local observable class
            local_obs = local.results_buffer['sz']
            print(local_obs)
            >>>> [0, 1, -1, 0]
            # qcobs is the parent class
            postprocessed_local_obs = qcobs._postprocess_local(local)
            post_proc_res = postprocessed_local_obs.results_buffer['sz']
            print(post_proc_res)
            >>>> {'default':[0, 1], 'ancilla':[-1, 0]}

        Parameters
        ----------
        local : :class:`TNObsLocal`
            Local observables to be postprocessed

        Returns
        -------
        :class:`TNObsLocal`
            Postprocessed local observables
        """

        new_results = {}
        for key, obs in local.results_buffer.items():
            new_results[key] = {}
            for qreg_key, indexing in self.qregisters.items():
                new_results[key][qreg_key] = obs[indexing]
        local.results_buffer = new_results

        return local

    def _postprocess_projective(self, projective):
        """
        Postprocess projective measurements. In input,
        you get the dictionary of the measurement,
        in output a dictionary further divided by the
        quantum registers, as shown in the example.

        .. _ProjectiveObs:

        Example
        -------
        Let us suppose that we have a chain of 4 qubits.
        Qubits 0,1,2 are part of register `'default'`
        and are in a GHZ state, while qubits 3 of
        `'ancilla'` and is in the |1> state. Then:

        .. code-block:: python

            # proj is the projective measuremenent observable class
            proj_obs = proj.results_buffer['projective_measurements']
            print(proj_obs)
            >>>> {'1111' : 512, '1000' : 512}
            # qcobs is the parent class
            pp_proj = qcobs._postprocess_projective(proj)
            post_proc_res = pp_proj.results_buffer['projective_measurements']
            print(post_proc_res)
            >>>> {'default':{'000':512, '111':512}, 'ancilla':{'1':1024}}

        Parameters
        ----------
        local : :class:`TNObsProjective`
            Projective measurement observables to be postprocessed

        Returns
        -------
        :class:`TNObsProjective`
            Postprocessed projective measurement observables
        """

        measures = projective.results_buffer["projective_measurements"]

        new_measures = {}
        for qreg_key, indexing in self.qregisters.items():
            new_measures[qreg_key] = {}
            indexing = self.num_sites - 1 - indexing

            for key, value in measures.items():
                if "," in key:
                    key = np.array(key.split(","))
                    sep = ","
                else:
                    key = np.array(list(key))
                    sep = ""
                key = np.array2string(key[indexing].astype(int), separator=sep)
                key = key.replace("[", "").replace("]", "")

                if key in new_measures[qreg_key]:
                    new_measures[qreg_key][key] += value
                else:
                    new_measures[qreg_key][key] = value
        projective.results_buffer["projective_measurements"] = new_measures

        return projective

    def _postprocess_probabilities(self, probabilities):
        """
        Postprocess probability measurements. In input,
        you get the dictionary of the probabilities,
        in output a dictionary further divided by the
        quantum registers, as shown in the example.
        While probabilities are summed for the even
        and greedy case, when focusing on a quantum register,
        they are instead concatenated in the unbiased case,
        since in that scenario we measure the probability intervals

        .. _ProbabilityObs:

        Examples
        --------
        Let us suppose that we have a chain of 4 qubits.
        Qubits 0,1,2 are part of register `'default'`
        and are in a GHZ state, while qubits 3 of
        `'ancilla'` and is in the |1> state.

        **Even or greedy probabilities**

        Probabilities on the same state are summed.

        .. code-block:: python

            # prob is the probability measuremenent observable class
            prob_obs = prob.results_buffer['even_probabilities']
            print(prob_obs)
            >>>> {'1111' : 0.5, '1000' : 0.5}
            # qcobs is the parent class
            pp_prob = qcobs._postprocess_probabilities(prob)
            post_proc_res = pp_prob.results_buffer['even_probabilities']
            print(post_proc_res)
            >>>> {'default':{'000':0.5, '111':0.5}, 'ancilla':{'1':1}}

        **Unbiased probabilities**

        In this specific case the intervals could be summed, since they
        are contigous, but in the more general case they simply
        cannot, without losing informations.

        .. code-block:: python

            # prob is the probability measuremenent observable class
            prob_obs = prob.results_buffer['unbiased_probabilities']
            print(prob_obs)
            >>>> {'1000' : (0, 0.5), '1111' : (0.5, 1)}
            # qcobs is the parent class
            pp_prob = qcobs._postprocess_probabilities(prob)
            post_proc_res = pp_prob.results_buffer['unbiased_probabilities']
            print(post_proc_res)
            >>>> {'default':{'000':(0, 0.5), '111':(0.5, 1)},
            >>>>    'ancilla':{'1':(0, 0.5, 0.5, 1) }}

        Parameters
        ----------
        probabilities : :class:`TNObsProbabilities`
            Probabilities measurement observables to be postprocessed

        Returns
        -------
        :class:`TNObsProbabilities`
            Postprocessed probabilities measurement observables
        """

        new_probs = {}

        for prob_key, prob in probabilities.results_buffer.items():
            new_probs[prob_key] = {}
            for qreg_key, indexing in self.qregisters.items():
                new_probs[prob_key][qreg_key] = {}
                indexing = self.num_sites - 1 - indexing
                if isinstance(prob, tuple):
                    # in case qtealeaves also return the samples
                    # (see `do_return_samples=True` option)
                    prob = prob[0]
                for key, value in prob.items():
                    if "," in key:
                        key = np.array(key.split(","))
                        sep = ","
                    else:
                        key = np.array(list(key))
                        sep = ""

                    key = np.array2string(key[indexing].astype(int), separator=sep)
                    key = key.replace("[", "").replace("]", "")

                    if key in new_probs[prob_key][qreg_key]:
                        new_probs[prob_key][qreg_key][key] += value
                    else:
                        new_probs[prob_key][qreg_key][key] = value

        probabilities.results_buffer = new_probs

        return probabilities
