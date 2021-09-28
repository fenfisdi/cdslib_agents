import pytest

from numpy import random, array, nan, all, pi, round, sqrt
from pandas import DataFrame

from abmodel.agent.movement import AgentMovement
from abmodel.models.population import BoxSize
from abmodel.utils.distributions import Distribution
from scipy.stats import kstest

class TestCaseAgentMovement:
    """
        Verify the functionality of all methods in the AgentMovement class
        from agent, using unitary test with the Python testing tool pytest.
    """

    def setup_method(self, method):
        print('==>')
        print(method.__doc__)


    @pytest.fixture
    def setUp(self, autouse = True) -> None:

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
    def fixture_crash_with_wall(self, setUp, scope = 'method') -> None:

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
    def fixture_crash_with_corner(self, setUp, scope = 'method') -> None:

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
    def fixture_stop_agents(self, scope = 'method') -> None:

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
    def fixture_test_vector_angles_raise_error(self, scope = 'method') -> None:

        pytest.data = {
            'x': [0],
            'y': [0],
            'vx': [1.0],
            'vy': [0],
            }

        pytest.wrong_list = ['X' , 'vx']

    @pytest.fixture
    def fixture_update_velocities(self, scope = 'class') -> None:

        pytest.angle_variance = 0.1
        samples = 500
        pytest.data = {
            'vx': -20*random.random(samples) +10,
            'vy': -20*random.random(samples) +10
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
            scale=pytest.angle_variance
            ).sample(size=samples)

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
    def fixture_avoid_agents(self, scope = 'class'):

        pytest.data_df1 = {
            'agent': [1, 2, 3],
            'x': [0, 1, 1],
            'y': [0, 1, -1],
            'vx': [1.0, 2.0, 0],
            'vy': [0, 2.0, 0],
            }

        pytest.data_df2 = {
            'agent': [1, 1],
            'agent_to_avoid': [2, 3]
            }

        pytest.data_whitout_agent = {
            'x': [0, 1, 1],
            'y': [0, 1, -1],
            'vx': [1.0, 2.0, 0],
            'vy': [0, 2.0, 0],
            }

    def test_movement_function(self,setUp):
        """Change just the x agent position on the movement_function."""

        df = DataFrame(pytest.data)
        df = AgentMovement.move_agents(df, pytest.box_size, pytest.dt)

        assert 1.0 == df['x'][0]


    def test_crash_with_boundary_wall_(self, fixture_crash_with_wall):
        """Crash of one agent with a box boundary wall."""

        df = DataFrame(pytest.data)
        df = AgentMovement.move_agents(df, pytest.box_size, pytest.dt)
        expected_df = DataFrame(pytest.expected_data)

        assert all(df == expected_df) == True


    def test_crash_with_boundary_corner(self, fixture_crash_with_corner):
        """Crash of one agent with a box boundary corner."""

        df = DataFrame(pytest.data)
        df = AgentMovement.move_agents(df, pytest.box_size, pytest.dt)

        expected_df = DataFrame(pytest.expected_data)

        assert all(df == expected_df) == True


    def test_movement_function_field_error(self, setUp):
        """Raise an exception when the input DataFrame has na values."""

        df = DataFrame(pytest.data_na)

        with pytest.raises(ValueError):
            assert AgentMovement.move_agents(df, pytest.box_size, pytest.dt)


    def test_stop_agents(self, fixture_stop_agents):
        """Stop agent movement with a correct list of index."""

        df = DataFrame(pytest.data)
        df = AgentMovement.stop_agents(df, pytest.list_index_stopped)

        for i in range(len(pytest.list_index_stopped)):
            assert df['vx'][i] == df['vy'][i] == 0


    def test_stop_agents_raise_Exception(self, fixture_stop_agents):
        """Raise an exception when the input DataFrame columns 'vx' and 'vy' does not exists."""

        df = DataFrame(pytest.data_wrong_name_columns)

        with pytest.raises(ValueError):
            assert AgentMovement.stop_agents(df, pytest.list_index_stopped)


    @pytest.mark.parametrize(
        "input_angle, expected_angle",[
        (13*pi/4, 5*pi/4),
        (-pi/4, 7*pi/4),
        (0, 0)
        ],
        ids=['13*pi/4 - 5*pi/4', '-pi/4 - 7*pi/4', '0 - 0']
    )
    def test_standardize_angle(self, input_angle, expected_angle):
        """Verify standarization on the interval [0, 2*pi]"""

        assert round(AgentMovement.standardize_angle(input_angle), decimals =10) == round(expected_angle, decimals =10)


    @pytest.mark.parametrize(
        "input_df, expected_angle", [
        (DataFrame({
            'x': [-1.0],
            'y': [1.0],
            }), 3*pi/4),
        (DataFrame({
            'x': [-1.0],
            'y': [0.0],
            }), pi)
    ], ids=['Case 1', 'Case 2']
    )
    def test_vector_angles(self, input_df, expected_angle):
        """Calculate vector direction adequately between 'x' and 'y' component of the input DataFrame."""

        angle = AgentMovement.vector_angles(input_df, ['x', 'y'])

        assert round(angle[0], decimals =10) == round(expected_angle, decimals =10)


    def test_vector_angles_raise_error(self, fixture_test_vector_angles_raise_error):
        """Raise an exception when the input DataFrame columns 'vx' and 'vy' does not exists."""

        df = DataFrame(pytest.data)
        wrong_list = (pytest.wrong_list)

        with pytest.raises(ValueError):
            assert AgentMovement.vector_angles(df, wrong_list)


    def test_update_velocities_angle_variance_0(self, fixture_update_velocities):
        """Not variations in the direction of agent (angle_variance = 0.0)."""


        df = DataFrame(pytest.data)
        angles_before = AgentMovement.vector_angles(df, ['vx', 'vy'])


        df = AgentMovement.update_velocities(df, pytest.distrib, 0.0)
        angles_after = AgentMovement.vector_angles(df, ['vx', 'vy'])


        not_angle_variation = \
            all(round(angles_before.head() - angles_after.head(), 7)) == 0

        assert not_angle_variation == True


    def test_update_velocities_comparation_normal_distribution(self, fixture_update_velocities):
        """Comparation of the magnitude velocities of agents with a given distribution (normal), through a Kolmogorov-smirnov test."""

        df = DataFrame(pytest.data)
        df = AgentMovement.update_velocities(df, pytest.distrib, 0.0)
        velocities_magnitude = sqrt(df['vx']**2 + df['vy']**2)
        k, p = kstest(velocities_magnitude.values - 10, 'norm')
        if p > 0.05:
            velocity_distrib = True
        else:
            velocity_distrib = False

            assert velocity_distrib == True


    def test_update_velocities_3(self, fixture_update_velocities):
        """Comparation of the angles of agents with a given distribution (normal), through a Kolmogorov-smirnov test."""

        df = DataFrame(pytest.data)
        angles_before = AgentMovement.vector_angles(df, ['vx', 'vy'])
        df = AgentMovement.update_velocities(
            df, pytest.distrib, pytest.angle_variance
            )
        angles_after = AgentMovement.vector_angles(df, ['vx', 'vy'])
        #np.savetxt('Data angles_after.csv', angles_after)
        angle_variation = angles_after - angles_before
        k, p = kstest(angle_variation.values, pytest.delta_angles)
        if p > 0.05:
            angle_variation = True
        else:
            angle_variation = False

        assert angle_variation == True


    def test_update_velocities_under_field(self, fixture_update_velocities):
        """Update velocities only for agents under a field."""

        df = DataFrame(pytest.data_Campo)
        df = AgentMovement.update_velocities(
            df, pytest.distrib, pytest.angle_variance_Campo,
            group_field='Campo',
            group_label=1
            )
        velocities_field_vx = df.loc[1, 'vx'] != 2.0
        velocities_field_vy = df.loc[1, 'vy'] != 2.0

        assert velocities_field_vx and velocities_field_vy == True


    def test_update_velocities_raise_error(self, fixture_update_velocities):
        """Raise an exception when the input DataFrame columns 'vx' and 'vy' does not exists."""

        df = DataFrame(pytest.data_wrong_name_columns)

        with pytest.raises(ValueError):
            assert AgentMovement.update_velocities(df, pytest.distrib, pytest.angle_variance)


    def test_avoid_agents(self, fixture_avoid_agents):
        """Avoid one agent of a DataFrame."""

        df = DataFrame(pytest.data_df1)
        df_to_avoid = DataFrame(pytest.data_df2)
        new_df = AgentMovement.avoid_agents(df, df_to_avoid)
        condition = round(new_df.vx[new_df.agent == 1][0] - -1.0, 7) == 0 \
            and round(new_df.vy[new_df.agent == 1][0] - 0, 7) == 0

        assert condition == True


        def test_avoid_agents_raise_error(self, fixture_avoid_agents):
            """Raise an exception when the input DataFrame column 'agent' does not exists"""

            df = DataFrame(pytest.data_whitout_agent)
            df_to_avoid = DataFrame(pytest.data_df2)

            with pytest.raises(ValueError):
                assert AgentMovement.avoid_agents(df, df_to_avoid)
