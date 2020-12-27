import pytest
from typing import Tuple
from itertools import product

import pandas as pd
import numpy as np

from agents import behaviour


# Relative tolerance when comparing numerical data
REL_TOL = 0.99
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


@pytest.mark.parametrize(
    'slope,point,x_lim,expected_result',
    [
        (0, np.array([0, 0]), 1, np.array([1, 0])),
        (0, np.array([-1, 0]), 1, np.array([1, 0])),
        (0, np.array([1, 0]), 1, np.array([1, 0])),
        (1, np.array([1, 1]), 1, np.array([1, 1])),
        (-1, np.array([-2, -2]), 1, np.array([1, -3])),
        (0.5, np.array([1, 1]), 1, np.array([3, 2])),
    ]
)
def test_behaviour_intercept_x_lim(
    slope: float, point: np.array, x_lim: float, expected_result: np.array
):
    result = behaviour.intercept_x_lim(slope, point, x_lim)
    assert result == pytest.approx(expected_result, rel=REL_TOL)


@pytest.mark.parametrize(
    'slope,point,y_lim,expected_result',
    [
        (np.inf, np.array([0, 0]), 1, np.array([0, 1])),
        (np.inf, np.array([-1, 0]), 1, np.array([-1, 1])),
        (np.inf, np.array([1, 0]), 1, np.array([1, 1])),
        (1, np.array([1, 1]), 1, np.array([1, 1])),
        (-1, np.array([-2, -2]), 1, np.array([-5, 1])),
        (0.5, np.array([1, 1]), 1, np.array([1, 1])),
    ]
)
def test_behaviour_intercept_y_lim(
    slope: float, point: np.array, y_lim: float, expected_result: np.array
):
    result = behaviour.intercept_y_lim(slope, point, y_lim)
    assert result == pytest.approx(expected_result, rel=REL_TOL)


@pytest.mark.parametrize(
    'vector,expected_result',
    [
        (np.array([0, 1]), np.array([0, 1])),
        (np.array([0, 0]), np.array([0, 0])),
        (np.array([1, 1]), np.array([-1, 1])),
        (np.array([-1, 1]), np.array([1, 1])),
    ]
)
def test_behaviour_reflect_x_component(vector: np.array, expected_result: np.array):
    result = behaviour.reflect_x_component(vector)
    assert result == pytest.approx(expected_result, rel=REL_TOL)


@pytest.mark.parametrize(
    'vector,expected_result',
    [
        (np.array([0, 1]), np.array([0, -1])),
        (np.array([0, 0]), np.array([0, 0])),
        (np.array([1, -1]), np.array([1, 1])),
        (np.array([-1, 1]), np.array([-1, -1])),
    ]
)
def test_behaviour_reflect_y_component(vector: np.array, expected_result: np.array):
    result = behaviour.reflect_y_component(vector)
    assert result == pytest.approx(expected_result, rel=REL_TOL)


@pytest.mark.parametrize(
    'position_0,position_1,x_lim,y_lim,expected_result',
    [
        (np.array([0, -1]), np.array([2, 1]), 1, 1, (np.array([1, 0]), np.array([0, 1]))),
        (np.array([0, -1]), np.array([3, 2]), 1, 1, (np.array([1, 0]), np.array([-1, 2]))),
        (np.array([0, -1]), np.array([0, -2]), 1, 1, (np.array([0, -1]), np.array([0, 0]))),
        (np.array([0, 0]), np.array([0, -2]), 1, 1, (np.array([0, -1]), np.array([0, 0]))),
        (np.array([0, 0]), np.array([0, -2]), 1, 1, (np.array([0, -1]), np.array([0, 0]))),
        (np.array([0, 0]), np.array([4, 2]), 1, 1, (np.array([1, 0.5]), np.array([-2, 2]))),
        (np.array([-1, 0]), np.array([1, -2]), 1, 1, (np.array([0, -1]), np.array([1, 0]))),
        (np.array([-1, 0]), np.array([1, 2]), 1, 1, (np.array([0, 1]), np.array([1, 0]))),
        (np.array([-1, 0]), np.array([2, 3]), 1, 1, (np.array([0, 1]), np.array([2, -1]))),
    ]
)
def test_behaviour_bounce_once(
    position_0: np.ndarray, position_1: np.ndarray, x_lim: float, y_lim: float,
    expected_result: Tuple[np.ndarray, np.ndarray]
):
    result = behaviour.bounce_once(position_0, position_1, x_lim, y_lim)
    assert result[0] == pytest.approx(expected_result[0], rel=REL_TOL)
    assert result[1] == pytest.approx(expected_result[1], rel=REL_TOL)


@pytest.mark.parametrize(
    'position_0,position_1,x_lim,y_lim,expected_result',
    [
        (np.array([0, -1]), np.array([2, 1]), 1, 1, np.array([0, 1])),
        (np.array([0, -1]), np.array([3, 2]), 1, 1, np.array([-1, 0])),
        (np.array([0, -1]), np.array([0, -2]), 1, 1, np.array([0, 0])),
        (np.array([0, 0]), np.array([0, -2]), 1, 1, np.array([0, 0])),
        (np.array([0, 0]), np.array([0, -2]), 1, 1, np.array([0, 0])),
        (np.array([0, 0]), np.array([4, 2]), 1, 1, np.array([0, 0])),
        (np.array([-1, 0]), np.array([1, -2]), 1, 1, np.array([1, 0])),
        (np.array([-1, 0]), np.array([1, 2]), 1, 1, np.array([1, 0])),
        (np.array([-1, 0]), np.array([2, 3]), 1, 1, np.array([0, -1])),
    ]
)
def test_behaviour_bounce(
    position_0: np.ndarray, position_1: np.ndarray, x_lim: float, y_lim: float,
    expected_result: np.ndarray
):
    result = behaviour.bounce(position_0, position_1, x_lim, y_lim)
    assert result == pytest.approx(expected_result, rel=REL_TOL)


def test_behaviour_bounce_once_error():
    with pytest.raises(ValueError):
        behaviour.bounce_once(
            np.array([0, 0.5]), np.array([0, 0.7]), 1, 1
        )

def test_behaviour_intercept_x_lim_error():
    with pytest.raises(ValueError):
        behaviour.intercept_x_lim(np.inf, None, None)


def test_behaviour_intercept_y_lim_error():
    with pytest.raises(ValueError):
        behaviour.intercept_y_lim(0, None, None)