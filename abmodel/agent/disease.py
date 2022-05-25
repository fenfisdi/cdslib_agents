# Copyright (C) 2021, Camilo Hincapié Gutiérrez
# This file is part of CDSLIB.
#
# CDSLIB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CDSLIB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
#
# This package is authored by:
# Camilo Hincapié (https://www.linkedin.com/in/camilo-hincapie-gutierrez/) (main author)
# Ian Mejía (https://github.com/IanMejia)
# Emil Rueda (https://www.linkedin.com/in/emil-rueda-424012207/)
# Nicole Rivera (https://github.com/nicolerivera1)
# Carolina Rojas Duque (https://github.com/carolinarojasd)

from datetime import timedelta
from typing import Union, Optional
from copy import deepcopy

from numpy import where, full, isin, concatenate, setdiff1d, array
from numpy import isnan, nan, transpose, equal
from numpy.random import choice, random_sample
from pandas.core.frame import DataFrame
from pandas.core.series import Series
from pandas import concat
from dask.dataframe import from_pandas

from abmodel.utils import ExecutionModes
from abmodel.utils import check_field_existance
from abmodel.utils import exception_burner
from abmodel.utils import std_str_join_cols
from abmodel.models import DistTitles
from abmodel.models import NaturalHistory
from abmodel.models import DiseaseStates
from abmodel.models import SusceptibilityGroups
from abmodel.models import ImmunizationGroups
from abmodel.models import MobilityGroups
from abmodel.models import IsolationAdherenceGroups
from abmodel.models import MRAdherenceGroups
from abmodel.models import HealthSystem
from abmodel.models import InterestVariables
from abmodel.models import MRTStopModes
from abmodel.models import CyclicMRModes
from abmodel.models import GlobalCyclicMR


# =============================================================================
def init_calculate_max_time_iterative(
    key: str,
    natural_history: NaturalHistory
) -> bool:
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        See Also
        --------
        init_calculate_max_time_vectorized : TODO complete explanation

        Examples
        --------
        TODO: include some examples
    """
    dist_type = natural_history.items[key] \
        .dist[DistTitles.time.value].dist_type
    return False if dist_type is None else True


def init_calculate_max_time_vectorized(
    key: Series,  # str
    natural_history: NaturalHistory
) -> Series:
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        See Also
        --------
        init_calculate_max_time_iterative : TODO complete explanation

        Examples
        --------
        TODO: include some examples
    """
    return list(map(
        lambda single_key: False if natural_history
        .items[single_key]
        .dist[DistTitles.time.value].dist_type is None else True,
        key
    ))


# =============================================================================
def calculate_max_time_iterative(
    key: str,
    disease_state: str,
    do_calculate_max_time: bool,
    disease_state_time: Union[float, None],
    disease_state_max_time: Union[float, None],
    disease_groups: DiseaseStates,
    natural_history: NaturalHistory
) -> Series([float, float]):
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        See Also
        --------
        calculate_max_time_vectorized : TODO complete explanation

        Examples
        --------
        TODO: include some examples
    """
    if do_calculate_max_time:
        if disease_groups.items[disease_state].is_dead:
            return Series([nan, nan])
        else:
            return Series([0,
                           natural_history.items[key]
                           .dist[DistTitles.time.value]
                           .sample()
                           ])
    else:
        return Series([disease_state_time, disease_state_max_time])


# TODO: Reimplement this function in order to also return disease_state_time
def calculate_max_time_vectorized(
    key: Series,  # str
    do_calculate_max_time: Series,  # bool
    disease_state_time: Series,  # float or None
    disease_state_max_time: Series,  # float or None
    natural_history: NaturalHistory
) -> Series:  # Series of float
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        See Also
        --------
        calculate_max_time_iterative : TODO complete explanation

        Examples
        --------
        TODO: include some examples
    """
    return list(map(
        lambda single_key, cond, time_value: natural_history
        .items[single_key]
        .dist[DistTitles.time.value]
        .sample() if cond else time_value,
        zip(key, do_calculate_max_time, disease_state_max_time)
    ))


