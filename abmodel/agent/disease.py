from typing import Union

from pandas.core.frame import DataFrame

from abmodel.utils.distributions import Distribution
from abmodel.utils.utilities import check_field_errors, check_field_existance
from abmodel.utils.utilities import std_str_join_cols
from abmodel.models.disease import NaturalHistory, DistTitles


class AgentDisease:
    """
        ... TODO
    """
    @classmethod
    def determine_disease_state_max_time(
        cls, df: DataFrame, natural_history: NaturalHistory
    ) -> DataFrame:
        """
            TODO
        """
        def calculate_max_time(row) -> Union[int, float]:
            """
                TODO
            """
            key = std_str_join_cols(
                row["vulnerability_group"],
                row["disease_state"]
                )
            return natural_history.items[key].dist[DistTitles.time].sample()

        try:
            df = df.apply(calculate_max_time, axis=1)
        except Exception:
            validation_list = ["disease_state_max_time", "disease_state",
                               "vulnerability_group"]
            check_field_existance(df, validation_list)
        else:
            return df

    @classmethod
    def disease_state_transition(
        cls, df: DataFrame, dt: float
    ) -> DataFrame:
        """
        """
        def transition_function() -> None:
            """
            """
            return 0

        try:
            df = df.apply(transition_function, axis=1)
        except Exception:
            validation_list = ["disease_state_time"]
            check_field_existance(df, validation_list)
        else:
            return df

    def disease_state_transition(
        self,
        dt: int,
        hospitals: dict,
        hospitals_spatial_tree,
        hospitals_labels
        ):
        """
        """
        self.disease_state_time += dt
        previous_disease_state = self.disease_state

        if (self.disease_state_max_time
        and self.disease_state_time >= self.disease_state_max_time):

            # Verify: becomes into ? ... Throw the dice
            dice = np.random.random_sample()

            cummulative_probability = 0. + self.immunization_level

            for (probability, becomes_into_disease_state) in sorted(
                zip(
                    self.__disease_states_transitions_by_vulnerability_group[
                    self.vulnerability_group][self.disease_state]['transition_probability'],
                    self.__disease_states_transitions_by_vulnerability_group[
                    self.vulnerability_group][self.disease_state]['becomes_into']
                    ),
                # In order to use criticality_level
                # pair = (probability, becomes_into_disease_state)
                key=lambda pair: self.__criticality_level_of_evolution_of_disease_states[pair[1]]
                ):

                cummulative_probability += probability

                if dice <= cummulative_probability:

                    self.update_infection_status(becomes_into_disease_state)

                    self.disease_state = becomes_into_disease_state

                    if becomes_into_disease_state == 'dead':
                        # Agent died by disease
                        self.live_state = 'dead by disease'

                    self.update_diagnosis_state(dt, previous_disease_state)

                    hospitals = self.update_hospitalization_state(
                        dt,
                        hospitals,
                        hospitals_spatial_tree,
                        hospitals_labels
                        )

                    self.disease_state_time = 0

                    self.determine_disease_state_time()

                    break

        else:
            self.update_diagnosis_state(dt, previous_disease_state)

            hospitals = self.update_hospitalization_state(
                dt,
                hospitals,
                hospitals_spatial_tree,
                hospitals_labels
                )

        return hospitals