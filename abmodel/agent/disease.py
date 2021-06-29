from pandas.core.frame import DataFrame, Series

from abmodel.utils.distributions import Distribution
from abmodel.utils.utilities import check_field_errors, check_field_existance





class AgentDisease:
    """
        ... TODO
    """
    def __init__(
        self,
        vulnerability_groups
        disease_states
        natural_history_params: dict,
    ):
        """
            ...TODO

            Parameters
            ----------
            natural_history_params : dict
                Dictionary with the disease natural history
                parameters

        """
        self.vulnerability_groups = 
        self.disease_states =

        {vulnerability_group: {disease_state: 0 for disease_state in disease_states} for vulnerability_group in vulnerability_groups}

        self.disease_state_time_distributions =
        

    @classmethod
    def determine_disease_state_time(
        cls, df: DataFrame
        ) -> DataFrame:
        """
        """
        if self.__disease_states_time_functions[
            self.vulnerability_group][self.disease_state]['time_function']:

            self.disease_state_max_time = \
                self.__disease_states_time_functions[
                self.vulnerability_group][self.disease_state]['time_function']()

        else:
            self.disease_state_max_time = None

    @classmethod
    def disease_state_transition(
        cls, df: DataFrame, dt: float
    ) -> DataFrame:
    """
    """
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