# =============================================================================
def transition_function(
    disease_state: str,
    disease_state_time: float,
    disease_state_max_time: float,
    is_dead: bool,
    key: str,
    disease_groups: DiseaseStates,
    natural_history: NaturalHistory
) -> Series([str, float, bool, bool, bool]):
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        Examples
        --------
        TODO: include some examples
    """
    # Set False the flag that forces to calculate
    # disease state max time and the flag that forces to update immunization
    # params. They are going to be changed to True if disease state changes
    do_calculate_max_time = False
    do_update_immunization_params = False

    if not isnan(disease_state_max_time):
        if disease_state_time >= disease_state_max_time:
            # Get the transitions info for the current
            # key (vulnerability_group, current disease_state)
            transitions = natural_history.items[key].transitions

            # Get disease_states enabled for the probable transition and
            # their corresponding probabilities
            disease_states = list(transitions.keys())
            probabilities = [
                transitions[transition].probability
                for transition in disease_states
                ]

            # disease state must change
            # Verify: becomes into? ... Throw the dice
            disease_state = choice(
                disease_states,
                p=probabilities
                )

            # Set True the flag that forces to calculate
            # disease state max time
            do_calculate_max_time = True

            # Set True the flag that forces to update
            # immunization params
            do_update_immunization_params = True

            # Update is_dead value
            is_dead = disease_groups.items[disease_state].is_dead

    return Series([disease_state, disease_state_time, is_dead,
                   do_calculate_max_time, do_update_immunization_params])


# =============================================================================
def hospitalization_vectorized(
    is_hospitalized: Series,
    is_in_ICU: Series,
    disease_states: Series,
    is_dead: Series,
    reduction_factor: Series,
    dead_disease_group: str,
    alpha: float,  # Reduction factor of spread prob due to hospitalization
    disease_groups: DiseaseStates,
    health_system: HealthSystem
) -> DataFrame:
    """
        TODO: Add brief explanation
        # step 1: no is_hospitalized and disease_state has probability
        # to be hospitalized

        # step 2: is_hospitalized ... No matter if disease states
        # changes or not ... Throw dice to see if agent still
        # hospitalized

        # step 3: if one agent cannot be hospitalized, see if it dies
        # because of disease

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        Examples
        --------
        TODO: include some examples
    """
    # Get former is_hospitalized info
    agents_number = len(is_hospitalized)

    # Please be aware that if an agent is in ICU, then it must be
    # hospitalized too
    former_is_hospitalized = deepcopy(is_hospitalized)
    former_is_in_ICU = deepcopy(is_in_ICU)

    # ICU state has higher priority
    # Verify: is going to be in ICU or remains in ICU?
    # ... Throw the dice ... Do it for all the agents
    dice = random_sample(agents_number)

    ICU_prob = array([
        disease_groups
        .items[disease_state]
        .dist[DistTitles.icu_prob.value]
        .sample()
        for disease_state in disease_states
        ])
    ICU_prob[equal(ICU_prob, None)] = 0

    # if dice <= ICU_prob
    # agent should be in ICU
    is_in_ICU = where(
        dice <= ICU_prob,
        full(agents_number, True),
        full(agents_number, False)
        )

    new_in_ICU_number = len(
        where(equal(is_in_ICU, True))[0]
        )

    if new_in_ICU_number > health_system.ICU_capacity:
        # Health system got overloaded in ICU
        # Some agents are susceptible to die
        # 1. Those agents that were in ICU before, should remain in ICU
        # 2. New agents in ICU, must throw the dice to see who dies
        # or who survives.

        # NOTE: if on the contrary, health system still having
        # ICU capacity, then this ICU vacancy can be used for
        # hospitalization if the health system gets overloaded
        # for hospitalization, in other words, hospitalization
        # vacancy includes ICU vacancy, but the contrary doesn't hold.
        # This is simulated enabling that those in ICU are also
        # hospitalized

        completely_new_in_ICU = where(
            (equal(is_in_ICU, True)) & (equal(former_is_in_ICU, False))
            )[0]

        must_die_number = new_in_ICU_number \
            - health_system.ICU_capacity

        # Update new_in_ICU_number
        new_in_ICU_number = health_system.ICU_capacity

        must_die = choice(
            completely_new_in_ICU,
            size=must_die_number,
            replace=False
            )

        # Update disease state of those that died
        disease_states[must_die] = dead_disease_group

        # Update is_dead for those that died
        is_dead[must_die] = True

        is_in_ICU_False = where(equal(is_in_ICU, False))[0]
        is_in_ICU_True = where(equal(is_in_ICU, True))[0]

        new_is_in_ICU_False = concatenate([is_in_ICU_False, must_die])
        mask = isin(is_in_ICU_True, must_die, invert=True)
        new_is_in_ICU_True = is_in_ICU_True[mask]

        # Update values
        is_in_ICU[new_is_in_ICU_False] = False
        is_in_ICU[new_is_in_ICU_True] = True

    # Next step is to change hospitalization state
    # Verify: is going to be hospitalized or remains hospitalized?
    # ... Throw the dice ... Do it for all the agents
    dice = random_sample(agents_number)

    hospitalization_prob = array([
        disease_groups
        .items[disease_state]
        .dist[DistTitles.hospitalization.value]
        .sample()
        for disease_state in disease_states
        ])
    hospitalization_prob[equal(hospitalization_prob, None)] = 0

    # if dice <= hospitalization_prob
    # agent should be hospitalized
    is_hospitalized = where(
        dice <= hospitalization_prob,
        full(agents_number, True),
        full(agents_number, False)
        )

    # Merge this new is_hospitalized with those
    # new hospitalized due to ICU
    # Remember that those in ICU are also hospitalized
    is_hospitalized = where(
        (equal(is_hospitalized, False)) & (equal(is_in_ICU, True)),
        full(agents_number, True),
        is_hospitalized
        )

    new_hospitalized_number = len(
        where(equal(is_hospitalized, True))[0]
        )

    if new_hospitalized_number > health_system.hospital_capacity:
        # Health system got overloaded in hospital vacancy
        # Some agents are susceptible to die
        # 1. ICU has higher priority. Those agents that are in ICU,
        # should remain in ICU
        # 2. New hospitalized agents, that are not in ICU, must throw
        # the dice to see who dies or who survives.
        completely_new_hospitalized_not_in_ICU = where(
            (equal(is_hospitalized, True)) & (equal(is_in_ICU, False))
            & (equal(former_is_hospitalized, False))
            )[0]

        susceptible_to_die_number = len(
            completely_new_hospitalized_not_in_ICU
            )

        must_die_number = new_hospitalized_number \
            - health_system.hospital_capacity

        if must_die_number < susceptible_to_die_number:
            must_die = choice(
                completely_new_hospitalized_not_in_ICU,
                size=must_die_number,
                replace=False
                )
        elif susceptible_to_die_number == must_die_number:
            must_die = completely_new_hospitalized_not_in_ICU
        else:
            # must_die_number > susceptible_to_die_number
            # The surplus of must die number forces us to include the
            # possibility that some former hospitalized not in UCI have
            # died
            must_die_number_surplus = must_die_number \
                - susceptible_to_die_number

            remain_hospitalized_but_not_in_ICU = where(
                (equal(is_hospitalized, True)) & (equal(is_in_ICU, False))
                & (equal(former_is_hospitalized, True))
                )[0]

            must_die_surplus = choice(
                remain_hospitalized_but_not_in_ICU,
                size=must_die_number_surplus,
                replace=False
                )

            must_die = concatenate([
                must_die_surplus,
                completely_new_hospitalized_not_in_ICU
            ])

        # Update disease state of those that died
        disease_states[must_die] = dead_disease_group

        # Update is_dead for those that died
        is_dead[must_die] = True

        is_hospitalized_False = where(equal(is_hospitalized, False))[0]
        is_hospitalized_True = where(equal(is_hospitalized, True))[0]

        new_is_hospitalized_False = concatenate([
            is_hospitalized_False, must_die
            ])
        mask = isin(is_hospitalized_True, must_die, invert=True)
        new_is_hospitalized_True = is_hospitalized_True[mask]

        # Update values
        is_hospitalized[new_is_hospitalized_False] = False
        is_hospitalized[new_is_hospitalized_True] = True

    # Determine indexes for changing reduction factor
    new_hospitalized_indexes = where(
        (equal(is_hospitalized, True)) & (equal(former_is_hospitalized, False))
        )[0]

    recovered_from_hospitalization_indexes = where(
        (equal(is_hospitalized, False)) & (equal(former_is_hospitalized, True))
        )[0]

    # Calculate reduction factor
    reduction_factor_copy = reduction_factor.copy()

    reduction_factor_copy[new_hospitalized_indexes] = \
        reduction_factor[new_hospitalized_indexes]*alpha

    reduction_factor_copy[recovered_from_hospitalization_indexes] = \
        reduction_factor[recovered_from_hospitalization_indexes]/alpha

    # Wrap data together
    data = array([is_hospitalized, is_in_ICU, disease_states, is_dead,
                 reduction_factor_copy])
    data_transposed = transpose(data)

    return DataFrame(data_transposed)


# =============================================================================
def diagnosis_function(
    disease_state: str,
    is_dead: bool,
    is_diagnosed: bool,
    disease_groups: DiseaseStates
) -> bool:
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        Examples
        --------
        TODO: include some examples
    """
    if is_dead:
        is_diagnosed = False
    else:
        if is_diagnosed:
            # is_diagnosed = True
            # do nothing
            pass
        else:
            # it is not diagnosed
            is_infected = disease_groups \
                .items[disease_state].is_infected
            if is_infected:
                # Agent can be diagnosed
                # Verify: is going to be diagnosed? ... Throw the dice
                dice = random_sample()

                be_diagnosed_prob = disease_groups \
                    .items[disease_state] \
                    .dist[DistTitles.diagnosis.value] \
                    .sample()

                if dice <= be_diagnosed_prob:
                    # Agent was diagnosed !!!
                    is_diagnosed = True
                else:
                    # Agent was not diagnosed
                    # do nothing
                    pass
            else:
                is_diagnosed = False
    return is_diagnosed


# =============================================================================
def isolation_function(
    disease_state: str,
    disease_groups: DiseaseStates
) -> tuple[bool, float, float]:
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        Examples
        --------
        TODO: include some examples
    """
    # How much time is going to be isolated?
    # ... Throw the dice
    # isolation_max_time is in the scale of days
    isolation_max_time = disease_groups \
        .items[disease_state] \
        .dist[DistTitles.isolation_days.value] \
        .sample()

    isolation_time = 0.0
    is_isolated = True

    return is_isolated, isolation_time, isolation_max_time


def isolation_handler(
    disease_state: str,
    isolation_adherence_group: str,
    is_diagnosed: bool,
    is_isolated: bool,
    isolation_time: float,
    isolation_max_time: float,
    adheres_to_isolation: bool,
    reduction_factor: float,
    beta: float,  # Reduction factor of spread prob due to being isolated
    disease_groups: DiseaseStates,
    isolation_adherence_groups: Optional[IsolationAdherenceGroups] = None
) -> Series([bool, bool, float, float, bool, float]):
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        See Also
        --------
        isolation_function : TODO complete explanation

        Examples
        --------
        TODO: include some examples
    """
    if not is_diagnosed:
        # is_diagnosed = False
        # do nothing
        pass
    else:
        # it is diagnosed
        if is_isolated:
            # it is isolated
            if isolation_time >= isolation_max_time:
                # isolation must end
                isolation_time = nan
                isolation_max_time = nan
                is_isolated = False
                is_diagnosed = False
                reduction_factor = reduction_factor/beta
            else:
                # isolation has not finished yet
                # do nothing
                pass
        else:
            # it is not isolated
            if isolation_adherence_groups is None:
                # Agent always adheres to isolation
                adheres_to_isolation = True
                reduction_factor = reduction_factor*beta

                (is_isolated, isolation_time,
                    isolation_max_time) = isolation_function(
                    disease_state,
                    disease_groups
                )
            else:
                # isolation_adherence_groups is not None

                # Does agent adhere to be isolated?
                # ... Throw the dice
                dice = random_sample()

                adherence_prob = isolation_adherence_groups.items[
                    isolation_adherence_group
                    ].dist[
                        DistTitles.adherence.value
                        ].sample()

                if dice <= adherence_prob:
                    # Agent adheres to isolation
                    adheres_to_isolation = True
                    reduction_factor = reduction_factor*beta

                    (is_isolated, isolation_time,
                        isolation_max_time) = isolation_function(
                        disease_state,
                        disease_groups
                    )
                else:
                    # Agent doesn't adhere to isolation
                    # do nothing
                    adheres_to_isolation = False

    return Series([is_diagnosed, is_isolated, isolation_time,
                   isolation_max_time, adheres_to_isolation,
                   reduction_factor])


