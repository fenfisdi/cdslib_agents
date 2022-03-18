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

from enum import Enum
from dataclasses import dataclass
from copy import deepcopy

from abmodel.models import SimpleDistGroups
from abmodel.models import ComplexDistGroups
from abmodel.utils import std_str_join_cols


# ============================================================================
# Groups with distributions in their attributes
# ============================================================================

class DistTitles(Enum):
    """
        This class enumerates some fundamental
        distribution titles that are used
        across the library.
    """
    susceptibility = "susceptibility_dist"
    mobility = "mobility_profile"
    adherence = "adherence_prob"
    diagnosis = "diagnosis_prob"
    isolation_days = "isolation_days"
    hospitalization = "hospitalization_prob"
    icu_prob = "ICU_prob"
    immunization_time = "immunization_time_distribution"
    time = "time_dist"
    alertness = "alertness_prob"
    immunization_level = "immunization_level_dist"
    mr_adherence = "mr_adherence_prob"


@dataclass
class SusceptibilityGroups(SimpleDistGroups):
    """
        Dataclass used for wrapping Susceptibility groups

        Attributes
        ----------
        dist_title : str
            Distribution title. It must be equal to
            `DistTitles.susceptibility`

        group_info : list of dict
            The list of different single group
            information required to instantiate
            a DistributionGroup.

        items : dict
            The dictionary created from the list `group_info`.
            Each key of this dictionary corresponds to a single
            group name.

        See Also
        --------
        DistTitles : fundamental distribution titles

        abmodel.models.base.SimpleDistGroups : Simple Distribution groups class

        Examples
        --------
        TODO: include some examples
    """
    def __post_init__(self):
        """
            Validates `dist_title` to be equal to
            `DistTitles.susceptibility` and then
            performs `items` dictionary
            assignment from `group_info` list.
        """
        self.single_dist_title_validation(
            expected_dist_title=DistTitles.susceptibility.value
            )
        super().__post_init__()


@dataclass
class ImmunizationGroups(SimpleDistGroups):
    """
        Dataclass used for wrapping Immunization groups

        Attributes
        ----------
        TODO

        group_info : list of dict
            The list of different single group
            information required to instantiate
            a DistributionGroup.

        items : dict
            The dictionary created from the list `group_info`.
            Each key of this dictionary corresponds to a single
            group name.

        See Also
        --------
        DistTitles : fundamental distribution titles

        abmodel.models.base.SimpleDistGroups : Simple Distribution groups class

        Examples
        --------
        TODO: include some examples
    """
    def __post_init__(self):
        """
            TODO
        """
        # TODO: Include dist_title_validation
        super().__post_init__()


@dataclass
class MobilityGroups(ComplexDistGroups):
    """
        Dataclass used for wrapping Mobility groups

        Attributes
        ----------
        dist_title : str
            Distribution title. It must be equal to
            `DistTitles.mobility`

        group_info : list of dict
            The list of different single group
            information required to instantiate
            a DistributionGroup.

        items : dict
            The dictionary created from the list `group_info`.
            Each key of this dictionary corresponds to a single
            group name.

        labels : list
            TODO complete explanation

        See Also
        --------
        DistTitles : fundamental distribution titles

        abmodel.models.base.ComplexDistGroups : TODO complete explanation

        Examples
        --------
        TODO: include some examples
    """
    def __post_init__(self):
        """
            This method performs `items` dictionary
            assignment from `group_info` list.
        """
        # TODO: Include dist_title_validation

        self.labels = [
            "angle_variance"
        ]
        super().__post_init__()


@dataclass
class IsolationAdherenceGroups(SimpleDistGroups):
    """
        Dataclass used for wrapping Adherence groups

        Attributes
        ----------
        dist_title : str
            Distribution title. It must be equal to
            `DistTitles.adherence`

        group_info : list of dict
            The list of different single group
            information required to instantiate
            a DistributionGroup.

        items : dict
            The dictionary created from the list `group_info`.
            Each key of this dictionary corresponds to a single
            group name.

        See Also
        --------
        DistTitles : fundamental distribution titles

        abmodel.models.base.SimpleDistGroups : Simple Distribution groups class

        Examples
        --------
        TODO: include some examples
    """
    def __post_init__(self):
        """
            Validates `dist_title` to be equal to
            `DistTitles.adherence` and then
            performs `items` dictionary
            assignment from `group_info` list.
        """
        self.single_dist_title_validation(
            expected_dist_title=DistTitles.adherence.value
            )
        super().__post_init__()


