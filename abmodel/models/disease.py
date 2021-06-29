from enum import Enum
from dataclasses import dataclass

from abmodel.models.base import SimpleDistGroups


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


@dataclass
class SusceptibilityGroups(SimpleDistGroups):
    """
        Dataclass used for wrapping Susceptibility groups

        Attributes
        ----------
        dist_title : str
            Distribution title. It must be equal to
            `DistTitles.susceptibility`

        group_info : list[dict]
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
    dist_title: str

    def __post_init__(self):
        """
            Validates `dist_title` to be equal to
            `DistTitles.susceptibility`
        """
        condition = self.dist_title == DistTitles.susceptibility.value
        assert condition, ValueError(
            "'dist_title' is not equal to "
            f"'{DistTitles.susceptibility.value}'"
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

        group_info : list[dict]
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
    dist_title: str

    def __post_init__(self):
        """
            Validates `dist_title` to be equal to
            `SimpleDistTitles.mobility`
        """
        condition = self.dist_title == DistTitles.mobility.value
        assert condition, ValueError(
            "'dist_title' is not equal to "
            f"'{DistTitles.mobility.value}'"
            )
        super().__post_init__()
