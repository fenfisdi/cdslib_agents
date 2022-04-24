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

from abmodel.models import DistTitles, SusceptibilityGroups
from abmodel.models import ImmunizationGroups, MobilityGroups
from abmodel.models import IsolationAdherenceGroups, MRAdherenceGroups
from abmodel.models import DiseaseStates, Transitions, NaturalHistory


class TestClassDisease:
    """
        Verifies the functionality of all class in the disease module.
    """
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    # ========================================================================
    # Fixtures
    # ========================================================================

    @pytest.fixture
    def fixture_DistTitles(self) -> list:
        distribution_titles = [
            "susceptibility_dist",
            "mobility_profile",
            "adherence_prob",
            "diagnosis_prob",
            "isolation_days",
            "hospitalization_prob",
            "ICU_prob",
            "immunization_time_distribution",
            "time_dist",
            "alertness_prob",
            "immunization_level_dist",
            "mr_adherence_prob",
        ]
        return distribution_titles

    @pytest.fixture
    def fixture_SusceptibilityGroups(self) -> tuple[str, list]:
        dist_title = "susceptibility_dist"
        group_info = [
            {
                "name": "suceptibility_group_1",
                "dist_info": {
                    "dist_title": "susceptibility_dist",
                    "dist_type": "constant",
                    "constant": 2.9
                }
            },
            {
                "name": "suceptibility_group_2",
                "dist_info": {
                    "dist_title": "susceptibility_dist",
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
    def fixture_ImmunizationGroups(self) -> tuple[list, list]:
        dist_title = [
            "immunization_level_dist",
            "immunization_time_distribution"
        ]
        group_info = [
            {
                "name": "immunizated",
                "dist_info": {
                    "dist_title": "immunization_level_dist",
                    "dist_type": "constant",
                    "constant": 2.9
                }
            },
            {
                "name": "not_immunizated",
                "dist_info": {
                    "dist_title": "immunization_time_distribution",
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
    def fixture_MobilityGroups(self) -> tuple[str, list]:
        dist_title = "mobility_profile"
        group_info = [
            {
                "name": "MG_1",
                "angle_variance": 0.5,
                "dist_info": {
                    "dist_title": "mobility_profile",
                    "dist_type": "constant",
                    "constant": 2.9
                }
            },
            {
                "name": "MG_2",
                "angle_variance": 0.5,
                "dist_info": {
                    "dist_title": "mobility_profile",
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
    def fixture_IsolationAdherenceGroups(self) -> tuple[str, list]:
        dist_title = "adherence_prob"
        group_info = [
            {
                "name": "adherence_group_1",
                "dist_info": {
                    "dist_title": "adherence_prob",
                    "dist_type": "constant",
                    "constant": 2.9
                }
            },
            {
                "name": "adherence_group_2",
                "dist_info": {
                    "dist_title": "adherence_prob",
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
    def fixture_MRAdherenceGroups(self) -> tuple[str, list]:
        dist_title = "mr_adherence_prob"
        group_info = [
            {
                "name": "mr_adherence_group_1",
                "dist_info": {
                    "dist_title": "mr_adherence_prob",
                    "dist_type": "constant",
                    "constant": 2.9
                }
            },
            {
                "name": "mr_adherence_group_2",
                "dist_info": {
                    "dist_title": "mr_adherence_prob",
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
    def fixture_DiseaseStates(self) -> tuple[list, list]:
        dist_title = ["hospitalization_prob", "ICU_prob"]
        group_info = [
            {
                "name": "infectious",
                "can_get_infected": False,
                "is_infected": True,
                "can_spread": True,
                "spread_radius": 3,
                "spread_radius_unit": "meters",
                "spread_probability": 0.75,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "hospitalization_prob",
                        "dist_type": "constant",
                        "constant": 2.9
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": "constant",
                        "constant": 2.9
                    }
                ]
            },
            {
                "name": "dead",
                "can_get_infected": False,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": True,
                "dist_info": [
                    {
                        "dist_title": "hospitalization_prob",
                        "dist_type": None,
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": None,
                    }
                ]
            }
        ]
        return dist_title, group_info

    @pytest.fixture
    def fixture_DiseaseStates_dead_label_are_not_bool(
        self
    ) -> tuple[list, list]:
        dist_title = ["hospitalization_prob", "ICU_prob"]
        group_info = [
            {
                "name": "infectious",
                "can_get_infected": False,
                "is_infected": True,
                "can_spread": True,
                "spread_radius": 3,
                "spread_radius_unit": "meters",
                "spread_probability": 0.75,
                "is_dead": "yes",
                "dist_info": [
                    {
                        "dist_title": "hospitalization_prob",
                        "dist_type": "constant",
                        "constant": 2.9
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": "constant",
                        "constant": 2.9
                    }
                ]
            },
            {
                "name": "dead",
                "can_get_infected": False,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": "yes",
                "dist_info": [
                    {
                        "dist_title": "hospitalization_prob",
                        "dist_type": None,
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": None,
                    }
                ]
            }
        ]
        return dist_title, group_info

    @pytest.fixture
    def fixture_DiseaseStates_there_is_not_dead(self) -> tuple[list, list]:
        dist_title = ["hospitalization_prob", "ICU_prob"]
        group_info = [
            {
                "name": "infectious",
                "can_get_infected": False,
                "is_infected": True,
                "can_spread": True,
                "spread_radius": 3,
                "spread_radius_unit": "meters",
                "spread_probability": 0.75,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "hospitalization_prob",
                        "dist_type": "constant",
                        "constant": 2.9
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": "constant",
                        "constant": 2.9
                    }
                ]
            }
        ]
        return dist_title, group_info

    @pytest.fixture
    def fixture_Transitions(self) -> tuple[str, list]:
        dist_title = "transitions"
        group_info = [
            {
                "transition_name": "transition_1",
                "probability": 1.0,
                "immunization_gain": 0.0,
                "dist_info": {
                    "dist_title": "transition_prob",
                    "dist_type": "constant",
                    "constant": 2.9
                }
            },
            {
                "transition_name": "transition_2",
                "probability": 1.0,
                "immunization_gain": 0.0,
                "dist_info": {
                    "dist_title": "transition_prob",
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
    def fixture_NaturalHistory(self) -> tuple[str, list]:
        dist_title = "transitions"
        group_info = [
            {
                "avoidance_radius": 1,
                "avoidance_radius_unit": "meters",
                "transition_by_contagion": True,
                "vulnerability_group": "not_vulnerable",
                "disease_group": "suceptible",
                "transitions": [
                    {
                        "transition_name": "transition_1",
                        "probability": 1.0,
                        "immunization_gain": 0.0,
                        "dist_info": {
                            "dist_title": "transition_prob",
                            "dist_type": "constant",
                            "constant": 2.9
                        }
                    }
                ],
                "dist_info": {
                    "dist_title": "time_dist",
                    "dist_type": "constant",
                    "constant": 2.9
                }
            },
            {
                "avoidance_radius": 1,
                "avoidance_radius_unit": "meters",
                "transition_by_contagion": True,
                "vulnerability_group": "vulnerable",
                "disease_group": "suceptible",
                "transitions": [
                    {
                        "transition_name": "transition_1",
                        "probability": 1.0,
                        "immunization_gain": 0.0,
                        "dist_info": {
                            "dist_title": "transition_prob",
                            "dist_type": "constant",
                            "constant": 2.9
                        }
                    }
                ],
                "dist_info": {
                    "dist_title": "time_dist",
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

    def test_DistTitles(self, fixture_DistTitles):
        """
            Verifies whether DistTitles enumerates correctly dist titles.
        """
        items = fixture_DistTitles

        dist_titles = list(DistTitles)

        for dist_title, item in zip(dist_titles, items):
            assert dist_title.value == item

    def test_SusceptibilityGroups(self, fixture_SusceptibilityGroups):
        """
            Verifies whether SusceptibilityGroups assigns correctly
            dist_title attribute, creates item with its right type
            and assigns a correct type distributions for each group.
        """
        dist_title = fixture_SusceptibilityGroups[0]
        group_info = fixture_SusceptibilityGroups[1]

        susceptibility_groups = SusceptibilityGroups(
            dist_title,
            group_info
        )

        assert isinstance(susceptibility_groups.items, dict)
        assert susceptibility_groups.dist_title == \
            DistTitles.susceptibility.value
        assert getattr(
            susceptibility_groups.items["suceptibility_group_1"], "dist"
        )["susceptibility_dist"].dist_type == "constant"
        assert getattr(
            susceptibility_groups.items["suceptibility_group_2"], "dist"
        )["susceptibility_dist"].dist_type == "numpy"

    def test_ImmunizationGroups(self, fixture_ImmunizationGroups):
        """
            Verifies whether ImmunizationGroups assigns correctly
            dist_title attribute, creates item with its right type
            and assigns a correct type distributions for each group.
        """
        dist_title = fixture_ImmunizationGroups[0]
        group_info = fixture_ImmunizationGroups[1]

        immunization_groups = ImmunizationGroups(
            dist_title,
            group_info
        )

        assert isinstance(immunization_groups.items, dict)
        assert immunization_groups.dist_title == dist_title
        assert getattr(
            immunization_groups.items["immunizated"], "dist"
        )["immunization_level_dist"].dist_type == "constant"
        assert getattr(
            immunization_groups.items["not_immunizated"], "dist"
        )["immunization_time_distribution"].dist_type == "numpy"

    def test_MobilityGroups(self, fixture_MobilityGroups):
        """
            Verifies whether MobilityGroups assigns correctly
            dist_title attribute, creates item with its right type
            and assigns a correct type distributions for each group.
            Finally, Assigns the attribute labels.
        """
        dist_title = fixture_MobilityGroups[0]
        group_info = fixture_MobilityGroups[1]

        mobility_groups = MobilityGroups(
            dist_title,
            group_info
        )

        assert isinstance(mobility_groups.items, dict)
        assert mobility_groups.dist_title == dist_title
        assert mobility_groups.labels == ["angle_variance"]
        print(mobility_groups.items)
        assert getattr(
            mobility_groups.items["MG_1"], "dist"
        )[DistTitles.mobility.value].dist_type == "constant"
        assert getattr(
            mobility_groups.items["MG_2"], "dist"
        )[DistTitles.mobility.value].dist_type == "numpy"

    def test_IsolationAdherenceGroups(self, fixture_IsolationAdherenceGroups):
        """
            Verifies whether IsolationAdherenceGroups assigns correctly
            dist_title attribute, creates item with its right type
            and assigns a correct type distributions for each group.
        """
        dist_title = fixture_IsolationAdherenceGroups[0]
        group_info = fixture_IsolationAdherenceGroups[1]

        isolation_adherence_groups = IsolationAdherenceGroups(
            dist_title,
            group_info
        )

        assert isinstance(isolation_adherence_groups.items, dict)
        assert isolation_adherence_groups.dist_title == \
            DistTitles.adherence.value
        assert getattr(
            isolation_adherence_groups.items["adherence_group_1"], "dist"
        )[DistTitles.adherence.value].dist_type == "constant"
        assert getattr(
            isolation_adherence_groups.items["adherence_group_2"], "dist"
        )[DistTitles.adherence.value].dist_type == "numpy"

    def test_MRAdherenceGroups(self, fixture_MRAdherenceGroups):
        """
            Verifies whether MRAdherenceGroups assigns correctly
            dist_title attribute, creates item with its right type
            and assigns a correct type distributions for each group.
        """
        dist_title = fixture_MRAdherenceGroups[0]
        group_info = fixture_MRAdherenceGroups[1]

        mr_adherence_groups = MRAdherenceGroups(
            dist_title,
            group_info
        )

        assert isinstance(mr_adherence_groups.items, dict)
        assert mr_adherence_groups.dist_title == DistTitles.mr_adherence.value
        assert getattr(
            mr_adherence_groups.items["mr_adherence_group_1"], "dist"
        )[DistTitles.mr_adherence.value].dist_type == "constant"
        assert getattr(
            mr_adherence_groups.items["mr_adherence_group_2"], "dist"
        )[DistTitles.mr_adherence.value].dist_type == "numpy"

    def test_DiseaseStates(self, fixture_DiseaseStates):
        """
            Verifies whether DiseaseStates creates the item
            attribute with its right type and assigns a
            correct type distributions for each group.
            Finally, Assigns labels attribute.
        """
        dist_title = fixture_DiseaseStates[0]
        group_info = fixture_DiseaseStates[1]

        disease_groups = DiseaseStates(
            dist_title,
            group_info
        )

        assert isinstance(disease_groups.items, dict)
        assert disease_groups.labels == [
            "can_get_infected",
            "is_infected",
            "can_spread",
            "spread_radius",
            "spread_radius_unit",
            "spread_probability",
            "is_dead"
        ]
        assert getattr(
            disease_groups.items["infectious"], "dist"
        )[DistTitles.hospitalization.value].dist_type == "constant"
        assert getattr(
            disease_groups.items["infectious"], "dist"
        )[DistTitles.icu_prob.value].dist_type == "constant"
        assert getattr(
            disease_groups.items["dead"], "dist"
        )[DistTitles.hospitalization.value].dist_type == None
        assert getattr(
            disease_groups.items["dead"], "dist"
        )[DistTitles.icu_prob.value].dist_type == None

    def test_DiseaseStates_labels_are_not_bool(
        self,
        fixture_DiseaseStates_dead_label_are_not_bool
    ):
        """
            Raises ValueError when dead label are not a bool type.
        """
        dist_title = fixture_DiseaseStates_dead_label_are_not_bool[0]
        group_info = fixture_DiseaseStates_dead_label_are_not_bool[1]

        with pytest.raises(
            ValueError,
            match="All values for is_dead must be boolean type"
        ):
            DiseaseStates(
                dist_title,
                group_info
            )

    def test_DiseaseStates_there_is_not_dead(
        self,
        fixture_DiseaseStates_there_is_not_dead
    ):
        """
            Raises ValueError when there is not a
            group with dead label equals to True.
        """
        dist_title = fixture_DiseaseStates_there_is_not_dead[0]
        group_info = fixture_DiseaseStates_there_is_not_dead[1]

        with pytest.raises(
            ValueError,
            match="At least one value for is_dead must be True"
        ):
            DiseaseStates(
                dist_title,
                group_info
            )

    def test_Transitions(self, fixture_Transitions):
        """
            Verifies whether Transitions creates the item
            attribute with its right type and assigns a
            correct type distributions for each group.
            Assigns labels attribute, and deletes
            dist_title and group_infoattributes.
        """
        dist_title = fixture_Transitions[0]
        group_info = fixture_Transitions[1]

        transitions = Transitions(
            dist_title,
            group_info
        )

        assert isinstance(transitions.items, dict)
        transitions.labels == [
            "probability",
            "immunization_gain"
        ]
        assert getattr(
            transitions.items["transition_1"], "dist"
        )["transition_prob"].dist_type == "constant"
        assert getattr(
           transitions.items["transition_2"], "dist"
        )["transition_prob"].dist_type == "numpy"
        with pytest.raises(AttributeError):
            transitions.dist_title
            transitions.group_info

    def test_NaturalHistory(self, fixture_NaturalHistory):
        """
            Verifies whether NaturalHistory creates the item
            attribute with its right type and assigns a
            correct type distributions for each group.
            Assigns labels attribute, and deletes
            transitions attribute.
        """
        dist_title = fixture_NaturalHistory[0]
        group_info = fixture_NaturalHistory[1]

        natural_history = NaturalHistory(
            dist_title,
            group_info
        )

        assert isinstance(natural_history.items, dict)
        natural_history.labels == [
            "avoidance_radius",
            "avoidance_radius_unit",
            "transition_by_contagion"
        ]
        assert getattr(
            natural_history.items["not_vulnerable-suceptible"], "dist"
        )["time_dist"].dist_type == "constant"
        assert getattr(
            natural_history.items["vulnerable-suceptible"], "dist"
        )["time_dist"].dist_type == "numpy"
        with pytest.raises(AttributeError):
            natural_history.transitions
