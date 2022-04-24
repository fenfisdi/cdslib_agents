import pytest
from datetime import timedelta
from math import nan, isnan
from pandas import DataFrame, Series, testing

from abmodel.agent.disease import AgentDisease
from abmodel.agent.disease import init_calculate_max_time_iterative
from abmodel.agent.disease import init_calculate_max_time_vectorized
from abmodel.agent.disease import calculate_max_time_iterative
from abmodel.agent.disease import hospitalization_vectorized
from abmodel.agent.disease import diagnosis_function
from abmodel.agent.disease import isolation_function
from abmodel.agent.disease import isolation_handler
from abmodel.agent.disease import init_immunization_params_iterative
from abmodel.agent.disease import transition_function
from abmodel.models.disease import DiseaseStates, NaturalHistory
from abmodel.models.disease import IsolationAdherenceGroups
from abmodel.models.disease import ImmunizationGroups
from abmodel.models import HealthSystem
from abmodel.utils.execution_modes import ExecutionModes
from abmodel.models.mobility_restrictions import InterestVariables
from abmodel.models.mobility_restrictions import MRTracingPolicies
from abmodel.models.mobility_restrictions import MRTStopModes
from abmodel.models.mobility_restrictions import MRTimeUnits
from abmodel.models.mobility_restrictions import CyclicMRPolicies
from abmodel.models.mobility_restrictions import GlobalCyclicMR
from abmodel.models.mobility_restrictions import CyclicMRModes
from abmodel.models.disease import MRAdherenceGroups
from abmodel.models.base import SimpleGroups