def mr_handler(
    mr_group: str,
    mr_adherence_group: str,
    is_diagnosed: bool,
    reduction_factor: float,
    beta: float,  # Reduction factor of spread prob due to being isolated
    mrc_target_groups: list,
    mr_adherence_groups: Optional[IsolationAdherenceGroups] = None
) -> Series([bool, bool, float]):
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        See Also
        --------
        isolation_function : TODO complete explanation

        Examples
        --------
        TODO: include some examples
    """
    if mr_group not in mrc_target_groups:
        # it is not isolated by mr
        adheres_to_mr_isolation = False
        isolated_by_mr = False
    else:
        # it is isolated by mr
        isolated_by_mr = True
        if mr_adherence_groups is None:
            # Agent always adheres to isolation
            adheres_to_mr_isolation = True
            reduction_factor = reduction_factor*beta
        else:
            # mr_adherence_groups is not None

            # Does agent adhere to be isolated?
            # ... Throw the dice
            dice = random_sample()

            adherence_prob = mr_adherence_groups.items[
                mr_adherence_group
                ].dist[
                    DistTitles.mr_adherence.value
                    ].sample()

            if dice <= adherence_prob:
                # Agent adheres to isolation
                adheres_to_mr_isolation = True
                if is_diagnosed:
                    reduction_factor = reduction_factor*beta
            else:
                # Agent doesn't adhere to isolation
                adheres_to_mr_isolation = False

    return Series([isolated_by_mr, adheres_to_mr_isolation, reduction_factor])


# =============================================================================
def contagion_function(
    agent: int,
    x: float,
    y: float,
    immunization_level: float,
    key: str,
    disease_state: str,
    susceptibility_group: str,
    times_infected: int,
    disease_state_time: float,
    reduction_factor: float,
    natural_history: NaturalHistory,
    disease_groups: DiseaseStates,
    susceptibility_groups: SusceptibilityGroups,
    kdtree_by_disease_state: dict,
    agents_labels_by_disease_state: dict,
    df_copy: DataFrame
) -> Series([str, int, list, float, bool, bool]):
    """
        TODO
        # Set None the disease_state_time
        # It should be changed to zero 0 if gets infected

        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        Examples
        --------
        TODO: include some examples
    """
    # Set False the flag that forces to calculate
    # disease state max time and the flag that forces to update immunization
    # params. They are going to be changed to True if disease state changes
    do_calculate_max_time = False
    do_update_immunization_params = False

    # List to save who infected the agent
    infected_by = []

    # Get transition_by_contagion boolean
    transition_by_contagion = \
        natural_history.items[key].transition_by_contagion

    if transition_by_contagion:
        # Get the transitions info for the current
        # key (vulnerability_group, current disease_state)
        transitions = natural_history.items[key].transitions

        # Get disease_states enabled for the probable transition
        # after contagion and and their corresponding probabilities
        disease_states = list(transitions.keys())
        probabilities = [
            transitions[transition].probability
            for transition in disease_states
            ]

        # Agent location
        agent_location = [x, y]

        # Cycle through each spreader to see if the agent gets
        # infected by the spreader
        spreaders = []
        for disease_state_label in disease_groups.items.keys():
            if disease_groups.items[disease_state_label].can_spread:
                spreaders.append(disease_state_label)

        for spreader_state in spreaders:
            if kdtree_by_disease_state[spreader_state]:
                # Retrieve spread_radius
                spread_radius = \
                    disease_groups.items[spreader_state] \
                    .spread_radius

                # Detect if the agents of "disease_state" that are
                # inside a distance equal to the tracing_radius
                # points_inside_radius_array is a ndarray with a
                # list of indeces which correspond neighbors of
                # agent
                points_inside_radius_array = \
                    kdtree_by_disease_state[spreader_state] \
                    .query_ball_point(
                        agent_location,
                        spread_radius
                        )

                # Now we have to get the corresponding spreader
                # labels excluding the agent's own label
                spreader_labels_inside_radius = list(setdiff1d(
                        agents_labels_by_disease_state[
                            spreader_state][
                            points_inside_radius_array],
                        agent
                        )
                    )

                # Calculate joint probability for contagion
                spread_probability = disease_groups.items[spreader_state] \
                    .spread_probability

                joint_probability = \
                    (1.0 - immunization_level) \
                    * (susceptibility_groups.items[susceptibility_group]
                       .dist[DistTitles.susceptibility.value].sample()) \
                    * spread_probability * reduction_factor

                # Check if got infected
                for spreader in spreader_labels_inside_radius:
                    # Throw the dice
                    dice = random_sample()

                    if dice <= joint_probability:
                        # Got infected !!!
                        # Save who infected the agent
                        infected_by.append(spreader)

        if len(infected_by) != 0:
            # Update times_infected
            times_infected += 1

            # Verify: becomes into? ... Throw the dice
            disease_state = choice(
                disease_states,
                p=probabilities
                )

            # Set the time elapsed since it got infected
            # in zero
            disease_state_time = 0

            # Set True the flag that forces to calculate
            # disease state max time
            do_calculate_max_time = True

            # Set True the flag that forces to update
            # immunization params
            do_update_immunization_params = True
    else:
        # transition_by_contagion == False
        # It is supposed that this is the case for those with is_dead == True
        pass

    return Series([disease_state, times_infected, infected_by,
                   disease_state_time, do_calculate_max_time,
                   do_update_immunization_params])


# =============================================================================
def init_immunization_params_iterative(
    immunization_group: str,
    immunization_level: float,
    immunization_groups: ImmunizationGroups
) -> Series([float, float, float]):
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        Examples
        --------
        TODO: include some examples
    """
    if immunization_level != 0:

        distribution = immunization_groups \
            .items[immunization_group] \
            .dist[DistTitles.immunization_time.value]

        if distribution.dist_type is not None:
            # Init immunization_time
            # In scale of days
            immunization_time = 0

            # Calculate immunization_max_time
            # In scale of days
            immunization_max_time = distribution.sample()

            # Calculate immunization_slope
            immunization_slope = - immunization_level/immunization_max_time
        else:
            raise ValueError(
                f"Error with {DistTitles.immunization_time.value} for"
                f"immunization group '{immunization_group}': "
                "If immunization_level != 0"
                f"then {DistTitles.immunization_time.value} must not be None"
                )
    else:
        immunization_time = nan
        immunization_max_time = nan
        immunization_slope = nan

    return Series([immunization_time, immunization_max_time,
                   immunization_slope])


