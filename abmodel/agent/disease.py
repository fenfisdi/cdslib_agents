from typing import Union, Optional
from copy import deepcopy

from numpy import where, full, ndarray, isin, concatenate, setdiff1d
from numpy import isnan, nan
from numpy.random import choice, random_sample
from pandas.core.frame import DataFrame
from pandas.core.series import Series

from abmodel.utils.execution_modes import ExecutionModes
from abmodel.utils.utilities import check_field_existance, exception_burner
from abmodel.utils.utilities import std_str_join_cols
from abmodel.models.disease import NaturalHistory, DiseaseStates
from abmodel.models.disease import IsolationAdherenceGroups, DistTitles
from abmodel.models.health_system import HealthSystem


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
    do_calculate_max_time: bool,
    disease_state_time: Union[float, None],
    disease_state_max_time: Union[float, None],
    natural_history: NaturalHistory
) -> tuple[float, float]:
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
        return Series([0,
                       natural_history.items[key].dist[DistTitles.time.value]
                       .sample()
                       ])
    else:
        return Series([disease_state_time, disease_state_max_time])


# TODO
# Reimplement this function in order to also return disease_state_time
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
    key: str,
    natural_history: NaturalHistory
) -> tuple[str, float, bool]:
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
    # disease state max time. It is going to be changed to True
    # if disease state changes
    do_calculate_max_time = False

    # Get the transitions info for the current
    # key (vulnerability_group, current disease_state)
    transitions = natural_history.items[key].transitions

    # Get disease_states enabled for the probable transition and
    # their corresponding probabilities
    disease_states = transitions.keys()
    probabilities = [
        transitions[transition].probability
        for transition in disease_states
        ]

    if not isnan(disease_state_max_time):
        if disease_state_time >= disease_state_max_time:
            # disease state must change
            # Verify: becomes into? ... Throw the dice
            disease_state = choice(
                disease_states,
                p=probabilities
                )

            # Set the time elapsed since it changed disease state
            # in zero
            # TODO: Remove this comment. This statement has been moved to the
            # functions:
            # calculate_max_time_iterative/calculate_max_time_vectorized
            #
            # disease_state_time = 0

            # Set True the flag that forces to calculate
            # disease state max time
            do_calculate_max_time = True

    return Series([disease_state, disease_state_time, do_calculate_max_time])


# =============================================================================
def diagnosis_function(
    disease_state: str,
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
# TODO
# Calculate isolation_max_time from isolation_days
# i.e. change units
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
    isolation_days = disease_groups \
        .items[disease_state] \
        .dist[DistTitles.isolation_days.value] \
        .sample()

    # TODO
    # Calculate isolation_max_time from isolation_days
    # i.e. change units
    isolation_max_time = isolation_days

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
    disease_groups: DiseaseStates,
    isolation_adherence_groups: Optional[IsolationAdherenceGroups] = None
) -> tuple[bool, bool, float, float, bool]:
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
                isolation_time = None
                isolation_max_time = None
                is_isolated = False
                is_diagnosed = False
            else:
                # isolation has not finished yet
                # do nothing
                pass
        else:
            # it is not isolated
            if isolation_adherence_groups is None:
                # Agent always adheres to isolation
                adheres_to_isolation = True

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
                   isolation_max_time, adheres_to_isolation])


