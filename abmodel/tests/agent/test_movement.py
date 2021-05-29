from unittest import TestCase

import numpy as np
import pandas as pd

from abmodel.agent.movement import AgentMovement
from abmodel.models.population import BoxSize
from abmodel.utils.distributions import Distribution


class AgentMovementTestCase(TestCase):
    """
    """
    def setUp(self):
        """
        """
        self.box_size = BoxSize(-50, 50, -30, 30)
        self.dt = 1.0

    def test_movement_function_1(self):
        """
        """
        print("\n")
        print("Test #1: Change all agents' positions")
    
        samples = 50
        iterations = 10

        data = {
            'x': np.random.randint(-20, 20, samples),
            'y': np.random.randint(-20, 20, samples),
            'vx': -20 * np.random.random(samples) + 10,
            'vy': -20 * np.random.random(samples) + 10,
        }
        df = pd.DataFrame(data)

        for _ in range(iterations):
            df = AgentMovement.move_agents(df, self.box_size, self.dt)

        self.assertNotEqual(data.get('x')[0], df['x'][0])

    def test_movement_function_2(self):
        """
        """
        print("\n")
        print("Test #2: Change just one agent position")

        data = {
            'x': np.array([0]),
            'y': np.array([0]),
            'vx': np.array([1.0]),
            'vy': np.array([0]),
            }
        df = pd.DataFrame(data)

        df = AgentMovement.move_agents(df, self.box_size, self.dt)

        self.assertAlmostEqual(1.0, df['x'][0])

    def test_stop_agents(self):
        """
        """
        print("\n")
        print("Test: Change just one agent position")

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
        print("Test: Calculate vector direction adequately")

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

    def test_update_velocities(self):
        """
        """
        print("\n")
        print("Test: Calculate vector direction adequately")

        data = {
            'x': np.array([0]),
            'y': np.array([0]),
            'vx': np.array([1.0]),
            'vy': np.array([0]),
            }
        df = pd.DataFrame(data)
        distrib = Distribution(
            dist_type="numpy",
            distribution="normal",
            loc=0.0,
            scale=1.0
            )
        #print('iteré:')
        df = AgentMovement.update_velocities(df, distrib, 1.0)
        print(df)
        self.assertNotEqual(1.0, df['vx'][0])        
