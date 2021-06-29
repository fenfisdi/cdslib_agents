from typing import Union, Any
from dataclasses import dataclass, field

from abmodel.utils.distributions import Distribution
from abmodel.utils.helpers.distributions import init_distribution


@dataclass
class DistributionGroup:
    """
        This dataclass uses `init_distribution` function
        in order to encapsulate a Distribution
        as the attribute `dist` belonging to this class.

        Attributes
        ----------
        name : str
            Group name.

        dist_info : Union[dict, list[dict]]
            Dictionary with the required information
            in order to initialize the distribution.
            It must contain `dist_title` key, which refers to
            the distribution title.

        dist : dict[Distribution]
            Distribution used in this group.

        See Also
        --------
        abmodel.utils.helpers.distributions.init_distribution : Function to
        initialize a distribution

        abmodel.utils.distributions.Distribution : Distribution class

    """
    name: str
    dist_info: Union[dict[str, Any], list[dict[str, Any]]]
    dist: dict[Distribution] = field(init=False)

    def __post_init__(self):
        """
            This method initializes `dist` distribution
            dictionary from `dist_info` info.
        """
        def prepare_dict_field(dist_dict) -> None:
            """
                This method adds a single distribution
                to `dist` distribution dictionary

                Parameters
                ----------
                dist_dict : dict
                    It is a single distribution dictionary
            """
            dist_title = dist_dict.pop("dist_title")
            self.dist[dist_title] = init_distribution(dist_dict)

        # Initialize void dict
        self.dist = {}

        if isinstance(self.dist_info, dict):
            prepare_dict_field(self.dist_info)
        else:
            # self.dist_info should be a list of dictionaries
            for dist_dict in self.dist_info:
                prepare_dict_field(dist_dict)


@dataclass
class SimpleDistGroups:
    """
        This dataclass wraps a set of DistributionGroup
        in a dictionary in order to make easier
        their retrieval.

        Attributes
        ----------
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
        DistributionGroup : Single Distribution group
    """
    group_info: list[dict]
    items: dict = field(init=False)

    def __post_init__(self):
        """
            This method performs `items` dictionary
            assignment from `group_info` list.
        """
        self.items = {
            single_group["name"]: DistributionGroup(**single_group)
            for single_group in self.group_info
        }
