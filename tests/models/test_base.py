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

import pytest

from abmodel.models import SimpleGroups, DistributionGroup
from abmodel.models import SimpleDistGroups


class TestClassDisease:
    """
        Verifies the functionality of the dataclasses
        defined in disease module.
    """
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    # ========================================================================
    # Fixtures
    # ========================================================================

    @pytest.fixture
    def fixture_SimpleGroups(self) -> list:
        names = [
            "child",
            "teenager",
            "vicenarian",
            "tricenarian",
            "quadragenarian",
            "quinquagenarian",
            "sexagenarian"
        ]
        return names

    @pytest.fixture
    def fixture_DistributionGroup_dictionary(self) -> tuple[str, dict]:
        name = "group_name"
        dist_info = {
            "dist_title": "group_prob",
            "dist_type": "constant",
            "constant": 2.9
        }
        return name, dist_info

    @pytest.fixture
    def fixture_DistributionGroup_list(self) -> tuple[str, list]:
        name = "group"
        dist_info = [
            {
                "dist_title": "group_prob_1",
                "dist_type": "constant",
                "constant": 2.9
            },
            {
                "dist_title": "group_prob_2",
                "dist_type": "numpy",
                "dist_name": "beta",
                "kwargs": {
                    "a": 1,
                    "b": 1
                }
            }
        ]
        return name, dist_info

    @pytest.fixture
    def fixture_SimpleDistGroups_str(self) -> tuple[str, list]:
        dist_title = "group_1"
        group_info = [
            {
                "name": "group_name_1",
                "dist_info": {
                    "dist_title": "group_name_1",
                    "dist_type": "constant",
                    "constant": 2.9
                }
            },
            {
                "name": "group_name_2",
                "dist_info": {
                    "dist_title": "group_name_2",
                    "dist_type": "numpy",
                    "dist_name": "beta",
                    "kwargs": {
                        "a": 1,
                        "b": 1
                    }
                }
            }
        ]
        return dist_title, group_info

    @pytest.fixture
    def fixture_SimpleDistGroups_list(self) -> tuple[list, list]:
        dist_title = ["group_1", "group_2"]
        group_info = [
            {
                "name": "group_name_1",
                "dist_info": {
                    "dist_title": "group_name_1",
                    "dist_type": "constant",
                    "constant": 2.9
                }
            },
            {
                "name": "group_name_2",
                "dist_info": {
                    "dist_title": "group_name_2",
                    "dist_type": "numpy",
                    "dist_name": "beta",
                    "kwargs": {
                        "a": 1,
                        "b": 1
                    }
                }
            }
        ]
        return dist_title, group_info

    # ========================================================================
    # Tests
    # ========================================================================

    def test_SimpleGroups(self, fixture_SimpleGroups):
        """
            Verifies whether SimpleGroups attribute names has a correct lenght
            and elements.
        """
        names = fixture_SimpleGroups

        age_groups = SimpleGroups(
            names=names
        )

        assert len(age_groups.names) == len(names)
        assert age_groups.names == names

    def test_DistributionGroup_dictionary(
        self,
        fixture_DistributionGroup_dictionary
    ):
        """
            Verifies whether DistributionGroup creates the attribute dist and
            assigns a correct type istribution, passing only a dcitionary.
        """
        name = fixture_DistributionGroup_dictionary[0]
        dist_info = fixture_DistributionGroup_dictionary[1]

        distribution_group = DistributionGroup(
            name=name,
            dist_info=dist_info
        )

        assert isinstance(distribution_group.dist, dict)
        assert distribution_group.dist["group_prob"].dist_type == "constant"

    def test_DistributionGroup_list(
        self,
        fixture_DistributionGroup_list
    ):
        """
            Verifies whether DistributionGroup creates the attribute dist and
            assigns a correct typedistribution, passing a list of dictionaries.
        """
        name = fixture_DistributionGroup_list[0]
        dist_info = fixture_DistributionGroup_list[1]

        distribution_group = DistributionGroup(
            name=name,
            dist_info=dist_info
        )

        assert isinstance(distribution_group.dist, dict)
        assert distribution_group.dist["group_prob_1"].dist_type == "constant"
        assert distribution_group.dist["group_prob_2"].dist_type == "numpy"

    def test_SimpleDistGroups_str(
        self,
        fixture_SimpleDistGroups_str
    ):
        """
            Verifies whether SimpleDistGroups assigns a correct dist_title,
            creates a correct type attribute item and assigns a correct type
            distributions, passing a string as dist_title.
        """
        dist_title = fixture_SimpleDistGroups_str[0]
        group_info = fixture_SimpleDistGroups_str[1]

        simple_dist_group = SimpleDistGroups(
            dist_title=dist_title,
            group_info=group_info
        )

        assert isinstance(simple_dist_group.items, dict)
        assert simple_dist_group.dist_title == "group_1"
        assert getattr(
            simple_dist_group.items["group_name_1"], "dist"
        )["group_name_1"].dist_type == "constant"
        assert getattr(
            simple_dist_group.items["group_name_2"], "dist"
        )["group_name_2"].dist_type == "numpy"

        print(simple_dist_group.items)

    def test_SimpleDistGroups_list(
        self,
        fixture_SimpleDistGroups_list
    ):
        """
            Verifies whether SimpleDistGroups assigns a correct dist_title,
            creates a correct type attribute item and assigns a correct type
            distributions, passing a list as dist_title.
        """
        dist_title = fixture_SimpleDistGroups_list[0]
        group_info = fixture_SimpleDistGroups_list[1]

        simple_dist_group = SimpleDistGroups(
            dist_title=dist_title,
            group_info=group_info
        )

        assert isinstance(simple_dist_group.items, dict)
        assert simple_dist_group.dist_title == ["group_1", "group_2"]
        assert getattr(
            simple_dist_group.items["group_name_1"], "dist"
        )["group_name_1"].dist_type == "constant"
        assert getattr(
            simple_dist_group.items["group_name_2"], "dist"
        )["group_name_2"].dist_type == "numpy"
