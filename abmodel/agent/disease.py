from typing import Union
from copy import deepcopy

from numpy import where, full, ndarray, isin, concatenate, setdiff1d
from numpy.random import choice, random_sample
from pandas.core.frame import DataFrame
from pandas.core.series import Series

from abmodel.utils.utilities import check_field_existance
from abmodel.utils.utilities import std_str_join_cols
from abmodel.models.disease import NaturalHistory, DiseaseStates
from abmodel.models.disease import IsolationAdherenceGroups, DistTitles
from abmodel.models.health_system import HealthSystem
from abmodel.agent.execution_modes import ExecutionModes


class AgentDisease:
    """
        ... TODO
    """
    @classmethod
    def generate_key_col(
        cls, df: DataFrame,
        execmode: ExecutionModes = ExecutionModes.pandas
    ) -> DataFrame:
        """
            TODO
        """
        try:
            if execmode == ExecutionModes.pandas:
                df["key"] = df.apply(
                    lambda row: std_str_join_cols(
                        row["vulnerability_group"],
                        row["disease_state"]
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.vectorized:
                df["key"] = std_str_join_cols(
                    df["vulnerability_group"],
                    df["disease_state"]
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception:
            validation_list = ["disease_state", "vulnerability_group"]
            check_field_existance(df, validation_list)
        else:
            return df

    @classmethod
    def init_disease_state_max_time(
        cls, df: DataFrame, natural_history: NaturalHistory,
        execmode: ExecutionModes = ExecutionModes.pandas
    ) -> DataFrame:
        """
            TODO
        """
        # =====================================================================
        def init_calculate_max_time(
            key,
            natural_history,
            execmode
        ) -> Union[bool, Series]:
            """
                TODO
            """
            if execmode == ExecutionModes.pandas:
                dist_type = natural_history.items[key] \
                    .dist[DistTitles.time.value].dist_type
                return False if dist_type is None else True

            if execmode == ExecutionModes.vectorized:
                return list(map(
                    lambda single_key: False if natural_history
                    .items[single_key]
                    .dist[DistTitles.time.value].dist_type is None else True,
                    key
                ))

        # =====================================================================
        try:
            if execmode == ExecutionModes.pandas:
                df["do_calculate_max_time"] = df.apply(
                    lambda row: init_calculate_max_time(
                        row["key"],
                        natural_history,
                        execmode
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.vectorized:
                df["do_calculate_max_time"] = init_calculate_max_time(
                    df["key"],
                    natural_history,
                    execmode
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception:
            validation_list = ["key", "do_calculate_max_time"]
            check_field_existance(df, validation_list)
        else:
            # Call determine_disease_state_max_time function in order
            # to calculate it for those agents who are infected
            df = cls.determine_disease_state_max_time(
                df, natural_history, execmode
            )
            return df

    @classmethod
    def determine_disease_state_max_time(
        cls, df: DataFrame, natural_history: NaturalHistory,
        execmode: ExecutionModes = ExecutionModes.pandas
    ) -> DataFrame:
        """
            TODO
        """
        # =====================================================================
        def calculate_max_time(
            key,
            do_calculate_max_time,
            disease_state_max_time,
            natural_history,
            execmode
        ) -> Union[float, Series]:
            """
                TODO
            """
            if execmode == ExecutionModes.pandas:
                if do_calculate_max_time:
                    return natural_history.items[key] \
                        .dist[DistTitles.time.value] \
                        .sample()
                else:
                    return disease_state_max_time

            if execmode == ExecutionModes.vectorized:
                return list(map(
                    lambda single_key, cond, time_value: natural_history
                    .items[single_key]
                    .dist[DistTitles.time.value]
                    .sample() if cond else time_value,
                    zip(key, do_calculate_max_time, disease_state_max_time)
                ))

        # =====================================================================
        try:
            if execmode == ExecutionModes.pandas:
                df["disease_state_max_time"] = df.apply(
                    lambda row: calculate_max_time(
                        row["key"],
                        row["do_calculate_max_time"],
                        row["disease_state_max_time"],
                        natural_history,
                        execmode
                        ),
                    axis=1
                    )
            elif execmode == ExecutionModes.vectorized:
                df["disease_state_max_time"] = calculate_max_time(
                    df["key"],
                    df["do_calculate_max_time"],
                    df["disease_state_max_time"],
                    natural_history,
                    execmode
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception:
            validation_list = ["disease_state_max_time", "key",
                               "do_calculate_max_time"]
            check_field_existance(df, validation_list)
        else:
            return df

    @classmethod
    def disease_state_transition(
        cls, df: DataFrame, dt: float, natural_history: NaturalHistory,
        execmode: ExecutionModes = ExecutionModes.pandas
    ) -> DataFrame:
        """
            TODO
        """
        # =====================================================================
        def transition_function(
            disease_state_time,
            disease_state_max_time,
            key,
            natural_history,
            execmode
        ) -> tuple[
            Union[str, Series],
            Union[float, Series],
            Union[bool, Series]
        ]:
            """
                TODO
            """
            if execmode == ExecutionModes.pandas:
                # Set False the flag that forces to calculate
                # disease state max time. It is going to be change to True
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

                if disease_state_max_time is not None:
                    if disease_state_time >= disease_state_max_time:
                        # disease state must change
                        # Verify: becomes into? ... Throw the dice
                        disease_state = choice(
                            disease_states,
                            p=probabilities
                            )

                        # Set the time elapsed since it changed disease state
                        # in zero
                        disease_state_time = 0

                        # Set True the flag that forces to calculate
                        # disease state max time
                        do_calculate_max_time = True

                return disease_state, disease_state_time, do_calculate_max_time

        # =====================================================================
        try:
            if execmode == ExecutionModes.pandas:
                # Update disease state time
                df["disease_state_time"] = list(map(
                    lambda t: t + dt if t is not None else None,
                    df["disease_state_time"]
                ))

                df[["disease_state", "disease_state_time",
                    "do_calculate_max_time"]] = df.apply(
                    lambda row: transition_function(
                        row["disease_state_time"],
                        row["disease_state_max_time"],
                        row["key"],
                        natural_history,
                        execmode
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

        except Exception:
            validation_list = ["disease_state", "disease_state_time", "key"
                               "disease_state_max_time",
                               "do_calculate_max_time"]
            check_field_existance(df, validation_list)
        else:
            return df

    @classmethod
    def to_diagnose_agents(
        cls, df: DataFrame, disease_groups: DiseaseStates,
        execmode: ExecutionModes = ExecutionModes.pandas
    ) -> DataFrame:
        """
            TODO
        """
        # =====================================================================
        def diagnosis_function(
            disease_state,
            is_diagnosed,
            disease_groups,
            execmode
        ):
            """
                TODO
            """
            if execmode == ExecutionModes.pandas:
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

        # =====================================================================
        try:
            if execmode == ExecutionModes.pandas:
                df["is_diagnosed"] = df.apply(
                    lambda row: diagnosis_function(
                        row["disease_state"],
                        row["is_diagnosed"],
                        disease_groups,
                        execmode
                        ),
                    axis=1
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception:
            validation_list = ["disease_state", "is_diagnosed"]
            check_field_existance(df, validation_list)
        else:
            return df

    @classmethod
    def to_isolate_agents(
        cls, df: DataFrame, dt: float, disease_groups: DiseaseStates,
        isolation_adherence_groups: Union[
            IsolationAdherenceGroups, None] = None,
        execmode: ExecutionModes = ExecutionModes.pandas
    ) -> DataFrame:
        """
            TODO
        """
        # =====================================================================
        def isolation_function(
            disease_state,
            disease_groups,
            execmode
        ):
            """
                TODO
            """
            if execmode == ExecutionModes.pandas:
                # How much time is going to be isolated?
                # ... Throw the dice
                isolation_days = disease_groups \
                    .items[disease_state] \
                    .dist[DistTitles.isolation_days.value] \
                    .sample()

                # TODO
                # isolation_days --> isolation_time
                isolation_max_time = isolation_days

                isolation_time = 0.0
                is_isolated = True

            return is_isolated, isolation_time, isolation_max_time

        # =====================================================================
        def isolation_handler(
            disease_state,
            isolation_adherence_group,
            is_diagnosed,
            is_isolated,
            isolation_time,
            isolation_max_time,
            disease_groups,
            isolation_adherence_groups,
            execmode
        ):
            """
                TODO
            """
            if execmode == ExecutionModes.pandas:
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
                            (is_isolated, isolation_time,
                             isolation_max_time) = isolation_function(
                                disease_state,
                                disease_groups,
                                execmode
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
                                # Agent adheres to be isolated
                                (is_isolated, isolation_time,
                                 isolation_max_time) = isolation_function(
                                    disease_state,
                                    disease_groups,
                                    execmode
                                )
                            else:
                                # Agent doesn't adhere to be isolated
                                # do nothing
                                pass

                return (is_diagnosed, is_isolated, isolation_time,
                        isolation_max_time)

        # =====================================================================
        try:
            # TODO
            # Should we change positions for an isolated agent?

            if execmode == ExecutionModes.pandas:
                # Update isolation time
                df["isolation_time"] = list(map(
                    lambda t: t + dt if t is not None else None,
                    df["isolation_time"]
                ))

                df[["is_diagnosed", "is_isolated", "isolation_time",
                   "isolation_max_time"]] = df.apply(
                    lambda row: isolation_handler(
                        row["disease_state"],
                        row["isolation_adherence_group"],
                        row["is_diagnosed"],
                        row["is_isolated"],
                        row["isolation_time"],
                        row["isolation_max_time"],
                        disease_groups,
                        isolation_adherence_groups,
                        execmode
                        ),
                    axis=1
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception:
            validation_list = ["disease_state", "isolation_adherence_group",
                               "is_isolated", "is_diagnosed", "isolation_time",
                               "isolation_max_time"]
            check_field_existance(df, validation_list)
        else:
            return df

    @classmethod
    def to_hospitalize_agents(
        cls, df: DataFrame, dead_disease_group: str,
        disease_groups: DiseaseStates, health_system: HealthSystem,
        execmode: ExecutionModes = ExecutionModes.vectorized
    ) -> DataFrame:
        """
            TODO
        """
        # =====================================================================
        def hospitalization_vectorized(
            is_hospitalized: ndarray,
            is_in_ICU: ndarray,
            disease_states: ndarray,
            is_dead: ndarray,
            dead_disease_group: str,
            disease_groups: DiseaseStates,
            health_system: HealthSystem
        ):
            """
                TODO
                # step 1: no is_hospitalized and disease_state has probability
                # to be hospitalized

                # step 2: is_hospitalized ... No matter if disease states
                # changes or not ... Throw dice to see if agent still
                # hospitalized

                # step 3: if one agent cannot be hospitalized, see if it dies
                # because of disease
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

        # =====================================================================
        try:
            if execmode == ExecutionModes.vectorized:
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
        except Exception:
            validation_list = ["disease_state", "is_in_ICU", "disease_states",
                               "is_dead"]
            check_field_existance(df, validation_list)
        else:
            return df

    @classmethod
    def disease_state_transition_by_contagion(
        cls, df: DataFrame, dt: float, natural_history: NaturalHistory, step: int,
        disease_states: DiseaseStates,
        execmode: ExecutionModes = ExecutionModes.pandas
    ) -> DataFrame:
        """
            TODO
        """
        def transition_function(
            key,
            natural_history,
            execmode,
            spatial_trees_by_disease_state,
            agents_indices_by_disease_state
        ) -> tuple[
            Union[str, Series],
            Union[float, Series],
            Union[bool, Series]:
        ]:
            """
                TODO
            """
            if execmode == ExecutionModes.pandas:
                # Set False the flag that forces to calculate
                # disease state max time. It is going to be change to True
                # if disease state changes
                do_calculate_max_time = False
    
           
            if disease_states.labels['can_get_infected']:
                """
                    # Retrieve agent location
                    # List to save who infected the agent
                    TODO
                """
                agent_location=[]
                infected_by = []

                for disease_state in disease_states.labels:

                    if (disease_state['can_spread'] 
                    and spatial_trees_by_disease_state[disease_state]):

                        points_inside_radius = \
                        spatial_trees_by_disease_state[disease_state].query_ball_point(
                            agent_location, disease_state['spread_radius']
                            )

                        spreaders_indices_inside_radius = \
                            agents_indices_by_disease_state[
                                disease_state][points_inside_radius]   

                        # If self.agent in spreaders_indices_inside_radius,
                        # then remove it
                        if cls.agent in spreaders_indices_inside_radius:
                            
                            spreaders_indices_inside_radius = setdiff1d(
                            spreaders_indices_inside_radius,
                            cls.agent
                            )
                        joint_probability = \
                        (1.0 - cls.immunization_level) \
                        * cls.contagion_probabilities_by_susceptibility_groups[
                            cls.susceptibility_group] \
                        * disease_states['spread_probability']

                        for spreader_agent_index in spreaders_indices_inside_radius:

                            dice = random_sample()

                            if dice <= joint_probability:
                                # Got infected !!!
                                # Save who infected the agent
                                infected_by.append(spreader_agent_index)

                    if len(infected_by) is not 0:

                        infected_by = infected_by
                        infected_in_step = step
                        cls.infected_info[step] = infected_by

                        dice = random_sample()

                        cummulative_probability = 0. + cls.immunization_level

                    if (disease_state['can_spread'] 
                    and spatial_trees_by_disease_state[disease_state]):

                        points_inside_radius = \
                        spatial_trees_by_disease_state[disease_state].query_ball_point(
                            agent_location, disease_state['spread_radius']
                            )

                        spreaders_indices_inside_radius = \
                            agents_indices_by_disease_state[
                                disease_state][points_inside_radius]   

                        # If self.agent in spreaders_indices_inside_radius,
                        # then remove it
                        if cls.agent in spreaders_indices_inside_radius:
                            
                            spreaders_indices_inside_radius = setdiff1d(
                            spreaders_indices_inside_radius,
                            cls.agent
                            )
                        joint_probability = \
                        (1.0 - cls.immunization_level) \
                        * cls.contagion_probabilities_by_susceptibility_groups[
                            cls.susceptibility_group] \
                        * disease_states['spread_probability']

                        for spreader_agent_index in spreaders_indices_inside_radius:

                            dice = random_sample()

                            if dice <= joint_probability:
                                # Got infected !!!
                                # Save who infected the agent
                                infected_by.append(spreader_agent_index)

                    if len(infected_by) is not 0:

                        infected_by = infected_by
                        infected_in_step = step
                        cls.infected_info[step] = infected_by

                        dice = random_sample()

                        cummulative_probability = 0. + cls.immunization_level

    # def update_alertness_state

    # def update_immunization_level

    # def quarantine_by_government_decrees

    # def init_columns
