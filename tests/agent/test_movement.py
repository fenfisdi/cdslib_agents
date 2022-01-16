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
#This package is authored by:
#Camilo Hincapié (https://www.linkedin.com/in/camilo-hincapie-gutierrez/) (main author)
#Ian Mejía (https://github.com/IanMejia)
#Emil Rueda (https://www.linkedin.com/in/emil-rueda-424012207/)
#Nicole Rivera (https://github.com/nicolerivera1)
#Carolina Rojas Duque (https://github.com/carolinarojasd)
#and the conceptual contributions about epidemiology of
#Lina Marcela Ruiz Galvis (mailto:lina.ruiz2@udea.edu.co).
#
#Other remarkably contributors to this work were
#Alejandro Campillo (https://www.linkedin.com/in/alucardcampillo/)
#Daniel Alfonso Montoya (https://www.linkedin.com/in/daniel-montoya-ds/).

import pytest
from pandas import DataFrame, Series
from scipy.stats import kstest
from numpy import random, array, nan, all, pi, round, sqrt, cos, sin, inf

from abmodel.agent.movement import AgentMovement
from abmodel.models.population import BoxSize
from abmodel.utils.distributions import Distribution
from abmodel.models.disease import MobilityGroups


class TestCaseAgentMovement:
    """
        Verifies the functionality of all methods in the AgentMovement class
        from agent.
    """
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    @pytest.fixture
    def fixture_initialize_velocities(self):

        distribution = Distribution(
            dist_type="numpy",
            dist_name="gamma",
            shape=2
            )
        angle_dist = Distribution(
            dist_type="constant",
            constant=pi/4
            )
        distribution_2 = Distribution(
            dist_type="constant",
            constant=1
            )
        angle_dist_2 = Distribution(
            dist_type="constant",
            constant=0
            )
        indexes = [0, 1, 2, 3, 4]
        return distribution, angle_dist, distribution_2, angle_dist_2, indexes

    @pytest.fixture
    def fixture_set_velocities(self):
        distribution = Distribution(
            dist_type="constant",
            constant=5
            )
        delta_angles = Distribution(
                    dist_type="numpy",
                    dist_name="normal",
                    loc=0.0,
                    scale=0.1
                    ).sample(5)
        angles = [0, pi/4, pi/2, pi, 3*pi/4]
        pytest.vx = [
            5*cos(angle + delta_angle) for
            (angle, delta_angle) in zip(angles, delta_angles)
        ]
        pytest.vy = [
            5*sin(angle + delta_angle) for
            (angle, delta_angle) in zip(angles, delta_angles)
        ]
        return distribution, delta_angles

    @pytest.fixture
    def fixture_init_required_fields(self):
        data = random.normal(0.0, 10, 15)
        dist_title = "MobilityGroup_test_dist"
        group_info1 = [
            {
                "name": "MG_1",
                "angle_variance": 0.1,
                "dist_info": {
                    "dist_title": "mobility_profile",
                    "dist_type": "empirical",
                    "constant": 0.4,
                    "dist_name": None,
                    "filename": None,
                    "data": data,
                    "kwargs": {
                        "kernel": "gaussian",
                        "bandwidth": 0.1
                        }
                    }
            }
        ]
        group_info2 = [
            {
                "name": "MG_1",
                "angle_variance": 0.5,
                "dist_info": {
                    "dist_title": "mobility_profile",
                    "dist_type": "numpy",
                    "constant": None,
                    "dist_name": "standard_t",
                    "filename": None,
                    "data": None,
                    "kwargs": {"df": 16}
                    }
            }
        ]
        pytest.expected_columns = [
            "mobility_group",
            "agent", "step",
            "x", "y", "vx", "vy"
            ]
        return dist_title, group_info1, group_info2

    @pytest.fixture
    def set_up(self) -> None:
        pytest.box_size = BoxSize(-50, 50, -30, 30)
        pytest.dt = 1.0
        pytest.data = {
            "x": [0],
            "y": [0],
            "vx": [1.0],
            "vy": [0],
        }

        pytest.data_na = {
            "x": [nan],
            "y": [0],
            "vx": [1.0],
            "vy": [0],
        }

    @pytest.fixture
    def fixture_crash_with_wall(self, set_up) -> None:
        pytest.data = {
            "x": [49, 0, -49, 0],
            "y": [0, 29, 0, -29],
            "vx": [2.0, 2.0, -2.0, 2.0],
            "vy": [2.0, 2.0, 2.0, -2.0],
        }

        pytest.expected_data = {
            "x": [50.0, 2.0, -50.0, 2.0],
            "y": [2.0, 30.0, 2.0, -30.0],
            "vx": [-2.0, 2.0, 2.0, 2.0],
            "vy": [2.0, -2.0, 2.0, 2.0],
        }

    @pytest.fixture
    def fixture_crash_with_corner(self, set_up) -> None:
        pytest.data = {
            "x": [49, -49, -49, 49],
            "y": [29, 29, -29, -29],
            "vx": [2.0, -2.0, -2.0, 2.0],
            "vy": [2.0, 2.0, -2.0, -2.0],
        }

        pytest.expected_data = {
            "x": [50.0, -50.0, -50.0, 50.0],
            "y": [30.0, 30.0, -30.0, -30.0],
            "vx": [-2.0, 2.0, 2.0, -2.0],
            "vy": [-2.0, -2.0, 2.0, 2.0],
        }

    @pytest.fixture
    def fixture_raise_errors(self, set_up) -> None:
        pytest.data_without_x = {
            "y": [0],
            "vx": [1.0],
            "vy": [0],
        }
        pytest.error_message = (
                    "Some columns might be initialized incorrectly.\n"
                    "To pinpoint especific errors, "
                    "add `debug=True` as a parameter"
        )

        check_cols = ["x"]
        cols = ["x", "y", "vx", "vy"]
        error_string = "df must contain: " + ", ".join(cols) + ".\n"
        check_string = ", ".join(check_cols) + " must be checked"
        pytest.error_message2 = error_string + check_string

    @pytest.fixture
    def fixture_stop_agents(self) -> None:
        samples = 10
        sample_stopped = 5
        pytest.data = {
            "vx": random.randint(-20, 20, samples),
            "vy": random.randint(-20, 20, samples)
        }
        pytest.list_index_stopped = [x for x in range(sample_stopped)]
        pytest.data_wrong_name_columns = {
            "Vx": random.randint(-20, 20, samples),
            "VY": random.randint(-20, 20, samples)
        }

    @pytest.fixture
    def fixture_vector_angles_raise_error(self) -> None:
        pytest.data = {
            "x": [0],
            "y": [0],
            "vx": [1.0],
            "vy": [0],
        }

        pytest.wrong_data = {
            "X": [0],
            "Y": [0],
            "vx": [1.0],
            "vy": [0],
        }

        pytest.wrong_list = ["X", "vX"]
        pytest.correct_list = ["x", "y"]

    @pytest.fixture
    def fixture_update_velocities(self) -> None:
        pytest.angle_variance = 0.1
        pytest.angle_variance_2 = 0.5
        pytest.angle_variance_field = 0.1
        large_sample = 500
        pytest.data_large_sample = {
            "vx": -20*random.random(large_sample) + 10,
            "vy": -20*random.random(large_sample) + 10
        }

        pytest.distrib = Distribution(
            dist_type="numpy",
            dist_name="normal",
            loc=10.0,
            scale=1.0
        )

        pytest.delta_angles = Distribution(
            dist_type="numpy",
            dist_name="normal",
            loc=0.0,
            scale=pytest.angle_variance).sample(size=large_sample)

        pytest.data_field = {
            "field": array(["field_2", "field_1"]),
            "vx": array([1.0, 2.0]),
            "vy": array([0, 2.0]),
        }
        pytest.delta_angles_2 = Distribution(
                    dist_type="numpy",
                    dist_name="normal",
                    loc=0.0,
                    scale=pytest.angle_variance_2
                    ).sample(large_sample)

    @pytest.fixture
    def fixture_replace_velocities_different_components(self) -> None:
        pytest.new_angles_list = [pi, pi/2, pi/3]
        pytest.new_angles_data = {
            k: v for (k, v) in zip(
                [k for k in range(1, 4, 1)], pytest.new_angles_list
                )
        }

        pytest.data = {
            "agent": [1, 2, 3],
            "x": [0, 1, 1],
            "y": [0, 1, -1],
            "vx": [0.0, 1.0, sqrt(2.0)],
            "vy": [0.0, 1.0, sqrt(2.0)],
        }

    @pytest.fixture
    def fixture_replace_velocities_norm_equal_to_zero(self) -> None:
        pytest.new_angle = {1: pi}
        pytest.data = {
            "agent": [1],
            "x": [1],
            "y": [-1],
            "vx": [0.0],
            "vy": [0.0],
        }

    @pytest.fixture
    def fixture_replace_velocities_same_components(self) -> None:
        pytest.data = {
            "agent": [1, 2, 3],
            "x": [0, 1, 1],
            "y": [0, 1, -1],
            "vx": [1.0, 1.0, 1.0],
            "vy": [1.0, 1.0, 1.0],
        }
        pytest.new_angles_data = {1: pi, 2: pi, 3: pi}

    @pytest.fixture
    def fixture_avoid_agents_same_rel_angles(self) -> None:
        pytest.data = {
            "agent": [1, 2, 3],
            "x": [0, 1, 2],
            "y": [0, 1, 2],
            "vx": [1.0, 10.0, 10],
            "vy": [0, 10.0, 10],
        }

        pytest.data_avoid = {
            "agent": [1, 1],
            "agent_to_avoid": [2, 3]
        }

    @pytest.fixture
    def fixture_avoid_agents_one_avoids_two(self) -> None:
        pytest.data = {
            "agent": [1, 2, 3],
            "x": [0, 1, 1],
            "y": [0, 1, -1],
            "vx": [1.0, 2.0, 0],
            "vy": [0, 2.0, 0],
        }

        pytest.data_avoid = {
            "agent": [1, 1],
            "agent_to_avoid": [2, 3]
        }

    @pytest.fixture
    def fixture_avoid_agents_different_rel_angles(self) -> None:
        pytest.data = {
            "agent": [1, 2, 3],
            "x": [0, 1, 0],
            "y": [0, 0, 1],
            "vx": [1.0, 0.0, 10],
            "vy": [0, 1, 10],
        }

        pytest.data_avoid = {
            "agent": [1, 2],
            "agent_to_avoid": [3, 3]
        }

    @pytest.fixture
    def fixture_avoid_agents_two_agents_avoid_one(self) -> None:
        pytest.data = {
            "agent": [1, 2, 3],
            "x": [0, 0, 0],
            "y": [-1, -2, -3],
            "vx": [1.0, 0.0, 10],
            "vy": [0, 1, 10],
        }

        pytest.data_avoid = {
            "agent": [1, 2],
            "agent_to_avoid": [3, 3]
        }

    @pytest.fixture
    def fixture_avoid_agents_one_agent_avoids_three(self) -> None:
        pytest.data = {
            "agent": [1, 2, 3, 4],
            "x": [-1, 1, 0, 0],
            "y": [0, 0, -1, 1],
            "vx": [1.0, 0.0, 10, 20],
            "vy": [1.0, 1, 10, 20],
        }

        pytest.data_avoid = {
            "agent": [1, 1, 1],
            "agent_to_avoid": [2, 3, 4]
        }

    @pytest.fixture
    def fixture_avoid_agents_one_agent_between_two(self) -> None:
        pytest.data = {
            "agent": [1, 2, 3],
            "x": [0, 1, -1],
            "y": [0, 0, 0],
            "vx": [1.0, 2.0, 0],
            "vy": [1.0, 2.0, 0],
        }
        pytest.data_avoid = {
            "agent": [1, 1],
            "agent_to_avoid": [2, 3]
        }

    @pytest.fixture
    def fixture_avoid_agents_one_avoids_four_in_each_axis(self) -> None:
        pytest.data = {
            "agent": [1, 2, 3, 4, 5],
            "x": [0, 1, 0, -1, 0],
            "y": [0, 0, 1, 0, -1],
            "vx": [1.0, 2.0, 0, 10, 2],
            "vy": [0.0, 2.0, 0, 5, 2],
        }
        pytest.data_avoid = {
            "agent": [1, 1, 1, 1],
            "agent_to_avoid": [2, 3, 4, 5]
        }

    @pytest.fixture
    def fixture_avoid_agents_raise_error(self) -> None:
        pytest.data_without_agent = {
            "x": [0, 1, 1],
            "y": [0, 1, -1],
            "vx": [1.0, 2.0, 0],
            "vy": [0, 2.0, 0],
        }

        pytest.data_avoid = {
            "agent": [1, 1],
            "agent_to_avoid": [2, 3]
        }

    def test_initialize_velocities_indexes_and_group_field_not_None_one_group(
        self,
        fixture_initialize_velocities
    ):
        """
        Verifies whether `initialize_velocities` applies `set_velocities` only
        to the agents in the indexes list passed when all of them are in the
        same `group_field`.
        """
        angle_dist = fixture_initialize_velocities[3]
        distribution = fixture_initialize_velocities[2]
        indexes = fixture_initialize_velocities[4]

        input_df = DataFrame(
            {
                "vx": random.randint(9, size=9),
                "vy": random.randint(9, size=9),
                "mobility_group": ["MG_1" for i in range(9)]
            }
            )
        df = AgentMovement.initialize_velocities(
            input_df,
            distribution,
            angle_dist,
            indexes,
            "mobility_group",
            "MG_1"
            )

        assert all(df["vx"][0:5] == 1) & all(df["vy"][0:5] == 0)
        assert all(
            input_df["vx"][5:] == df["vx"][5:]
            ) & all(
                input_df["vy"][5:] == df["vy"][5:]
                )

    def test_initialize_velocities_indexes_and_group_field_not_None_two_groups(
        self,
        fixture_initialize_velocities
    ):
        """
        Verifies whether `initialize_velocities` applies `set_velocities` only
        to the agents in the indexes list passed and in the `group_field`
        specified.
        """
        angle_dist = fixture_initialize_velocities[3]
        distribution = fixture_initialize_velocities[2]
        indexes = fixture_initialize_velocities[4]

        input_df = DataFrame(
            {
                "vx": random.randint(9, size=9),
                "vy": random.randint(9, size=9),
                "mobility_group": [
                    "MG_1", "MG_1", "MG_1", "MG_2", "MG_2",
                    "MG_2", "MG_2", "MG_2", "MG_2"
                ]

            }
            )
        df = AgentMovement.initialize_velocities(
            input_df,
            distribution,
            angle_dist,
            indexes,
            "mobility_group",
            "MG_1"
            )

        assert all(df["vx"][0:3] == 1) & all(df["vy"][0:3] == 0)
        assert all(
            input_df["vx"][3:] == df["vx"][3:]
            ) & all(
                input_df["vy"][3:] == df["vy"][3:]
                )

    def test_initialize_velocities_indexes_is_empty(
        self,
        fixture_initialize_velocities
    ):
        """
        Verifies whether `initialize_velocities` does not applies
        `set_velocities` when `indexes` is an empty list.
        """
        angle_dist = fixture_initialize_velocities[3]
        distribution = fixture_initialize_velocities[2]

        input_df = DataFrame(
            {
                "vx": random.randint(9, size=9),
                "vy": random.randint(9, size=9),
                "mobility_group": [
                    "MG_1", "MG_1", "MG_1", "MG_2", "MG_2",
                    "MG_2", "MG_2", "MG_2", "MG_2"
                ]

            }
            )
        indexes = []
        df = AgentMovement.initialize_velocities(
            input_df,
            distribution,
            angle_dist,
            indexes,
            "mobility_group",
            "MG_1"
            )

        assert all(
            input_df["vx"][:] == df["vx"][:]
            ) & all(
                input_df["vy"][:] == df["vy"][:]
                )

    def test_initialize_velocities_group_label_is_not_in_group_field(
        self,
        fixture_initialize_velocities
    ):
        """
        Verifies whether `initialize_velocities` does not applies
        `set_velocities` when `group_label` is not in `group_field`.
        """
        angle_dist = fixture_initialize_velocities[3]
        distribution = fixture_initialize_velocities[2]
        indexes = fixture_initialize_velocities[4]

        input_df = DataFrame(
            {
                "vx": random.randint(9, size=9),
                "vy": random.randint(9, size=9),
                "mobility_group": [
                    "MG_1", "MG_1", "MG_1", "MG_2", "MG_2",
                    "MG_2", "MG_2", "MG_2", "MG_2"
                ]

            }
            )
        df = AgentMovement.initialize_velocities(
            input_df,
            distribution,
            angle_dist,
            indexes,
            "mobility_group",
            "MG_3"
            )

        assert all(
            input_df["vx"][:].eq(df["vx"][:])
            ) & all(
                input_df["vy"][:].eq(df["vy"][:])
                )

    def test_initialize_velocities_preserve_dtypes_dict(
        self,
        fixture_initialize_velocities
    ):
        """
        Verifies whether `initialize_velocities` set the data types when
        a `preserve_dtypes_dict` is passed.
        """
        angle_dist = fixture_initialize_velocities[3]
        distribution = fixture_initialize_velocities[2]
        indexes = fixture_initialize_velocities[4]

        input_df = DataFrame(
            {
                "vx": random.randint(9, size=9),
                "vy": random.randint(9, size=9),
                "mobility_group": [
                    "MG_1", "MG_1", "MG_1", "MG_2", "MG_2",
                    "MG_2", "MG_2", "MG_2", "MG_2"
                ]

            }
            )
        preserve_dtypes_dict = {"vx": str, "vy": str}
        df = AgentMovement.initialize_velocities(
            input_df,
            distribution,
            angle_dist,
            indexes,
            "mobility_group",
            "MG_1",
            preserve_dtypes_dict
            )

        assert all(df["vx"].apply(lambda vx: isinstance(vx, str)))
        assert all(df["vy"].apply(lambda vy: isinstance(vy, str)))

    def test_initialize_velocities_indexes_not_None_group_field_not_in_df(
        self,
        fixture_initialize_velocities
    ):
        """
        Verifies whether `initialize_velocities` returns unaltered df when
        `group_field` passed is not in the input DataFrame.
        """
        angle_dist = fixture_initialize_velocities[3]
        distribution = fixture_initialize_velocities[2]

        input_df = DataFrame(
            {
                "vx": random.randint(9, size=9),
                "vy": random.randint(9, size=9),
                "mobility_group": ["MG_2" for i in range(9)]
            }
            )
        df = AgentMovement.initialize_velocities(
            input_df,
            distribution,
            angle_dist,
            None,
            "mobility_group",
            "MG_1"
            )

        assert all(
            input_df["vx"][:] == df["vx"][:]
            ) & all(
                input_df["vy"][:] == df["vy"][:]
                )

    def test_initialize_velocities_angle_distribution_constant(
        self,
        fixture_initialize_velocities
    ):
        """
        Verifies whether `vx` and `vy` agent velocities components are the same
        when the `angle_distribution` is set to constant with the constant
        equals to pi/4 for all the agents.
        """
        distribution = fixture_initialize_velocities[0]
        angle_dist = fixture_initialize_velocities[1]

        df = DataFrame(
            {"vx": random.randint(9, size=9), "vy": random.randint(9, size=9)}
            )
        df = AgentMovement.initialize_velocities(
            df,
            distribution,
            angle_dist,
            None,
            None,
            None
            )

        assert all(round(df["vx"], 12) == round(df["vy"], 12))

    def test_initialize_velocities_ValueError_indexes_and_group_field_not_None(
        self,
        fixture_initialize_velocities
    ):
        """
        Raises a ValueError when `vx` column is not in the input DataFrame,
        `indexes` and `group_field` are not None.
        """
        distribution = fixture_initialize_velocities[0]
        angle_dist = fixture_initialize_velocities[1]

        df = DataFrame(
            {
                "vy": random.randint(9, size=9),
                "mobility_group": ["MG_1" for i in range(9)]
            }
            )

        with pytest.raises(ValueError):
            AgentMovement.initialize_velocities(
                df,
                distribution,
                angle_dist,
                "mobility_group",
                "MG_1"
                )

    def test_initialize_velocities_ValueError_indexes_and_group_field_are_None(
        self,
        fixture_initialize_velocities
    ):
        """
        Raises a ValueError when `vx` column is not in the input DataFrame,
        `indexes` and `group_field` are None.
        """
        distribution = fixture_initialize_velocities[0]
        angle_dist = fixture_initialize_velocities[1]

        df = DataFrame({"vx": random.randint(9, size=9)})

        with pytest.raises(ValueError):
            AgentMovement.initialize_velocities(
                df,
                distribution,
                angle_dist
                )

    def test_initialize_velocities_raise_error_no_group_field(
        self,
        fixture_initialize_velocities
    ):
        """
        Raises a ValueError when `group_field` column is not in the input
        DataFrame.
        """
        distribution = fixture_initialize_velocities[0]
        angle_dist = fixture_initialize_velocities[1]

        df = DataFrame(
            {"vx": random.randint(9, size=9), "vy": random.randint(9, size=9)}
            )

        with pytest.raises(ValueError):
            assert AgentMovement.initialize_velocities(
                df,
                distribution,
                angle_dist,
                None,
                "mobility_group"
                )

    def test_initialize_velocities_only_indexes_is_not_None(
        self,
        fixture_initialize_velocities
    ):
        """
        Verifies whether `initialize_velocities` does not applies
        `set_velocities` when `group_label` is not in `group_field` column.
        """
        distribution = fixture_initialize_velocities[2]
        angle_dist = fixture_initialize_velocities[3]
        indexes = fixture_initialize_velocities[4]

        input_df = DataFrame(
            {
                "vx": random.randint(9, size=9),
                "vy": random.randint(9, size=9),
                "mobility_group": [
                    "MG_1", "MG_1", "MG_1", "MG_2", "MG_2",
                    "MG_2", "MG_2", "MG_2", "MG_2"
                ]

            }
            )
        df = AgentMovement.initialize_velocities(
            input_df,
            distribution,
            angle_dist,
            indexes,
            None,
            None
            )

        assert all(df["vx"][:5] == 1) & all(df["vy"][:5] == 0)
        assert all(
            input_df["vx"][5:] == df["vx"][5:]
            ) & all(
                input_df["vy"][5:] == df["vy"][5:]
                )

    def test_set_velocities(self, fixture_set_velocities):
        """
        Verifies whether set_velocities method assigns correctly new
        velocities to the agents of a  DataFrame, using a constant distribution
        for the norm of the velocities and a None `angle_distribution`.
        """
        distribution = fixture_set_velocities[0]

        df = DataFrame({"vx": [1, 2, 0, -1, -1], "vy": [0, 2, 1, 0, 1]})
        df = AgentMovement.set_velocities(df, distribution, 0.1)
        expected_df = DataFrame({"vx": pytest.vx, "vy": pytest.vy})

        assert all(round(df, 10) == round(expected_df, 10))

    def test_set_velocities_raise_error(self, fixture_set_velocities):
        """
        Raises a ValueError when `vy` column is not in the input
        DataFrame.
        """
        distribution = fixture_set_velocities[0]

        df = DataFrame({"vx": [1, 2, 0, -1, -1]})

        with pytest.raises(ValueError):
            AgentMovement.set_velocities(df, distribution, 0.1)

    def test_init_required_fields(
        self,
        set_up,
        fixture_init_required_fields
    ):
        """
        Verifies whether init_required_fields creates the columns:
        `x`, `y`, `vx`, `vy` of an input DataFrame, and verifies whether the
        velocity distribution was applied.
        """
        dist_title = fixture_init_required_fields[0]
        group_info = fixture_init_required_fields[1]

        mobility_groups = MobilityGroups(
            dist_title=dist_title,
            group_info=group_info
            )
        df = DataFrame(
            {
                "mobility_group": ["MG_1" for i in range(15)],
                "agent": [i for i in range(15)],
                "step": [i for i in range(15)]
            }
            )
        df = AgentMovement.init_required_fields(
            df,
            pytest.box_size,
            mobility_groups
            )

        assert all(df.columns.values == pytest.expected_columns)
        assert all(df["vx"] != inf) and all(df["vy"] != inf)

    def test_init_required_fields_positions(
        self,
        set_up,
        fixture_init_required_fields
    ):
        """
        Verifies whether `x`, `y` components of the agents are inside the
        `box_size`.
        """
        dist_title = fixture_init_required_fields[0]
        group_info = fixture_init_required_fields[1]

        mobility_groups = MobilityGroups(
            dist_title=dist_title,
            group_info=group_info
            )
        df = DataFrame(
            {
                "mobility_group": ["MG_1" for i in range(15)],
                "agent": [i for i in range(15)],
                "step": [i for i in range(15)]
            }
            )
        df = AgentMovement.init_required_fields(
            df,
            pytest.box_size,
            mobility_groups
            )

        assert all(df["x"] < pytest.box_size.right)
        assert all(df["x"] > pytest.box_size.left)
        assert all(df["y"] > pytest.box_size.bottom)
        assert all(df["y"] < pytest.box_size.top)

    def test_init_required_fields_angles(
        self,
        set_up,
        fixture_init_required_fields
    ):
        """
        Verifies whether the angles of the velocities of the agents are
        positives and minors than 2*pi.
        """
        dist_title = fixture_init_required_fields[0]
        group_info = fixture_init_required_fields[1]

        mobility_groups = MobilityGroups(
            dist_title=dist_title,
            group_info=group_info
            )
        df = DataFrame(
            {
                "mobility_group": ["MG_1" for i in range(15)],
                "agent": [i for i in range(15)],
                "step": [i for i in range(15)]
            }
            )
        df = AgentMovement.init_required_fields(
            df,
            pytest.box_size,
            mobility_groups)
        angles = Series(
            AgentMovement.angle(vx, vy) for (vx, vy) in zip(df["vx"], df["vy"])
        )

        assert all(angles.lt(2*pi))
        assert all(angles.ge(0))

    def test_init_required_fields_field(
        self,
        set_up,
        fixture_init_required_fields
    ):
        """
        Verifies whether are set the velocities of the agents for a group
        field and are initialized the others.
        """
        dist_title = fixture_init_required_fields[0]
        group_info = fixture_init_required_fields[2]

        mobility_groups = MobilityGroups(
            dist_title=dist_title,
            group_info=group_info
            )
        df = DataFrame(
            {
                "mobility_group": ["MG_1" for i in range(15)],
                "agent": [i for i in range(15)],
                "step": [i for i in range(15)]
            }
            )
        df.loc[0:9, "mobility_group"] = nan
        df = AgentMovement.init_required_fields(
            df,
            pytest.box_size,
            mobility_groups)

        assert all(df["vx"][0:10] == inf) and all(df["vy"][0:10] == inf)
        assert all(df["vx"][10:15] != inf) and all(df["vy"][10:15] != inf)

    def test_init_required_fields_no_field(
        self,
        set_up,
        fixture_init_required_fields
    ):
        """
        Initializes and no change the velocities when there is no
        `group_label` in the `mobility_group` column of the input DataFrame.
        """
        dist_title = fixture_init_required_fields[0]
        group_info = fixture_init_required_fields[2]

        mobility_groups = MobilityGroups(
            dist_title=dist_title,
            group_info=group_info
            )
        df = DataFrame(
            {
                "mobility_group": [None for i in range(15)],
                "agent": [i for i in range(15)],
                "step": [i for i in range(15)]
            }
            )
        df = AgentMovement.init_required_fields(
            df,
            pytest.box_size,
            mobility_groups
            )

        assert all(df["vy"] == inf) and all(df["vx"] == inf)
        assert set(["x", "y"]).issubset(df.columns)

    def test_movement_function(self, set_up):
        """Changes just the x agent position on the movement_function."""
        df = DataFrame(pytest.data)
        df = AgentMovement.move_agents(df, pytest.box_size, pytest.dt)

        assert 1.0 == df['x'][0]

    def test_crash_with_boundary_wall_(self, fixture_crash_with_wall):
        """Crash of one agent with each of the four box boundary wall."""
        df = DataFrame(pytest.data)
        df = AgentMovement.move_agents(df, pytest.box_size, pytest.dt)
        expected_df = DataFrame(pytest.expected_data)

        assert all(df == expected_df)

    def test_crash_with_boundary_corner(self, fixture_crash_with_corner):
        """Crash of one agent with each of the four box boundary corner."""
        df = DataFrame(pytest.data)
        df = AgentMovement.move_agents(df, pytest.box_size, pytest.dt)

        expected_df = DataFrame(pytest.expected_data)

        assert all(df == expected_df)

    def test_movement_function_field_error(self, fixture_raise_errors):
        """Raises an exception when the input DataFrame has na values."""
        df = DataFrame(pytest.data_na)

        with pytest.raises(ValueError, match=pytest.error_message):
            AgentMovement.move_agents(df, pytest.box_size, pytest.dt)

    def test_movement_function_field_existence(self, fixture_raise_errors):
        """
        Raises an exception when the input DataFrame does not have any of
        the columns: 'x', 'y', 'vx' and 'vy'.
        """
        df = DataFrame(pytest.data_without_x)

        with pytest.raises(KeyError):
            AgentMovement.move_agents(df, pytest.box_size, pytest.dt)

    def test_stop_agents(self, fixture_stop_agents):
        """Stops agent movement with a correct list of index."""
        df = DataFrame(pytest.data)
        df = AgentMovement.stop_agents(df, pytest.list_index_stopped)

        for i in range(len(pytest.list_index_stopped)):
            assert df['vx'][i] == df['vy'][i] == 0

    def test_stop_agents_raise_ValueError(
        self,
        fixture_stop_agents,
        fixture_raise_errors
    ):
        """
        Raises an exception when the input DataFrame columns `vx` or `vy`
        does not exist.
        """
        df = DataFrame(pytest.data_wrong_name_columns)
        with pytest.raises(ValueError):
            AgentMovement.stop_agents(df, pytest.list_index_stopped)

    @pytest.mark.parametrize(
        "input_angle, expected_angle",
        [(13*pi/4, 5*pi/4),
         (-pi/4, 7*pi/4),
         (0, 0)], ids=['13*pi/4 - 5*pi/4', '-pi/4 - 7*pi/4', '0 - 0']
    )
    def test_standardize_angle(self, input_angle, expected_angle):
        """Verifies standardization on the interval [0, 2*pi]."""
        angles = AgentMovement.standardize_angle(input_angle)

        assert round(angles, decimals=10) == round(expected_angle, decimals=10)

    @pytest.mark.parametrize(
        "x, y, expected_angle",
        [
            (-1, -1, 5*pi/4),
            (1, -1, 7*pi/4),
            (1, 0, 0.0)
        ], ids=['13*pi/4 - 5*pi/4', '-pi/4 - 7*pi/4', '2*pi - 2*pi']
    )
    def test_angle(self, x, y, expected_angle):
        """
        Verifies the standardized angle returned by the angle method
        of the agents with position components `x` and `y`.
        """
        angles = AgentMovement.angle(x, y)

        assert round(angles, decimals=10) == round(expected_angle, decimals=10)

    @pytest.mark.parametrize(
        "input_df, expected_angle",
        [
            (DataFrame({'x': [-1.0], 'y': [1.0]}), 3*pi/4),
            (DataFrame({'x': [-1.0], 'y': [0.0]}), pi)
        ], ids=['Case 1', 'Case 2']
    )
    def test_vector_angles(self, input_df, expected_angle):
        """
        Calculates the angle position of the agents with components
        `x` and `y` of the input DataFrame.
        """
        angle = AgentMovement.vector_angles(input_df, ['x', 'y'])

        assert round(angle[0], decimals=10) == \
            round(expected_angle, decimals=10)

    def test_vector_angles_raise_error_wrong_list(
        self,
        fixture_vector_angles_raise_error
    ):
        """
        Raises an exception when the input list does not have correct columns
        names, `vx` and `vy` in this case.
        """
        df = DataFrame(pytest.data)
        wrong_list = pytest.wrong_list

        with pytest.raises(ValueError):
            assert AgentMovement.vector_angles(df, wrong_list)

    def test_vector_angles_raise_error_correct_list(
        self,
        fixture_vector_angles_raise_error
    ):
        """
        Raises an exception when the input DataFrame columns are not in the
        list, `vx` and `vy` in this case.
        """
        df = DataFrame(pytest.wrong_data)
        correct_list = pytest.correct_list

        with pytest.raises(ValueError):
            assert AgentMovement.vector_angles(df, correct_list)

    def test_update_velocities_angle_variance_zero_indexes_group_field_None(
        self,
        fixture_update_velocities
    ):
        """
        Verifies whether there are no changes in the velocities components when
        the standard deviation of the numpy normal distribution is set to zero
        `angle_variance=0.0`. `indexes` and `group_field` is se to None.
        """
        df = DataFrame(pytest.data_large_sample)
        angles_before = AgentMovement.vector_angles(df, ['vx', 'vy'])

        df = AgentMovement.update_velocities(df, pytest.distrib, 0.0)
        angles_after = AgentMovement.vector_angles(df, ['vx', 'vy'])

        not_angle_variation = all(
            round(angles_before.head() - angles_after.head(), 7)
            )

        assert not_angle_variation == 0

    def test_update_velocities_comparison_angles_distribution(
        self,
        fixture_update_velocities
    ):
        """
        Comparison of the velocities magnitudes of agents after applying
        update velocities function through a Kolmogorov-smirnov. `indexes` and
        `group_field` is se to None.
        """
        df = DataFrame(pytest.data_large_sample)
        df = AgentMovement.update_velocities(df, pytest.distrib, 0.0)
        velocities_magnitude = sqrt(df['vx']**2 + df['vy']**2)
        k, p = kstest(velocities_magnitude.values - 10, 'norm')

        cond = True if p > 0.05 else False

        assert cond

    def test_update_velocities_comparison_KS_test(
            self,
            fixture_update_velocities
    ):
        """
        Comparison of the angles of the agents after applying update
        velocities through a Kolmogorov-smirnov test. `indexes` and
        `group_field` are set to None.
        """
        df = DataFrame(pytest.data_large_sample)
        angles_before = AgentMovement.vector_angles(df, ['vx', 'vy'])
        df = AgentMovement.update_velocities(
            df, pytest.distrib, pytest.angle_variance
            )
        angles_after = AgentMovement.vector_angles(df, ['vx', 'vy'])
        angle_variation = angles_after - angles_before
        k, p = kstest(angle_variation.values, pytest.delta_angles)

        cond = True if p > 0.05 else False

        assert cond

    def test_update_velocities_under_field_indexes_None(
        self,
        fixture_update_velocities
    ):
        """Updates velocities only for a group of agents under a field."""
        df = DataFrame(pytest.data_field)
        df = AgentMovement.update_velocities(
            df,
            pytest.distrib,
            pytest.angle_variance_field,
            None,
            "field",
            "field_1"
            )
        velocities_field_vx = df.loc[1, 'vx'] != 2.0
        velocities_field_vy = df.loc[1, 'vy'] != 2.0

        assert velocities_field_vx and velocities_field_vy

    def test_update_velocities_group_field_None(
        self,
        fixture_update_velocities
    ):
        """
        Comparison of the angles of the agents after applying update
        velocities through a Kolmogorov-smirnov test. `group_field` is set
        to None.
        """
        distribution = pytest.distrib
        sample_indexes = 400
        df = DataFrame(pytest.data_large_sample)

        angles_before = AgentMovement.vector_angles(
            df,
            ['vx', 'vy']
            )[:sample_indexes]
        indexes = [i for i in range(sample_indexes+1)]
        df = AgentMovement.update_velocities(
            df,
            distribution,
            pytest.angle_variance,
            indexes,
            None,
            None
            )
        angles_after = AgentMovement.vector_angles(
            df,
            ['vx', 'vy']
            )[:sample_indexes]
        angle_variation = angles_after - angles_before
        k, p = kstest(angle_variation.values, pytest.delta_angles)
        cond = True if p > 0.05 else False

        assert cond

    def test_update_velocities_group_field_and_indexes_not_None(
        self,
        fixture_update_velocities
    ):
        """
        Comparison of the angles of the agents after applying update
        velocities through a Kolmogorov-smirnov test. `indexes` and
        `group_field` are set not None.
        """
        distribution = pytest.distrib
        sample_indexes = 500
        delta_angles = pytest.delta_angles
        df = DataFrame(pytest.data_large_sample)
        df["mobility_profile"] = "MG_1"
        mobility_group_slice = 300
        df.loc[0: mobility_group_slice - 1, "mobility_profile"] = "MG_2"
        angles_before = AgentMovement.vector_angles(df, ['vx', 'vy'])
        indexes = [i for i in range(sample_indexes+1)]

        df = AgentMovement.update_velocities(
            df,
            distribution,
            pytest.angle_variance,
            indexes,
            "mobility_profile",
            "MG_2"
            )
        angles_after = AgentMovement.vector_angles(df, ['vx', 'vy'])
        angle_variation_1 = angles_after[:mobility_group_slice] - \
            angles_before[:mobility_group_slice]
        k, p_1 = kstest(angle_variation_1.values, delta_angles)
        angle_variation_2 = angles_after[mobility_group_slice:] - \
            angles_before[mobility_group_slice:]
        k, p_2 = kstest(angle_variation_2.values, delta_angles)

        cond_1 = True if p_1 > 0.05 else False
        cond_2 = True if p_2 < 0.05 else False

        assert cond_1 and cond_2

    def test_update_velocities_raise_error_indexes_and_group_field_None(
        self,
        fixture_update_velocities
    ):
        """
        Raises an exception when the input DataFrame columns `vx` and `vy`
        does not exist. `indexes` and `group_field` is se to None.
        """
        df = DataFrame(pytest.data_wrong_name_columns)

        with pytest.raises(ValueError):
            assert AgentMovement.update_velocities(
                df, pytest.distrib, pytest.angle_variance
                )

    @pytest.mark.parametrize(
        "input_df, expected_angle",
        [
            (DataFrame(
                {
                    "x_relative": [0, 1, 1],
                    "y_relative": [0, 1, -1]
                }
            ), pi),
            (DataFrame(
                {
                    "x_relative": [0, 0, 1],
                    "y_relative": [0, 1, 1]
                }
            ), 5*pi/4),
            (DataFrame(
                {
                    "x_relative": [1, 0, -1, -1],
                    "y_relative": [1, 1, 0,  1]
                }
            ), 13*pi/8)
        ],
        ids=["Max. angle = 3*pi/2", "Max. angle = pi/2", "Max. angle = 3*pi/2"]
    )
    def test_deviation_angle(self, input_df, expected_angle):
        """Verifies the deviation angle function in three different cases"""
        input_df["relative_angle"] = AgentMovement.vector_angles(
            input_df,
            ["x_relative", "y_relative"]
            )
        angle = AgentMovement.deviation_angle(input_df)

        assert round(angle, 12) == round(expected_angle, 12)

    def test_replace_velocities_different_components(
        self,
        fixture_replace_velocities_different_components
    ):
        """
        Verifies the replace velocity function on three different
        agents with different angles and components.
        """
        new_angles = Series(pytest.new_angles_data)
        df = DataFrame(pytest.data)
        df = df.apply(
            lambda row: AgentMovement.replace_velocities(row, new_angles),
            axis=1)

        for i in range(len(pytest.new_angles_list)):
            assert df.vx[i] == sqrt(2*i)*cos(pytest.new_angles_list[i])
            assert df.vy[i] == sqrt(2*i)*sin(pytest.new_angles_list[i])

    def test_replace_velocities_norm_equal_zero(
        self,
        fixture_replace_velocities_norm_equal_to_zero
    ):
        """
        Verifies the replace velocity function when one agent has its
        velocity norm equal to zero.
        """
        new_angle = Series(pytest.new_angle)
        df = DataFrame(pytest.data)
        df = df.apply(
            lambda row: AgentMovement.replace_velocities(row, new_angle),
            axis=1
            )

        assert df.vx[0] == df.vy[0] == 0

    def test_replace_velocities_same_components(
        self,
        fixture_replace_velocities_same_components
    ):
        """
        Verifies the replace velocity function on three different
        agents with the same velocities components.
        """
        new_angles = Series(pytest.new_angles_data)
        df = DataFrame(pytest.data)
        df = df.apply(
            lambda row: AgentMovement.replace_velocities(row, new_angles),
            axis=1
            )

        assert all(df.vy == sqrt(2)*sin(pi))
        assert all(df.vx == sqrt(2)*cos(pi))

    def test_avoid_agents_one_avoids_two(
        self,
        fixture_avoid_agents_same_rel_angles
    ):
        """One agent avoids two agents with the same relative angles."""
        df = DataFrame(pytest.data)
        df_to_avoid = DataFrame(pytest.data_avoid)
        df = AgentMovement.avoid_agents(df, df_to_avoid)
        expected_angle = 5*pi/4

        assert round(df.vx[0], 12) == round(cos(expected_angle), 12)
        assert round(df.vy[0], 12) == round(sin(expected_angle), 12)

    def test_avoid_agents_one_avoids_two_different_rel_angles(
        self,
        fixture_avoid_agents_one_avoids_two
    ):
        """
            One agent avoids two agents with different relative angles."""
        df = DataFrame(pytest.data)
        df_to_avoid = DataFrame(pytest.data_avoid)
        new_df = AgentMovement.avoid_agents(df, df_to_avoid)
        condition = round(
            new_df.vx[new_df.agent == 1][0] - -1.0, 7
            ) == round(
            new_df.vy[new_df.agent == 1][0] - 0, 7
            ) == 0

        assert condition

    def test_avoid_agents_two_avoid_one_different_rel_angles(
        self,
        fixture_avoid_agents_different_rel_angles
    ):
        """Two agents avoid one agent with different relative angles."""
        df = DataFrame(pytest.data)
        df_to_avoid = DataFrame(pytest.data_avoid)
        df = AgentMovement.avoid_agents(df, df_to_avoid)
        expected_angles = [3*pi/2, 7*pi/4]

        for i in range(len(expected_angles)):
            assert round(df.vx[i], 12) == round(cos(expected_angles[i]), 12)
            assert round(df.vy[i], 12) == round(sin(expected_angles[i]), 12)

    def test_avoid_agents_two_avoid_one(
        self,
        fixture_avoid_agents_two_agents_avoid_one
    ):
        """Two agents avoid one agent with the same relative angle."""
        df = DataFrame(pytest.data)
        df_to_avoid = DataFrame(pytest.data_avoid)
        df = AgentMovement.avoid_agents(df, df_to_avoid)
        expected_angles = [pi/2, pi/2]

        for i in range(len(expected_angles)):
            assert round(df.vx[i], 12) == round(cos(expected_angles[i]), 12)
            assert round(df.vy[i], 12) == round(sin(expected_angles[i]), 12)

    def test_avoid_agents_one_avoids_three(
        self,
        fixture_avoid_agents_one_agent_avoids_three
    ):
        """
            One agent avoids three agents with different relative angles.
        """
        df = DataFrame(pytest.data)
        df_to_avoid = DataFrame(pytest.data_avoid)
        df = AgentMovement.avoid_agents(df, df_to_avoid)
        expected_angle = pi

        assert round(df.vx[0], 12) ==  \
               round(sqrt(2)*cos(expected_angle), 12)
        assert round(df.vy[0], 12) == \
               round(sqrt(2)*sin(expected_angle), 12)

    def test_avoid_agents_one_agent_between_two(
        self,
        fixture_avoid_agents_one_agent_between_two
    ):
        """
        One agent avoids two agents diametrically opposite, i.e., with
        0 and pi relatives angles respectively.
        """
        df = DataFrame(pytest.data)
        df_to_avoid = DataFrame(pytest.data_avoid)
        df = AgentMovement.avoid_agents(df, df_to_avoid)
        expected_angle = pi/2

        assert round(df.vx[0], 12) == round(sqrt(2)*cos(expected_angle), 12)
        assert round(
            abs(df.vy[0]), 12) == round(sqrt(2)*sin(expected_angle), 12)

    def test_avoid_agents_one_avoids_four_in_each_axis(
        self,
        fixture_avoid_agents_one_avoids_four_in_each_axis
    ):
        """One agent avoids four agents in each axis."""
        df = DataFrame(pytest.data)
        df_to_avoid = DataFrame(pytest.data_avoid)
        df = AgentMovement.avoid_agents(df, df_to_avoid)
        expected_angle = pi/4

        assert round(abs(df.vx[0]), 12) == round(cos(expected_angle), 12)
        assert round(abs(df.vy[0]), 12) == round(sin(expected_angle), 12)

    def test_avoid_agents_raise_error(self, fixture_avoid_agents_raise_error):
        """
        Raises an exception when the input DataFrame column `agent`
        does not exist.
        """
        df = DataFrame(pytest.data_without_agent)
        df_to_avoid = DataFrame(pytest.data_avoid)

        with pytest.raises(ValueError):
            assert AgentMovement.avoid_agents(df, df_to_avoid)
