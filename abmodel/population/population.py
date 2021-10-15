from numpy import array, nan_to_num, inf, maximum, floor, setdiff1d
from scipy.spatial import KDTree
from pandas.core.frame import DataFrame

from abmodel.models.disease import NaturalHistory, DiseaseStates


class Population:
    """
        TODO: Add brief explanation

        Methods
        -------
        TODO
    """
    def __init__(
        self,
        disease_groups: DiseaseStates,
        natural_history: NaturalHistory
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

            Examples
            --------
            TODO: include some examples
        """
        self.disease_groups = disease_groups
        self.natural_history = natural_history

        self.get_disease_groups_alive()

        self.population = DataFrame()

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
