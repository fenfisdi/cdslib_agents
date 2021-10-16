from math import fmod
from numpy import arctan2, cos, sin, pi, sqrt
from pandas.core.frame import DataFrame

from abmodel.models.population import BoxSize
from abmodel.utils.distributions import Distribution
from abmodel.utils.utilities import check_field_errors, check_field_existance


def move_individual_agent(
    row: DataFrame,
    box_size: BoxSize,
    dt: float
) -> DataFrame:
    """
    TODO: Add brief explanation
    A row represents an agent.

    Parameters
    ----------
    TODO

    Returns
    -------
    TODO

    Notes
    -----
    TODO: include mathematical description and explanatory image

    Examples
    --------
    TODO: include some examples
    """
    # Update current position of the agent with its velocities
    row.x += row.vx * dt
    row.y += row.vy * dt

    # Verify if coordinates are out of the box
    # then return to the box limit
    if row.x < box_size.left:
        row.vx = -row.vx
        row.x = box_size.left
    if row.x > box_size.right:
        row.vx = -row.vx
        row.x = box_size.right

    if row.y < box_size.bottom:
        row.vy = -row.vy
        row.y = box_size.bottom
    if row.y > box_size.top:
        row.vy = -row.vy
        row.y = box_size.top

    return row


class AgentMovement:
    """
        TODO: Add brief explanation

        Methods
        -------
        TODO
    """
    @classmethod
    def move_agents(
        cls,
        df: DataFrame,
        box_size: BoxSize,
        dt: float
    ) -> DataFrame:
        """
            Function to apply as transformation in a pandas Dataframe to update
            coordinates from the agent with its velocities.

            Parameters
            ----------
            df : DataFrame
                Dataframe to apply transformation.
                Must have `x`, `y`, `vx` and `vy` columns.

            box_size : BoxSize
                Parameter with the region coordinates.

            dt : float
                Local time step, representing how often to take a measure.

            Returns
            -------
            df: DataFrame
                Dataframe with the transformations in columns `x` and `y`

            Raises
            ------
            ValueError
                If the dataframe `df` doesn't have `x`, `y`, `vx`
                and `vy` columns.

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            move_individual_agent : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        check_field_errors(df)
        try:
            df = df.apply(move_individual_agent, axis=1)
        except Exception:
            check_field_existance(df, ["x", "y", "vx", "vy"])
        else:
            return df

    @classmethod
    def stop_agents(cls, df: DataFrame, indexes: list) -> DataFrame:
        """
            Set the velocity of a given set of agents to zero.

            Parameters
            ----------
            df : DataFrame
                Dataframe to apply transformation.
                Must have `vx` and `vy` columns.

            indexes : list
                List containing the index of the agents that need to be
                stopped

            Returns
            -------
            df : DataFrame
                Dataframe with the transformations in columns `vx` and `vy`

            Raises
            ------
            ValueError
                If the dataframe `df` doesn't have `vx`
                and `vy` columns.

            Examples
            --------
            TODO: include some examples
        """
        try:
            df.loc[indexes, "vx"] = 0
            df.loc[indexes, "vy"] = 0
        except Exception:
            check_field_existance(df, ["vx", "vy"])
        else:
            return df

    @classmethod
    def standardize_angle(cls, angle: float) -> float:
        """
            Standardize angles to be in the interval [-pi, pi]

            Parameters
            ----------
            angle : float
                The angle to be standardized

            Returns
            -------
            standardized_angle : float
                The standardized angle

            Notes
            -----
            TODO: include mathematical description and explanatory image

            Examples
            --------
            TODO: include some examples
        """
        return fmod(angle + 2*pi, 2*pi)

    @classmethod
    def angle(cls, x: float, y: float) -> float:
        """
            Returns the standardized angle formed by the components
            `x` and `y`.

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            standardize_angle : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        # Standardize angles on the interval [0, 2*pi]
        return cls.standardize_angle(arctan2(y, x))

    @classmethod
    def vector_angles(cls, df: DataFrame, components: list) -> DataFrame:
        """
            Calculates vector angles from their euclidean components

            Parameters
            ----------
            df : DataFrame
                Dataframe with vector components to calculate the
                corresponding angles

            components: list
                Vector components names.
                If the vectors corresponds to positions, then
                `components = ['x', 'y']`.
                If the vectors corresponds to velocities, then
                `components = ['vx', 'vy']`.

            Returns
            -------
            angles : Series
                Serie with the computed angles.

            Raises
            ------
            ValueError
                If the dataframe `df` doesn't have the columns
                specified by `components`.

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            angle : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            angles = df.apply(
                lambda row: cls.angle(row[components[0]], row[components[1]]),
                axis=1
                )
        except Exception:
            check_field_existance(df, components)
        else:
            return angles

    @classmethod
    def change_velocities(
        cls,
        df: DataFrame,
        distribution: Distribution,
        angle_variance: float
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            standardize_angle : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        n_agents = len(df.index)
        new_velocities_norm = distribution.sample(size=n_agents)

        angles = cls.vector_angles(df, ["vx", "vy"])

        delta_angles = Distribution(
            dist_type="numpy",
            dist_name="normal",
            loc=0.0,
            scale=angle_variance
            ).sample(size=n_agents)

        angles = angles + delta_angles

        # Standardize angles on the interval [0, 2*pi]
        angles = angles.apply(lambda angle: cls.standardize_angle(angle))

        df.loc[df.index, "vx"] = new_velocities_norm * cos(angles)

        df.loc[df.index, "vy"] = new_velocities_norm * sin(angles)

        return df

    @classmethod
    def update_velocities(
        cls,
        df: DataFrame,
        distribution: Distribution,
        angle_variance: float,
        group_field: str = "",
        group_label: str = ""
    ) -> DataFrame:
        """
            Update the velocity of a given set of agents from a given
            mobility profile (i.e. a velocity distribution) and
            deviating the resulting angles using a normal distribution
            with a standard deviation equal to `angle_variance`.

            Parameters
            ----------
            df : DataFrame
                Dataframe to apply transformation.
                Must have `vx` and `vy` columns.

            distribution : Distribution
                Mobility profile. This is the velocity distribution
                to use for updating the population velocities each
                time step.

            angle_variation : float
                Standard deviation of the normal distribution
                used for changing the direction of the velocity
                from its initial value

            group_field : str, optional
                The field over which to filter the set of agents.
                If not provided, then the set of agents used is
                going to be the whole set of agents.

            group_label : str, optional
                The value of the `group_filed` used to filter
                the set of agents. If `group_field` is not provided,
                then this parameter is ignored.

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            The velocity direction change is calculated as:

            .. math::
                \theta_{new} = \theta_{former} + \Delta \theta

            Where :math: `\Delta \theta` is a random variable which
            follows a normal distribution with mean :math: `\mu = 0.0`
            and standard deviation equals to `angle_variance`.

            TODO: insert explanatory image

            See Also
            --------
            change_velocities : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        # TODO: Change group_field to be Optional using typing
        if group_field == "":
            try:
                # Change velocities for all the agents in df
                df = cls.change_velocities(df, distribution, angle_variance)
            except Exception:
                check_field_existance(df, ["vx", "vy"])
            else:
                return df

        if group_field != "":
            try:
                if group_label in df[group_field].values:
                    filtered_df = df.loc[df[group_field] == group_label]

                    # Change velocities only for the filtered_df
                    # Update df using filtered_df
                    df.update(
                        cls.change_velocities(
                            filtered_df,
                            distribution,
                            angle_variance
                            )
                        )
            except Exception:
                check_field_existance(df, [group_field, "vx", "vy"])
            else:
                return df

    @classmethod
    def deviation_angle(cls, grouped_df: DataFrame) -> float:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            standardize_angle : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        sorted_serie = \
            grouped_df["relative_angle"].sort_values().copy()

        consecutive_angle = sorted_serie.diff().shift(periods=-1)
        consecutive_angle.iloc[-1] = \
            (2*pi - sorted_serie.iloc[-1]) + sorted_serie.iloc[0]

        sorted_df = DataFrame()
        sorted_df["relative_angle"] = sorted_serie
        sorted_df["consecutive_angle"] = consecutive_angle

        max_angle = sorted_df["consecutive_angle"].max()

        greatest_angle_to_avoid = sorted_df.loc[
            sorted_df["consecutive_angle"] == max_angle
            ]

        # Standardize angles on the interval [0, 2*pi]
        return cls.standardize_angle(
            greatest_angle_to_avoid["relative_angle"].iloc[0]
            + greatest_angle_to_avoid["consecutive_angle"].iloc[0]/2)

    @classmethod
    def replace_velocities(
        cls,
        row: DataFrame,
        new_angles: DataFrame
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            Examples
            --------
            TODO: include some examples
        """
        if row.agent in new_angles.index:
            velocity_norm = sqrt(row.vx**2 + row.vy**2)
            row.vx = velocity_norm * cos(new_angles[row.agent])
            row.vy = velocity_norm * sin(new_angles[row.agent])
        return row

    @classmethod
    def avoid_agents(cls, df: DataFrame, df_to_avoid: DataFrame) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Raises
            ------
            TODO

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            deviation_angle : TODO complete explanation

            replace_velocities : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        if check_field_existance(df, ["agent", "x", "y", "vx", "vy"]):
            df_copy = df.copy()

            scared_agents = df_copy.loc[df_copy.agent.isin(
                df_to_avoid["agent"].unique()
                )][["agent", "x", "y", "vx", "vy"]]

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
                    lambda row: row.x_to_avoid - row.x, axis=1
                    )

            scary_agents["y_relative"] = scary_agents.apply(
                    lambda row: row.y_to_avoid - row.y, axis=1
                    )

            scary_agents["relative_angle"] = cls.vector_angles(
                scary_agents,
                ["x_relative", "y_relative"]
                )

            scary_agents["relative_angle"] = \
                scary_agents["relative_angle"].apply(cls.standardize_angle)

            new_angles = scary_agents[["agent", "relative_angle"]] \
                .groupby("agent").apply(cls.deviation_angle)

            return df.apply(
                lambda row: cls.replace_velocities(row, new_angles),
                axis=1
                )
