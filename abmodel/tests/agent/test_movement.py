from unittest import TestCase

import numpy as np
import pandas as pd

from abmodel.agent.movement import AgentMovement
from abmodel.models.population import BoxSize


class AgentMovementTestCase(TestCase):

    def setUp(self):
        self.box_size = BoxSize(-50, 50, -30, 30)
        self.dt = 1

    def test_movement_function(self):
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
            df = df.apply(
                AgentMovement.move_agents,
                axis=1,
                box_size=self.box_size,
                dt=self.dt
            )

        self.assertNotEqual(data.get('x')[0], df['x'][0])