def update_immunization_params_iterative(
    key: str,  # Must correspond to the outdated key
    disease_state: str,
    immunization_level: float,
    immunization_slope: float,
    immunization_time: float,  # In scale of days
    immunization_max_time: float,  # In scale of days
    do_update_immunization_params: bool,
    natural_history: NaturalHistory
) -> Series([float, float, float, float, bool]):
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        Examples
        --------
        TODO: include some examples
    """
    if do_update_immunization_params:
        # Get the transitions info for the former
        # key (vulnerability_group, former disease_state)
        transitions = natural_history.items[key].transitions

        # Update immunization_level with the gain
        gain = transitions[disease_state] \
            .immunization_gain

        immunization_level = min([immunization_level + gain, 1.0])

        # Update immunization_max_time and immunization_slope
        addend = transitions[disease_state] \
            .dist[DistTitles.immunization_time.value] \
            .sample()

        if addend is not None:
            if isnan(immunization_max_time):
                immunization_time_remainder = 0.0
            else:
                immunization_time_remainder = immunization_max_time \
                                            - immunization_time

            immunization_max_time = addend + immunization_time_remainder
        else:
            pass

        if not isnan(immunization_max_time):
            immunization_slope = - immunization_level/immunization_max_time
        else:
            immunization_slope = nan

        # Restart immnuzation_time
        immunization_time = 0

        do_update_immunization_params = False

    return Series([immunization_level, immunization_slope, immunization_time,
                   immunization_max_time, do_update_immunization_params])


# =============================================================================
def update_immunization_level_iterative(
    dt: float,  # In scale of days
    immunization_level: float,
    immunization_slope: float,
    immunization_time: float,  # In scale of days
    immunization_max_time: float  # In scale of days
) -> Series([float, float, float, float]):
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        See Also
        --------
        immunization_function : TODO complete explanation

        Examples
        --------
        TODO: include some examples
    """
    if immunization_time < immunization_max_time:
        immunization_level = immunization_slope * dt + immunization_level
        immunization_time = immunization_time + dt
    else:
        # immunization_time >= immunization_max_time
        immunization_level = 0
        immunization_slope = nan
        immunization_time = nan
        immunization_max_time = nan

    return Series([immunization_level, immunization_slope, immunization_time,
                   immunization_max_time])


# =============================================================================
def alertness_function(
    agent: int,
    key: str,
    x: float,
    y: float,
    is_dead: bool,
    vulnerability_group: str,
    disease_state: str,
    natural_history: NaturalHistory,
    disease_groups: DiseaseStates,
    kdtree_by_disease_state: dict,
    agents_labels_by_disease_state: dict,
    dead_disease_group: str
) -> Series([bool, list]):
    """
        TODO: Add brief explanation

        Parameters
        ----------
        TODO

        Returns
        -------
        TODO

        Notes
        -----
        TODO: include mathematical description and explanatory image

        Examples
        --------
        TODO: include some examples
    """
    is_alert = False
    alerted_by = []

    if is_dead:
        pass
    else:
        all_avoidable_neighbors = array([])

        # Agent location
        agent_location = [x, y]

        # =============================================
        # Cycle through each state of the neighbors to see if the agent
        # should be alert

        for avoidable_state in disease_groups.items.keys():
            if avoidable_state != dead_disease_group:
                # Compute avoidable_agent_key
                avoidable_agent_key = std_str_join_cols(
                    str(vulnerability_group),
                    str(avoidable_state)
                    )

                # Get radius to avoid an avoidable_agent (avoidance_radius)
                avoidance_radius = natural_history \
                    .items[avoidable_agent_key].avoidance_radius

                if (avoidance_radius != 0
                   and kdtree_by_disease_state[avoidable_state]):
                    # Detect if any avoidable agent is inside a distance
                    # equal to the corresponding avoidance_radius
                    points_inside_radius_array = \
                        kdtree_by_disease_state[avoidable_state] \
                        .query_ball_point(
                            agent_location,
                            avoidance_radius
                            )

                    avoidable_neighbors = setdiff1d(
                        agents_labels_by_disease_state[
                            avoidable_state][
                            points_inside_radius_array],
                        agent
                        )

                    if len(avoidable_neighbors) != 0:

                        all_avoidable_neighbors = concatenate(
                            (all_avoidable_neighbors, avoidable_neighbors),
                            axis=None
                            )

                        for avoidable_agent_index in avoidable_neighbors:
                            # Calculate alertness probability
                            probability = natural_history.items[key] \
                                .dist[DistTitles.alertness.value].sample()

                            if probability:

                                # Must agent be alert ? ... Throw the dice
                                dice = random_sample()

                                # Note that alertness depends on a probability,
                                # which tries to model the probability that an
                                # agent with a defined group and state is alert
                                if dice <= probability:

                                    # Agent is alerted !!!
                                    is_alert = True

                                    # Append avoidable_agent_index in
                                    # alerted_by
                                    alerted_by.append(avoidable_agent_index)

        # float to int
        all_avoidable_neighbors = all_avoidable_neighbors.astype(int)

        # ndarray to list
        all_avoidable_neighbors = all_avoidable_neighbors.tolist()

    return Series([is_alert, alerted_by])


