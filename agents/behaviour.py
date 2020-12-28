from typing import List, Tuple

import pandas as pd
import numpy as np


def move_agents(df: pd.DataFrame, dt: float) -> pd.DataFrame:
    """Updates position of all agents based on previous velocity."""
    df['x'] = df.apply(lambda row: row['x'] + row['vx'] * dt, axis=1)
    df['y'] = df.apply(lambda row: row['y'] + row['vy'] * dt, axis=1)


def stop_agents(df: pd.DataFrame, indexes: List[int]) -> pd.DataFrame:
    """Sets velocity to zero for specific agents identified by indexes."""
    df.loc[indexes, 'vx'] = 0
    df.loc[indexes, 'vy'] = 0


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
    
    Raises
    ------
    ValueError
        if ``slope == np.inf``, for the two lines would be parallel.
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
    
    Raises
    ------
    ValueError
        if ``slope == 0``, for the two lines would be parallel.
    """
    if slope == 0:
        raise ValueError(
            "slope can't be zero, because the two lines would be parallel."
        )
    return np.array([point[0] + (y_lim - point[1]) / slope, y_lim])


def reflect_x_component(vector: np.ndarray) -> np.ndarray:
    """Calculates reflected 2d vector across y axis.
    
    Parameters
    ----------
    vector : np.ndarray or lis, shape=(2,)
        Represents a 2d vector.

    Returns
    -------
    np.ndarray, shape=(2,)
        Reflected 2d vector across y axis.
    """
    return np.array([-vector[0], vector[1]])


def reflect_y_component(vector: np.ndarray) -> np.ndarray:
    """Calculates reflected 2d vector across x axis.
    
    Parameters
    ----------
    vector : np.ndarray or lis, shape=(2,)
        Represents a 2d vector.

    Returns
    -------
    np.ndarray, shape=(2,)
        Reflected 2d vector across x axis.
    """
    return np.array([vector[0], -vector[1]])


def bounce_once(
    position_0: np.ndarray, position_1: np.ndarray, x_lim: float, y_lim: float
) -> Tuple[np.ndarray, np.ndarray]:
    """Given a box of limits ``(-x_lim, xlim)`` and ``(-y_lim, y_lim)``, an
    initial position i.e. ``position_0`` inside the box, and a final position
    i.e. ``position_1`` outside the box, calculates the bounce point
    and the final position after bouncing off one of the limits (independently
    if the final position is inside or outside the box).

    Parameters
    ----------
    position_0 : np.ndarray shape=(2,)
        Initial position.
    position_1 : np.ndarray shape=(2,)
        Final position.
    x_lim : float
        Defines the horizontal limits of the box: ``(-x_lim, x_lim)``
    y_lim : float
        Defines the vertical limits of the box: ``(-y_lim, y_lim)``

    Returns
    -------
    bounce_point : np.ndarray shape=(2,)
        Point where the object bounces.
    final_position : np.ndarray shape=(2,)
        Position after bouncing.
    
    Raises
    ------
    ValueError
        Either if ``position_0`` is not inside the box or ``position_1`` is not
        outside the box.
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
    ``(-y_lim, y_lim)``.
    
    ``position_0`` is assumed to be inside the box and ``position_1`` outside
    the box. This function returns a new final position calculated as if the
    agent bounced off the limits of the box up to a total travel distance
    equivalent to that between ``position_0`` and ``position_1``. This
    mechanism will be further explained in the documentation (REFERENCE THE
    DOCUMENTATION HERE).

    Parameters
    ----------
    position_0 : np.ndarray, shape=(2,)
        Initial position (inside the box)
    position_1 : np.ndarray, shape=(2,)
        Final position (outside the box)
    x_lim : float
        Defines the horizontal limits of the box: ``(-x_lim, x_lim)``
    y_lim : float
        Defines the vertical limits of the box: ``(-y_lim, y_lim)``
    """
    if np.abs(position_1[0]) <= x_lim and np.abs(position_1[1]) <= y_lim:
        return position_1
    else:
        position_0, position_1 = bounce_once(position_0, position_1, x_lim, y_lim)
        return bounce(position_0, position_1, x_lim, y_lim)


def position_vector_from_df_series(df: pd.Series) -> np.ndarray:
    """Get the position vector from a series with indexes 'x' and 'y'."""
    return np.array([df.at['x'], df.at['y']])


def bounce_apply(
    row_current: pd.Series, df_previous:pd.DataFrame,  x_lim: float, y_lim: float
) -> pd.DataFrame:
    """Applies ``bounce`` function to a row of a pandas dataframe (the format
    of the row will be a pd.Series).

    Parameters
    ----------
    row_current : pd.Series
        Row containing the information of current iteration of a single agent.
        The indexes ``'agent'``, ``'x'`` and ``'y'`` must be defined.
    df_previous : pd.Dataframe
        Contains information of all agents of previous iteration.
        Columns ``'agent'``, ``'x'`` and ``'y'`` must be defined.
    x_lim : float
        Defines the horizontal limits of the box: ``(-x_lim, x_lim)``
    y_lim : float
        Defines the vertical limits of the box: ``(-y_lim, y_lim)``

    Note
    ----
    All the values of the column ``'agent'`` must coincide with the values of
    ``'index'``. These are unique identifiers of the agent.
    """

    agent = int(row_current.at['agent'])
    row_previous = df_previous.loc[agent].copy()

    position_0 = position_vector_from_df_series(row_previous)
    position_1 = position_vector_from_df_series(row_current)

    position_1_new = bounce(position_0, position_1, x_lim, y_lim)

    # This one is needed in order to avoid pandas' SettingWithCopyWarning
    row = row_current.copy()

    row.loc['x'] = position_1_new[0]
    row.loc['y'] = position_1_new[1]

    return row


def indexes_agents_out_of_box(df: pd.DataFrame, x_lim: float, y_lim: float):
    """Returns a list of indexes of agents that are out of the box limited by
    ``(-x_lim, xlim)`` and ``(-y_lim, y_lim)``. Columns ``'x'`` and ``'y'``
    must be defined in ``df``."""
    condition = (np.abs(df['x']) > x_lim) | (np.abs(df['y']) > y_lim)
    return df[condition].index.tolist()


def correct_agents_positions(
    df_previous: pd.DataFrame, df_current: pd.DataFrame, x_lim: float, y_lim: float
):
    """Fixes the positions of the agents that are out of the box by applying a
    bounce function.
    
    Parameters
    ----------
    df_previous : pd.Dataframe
        Contains information of the previous iteration of all agents including
        columns corresponding to ``'agent'``, ``'x'`` and ``'y'``.
    df_current : pd.Dataframe
        Contains information of the current iteration of all agents including
        columns corresponding to ``'agent'``, ``'x'`` and ``'y'``.
    x_lim : float
        Defines the horizontal limits of the box: ``(-x_lim, x_lim)``
    y_lim : float
        Defines the vertical limits of the box: ``(-y_lim, y_lim)``

    Note
    ----
    The goal of this function is to modify ``df_current`` such that the
    positions of all the agents will be inside the box.
    """
    agents_out_of_box = indexes_agents_out_of_box(df_current, x_lim, y_lim)
    df_current.loc[agents_out_of_box] = \
        df_current.loc[agents_out_of_box].apply(
            bounce_apply, args=(df_previous, x_lim, y_lim), axis=1
        )