@dataclass
class MRAdherenceGroups(SimpleDistGroups):
    """
        Dataclass used for wrapping Adherence groups

        Attributes
        ----------
        dist_title : str
            Distribution title. It must be equal to
            `DistTitles.adherence`

        group_info : list of dict
            The list of different single group
            information required to instantiate
            a DistributionGroup.

        items : dict
            The dictionary created from the list `group_info`.
            Each key of this dictionary corresponds to a single
            group name.

        See Also
        --------
        DistTitles : fundamental distribution titles

        abmodel.models.base.SimpleDistGroups : Simple Distribution groups class

        Examples
        --------
        TODO: include some examples
    """
    def __post_init__(self):
        """
            Validates `dist_title` to be equal to
            `DistTitles.adherence` and then
            performs `items` dictionary
            assignment from `group_info` list.
        """
        self.single_dist_title_validation(
            expected_dist_title=DistTitles.mr_adherence.value
            )
        super().__post_init__()


@dataclass
class DiseaseStates(ComplexDistGroups):
    """
        TODO: Add brief explanation

        Attributes
        ----------
        TODO

        See Also
        --------
        TODO

        Examples
        --------
        TODO: include some examples
    """
    def __post_init__(self):
        """
            This method performs `items` dictionary
            assignment from `group_info` list.
        """
        # TODO: Include dist_title_validation

        self.labels = [
            "can_get_infected",
            "is_infected",
            "can_spread",
            "spread_radius",
            "spread_radius_unit",
            "spread_probability",
            "is_dead"
        ]
        super().__post_init__()

        # Validate at least one disease_state
        is_dead_list = [self.items[item].is_dead for item in self.items.keys()]

        if not all(isinstance(elem, bool) for elem in is_dead_list):
            raise ValueError("All values for is_dead must be boolean type")
        if True not in is_dead_list:
            raise ValueError("At least one value for is_dead must be True")


@dataclass
class Transitions(ComplexDistGroups):
    """
        TODO: Add brief explanation

        Attributes
        ----------
        TODO

        See Also
        --------
        TODO

        Examples
        --------
        TODO: include some examples
    """
    def __post_init__(self):
        """
            This method performs `items` dictionary
            assignment from `group_info` list.
        """
        # TODO: Include dist_title_validation

        self.labels = [
            "probability",
            "immunization_gain"
        ]

        for single_group in self.group_info:
            single_group["name"] = single_group.pop("transition_name")

        super().__post_init__()

        self.__delattr__("dist_title")
        self.__delattr__("group_info")


@dataclass
class NaturalHistory(ComplexDistGroups):
    """
        TODO: Add brief explanation

        Attributes
        ----------
        TODO

        See Also
        --------
        TODO

        Examples
        --------
        TODO: include some examples
    """
    def __post_init__(self):
        """
            This method performs `items` dictionary
            assignment from `group_info` list.
        """
        # TODO: Include dist_title_validation

        self.labels = [
            "avoidance_radius",
            "avoidance_radius_unit",
            "transition_by_contagion"
        ]

        self.transitions = {}
        for single_group in self.group_info:
            vulnerability_group = single_group.pop("vulnerability_group")
            disease_group = single_group.pop("disease_group")
            single_group["name"] = std_str_join_cols(
                str(vulnerability_group), str(disease_group)
                )

            self.transitions[single_group["name"]] = Transitions(
                dist_title=DistTitles.immunization_time,
                group_info=single_group.pop("transitions")
                )

        super().__post_init__()

        for key in self.items.keys():
            self.items[key].transitions = deepcopy(self.transitions[key].items)

        self.__delattr__("transitions")
