from typing import List, Tuple

import pandas as pd
import numpy as np


def move_agents(df: pd.DataFrame, dt: float) -> pd.DataFrame:
    """Updates position of all agents based on previous velocity."""
    aux_df = df.copy()
    aux_df['x'] = aux_df.apply(lambda row: row['x'] + row['vx'] * dt, axis=1)
    aux_df['y'] = aux_df.apply(lambda row: row['y'] + row['vy'] * dt, axis=1)
    return aux_df



def stop_agents(df: pd.DataFrame, indexes: List[int]) -> pd.DataFrame:
    """Sets velocity to zero for specific agents identified by indexes."""
    aux_df = df.copy()
    aux_df.loc[indexes, 'vx'] = 0
    aux_df.loc[indexes, 'vy'] = 0
    return aux_df


def intercept_x_lim(slope: float, point: np.ndarray, x_lim: float):
    """Calculates intercept between line defined by ``slope`` and
    ``position_0`` and line ``x = x_lim``.
    
    Paramters
    ---------
    slope : float
        Slope of the line.
    position_0 : np.ndarray or list (len=2)
        Point in the line.
    x_lim : float
        Defines line ``x = x_lim``.

    Returns
    -------
    np.ndarray
        Point of intercept between line defined by (``slope``, ``position_0``)
        and line ``x = x_lim``.
    """
    if slope == np.inf:
        raise ValueError(
            "slope can't be np.inf, because the two lines would be parallel."
        )

    return np.array([x_lim, slope * (x_lim - point[0]) + point[1]])


def intercept_y_lim(slope: float, point: np.ndarray, y_lim: float):
    """Calculates intercept between line defined by ``slope`` and
    ``position_0`` and line ``y = y_lim``.
    
    Paramters
    ---------
    slope : float
        Slope of the line.
    position_0 : np.ndarray or list (len=2)
        Point in the line.
    y_lim : float
        Defines line ``x = y_lim``.

    Returns
    -------
    np.ndarray
        Point of intercept between line defined by (``slope``, ``position_0``)
        and line ``y = y_lim``
    """
    if slope == 0:
        raise ValueError(
            "slope can't be zero, because the two lines would be parallel."
        )
    return np.array([point[0] + (y_lim - point[1]) / slope, y_lim])


def reflect_x_component(vector: np.ndarray) -> np.ndarray:
    """Reflected 2d vector across y axis."""
    return np.array([-vector[0], vector[1]])


def reflect_y_component(vector: np.ndarray) -> np.ndarray:
    """Reflected 2d vector across x axis."""
    return np.array([vector[0], -vector[1]])


def bounce_once(
    position_0: np.ndarray, position_1: np.ndarray, x_lim: float, y_lim: float
) -> Tuple[np.ndarray, np.ndarray]:
    """Given a box of limits ``(-x_lim, xlim)`` and ``(-y_lim, y_lim)``, an
    initial position i.e. ``position_0`` inside the box, and a final position
    i.e. ``position_1`` outside the box, calculates the bounce point
    and the final position after bouncing (independently if the final position
    is inside or outside the box).
    
    Parameters
    ----------
    position_0 : np.ndarray shape=(2,)
        Initial position.
    position_1 : np.ndarray shape=(2,)
        Final position.
    x_lim : float > 0
        Defines the limit of the box in the x dimension ``(-x_lim, x_lim)``
    y_lim : float > 0
        Defines the limit of the box in the y dimension ``(-y_lim, y_lim)``.
    
    Returns
    -------
    bounce_point : np.ndarray shape=(2,)
        Point where the object bounces.
    final_position : np.ndarray shape=(2,)
        Position after bouncing.
    """
    
    delta = position_1 - position_0
    slope = delta[1] / delta[0] if delta[0] != 0. else np.inf
    bounce_x = False
    bounce_y = False

    if np.abs(position_1[0]) > x_lim and slope != np.inf:
        x_sign = np.sign(delta[0])
        bounce_point = intercept_x_lim(slope, position_0, x_sign * x_lim)
        if not np.abs(bounce_point[1]) > y_lim:
            bounce_x = True
            delta_aux = position_1 - bounce_point
            final_position = bounce_point + reflect_x_component(delta_aux)
            return bounce_point, final_position

    if np.abs(position_1[1]) > y_lim and not bounce_x:
        y_sign = np.sign(delta[1])
        bounce_point = intercept_y_lim(slope, position_0, y_sign * y_lim)
        delta_aux = position_1 - bounce_point
        final_position = bounce_point + reflect_y_component(delta_aux)
        bounce_y = True
        return bounce_point, final_position

    if not bounce_y and not bounce_x:
        raise ValueError(
            "position_1 must be out of the 'box' defined by x_lim and y_lim."
        )


def bounce(
    position_0: np.ndarray, position_1: np.ndarray, x_lim: float, y_lim: float
) -> np.ndarray:
    """Bounces an agent inside a box of limits ``(-x_lim, xlim)`` and
    ``(-y_lim, y_lim)``."""
    if np.abs(position_1[0]) <= x_lim and np.abs(position_1[1]) <= y_lim:
        return position_1
    else:
        position_0, position_1 = bounce_once(position_0, position_1, x_lim, y_lim)
        return bounce(position_0, position_1, x_lim, y_lim)


def correct_agent_positions(
    df_previous: pd.DataFrame, df_current: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    raise NotImplementedError
