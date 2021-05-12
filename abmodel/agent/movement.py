from numpy import cos, sin, arcsin
from pandas.core.frame import DataFrame
from typing import Any

from abmodel.models.population import BoxSize
from abmodel.utils.utilities import (check_field_existance,
                                     check_field_errors)
from abmodel.utils.distributions import Distribution


class AgentMovement:

    @classmethod
    def move_agents(
        cls, df: DataFrame, box_size: BoxSize, dt: float
    ) -> None:
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
        check_field_errors(df)
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

        except Exception:
            check_field_existance(df, ["x", "y", "vx", "vy"])

    @classmethod
    def stop_agents(cls, df: DataFrame, indexes: list) -> None:
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
        if check_field_existance(df, ["vx", "vy"]):
            df.loc[indexes, "vx"] = 0
            df.loc[indexes, "vy"] = 0

    @classmethod
    def velocity_angles(cls, df: DataFrame) -> Any:
        """
            Set the velocity of a given set of agents to zero.

            Parameters
            ----------
            df : DataFrame
                Dataframe to apply transformation, must have `vx` and `vy`
        """
        def angle(x: float, y: float) -> float:
            try:
                return arcsin(y/x)
            except Exception:
                return 0.0

        if check_field_existance(df, ["vx", "vy"]):
            return df.apply(
                lambda row: angle(row["x"], row["y"]),
                axis=1
                )

    @classmethod
    def update_velocities(cls, df: DataFrame, distribution: Distribution,
                          angle_variance: float, group_field: str = "",
                          group_label: str = "") -> None:
        """
            Set the velocity of a given set of agents to zero.

            Parameters
            ----------
            df : DataFrame
                Dataframe to apply transformation, must have ...
        """
        def change_velocities(df):
            """
            """
            n_agents = len(df.index)
            new_velocities = distribution.sample(size=n_agents)

            angles = cls.velocity_angles(df)

            delta_angles = Distribution(
                dist_type="numpy",
                distribution="normal",
                loc=0.0,
                scale=angle_variance
                ).sample(size=n_agents)

            angles = angles + delta_angles

            df.loc["vx"] = new_velocities * cos(angles)

            df.loc["vy"] = new_velocities * sin(angles)

        if check_field_existance(df, ["vx", "vy"]) and group_field == "":
            change_velocities(df)

        if group_field != "":
            if check_field_existance(df, [group_field, "vx", "vy"]):
                if group_label in df[group_field].values:
                    filtered_df = df.loc[df[group_field] == group_label]
                    change_velocities(filtered_df)
                else:
                    pass
