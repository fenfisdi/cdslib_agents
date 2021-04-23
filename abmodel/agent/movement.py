from pandas.core.frame import DataFrame

from cdslib.models.population import BoxSize


class AgentMovement:

    @classmethod
    def apply_movement(
        cls, df: DataFrame, box_size: BoxSize, dt: float
    ):
        """
            Function to apply as transformation in a pandas Dataframe to update
            coordinates from the agent with its velocities.

            Parameters
            ----------
            df: DataFrame
                Dataframe to apply transformation, must have x, y, vx
                and vy columns.

            box_size: BoxSize
                Parameter according to the region coordinates.

            dt: float
                Local time step, representing how often to take a measure.

            Returns
            -------
            DataFrame
                Dataframe with the transformations in columns x and y
        """
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
            df_cols = df.columns
            x_check = 'x' in df_cols
            y_check = 'y' in df_cols
            vx_check = 'vx' in df_cols
            vy_check = 'vy' in df_cols

            if (not x_check or not y_check or not vx_check or not vy_check):
                check_string = ""

                if not x_check:
                    check_string += "'x', "

                if not y_check:
                    check_string += "'y', "

                if not vx_check:
                    check_string += "'vx', "

                if not vy_check:
                    check_string += "'vy', "

                check_string += "must be checked."

                error_string = (
                    "df must contain 'x', 'y', 'vx' "
                    "and 'vy' columns. "
                    )

                raise ValueError(error_string + check_string)

    @classmethod
    def apply_stop_agents(df: DataFrame, indexes: list) -> DataFrame:
        """
            Sets velocity to zero for specific agents identified by indexes.
        """
        df.loc[indexes, 'vx'] = 0
        df.loc[indexes, 'vy'] = 0
