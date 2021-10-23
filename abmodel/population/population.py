from typing import Optional

from numpy import array, nan_to_num, inf, maximum, floor, setdiff1d
from scipy.spatial import KDTree
from pandas.core.frame import DataFrame

from abmodel.utils.execution_modes import ExecutionModes
from abmodel.models.population import Configutarion
from abmodel.models.health_system import HealthSystem
from abmodel.models.base import SimpleGroups
from abmodel.models.disease import SusceptibilityGroups, MobilityGroups
from abmodel.models.disease import NaturalHistory, DiseaseStates
from abmodel.models.disease import IsolationAdherenceGroups
from abmodel.population.initial_arrangement import InitialArrangement
from abmodel.models.mobility_restrictions import MRTracingPolicies
from abmodel.models.mobility_restrictions import GlobalCyclicMR
from abmodel.models.mobility_restrictions import CyclicMRPolicies


class Population:
    """
        TODO: Add brief explanation

        Methods
        -------
        TODO
    """
    def __init__(
        self,
        configuration: Configutarion,
        health_system: HealthSystem,
        age_groups: SimpleGroups,
        vulnerability_groups: SimpleGroups,
        mr_groups: SimpleGroups,
        susceptibility_groups: SusceptibilityGroups,
        mobility_groups: MobilityGroups,
        disease_groups: DiseaseStates,
        natural_history: NaturalHistory,
        initial_population_setup_list: list[dict],
        mrt_policies: Optional[MRTracingPolicies] = None,
        global_cyclic_mr: Optional[GlobalCyclicMR] = None,
        cyclic_mr_policies: Optional[CyclicMRPolicies] = None,
        isolation_adherence_groups: Optional[IsolationAdherenceGroups] = None,
        execmode: ExecutionModes = ExecutionModes.iterative
    ) -> None:
        """
            Constructor of Population class.

            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            See Also
            --------
            get_disease_groups_alive : TODO complete explanation

            choose_tracing_radius : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        # Store configuration
        self.configuration = configuration
        self.health_system = health_system
        self.age_groups = age_groups
        self.vulnerability_groups = vulnerability_groups
        self.mr_groups = mr_groups
        self.susceptibility_groups = susceptibility_groups
        self.mobility_groups = mobility_groups
        self.disease_groups = disease_groups
        self.natural_history = natural_history
        self.isolation_adherence_groups = isolation_adherence_groups
        self.mrt_policies = mrt_policies
        self.global_cyclic_mr = global_cyclic_mr
        self.cyclic_mr_policies = cyclic_mr_policies
        self.execmode = execmode

        # TODO
        # Handle units

        # Setup internal variables
        self.get_disease_groups_alive()
        self.choose_tracing_radius()

        # Init population dataframe
        self.df = DataFrame({
            "agent": list(range(self.configuration.population_number))
        })

        for initial_population_setup in initial_population_setup_list:
            self.df = InitialArrangement.setup(
                self.df,
                **initial_population_setup,
                )

        print(self.df)

    def get_disease_groups_alive(self) -> None:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            See Also
            --------
            TODO

            Examples
            --------
            TODO: include some examples
        """
        # Retrieve disease group label which corresponds to those dead
        for disease_group_label in self.disease_groups.items.keys():
            if self.disease_groups.items[disease_group_label].is_dead:
                self.dead_disease_group = disease_group_label

        # Also exclude those dead from disease groups alive
        self.disease_groups_alive = list(setdiff1d(
            list(self.disease_groups.items.keys()),
            [self.dead_disease_group]
            ))

    def choose_tracing_radius(self) -> None:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            See Also
            --------
            TODO

            Examples
            --------
            TODO: include some examples
        """
        # Retrieve maximum radius for trace_neighbors function
        spread_radius_list = [
            self.disease_groups.items[disease_group].spread_radius
            for disease_group in self.disease_groups.items.keys()
            ]

        avoidance_radius_list = [
            self.natural_history.items[key].avoidance_radius
            for key in self.natural_history.items.keys()
            ]

        spread_radius_arr = array(spread_radius_list, dtype=float)
        spread_radius_arr = nan_to_num(spread_radius_arr, nan=-inf)
        max_spread_radius = spread_radius_arr.max()

        avoidance_radius_arr = array(avoidance_radius_list, dtype=float)
        avoidance_radius_arr = nan_to_num(avoidance_radius_arr, nan=-inf)
        max_avoidance_radius = avoidance_radius_arr.max()

        self.tracing_radius = maximum(
            max_spread_radius,
            max_avoidance_radius
            )

    def kdtrees_and_agents_indices(self) -> None:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            See Also
            --------
            TODO

            Examples
            --------
            TODO: include some examples
        """
        self.kdtree_by_disease_state = {}
        self.agents_labels_by_disease_state = {}

        for disease_state in self.disease_groups_alive:
            # Filter population
            # Exclude those agents hospitalized and those that are dead
            filtered_df = self.population.loc[
                (self.population["disease_state"] == disease_state)
                &
                (~self.population["is_hospitalized"])
                &
                (~self.population["is_dead"])
                ][["agent", "x", "y"]].copy()

            # Calculate how many points were retrieved
            n_points = filtered_df.shape[0]

            if n_points != 0:
                # Get all agents locations
                locations = filtered_df[["x", "y"]].to_numpy()

                # Get all agents labels
                agents_labels = filtered_df["agent"].to_numpy()

                # Select a sensible leafsize for the KDtree method
                one_percent_of_points = floor(n_points*0.01)
                leafsize = (
                    one_percent_of_points
                    if one_percent_of_points > 10 else 10
                    )

                # Initialize (calculate) tree for the disease state
                # and store it inside the dict kdtree_by_disease_state
                self.kdtree_by_disease_state[disease_state] = KDTree(
                    locations, leafsize=leafsize
                    )

                # Also store the corresponding agents labels
                self.agents_labels_by_disease_state[disease_state] = \
                    agents_labels
            else:
                # n_points == 0
                self.kdtree_by_disease_state[disease_state] = None
                self.agents_labels_by_disease_state[disease_state] = None
