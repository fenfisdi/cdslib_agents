from typing import Any

from numpy import arctan2, cos, sin, pi, sqrt
from pandas.core.frame import DataFrame, Series

from abmodel.models.population import BoxSize
from abmodel.utils.distributions import Distribution
from abmodel.utils.utilities import check_field_errors, check_field_existance


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

        def move_individual_agent(df):

                #Analizando función de movimiento
                
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

        check_field_errors(df)
        try:
            #print('fefsa')
            df = df.apply(move_individual_agent, axis=1,)
            #print('fgbfj')
        except Exception:
            check_field_existance(df, ["x", "y", "vx", "vy"])
            
        return df

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
            
        return df

    @classmethod
    def vector_angles(cls, df: DataFrame, components: list) -> Any:
        """
            Set the direction of a given set of agents to zero.

            Parameters
            ----------
            df : DataFrame
                Dataframe to apply transformation
        
            Components: list ??????????????????????? vel or pos
            ----------
        """
        def angle(x: float, y: float) -> float:
            try:
                #return arctan(y/x)
                return arctan2(y, x)          #####mejor usar arctan2 para que no devuelva ángulo envuelto
            except Exception:
                return 0.0

        if check_field_existance(df, components):
            return df.apply(
                lambda row: angle(row[components[0]], row[components[1]]),
                axis=1
                )

        return df
    
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

            angles = cls.vector_angles(df, ["vx", "vy"])

            delta_angles = Distribution(
                dist_type="numpy",
                distribution="normal",
                loc=0.0,
                scale=angle_variance
                ).sample(size=n_agents)

            angles = angles + delta_angles

            df.loc["vx"] = new_velocities * cos(angles)

            df.loc["vy"] = new_velocities * sin(angles)
            print('cambio vel')
            return df

        print('entra a if')
        if check_field_existance(df, ["vx", "vy"]) and group_field == "":
            print('entrando a change vel')
            df = change_velocities(df)

        if group_field != "":
            if check_field_existance(df, [group_field, "vx", "vy"]):
                if group_label in df[group_field].values:
                    filtered_df = df.loc[df[group_field] == group_label]
                    change_velocities(filtered_df)
                else:
                    pass
        return df

       
    @classmethod
    def avoid_agents(cls, df: DataFrame, df_to_avoid: DataFrame) -> None:
        """
        """
        def deviation_angle(grouped_serie: Series) -> float:
            """
            """
            sorted_serie = \
                grouped_serie["relative_angle"].sort_values().copy()

            consecutive_angle = sorted_serie.diff().shift(periods=-1)
            consecutive_angle.iloc[-1] = \
                2*pi + (sorted_serie.iloc[-1] - sorted_serie.iloc[0])

            sorted_df = DataFrame()
            sorted_df["relative_angle"] = sorted_serie
            sorted_df["consecutive_angle"] = consecutive_angle

            greatest_angle_to_avoid = sorted_df.loc[
                sorted_df["consecutive_angle"] == sorted_df["consecutive_angle"].max()
                ]

            return (greatest_angle_to_avoid["relative_angle"].iloc[0] +
                    greatest_angle_to_avoid["consecutive_angle"].iloc[0]/2) % 2*pi

        def replace_velocities(row, new_angles):
            if row["agent"] in new_angles.index:
                velocity_norm = sqrt(row["vx"]**2 + row["vy"]**2)
                row["vx"] = velocity_norm * cos(new_angles[row["agent"]])
                row["vy"] = velocity_norm * sin(new_angles[row["agent"]])
            return row

        if check_field_existance(df, ["agent", "x", "y", "vx", "vy"]):
            df_copy = df.copy()

            scared_agents = df_copy.loc(
                    df_copy["agent"].equals(df_to_avoid["agent"].unique())
                    )[["agent", "x", "y", "vx", "vy"]]

            scary_agents = scared_agents.merge(
                        df_to_avoid, how="inner", on="agent"
                        ).merge(
                            df_copy.rename(
                                columns={
                                    "agent": "agent_to_avoid",
                                    "x": "x_to_avoid",
                                    "y": "y_to_avoid"
                                    })[["agent_to_avoid", "x_to_avoid", "y_to_avoid"]],
                            how="inner",
                            on="agent_to_avoid"
                            )
            scary_agents["x_relative"] = scary_agents.apply(
                    lambda row: row["x_to_avoid"] - row["x"], axis=1
                    )

            scary_agents["y_relative"] = scary_agents.apply(
                    lambda row: row["y_to_avoid"] - row["y"], axis=1
                    )

            scary_agents["relative_angle"] = cls.vector_angles(
                scary_agents,
                ["x_relative", "y_relative"]
                )

            scary_agents["relative_angle"] = \
                scary_agents["relative_angle"].apply(
                    lambda x: (x + 2*pi) % (2*pi)
                    )

            new_angles = scary_agents[["agent", "relative_angle"]] \
                .groupby("agent").apply(deviation_angle)

            df = df.apply(
                lambda row: replace_velocities(row, new_angles),
                axis=1
                )
