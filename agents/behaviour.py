import pandas as pd

def move_agent(df: pd.DataFrame, dt: float) -> pd.DataFrame:
    aux_df = df.copy()
    aux_df['x'] = aux_df.apply(lambda row: row['x'] + row['vx'] * dt, axis=1)
    aux_df['y'] = aux_df.apply(lambda row: row['y'] + row['vy'] * dt, axis=1)
    return aux_df