# =============================================================================
class AgentDisease:
    """
        TODO: Add brief explanation

        Methods
        -------
        TODO
    """
    @classmethod
    def init_required_fields(
        cls,
        df: DataFrame,
        dead_disease_group: str,
        alpha: float,
        beta: float,
        disease_groups: DiseaseStates,
        natural_history: NaturalHistory,
        health_system: HealthSystem,
        immunization_groups: Optional[ImmunizationGroups] = None,
        isolation_adherence_groups: Optional[IsolationAdherenceGroups] = None,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            TODO

            Examples
            --------
            TODO: include some examples
        """
        # Initialize is_dead
        df = cls.init_is_dead(df, disease_groups, execmode, npartitions)

        # Generate key column
        df = cls.generate_key_col(df, execmode, npartitions)

        # Init disease_state_max_time
        df = cls.init_disease_state_max_time(
            df,
            disease_groups,
            natural_history,
            ExecutionModes.iterative.value
        )

        # Init is_hospìtalized and is_in_ICU
        df = df.assign(is_hospitalized=False)
        df = df.assign(is_in_ICU=False)
        df = df.assign(reduction_factor=1.0)
        df = cls.to_hospitalize_agents(
            df, dead_disease_group, alpha, disease_groups, health_system,
            ExecutionModes.vectorized.value
            )

        # Init is_diagnosed
        df = df.assign(is_diagnosed=False)
        df = cls.to_diagnose_agents(df, disease_groups, execmode, npartitions)

        # Init is_isolated
        df = df.assign(is_isolated=False)
        df = df.assign(isolation_time=nan)
        df = df.assign(isolation_max_time=nan)
        df = df.assign(adheres_to_isolation=True)
        dt = 0.0  # Set dt to zero for initialization purposes
        df = cls.to_isolate_agents(
            df, dt, beta, disease_groups,
            isolation_adherence_groups, execmode, npartitions
            )

        # Init has_mr_restictions
        df = df.assign(isolated_by_mr=False)
        df = df.assign(adheres_to_mr_isolation=True)
        # df = cls.mr_isolate_agents(
        #    df, dt, beta, disease_groups, isolation_adherence_groups, execmode
        #    )

        # Init times_infected
        df = cls.init_times_infected(df, disease_groups, execmode, npartitions)

        if immunization_groups is not None:
            # Init immunization_level
            df = cls.init_immunization_level(
                df, immunization_groups, execmode, npartitions
            )

            # Init immunization params
            df = cls.init_immunization_params(
                df, immunization_groups, execmode, npartitions
            )
        else:
            # Init immunization_level
            df = df.assign(immunization_level=0)

            # Init immunization params
            df = df.assign(immunization_time=nan)
            df = df.assign(immunization_max_time=nan)
            df = df.assign(immunization_slope=nan)

        return df

    @classmethod
    def init_is_dead(
        cls,
        df: DataFrame,
        disease_groups: DiseaseStates,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df["is_dead"] = df.apply(
                    lambda row: disease_groups
                    .items[row["disease_state"]].is_dead,
                    axis=1
                )
            elif execmode == ExecutionModes.dask.value:
                df = from_pandas(df, npartitions=npartitions)
                df["is_dead"] = df.apply(
                    lambda row: disease_groups
                    .items[row["disease_state"]].is_dead,
                    axis=1,
                    meta=('is_dead', 'bool')
                )
                df = df.compute()
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["disease_state"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def init_times_infected(
        cls,
        df: DataFrame,
        disease_groups: DiseaseStates,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df["times_infected"] = df.apply(
                    lambda row: 1 if disease_groups
                    .items[row["disease_state"]].is_infected else 0,
                    axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                df = from_pandas(df, npartitions=npartitions)
                df["times_infected"] = df.apply(
                    lambda row: 1 if disease_groups
                    .items[row["disease_state"]].is_infected else 0,
                    axis=1,
                    meta=(0, "int64")
                )
                df = df.compute()
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["disease_state"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def init_immunization_level(
        cls,
        df: DataFrame,
        immunization_groups: ImmunizationGroups,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df["immunization_level"] = df.apply(
                    lambda row: immunization_groups
                    .items[row["immunization_group"]].dist[
                        DistTitles.immunization_level.value].sample(),
                    axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                df = from_pandas(df, npartitions=npartitions)
                df["immunization_level"] = df.apply(
                    lambda row: immunization_groups
                    .items[row["immunization_group"]].dist[
                        DistTitles.immunization_level.value].sample(),
                    axis=1,
                    meta=(0, "int64")
                )
                df = df.compute()
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["immunization_group"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def init_immunization_params(
        cls,
        df: DataFrame,
        immunization_groups: Optional[ImmunizationGroups],
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df[["immunization_time", "immunization_max_time",
                    "immunization_slope"]] = df.apply(
                    lambda row: init_immunization_params_iterative(
                        row["immunization_group"],
                        row["immunization_level"],
                        immunization_groups
                        ),
                        axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                df = from_pandas(df, npartitions=npartitions)
                df[["immunization_time", "immunization_max_time",
                    "immunization_slope"]] = df.apply(
                        lambda row: init_immunization_params_iterative(
                            row["immunization_group"],
                            row["immunization_level"],
                            immunization_groups
                        ),
                        axis=1,
                        meta={
                            0: "float64",
                            1: "float64",
                            2: "float64"
                        }
                    )
                df = df.compute()
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["immunization_group", "immunization_level"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def generate_key_col(
        cls,
        df: DataFrame,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            std_str_join_cols : TODO complete explanation

            check_field_existance : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df["key"] = df.apply(
                    lambda row: std_str_join_cols(
                        str(row["vulnerability_group"]),
                        str(row["disease_state"])
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                df = from_pandas(df, npartitions=npartitions)
                df["key"] = df.apply(
                    lambda row: std_str_join_cols(
                        str(row["vulnerability_group"]),
                        str(row["disease_state"])
                        ),
                    axis=1,
                    meta=(0, "str")
                    )
                df = df.compute()
            elif execmode == ExecutionModes.vectorized.value:
                df["key"] = std_str_join_cols(
                    df["vulnerability_group"],
                    df["disease_state"]
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["disease_state", "vulnerability_group"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def init_disease_state_max_time(
        cls,
        df: DataFrame,
        disease_groups: DiseaseStates,
        natural_history: NaturalHistory,
        execmode: ExecutionModes = ExecutionModes.iterative.value
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            init_calculate_max_time_iterative : TODO complete explanation

            init_calculate_max_time_vectorized : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            # Init disease_state_time and disease_state_max_time with None
            df = df.assign(disease_state_time=nan)
            df = df.assign(disease_state_max_time=nan)

            if execmode == ExecutionModes.iterative.value:
                df["do_calculate_max_time"] = df.apply(
                    lambda row: init_calculate_max_time_iterative(
                        row["key"],
                        natural_history
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.vectorized.value:
                df["do_calculate_max_time"] = \
                    init_calculate_max_time_vectorized(
                        df["key"],
                        natural_history
                        )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["key"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            # Call determine_disease_state_max_time function in order
            # to calculate it for those agents who are infected
            df = cls.determine_disease_state_max_time(
                df, disease_groups, natural_history, execmode
            )
            return df

    # TODO: Reimplement calculate_max_time_vectorized
    @classmethod
    def determine_disease_state_max_time(
        cls,
        df: DataFrame,
        disease_groups: DiseaseStates,
        natural_history: NaturalHistory,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[float] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            calculate_max_time_iterative : TODO complete explanation

            calculate_max_time_vectorized : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df[["disease_state_time",
                    "disease_state_max_time"]] = df.apply(
                    lambda row: calculate_max_time_iterative(
                        row["key"],
                        row["disease_state"],
                        row["do_calculate_max_time"],
                        row["disease_state_time"],
                        row["disease_state_max_time"],
                        disease_groups,
                        natural_history
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                df = from_pandas(df, npartitions=npartitions)
                df[["disease_state_time",
                    "disease_state_max_time"]] = df.apply(
                    lambda row: calculate_max_time_iterative(
                        row["key"],
                        row["disease_state"],
                        row["do_calculate_max_time"],
                        row["disease_state_time"],
                        row["disease_state_max_time"],
                        disease_groups,
                        natural_history
                        ),
                    axis=1,
                    meta={
                        0: "float64",
                        1: "float64"
                    }
                    )
                df = df.compute()
            # TODO: Reimplement calculate_max_time_vectorized
            # elif execmode == ExecutionModes.vectorized.value:
            #     df["disease_state_max_time"] = calculate_max_time_vectorized(
            #         df["key"],
            #         df["do_calculate_max_time"],
            #         df["disease_state_max_time"],
            #         natural_history
            #         )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["disease_state_max_time", "disease_state_time",
                               "key", "do_calculate_max_time"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            # Restart do_calculate_max_time
            df = df.assign(do_calculate_max_time=False)

            return df

    @classmethod
    def disease_state_transition(
        cls,
        df: DataFrame,
        dt: float,  # In scale of days
        disease_groups: DiseaseStates,
        natural_history: NaturalHistory,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            transition_function : TODO complete explanation

            determine_disease_state_max_time : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                # Update disease state time
                df["disease_state_time"] = df["disease_state_time"] + dt

                df[["disease_state", "disease_state_time", "is_dead",
                    "do_calculate_max_time",
                    "do_update_immunization_params"]] = df.apply(
                    lambda row: transition_function(
                        row["disease_state"],
                        row["disease_state_time"],
                        row["disease_state_max_time"],
                        row["is_dead"],
                        row["key"],
                        disease_groups,
                        natural_history
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                # Update disease state time
                df = from_pandas(df, npartitions=npartitions)
                df["disease_state_time"] = df["disease_state_time"] + dt

                df[["disease_state", "disease_state_time", "is_dead",
                    "do_calculate_max_time",
                    "do_update_immunization_params"]] = df.apply(
                    lambda row: transition_function(
                        row["disease_state"],
                        row["disease_state_time"],
                        row["disease_state_max_time"],
                        row["is_dead"],
                        row["key"],
                        disease_groups,
                        natural_history
                        ),
                    axis=1,
                    meta={
                        0: "str",
                        1: "float64",
                        2: "bool",
                        3: "bool",
                        4: "bool"
                    }
                    )
                df = df.compute()

            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )

            # Call determine_disease_state_max_time function in order
            # to calculate it for those agents who went through a transition
            df = cls.determine_disease_state_max_time(
                df, disease_groups, natural_history, execmode
                )

            # Call update_immunization_params function in order to update them
            # for those agents who went through a transition
            df = cls.update_immunization_params(
                df, natural_history, execmode
                )

            # Update key column
            df = cls.generate_key_col(df, execmode)

        except Exception as error:
            validation_list = ["disease_state", "disease_state_time",
                               "is_dead", "key", "disease_state_max_time"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def to_hospitalize_agents(
        cls,
        df: DataFrame,
        dead_disease_group: str,
        alpha: float,  # Reduction factor of spread prob due to hospitalization
        disease_groups: DiseaseStates,
        health_system: HealthSystem,
        execmode: ExecutionModes = ExecutionModes.vectorized.value
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            hospitalization_vectorized : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.vectorized.value:
                df[["is_hospitalized", "is_in_ICU",
                    "disease_state", "is_dead",
                    "reduction_factor"]] = hospitalization_vectorized(
                    df["is_hospitalized"],
                    df["is_in_ICU"],
                    df["disease_state"],
                    df["is_dead"],
                    df["reduction_factor"],
                    dead_disease_group,
                    alpha,
                    disease_groups,
                    health_system
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["is_hospitalized", "is_in_ICU", "disease_state",
                               "is_dead", "reduction_factor"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def to_diagnose_agents(
        cls,
        df: DataFrame,
        disease_groups: DiseaseStates,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            diagnosis_function : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df["is_diagnosed"] = df.apply(
                    lambda row: diagnosis_function(
                        row["disease_state"],
                        row["is_dead"],
                        row["is_diagnosed"],
                        disease_groups
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                df = from_pandas(df, npartitions=npartitions)
                df["is_diagnosed"] = df.apply(
                    lambda row: diagnosis_function(
                        row["disease_state"],
                        row["is_dead"],
                        row["is_diagnosed"],
                        disease_groups
                        ),
                    axis=1,
                    meta=(0, "bool")
                    )
                df = df.compute()
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["disease_state", "is_dead", "is_diagnosed"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def to_isolate_agents(
        cls,
        df: DataFrame,
        dt: float,  # dt represents the iteration_time in the scale of days,
        beta: float,  # Reduction factor of spread prob due to being isolated
        disease_groups: DiseaseStates,
        isolation_adherence_groups: Optional[IsolationAdherenceGroups] = None,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            isolation_handler : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                # Update isolation time
                df["isolation_time"] = df["isolation_time"] + dt

                df[["is_diagnosed", "is_isolated", "isolation_time",
                    "isolation_max_time", "adheres_to_isolation",
                    "reduction_factor"]] = df.apply(
                    lambda row: isolation_handler(
                        row["disease_state"],
                        row["isolation_adherence_group"],
                        row["is_diagnosed"],
                        row["is_isolated"],
                        row["isolation_time"],
                        row["isolation_max_time"],
                        row["adheres_to_isolation"],
                        row["reduction_factor"],
                        beta,
                        disease_groups,
                        isolation_adherence_groups
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                # Update isolation time
                df = from_pandas(df, npartitions=npartitions)
                df["isolation_time"] = df["isolation_time"] + dt

                df[["is_diagnosed", "is_isolated", "isolation_time",
                    "isolation_max_time", "adheres_to_isolation",
                    "reduction_factor"]] = df.apply(
                    lambda row: isolation_handler(
                        row["disease_state"],
                        row["isolation_adherence_group"],
                        row["is_diagnosed"],
                        row["is_isolated"],
                        row["isolation_time"],
                        row["isolation_max_time"],
                        row["adheres_to_isolation"],
                        row["reduction_factor"],
                        beta,
                        disease_groups,
                        isolation_adherence_groups
                        ),
                    axis=1,
                    meta={
                        0: "bool",
                        1: "bool",
                        2: "float64",
                        3: "float64",
                        4: "bool",
                        5: "float64",
                    }
                    )
                df = df.compute()
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["disease_state", "isolation_adherence_group",
                               "is_isolated", "is_diagnosed", "isolation_time",
                               "isolation_max_time", "adheres_to_isolation",
                               "reduction_factor"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def to_isolate_agents_by_mr(
        cls,
        df: DataFrame,
        mrc_target_groups: list,
        beta: float,  # Reduction factor of spread prob due to being isolated
        mr_adherence_groups: Optional[IsolationAdherenceGroups] = None,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            isolation_handler : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df[["isolated_by_mr", "adheres_to_mr_isolation",
                    "reduction_factor"]] = df.apply(
                    lambda row: mr_handler(
                        row["mr_group"],
                        row["mr_adherence_group"],
                        row["is_diagnosed"],
                        row["reduction_factor"],
                        beta,
                        mrc_target_groups,
                        mr_adherence_groups
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                df = from_pandas(df, npartitions=npartitions)
                df[["isolated_by_mr", "adheres_to_mr_isolation",
                    "reduction_factor"]] = df.apply(
                    lambda row: mr_handler(
                        row["mr_group"],
                        row["mr_adherence_group"],
                        row["is_diagnosed"],
                        row["reduction_factor"],
                        beta,
                        mrc_target_groups,
                        mr_adherence_groups
                        ),
                    axis=1,
                    meta={
                        0: "bool",
                        1: "bool",
                        2: "float64"
                    }
                    )
                df = df.compute()
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["mr_group", "mr_adherence_group",
                               "is_diagnosed", "isolated_by_mr",
                               "adheres_to_mr_isolation", "reduction_factor"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def disease_state_transition_by_contagion(
        cls,
        df: DataFrame,
        kdtree_by_disease_state: dict,
        agents_labels_by_disease_state: dict,
        natural_history: NaturalHistory,
        disease_groups: DiseaseStates,
        susceptibility_groups: SusceptibilityGroups,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            contagion_function : TODO complete explanation

            determine_disease_state_max_time : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df_copy = df.copy()

                df[["disease_state", "times_infected", "infected_by",
                    "disease_state_time", "do_calculate_max_time",
                    "do_update_immunization_params"]] = df.apply(
                    lambda row: contagion_function(
                        row["agent"],
                        row["x"],
                        row["y"],
                        row["immunization_level"],
                        row["key"],
                        row["disease_state"],
                        row["susceptibility_group"],
                        row["times_infected"],
                        row["disease_state_time"],
                        row["reduction_factor"],
                        natural_history,
                        disease_groups,
                        susceptibility_groups,
                        kdtree_by_disease_state,
                        agents_labels_by_disease_state,
                        df_copy
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                df_copy = df.copy()
                df = from_pandas(df, npartitions=npartitions)

                df[["disease_state", "times_infected", "infected_by",
                    "disease_state_time", "do_calculate_max_time",
                    "do_update_immunization_params"]] = df.apply(
                    lambda row: contagion_function(
                        row["agent"],
                        row["x"],
                        row["y"],
                        row["immunization_level"],
                        row["key"],
                        row["disease_state"],
                        row["susceptibility_group"],
                        row["times_infected"],
                        row["disease_state_time"],
                        row["reduction_factor"],
                        natural_history,
                        disease_groups,
                        susceptibility_groups,
                        kdtree_by_disease_state,
                        agents_labels_by_disease_state,
                        df_copy
                        ),
                    axis=1,
                    meta={
                        0: "str",
                        1: "int64",
                        2: "object",
                        3: "float64",
                        4: "bool",
                        5: "bool"
                    }
                    )
                df = df.compute()
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )

            # Call determine_disease_state_max_time function in order
            # to calculate it for those agents who went through a transition
            df = cls.determine_disease_state_max_time(
                df, disease_groups, natural_history, execmode
                )

            # Call update_immunization_params function in order to update them
            # for those agents who went through a transition
            df = cls.update_immunization_params(
                df, natural_history, execmode
                )

            # Update key column
            df = cls.generate_key_col(df, execmode)

        except Exception as error:
            validation_list = ["agent", "x", "y", "immunization_level",
                               "key", "disease_state", "susceptibility_group",
                               "times_infected", "disease_state_time",
                               "reduction_factor"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def update_immunization_params(
        cls,
        df: DataFrame,
        natural_history: NaturalHistory,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            update_immunization_params_iterative : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df[["immunization_level", "immunization_slope",
                    "immunization_time", "immunization_max_time",
                    "do_update_immunization_params"]] = df.apply(
                    lambda row: update_immunization_params_iterative(
                        row["key"],  # In this case, this key is the old one
                        row["disease_state"],
                        row["immunization_level"],
                        row["immunization_slope"],
                        row["immunization_time"],  # In scale of days
                        row["immunization_max_time"],  # In scale of days
                        row["do_update_immunization_params"],
                        natural_history
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                df = from_pandas(df, npartitions=npartitions)
                df[["immunization_level", "immunization_slope",
                    "immunization_time", "immunization_max_time",
                    "do_update_immunization_params"]] = df.apply(
                    lambda row: update_immunization_params_iterative(
                        row["key"],  # In this case, this key is the old one
                        row["disease_state"],
                        row["immunization_level"],
                        row["immunization_slope"],
                        row["immunization_time"],  # In scale of days
                        row["immunization_max_time"],  # In scale of days
                        row["do_update_immunization_params"],
                        natural_history
                        ),
                    axis=1,
                    meta={
                        0: "float64",
                        1: "float64",
                        2: "float64",
                        3: "float64",
                        4: "bool"
                    }
                    )
                df = df.compute()
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["key", "disease_state", "immunization_level",
                               "immunization_slope", "immunization_time",
                               "immunization_max_time",
                               "do_update_immunization_params"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def update_immunization_level(
        cls,
        df: DataFrame,
        dt: float,  # In scale of days
        natural_history: NaturalHistory,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            update_immunization_level_iterative : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df[["immunization_level", "immunization_slope",
                    "immunization_time", "immunization_max_time"]] = df.apply(
                    lambda row: update_immunization_level_iterative(
                        dt,  # In scale of days
                        row["immunization_level"],
                        row["immunization_slope"],
                        row["immunization_time"],  # In scale of days
                        row["immunization_max_time"]  # In scale of days
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                df = from_pandas(df, npartitions=npartitions)
                df[["immunization_level", "immunization_slope",
                    "immunization_time", "immunization_max_time"]] = df.apply(
                    lambda row: update_immunization_level_iterative(
                        dt,  # In scale of days
                        row["immunization_level"],
                        row["immunization_slope"],
                        row["immunization_time"],  # In scale of days
                        row["immunization_max_time"]  # In scale of days
                        ),
                    axis=1,
                    meta={
                        0: "float64",
                        1: "float64",
                        2: "float64",
                        3: "float64",
                    }
                    )
                df = df.compute()
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["key", "immunization_level",
                               "immunization_slope", "immunization_time",
                               "immunization_max_time"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def update_alertness_state(
        cls,
        df: DataFrame,
        kdtree_by_disease_state: dict,
        agents_labels_by_disease_state: dict,
        natural_history: NaturalHistory,
        disease_groups: DiseaseStates,
        dead_disease_group: str,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            alertness_function : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df[["is_alert", "alerted_by"]] = df.apply(
                    lambda row: alertness_function(
                        row["agent"],
                        row["key"],
                        row["x"],
                        row["y"],
                        row["is_dead"],
                        row["vulnerability_group"],
                        row["disease_state"],
                        natural_history,
                        disease_groups,
                        kdtree_by_disease_state,
                        agents_labels_by_disease_state,
                        dead_disease_group
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.dask.value:
                df = from_pandas(df, npartitions=npartitions)
                df[["is_alert", "alerted_by"]] = df.apply(
                    lambda row: alertness_function(
                        row["agent"],
                        row["key"],
                        row["x"],
                        row["y"],
                        row["is_dead"],
                        row["vulnerability_group"],
                        row["disease_state"],
                        natural_history,
                        disease_groups,
                        kdtree_by_disease_state,
                        agents_labels_by_disease_state,
                        dead_disease_group
                        ),
                    axis=1,
                    meta={
                        0: "bool",
                        1: "object"
                    }
                    )
                df = df.compute()
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["agent", "key", "x", "y", "is_dead",
                               "vulnerability_group", "disease_state"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    @classmethod
    def apply_mobility_restrictions(
        cls,
        step: int,
        df: DataFrame,
        # mr_groups: MobilityGroups,
        beta: float,
        mrt_policies: Optional[dict] = None,  # MRTracingPolicies
        mrt_policies_df: Optional[DataFrame] = None,
        global_cyclic_mr: Optional[GlobalCyclicMR] = None,
        cyclic_mr_policies: Optional[dict] = None,  # CyclicMRPolicies
        cmr_policies_df: Optional[DataFrame] = None,
        grace_time_in_steps: Optional[int] = None,
        iteration_time: Optional[timedelta] = None,
        mr_adherence_groups: Optional[MRAdherenceGroups] = None,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        npartitions: Optional[int] = 1
    ) -> tuple[DataFrame, DataFrame, DataFrame]:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.agent.execution_modes.ExecutionModes : TODO complete
            explanation

            check_field_existance : TODO complete explanation

            _function : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                # =============================================================
                # Mobility Restrictions - Tracing Policies
                # =============================================================

                # Init mrt_target_groups
                mrt_target_groups = []

                if mrt_policies is not None:
                    # Init policies_status dict
                    policies_status = {"step": step}

                    # Init target_groups_lists
                    target_groups_lists = []

                    for variable, policie in zip(
                        mrt_policies.keys(),
                        mrt_policies.values()
                    ):
                        former_activation_status = mrt_policies_df[
                            variable.value].iloc[-1]

                        if former_activation_status == "disabled":
                            # Find the corresponding count
                            # to assess start level
                            if variable == InterestVariables.dead:
                                count = df[["is_dead"]].sum()["is_dead"]
                            if variable == InterestVariables.diagnosed:
                                count = df[["is_diagnosed"]].sum()[
                                    "is_diagnosed"]
                            if variable == InterestVariables.ICU:
                                count = df[["is_in_ICU"]].sum()["is_in_ICU"]
                            if variable == InterestVariables.hospital:
                                count = df[["is_hospitalized"]].sum()[
                                    "is_hospitalized"]

                            if count >= policie.mr_start_level:
                                new_activation_status = "enabled"
                            else:
                                new_activation_status = "disabled"

                        if former_activation_status == "enabled":

                            mr_stop_mode = policie.mr_stop_mode

                            if mr_stop_mode == MRTStopModes.level_number:
                                # Find the corresponding count
                                # to assess stop level
                                if variable == InterestVariables.dead:
                                    count = df[["is_dead"]].sum()["is_dead"]
                                if variable == InterestVariables.diagnosed:
                                    count = df[["is_diagnosed"]].sum()[
                                        "is_diagnosed"]
                                if variable == InterestVariables.ICU:
                                    count = df[["is_in_ICU"]].sum()[
                                        "is_in_ICU"]
                                if variable == InterestVariables.hospital:
                                    count = df[["is_hospitalized"]].sum()[
                                        "is_hospitalized"]

                                if count <= policie.mr_stop_level:
                                    new_activation_status = "disabled"
                                else:
                                    new_activation_status = "enabled"

                            if mr_stop_mode == MRTStopModes.length:
                                # Find the step when the policie was enabled
                                df_copy = mrt_policies_df[
                                    ["step", variable.value]
                                    ].copy()

                                df_copy["status_changed"] = df_copy[
                                    variable.value].shift() != df_copy[
                                        variable.value]

                                enabled_start = df_copy[
                                    df_copy["status_changed"]
                                    ]["step"].iloc[-1]

                                # Here "step" is the current step
                                enabled_length = step - enabled_start

                                policie.set_mr_length_in_steps(
                                    iteration_time
                                )
                                mr_length = policie.mr_length_in_steps
                                if enabled_length >= mr_length:
                                    new_activation_status = "disabled"
                                else:
                                    # enabled_length < mr_length
                                    new_activation_status = "enabled"

                        # Append to policies_status dict
                        policies_status[variable.value] = \
                            [new_activation_status]

                        # Append target_groups_lists
                        if new_activation_status == "enabled":
                            target_groups_lists.append(policie.target_groups)

                    # Append policies_status to mrt_policies_df
                    mrt_policies_df = concat(
                        [mrt_policies_df, DataFrame(policies_status)],
                        ignore_index=True
                    )

                    # Flatten list of lists using list comprehension
                    flatten_target_groups_lists = [
                        item
                        for sublist in target_groups_lists
                        for item in sublist
                        ]

                    # Remove duplicates
                    mrt_target_groups = list(set(flatten_target_groups_lists))

                # =============================================================
                # Mobility Restrictions - Cyclic Policies
                # =============================================================

                # Init cmr_target_groups
                cmr_target_groups = []

                cond_1 = global_cyclic_mr is not None
                cond_2 = cyclic_mr_policies is not None

                if cond_1 and cond_2:
                    # Init policies_status dict
                    policies_status = {"step": step}

                    # Init target_groups_lists
                    target_groups_lists = []

                    global_cyclic_mr.set_global_mr_length(
                        iteration_time
                    )

                    if step > grace_time_in_steps:
                        global_activation_satus = \
                            cmr_policies_df["global_mr"].iloc[-1]

                        if global_activation_satus == "disabled":
                            # Verify the status of unrestricted_time_steps
                            if global_cyclic_mr.\
                                    unrestricted_time_steps is not None:
                                pass
                            else:
                                global_cyclic_mr.\
                                    set_unrestricted_time(
                                        iteration_time
                                    )
                            unrestricted_time_steps = \
                                global_cyclic_mr.unrestricted_time_steps

                            #  Calculate the elapsed time disabled
                            cmr_policies_df_copy = cmr_policies_df[
                                ["step", "global_mr"]].copy()

                            cmr_policies_df_copy["status_change"] = \
                                cmr_policies_df_copy["global_mr"].shift() != \
                                cmr_policies_df["global_mr"]

                            disabled_start_step = \
                                cmr_policies_df_copy[cmr_policies_df_copy[
                                    "status_change"]]["step"].iloc[-1]

                            disabled_steps = step - disabled_start_step
                            # Assign the policies_status for global_mr
                            # comparing with the elapsed time
                            policies_status["global_mr"] = \
                                "disabled" if disabled_steps < \
                                unrestricted_time_steps else "enabled"
                            # If enables, assign enabled_steps
                            if policies_status["global_mr"] == "enabled":
                                enabled_steps = 0

                            # In random mode, set unrestricted_time_steps
                            # to None and enabled_steps = 0 when there will be
                            # a change of policies_status to enabled
                            if global_cyclic_mr.unrestricted_time_mode == \
                                    CyclicMRModes.random:
                                if policies_status["global_mr"] == "enabled":
                                    global_cyclic_mr.\
                                        set_none_unrestricted_time()
                                    enabled_steps = 0
                                else:
                                    pass

                        if global_activation_satus == "enabled":
                            # Verify the status of unrestricted_time_steps
                            # Set None for random mode
                            global_mr_length_steps = \
                                global_cyclic_mr.global_mr_length_steps

                            # Calculate the elapsed time enabled
                            cmr_policies_df_copy = cmr_policies_df[
                                ["step", "global_mr"]].copy()

                            cmr_policies_df_copy["status_change"] = \
                                cmr_policies_df_copy["global_mr"].shift() != \
                                cmr_policies_df["global_mr"]

                            enabled_start_step = \
                                cmr_policies_df_copy[cmr_policies_df_copy[
                                    "status_change"]]["step"].iloc[-1]

                            enabled_steps = step - enabled_start_step

                            # Check if continue enabled or set disabled
                            policies_status["global_mr"] = \
                                "enabled" if enabled_steps < \
                                global_mr_length_steps else "disabled"

                            # In random mode, set unrestricted_time_steps
                            # when there will be a change of policies_status
                            # to disabled
                            if global_cyclic_mr.unrestricted_time_mode == \
                                    CyclicMRModes.random:
                                if enabled_steps == global_mr_length_steps:
                                    global_cyclic_mr.\
                                        set_unrestricted_time(
                                            iteration_time
                                        )
                        # Check the status of each group
                        if policies_status["global_mr"] == "enabled":

                            for group in cyclic_mr_policies.keys():
                                # Calling the methods so as to set mr_length
                                # and time_without_restrictions in steps
                                cyclic_mr_policies[group].\
                                    set_mr_length(iteration_time)

                                cyclic_mr_policies[group].\
                                    set_time_without_restrictions(
                                        iteration_time
                                    )

                                delay = cyclic_mr_policies[group].delay
                                mr_length = cyclic_mr_policies[group].\
                                    mr_length_in_steps

                                if delay:
                                    # Assign delay in steps
                                    cyclic_mr_policies[
                                        group
                                        ].set_delay(iteration_time)
                                    delay = cyclic_mr_policies[
                                            group
                                        ].delay_in_steps

                                    # Compare and append to policies_status
                                    # dict
                                    if delay > enabled_steps:
                                        policies_status[group] = "disabled"
                                    else:
                                        # Compare and append to policies_status
                                        # dict
                                        if delay < enabled_steps and \
                                                enabled_steps <= mr_length:
                                            policies_status[group] = "enabled"
                                        else:
                                            policies_status[group] = "disabled"
                                else:
                                    # Append to policies_status dict
                                    policies_status[group] = \
                                        "enabled" if enabled_steps <= \
                                        mr_length else "disabled"
                        else:
                            # Append to policies_status dict diabled for all
                            # groups
                            for col in setdiff1d(
                                cmr_policies_df.columns,
                                "step"
                            ):
                                policies_status[col] = "disabled"

                    elif step == grace_time_in_steps:
                        # Append to policies_status dict
                        policies_status["global_mr"] = "enabled"

                        for group in cyclic_mr_policies.keys():
                            if cyclic_mr_policies[group].delay > 0:
                                # Append to policies_status dict
                                policies_status[group] = "disabled"
                            else:
                                # Append to policies_status dict
                                policies_status[group] = "enabled"
                    else:
                        # Append to policies_status dict
                        for col in setdiff1d(cmr_policies_df.columns, "step"):
                            policies_status[col] = "disabled"

                    # Append policies_status to cmr_policies_df
                    cmr_policies_df = concat(
                        [cmr_policies_df, DataFrame(
                            policies_status, index=[0]
                            )],
                        ignore_index=True
                    )

                    policies_status_copy = policies_status.copy()
                    policies_status_copy.pop("step")
                    policies_status_copy.pop("global_mr")
                    policies_status_copy = zip(
                        policies_status_copy.keys(),
                        policies_status_copy.values()
                    )

                    # Append cmr_target_groups
                    for group, status in policies_status_copy:
                        if status == "enabled":
                            cmr_target_groups.append(group)

                # Create mrc_target_groups list
                mrc_target_groups = \
                    cmr_target_groups + mrt_target_groups

                # Remove duplicates
                mrc_target_groups = list(set(mrc_target_groups))

                df = cls.to_isolate_agents_by_mr(
                    df,
                    mrc_target_groups,
                    beta,
                    mr_adherence_groups,
                    execmode
                )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["agent"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df, mrt_policies_df, cmr_policies_df
