from typing import Union

from numpy.random import choice
from pandas.core.frame import DataFrame
from pandas.core.series import Series

from abmodel.utils.utilities import check_field_existance
from abmodel.utils.utilities import std_str_join_cols
from abmodel.models.disease import NaturalHistory, DiseaseStates, DistTitles
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
    def determine_disease_state_max_time(
        cls, df: DataFrame, natural_history: NaturalHistory,
        execmode: ExecutionModes = ExecutionModes.pandas
    ) -> DataFrame:
        """
            TODO
        """
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
                    return natural_history.items[key].dist[DistTitles.time] \
                        .sample()
                else:
                    return disease_state_max_time

            if execmode == ExecutionModes.vectorized:
                return list(map(
                    lambda single_key, cond, time_value: natural_history
                    .items[single_key]
                    .dist[DistTitles.time]
                    .sample() if cond else time_value,
                    zip(key, do_calculate_max_time, disease_state_max_time)
                ))

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
        def transition_function(
            disease_state_time,
            disease_state_max_time,
            key,
            natural_history,
            execmode
        ) -> str:
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
                        # Verify: becomes into ? ... Throw the dice
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

        try:
            # Update disease state time
            df["disease_state_time"] = list(map(
                lambda t: t + df if t is not None else None,
                df["disease_state_time"]
            ))

            if execmode == ExecutionModes.pandas:
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
    def to_diagnose(
        cls, df: DataFrame, disease_states: DiseaseStates,
        execmode: ExecutionModes = ExecutionModes.pandas
    ) -> DataFrame:
        """
            TODO
        """
        pass

    # def update_hospitalization_state

    # def update_immunization_level

    # def disease_state_transition_by_contagion

    # def trace_neighbors

    # def update_alertness_state

    # def quarantine_by_diagnosis

    # def quarantine_by_government_decrees

    # def init_columns

    # def init_do_calculate_max_time
