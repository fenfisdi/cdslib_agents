from enum import Enum
from dataclasses import dataclass

from abmodel.models.base import SimpleDistGroups, ComplexDistGroups


# ============================================================================
# Groups with distributions in their attributes
# ============================================================================

@dataclass
class SimpleGroups:
    """
        This dataclasss is best suited for supporting
        groups for which only their names are needed
        in the simulation.

        In this version of the library, it is used for:
        `age_groups`, `vulnerability_groups` and
        `quarantine_groups`.

        Attributes
        ----------
        names : list
    """
    names: list


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
    """
    def __post_init__(self):
        """
            This method performs `items` dictionary
            assignment from `group_info` list.
        """
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
