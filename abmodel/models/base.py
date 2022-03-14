
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

from typing import Union, Any
from dataclasses import dataclass, field
from copy import deepcopy

from munch import Munch
from pydantic import BaseModel

from abmodel.utils import Distribution
from abmodel.utils import init_distribution


# ============================================================================
# Groups with only names in their attributes
# ============================================================================

class SimpleGroups(BaseModel):
    """
        This dataclasss is best suited for supporting
        groups for which only their names are needed
        in the simulation.

        In this version of the library, it is used for:
        `age_groups`, `vulnerability_groups` and
        `mr_groups` (i.e. mobility restrictions groups).

        Attributes
        ----------
        names : list

        Examples
        --------
        TODO: include some examples
    """
    names: list


# ============================================================================
# Groups with distributions in their attributes
# ============================================================================

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

        dist_info : dict or list of dict
            Dictionary with the required information
            in order to initialize the distribution.
            It must contain `dist_title` key, which refers to
            the distribution title.

        dist : dict of Distribution
            Distribution used in this group.

        Raises
        ------
            TODO

        See Also
        --------
        abmodel.utils.helpers.distributions.init_distribution : Function to
        initialize a distribution

        abmodel.utils.distributions.Distribution : Distribution class

        Examples
        --------
        TODO: include some examples
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
        elif isinstance(self.dist_info, list):
            # self.dist_info is a list of dictionaries
            for dist_dict in self.dist_info:
                prepare_dict_field(dist_dict)
        else:
            # TODO
            raise ValueError("TODO")


@dataclass
class SimpleDistGroups:
    """
        This dataclass wraps a set of DistributionGroup
        in a dictionary in order to make easier
        their retrieval.

        Attributes
        ----------
        dist_title : str or list of str


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
        DistributionGroup : Single Distribution group

        ComplexDistGroups : Set of groups compound
            by distributions and other additional fields.

        Examples
        --------
        TODO: include some examples
    """
    dist_title: Union[str, list[str]]
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

    def single_dist_title_validation(self, expected_dist_title: str):
        """
            Validates `dist_title` to be equal to
            `expected_dist_title`.

            Parameters
            ----------
            expected_dist_title : str
                Canonical value of the expected distribution
                title.

            Raises
            ------
            ValueError
                If `dist_title` is not equal to `expected_dist_title`.
                If `dist_title` is not the same for all the groups.
                If `dist_title` for all the groups is not equal to
                `expected_dist_title`.
        """
        # Assess if dist_title == expected_dist_title
        condition = self.dist_title == expected_dist_title
        assert condition, ValueError(
            "'dist_title' is not equal to "
            f"'{expected_dist_title}'"
            )

        # Retrieve dist_title list from all group's single dist_title
        dist_title_list = [
            group['dist_info']['dist_title']
            for group in self.group_info
            ]

        # Assess if dist_title is the same for all the groups
        condition = len(set(dist_title_list)) == 1
        assert condition, ValueError(
            f"The list of dist_title in the group is: {dist_title_list}"
            "\n"
            "All of them must be the same and equal to "
            f"'{expected_dist_title}'"
        )

        # Assess if dist_title for all the groups is equal to
        # expected_dist_title
        condition = dist_title_list[0] == expected_dist_title
        assert condition, ValueError(
            f"The dist_title for each group is: {dist_title_list[0]}"
            "\n"
            f"It must be equal to '{expected_dist_title}'"
        )

    def multiple_dist_title_validation(self, expected_dist_title):
        """
            TODO:
                - Update expected_dist_title type
                - Update this docstring

            Validates `dist_title` list to be equal to
            `expected_dist_title` list.

            Parameters
            ----------
            expected_dist_title : list of str
                Canonical list of values of the expected distribution
                titles.

            Raises
            ------
            ValueError
                If `dist_title` and `expected_dist_title` does not have the
                same length.

                If `dist_title` is the same for all the groups
                If `dist_title` for all the groups is equal to
                `expected_dist_title`
        """
        # Assess if dist_title and expected_dist_title have the same length
        condition = len(self.dist_title) == len(expected_dist_title)
        assert condition, ValueError(
            "'dist_title' does not have the same length of "
            f"'{expected_dist_title}'"
            )

        # Assess if dist_title and expected_dist_title have the same elements
        condition = set(self.dist_title) == set(expected_dist_title)
        assert condition, ValueError(
            "'dist_title' does not have the same elements of "
            f"'{expected_dist_title}'"
            )

        # Retrieve dist_title list from all group's dist_titles
        dist_title_list = [
            [dist['dist_title'] for dist in group['dist_info']]
            for group in self.group_info
            ]

        print(dist_title_list)
        # TODO: to finish validations
        # # Assess if dist_title is the same for all the groups
        # condition = len(set(dist_title_list)) == 1
        # assert condition, ValueError(
        #     f"The list of dist_title in the group is: {dist_title_list}"
        #     "\n"
        #     "All of them must be the same and equal to "
        #     f"'{expected_dist_title}'"
        # )

        # # Assess if dist_title for all the groups is equal to
        # # expected_dist_title
        # condition = dist_title_list[0] == expected_dist_title
        # assert condition, ValueError(
        #     f"The dist_title for each group is: {dist_title_list[0]}"
        #     "\n"
        #     f"It must be equal to '{expected_dist_title}'"
        # )


@dataclass
class ComplexDistGroups(SimpleDistGroups):
    """
        This dataclass wraps a set of DistributionGroup
        in a dictionary in order to make easier
        their retrieval, nevertheless it differs from `SimpleDistGroups`
        in the fact that in addition to the distribution,
        it is also intended to wrap information
        from other fields specified by `labels` list.

        Attributes
        ----------
        group_info : list of dict
            The list of different single group
            information required to instantiate
            a DistributionGroup.

        labels : list
            Labels of the other fields apart from `dist`
            distribution.

        items : dict
            The dictionary created from the list `group_info`
            and the list of `labels`. Each key of this
            dictionary corresponds to a single
            group name.

        See Also
        --------
        DistributionGroup : TODO complete explanation

        SimpleDistGroups : Set of groups compound only
            by distributions.

        Examples
        --------
        TODO: include some examples
    """
    labels: list = field(init=False)

    def __post_init__(self):
        """
            This method performs `items` dictionary
            assignment from `group_info` list.
        """
        # Copy self.group_info in order to avoid
        # that it gets modified
        group_info = deepcopy(self.group_info)

        self.items = {
            single_group["name"]: Munch({
                label.replace(" ", "_"): single_group.pop(label)
                for label in self.labels
                })
            for single_group in group_info
        }

        for single_group in group_info:
            self.items[
                single_group["name"]
                ].dist = deepcopy(
                    DistributionGroup(**single_group).dist
                )
