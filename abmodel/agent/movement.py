from pandas.core.frame import DataFrame

from abmodel.models.population import BoxSize
from abmodel.utils.utilities import check_column_existance, check_column_errors


class AgentMovement:

    @classmethod
    def move_agents(
        cls, df: DataFrame, box_size: BoxSize, dt: float
    ):
        """
            Function to apply as transformation in a pandas Dataframe to update
            coordinates from the agent with its velocities.

            Parameters
            ----------
            df : DataFrame
                Dataframe to apply transformation, must have `x`, `y`, `vx`
                and `vy` columns.

            box_size : BoxSize
                Parameter according to the region coordinates.

            dt : float
                Local time step, representing how often to take a measure.

            Returns
            -------
            df: DataFrame
                Dataframe with the transformations in columns `x` and `y`

            Notes
            -----
            ... TODO: include mathematical description and explanatory
            image

            Examples
            --------
            ... TODO

        """
        check_column_errors(df)
        try:
            # Update current position of the agent with its velocities
            df.x += df.vx * dt
            df.y += df.vy * dt

            # Verify if coordinates are out of the box
            # then return to the box limit
            if df.x < box_size.left:
                df.vx = -df.vx
                df.x = box_size.left
            if df.x > box_size.right:
                df.vx = -df.vx
                df.x = box_size.right

            if df.y < box_size.bottom:
                df.vy = -df.vy
                df.y = box_size.bottom
            if df.y > box_size.top:
                df.vy = -df.vy
                df.y = box_size.top

            return df
        except Exception:
            check_column_existance(df, ["x", "y", "vx", "vy"])

    @classmethod
    def stop_agents(cls, df: DataFrame, indexes: list):
        """
            Set the velocity of a given set of agents to zero.

            Parameters
            ----------
            df : DataFrame
                Dataframe to apply transformation, must have `x`, `y`, `vx`
                and `vy` columns.

            indexes : list
                List containing the index of the agents that need to be
                stopped

        """
        if check_column_existance(df, ["vx", "vy"]):
            df.loc[indexes, "vx"] = 0
            df.loc[indexes, "vy"] = 0
