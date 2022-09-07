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

from typing import Optional

from numpy import array, nan_to_num, inf, maximum, floor, setdiff1d, isin, pi
from scipy.spatial import KDTree
from pandas.core.frame import DataFrame
from pandas import concat

from abmodel.utils import Distribution
from abmodel.utils import ExecutionModes
from abmodel.utils import EvolutionModes
from abmodel.utils import timedelta_to_days
from abmodel.models import DistTitles
from abmodel.models import Configutarion
from abmodel.models import HealthSystem
from abmodel.models import SimpleGroups
from abmodel.models import SusceptibilityGroups
from abmodel.models import ImmunizationGroups
from abmodel.models import MobilityGroups
from abmodel.models import NaturalHistory
from abmodel.models import DiseaseStates
# from abmodel.models import MRTracingPolicies
from abmodel.models import GlobalCyclicMR
# from abmodel.models import CyclicMRPolicies
from abmodel.models import IsolationAdherenceGroups
from abmodel.models import MRAdherenceGroups
from abmodel.agent import AgentMovement
from abmodel.agent import AgentDisease
from abmodel.agent import AgentNeighbors
from .initial_arrangement import InitialArrangement


class Population:
    """
        TODO: Add brief explanation

        Attributes
        ----------
        TODO

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
        mrt_policies: Optional[dict] = None,  # MRTracingPolicies
        global_cyclic_mr: Optional[GlobalCyclicMR] = None,
        cyclic_mr_policies: Optional[dict] = None,  # CyclicMRPolicies
        immunization_groups: Optional[ImmunizationGroups] = None,
        isolation_adherence_groups: Optional[IsolationAdherenceGroups] = None,
        mr_adherence_groups: Optional[MRAdherenceGroups] = None,
        execmode: ExecutionModes = ExecutionModes.iterative.value,
        evolmode: EvolutionModes = EvolutionModes.steps.value,
        npartitions: Optional[int] = 1
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
        self.initial_population_setup_list = initial_population_setup_list
        self.mrt_policies = mrt_policies
        self.global_cyclic_mr = global_cyclic_mr
        self.cyclic_mr_policies = cyclic_mr_policies
        self.immunization_groups = immunization_groups
        self.isolation_adherence_groups = isolation_adherence_groups
        self.mr_adherence_groups = mr_adherence_groups
        self.execmode = execmode
        self.evolmode = evolmode,
        self.npartitions = npartitions 

        # Required columns
        self.__req_cols_dict = {
            "age_group": self.age_groups,
            "disease_state": self.disease_groups,
            "mr_group": self.mr_groups,
            "vulnerability_group": self.vulnerability_groups,
            "mobility_group": self.mobility_groups,
            "susceptibility_group": self.susceptibility_groups,
            "immunization_group": self.immunization_groups,
            "isolation_adherence_group": self.isolation_adherence_groups,
            "mr_adherence_group": self.mr_adherence_groups
            }

        # TODO: Handle units

        # =====================================================================
        # Setup internal variables
        self.__get_disease_groups_alive()
        self.__choose_tracing_radius()

        # =====================================================================
        # Initialize population dataframe
        self.__initialize_df()

    @property
    def evolmode(self):
        return self.__evolmode

    @evolmode.setter
    def evolmode(self, value: EvolutionModes):
        self.__evolmode = value

    def __initialize_df(self):
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            See Also
            --------
            TODO
        """
        # =====================================================================
        # Init population dataframe __df
        self.__df = DataFrame({
            "agent": list(range(self.configuration.population_number))
        })

        # =====================================================================
        # Setup population's initial arrangement
        for initial_population_setup in self.initial_population_setup_list:
            self.__df = InitialArrangement.setup(
                self.__df,
                **initial_population_setup,
                )

        # Take care of required columns not initialized yet
        missing_cols = setdiff1d(
            list(self.__req_cols_dict.keys()),
            self.__df.columns.to_list()
            ).tolist()

        if missing_cols != []:
            self.__df = InitialArrangement.fulfill_setup(
                df=self.__df,
                missing_cols=missing_cols,
                req_cols_dict=self.__req_cols_dict
                )

        # =====================================================================
        # Store step information in a private attribute
        # for checking purposes
        self.__step = 0

        # Convert timedelta to days (float)
        self.dt = timedelta_to_days(self.configuration.iteration_time)

        # Initialize time columns
        self.__df.insert(loc=0, column="step", value=self.__step)
        self.__df.insert(loc=1, column="datetime",
                         value=self.configuration.initial_date)

        # =====================================================================
        # Initialize movement related columns
        self.__df = AgentMovement.init_required_fields(
            df=self.__df,
            box_size=self.configuration.box_size,
            mobility_groups=self.mobility_groups
            )

        # =====================================================================
        # Initialize disease related columns
        self.__df = AgentDisease.init_required_fields(
            df=self.__df,
            dead_disease_group=self.dead_disease_group,
            alpha=self.configuration.alpha,
            beta=self.configuration.beta,
            disease_groups=self.disease_groups,
            natural_history=self.natural_history,
            health_system=self.health_system,
            immunization_groups=self.immunization_groups,
            isolation_adherence_groups=self.isolation_adherence_groups,
            execmode=self.execmode,
            npartitions=self.npartitions
            )

        # =====================================================================
        # Initialize __accumulated_df
        if self.evolmode == EvolutionModes.cumulative.value:
            self.__accumulated_df = self.__df.copy()

        # =====================================================================
        # Initialize __mrt_policies_df
        if self.mrt_policies is not None:
            self.__mrt_policies_df = DataFrame({"step": [self.__step]})
            columns = [item.value for item in self.mrt_policies.keys()]
            for item in columns:
                self.__mrt_policies_df[item] = "disabled"

        else:
            self.__mrt_policies_df = None

        # =====================================================================
        # Initialize __cyclic_mr_policies_df
        cond_1 = self.global_cyclic_mr is not None
        cond_2 = self.cyclic_mr_policies is not None

        if cond_1 and cond_2:
            self.__grace_time_in_steps = int((
                self.global_cyclic_mr.grace_time
                - self.configuration.initial_date
                )/self.configuration.iteration_time)
            self.__cmr_policies_df = DataFrame({"step": [self.__step],
                "global_mr": ["disabled"]})
            for item in list(self.cyclic_mr_policies.keys()):
                self.__cmr_policies_df[item] = "disabled"
        else:
            self.__grace_time_in_steps = None
            self.__cmr_policies_df = None

    def get_population_df(self):
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            See Also
            --------
            TODO
        """
        return self.__df

    def get_accumulated_population_df(self):
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            See Also
            --------
            TODO

        """
        if self.evolmode == ExecutionModes.cumulative.value:
            return self.__accumulated_df
        else:
            raise ValueError(f"Denied: evolmode == {self.evolmode}")

    def get_mrt_policies_df(self):
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            See Also
            --------
            TODO
        """
        if self.mrt_policies is not None:
            return self.__mrt_policies_df
        else:
            raise ValueError("Denied: mrt_policies is None")

    def get_cmr_policies_df(self):
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            See Also
            --------
            TODO
        """
        cond_1 = self.global_cyclic_mr is not None
        cond_2 = self.cyclic_mr_policies is not None

        if cond_1 and cond_2:
            return self.__cmr_policies_df, self.__grace_time_in_steps
        else:
            if not cond_1 and not cond_2:
                raise ValueError(
                    "Denied: both global_cyclic_mr and "
                    "cyclic_mr_policies are None"
                    )
            if not cond_1:
                raise ValueError("Denied: global_cyclic_mr is None")
            if not cond_2:
                raise ValueError("Denied: cyclic_mr_policies is None")

    def get_units(self):
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
        return None

    def evolve(
        self,
        iterations: int
    ):
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
        # TODO: add the option to iterate by date
        for step in range(iterations):
            self.__evolve_single_step()

            if self.evolmode == EvolutionModes.cumulative.value:
                self.__accumulated_df = concat(
                    [self.__accumulated_df, self.__df],
                    ignore_index=True
                    )

    def __remove_dead_agents(self):
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
        self.__df = self.__df[
            ~self.__df[["is_dead"]].any(axis="columns")
            ]

    def __evolve_single_step(self):
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
        # =====================================================================
        # Remove dead agents before evolving population dataframe
        self.__remove_dead_agents()
        former_df = self.__df.copy()

        # =====================================================================
        # Evolve step
        self.__step += 1
        self.__df["step"] = self.__step

        # Evolve date
        self.__df["datetime"] += self.configuration.iteration_time

        # =====================================================================
        # Update agents' velocities
        for mobility_group in self.mobility_groups.items.keys():
            self.__df = AgentMovement.update_velocities(
                df=self.__df,
                distribution=self.mobility_groups
                .items[mobility_group].dist[DistTitles.mobility.value],
                angle_variance=self.mobility_groups
                .items[mobility_group].angle_variance,
                group_field="mobility_group",
                group_label=mobility_group,
                preserve_dtypes_dict={"step": int, "agent": int}
                )

        # =====================================================================
        # Update population states by means of state transition
        self.__df = AgentDisease.disease_state_transition(
            df=self.__df,
            dt=self.dt,
            disease_groups=self.disease_groups,
            natural_history=self.natural_history,
            execmode=self.execmode,
            npartitions=self.npartitions
            )

        # =====================================================================
        # Update Hospitalization and ICU status
        self.__df = AgentDisease.to_hospitalize_agents(
            df=self.__df,
            dead_disease_group=self.dead_disease_group,
            alpha=self.configuration.alpha,
            disease_groups=self.disease_groups,
            health_system=self.health_system,
            execmode=ExecutionModes.vectorized.value
            )

        # =====================================================================
        # Update diagnosis status
        self.__df = AgentDisease.to_diagnose_agents(
            df=self.__df,
            disease_groups=self.disease_groups,
            execmode=self.execmode,
            npartitions=self.npartitions
            )

        # =====================================================================
        # Update isolation status
        self.__df = AgentDisease.to_isolate_agents(
            df=self.__df,
            dt=self.dt,
            beta=self.configuration.beta,
            disease_groups=self.disease_groups,
            isolation_adherence_groups=self.isolation_adherence_groups,
            execmode=self.execmode,
            npartitions=self.npartitions
            )

        # =====================================================================
        # Stop isolated and hospitalized agents
        indexes = self.__df.query(
            "is_isolated == True | is_hospitalized == True"
            ).index.values

        if len(indexes) != 0:
            self.__df = AgentMovement.stop_agents(self.__df, indexes)

        # =====================================================================
        # Initialize velocities for formerly isolated and formerly hospitalized
        # agents
        former_indexes = former_df.query(
            "is_isolated == True | is_hospitalized == True"
            ).index.values

        mask = isin(former_indexes, indexes, invert=True)
        should_init_indexes = former_indexes[mask]

        if len(should_init_indexes) != 0:
            for mobility_group in self.mobility_groups.items.keys():
                self.__df = AgentMovement.initialize_velocities(
                    df=self.__df,
                    distribution=self.mobility_groups.items[
                        mobility_group].dist[DistTitles.mobility.value],
                    angle_distribution=Distribution(
                        dist_type="numpy",
                        dist_name="uniform",
                        low=0.0,
                        high=2*pi
                        ),
                    indexes=should_init_indexes,
                    group_field="mobility_group",
                    group_label=mobility_group,
                    preserve_dtypes_dict={"step": int, "agent": int}
                    )

        # =====================================================================
        # Create KDTree for agents of each alive disease state
        self.__kdtrees_and_agents_indices()

        # =====================================================================
        # Trace neighbors to susceptible agents
        self.__df = AgentNeighbors.trace_neighbors_to_susceptibles(
            df=self.__df,
            tracing_radius=self.tracing_radius,
            kdtree_by_disease_state=self.kdtree_by_disease_state,
            agents_labels_by_disease_state=self.agents_labels_by_disease_state,
            dead_disease_group=self.dead_disease_group,
            disease_groups=self.disease_groups,
            execmode=ExecutionModes.vectorized.value
            )

        # =====================================================================
        # Update alertness states for avoiding avoidable agents
        self.__df = AgentDisease.update_alertness_state(
            df=self.__df,
            kdtree_by_disease_state=self.kdtree_by_disease_state,
            agents_labels_by_disease_state=self.agents_labels_by_disease_state,
            natural_history=self.natural_history,
            disease_groups=self.disease_groups,
            dead_disease_group=self.dead_disease_group,
            execmode=self.execmode,
            npartitions=self.npartitions
            )

        # =====================================================================
        # Change population states by means of contagion
        self.__df = AgentDisease.disease_state_transition_by_contagion(
            df=self.__df,
            kdtree_by_disease_state=self.kdtree_by_disease_state,
            agents_labels_by_disease_state=self.agents_labels_by_disease_state,
            natural_history=self.natural_history,
            disease_groups=self.disease_groups,
            susceptibility_groups=self.susceptibility_groups,
            execmode=self.execmode,
            npartitions=self.npartitions
            )

        # =====================================================================
        # Update immunization level
        self.__df = AgentDisease.update_immunization_level(
            df=self.__df,
            dt=self.dt,
            natural_history=self.natural_history,
            execmode=self.execmode,
            npartitions=self.npartitions
            )

        # =====================================================================
        # Mobility Restrictions
        variables = AgentDisease.apply_mobility_restrictions(
            step=self.__step,
            df=self.__df,
            beta=self.configuration.beta,
            mrt_policies=self.mrt_policies,
            mrt_policies_df=self.__mrt_policies_df,
            global_cyclic_mr=self.global_cyclic_mr,
            cyclic_mr_policies=self.cyclic_mr_policies,
            cmr_policies_df=self.__cmr_policies_df,
            grace_time_in_steps=self.__grace_time_in_steps,
            iteration_time=self.configuration.iteration_time,
            mr_adherence_groups=self.mr_adherence_groups,
            execmode=ExecutionModes.iterative.value
            )
        # Assign values
        self.__df = variables[0]
        self.__mrt_policies_df = variables[1]
        self.__cmr_policies_df = variables[2]
        
        # =====================================================================
        # Stop agents isolated by mobility resytictions
        indexes = self.__df.query("isolated_by_mr == True").index.values

        if len(indexes) != 0:
            self.__df = AgentMovement.stop_agents(self.__df, indexes)

        # =====================================================================
        # Initialize velocities for formerly isolated by mr
        # agents
        former_indexes = former_df.query(
            "isolated_by_mr == True"
            ).index.values

        mask = isin(former_indexes, indexes, invert=True)
        should_init_indexes = former_indexes[mask]

        if len(should_init_indexes) != 0:
            for mobility_group in self.mobility_groups.items.keys():
                self.__df = AgentMovement.initialize_velocities(
                    df=self.__df,
                    distribution=self.mobility_groups.items[
                        mobility_group].dist[DistTitles.mobility.value],
                    angle_distribution=Distribution(
                        dist_type="numpy",
                        dist_name="uniform",
                        low=0.0,
                        high=2*pi
                        ),
                    indexes=should_init_indexes,
                    group_field="mobility_group",
                    group_label=mobility_group,
                    preserve_dtypes_dict={"step": int, "agent": int}
                    )

        # =====================================================================
        # Avoid avoidable agents
        filtered_df = self.__df[self.__df["is_alert"]][["agent", "alerted_by"]]
        df_to_avoid = filtered_df \
            .explode("alerted_by") \
            .rename(columns={"alerted_by": "agent_to_avoid"})
        if df_to_avoid.empty is False:
            self.__df = AgentMovement.avoid_agents(
                df=self.__df,
                df_to_avoid=df_to_avoid
            )

        # =====================================================================
        # Update agents' positions
        # NOTE: mobility_profile should be in iteration_time units, so the
        # value we should use for dt here is dt=1.0
        self.__df = AgentMovement.move_agents(
            df=self.__df,
            box_size=self.configuration.box_size,
            dt=1.0
            )

    def __get_disease_groups_alive(self) -> None:
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

    def __choose_tracing_radius(self) -> None:
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

    def __kdtrees_and_agents_indices(self) -> None:
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
            filtered_df = self.__df.loc[
                (self.__df["disease_state"] == disease_state)
                &
                (~self.__df["is_hospitalized"])
                &
                (~self.__df["is_dead"])
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
