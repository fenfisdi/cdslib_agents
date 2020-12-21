import pytest
from itertools import product

import pandas as pd
import numpy as np

from agents import behaviour

# All combinations of x, y, vx, vy (positive, negative or zero)
possible_values = [1., 0, -1.]
permutations = np.array(
    [np.array(values) for values in product(possible_values, repeat=4)]
)
permutations = permutations.T
x, y, vx, vy = permutations[0], permutations[1], permutations[2], permutations[3]


@pytest.fixture
def small_df():
    data = {'x': x, 'y': y, 'vx': vx, 'vy': vy}
    df = pd.DataFrame(data)
    return df


def test_behaviour_move_agent(small_df: pd.DataFrame):
    """Test movement of agents using several combinations of positive, negative
    and zero values in positions and velocities."""
    def q_new(q, v, dt):
        return q + v * dt
    
    dtime = 1
    new_df = behaviour.move_agent(small_df, dtime)
    
    for i in range(len(new_df)):
        x_expected = q_new(x[i], vx[i], dtime)
        y_expected = q_new(y[i], vy[i], dtime)
        
        agent = new_df.iloc[i]
        
        x_test = agent['x'] == pytest.approx(x_expected, rel=0.99)
        y_test = agent['y'] == pytest.approx(y_expected, rel=0.99)
        
        assert x_test and y_test
