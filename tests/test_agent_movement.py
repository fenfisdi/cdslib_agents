import pytest
from itertools import product

import pandas as pd
import numpy as np

from agents import behaviour


# Relative tolerance when comparing numerical data
REL_TOL =0.99
# All combinations of x, y, vx, vy (positive, negative or zero)
POSITION_X, POSITION_Y, VX, VY = np.array(
    [np.array(values) for values in product([1., 0, -1.], repeat=4)]
).T


@pytest.fixture
def small_df():
    data = {'x': POSITION_X, 'y': POSITION_Y, 'vx': VX, 'vy': VY}
    df = pd.DataFrame(data)
    return df


def test_behaviour_move_agent(small_df: pd.DataFrame):
    """Test movement of agents using several combinations of positive, negative
    and zero values in positions and velocities."""
    def q_new(q, v, dt):
        return q + v * dt
    
    dtime = 1.
    new_df = behaviour.move_agents(small_df, dtime)
    
    for i in range(len(new_df)):
        x_expected = q_new(POSITION_X[i], VX[i], dtime)
        y_expected = q_new(POSITION_Y[i], VY[i], dtime)
        agent = new_df.iloc[i]
        x_is_expected = agent['x'] == pytest.approx(x_expected, rel=REL_TOL)
        y_is_expected = agent['y'] == pytest.approx(y_expected, rel=REL_TOL)
        assert x_is_expected and y_is_expected


def test_behaviour_stop_agents(small_df: pd.DataFrame):
    """Test stopping agents for some specific agents"""
    condition = (small_df['vx'] == 1.) & (small_df['vy'] == 1.)
    indexes = small_df[condition].index.tolist()
    new_df = behaviour.stop_agents(small_df, indexes)
    for index in indexes:
        row = new_df.loc[[index]]
        vx_is_zero = float(row['vx']) == pytest.approx(0, rel=REL_TOL)
        vy_is_zero = float(row['vy']) == pytest.approx(0, rel=REL_TOL)
        assert vx_is_zero and vy_is_zero