# =============================================================================
# TODO: ADD is_dead
# TODO
# Should we change positions for hospitalized agents?
def hospitalization_vectorized(
    is_hospitalized: ndarray,
    is_in_ICU: ndarray,
    disease_states: ndarray,
    is_dead: ndarray,
    dead_disease_group: str,
    disease_groups: DiseaseStates,
    health_system: HealthSystem
) -> tuple[bool, bool, ndarray]:
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

    ICU_prob = [
        disease_groups
        .items[disease_state]
        .dist[DistTitles.icu_prob.value]
        .sample()
        for disease_state in disease_states
        ]

    # if dice <= ICU_prob
    # agent should be in ICU
    is_in_ICU = where(
        dice <= ICU_prob,
        full(agents_number, True),
        full(agents_number, False)
        )

    new_in_ICU_number = len(
        where(is_in_ICU == False)[0]
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
        # vacancy includes ICU vancacy, but the contrary doesn't hold.
        # This is simulated enabling that those in ICU are also
        # hospitalized

        completely_new_in_ICU = where(
            (is_in_ICU == True) & (former_is_in_ICU == False)
            )[0]

        must_die_number = new_in_ICU_number \
            - health_system.ICU_capacity

        # Update new_in_ICU_number
        new_in_ICU_number = health_system.ICU_capacity

        must_die = choice(
            completely_new_in_ICU,
            sice=must_die_number,
            replace=False
            )

        # Update disease state of those that died
        disease_states[must_die] = dead_disease_group
        # TODO: ADD is_dead

        is_in_ICU_False = where(is_in_ICU == False)[0]
        is_in_ICU_True = where(is_in_ICU == True)[0]

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

    hospitalization_prob = [
        disease_groups
        .items[disease_state]
        .dist[DistTitles.hospitalization.value]
        .sample()
        for disease_state in disease_states
        ]

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
        (is_hospitalized == False) & (is_in_ICU == True),
        full(agents_number, True),
        is_hospitalized
        )

    new_hospitalized_number = len(
        where(is_hospitalized == False)[0]
        )

    if new_hospitalized_number > health_system.hospital_capacity:
        # Health system got overloaded in hospital vacancy
        # Some agents are susceptible to die
        # 1. ICU has higher priority. Those agents that are in ICU,
        # should remain in ICU
        # 2. New hospitalized agents, that are not in ICU, must throw
        # the dice to see who dies or who survives.
        completely_new_hospitalized_not_in_ICU = where(
            (is_hospitalized == True) & (is_in_ICU == False)
            & (former_is_hospitalized == False)
            )[0]

        susceptible_to_die_number = len(
            completely_new_hospitalized_not_in_ICU
            )

        must_die_number = new_hospitalized_number \
            - health_system.hospital_capacity

        if must_die_number < susceptible_to_die_number:
            must_die = choice(
                completely_new_hospitalized_not_in_ICU,
                sice=must_die_number,
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
                (is_hospitalized == True) & (is_in_ICU == False)
                & (former_is_hospitalized == True)
                )[0]

            must_die_surplus = choice(
                remain_hospitalized_but_not_in_ICU,
                sice=must_die_number_surplus,
                replace=False
                )

            must_die = concatenate([
                must_die_surplus,
                completely_new_hospitalized_not_in_ICU
            ])

            # Update disease state of those that died
            disease_states[must_die] = dead_disease_group
            # TODO: ADD is_dead

            is_hospitalized_False = where(is_hospitalized == False)[0]
            is_hospitalized_True = where(is_hospitalized == True)[0]

            new_is_hospitalized_False = concatenate([
                is_hospitalized_False, must_die
                ])
            mask = isin(is_hospitalized_True, must_die, invert=True)
            new_is_hospitalized_True = is_hospitalized_True[mask]

            # Update values
            is_hospitalized[new_is_hospitalized_False] = False
            is_hospitalized[new_is_hospitalized_True] = True

    # TODO
    # Should we change positions for hospitalized agents?

    return is_hospitalized, is_in_ICU, disease_states


# =============================================================================
# TODO
# Add susceptibility_dist
def contagion_function(
    step: int,
    agent: int,
    x: float,
    y: float,
    immunization_level: float,
    key: str,
    disease_state: str,
    times_infected: int,
    infected_info: dict,
    disease_state_time: float,
    natural_history: NaturalHistory,
    disease_groups: DiseaseStates,
    kdtree_by_disease_state: dict,
    agents_labels_by_disease_state: dict
) -> tuple[str, int, dict, float, bool]:
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
    # disease state max time. It is going to be changed to True
    # if disease state changes
    do_calculate_max_time = False

    # Get transition_by_contagion boolean
    transition_by_contagion = \
        natural_history.items[key].transition_by_contagion

    if transition_by_contagion:
        # Get the transitions info for the current
        # key (vulnerability_group, current disease_state)
        transitions = natural_history.items[key].transitions

        # Get disease_states enabled for the probable transition
        # after contagion and and their corresponding probabilities
        disease_states = transitions.keys()
        probabilities = [
            transitions[transition].probability
            for transition in disease_states
            ]

        # Agent location
        agent_location = [x, y]

        # List to save who infected the agent
        infected_by = []

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
                joint_probability = \
                    (1.0 - immunization_level) \
                    * 1.0  \
                    * disease_groups.items[spreader_state] \
                    .spread_probability  # TODO: Add susceptibility_dist

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

            infected_info[step] = infected_by

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
    else:
        # transition_by_contagion == False
        pass

    return (disease_state, times_infected, infected_info,
            disease_state_time, do_calculate_max_time)


