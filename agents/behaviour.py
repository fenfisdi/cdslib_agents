from typing import List

import pandas as pd


def move_agents(df: pd.DataFrame, dt: float) -> pd.DataFrame:
    """Updates position of all agents based on previous velocity."""
    df['x'] = df.apply(lambda row: row['x'] + row['vx'] * dt, axis=1)
    df['y'] = df.apply(lambda row: row['y'] + row['vy'] * dt, axis=1)


def stop_agents(df: pd.DataFrame, indexes: List[int]) -> pd.DataFrame:
    """Sets velocity to zero for specific agents identified by indexes."""
    df.loc[indexes, 'vx'] = 0
    df.loc[indexes, 'vy'] = 0