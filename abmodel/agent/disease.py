from typing import Union
from copy import deepcopy

from numpy import where, full, ndarray
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
        """
        # =====================================================================
        def init_calculate_max_time(
            key,
            natural_history,
            execmode
        ) -> Union[bool, Series]:
            """
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
                    lambda t: t + df if t is not None else None,
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
                    lambda t: t + df if t is not None else None,
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
        cls, df: DataFrame, dt: float, disease_groups: DiseaseStates,
        health_system: HealthSystem,
        execmode: ExecutionModes = ExecutionModes.pandas
    ) -> DataFrame:
        """
            TODO
        """
        # =====================================================================
        def hospitalization_vectorized(
            disease_states_vec,
            is_hospitalized_vec: ndarray,
            health_system
        ):
            """
                # step 1: no is_hospitalized and disease_state has probability to
                # be hospitalized

                # step 2: is_hospitalized ... No matter if disease states changes
                # or not ... Throw dice to see if agent still hospitalized

                # step 3: if one agent cannot be hospitalized, see if it dies
                # because of disease
            """
            # Get former is_hospitalized info
            agents_number = len(is_hospitalized_vec)

            former_is_hospitalized = deepcopy(is_hospitalized_vec)

            former_hospitalized_number = len(
                where(is_hospitalized_vec == False)[0]
                )

            # Verify: is going to be hospitalized? ... Throw the dice
            # Do it for all the agents
            dice = random_sample(agents_number)

            hospitalization_prob = [
                disease_groups
                .items[disease_state]
                .dist[DistTitles.hospitalization.value]
                .sample()
                for disease_state in disease_states_vec
                ]

            # if dice <= hospitalization_prob
            # agent should be hospitalized
            is_hospitalized_vec = where(
                dice <= hospitalization_prob,
                full(len(is_hospitalized_vec, True)),
                full(len(is_hospitalized_vec, False)),
            )

            new_hospitalized_number = len(
                where(is_hospitalized_vec == False)[0]
                )

            if new_hospitalized_number <= health_system.hospital_capacity:
                return is_hospitalized_vec
            else:
                pass

        # =====================================================================
        try:
            if execmode == ExecutionModes.vectorized:
                pass
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

    # def update_immunization_level

    # def disease_state_transition_by_contagion

    # def trace_neighbors

    # def update_alertness_state

    # def quarantine_by_government_decrees

    # def init_columns