# =============================================================================
# TODO
# Should immunization_max_time start as None?
def calculate_immunization_params_iterative(
    key: str,
    disease_state: str,
    immunization_level: float,
    immunization_level_start: float,
    immunization_max_time: float,
    do_update_immunization_params: bool,
    natural_history: NaturalHistory
) -> tuple[float, float]:
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
        # Get the transitions info for the current
        # key (vulnerability_group, current disease_state)
        transitions = natural_history.items[key].transitions

        # Calculate immunization_max_time
        immunization_max_time = transitions[disease_state] \
            .dist[DistTitles.immunization_time.value] \
            .sample()

        # Calculate immunization_level_start
        gain = transitions[disease_state] \
            .immunization_gain

        immunization_level_start = immunization_level + gain

        # TODO
        # Should immunization_max_time start as None?

    return (immunization_level_start, immunization_max_time)


# =============================================================================
# TODO
def immunization_function(
    immunization_time: float,
    immunization_level_start: float,
    immunization_max_time: float
) -> float:
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
    return None


def calculate_immunization_level_iterative(
    immunization_level: float,
    immunization_time: float,
    immunization_level_start: float,
    immunization_max_time: float
) -> float:
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
        immunization_level = immunization_function(
            immunization_time,
            immunization_level_start,
            immunization_max_time
        )
    else:
        # immunization_time >= immunization_max_time
        pass
    return immunization_level


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
        disease_groups: DiseaseStates,
        natural_history: NaturalHistory,
        isolation_adherence_groups: Optional[IsolationAdherenceGroups] = None,
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
            TODO

            Examples
            --------
            TODO: include some examples
        """
        # Initialize is_dead
        df = cls.init_is_dead(df, disease_groups, execmode)

        # Generate key column
        df = cls.generate_key_col(df, execmode)

        # Init disease_state_max_time
        df = cls.init_disease_state_max_time(df, natural_history, execmode)

        # Init is_diagnosed
        df = df.assign(is_diagnosed=False)
        df = cls.to_diagnose_agents(df, disease_groups, execmode)

        # Init is_isolated
        df = df.assign(is_isolated=False)
        df = df.assign(isolation_time=nan)
        df = df.assign(isolation_max_time=nan)
        df = df.assign(adheres_to_isolation=True)
        dt = 0.0  # Set dt to zero
        df = cls.to_isolate_agents(
            df, dt, disease_groups, isolation_adherence_groups, execmode
            )

        return df

    @classmethod
    def init_is_dead(
        cls,
        df: DataFrame,
        disease_groups: DiseaseStates,
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
    def generate_key_col(
        cls,
        df: DataFrame,
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
                        row["vulnerability_group"],
                        row["disease_state"]
                        ),
                    axis=1
                    )
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
                df, natural_history, execmode
            )
            return df

    # TODO
    # Reimplement calculate_max_time_vectorized
    @classmethod
    def determine_disease_state_max_time(
        cls,
        df: DataFrame,
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
                        row["do_calculate_max_time"],
                        row["disease_state_time"],
                        row["disease_state_max_time"],
                        natural_history
                        ),
                    axis=1
                    )
            # TODO
            # Reimplement calculate_max_time_vectorized
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
        dt: float,
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

                df[["disease_state", "disease_state_time",
                    "do_calculate_max_time"]] = df.apply(
                    lambda row: transition_function(
                        row["disease_state"],
                        row["disease_state_time"],
                        row["disease_state_max_time"],
                        row["key"],
                        natural_history
                        ),
                    axis=1
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )

            # Call determine_disease_state_max_time function in order
            # to calculate it for those agents who went through a transition
            df = cls.determine_disease_state_max_time(
                df, natural_history, execmode
            )

        except Exception as error:
            validation_list = ["disease_state", "disease_state_time", "key",
                               "disease_state_max_time"]
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
                        row["is_diagnosed"],
                        disease_groups
                        ),
                    axis=1
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["disease_state", "is_diagnosed"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df

    # TODO
    # Should we change positions for an isolated agent?
    @classmethod
    def to_isolate_agents(
        cls,
        df: DataFrame,
        dt: float,
        disease_groups: DiseaseStates,
        isolation_adherence_groups: Optional[IsolationAdherenceGroups] = None,
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

            isolation_handler : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            # TODO
            # Should we change positions for an isolated agent?

            if execmode == ExecutionModes.iterative.value:
                # Update isolation time
                df["isolation_time"] = df["isolation_time"] + dt

                df[["is_diagnosed", "is_isolated", "isolation_time",
                   "isolation_max_time", "adheres_to_isolation"]] = df.apply(
                    lambda row: isolation_handler(
                        row["disease_state"],
                        row["isolation_adherence_group"],
                        row["is_diagnosed"],
                        row["is_isolated"],
                        row["isolation_time"],
                        row["isolation_max_time"],
                        row["adheres_to_isolation"],
                        disease_groups,
                        isolation_adherence_groups
                        ),
                    axis=1
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["disease_state", "isolation_adherence_group",
                               "is_isolated", "is_diagnosed", "isolation_time",
                               "isolation_max_time", "adheres_to_isolation"]
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
                   "disease_states", "is_dead"]] = hospitalization_vectorized(
                    df["is_hospitalized"],
                    df["is_in_ICU"],
                    df["disease_states"],
                    df["is_dead"],
                    dead_disease_group,
                    disease_groups,
                    health_system
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["disease_state", "is_in_ICU", "disease_states",
                               "is_dead"]
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

            contagion_function : TODO complete explanation

            determine_disease_state_max_time : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df[["disease_state", "times_infected", "infected_info",
                    "disease_state_time", "do_calculate_max_time"]] = df.apply(
                    lambda row: contagion_function(
                        row["step"],
                        row["agent"],
                        row["x"],
                        row["y"],
                        row["immunization_level"],
                        row["key"],
                        row["disease_state"],
                        row["times_infected"],
                        row["infected_info"],
                        row["disease_state_time"],
                        natural_history,
                        disease_groups,
                        kdtree_by_disease_state,
                        agents_labels_by_disease_state
                        ),
                    axis=1
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )

            # Call determine_disease_state_max_time function in order
            # to calculate it for those agents who went through a transition
            df = cls.determine_disease_state_max_time(
                df, natural_history, execmode
            )
        except Exception as error:
            validation_list = ["step", "agent", "x", "y", "immunization_level",
                               "key", "disease_state", "times_infected",
                               "infected_info", "disease_state_time"]
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

            calculate_immunization_params_iterative : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df[["immunization_level_start",
                    "immunization_max_time"]] = df.apply(
                    lambda row: calculate_immunization_params_iterative(
                        row["key"],
                        row["disease_state"],
                        row["immunization_level"],
                        row["immunization_level_start"],
                        row["immunization_max_time"],
                        row["do_update_immunization_params"],
                        natural_history
                        ),
                    axis=1
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["key", "immunization_level",
                               "immunization_level_start",
                               "immunization_max_time",
                               "do_update_immunization_params"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            # Restart do_calculate_max_time
            df = df.assign(do_update_immunization_params=False)

            return df

    @classmethod
    def update_immunization_level(
        cls,
        df: DataFrame,
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

            calculate_immunization_level_iterative : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.iterative.value:
                df["immunization_level"] = df.apply(
                    lambda row: calculate_immunization_level_iterative(
                        row["key"],
                        row["do_update_immunization_constant"],
                        row["immunization_level"],
                        natural_history
                        ),
                    axis=1
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["disease_state_max_time", "key",
                               "do_update_immunization_level"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            # Remove unnecessary column
            df.drop(columns=["do_update_immunization_level"], inplace=True)

            return df

    # def update_alertness_state

    # def quarantine_by_government_decrees

    # def init_columns
