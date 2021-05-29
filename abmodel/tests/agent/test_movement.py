from unittest import TestCase

import numpy as np
import pandas as pd

from abmodel.agent.movement import AgentMovement
from abmodel.models.population import BoxSize
from abmodel.utils.distributions import Distribution


class AgentMovementTestCase(TestCase):

    def setUp(self):
        self.box_size = BoxSize(-50, 50, -30, 30)
        self.dt = 1.0

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
            df = AgentMovement.move_agents(df, self.box_size, self.dt)

        self.assertNotEqual(data.get('x')[0], df['x'][0])
        
        

    def test_movement_walls(self):
        #samples = 1
        iterations = 1

        data = {
            'x': np.array([0]),
            'y': np.array([0]),
            'vx': np.array([1.0]),  #cambia resultado si se pone entero o float (vel = 1 o a 1.0 para dt = 0.5
            'vy': np.array([0]),
        }
        df = pd.DataFrame(data)

        for _ in range(iterations):
             df = AgentMovement.move_agents(df, self.box_size, self.dt)
            #print('iteré:')
        print(df)
        self.assertAlmostEqual(1.0, df['x'][0])        
        
        

    def test_stop_agents(self):
        samples = 2
        iterations = 10

        data = {
            'x': np.random.randint(-20, 20, samples),
            'y': np.random.randint(-20, 20, samples),
            'vx': -20 * np.random.random(samples) + 10,
            'vy': -20 * np.random.random(samples) + 10,
        }
        df = pd.DataFrame(data)

        for _ in range(iterations):
            df = AgentMovement.stop_agents(df, [1])
            
        cond1 = df['vx'][1] == 0.0
        cond2 = df['vy'][1] == 0.0

        self.assertTrue(cond1 and cond2) 
    
    
    def test_vector_angles(self):

        data = {
            'x': np.array([0]),
            'y': np.array([0]),
            'vx': np.array([-1.0]),  
            'vy': np.array([1.0]),
        }
        df = pd.DataFrame(data)

        df = AgentMovement.vector_angles(df, ['vx', 'vy'])
            #print('iteré:')
        print(df)
        self.assertAlmostEqual(3*np.pi/4, df[0]) 
        
    
    def test_update_velocities(self):

        data = {
            'x': np.array([0]),
            'y': np.array([0]),
            'vx': np.array([1.0]),  
            'vy': np.array([0]),
        }
        df = pd.DataFrame(data)
        Distrib = Distribution(
                dist_type="numpy",
                distribution="normal",
                loc=0.0,
                scale=1.0   #angle_variance
                )
            #print('iteré:')
        df = AgentMovement.update_velocities(df, Distrib, 1.0)
        print(df)
        self.assertNotEqual(1.0, df['vx'][0])        
               
        