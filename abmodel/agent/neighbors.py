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

from numpy import array, setdiff1d, concatenate, transpose
# where, full, ndarray, isin, concatenate
# from numpy.random import choice, random_sample
from pandas.core.frame import DataFrame

from abmodel.utils.execution_modes import ExecutionModes
from abmodel.utils.utilities import check_field_existance, exception_burner
from abmodel.models.disease import DiseaseStates


def trace_neighbors_vectorized(
    df: DataFrame,
    tracing_radius: float,
    kdtree_by_disease_state: dict,
    agents_labels_by_disease_state: dict,
    dead_disease_group: str,
    disease_groups: DiseaseStates
) -> DataFrame:
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
    # Retrieve agents locations
    agents_locations = df[["x", "y"]].to_numpy()
    agents_labels = df[["agent"]].to_numpy()
    n_agents = df.shape[0]

    susceptible_neighbors = \
        [array([], dtype=int) for index in range(n_agents)]
    infected_spreader_neighbors = \
        [array([], dtype=int) for index in range(n_agents)]
    infected_non_spreader_neighbors = \
        [array([], dtype=int) for index in range(n_agents)]
    immune_neighbors = \
        [array([], dtype=int) for index in range(n_agents)]
    total_neighbors = \
        [array([], dtype=int) for index in range(n_agents)]

    # Cycle through each state of the neighbors
    for disease_state in disease_groups.items.keys():

        can_get_infected = \
            disease_groups.items[disease_state].can_get_infected

        is_infected = \
            disease_groups.items[disease_state].is_infected

        can_spread = \
            disease_groups.items[disease_state].can_spread

        if disease_state != dead_disease_group:

            if kdtree_by_disease_state[disease_state]:

                # Detect if the agents of "disease_state" that are
                # inside a distance equal to the tracing_radius
                # points_inside_radius_array is a ndarray with a list
                # of indeces which correspond neighbors of agent
                points_inside_radius_array = \
                    kdtree_by_disease_state[disease_state] \
                    .query_ball_point(
                        agents_locations,
                        tracing_radius
                        )

                # Now we have to get the corresponding agents labels
                # excluding the agent's own index
                agents_labels_inside_radius_list = [
                    setdiff1d(
                        agents_labels_by_disease_state[disease_state][
                            points_inside_radius_array[i]],
                        agents_labels[i]
                        ).astype(int)
                    for i in range(n_agents)
                    ]

                if can_get_infected:
                    # i.e. susceptibles
                    susceptible_neighbors = [
                        concatenate(
                            (susceptible_neighbors[i],
                                agents_labels_inside_radius_list[i]),
                            axis=None,
                            dtype=int
                            )
                        for i in range(n_agents)
                        ]

                if not can_get_infected and not is_infected:
                    # i.e. inmunes
                    immune_neighbors = [
                        concatenate(
                            (immune_neighbors[i],
                                agents_labels_inside_radius_list[i]),
                            axis=None,
                            dtype=int
                            )
                        for i in range(n_agents)
                        ]

                if is_infected:
                    # infected

                    if can_spread:
                        infected_spreader_neighbors = [
                            concatenate(
                                (infected_spreader_neighbors[i],
                                    agents_labels_inside_radius_list[i]),
                                axis=None,
                                dtype=int
                                )
                            for i in range(n_agents)
                            ]

                    else:
                        infected_non_spreader_neighbors = [
                            concatenate(
                                (infected_non_spreader_neighbors[i],
                                    agents_labels_inside_radius_list[i]),
                                axis=None,
                                dtype=int
                                )
                            for i in range(n_agents)
                            ]

        else:
            # disease_state == dead_disease_group
            pass

    # Extend total_neighbors
    total_neighbors = [
        concatenate(
            (total_neighbors[i],
                susceptible_neighbors[i],
                immune_neighbors[i],
                infected_spreader_neighbors[i],
                infected_non_spreader_neighbors[i]),
            axis=None,
            dtype=int
            )
        for i in range(n_agents)
        ]

    data = array([susceptible_neighbors, infected_spreader_neighbors,
                  infected_non_spreader_neighbors, immune_neighbors,
                  total_neighbors], dtype="object")
    data_transposed = transpose(data)

    if data_transposed.size == 0:
        columns = [i for i in range(5)]
        column_data = [
                [
                    array([]) for agent in range(n_agents)
            ] for column in range(len(columns))
        ]
        data_empty = zip(columns, column_data)
        _df = DataFrame(
            {k: v for k,v in data_empty}
        )
        return _df
    else:
        return DataFrame(data_transposed)


class AgentNeighbors:
    """
        TODO: Add brief explanation

        Methods
        -------
        TODO
    """
    @classmethod
    def trace_neighbors_to_susceptibles(
        cls,
        df: DataFrame,
        tracing_radius: float,
        kdtree_by_disease_state: dict,
        agents_labels_by_disease_state: dict,
        dead_disease_group: str,
        disease_groups: DiseaseStates,
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

            See Also
            --------
            trace_neighbors_vectorized : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            if execmode == ExecutionModes.vectorized.value:
                df[["susceptible_neighbors",
                    "infected_spreader_neighbors",
                    "infected_non_spreader_neighbors",
                    "immune_neighbors",
                    "total_neighbors"]] = trace_neighbors_vectorized(
                    df,
                    tracing_radius,
                    kdtree_by_disease_state,
                    agents_labels_by_disease_state,
                    dead_disease_group,
                    disease_groups
                    )
            else:
                raise NotImplementedError(
                    f"`execmode = {execmode}` is still not implemented yet"
                    )
        except Exception as error:
            validation_list = ["susceptible_neighbors",
                               "infected_spreader_neighbors",
                               "infected_non_spreader_neighbors",
                               "immune_neighbors", "total_neighbors"]
            exception_burner([
                error,
                check_field_existance(df, validation_list)
                ])
        else:
            return df
