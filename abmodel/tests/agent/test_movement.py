from unittest import TestCase

import numpy as np
import pandas as pd

from abmodel.agent.movement import AgentMovement
from abmodel.models.population import BoxSize
from abmodel.utils.distributions import Distribution
from scipy.stats import kstest


class AgentMovementTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        self.box_size = BoxSize(-50, 50, -30, 30)
        self.dt = 1.0

    def test_movement_function(self):
        """
        """
        print("\n")
        print("Test #1: Change just one agent position")

        data = {
            'x': np.array([0]),
            'y': np.array([0]),
            'vx': np.array([1.0]),
            'vy': np.array([0]),
            }
        print('Test before movement')
        df = pd.DataFrame(data)
        print(df)

        print('Test after movement')
        df = AgentMovement.move_agents(df, self.box_size, self.dt)
        print(df)

        self.assertAlmostEqual(1.0, df['x'][0])

    def test_crash_with_boundaries(self):
        """
        """
        print("\n")
        print("Test #2: Crash of one agent with Box Boundaries")

        print("Crash with a wall")
        data = {
            'x': np.array([49, 0, -49, 0]),
            'y': np.array([0, 29, 0, -29]),
            'vx': np.array([2.0, 2.0, -2.0, 2.0]),
            'vy': np.array([2.0, 2.0, 2.0, -2.0]),
            }
        print('Test before movement')
        df = pd.DataFrame(data)
        print(df)

        print('Test after movement')
        df = AgentMovement.move_agents(df, self.box_size, self.dt)
        print(df)

        cond1 = np.all(df['x'] == np.array([50.0, 2.0, -50.0, 2.0]))
        cond2 = np.all(df['y'] == np.array([2.0, 30.0, 2.0, -30.0]))
        cond3 = np.all(df['vx'] == np.array([-2.0, 2.0, 2.0, 2.0]))
        cond4 = np.all(df['vy'] == np.array([2.0, -2.0, 2.0, 2.0]))

        good_crash_walls = np.all([cond1, cond2, cond3, cond4])

        print("Crash with a corners")

        data = {
            'x': np.array([49, -49, -49, 49]),
            'y': np.array([29, 29, -29, -29]),
            'vx': np.array([2.0, -2.0, -2.0, 2.0]),
            'vy': np.array([2.0, 2.0, -2.0, -2.0]),
            }
        print('Test before movement')
        df = pd.DataFrame(data)
        print(df)

        print('Test after movement')
        df = AgentMovement.move_agents(df, self.box_size, self.dt)
        print(df)

        cond1 = np.all(df['x'] == np.array([50.0, -50.0, -50.0, 50.0]))
        cond2 = np.all(df['y'] == np.array([30.0, 30.0, -30.0, -30.0]))
        cond3 = np.all(df['vx'] == np.array([-2.0, 2.0, 2.0, -2.0]))
        cond4 = np.all(df['vy'] == np.array([-2.0, -2.0, 2.0, 2.0]))
        good_crash_corners = np.all([cond1, cond2, cond3, cond4])

        self.assertTrue(good_crash_walls and good_crash_corners)

    def test_stop_agents(self):
        """
        """
        print("\n")
        print("Test #3: Stop one agent movement")

        samples = 2

        data = {
            'vx': -20 * np.random.random(samples) + 10,
            'vy': -20 * np.random.random(samples) + 10,
        }
        df = pd.DataFrame(data)

        print("Before applying stop_agents:")
        print(df)

        df = AgentMovement.stop_agents(df, [1])

        print("After applying stop_agents stopping 2nd agent (index=1):")
        print(df)

        cond1 = df['vx'][1] == 0.0
        cond2 = df['vy'][1] == 0.0

        self.assertTrue(cond1 and cond2)

    def test_vector_angles(self):
        """
        """
        print("\n")
        print("Test #4: Calculate vector direction adequately")

        data = {
            'x': np.array([-1.0]),
            'y': np.array([1.0]),
            }
        df = pd.DataFrame(data)

        print("The vector points towards 3*pi/4:")
        print(df)

        angles = AgentMovement.vector_angles(df, ['x', 'y'])

        print("The calculated angle is:")
        print(angles)
        self.assertAlmostEqual(3*np.pi/4, angles[0])

    def test_update_velocities_1(self):
        """
        """
        print("\n")
        print("Test #5.1: Not variations in the direction of agent")
        samples = 500

        data = {
            'vx': -20 * np.random.random(samples) + 10,
            'vy': -20 * np.random.random(samples) + 10,
        }

        df = pd.DataFrame(data)

        distrib = Distribution(
            dist_type="numpy",
            dist_name="normal",
            loc=10.0,
            scale=0.1
            )

        angles_before = AgentMovement.vector_angles(df, ['vx', 'vy'])
        print(angles_before[26])

        df = AgentMovement.update_velocities(df, distrib, 0.0)

        angles_after = AgentMovement.vector_angles(df, ['vx', 'vy'])
        print(angles_after[26])

        not_angle_variation = \
            round(angles_before[26] - angles_after[26], 7) == 0

        self.assertTrue(not_angle_variation)

    def test_update_velocities_2(self):
        """
        """
        print("\n")
        print("Test #5.2: New velocities of agents with a given distribution")
        samples = 500

        data = {
            'vx': -20 * np.random.random(samples) + 10,
            'vy': -20 * np.random.random(samples) + 10,
        }

        distrib = Distribution(
            dist_type="numpy",
            dist_name="normal",
            loc=10.0,
            scale=1.0
            )

        df = pd.DataFrame(data)

        df = AgentMovement.update_velocities(df, distrib, 0.0)

        velocities_magnitude = np.sqrt(df['vx']**2 + df['vy']**2)
        print(velocities_magnitude.values)

        k, p = kstest(velocities_magnitude.values - 10, 'norm')
        print(p)
        if p > 0.05:
            velocity_distrib = True
        else:
            velocity_distrib = False

        self.assertTrue(velocity_distrib)

    def test_update_velocities_3(self):
        """
        """
        print("\n")
        print("Test #5.3: New angles of agents with a given distribution")
        samples = 500

        data = {
            'vx': -20 * np.random.random(samples) + 10,
            'vy': -20 * np.random.random(samples) + 10,
        }

        angle_variance = 0.1

        distrib = Distribution(
            dist_type="numpy",
            dist_name="normal",
            loc=10.0,
            scale=1.0
            )

        delta_angles = Distribution(
            dist_type="numpy",
            dist_name="normal",
            loc=0.0,
            scale=angle_variance
            ).sample(size=samples)

        df = pd.DataFrame(data)

        angles_before = AgentMovement.vector_angles(df, ['vx', 'vy'])

        df = AgentMovement.update_velocities(
            df, distrib, angle_variance
            )

        angles_after = AgentMovement.vector_angles(df, ['vx', 'vy'])

        np.savetxt('Data angles_after.csv', angles_after)

        angle_variation = angles_after - angles_before

        k, p = kstest(angle_variation.values, delta_angles)
        print(f'p-value: {p}')
        if p > 0.05:
            angle_variation = True
        else:
            angle_variation = False

        self.assertTrue(angle_variation)

    def test_update_velocities_4(self):
        """
        """
        print("\n")
        print("Test #5.4: New velocities only for agents under a field")
        samples = 500

        data = {
            'vx': -20 * np.random.random(samples) + 10,
            'vy': -20 * np.random.random(samples) + 10,
        }

        distrib = Distribution(
            dist_type="numpy",
            dist_name="normal",
            loc=10.0,
            scale=1.0
            )

        data = {
            'Campo': np.array([0, 1]),
            'vx': np.array([1.0, 2.0]),
            'vy': np.array([0, 2.0]),
            }

        df = pd.DataFrame(data)
        print(df)

        df = AgentMovement.update_velocities(
            df, distrib, 1.0,
            group_field='Campo',
            group_label=1
            )
        print(df)

        velocities_field = df['vx'][1] != 2.0

        self.assertTrue(velocities_field)
    
    def test_avoid_agents(self):

        data = {
            'agent': np.array([1, 2, 3]),
            'x': np.array([0, 1, 1]),
            'y':np.array([0, 1, -1]),
            'vx': np.array([1.0, 2.0, 0]),
            'vy': np.array([0, 2.0, 0]),
            }
        
        df = pd.DataFrame(data)
        print(df)

        data = {
            'agent': np.array([1,1]),
            'agent_to_avoid': np.array([2, 3])
            }
        
        df_to_avoid = pd.DataFrame(data)
        print(df_to_avoid)
        
        new_df = AgentMovement.avoid_agents(df, df_to_avoid)
        
        print(new_df)
        
        condition = round(new_df.vx[new_df.agent == 1][0] - -1.0, 7) == 0 \
            and round(new_df.vy[new_df.agent == 1][0] - 0, 7) == 0
            
        self.assertTrue(condition)
        
