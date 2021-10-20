import pytest
from pandas import DataFrame, Series
from scipy.stats import kstest
from numpy import random, array, nan, all, pi, round, sqrt, cos, sin

from abmodel.agent.movement import AgentMovement
from abmodel.models.population import BoxSize
from abmodel.utils.distributions import Distribution


class TestCaseAgentMovement:
    """
        Verifies the functionality of all methods in the AgentMovement class
        from agent.
    """

    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    @pytest.fixture
    def set_up(self, autouse=True) -> None:
        pytest.box_size = BoxSize(-50, 50, -30, 30)
        pytest.dt = 1.0
        pytest.data = {
            'x': [0],
            'y': [0],
            'vx': [1.0],
            'vy': [0],
            }

        pytest.data_na = {
            'x': [nan],
            'y': [0],
            'vx': [1.0],
            'vy': [0],
            }

    @pytest.fixture
    def fixture_crash_with_wall(self, set_up) -> None:
        pytest.data = {
            'x': [49, 0, -49, 0],
            'y': [0, 29, 0, -29],
            'vx': [2.0, 2.0, -2.0, 2.0],
            'vy': [2.0, 2.0, 2.0, -2.0],
            }

        pytest.expected_data = {
            'x': [50.0, 2.0, -50.0, 2.0],
            'y': [2.0, 30.0, 2.0, -30.0],
            'vx': [-2.0, 2.0, 2.0, 2.0],
            'vy': [2.0, -2.0, 2.0, 2.0],
            }

    @pytest.fixture
    def fixture_crash_with_corner(self, set_up) -> None:
        pytest.data = {
            'x': [49, -49, -49, 49],
            'y': [29, 29, -29, -29],
            'vx': [2.0, -2.0, -2.0, 2.0],
            'vy': [2.0, 2.0, -2.0, -2.0],
            }

        pytest.expected_data = {
            'x': [50.0, -50.0, -50.0, 50.0],
            'y': [30.0, 30.0, -30.0, -30.0],
            'vx': [-2.0, 2.0, 2.0, -2.0],
            'vy': [-2.0, -2.0, 2.0, 2.0],
            }

    @pytest.fixture
    def fixture_raise_errors(self, set_up, scope='method') -> None:
        pytest.data_whitout_x = {
            'y': [0],
            'vx': [1.0],
            'vy': [0],
            }
        pytest.error_message = (
                    "Some columns might be initialized incorrectly.\n"
                    "To pinpoint especific errors, "
                    "add `debug=True` as a parameter")

        cols = ["x", "y", "vx", "vy"]
        check_cols = "x"
        error_string = "df must contain: " + ", ".join(cols) + ".\n"
        check_string = ", ".join(check_cols) + " must be checked"
        pytest.error_message2 = error_string + check_string

    @pytest.fixture
    def fixture_stop_agents(self) -> None:
        samples = 10
        sample_stopped = 5
        pytest.data = {
            'vx': random.randint(-20, 20, samples),
            'vy': random.randint(-20, 20, samples)
        }
        pytest.list_index_stopped = [x for x in range(sample_stopped)]
        pytest.data_wrong_name_columns = {
            'Vx': random.randint(-20, 20, samples),
            'VY': random.randint(-20, 20, samples)
        }

    @pytest.fixture
    def fixture_test_vector_angles_raise_error(self) -> None:
        pytest.data = {
            'x': [0],
            'y': [0],
            'vx': [1.0],
            'vy': [0],
            }

        pytest.wrong_data = {
            'X': [0],
            'Y': [0],
            'vx': [1.0],
            'vy': [0],
            }

        pytest.wrong_list = ['X', 'vX']
        pytest.correct_list = ['x', 'y']

    @pytest.fixture
    def fixture_change_velocities(self) -> None:
        pytest.angle_variance = 0.5
        samples = 500
        pytest.data = {
            'vx': -20*random.random(samples) + 10,
            'vy': -20*random.random(samples) + 10
        }

        pytest.constant_dist = Distribution(
        dist_type="constant",
        constant=1)

        pytest.delta_angles = Distribution(
            dist_type="numpy",
            dist_name="normal",
            loc=0.0,
            scale=pytest.angle_variance).sample(size=samples)

        pytest.data_Campo = {
            'Campo': array([0, 1]),
            'vx': array([1.0, 2.0]),
            'vy': array([0, 2.0]),
            }

        pytest.angle_variance_Campo = 1.0

        pytest.data_wrong_name_columns = {
            'Vx': random.randint(-20, 20, samples),
            'VY': random.randint(-20, 20, samples)
        }

    @pytest.fixture
    def fixture_update_velocities(self, scope='class') -> None:
        pytest.angle_variance = 0.1
        pytest.angle_variance_field = 0.1
        samples = 500
        pytest.data = {
            'vx': -20*random.random(samples) + 10,
            'vy': -20*random.random(samples) + 10
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
            scale=pytest.angle_variance).sample(size=samples)

        pytest.data_field = {
            'field': array([0, 1]),
            'vx': array([1.0, 2.0]),
            'vy': array([0, 2.0]),
            }

    @pytest.fixture
    def fixture_replace_velocities_different_components(self) -> None:
        pytest.new_angles_list = [pi, pi/2, pi/3]
        pytest.new_angles_data = \
            {k: v for (k, v) in zip(
                [k for k in range(1, 4, 1)], pytest.new_angles_list)}

        pytest.data = {
            'agent': [1, 2, 3],
            'x': [0, 1, 1],
            'y': [0, 1, -1],
            'vx': [0.0, 1.0, sqrt(2.0)],
            'vy': [0.0, 1.0, sqrt(2.0)],
            }

    @pytest.fixture
    def fixture_replace_velocities_norm_equal_to_zero(self) -> None:
        pytest.new_angle = {1: pi}
        pytest.data = {
            'agent': [1],
            'x': [1],
            'y': [-1],
            'vx': [0.0],
            'vy': [0.0],
            }

    @pytest.fixture
    def fixture_replace_velocities_same_components(self) -> None:
        pytest.data = {
            'agent': [1, 2, 3],
            'x': [0, 1, 1],
            'y': [0, 1, -1],
            'vx': [1.0, 1.0, 1.0],
            'vy': [1.0, 1.0, 1.0],
            }
        pytest.new_angles_data = {1: pi, 2: pi, 3: pi}

    @pytest.fixture
    def fixture_avoid_agents_same_rel_angles(self) -> None:
        pytest.data = {
            'agent': [1, 2, 3],
            'x': [0, 1, 2],
            'y': [0, 1, 2],
            'vx': [1.0, 10.0, 10],
            'vy': [0, 10.0, 10],
            }

        pytest.data_avoid = {
            'agent': [1, 1],
            'agent_to_avoid': [2, 3]
            }

    @pytest.fixture
    def fixture_avoid_agents_one_avoids_two(self) -> None:
        pytest.data = {
            'agent': [1, 2, 3],
            'x': [0, 1, 1],
            'y': [0, 1, -1],
            'vx': [1.0, 2.0, 0],
            'vy': [0, 2.0, 0],
            }

        pytest.data_avoid = {
            'agent': [1, 1],
            'agent_to_avoid': [2, 3]
            }

    @pytest.fixture
    def fixture_avoid_agents_different_rel_angles(self) -> None:
        pytest.data = {
            'agent': [1, 2, 3],
            'x': [0, 1, 0],
            'y': [0, 0, 1],
            'vx': [1.0, 0.0, 10],
            'vy': [0, 1, 10],
            }

        pytest.data_avoid = {
            'agent': [1, 2],
            'agent_to_avoid': [3, 3]
            }

    @pytest.fixture
    def fixture_avoid_agents_two_agents_avoid_one(self) -> None:
        pytest.data = {
            'agent': [1, 2, 3],
            'x': [0, 0, 0],
            'y': [-1, -2, -3],
            'vx': [1.0, 0.0, 10],
            'vy': [0, 1, 10],
            }

        pytest.data_avoid = {
            'agent': [1, 2],
            'agent_to_avoid': [3, 3]
            }

    @pytest.fixture
    def fixture_avoid_agents_one_agent_avoids_three(self) -> None:
        pytest.data = {
            'agent': [1, 2, 3, 4],
            'x': [-1, 1, 0, 0],
            'y': [0, 0, -1, 1],
            'vx': [1.0, 0.0, 10, 20],
            'vy': [1.0, 1, 10, 20],
            }

        pytest.data_avoid = {
            'agent': [1, 1, 1],
            'agent_to_avoid': [2, 3, 4]
            }

    @pytest.fixture
    def fixture_avoid_agents_raise_error(self) -> None:
        pytest.data_whitout_agent = {
            'x': [0, 1, 1],
            'y': [0, 1, -1],
            'vx': [1.0, 2.0, 0],
            'vy': [0, 2.0, 0],
            }

        pytest.data_avoid = {
            'agent': [1, 1],
            'agent_to_avoid': [2, 3]
            }

    def test_movement_function(self, set_up):
        """Change just the x agent position on the movement_function."""
        df = DataFrame(pytest.data)
        df = AgentMovement.move_agents(df, pytest.box_size, pytest.dt)

        assert 1.0 == df['x'][0]

    def test_crash_with_boundary_wall_(self, fixture_crash_with_wall):
        """Crash of one agent with each of the four box boundary wall."""
        df = DataFrame(pytest.data)
        df = AgentMovement.move_agents(df, pytest.box_size, pytest.dt)
        expected_df = DataFrame(pytest.expected_data)

        assert all(df == expected_df) == True

    def test_crash_with_boundary_corner(self, fixture_crash_with_corner):
        """Crash of one agent with each of the four box boundary corner."""
        df = DataFrame(pytest.data)
        df = AgentMovement.move_agents(df, pytest.box_size, pytest.dt)

        expected_df = DataFrame(pytest.expected_data)

        assert all(df == expected_df) == True

    def test_movement_function_field_error(self, fixture_raise_errors):
        """Raises an exception when the input DataFrame has na values."""
        df = DataFrame(pytest.data_na)

        with pytest.raises(ValueError, match=pytest.error_message):
            assert AgentMovement.move_agents(df, pytest.box_size, pytest.dt)

        with pytest.raises(ValueError, match=pytest.error_message):
            assert AgentMovement.move_agents(df, pytest.box_size, pytest.dt)

    def test_movement_function_field_existence(self, fixture_raise_errors):
        """Raises an exception when the input DataFrame does not have any of
        the columns ['x', 'y', 'vx', 'vy']"""
        df = DataFrame(pytest.data_whitout_x)

        with pytest.raises(ValueError, match=pytest.error_message2):
            assert AgentMovement.move_agents(df, pytest.box_size, pytest.dt)

    def test_stop_agents(self, fixture_stop_agents):
        """Stops agent movement with a correct list of index."""
        df = DataFrame(pytest.data)
        df = AgentMovement.stop_agents(df, pytest.list_index_stopped)

        for i in range(len(pytest.list_index_stopped)):
            assert df['vx'][i] == df['vy'][i] == 0

    def test_stop_agents_raise_Exception(self, fixture_stop_agents):
        """
        Raises an exception when the input DataFrame columns `vx` and `vy`
        does not exist.
        """
        df = DataFrame(pytest.data_wrong_name_columns)

        with pytest.raises(ValueError):
            assert AgentMovement.stop_agents(df, pytest.list_index_stopped)

    @pytest.mark.parametrize(
        "input_angle, expected_angle",
        [(13*pi/4, 5*pi/4),
         (-pi/4, 7*pi/4),
         (0, 0)], ids=['13*pi/4 - 5*pi/4', '-pi/4 - 7*pi/4', '0 - 0']
    )
    def test_standardize_angle(self, input_angle, expected_angle):
        """Verifies standardization on the interval [0, 2*pi]."""
        assert round(AgentMovement.standardize_angle(input_angle),
                     decimals=10) == round(expected_angle, decimals=10)

    @pytest.mark.parametrize(
        "x, y, expected_angle",
        [(-1, -1, 5*pi/4),
         (1, -1, 7*pi/4),
         (1, 0, 0.0)
        ], ids=['13*pi/4 - 5*pi/4', '-pi/4 - 7*pi/4', '2*pi - 2*pi']
    )
    def test_angle(self, x, y, expected_angle):
        """Verifies the standardized angle formed by the components `x` and `y`
        returned by the angle method."""
        assert round(AgentMovement.angle(x, y),
                     decimals=10) == round(expected_angle, decimals=10)

    @pytest.mark.parametrize(
        "input_df, expected_angle",
        [(DataFrame({'x': [-1.0], 'y': [1.0]}), 3*pi/4),
         (DataFrame({'x': [-1.0], 'y': [0.0]}), pi)], ids=['Case 1', 'Case 2']
    )
    def test_vector_angles(self, input_df, expected_angle):
        """
        Calculates the vector direction adequately between `x` and `y`
        components of the input DataFrame.
        """
        angle = AgentMovement.vector_angles(input_df, ['x', 'y'])

        assert round(angle[0], decimals=10) == \
            round(expected_angle, decimals=10)

    def test_vector_angles_raise_error_wrong_list(
            self, fixture_test_vector_angles_raise_error):
        """
        Raises an exception when the input list does not have correct columns
        names, `vx` and `vy` in this case.
        """
        df = DataFrame(pytest.data)
        wrong_list = pytest.wrong_list

        with pytest.raises(ValueError):
            assert AgentMovement.vector_angles(df, wrong_list)

    def test_vector_angles_raise_error_correct_list(
            self, fixture_test_vector_angles_raise_error):
        """
        Raises an exception when the input DataFrame columns are not in the
        list, `vx` and `vy` in this case.
        """
        df = DataFrame(pytest.wrong_data)
        correct_list = pytest.correct_list

        with pytest.raises(ValueError):
            assert AgentMovement.vector_angles(df, correct_list)

    def test_update_velocities_angle_variance_zero(
            self, fixture_update_velocities):
        """
        Verifies wheter there are no changes in the velocities components when
        the standard deviation of the numpy normal distribution is set to zero
        (angle_variance=0.0).
        """
        df = DataFrame(pytest.data)
        angles_before = AgentMovement.vector_angles(df, ['vx', 'vy'])

        df = AgentMovement.update_velocities(df, pytest.distrib, 0.0)
        angles_after = AgentMovement.vector_angles(df, ['vx', 'vy'])

        not_angle_variation = \
            all(round(angles_before.head() - angles_after.head(), 7)) == 0

        assert not_angle_variation == True

    def test_update_velocities_comparison_angles_distribution(
            self, fixture_update_velocities):
        """
        Comparison of the velocities magnitudes of agents after applying
        update velocities function through a Kolmogorov-smirnov.
        """
        df = DataFrame(pytest.data)
        df = AgentMovement.update_velocities(df, pytest.distrib, 0.0)
        velocities_magnitude = sqrt(df['vx']**2 + df['vy']**2)
        k, p = kstest(velocities_magnitude.values - 10, 'norm')

        if p > 0.05:
            velocity_distrib = True
        else:
            velocity_distrib = False

            assert velocity_distrib == True

    def test_update_velocities_comparison_KS_test(
            self, fixture_update_velocities):
        """
        Comparison of the angles of the agents after applying update
        velocities through a Kolmogorov-smirnov test.
        """
        df = DataFrame(pytest.data)
        angles_before = AgentMovement.vector_angles(df, ['vx', 'vy'])
        df = AgentMovement.update_velocities(
            df, pytest.distrib, pytest.angle_variance
            )
        angles_after = AgentMovement.vector_angles(df, ['vx', 'vy'])
        angle_variation = angles_after - angles_before
        k, p = kstest(angle_variation.values, pytest.delta_angles)
        if p > 0.05:
            angle_variation = True
        else:
            angle_variation = False

        assert angle_variation == True

    def test_update_velocities_under_field(self, fixture_update_velocities):
        """Updates velocities only for agents under a field."""
        df = DataFrame(pytest.data_field)
        df = AgentMovement.update_velocities(
            df, pytest.distrib, pytest.angle_variance_field,
            group_field='field',
            group_label=1
            )
        velocities_field_vx = df.loc[1, 'vx'] != 2.0
        velocities_field_vy = df.loc[1, 'vy'] != 2.0

        assert velocities_field_vx and velocities_field_vy == True

    def test_update_velocities_raise_error(self, fixture_update_velocities):
        """
        Raises an exception when the input DataFrame columns `vx` and `vy`
        does not exist.
        """
        df = DataFrame(pytest.data_wrong_name_columns)

        with pytest.raises(ValueError):
            assert AgentMovement.update_velocities(
                df, pytest.distrib, pytest.angle_variance
                )

    @pytest.mark.parametrize(
        "input_df, expected_angle",
        [(DataFrame(
            {'x_relative': [0, 1, 1],
            'y_relative': [0, 1, -1]}
            ), pi),
        (DataFrame(
            {'x_relative': [0, 0, 1],
            'y_relative': [0, 1, 1]}
            ), 5*pi/4),
        (DataFrame(
            {'x_relative': [1, -1, 0],
            'y_relative': [1, 0, -1]}),
            5*pi/8)],
        ids=["Max. angle = pi", "Max. angle = pi/2", "Max. angle = 3pi/4"]
    )
    def test_deviation_angle(self, input_df, expected_angle):
        """Verifies the deviation angle function in three different cases"""
        input_df['relative_angle'] = \
            AgentMovement.vector_angles(input_df, ['x_relative', 'y_relative'])
        angle = AgentMovement.deviation_angle(input_df)

        assert round(angle, 12) == round(expected_angle, 12)

    def test_replace_velocities_different_components(
            self, fixture_replace_velocities_different_components):
        """Verifies the replace velocity function on three different
        agents with differents angles and components."""
        new_angles = Series(pytest.new_angles_data)
        df = DataFrame(pytest.data)
        df = df.apply(
            lambda row: AgentMovement.replace_velocities(row, new_angles),
            axis=1
            )

        for i in range(len(pytest.new_angles_list)):
            assert df.vx[i] == sqrt(2*i)*cos(pytest.new_angles_list[i])
            assert df.vy[i] == sqrt(2*i)*sin(pytest.new_angles_list[i])

    def test_replace_velocities_norm_equal_zero(
            self, fixture_replace_velocities_norm_equal_to_zero):
        """Verifies the replace velocity function when one agent has its
        velocity norm equal to zero."""
        new_angle = Series(pytest.new_angle)
        df = DataFrame(pytest.data)
        df = df.apply(lambda row: AgentMovement.replace_velocities(row, new_angle), axis=1)

        assert df.vx[0] == df.vy[0] == 0

    def test_replace_velocities_same_components(
            self, fixture_replace_velocities_same_components):
        """Verifies the replace velocity function on three different
        agents with the same velocities components."""
        new_angles = Series(pytest.new_angles_data)
        df = DataFrame(pytest.data)
        df = df.apply(
            lambda row: AgentMovement.replace_velocities(row, new_angles),
            axis=1
            )

        assert all(df.vy == sqrt(2)*sin(pi))
        assert all(df.vx == sqrt(2)*cos(pi))

    def test_avoid_agents_one_avoids_two(
            self, fixture_avoid_agents_same_rel_angles):
        """One agent avoids two agents with the the same relative angles."""
        df = DataFrame(pytest.data)
        df_to_avoid = DataFrame(pytest.data_avoid)
        df = AgentMovement.avoid_agents(df, df_to_avoid)
        expected_angle = 5*pi/4

        assert round(df.vx[0], 12) == round(cos(expected_angle), 12)
        assert round(df.vy[0], 12) == round(sin(expected_angle), 12)

    def test_avoid_agents_one_avoids_two_different_relative_angles(
            self, fixture_avoid_agents_one_avoids_two):
        """One agent avoids two angets with different relative angles"""
        df = DataFrame(pytest.data)
        df_to_avoid = DataFrame(pytest.data_avoid)
        new_df = AgentMovement.avoid_agents(df, df_to_avoid)
        condition = round(new_df.vx[new_df.agent == 1][0] - -1.0, 7) == 0 \
            and round(new_df.vy[new_df.agent == 1][0] - 0, 7) == 0

        assert condition == True

    def test_avoid_agents_two_avoid_one_different_rel_angles(
            self, fixture_avoid_agents_different_rel_angles):
        """Two agents avoid one agent with different relative angles"""
        df = DataFrame(pytest.data)
        df_to_avoid = DataFrame(pytest.data_avoid)
        df = AgentMovement.avoid_agents(df, df_to_avoid)
        expected_angles = [3*pi/2, 7*pi/4]

        for i in range(len(expected_angles)):

            assert round(df.vx[i], 12) == round(cos(expected_angles[i]), 12)
            assert round(df.vy[i], 12) == round(sin(expected_angles[i]), 12)

    def test_avoid_agents_two_avoid_one(
            self, fixture_avoid_agents_two_agents_avoid_one):
        """Two agents avoid one agent with the same realtive angle"""
        df = DataFrame(pytest.data)
        df_to_avoid = DataFrame(pytest.data_avoid)
        df = AgentMovement.avoid_agents(df, df_to_avoid)
        expected_angles = [pi/2, pi/2]

        for i in range(len(expected_angles)):

            assert round(df.vx[i], 12) == round(cos(expected_angles[i]), 12)
            assert round(df.vy[i], 12) == round(sin(expected_angles[i]), 12)

    def test_avoid_agents_one_avoids_three(
            self, fixture_avoid_agents_one_agent_avoids_three):
        """One agent avoids three agents with different relative angles"""
        df = DataFrame(pytest.data)
        df_to_avoid = DataFrame(pytest.data_avoid)
        df = AgentMovement.avoid_agents(df, df_to_avoid)
        expected_angle = pi

        assert round(df.vx[0], 12) == round(sqrt(2)*cos(expected_angle), 12)
        assert round(df.vy[0], 12) == round(sqrt(2)*sin(expected_angle), 12)

    def test_avoid_agents_raise_error(self, fixture_avoid_agents_raise_error):
        """
        Raises an exception when the input DataFrame column 'agent'
        does not exist.
        """
        df = DataFrame(pytest.data_whitout_agent)
        df_to_avoid = DataFrame(pytest.data_avoid)

        with pytest.raises(ValueError):
            assert AgentMovement.avoid_agents(df, df_to_avoid)