class TestAgentDisease:
    """Unitary tests for AgentDisease class from disease module"""
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    # ========================================================================
    # Fixtures
    # ========================================================================

    @pytest.fixture()
    def fixture_generate_key_col_iterative(self) -> tuple[DataFrame, str]:
        vulnerability_groups = [
            "vulnerable",
            "vulnerable",
            "not_vulnerable"
            ]
        disease_state = [
            "susceptible",
            "susceptible",
            "immune"
            ]
        data = {
            "vulnerability_group": vulnerability_groups,
            "disease_state": disease_state
            }
        df = DataFrame(data)
        expected = [
            vulnerability_groups + '-' + disease_state for (
                vulnerability_groups,
                disease_state
            ) in zip(vulnerability_groups, disease_state)
        ]
        return df, expected

    @pytest.fixture()
    def fixture_init_required_fields(
        self
    ) -> tuple[NaturalHistory, DiseaseStates]:
        dist_title_natural_history = [
            "time_dist", "alertness_prob"
            ]
        group_info_natural_history = [
                {
                    "vulnerability_group": "not_vulnerable",
                    "disease_group": "susceptible",
                    "avoidance_radius": 2.0,
                    "avoidance_radius_unit": "meters",
                    "transition_by_contagion": True,
                    "transitions": [
                        {
                            "transition_name": "latency",
                            "probability": 1.0,
                            "immunization_gain": 0.0,

                            "dist_info": {
                                "dist_title": "immunization_time_distribution",
                                "dist_type": None,
                                "constant": None,
                                "dist_name": None,
                                "filename": None,
                                "data": None,
                                "kwargs": {}
                            }
                        }
                    ],
                    "dist_info": [
                        {
                            "dist_title": "time_dist",
                            "dist_type": None,
                            "constant": None,
                            "dist_name": None,
                            "filename": None,
                            "data": None,
                            "kwargs": {}
                        },
                        {
                            "dist_title": "alertness_prob",
                            "dist_type": "constant",
                            "constant": 1.0,
                            "dist_name": None,
                            "filename": None,
                            "data": None,
                            "kwargs": {}
                        }

                    ]
                },
                {
                    "vulnerability_group": "vulnerable",
                    "disease_group": "susceptible",
                    "avoidance_radius": 4.0,
                    "avoidance_radius_unit": "meters",
                    "transition_by_contagion": True,
                    "transitions": [
                        {
                            "transition_name": "latency",
                            "probability": 1.0,
                            "immunization_gain": 0.0,

                            "dist_info": {
                                "dist_title": "immunization_time_distribution",
                                "dist_type": None,
                                "constant": None,
                                "dist_name": None,
                                "filename": None,
                                "data": None,
                                "kwargs": {}
                            }
                        },
                        {
                            "transition_name": "dead",
                            "probability": 0.6,
                            "immunization_gain": 0.0,

                            "dist_info": {
                                "dist_title": "immunization_time_distribution",
                                "dist_type": None,
                                "constant": None,
                                "dist_name": None,
                                "filename": None,
                                "data": None,
                                "kwargs": {}
                            }
                        }
                    ],
                    "dist_info": [
                        {
                            "dist_title": "time_dist",
                            "dist_type": "constant",
                            "constant": 10,
                            "dist_name": None,
                            "filename": None,
                            "data": None,
                            "kwargs": None
                        },
                    ]
                }
            ]
        dist_title_disease_groups = [
            "diagnosis_prob", "isolation_days",
            "hospitalization_prob", "ICU_prob"
        ]
        group_info_disease_groups = [
            {
                "name": "susceptible",
                "can_get_infected": True,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "isolation_days",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "hospitalization_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "immune",
                "can_get_infected": False,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "isolation_days",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "hospitalization_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
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
                        "dist_title": "diagnosis_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "isolation_days",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "hospitalization_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            }
        ]
        natural_history = NaturalHistory(
            dist_title=dist_title_natural_history,
            group_info=group_info_natural_history
            )
        disease_groups = DiseaseStates(
            dist_title=dist_title_disease_groups,
            group_info=group_info_disease_groups
            )

        cols = ["disease_state"]
        check_cols = ["disease_state"]
        error_string = "df must contain: " + ", ".join(cols) + ".\n"
        check_string = ", ".join(check_cols) + " must be checked"
        pytest.error_init_is_dead = error_string + check_string

        cols = [
                "disease_state_max_time",
                "disease_state_time",
                "key",
                "do_calculate_max_time"
        ]
        check_cols = ["disease_state_max_time", "disease_state_time"]
        error_string = "df must contain: " + ", ".join(cols) + ".\n"
        check_string = ", ".join(check_cols) + " must be checked"
        pytest.error_determine_disease_state_max_time = (
            error_string + check_string
            )

        cols = ["key"]
        check_cols = ["key"]
        error_string = "df must contain: " + ", ".join(cols) + ".\n"
        check_string = ", ".join(check_cols) + " must be checked"
        pytest.error_init_disease_state_max_time = (
            error_string + check_string
            )

        return natural_history, disease_groups

    @pytest.fixture()
    def fixture_hospitalization_vectorized(
        self
    ) -> tuple[dict, dict, dict, dict, dict]:
        dist_title_disease_groups = [
            "hospitalization_prob", "ICU_prob"
        ]
        group_info_disease_groups_None = [
            {
                "name": "susceptible",
                "can_get_infected": True,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "hospitalization_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "immune",
                "can_get_infected": False,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "hospitalization_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
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
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            }
        ]
        group_info_disease_groups_ICU_prob_equals_one = [
            {
                "name": "susceptible",
                "can_get_infected": True,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "hospitalization_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": "constant",
                        "constant": 1,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
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
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            }
        ]
        group_info_disease_groups_hospitalization_prob_one = [
            {
                "name": "susceptible",
                "can_get_infected": True,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "hospitalization_prob",
                        "dist_type": "constant",
                        "constant": 1,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
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
                        "dist_type": "constant",
                        "constant": 1,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "ICU_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            }
        ]
        disease_groups_ICU_hospitalize_dist_None = DiseaseStates(
            dist_title=dist_title_disease_groups,
            group_info=group_info_disease_groups_None
            )
        disease_groups_ICU_dist_constant_one = DiseaseStates(
            dist_title=dist_title_disease_groups,
            group_info=group_info_disease_groups_ICU_prob_equals_one
            )
        disease_groups_hospitalization_prob_equals_one = DiseaseStates(
            dist_title=dist_title_disease_groups,
            group_info=group_info_disease_groups_hospitalization_prob_one
            )
        kwargs_ICU_and_hospitalize_dist_None = {
            "disease_groups": disease_groups_ICU_hospitalize_dist_None,
            "is_hospitalized": Series([True, True, False, True, False]),
            "is_in_ICU": Series([True, True, False, False, False]),
            "disease_states": Series(
                ["immune", "susceptible", "dead", "susceptible", "immune"]
            ),
            "is_dead": Series([False, False, True, False, False]),
            "alpha": 0.3,
            "dead_disease_group": "dead",
            "reduction_factor": Series([0.8, 0.7, 0.6, 0.9, 0.2]),
            "health_system": HealthSystem(
                hospital_capacity=10,
                ICU_capacity=10
            )
        }
        kwargs_ICU_dist_constant_one = {
            "disease_groups": disease_groups_ICU_dist_constant_one,
            "is_hospitalized": Series([True, False, False, True, False]),
            "is_in_ICU": Series([True, False, False, False, False]),
            "disease_states": Series(["susceptible" for agent in range(5)]),
            "reduction_factor": Series([0.8, 0.7, 0.6, 0.9, 0.2]),
            "is_dead": Series([False, False, False, False, False]),
            "dead_disease_group": "dead",
            "alpha": 0.3,
            "health_system": HealthSystem(
                hospital_capacity=10,
                ICU_capacity=10
            )
        }
        kwargs_ICU_dist_constant_one_ICU_capacity_0 = {
            "disease_groups": disease_groups_ICU_dist_constant_one,
            "is_hospitalized": Series([True, False, True, True, False]),
            "is_in_ICU": Series([False, False, False, False, False]),
            "disease_states": Series(["susceptible" for agent in range(5)]),
            "reduction_factor": Series([0.8, 0.7, 0.6, 0.9, 0.2]),
            "is_dead": Series([False, False, False, False, False]),
            "dead_disease_group": "dead",
            "alpha": 0.3,
            "health_system": HealthSystem(
                hospital_capacity=10,
                ICU_capacity=0
            )
        }
        kwargs_hospitalization_dist_onstant_one_hospital_capacity_0 = {
            "disease_groups": disease_groups_hospitalization_prob_equals_one,
            "is_hospitalized": Series([True, False, True, True, False]),
            "is_in_ICU": Series([False, False, False, False, False]),
            "disease_states": Series(["susceptible" for agent in range(5)]),
            "reduction_factor": Series([0.8, 0.7, 0.6, 0.9, 0.2]),
            "is_dead": Series([False, False, False, False, False]),
            "dead_disease_group": "dead",
            "alpha": 0.3,
            "health_system": HealthSystem(
                hospital_capacity=0,
                ICU_capacity=0
            )
        }
        kwargs_hospitalization_dist_onstant_one = {
            "disease_groups": disease_groups_hospitalization_prob_equals_one,
            "is_hospitalized": Series([False, False, True, False, False]),
            "is_in_ICU": Series([False, False, False, False, False]),
            "disease_states": Series(["susceptible" for agent in range(5)]),
            "reduction_factor": Series([0.8, 0.7, 0.6, 0.9, 0.2]),
            "is_dead": Series([False, False, False, False, False]),
            "dead_disease_group": "dead",
            "alpha": 0.3,
            "health_system": HealthSystem(
                hospital_capacity=2,
                ICU_capacity=0
            )
        }

        kwargs_tuple = (
            kwargs_ICU_and_hospitalize_dist_None,
            kwargs_ICU_dist_constant_one,
            kwargs_ICU_dist_constant_one_ICU_capacity_0,
            kwargs_hospitalization_dist_onstant_one_hospital_capacity_0,
            kwargs_hospitalization_dist_onstant_one
        )

        return kwargs_tuple

    @pytest.fixture()
    def fixture_diagnosis_function(self) -> tuple[DiseaseStates, dict]:
        dist_title_disease_groups = [
            "diagnosis_prob"
        ]
        group_info_disease_groups = [
            {
                "name": "susceptible",
                "can_get_infected": True,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": "constant",
                        "constant": 0,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "immune",
                "can_get_infected": False,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "infectious",
                "can_get_infected": False,
                "is_infected": True,
                "can_spread": True,
                "spread_radius": 3.0,
                "spread_radius_unit": "meters",
                "spread_probability": 0.6,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": "constant",
                        "constant": 0.0,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "hospital",
                "can_get_infected": False,
                "is_infected": True,
                "can_spread": True,
                "spread_radius": 4.0,
                "spread_radius_unit": "meters",
                "spread_probability": 0.8,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": "constant",
                        "constant": 1.0,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
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
                        "dist_title": "diagnosis_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            }
        ]
        disease_groups = DiseaseStates(
            dist_title=dist_title_disease_groups,
            group_info=group_info_disease_groups
            )
        data_dict = {
            "disease_state": Series(
                [
                    "susceptible",
                    "dead",
                    "hospital",
                    "infectious"

                ]
            ),
            "is_dead": Series([False, True, False, False]),
            "is_diagnosed": Series([False, False, False, True]),
        }

        return disease_groups, data_dict

    @pytest.fixture()
    def fixture_to_isolate_agents(
        self
    ) -> tuple[DiseaseStates, dict, dict, dict, dict, dict, dict]:
        dist_title_disease_groups = [
            "isolation_days"
        ]
        group_info_disease_groups = [
            {
                "name": "susceptible",
                "can_get_infected": True,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "isolation_days",
                        "dist_type": "constant",
                        "constant": 0,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "immune",
                "can_get_infected": False,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "isolation_days",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "infectious",
                "can_get_infected": False,
                "is_infected": True,
                "can_spread": True,
                "spread_radius": 3.0,
                "spread_radius_unit": "meters",
                "spread_probability": 0.6,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "isolation_days",
                        "dist_type": "constant",
                        "constant": 10.0,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "hospital",
                "can_get_infected": False,
                "is_infected": True,
                "can_spread": True,
                "spread_radius": 4.0,
                "spread_radius_unit": "meters",
                "spread_probability": 0.8,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "isolation_days",
                        "dist_type": "constant",
                        "constant": 0.0,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
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
                        "dist_title": "isolation_days",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            }
        ]
        disease_groups = DiseaseStates(
            dist_title=dist_title_disease_groups,
            group_info=group_info_disease_groups
        )
        dist_title_isolation_adherence = "adherence_prob"
        group_info_isolation_adherence = [
            {
                "name": "adherence_1",
                "dist_info": {
                    "dist_title": "adherence_prob",
                    "dist_type": "constant",
                    "constant": 1,
                    "dist_name": None,
                    "filename": None,
                    "data": None,
                    "kwargs": {}
                }
            },
            {
                "name": "adherence_2",
                "dist_info": {
                    "dist_title": "adherence_prob",
                    "dist_type": "constant",
                    "constant": 0.0,
                    "dist_name": None,
                    "filename": None,
                    "data": None,
                    "kwargs": {}
                }
            }
        ]
        isolation_adherence_groups = IsolationAdherenceGroups(
            dist_title=dist_title_isolation_adherence,
            group_info=group_info_isolation_adherence
        )
        kwargs_isolation_time_greater_isolation_max_time = {
            "disease_state": "immune",
            "isolation_adherence_group": "adherence_1",
            "is_diagnosed": True,
            "is_isolated": True,
            "isolation_time": 10,
            "isolation_max_time": 9,
            "adheres_to_isolation": True,
            "reduction_factor": 0.3,
            "beta": 0.8,
            "disease_groups": disease_groups
        }
        kwargs_isolation_time_less_isolation_max_time = {
            "disease_state": "immune",
            "isolation_adherence_group": "adherence_1",
            "is_diagnosed": True,
            "is_isolated": True,
            "isolation_time": 8,
            "isolation_max_time": 10,
            "adheres_to_isolation": True,
            "reduction_factor": 0.3,
            "beta": 0.8,
            "disease_groups": disease_groups
        }
        kwargs_isolation_adherence_groups_None = {
            "disease_state": "infectious",
            "isolation_adherence_group": "adherence_1",
            "is_diagnosed": True,
            "is_isolated": False,
            "isolation_time": 8,
            "isolation_max_time": 10,
            "adheres_to_isolation": False,
            "reduction_factor": 0.3,
            "beta": 0.8,
            "disease_groups": disease_groups
        }
        kwargs_isolation_adherence_prob_1 = {
            "disease_state": "infectious",
            "isolation_adherence_group": "adherence_1",
            "is_diagnosed": True,
            "is_isolated": False,
            "isolation_time": 8,
            "isolation_max_time": 10,
            "adheres_to_isolation": False,
            "reduction_factor": 0.3,
            "beta": 0.8,
            "disease_groups": disease_groups,
            "isolation_adherence_groups": isolation_adherence_groups
        }
        kwargs_isolation_dherence_prob_0 = {
            "disease_state": "susceptible",
            "isolation_adherence_group": "adherence_2",
            "is_diagnosed": True,
            "is_isolated": False,
            "isolation_time": 8,
            "isolation_max_time": 10,
            "adheres_to_isolation": True,
            "reduction_factor": 0.3,
            "beta": 0.8,
            "disease_groups": disease_groups,
            "isolation_adherence_groups": isolation_adherence_groups
        }
        data_dict = {
            "disease_state": ["susceptible", "infectious"],
            "isolation_adherence_group": ["adherence_2", "adherence_1"],
            "is_diagnosed": [True, True],
            "is_isolated": [False, False],
            "isolation_time": 8,
            "isolation_max_time": 10,
            "adheres_to_isolation": [True, False],
            "reduction_factor": 0.3,
            "beta": 0.8,
            "dt": 5,
            "disease_groups": disease_groups,
            "isolation_adherence_groups": isolation_adherence_groups
        }
        fixture_tuple = (
            disease_groups,
            kwargs_isolation_time_greater_isolation_max_time,
            kwargs_isolation_time_less_isolation_max_time,
            kwargs_isolation_adherence_groups_None,
            kwargs_isolation_adherence_prob_1,
            kwargs_isolation_dherence_prob_0,
            data_dict
        )

        return fixture_tuple

    @pytest.fixture()
    def fixture_init_times_infected(self) -> DiseaseStates:
        dist_title_disease_groups = [
            "diagnosis_prob", "isolation_days",
            "hospitalization_prob", "ICU_prob"
        ]
        group_info_disease_groups = [
            {
                "name": "susceptible",
                "can_get_infected": True,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "latency",
                "can_get_infected": False,
                "is_infected": True,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": "constant",
                        "constant": 0.3,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "immune",
                "can_get_infected": False,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "infectious",
                "can_get_infected": False,
                "is_infected": True,
                "can_spread": True,
                "spread_radius": 3.0,
                "spread_radius_unit": "meters",
                "spread_probability": 0.6,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": "constant",
                        "constant": 0.6,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "hospital",
                "can_get_infected": False,
                "is_infected": True,
                "can_spread": True,
                "spread_radius": 4.0,
                "spread_radius_unit": "meters",
                "spread_probability": 0.8,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": "constant",
                        "constant": 1.0,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
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
                        "dist_title": "diagnosis_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            }
        ]
        disease_groups = DiseaseStates(
            dist_title=dist_title_disease_groups,
            group_info=group_info_disease_groups
        )
        cols = ["disease_state"]
        check_cols = ["disease_state"]
        error_string = "df must contain: " + ", ".join(cols) + ".\n"
        check_string = ", ".join(check_cols) + " must be checked"
        pytest.error_init_times_infected_ValueError = (
            error_string + check_string
        )

        return disease_groups

    @pytest.fixture()
    def fixture_init_immunization(self) -> ImmunizationGroups:
        dist_title = [
            "immunization_level_dist",
            "immunization_time_distribution"
            ]
        group_info = [
            {
                "name": "not_immunized",
                "dist_info": [
                    {
                        "dist_title": "immunization_level_dist",
                        "dist_type": "constant",
                        "constant": 0.0,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "immunization_time_distribution",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                ]
            },
            {
                "name": "immunized",
                "dist_info": [
                    {
                        "dist_title": "immunization_level_dist",
                        "dist_type": "constant",
                        "constant": 1.0,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                    {
                        "dist_title": "immunization_time_distribution",
                        "dist_type": "constant",
                        "constant": 30,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                ]
            }
        ]

        immunization_groups = ImmunizationGroups(
            dist_title=dist_title,
            group_info=group_info
        )

        return immunization_groups

    @pytest.fixture()
    def fixture_transition_function(
        self
    ) -> tuple[NaturalHistory, DiseaseStates, dict]:
        dist_title_natural_history = ["time_dist"]
        group_info_natural_history = [
            {
                "vulnerability_group": "not_vulnerable",
                "disease_group": "susceptible",
                "avoidance_radius": 2.0,
                "avoidance_radius_unit": "meters",
                "transition_by_contagion": True,
                "transitions": [
                    {
                        "transition_name": "latency",
                        "probability": 1.0,
                        "immunization_gain": 0.0,
                        "dist_info": {
                            "dist_title": "immunization_time_distribution",
                            "dist_type": None,
                            "constant": None,
                            "dist_name": None,
                            "filename": None,
                            "data": None,
                            "kwargs": {}
                        }
                    }
                ],
                "dist_info": [
                    {
                        "dist_title": "time_dist",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                ]
            },
            {
                "vulnerability_group": "vulnerable",
                "disease_group": "latency",
                "avoidance_radius": 2.0,
                "avoidance_radius_unit": "meters",
                "transition_by_contagion": False,
                "transitions": [
                    {
                        "transition_name": "infectious",
                        "probability": 0.0,
                        "immunization_gain": 0.0,
                        "dist_info": {
                            "dist_title": "immunization_time_distribution",
                            "dist_type": None,
                            "constant": None,
                            "dist_name": None,
                            "filename": None,
                            "data": None,
                            "kwargs": {}
                        }
                    },
                    {
                        "transition_name": "immune",
                        "probability": 1.0,
                        "immunization_gain": 0.0,
                        "dist_info": {
                            "dist_title": "immunization_time_distribution",
                            "dist_type": None,
                            "constant": None,
                            "dist_name": None,
                            "filename": None,
                            "data": None,
                            "kwargs": {}
                        }
                    }
                ],
                "dist_info": [
                    {
                        "dist_title": "time_dist",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "vulnerability_group": "vulnerable",
                "disease_group": "infectious",
                "avoidance_radius": 2.0,
                "avoidance_radius_unit": "meters",
                "transition_by_contagion": True,
                "transitions": [
                    {
                        "transition_name": "dead",
                        "probability": 1.0,
                        "immunization_gain": 0.0,

                        "dist_info": {
                            "dist_title": "immunization_time_distribution",
                            "dist_type": None,
                            "constant": None,
                            "dist_name": None,
                            "filename": None,
                            "data": None,
                            "kwargs": {}
                        }
                    }
                ],
                "dist_info": [
                    {
                        "dist_title": "time_dist",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                ]
            }
        ]
        dist_title_disease_groups = [
            "diagnosis_prob", "isolation_days",
            "hospitalization_prob", "ICU_prob"
        ]
        group_info_disease_groups = [
            {
                "name": "susceptible",
                "can_get_infected": True,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    },
                ]
            },
            {
                "name": "immune",
                "can_get_infected": False,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "latency",
                "can_get_infected": False,
                "is_infected": True,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": "constant",
                        "constant": 0.3,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            },
            {
                "name": "immune",
                "can_get_infected": False,
                "is_infected": False,
                "can_spread": False,
                "spread_radius": None,
                "spread_radius_unit": None,
                "spread_probability": None,
                "is_dead": False,
                "dist_info": [
                    {
                        "dist_title": "diagnosis_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
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
                        "dist_title": "diagnosis_prob",
                        "dist_type": None,
                        "constant": None,
                        "dist_name": None,
                        "filename": None,
                        "data": None,
                        "kwargs": {}
                    }
                ]
            }
        ]
        natural_history = NaturalHistory(
            dist_title=dist_title_natural_history,
            group_info=group_info_natural_history
        )
        disease_groups = DiseaseStates(
            dist_title=dist_title_disease_groups,
            group_info=group_info_disease_groups
        )
        data_dict = {
            "disease_state": [
                "susceptible",
                "latency",
                "susceptible",
                "infectiuos"
            ],
            "disease_state_time": [10, 10, 1, 10],
            "disease_state_max_time": [5, 5, 5, 5],
            "is_dead": [False, False, False, False],
            "key": [
                "not_vulnerable-susceptible",
                "vulnerable-latency",
                "not_vulnerable-susceptible",
                "vulnerable-infectious"
            ],
            "immunization_level": [1, 1, 1, 1],
            "immunization_slope": [1.0, 1.0, 1.0, 1.0],
            "immunization_time": [0.0, 0.0, 0.0, 0.0],
            "immunization_max_time": [1.0, 1.0, 1.0, 1.0],
            "do_update_immunization_params": [False, False, False, False],
            "vulnerability_group": [
                "not_vulnerable",
                "vulnerable",
                "not_vulnerable",
                "vulnerable"
            ]
        }
        cols = [
                "disease_state",
                "disease_state_time",
                "is_dead",
                "key", "disease_state_max_time"
                ]
        check_cols = ["disease_state"]
        error_string = "df must contain: " + ", ".join(cols) + ".\n"
        check_string = ", ".join(check_cols) + " must be checked"
        pytest.error_disease_state_transition = (
            error_string + check_string
        )

        return natural_history, disease_groups, data_dict

    @pytest.fixture
    def fixture_apply_mobility_restrictions_tracing(
        self
    ) -> tuple[dict, MRTracingPolicies, MRTracingPolicies]:
        data_df = {
            "is_dead": [True, True],
            "agent": [1, 2],
            "mr_group": ["mr_group_1", "mr_group_2"],
            "mr_adherence_group": [
                "mr_adherence_group_1",
                "mr_adherence_group_1"
            ],
            "is_diagnosed": [True, True],
            "isolated_by_mr": [False, False],
            "adheres_to_mr_isolation": [True, True],
            "reduction_factor": [0.8, 0.8]
        }
        sm = SimpleGroups(names=["mr_group_1"])
        mrt_policies_level = MRTracingPolicies(
            variable=InterestVariables.dead,
            mr_start_level=1,
            mr_stop_mode=MRTStopModes.level_number,
            mr_stop_level=2,
            mr_length=None,
            mr_length_units=None,
            mr_groups=sm,
            target_groups=["mr_group_1"]
        )
        mrt_policies_lenght = MRTracingPolicies(
            variable=InterestVariables.dead,
            mr_start_level=10,
            mr_stop_mode=MRTStopModes.length,
            mr_length=1,
            mr_length_units=MRTimeUnits.days,
            mr_groups=sm,
            target_groups=["mr_group_1"]
        )

        return data_df, mrt_policies_level, mrt_policies_lenght

    @pytest.fixture
    def fixture_apply_mobility_restrictions_cyclic(
        self
    ) -> tuple[dict, CyclicMRPolicies, GlobalCyclicMR]:
        data_df = {
                "is_dead": [False, False],
                "agent": [1, 2],
                "mr_group": ["mr_group_1", "mr_group_1"],
                "mr_adherence_group": [
                    "mr_adherence_group_2",
                    "mr_adherence_group_1"
                ],
                "is_diagnosed": [True, True],
                "isolated_by_mr": [False, False],
                "adheres_to_mr_isolation": [True, True],
                "reduction_factor": [0.8, 0.8]
            }
        sm = SimpleGroups(names=["mr_group_1"])
        cyclic_policies_1 = CyclicMRPolicies(
            mr_groups=sm,
            target_group="mr_group_1",
            delay=1,
            delay_units=MRTimeUnits.days,
            mr_length=1,
            mr_length_units=MRTimeUnits.days,
            time_without_restrictions=1,
            time_without_restrictions_units=MRTimeUnits.days
        )
        global_cyclic_mr_1 = GlobalCyclicMR(
            enabled=True,
            grace_time=1,
            global_mr_length=1,
            global_mr_length_units=MRTimeUnits.days,
            unrestricted_time_mode=CyclicMRModes.fixed,
            unrestricted_time=1,
            unrestricted_time_units=MRTimeUnits.days
        )
        cyclic_policies_2 = CyclicMRPolicies(
            mr_groups=sm,
            target_group="mr_group_1",
            delay=0,
            delay_units=MRTimeUnits.days,
            mr_length=3,
            mr_length_units=MRTimeUnits.days,
            time_without_restrictions=2,
            time_without_restrictions_units=MRTimeUnits.days
        )
        global_cyclic_mr_2 = GlobalCyclicMR(
            enabled=True,
            grace_time=1,
            global_mr_length=8,
            global_mr_length_units=MRTimeUnits.days,
            unrestricted_time_mode=CyclicMRModes.fixed,
            unrestricted_time=3,
            unrestricted_time_units=MRTimeUnits.days
        )
        cyclic_policies_3 = CyclicMRPolicies(
            mr_groups=sm,
            target_group="mr_group_1",
            delay=0,
            delay_units=MRTimeUnits.days,
            mr_length=1,
            mr_length_units=MRTimeUnits.days,
            time_without_restrictions=2,
            time_without_restrictions_units=MRTimeUnits.days
        )
        global_cyclic_mr_3 = GlobalCyclicMR(
            enabled=True,
            grace_time=1,
            global_mr_length=8,
            global_mr_length_units=MRTimeUnits.days,
            unrestricted_time_mode=CyclicMRModes.fixed,
            unrestricted_time=4,
            unrestricted_time_units=MRTimeUnits.days
        )
        cyclic_policies_4 = CyclicMRPolicies(
            mr_groups=sm,
            target_group="mr_group_1",
            delay=0,
            delay_units=MRTimeUnits.days,
            mr_length=1,
            mr_length_units=MRTimeUnits.days,
            time_without_restrictions=2,
            time_without_restrictions_units=MRTimeUnits.days
        )
        global_cyclic_mr_4 = GlobalCyclicMR(
            enabled=True,
            grace_time=1,
            global_mr_length=8,
            global_mr_length_units=MRTimeUnits.days,
            unrestricted_time_mode=CyclicMRModes.random,
            unrestricted_time_units=MRTimeUnits.days
        )
        cyclic_policies_5 = CyclicMRPolicies(
            mr_groups=sm,
            target_group="mr_group_1",
            delay=0,
            delay_units=MRTimeUnits.days,
            mr_length=2,
            mr_length_units=MRTimeUnits.days,
            time_without_restrictions=3,
            time_without_restrictions_units=MRTimeUnits.days
        )
        global_cyclic_mr_5 = GlobalCyclicMR(
            enabled=True,
            grace_time=1,
            global_mr_length=2,
            global_mr_length_units=MRTimeUnits.days,
            unrestricted_time=5,
            unrestricted_time_mode=CyclicMRModes.fixed,
            unrestricted_time_units=MRTimeUnits.days
        )
        cyclic_policies_6 = CyclicMRPolicies(
            mr_groups=sm,
            target_group="mr_group_1",
            delay=0,
            delay_units=MRTimeUnits.days,
            mr_length=1,
            mr_length_units=MRTimeUnits.days,
            time_without_restrictions=1,
            time_without_restrictions_units=MRTimeUnits.days
        )
        global_cyclic_mr_6 = GlobalCyclicMR(
            enabled=True,
            grace_time=0,
            global_mr_length=2,
            global_mr_length_units=MRTimeUnits.days,
            unrestricted_time_mode=CyclicMRModes.random,
            unrestricted_time_units=MRTimeUnits.days
        )
        cyclic_policies_7 = CyclicMRPolicies(
            mr_groups=sm,
            target_group="mr_group_1",
            delay=0,
            delay_units=MRTimeUnits.days,
            mr_length=1,
            mr_length_units=MRTimeUnits.days,
            time_without_restrictions=1,
            time_without_restrictions_units=MRTimeUnits.days
        )
        global_cyclic_mr_7 = GlobalCyclicMR(
            enabled=True,
            grace_time=0,
            global_mr_length=3,
            global_mr_length_units=MRTimeUnits.days,
            unrestricted_time_mode=CyclicMRModes.random,
            unrestricted_time_units=MRTimeUnits.days
        )
        fixture_tuple = (
            data_df,
            cyclic_policies_1,
            global_cyclic_mr_1,
            cyclic_policies_2,
            global_cyclic_mr_2,
            cyclic_policies_3,
            global_cyclic_mr_3,
            cyclic_policies_4,
            global_cyclic_mr_4,
            cyclic_policies_5,
            global_cyclic_mr_5,
            cyclic_policies_6,
            global_cyclic_mr_6,
            cyclic_policies_7,
            global_cyclic_mr_7
        )

        return fixture_tuple

    # ========================================================================
    # Tests
    # ========================================================================

    def test_init_is_dead(
        self,
        fixture_init_required_fields
    ):
        """
            verifies whether init_is_dead assigns
            correctly values to is_dead column.
        """

        df = DataFrame({"disease_state": ["susceptible", "dead", "immune"]})
        disease_groups = fixture_init_required_fields[1]
        df = AgentDisease.init_is_dead(
            df,
            disease_groups
            )

        expected = [False, True, False]

        assert all(df["is_dead"].eq(expected))

    def test_init_is_dead_dask(
        self,
        fixture_init_required_fields
    ):
        """
            verifies whether init_is_dead assigns correctly values to
            is_dead column when `ExecutionModes` is equals to dask.
        """

        df = DataFrame({"disease_state": ["susceptible", "dead", "immune"]})
        disease_groups = fixture_init_required_fields[1]
        df = AgentDisease.init_is_dead(
            df,
            disease_groups,
            execmode=ExecutionModes.dask.value
        )

        expected = [False, True, False]
        assert all(df["is_dead"].eq(expected))

    def test_init_is_dead_raise_NotImplementedError(
        self,
        fixture_init_required_fields
    ):
        """
            Raises a NotImplementedError when execmode
            is different to `ExecutionModes.iterative.value`.
        """
        df = DataFrame({"disease_state": ["susceptible", "dead", "immune"]})
        disease_groups = fixture_init_required_fields[1]

        with pytest.raises(TypeError, match="NotImplementedError"):
            AgentDisease.init_is_dead(
                df,
                disease_groups,
                ExecutionModes.vectorized.value
            )

    def test_init_is_dead_raise_ValueError(
        self,
        fixture_init_required_fields
    ):
        """
            Raises a ValueError when `disease_state`
            column is not in the input DataFrame.
        """

        df = DataFrame({"disease": ["susceptible", "dead", "immune"]})
        disease_groups = fixture_init_required_fields[1]

        with pytest.raises(ValueError, match=pytest.error_init_is_dead):
            AgentDisease.init_is_dead(
                df,
                disease_groups
            )

    def test_generate_key_col_iterative(
        self,
        fixture_generate_key_col_iterative
    ):
        """
            Verifies whether the column `key` is created on the input
            DataFrame and assigns correctly values in iterative mode.
        """
        df = AgentDisease.generate_key_col(
            df=fixture_generate_key_col_iterative[0]
            )
        expected = fixture_generate_key_col_iterative[1]

        assert all(df["key"].eq(expected))

    def test_generate_key_col_dask(
        self,
        fixture_generate_key_col_iterative
    ):
        """
            Verifies whether the column `key` is created on the input
            DataFrame and assigns correctly values in dask mode.
        """
        df = AgentDisease.generate_key_col(
            df=fixture_generate_key_col_iterative[0],
            execmode=ExecutionModes.dask.value
        )
        expected = fixture_generate_key_col_iterative[1]

        assert all(df["key"].eq(expected))

    def test_generate_key_col_vectorized(
        self,
        fixture_generate_key_col_iterative
    ):
        """
            Verifies whether the column `key` is created on the input
            DataFrame and assigns correct values in vectorized mode.
        """
        df = AgentDisease.generate_key_col(
            df=fixture_generate_key_col_iterative[0],
            execmode=ExecutionModes.vectorized.value
            )
        expected = fixture_generate_key_col_iterative[1]

        assert all(df["key"].eq(expected))

    def test_generate_key_col_raise_Exception_error(
        self,
        fixture_generate_key_col_iterative
    ):
        """
            Raises a ValueError when one of the columns: `disease_state` or
            `vulnerability_group` is not a column of the input DataFrame
        """
        fixture_generate_key_col_iterative[0].pop("disease_state")
        error_message = (
            "df must contain: disease_state, vulnerability_group.\n"
            "disease_state must be checked"
            )

        with pytest.raises(ValueError, match=error_message):
            AgentDisease.generate_key_col(
                df=fixture_generate_key_col_iterative[0],
                execmode=ExecutionModes.vectorized.value
            )

    def test_generate_key_col_raise_NotImplementedError(
        self,
        fixture_generate_key_col_iterative
    ):
        """
            Raises a NotImplementedError when execmode is
            different from `ExecutionModes.iterative.value`
            or `ExecutionModes.vectorized.value`.
        """
        with pytest.raises(TypeError, match="NotImplementedError"):
            AgentDisease.generate_key_col(
                df=fixture_generate_key_col_iterative[0],
                execmode=ExecutionModes
            )

    def test_init_calculate_max_time_iterative_False(
        self,
        fixture_init_required_fields
    ):
        """
            Verifies whether init_calculate_max_time_iterative
            returns a correct boolean value when time_dist
            is a None type distribution.
        """
        natural_history = fixture_init_required_fields[0]

        value = init_calculate_max_time_iterative(
            key="not_vulnerable-susceptible",
            natural_history=natural_history
            )

        assert value == False

    def test_init_calculate_max_time_iterative_True(
        self,
        fixture_init_required_fields
    ):
        """
            Verifies whether init_calculate_max_time_iterative
            returns a correct boolean value when time_dist
            is different from a None type distribution.
        """
        natural_history = fixture_init_required_fields[0]

        value = init_calculate_max_time_iterative(
            key="vulnerable-susceptible",
            natural_history=natural_history
            )

        assert value == True

    def test_init_calculate_max_time_vectorized(
        self,
        fixture_init_required_fields
    ):
        """
            Verifies whether init_calculate_max_time_vectorized
            returns a correct boolean list.
        """
        natural_history = fixture_init_required_fields[0]

        value = init_calculate_max_time_vectorized(
            key=Series(
                ["not_vulnerable-susceptible", "vulnerable-susceptible"]
            ),
            natural_history=natural_history
        )

        assert value == [False, True]

    def test_calculate_max_time_iterative_dead(
        self,
        fixture_init_required_fields
    ):
        """
            Verifies whether calculate_max_time_iterative
            returns a Series with nan values when disease_state
            provided is `dead`.
        """
        natural_history = fixture_init_required_fields[1]
        disease_groups = fixture_init_required_fields[1]

        s = calculate_max_time_iterative(
            key="vulnerable-susceptible",
            disease_state="dead",
            do_calculate_max_time=True,
            disease_state_time=None,
            disease_state_max_time=None,
            disease_groups=disease_groups,
            natural_history=natural_history
        )

        assert all([isnan(value) for value in s])

    def test_calculate_max_time_iterative_calculate_True(
        self,
        fixture_init_required_fields
    ):
        """
            Verifies whether calculate_max_time_iterative
            returns a Series with nan values when disease_state
            provided is `dead`.
        """
        natural_history = fixture_init_required_fields[0]
        disease_groups = fixture_init_required_fields[1]

        s = calculate_max_time_iterative(
            key="vulnerable-susceptible",
            disease_state="immune",
            do_calculate_max_time=True,
            disease_state_time=None,
            disease_state_max_time=None,
            disease_groups=disease_groups,
            natural_history=natural_history
        )

        assert all(s.eq([0, 10]))

    def test_calculate_max_time_iterative_calculate_False(
        self,
        fixture_init_required_fields
    ):
        """
            Verifies whether calculate_max_time_iterative
            returns a Series with nan values when disease_state
            provided is `dead`.
        """
        natural_history = fixture_init_required_fields[0]
        disease_groups = fixture_init_required_fields[1]

        s = calculate_max_time_iterative(
            key="vulnerable-susceptible",
            disease_state="immune",
            do_calculate_max_time=False,
            disease_state_time=5,
            disease_state_max_time=10,
            disease_groups=disease_groups,
            natural_history=natural_history
        )

        assert all(s.eq([5, 10]))

    def test_determine_disease_state_max_time(
        self,
        fixture_init_required_fields
    ):
        """
            Verifies whether determine_disease_state_max_time
            creates correctly `disease_state_time` and
            `disease_state_max_time` columns correctly and sets to
            False in `do_calculate_max_time` for all agents.
        """
        natural_history = fixture_init_required_fields[0]
        disease_groups = fixture_init_required_fields[1]

        df = DataFrame(
            {
                "key": [
                    "not_vulnerable-susceptible",
                    "vulnerable-susceptible"
                ],
                "disease_state": ["susceptible", "susceptible"],
                "do_calculate_max_time": [False, True],
                "disease_state_time": [None, None],
                "disease_state_max_time": [None, None]
            }
        )

        df = AgentDisease.determine_disease_state_max_time(
            df=df,
            disease_groups=disease_groups,
            natural_history=natural_history,
        )

        assert isnan(df["disease_state_time"][0])
        assert df["disease_state_time"][1] == 0
        assert isnan(df["disease_state_max_time"][0])
        assert df["disease_state_max_time"][1] == 10
        assert all(df["do_calculate_max_time"].eq([False, False]))

    def test_determine_disease_state_max_time_raise_NotImplementedError(
        self,
        fixture_init_required_fields
    ):
        """
            Verifies whether determine_disease_state_max_time
            raises a NotImplementedError when the `execmode` is
            not implemented yet.
        """
        natural_history = fixture_init_required_fields[0]
        disease_groups = fixture_init_required_fields[1]

        df = DataFrame(
            {
                "key": [
                    "not_vulnerable-susceptible",
                    "vulnerable-susceptible"
                ],
                "disease_state": ["susceptible", "susceptible"],
                "do_calculate_max_time": [False, True],
                "disease_state_time": [None, None],
                "disease_state_max_time": [None, None]
            }
        )

        with pytest.raises(TypeError, match="NotImplementedError"):
            AgentDisease.determine_disease_state_max_time(
                df=df,
                disease_groups=disease_groups,
                natural_history=natural_history,
                execmode=ExecutionModes.vectorized.value
            )

    def test_init_disease_state_max_time_iterative(
        self,
        fixture_init_required_fields
    ):
        """
            Verifies whether determine_disease_state_max_time
            raises a NotImplementedError when the `execmode` is
            not implemented yet.
        """
        natural_history = fixture_init_required_fields[0]
        disease_groups = fixture_init_required_fields[1]

        df = DataFrame(
            {
                "key": [
                    "not_vulnerable-susceptible",
                    "vulnerable-susceptible"
                ],
                "disease_state": ["susceptible", "susceptible"],
                "disease_state_time": [None, None],
                "disease_state_max_time": [None, None]
            }
        )

        df = AgentDisease.init_disease_state_max_time(
            df=df,
            disease_groups=disease_groups,
            natural_history=natural_history
        )

        assert all(df["do_calculate_max_time"].eq([False, False]))
        assert isnan(df["disease_state_time"][0])
        assert df["disease_state_time"][1] == 0
        assert isnan(df["disease_state_max_time"][0])
        assert df["disease_state_max_time"][1] == 10
        assert all(df["do_calculate_max_time"].eq([False, False]))

    def test_init_disease_state_max_time_raise_Exception_error(
        self,
        fixture_init_required_fields
    ):
        """
            Verifies whether determine_disease_state_max_time
            raises a NotImplementedError when the `execmode` is
            different from `ExecutionModes.iterative.value`.
        """
        natural_history = fixture_init_required_fields[0]
        disease_groups = fixture_init_required_fields[1]

        df = DataFrame(
            {
                "disease_state": ["susceptible", "susceptible"],
                "disease_state_time": [None, None],
                "disease_state_max_time": [None, None]
            }
        )

        with pytest.raises(
            Exception,
            match=pytest.error_init_disease_state_max_time
        ):
            AgentDisease.init_disease_state_max_time(
                df=df,
                disease_groups=disease_groups,
                natural_history=natural_history,
                execmode=ExecutionModes.vectorized.value
            )

    def test_hospitalization_vectorized_ICU_and_hospitalization_prob_is_None(
        self,
        fixture_hospitalization_vectorized
    ):
        """
            No agents hospitilized neither in ICU when `ICU_prob` and
            `hospitalization_prob` distributions are set to None,
            furthermore there is no changes in `is_dead` Series.
        """
        kwargs = fixture_hospitalization_vectorized[0]

        df = hospitalization_vectorized(**kwargs)
        expected_is_hospitalized = Series([False for agent in df[0]])
        expected_is_in_ICU = Series([False for value in df[0]])

        assert all(df[0].eq(expected_is_hospitalized))
        assert all(df[1].eq(expected_is_in_ICU))
        assert all(df[2].eq(kwargs["disease_states"]))
        assert all(df[3].eq(kwargs["is_dead"]))

    def test_hospitalization_vectorized_ICU_prob_is_one(
        self,
        fixture_hospitalization_vectorized
    ):
        """
            All agents have `ICU_prob` equal to one, then, everyone must
            be in ICU, and therefore hospitalized. No one is dead.
        """
        kwargs = fixture_hospitalization_vectorized[1]

        df = hospitalization_vectorized(**kwargs)
        expected_is_in_ICU = Series([True for agent in df[0]])
        expected_is_hospitalized = expected_is_in_ICU

        assert all(df[0].eq(expected_is_hospitalized))
        assert all(df[1].eq(expected_is_in_ICU))
        assert all(df[3].eq(kwargs["is_dead"]))

    def test_hospitalization_vectorized_ICU_prob_one_and_ICU_capacity_cero(
        self,
        fixture_hospitalization_vectorized
    ):
        """
            All agents have `ICU_prob` equal to one, but
            ICU_capacity is set to zero, then no one must
            be in ICU, and everyone must is dead.
        """
        kwargs = fixture_hospitalization_vectorized[2]

        df = hospitalization_vectorized(**kwargs)
        expected_is_in_ICU = Series([False for agent in df[0]])
        expected_is_dead = Series([True for agent in df[3]])
        expected_disease_states = Series(["dead" for agent in df[0]])

        assert all(df[1].eq(expected_is_in_ICU))
        assert all(df[2].eq(expected_disease_states))
        assert all(df[3].eq(expected_is_dead))

    def test_hospitalization_vectorized_hospital_all_agent_must_died(
        self,
        fixture_hospitalization_vectorized
    ):
        """
            Everyone is dead when `hospital_capacity` is set to cero
            and hospitalization prob of the disease group is one.
        """
        kwargs = fixture_hospitalization_vectorized[3]

        df = hospitalization_vectorized(**kwargs)
        expected_is_in_ICU = Series([False for agent in df[0]])
        expected_is_hospitalized = expected_is_in_ICU
        expected_is_dead = Series([True for agent in df[0]])

        assert all(df[0] == expected_is_hospitalized)
        assert all(df[1] == expected_is_in_ICU)
        assert all(df[3] == expected_is_dead)

    def test_hospitalization_vectorized_hospital_capacity_is_cero(
        self,
        fixture_hospitalization_vectorized
    ):
        """
           Two agents must be died when `hospital_capacity`
           is three and five agents in the same disease group
           has `hospitalization_prob` equals to one.
        """
        kwargs = fixture_hospitalization_vectorized[4]

        df = hospitalization_vectorized(**kwargs)
        is_hospitalized = df[df[0] == True]
        expected_is_in_ICU = kwargs["is_in_ICU"]
        is_dead = df[df[3] == True]

        assert len(is_hospitalized) == 2
        assert all(df[1].eq(expected_is_in_ICU))
        assert len(is_dead) == 3

    def test_to_hospitalize_agents(
        self,
        fixture_hospitalization_vectorized
    ):
        """
            Verifies whether to_hospitalize_agents modyfies correctly
            the respective columns values for each agent.
        """
        data_dict = fixture_hospitalization_vectorized[0]
        health_system = data_dict.pop("health_system")
        alpha = data_dict.pop("alpha")
        dead_disease_group = data_dict.pop("dead_disease_group")
        disease_groups = data_dict.pop("disease_groups")

        df = DataFrame(data_dict)
        df["disease_state"] = df["disease_states"]
        df.pop("disease_states")

        df = AgentDisease.to_hospitalize_agents(
            df=df,
            dead_disease_group=dead_disease_group,
            alpha=alpha,
            disease_groups=disease_groups,
            health_system=health_system
        )
        expected_is_hospitalized = Series(
            [False for agent in df["is_hospitalized"]]
        )
        expected_is_in_ICU = Series([False for value in df["is_in_ICU"]])

        assert all(df["is_hospitalized"].eq(expected_is_hospitalized))
        assert all(df["is_in_ICU"].eq(expected_is_in_ICU))
        assert all(df["disease_state"].eq(data_dict["disease_states"]))
        assert all(df["is_dead"].eq(data_dict["is_dead"]))

    def test_to_hospitalize_agents_raise_Exception_error(
        self,
        fixture_hospitalization_vectorized
    ):
        """
            Raises a ValueError when when some fundamental
            columns (`disease_state` in this case) is not
            in the input DataFrame.
        """
        data_dict = fixture_hospitalization_vectorized[0]
        health_system = data_dict.pop("health_system")
        alpha = data_dict.pop("alpha")
        dead_disease_group = data_dict.pop("dead_disease_group")
        disease_groups = data_dict.pop("disease_groups")

        df = DataFrame(data_dict)

        with pytest.raises(Exception, match="disease_state"):
            df = AgentDisease.to_hospitalize_agents(
                df=df,
                dead_disease_group=dead_disease_group,
                alpha=alpha,
                disease_groups=disease_groups,
                health_system=health_system
            )

    def test_to_hospitalize_agents_raise_NotImplementedError(
        self,
        fixture_hospitalization_vectorized
    ):
        """
            Raises NotImplementedError when when `execmode`
            is different from ExecutionModes.vectorized.value.
        """
        data_dict = fixture_hospitalization_vectorized[0]
        health_system = data_dict.pop("health_system")
        alpha = data_dict.pop("alpha")
        dead_disease_group = data_dict.pop("dead_disease_group")
        disease_groups = data_dict.pop("disease_groups")
        execmode = ExecutionModes.iterative.value

        df = DataFrame(data_dict)
        df["disease_state"] = df["disease_states"]
        df.pop("disease_states")

        with pytest.raises(TypeError, match="NotImplementedError"):
            df = AgentDisease.to_hospitalize_agents(
                df=df,
                dead_disease_group=dead_disease_group,
                alpha=alpha,
                disease_groups=disease_groups,
                health_system=health_system,
                execmode=execmode
            )

    def test_diagnosis_function_agent_dead(
            self,
            fixture_diagnosis_function
    ):
        """
            Returns False when the agent is dead.
        """
        disease_groups = fixture_diagnosis_function[0]

        is_diagnosed = diagnosis_function(
            disease_state="dead",
            is_dead=True,
            is_diagnosed=True,
            disease_groups=disease_groups
        )

        assert is_diagnosed == False

    def test_diagnosis_functionis_diagnosed_True(
            self,
            fixture_diagnosis_function
    ):
        """
            Returns True when `is_diagnosed` is set to True for the agent.
        """
        disease_groups = fixture_diagnosis_function[0]

        is_diagnosed = diagnosis_function(
            disease_state="immune",
            is_dead=False,
            is_diagnosed=True,
            disease_groups=disease_groups
        )

        assert is_diagnosed

    def test_diagnosis_function_not_infected(
            self,
            fixture_diagnosis_function
    ):
        """
            Returns False when the agent is not infected
            and `is_diagnosed` is set to False.
        """
        disease_groups = fixture_diagnosis_function[0]

        is_diagnosed = diagnosis_function(
            disease_state="immune",
            is_dead=False,
            is_diagnosed=False,
            disease_groups=disease_groups
            )

        assert is_diagnosed == False

    def test_diagnosis_function_diagnosis_prob_1(
            self,
            fixture_diagnosis_function
    ):
        """
            Returns True when the agent is infected, `is_diagnosed` is
            set to False and diagnosis_prob for his disease_state is
            a constant distribution with a constant equals to 1.
        """
        disease_groups = fixture_diagnosis_function[0]

        is_diagnosed = diagnosis_function(
            disease_state="hospital",
            is_dead=False,
            is_diagnosed=False,
            disease_groups=disease_groups
        )

        assert is_diagnosed

    def test_diagnosis_function_diagnosis_prob_0(
            self,
            fixture_diagnosis_function
    ):
        """
            Returns False when the agent is infected, `is_diagnosed` is
            set to False and diagnosis_prob for his disease_state is
            a constant distribution with a constant equals to 0.
        """
        disease_groups = fixture_diagnosis_function[0]

        is_diagnosed = diagnosis_function(
            disease_state="susceptible",
            is_dead=False,
            is_diagnosed=False,
            disease_groups=disease_groups
            )

        assert is_diagnosed == False

    def test_to_diagnose_agents_iterative(
            self,
            fixture_diagnosis_function
    ):
        """
            to_diagnose_agents modifies correctly the
            `is_diagnosed` column of the input DataFrame.
        """
        disease_groups = fixture_diagnosis_function[0]
        data_dict = fixture_diagnosis_function[1]
        df = DataFrame(data_dict)

        df = AgentDisease.to_diagnose_agents(
            df=df,
            disease_groups=disease_groups
        )
        expected = [False, False, True, True]

        assert all(df["is_diagnosed"].eq(expected))

    def test_to_diagnose_agents_dask(
            self,
            fixture_diagnosis_function
    ):
        """
            to_diagnose_agents modifies correctly the `is_diagnosed` column
            of the input DataFrame. Setting `ExecutionModes` equals to dask.
        """
        disease_groups = fixture_diagnosis_function[0]
        data_dict = fixture_diagnosis_function[1]
        df = DataFrame(data_dict)

        df = AgentDisease.to_diagnose_agents(
            df=df,
            disease_groups=disease_groups,
            execmode=ExecutionModes.dask.value
        )
        expected = [False, False, True, True]

        assert all(df["is_diagnosed"].eq(expected))

    def test_isolation_function_isolation_prob_1(
        self,
        fixture_to_isolate_agents
    ):
        """
            Verifies whether isolation_function returns a
            correct values when `isolation_days` dist is constant,
            with its constant equals to 1.
        """
        disease_groups = fixture_to_isolate_agents[0]

        output_tuple = isolation_function(
            "infectious",
            disease_groups
        )
        expected = (True, 0.0, 10.0)

        assert output_tuple == expected

    def test_isolation_function_isolation_prob_0(
        self,
        fixture_to_isolate_agents
    ):
        """
            Verifies whether isolation_function returns a
            correct values when `isolation_days` dist is constant,
            with its constant equals to 0.
        """
        disease_groups = fixture_to_isolate_agents[0]

        output_tuple = isolation_function(
            "hospital",
            disease_groups
        )
        expected = (True, 0.0, 0.0)

        assert output_tuple == expected

    def test_isolation_handler_is_diagnosed_False(
        self,
        fixture_to_isolate_agents
    ):
        """
            Verifies whether there is no changes
            when `is_diagnosed` is False.
        """
        kwargs = fixture_to_isolate_agents[1]
        kwargs["is_diagnosed"] = not kwargs["is_diagnosed"]

        s = isolation_handler(**kwargs)
        expected_s = Series([
            kwargs["is_diagnosed"],
            kwargs["is_isolated"],
            kwargs["isolation_time"],
            kwargs["isolation_max_time"],
            kwargs["adheres_to_isolation"],
            kwargs["reduction_factor"]
        ])

        assert all(s.eq(expected_s))

    def test_isolation_handler_isolation_time_greater_isolation_max_time(
        self,
        fixture_to_isolate_agents
    ):
        """
            Verifies whether isolation_handler returns correct
            values when `is_isolated` is True and `isolation_time`
            is greater than isolation_max_time.
        """
        kwargs = fixture_to_isolate_agents[1]

        s = isolation_handler(**kwargs)
        expected_s = Series([
            not kwargs["is_diagnosed"],
            not kwargs["is_isolated"],
            nan,
            nan,
            kwargs["adheres_to_isolation"],
            kwargs["reduction_factor"]/kwargs["beta"]
        ])

        assert s[0] == expected_s[0] and s[1] == expected_s[1]
        assert isnan(s[2]) and isnan(s[3])
        assert s[4] == expected_s[4] and s[5] == expected_s[5]

    def test_isolation_handler_isolation_time_less_isolation_max_time(
        self,
        fixture_to_isolate_agents
    ):
        """
            Verifies whether isolation_handler returns correct
            values when `is_isolated` is True and `isolation_time`
            is less than isolation_max_time.
        """
        kwargs = fixture_to_isolate_agents[2]

        s = isolation_handler(**kwargs)
        expected_s = Series([
            kwargs["is_diagnosed"],
            kwargs["is_isolated"],
            kwargs["isolation_time"],
            kwargs["isolation_max_time"],
            kwargs["adheres_to_isolation"],
            kwargs["reduction_factor"]
        ])

        assert all(s.eq(expected_s))

    def test_isolation_handler_isolation_adherence_groups_None(
        self,
        fixture_to_isolate_agents
    ):
        """
            Verifies whether isolation_handler returns
            correct values when `is_isolated` is False
            and `isolation_adherence_groups` is None.
        """
        kwargs = fixture_to_isolate_agents[3]

        s = isolation_handler(**kwargs)
        expected_s = Series([
            kwargs["is_diagnosed"],
            not kwargs["is_isolated"],
            0.0,
            10,
            not kwargs["adheres_to_isolation"],
            kwargs["reduction_factor"]*kwargs["beta"]
        ])

        assert all(s.eq(expected_s))

    def test_isolation_handler_adherence_prob_1(
        self,
        fixture_to_isolate_agents
    ):
        """
            Verifies whether isolation_handler returns correct values
            when `is_isolated` is False and the `isolation_adherence_groups`
            has a constant distribution with constant equals to 1.
        """
        kwargs = fixture_to_isolate_agents[4]

        s = isolation_handler(**kwargs)

        expected_s = Series([
            kwargs["is_diagnosed"],
            not kwargs["is_isolated"],
            0.0,
            10,
            not kwargs["adheres_to_isolation"],
            kwargs["reduction_factor"]*kwargs["beta"]
        ])

        assert all(s == expected_s)

    def test_isolation_handler_adherence_prob_0(
        self,
        fixture_to_isolate_agents
    ):
        """
            Verifies whether isolation_handler returns correct values
            when `is_isolated` is False and the `isolation_adherence_groups`
            has a constant distribution with constant equals to 0.
        """
        kwargs = fixture_to_isolate_agents[5]

        s = isolation_handler(**kwargs)
        expected_s = Series([
            kwargs["is_diagnosed"],
            kwargs["is_isolated"],
            kwargs["isolation_time"],
            kwargs["isolation_max_time"],
            not kwargs["adheres_to_isolation"],
            kwargs["reduction_factor"]
        ])

        assert all(s.eq(expected_s))

    def test_to_isolate_agents_iterative(
        self,
        fixture_to_isolate_agents
    ):
        """
            Verifies whether isolation_handler returns correct values
            when `is_isolated` is False the `isolation_adherence_groups`
            has a constant distribution with constant equals to 0 and
            `ExecutionModes` is equals to dask.
        """
        data_dict = fixture_to_isolate_agents[6]
        beta = data_dict.pop("beta")
        disease_groups = data_dict.pop("disease_groups")
        isolation_adherence_groups = data_dict.pop(
            "isolation_adherence_groups"
        )
        dt = data_dict.pop("dt")

        df = DataFrame(data_dict)
        df = AgentDisease.to_isolate_agents(
            df=df,
            dt=dt,
            beta=beta,
            disease_groups=disease_groups,
            isolation_adherence_groups=isolation_adherence_groups
        )
        expected_df = DataFrame(
            {
                "is_diagnosed": [True, True],
                "is_isolated": [True, False],
                "isolation_time": [0.0 + dt, 8 + dt],
                "isolation_max_time": [10, 10],
                "adheres_to_isolation": [True, False],
                "reduction_factor": [0.3*beta, 0.3]
            }
        )

        assert all(df.eq(expected_df))

    def test_to_isolate_agents_dask(
        self,
        fixture_to_isolate_agents
    ):
        """
            Verifies whether isolation_handler returns correct values
            when `is_isolated` is False, the `isolation_adherence_groups`
            has a constant distribution with constant equals to 0 and
            `ExecutionModes` is equals to dask.
        """
        data_dict = fixture_to_isolate_agents[6]
        beta = data_dict.pop("beta")
        disease_groups = data_dict.pop("disease_groups")
        isolation_adherence_groups = data_dict.pop(
            "isolation_adherence_groups"
        )
        dt = data_dict.pop("dt")

        df = DataFrame(data_dict)
        df = AgentDisease.to_isolate_agents(
            df=df,
            dt=dt,
            beta=beta,
            disease_groups=disease_groups,
            isolation_adherence_groups=isolation_adherence_groups,
            execmode=ExecutionModes.dask.value
        )
        expected_df = DataFrame(
            {
                "is_diagnosed": [True, True],
                "is_isolated": [True, False],
                "isolation_time": [0.0 + dt, 8 + dt],
                "isolation_max_time": [10, 10],
                "adheres_to_isolation": [True, False],
                "reduction_factor": [0.3*beta, 0.3]
            }
        )

        assert all(df.eq(expected_df))

    def test_to_isolate_agents_raise_NotImplementedError(
        self,
        fixture_to_isolate_agents
    ):
        """
            Verifies whether isolation_handler returns correct values
            when `is_isolated` is False the `isolation_adherence_groups`
            has a constant distribution with constant equals to 0.
        """
        data_dict = fixture_to_isolate_agents[6]
        beta = data_dict.pop("beta")
        disease_groups = data_dict.pop("disease_groups")
        isolation_adherence_groups = data_dict.pop(
            "isolation_adherence_groups"
        )
        dt = data_dict.pop("dt")

        df = DataFrame(data_dict)
        with pytest.raises(TypeError, match="NotImplementedError"):
            AgentDisease.to_isolate_agents(
                df=df,
                dt=dt,
                beta=beta,
                disease_groups=disease_groups,
                isolation_adherence_groups=isolation_adherence_groups,
                execmode=ExecutionModes.vectorized.value
            )

    def test_to_isolate_agents_raise_Exception_error(
        self,
        fixture_to_isolate_agents
    ):
        """
            Raises Exception as error when some fundamental columns
            (`disease_state` in this case) is not in the input DataFrame
        """
        data_dict = fixture_to_isolate_agents[6]
        beta = data_dict.pop("beta")
        disease_groups = data_dict.pop("disease_groups")
        isolation_adherence_groups = data_dict.pop(
            "isolation_adherence_groups"
        )
        dt = data_dict.pop("dt")
        data_dict.pop("disease_state")

        df = DataFrame(data_dict)
        with pytest.raises(Exception, match="disease_state"):
            AgentDisease.to_isolate_agents(
                df=df,
                dt=dt,
                beta=beta,
                disease_groups=disease_groups,
                isolation_adherence_groups=isolation_adherence_groups,
            )

    def test_init_times_infected(
            self,
            fixture_init_times_infected
    ):
        """
            Verifies whether init_times_infected method assigns correct values
            according to the `is_infected` values in the `DiseaseStates`.
        """
        disease_groups = fixture_init_times_infected

        df = DataFrame(
            {
                "agent": [i + 1 for i in range(6)],
                "disease_state": [
                    "susceptible",
                    "latency",
                    "immune",
                    "infectious",
                    "hospital",
                    "dead"
                ]
            }
        )
        df = AgentDisease.init_times_infected(df, disease_groups)
        times_infected_expected = [0, 1, 0, 1, 1, 0]

        assert all(df["times_infected"].eq(times_infected_expected))

    def test_init_times_infected_dask(
            self,
            fixture_init_times_infected
    ):
        """
            Verifies whether init_times_infected method assigns correct values
            according to the `is_infected` values in the `DiseaseStates`.
        """
        disease_groups = fixture_init_times_infected

        df = DataFrame(
            {
                "agent": [i + 1 for i in range(6)],
                "disease_state": [
                    "susceptible",
                    "latency",
                    "immune",
                    "infectious",
                    "hospital",
                    "dead"
                ]
            }
        )
        df = AgentDisease.init_times_infected(
            df,
            disease_groups,
            execmode=ExecutionModes.dask.value
        )
        times_infected_expected = [0, 1, 0, 1, 1, 0]

        assert all(df["times_infected"].eq(times_infected_expected))

    def test_init_times_infected_NotImplementedError(
            self,
            fixture_init_times_infected
    ):
        """
            Raises a ValueError when input DataFrame
            does not have the `disease_state` column.
        """
        disease_groups = fixture_init_times_infected

        df = DataFrame(
            {
                "agent": [i + 1 for i in range(6)],
                "disease_state": [
                    "susceptible",
                    "latency",
                    "immune",
                    "infectious",
                    "hospital",
                    "dead"
                ]
            }
        )

        with pytest.raises(TypeError, match="NotImplementedError"):
            AgentDisease.init_times_infected(
                df=df,
                disease_groups=disease_groups,
                execmode=ExecutionModes.vectorized.value
            )

    def test_init_times_infected_ValueError(
            self,
            fixture_init_times_infected
    ):
        """
            Raises a ValueError when input DataFrame
            does not have the `disease_state` column.
        """
        disease_groups = fixture_init_times_infected

        df = DataFrame({"agent": [i + 1 for i in range(6)]})

        with pytest.raises(
            ValueError,
            match=pytest.error_init_times_infected_ValueError
        ):
            AgentDisease.init_times_infected(
                df=df,
                disease_groups=disease_groups,
            )

    def test_init_immunization_level(
        self,
        fixture_init_immunization
    ):
        """
            Verifies whether init_immunization_level creates
            `immunization_level` column and assigns correctly
            values according with a ImmunizationGroups provided.
        """
        immunization_groups = fixture_init_immunization

        df = DataFrame(
            {
                "agent": [i + 1 for i in range(4)],
                "immunization_group": [
                    "not_immunized",
                    "immunized",
                    "not_immunized",
                    "immunized",
                ]
            }
        )
        df = AgentDisease.init_immunization_level(df, immunization_groups)
        expected_immunization_level = [0, 1, 0, 1]

        assert all(df["immunization_level"].eq(expected_immunization_level))

    def test_init_immunization_level_dask(
        self,
        fixture_init_immunization
    ):
        """
            Verifies whether init_immunization_level creates
            `immunization_level` column and assigns correctly
            values according with a ImmunizationGroups provided
            when `ExecutionModes` is equals to dask.
        """
        immunization_groups = fixture_init_immunization

        df = DataFrame(
            {
                "agent": [i + 1 for i in range(4)],
                "immunization_group": [
                    "not_immunized",
                    "immunized",
                    "not_immunized",
                    "immunized",
                ]
            }
        )
        df = AgentDisease.init_immunization_level(
            df,
            immunization_groups,
            execmode=ExecutionModes.dask.value
        )
        expected_immunization_level = [0, 1, 0, 1]

        assert all(df["immunization_level"].eq(expected_immunization_level))

    def test_init_immunization_params_iterative(
        self,
        fixture_init_immunization
    ):
        """
            Verifies whether init_immunization_params_iterative
            returns correctly values when `immunization_time_distribution`
            is a constant distribution with a constant equals to one.
        """
        immunization_groups = fixture_init_immunization

        s = init_immunization_params_iterative(
            immunization_group="immunized",
            immunization_level=1.0,
            immunization_groups=immunization_groups
        )
        expected_s = Series([0, 30.0, -1/30.0])

        assert all(s.eq(expected_s))

    def test_init_immunization_params_iterative_None_dist(
        self,
        fixture_init_immunization
    ):
        """
            Verifies whether init_immunization_params_iterative
            raises ValueError when `immunization_time_distribution`
            is a None type distribution.
        """
        immunization_groups = fixture_init_immunization

        with pytest.raises(
            ValueError,
            match="immunization_time_distribution"
        ):
            init_immunization_params_iterative(
                immunization_group="not_immunized",
                immunization_level=1.0,
                immunization_groups=immunization_groups
            )

    def test_init_immunization_params_iterative_immunization_level_zero(
        self,
        fixture_init_immunization
    ):
        """
            Verifies whether init_immunization_params_iterative
            raises ValueError when `immunization_time_distribution`
            is a None type distribution.
        """
        immunization_groups = fixture_init_immunization

        s = init_immunization_params_iterative(
            immunization_group="not_immunized",
            immunization_level=0.0,
            immunization_groups=immunization_groups
        )

        for item in s:
            assert isnan(item)

    def test_init_immunization_params(
        self,
        fixture_init_immunization
    ):
        """
            Verifies whether init_immunization_level creates
            `immunization_level` column and assigns correctly
            values according with a ImmunizationGroups provided.
        """
        immunization_groups = fixture_init_immunization

        df = DataFrame(
            {
                "agent": [i + 1 for i in range(3)],
                "immunization_group": [
                    "immunized",
                    "immunized",
                    "immunized",
                ],
                "immunization_level": [0.1, 0.5, 1.0]
            }
        )
        df = AgentDisease.init_immunization_params(
            df=df,
            immunization_groups=immunization_groups
        )
        expected_df = DataFrame(
            {
                "agent": [i + 1 for i in range(3)],
                "immunization_group": [
                    "immunized",
                    "immunized",
                    "immunized",
                ],
                "immunization_level": [0.1, 0.5, 1.0],
                "immunization_time": [0.0, 0.0, 0.0],
                "immunization_max_time": [30.0, 30.0, 30.0],
                "immunization_slope": [0.1/30.0, 0.5/30.0, 1/30.0]
            }
        )

        assert all(df.eq(expected_df))

    def test_init_immunization_dask(
        self,
        fixture_init_immunization
    ):
        """
            Verifies whether init_immunization_level creates
            `immunization_level` column and assigns correctly
            values according with a ImmunizationGroups provided.
        """
        immunization_groups = fixture_init_immunization

        df = DataFrame(
            {
                "agent": [i + 1 for i in range(3)],
                "immunization_group": [
                    "immunized",
                    "immunized",
                    "immunized",
                ],
                "immunization_level": [0.1, 0.5, 1.0]
            }
        )
        df = AgentDisease.init_immunization_params(
            df=df,
            immunization_groups=immunization_groups,
            execmode=ExecutionModes.dask.value
        )
        expected_df = DataFrame(
            {
                "agent": [i + 1 for i in range(3)],
                "immunization_group": [
                    "immunized",
                    "immunized",
                    "immunized",
                ],
                "immunization_level": [0.1, 0.5, 1.0],
                "immunization_time": [0.0, 0.0, 0.0],
                "immunization_max_time": [30.0, 30.0, 30.0],
                "immunization_slope": [0.1/30.0, 0.5/30.0, 1/30.0]
            }
        )

        assert all(df.eq(expected_df))

    def test_init_immunization_params_NotImplementedError(
        self,
        fixture_init_immunization
    ):
        """
            Raises ValueError when the execmode
            is set to `ExecutionModes.iterative.value`.
        """
        immunization_groups = fixture_init_immunization

        df = DataFrame(
            {
                "agent": [i + 1 for i in range(3)],
                "immunization_group": [
                    "immunized",
                    "immunized",
                    "immunized",
                ],
                "immunization_level": [0.1, 0.5, 1.0]
            }
        )

        with pytest.raises(TypeError, match="NotImplementedError"):
            AgentDisease.init_immunization_params(
                df=df,
                immunization_groups=immunization_groups,
                execmode=ExecutionModes.vectorized.value
            )

    def test_init_immunization_params_Exception_immunization_level_column(
        self,
        fixture_init_immunization
    ):
        """
            Raises an Exception when the input DataFrame
            does not contain `immunization_level` column.
        """
        immunization_groups = fixture_init_immunization

        df = DataFrame(
            {
                "agent": [i + 1 for i in range(3)],
                "immunization_group": [
                    "immunized",
                    "immunized",
                    "immunized",
                ]
            }
        )

        with pytest.raises(Exception, match="immunization_level"):
            AgentDisease.init_immunization_params(
                df=df,
                immunization_groups=immunization_groups
            )

    def test_transition_function_probability_transition_equals_one(
            self,
            fixture_transition_function
    ):
        """
            There must be a `disease_state` transition when
            `disease_state_time` is greater than `disease_state_max_time`,
            there are only one transition and its probability is set to one.
        """
        natural_history = fixture_transition_function[0]
        disease_groups = fixture_transition_function[1]

        transition = transition_function(
            disease_state="susceptible",
            disease_state_time=10,
            disease_state_max_time=9,
            is_dead=False,
            key="not_vulnerable-susceptible",
            disease_groups=disease_groups,
            natural_history=natural_history
            )

        expected_disease_state = "latency"
        expected_is_dead = False
        expected_do_calculate_max_time = True
        expected_do_update_immunization_params = True

        assert transition[0] == expected_disease_state
        assert transition[2] == expected_is_dead
        assert transition[3] == expected_do_calculate_max_time
        assert transition[4] == expected_do_update_immunization_params

    def test_transition_function_probability_transition_equals_cero(
            self,
            fixture_transition_function
    ):
        """
            There is no `disease_state` transition when
            `disease_state_time` is greater than `disease_state_max_time`
            and the probability is set to zero.
        """
        natural_history = fixture_transition_function[0]
        disease_groups = fixture_transition_function[1]

        transition = transition_function(
            disease_state="latency",
            disease_state_time=10,
            disease_state_max_time=5,
            is_dead=False,
            key="vulnerable-latency",
            disease_groups=disease_groups,
            natural_history=natural_history
            )

        disease_state_prob_zero = "infectious"
        expected_is_dead = False
        expected_do_calculate_max_time = True

        assert transition[0] != disease_state_prob_zero
        assert transition[2] == expected_is_dead
        assert transition[3] == expected_do_calculate_max_time

    def test_transition_function_disease_state_max_time_grater_disease_state(
            self,
            fixture_transition_function
    ):
        """
            There is no `disease_state` transition when
            `disease_state_max_time` is
            greater than `disease_state_time`.
        """
        natural_history = fixture_transition_function[0]
        disease_groups = fixture_transition_function[1]

        transition = transition_function(
            disease_state="susceptible",
            disease_state_time=1,
            disease_state_max_time=5,
            is_dead=False,
            key="not_vulnerable-susceptible",
            disease_groups=disease_groups,
            natural_history=natural_history
            )

        disease_state_expected = "susceptible"
        is_dead_expected = False
        do_calculate_max_time_expected = False

        assert transition[0] == disease_state_expected
        assert transition[2] == is_dead_expected
        assert transition[3] == do_calculate_max_time_expected

    def test_transition_function_is_dead_True(
            self,
            fixture_transition_function
    ):
        """
            When there is a transition to `dead`
            transition_function assigns True to `is_dead`.
        """
        natural_history = fixture_transition_function[0]
        disease_groups = fixture_transition_function[1]

        transition = transition_function(
            disease_state="infectiuos",
            disease_state_time=10,
            disease_state_max_time=5,
            is_dead=False,
            key="vulnerable-infectious",
            disease_groups=disease_groups,
            natural_history=natural_history
            )

        disease_state_expected = "dead"
        is_dead_expected = True
        do_calculate_max_time_expected = True

        assert transition[0] == disease_state_expected
        assert transition[2] == is_dead_expected
        assert transition[3] == do_calculate_max_time_expected

    def test_disease_state_transition_iterative(
            self,
            fixture_transition_function
    ):
        """
            Verifies whether `disease_state_transition`
            applies correctly the function `transition_function`
            when execmode is set to iterative.
        """
        natural_history = fixture_transition_function[0]
        disease_groups = fixture_transition_function[1]
        data_dict = fixture_transition_function[2]

        df = DataFrame(data_dict)
        df = AgentDisease.disease_state_transition(
            df=df,
            dt=2,
            disease_groups=disease_groups,
            natural_history=natural_history
            )

        disease_state_expected = [
            "latency",
            "immune",
            "susceptible",
            "dead"
        ]
        is_dead_expected = [False, False, False, True]
        disease_state_max_time_expected = Series(
            [nan, nan, 5, nan],
            name="disease_state_max_time"
        )
        initial_disease_state_time = data_dict["disease_state_time"]
        cond_disease_state = df["disease_state"].eq(disease_state_expected)
        cond_disease_state_time = df[
            "disease_state_time"
        ].ne(initial_disease_state_time)
        cond_is_dead = df["is_dead"].eq(is_dead_expected)

        assert all(cond_disease_state)
        assert all(cond_disease_state_time)
        assert all(cond_is_dead)
        testing.assert_series_equal(
            df["disease_state_max_time"],
            disease_state_max_time_expected
        )

    def test_disease_state_transition_dask(
            self,
            fixture_transition_function
    ):
        """
            Verifies whether `disease_state_transition`
            applies correctly the function `transition_function`
            when execmode is set to dask.
        """
        natural_history = fixture_transition_function[0]
        disease_groups = fixture_transition_function[1]
        data_dict = fixture_transition_function[2]

        df = DataFrame(data_dict)
        df = AgentDisease.disease_state_transition(
            df=df,
            dt=2,
            disease_groups=disease_groups,
            natural_history=natural_history,
            execmode=ExecutionModes.dask.value
            )

        disease_state_expected = [
            "latency",
            "immune",
            "susceptible",
            "dead"
        ]
        is_dead_expected = [False, False, False, True]
        disease_state_max_time_expected = Series(
            [nan, nan, 5, nan],
            name="disease_state_max_time"
        )
        initial_disease_state_time = data_dict["disease_state_time"]
        cond_disease_state = df["disease_state"].eq(disease_state_expected)
        cond_disease_state_time = df[
            "disease_state_time"
        ].ne(initial_disease_state_time)
        cond_is_dead = df["is_dead"].eq(is_dead_expected)

        assert all(cond_disease_state)
        assert all(cond_disease_state_time)
        assert all(cond_is_dead)
        testing.assert_series_equal(
            df["disease_state_max_time"],
            disease_state_max_time_expected
        )

    def test_disease_state_transition_ValueError(
            self,
            fixture_transition_function
    ):
        """
            Raises a ValueError when input DataFrame does
            not have the `disease_state` column.
        """
        natural_history = fixture_transition_function[0]
        disease_groups = fixture_transition_function[1]
        data_dict = fixture_transition_function[2]
        data_dict.pop("disease_state")

        df = DataFrame(data_dict)

        with pytest.raises(
            ValueError,
            match=pytest.error_disease_state_transition
        ):
            AgentDisease.disease_state_transition(
                df=df,
                dt=2,
                disease_groups=disease_groups,
                natural_history=natural_history
            )

    def test_apply_mobility_restrictions_tracing_enabled(
        self,
        fixture_apply_mobility_restrictions_tracing
    ):
        """
            verifies whether apply_mobility_restriction sets
            mrt_policies to enabled when conditions are fulfilled.
        """
        data_df = fixture_apply_mobility_restrictions_tracing[0]
        mrt_policies = fixture_apply_mobility_restrictions_tracing[1]

        interest_variable = InterestVariables.dead
        input_df = DataFrame(data_df)
        output_tuple = AgentDisease.apply_mobility_restrictions(
            step=2,
            df=input_df,
            beta=0.5,
            mrt_policies={interest_variable: mrt_policies},
            mrt_policies_df=DataFrame(
                {
                    "step": 1,
                    "dead_by_disease": "disabled"
                }, index=[0]
            ),
            iteration_time=timedelta(days=1)
        )

        assert output_tuple[1]["dead_by_disease"].iloc[-1] == "enabled"

    def test_apply_mobility_restrictions_tracing_disabled_stop_level(
        self,
        fixture_apply_mobility_restrictions_tracing
    ):
        """
            verifies whether apply_mobility_restriction sets
            mrt_policies to disabled when conditions are fulfilled.
        """
        data_df = fixture_apply_mobility_restrictions_tracing[0]
        mrt_policies = fixture_apply_mobility_restrictions_tracing[1]

        interest_variable = InterestVariables.dead
        input_df = DataFrame(data_df)
        output_tuple = AgentDisease.apply_mobility_restrictions(
            step=2,
            df=input_df,
            beta=0.5,
            mrt_policies={interest_variable: mrt_policies},
            mrt_policies_df=DataFrame(
                {
                    "step": 1,
                    "dead_by_disease": "enabled"
                }, index=[0]
            ),
            iteration_time=timedelta(days=1)
        )

        assert output_tuple[1]["dead_by_disease"].iloc[-1] == "disabled"

    def test_apply_mobility_restrictions_tracing_disabled_stop_lenght(
        self,
        fixture_apply_mobility_restrictions_tracing
    ):
        """
            verifies whether apply_mobility_restriction sets
            mrt_policies to disabled when conditions are fulfilled.
        """
        data_df = fixture_apply_mobility_restrictions_tracing[0]
        mrt_policies = fixture_apply_mobility_restrictions_tracing[2]

        interest_variable = InterestVariables.dead
        input_df = DataFrame(data_df)
        output_tuple = AgentDisease.apply_mobility_restrictions(
            step=3,
            df=input_df,
            beta=0.5,
            mrt_policies={interest_variable: mrt_policies},
            mrt_policies_df=DataFrame(
                {
                    "step": [1, 2],
                    "dead_by_disease": ["enabled", "enabled"]
                }
            ),
            iteration_time=timedelta(days=1)
        )

        assert output_tuple[1]["dead_by_disease"].iloc[-1] == "disabled"

    def test_apply_mobility_restrictions_cyclic_grace_time_equals_step(
        self,
        fixture_apply_mobility_restrictions_cyclic
    ):
        """
            verifies whether apply_mobility_restriction sets
            `global_mr` to enabled but `MG_1` disabled due to delay time.
        """
        input_df = DataFrame(fixture_apply_mobility_restrictions_cyclic[0])
        cyclic_policies = fixture_apply_mobility_restrictions_cyclic[1]
        global_cyclic_mr = fixture_apply_mobility_restrictions_cyclic[2]

        output_tuple = AgentDisease.apply_mobility_restrictions(
            step=2,
            df=input_df,
            beta=0.5,
            global_cyclic_mr=global_cyclic_mr,
            cyclic_mr_policies={"mr_group_1": cyclic_policies},
            cmr_policies_df=DataFrame({
                "step": 1,
                "global_mr": "disabled",
                "MG_1": "enabled"
                }, index=[0]),
            grace_time_in_steps=1,
            iteration_time=timedelta(days=1)
        )
        assert output_tuple[2]["mr_group_1"].iloc[-1] == "disabled"
        assert output_tuple[2]["global_mr"].iloc[-1] == "enabled"

    def test_apply_mobility_restrictions_step_less_than_grace_times(
        self,
        fixture_apply_mobility_restrictions_cyclic
    ):
        """
            verifies whether apply_mobility_restriction sets `cyclic_policies`
            to disabled when the step is less than grace times.
        """
        input_df = DataFrame(fixture_apply_mobility_restrictions_cyclic[0])
        cyclic_policies = fixture_apply_mobility_restrictions_cyclic[1]
        global_cyclic_mr = fixture_apply_mobility_restrictions_cyclic[2]

        output_tuple = AgentDisease.apply_mobility_restrictions(
            step=1,
            df=input_df,
            beta=0.5,
            global_cyclic_mr=global_cyclic_mr,
            cyclic_mr_policies={"MG_1": cyclic_policies},
            cmr_policies_df=DataFrame({
                "step": 0,
                "global_mr": "disabled",
                "MG_1": "enabled"
                }, index=[0]),
            grace_time_in_steps=2,
            iteration_time=timedelta(days=1)
        )

        assert output_tuple[2]["MG_1"].iloc[-1] == "disabled"
        assert output_tuple[2]["global_mr"].iloc[-1] == "disabled"

    def test_apply_mobility_restrictions_grace_time_less_than_step(
        self,
        fixture_apply_mobility_restrictions_cyclic
    ):
        """
            verifies whether apply_mobility_restriction sets `cyclic_policies`
            to disabled when grace times is less than the step.
        """
        cyclic_policies = fixture_apply_mobility_restrictions_cyclic[3]
        input_df = DataFrame(fixture_apply_mobility_restrictions_cyclic[0])
        global_cyclic_mr = fixture_apply_mobility_restrictions_cyclic[4]

        output_tuple = AgentDisease.apply_mobility_restrictions(
            step=3,
            df=input_df,
            beta=0.5,
            global_cyclic_mr=global_cyclic_mr,
            cyclic_mr_policies={"mr_group_1": cyclic_policies},
            cmr_policies_df=DataFrame({
                "step": [1, 2],
                "global_mr": ["disabled", "disabled"],
                "mr_group_1": ["disabled", "disabled"]
                }),
            grace_time_in_steps=1,
            iteration_time=timedelta(days=1)
        )

        assert output_tuple[2]["global_mr"].iloc[-1] == "disabled"
        assert output_tuple[2]["mr_group_1"].iloc[-1] == "disabled"

    def test_apply_mobility_restrictions_delay_zero_fixed(
        self,
        fixture_apply_mobility_restrictions_cyclic
    ):
        """
            verifies whether apply_mobility_restriction sets
            `cyclic_policies` to disabled when grace times is
            less than the step and delay is equals to zero.
        """
        cyclic_policies = fixture_apply_mobility_restrictions_cyclic[5]
        input_df = DataFrame(fixture_apply_mobility_restrictions_cyclic[0])
        global_cyclic_mr = fixture_apply_mobility_restrictions_cyclic[6]

        output_tuple = AgentDisease.apply_mobility_restrictions(
            step=3,
            df=input_df,
            beta=0.5,
            global_cyclic_mr=global_cyclic_mr,
            cyclic_mr_policies={"mr_group_1": cyclic_policies},
            cmr_policies_df=DataFrame({
                "step": [0, 1, 2],
                "global_mr": ["disabled", "enabled", "enabled"],
                "mr_group_1": ["disabled", "disabled", "enabled"]
                }),
            grace_time_in_steps=1,
            iteration_time=timedelta(days=1)
        )

        assert output_tuple[2]["global_mr"].iloc[-1] == "enabled"
        assert output_tuple[2]["mr_group_1"].iloc[-1] == "disabled"

    def test_apply_mobility_restrictions_delay_zero_random(
        self,
        fixture_apply_mobility_restrictions_cyclic
    ):
        """
            verifies whether apply_mobility_restriction sets
            `cyclic_policies` to disabled when grace times is
            less than the step and delay is equals to zero.
        """
        cyclic_policies = fixture_apply_mobility_restrictions_cyclic[7]
        input_df = DataFrame(fixture_apply_mobility_restrictions_cyclic[0])
        global_cyclic_mr = fixture_apply_mobility_restrictions_cyclic[8]

        output_tuple = AgentDisease.apply_mobility_restrictions(
            step=3,
            df=input_df,
            beta=0.5,
            global_cyclic_mr=global_cyclic_mr,
            cyclic_mr_policies={"mr_group_1": cyclic_policies},
            cmr_policies_df=DataFrame({
                "step": [0, 1, 2],
                "global_mr": ["disabled", "enabled", "enabled"],
                "mr_group_1": ["disabled", "disabled", "enabled"]
                }),
            grace_time_in_steps=1,
            iteration_time=timedelta(days=1)
        )

        assert output_tuple[2]["global_mr"].iloc[-1] == "enabled"
        assert output_tuple[2]["mr_group_1"].iloc[-1] == "disabled"

    def test_apply_mobility_restrictions_two_restriction_cycles_fixed(
        self,
        fixture_apply_mobility_restrictions_cyclic
    ):
        """
            verifies whether apply_mobility_restriction sets
            `cyclic_policies` to enabled when conditions are
            fulfilled before two restrictions cycles.
        """
        cyclic_policies = fixture_apply_mobility_restrictions_cyclic[9]
        input_df = DataFrame(fixture_apply_mobility_restrictions_cyclic[0])
        global_cyclic_mr = fixture_apply_mobility_restrictions_cyclic[10]

        app = AgentDisease.apply_mobility_restrictions(
            step=9,
            df=input_df,
            beta=0.5,
            global_cyclic_mr=global_cyclic_mr,
            cyclic_mr_policies={"MG_1": cyclic_policies},
            cmr_policies_df=DataFrame(
                {
                    "step": [1, 2, 3, 4, 5, 6, 7, 8],
                    "global_mr": [
                        "enabled",
                        "enabled",
                        "disabled",
                        "disabled",
                        "disabled",
                        "disabled",
                        "disabled",
                        "enabled"
                    ],
                    "MG_1": [
                        "disabled",
                        "disabled",
                        "enabled",
                        "enabled",
                        "disabled",
                        "disabled",
                        "disabled",
                        "enabled"
                    ]
                }
            ),
            grace_time_in_steps=1,
            iteration_time=timedelta(days=1)
        )

        assert app[2]["global_mr"].iloc[-1] == "enabled"
        assert app[2]["MG_1"].iloc[-1] == "enabled"

    def test_apply_mobility_restrictions_two_restriction_cycles_random(
        self,
        fixture_apply_mobility_restrictions_cyclic
    ):
        """
            verifies whether apply_mobility_restriction sets
            `cyclic_policies` to enabled when conditions are
            fulfilled before two restrictions cycles and
            `unrestricted_time_mode` is setted to `CyclicMRModes.random`.
        """
        cyclic_policies = fixture_apply_mobility_restrictions_cyclic[11]
        input_df = DataFrame(fixture_apply_mobility_restrictions_cyclic[0])
        global_cyclic_mr = fixture_apply_mobility_restrictions_cyclic[12]

        output_tuple = AgentDisease.apply_mobility_restrictions(
            step=6,
            df=input_df,
            beta=0.5,
            global_cyclic_mr=global_cyclic_mr,
            cyclic_mr_policies={"mr_group_1": cyclic_policies},
            cmr_policies_df=DataFrame(
                {
                    "step": [1, 2, 3, 4, 5],
                    "global_mr": [
                        "enabled",
                        "enabled",
                        "disabled",
                        "enabled",
                        "enabled"
                    ],
                    "mr_group_1": [
                        "disabled",
                        "disabled",
                        "enabled",
                        "enabled",
                        "disabled"
                    ]
                }
            ),
            grace_time_in_steps=0,
            iteration_time=timedelta(days=1)
        )
        assert output_tuple[2]["global_mr"].iloc[-1] == "disabled"
        assert output_tuple[2]["mr_group_1"].iloc[-1] == "disabled"

    def test_apply_mobility_restrictions_MRAdherenceGroups(
        self,
        fixture_apply_mobility_restrictions_cyclic
    ):
        """
            Verifies the adherences of the agents when
            there are two `mr_adherence_group`; one with a
            mr_adherence_prob of 1 and the other of zero.
        """
        cyclic_policies = fixture_apply_mobility_restrictions_cyclic[13]
        input_df = DataFrame(fixture_apply_mobility_restrictions_cyclic[0])
        global_cyclic_mr = fixture_apply_mobility_restrictions_cyclic[14]

        mr_adherence = MRAdherenceGroups(
            dist_title="mr_adherence_prob",
            group_info=[{
                "name": "mr_adherence_group_1",
                "dist_info": {
                    "dist_title": "mr_adherence_prob",
                    "dist_type": "constant",
                    "constant": 1
                }
            },
                {
                "name": "mr_adherence_group_2",
                "dist_info": {
                    "dist_title": "mr_adherence_prob",
                    "dist_type": "constant",
                    "constant": 0
                }
            }]
        )
        output_tuple = AgentDisease.apply_mobility_restrictions(
            step=2,
            df=input_df,
            beta=5,
            global_cyclic_mr=global_cyclic_mr,
            cyclic_mr_policies={"mr_group_1": cyclic_policies},
            cmr_policies_df=DataFrame({
                "step": [1],
                "global_mr": ["enabled"],
                "mr_group_1": ["disabled"]
                }),
            grace_time_in_steps=0,
            iteration_time=timedelta(days=1),
            mr_adherence_groups=mr_adherence
        )

        assert output_tuple[2]["global_mr"].iloc[-1] == "enabled"
        assert output_tuple[2]["mr_group_1"].iloc[-1] == "enabled"
        assert output_tuple[0]["isolated_by_mr"].iloc[-1] == True
        assert output_tuple[0]["adheres_to_mr_isolation"].iloc[-1] == True
        assert output_tuple[0]["isolated_by_mr"].iloc[0] == True
        assert output_tuple[0]["adheres_to_mr_isolation"].iloc[0] == False
