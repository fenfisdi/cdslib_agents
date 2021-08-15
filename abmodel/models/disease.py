from enum import Enum
from dataclasses import dataclass
from copy import deepcopy

from abmodel.models.base import SimpleDistGroups, ComplexDistGroups
from abmodel.utils.utilities import std_str_join_cols


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
    diagnosis = "diagnosis_prob"
    isolation_days = "isolation_days"
    hospitalization = "hospitalization_prob"
    icu_prob = "ICU_prob"
    immunization_time = "immunization_time_distribution"
    time = "time_dist"
    alertness = "alertness_prob"


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
class MobilityGroups(SimpleDistGroups):
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

        See Also
        --------
        DistTitles : fundamental distribution titles

        abmodel.models.base.SimpleDistGroups : Simple Distribution groups class
    """
    def __post_init__(self):
        """
            Validates `dist_title` to be equal to
            `DistTitles.mobility` and then
            performs `items` dictionary
            assignment from `group_info` list.
        """
        self.single_dist_title_validation(
            expected_dist_title=DistTitles.mobility.value
            )
        super().__post_init__()


@dataclass
class DiseaseStates(ComplexDistGroups):
    """
        TODO
    """
    def __post_init__(self):
        """
            This method performs `items` dictionary
            assignment from `group_info` list.
        """
        # TODO
        # Include dist_title_validation

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


@dataclass
class Transitions(ComplexDistGroups):
    """
    """
    def __post_init__(self):
        """
            This method performs `items` dictionary
            assignment from `group_info` list.
        """
        # TODO
        # Include dist_title_validation

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
        TODO
    """
    def __post_init__(self):
        """
            This method performs `items` dictionary
            assignment from `group_info` list.
        """
        # TODO
        # Include dist_title_validation

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
                vulnerability_group, disease_group
                )

            self.transitions[single_group["name"]] = Transitions(
                dist_title=DistTitles.immunization_time,
                group_info=single_group.pop("transitions")
                )

        super().__post_init__()

        for key in self.items.keys():
            self.items[key].transitions = deepcopy(self.transitions[key].items)

        self.__delattr__("transitions")
