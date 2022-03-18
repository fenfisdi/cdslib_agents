# Copyright (C) 2021, Camilo Hincapié Gutiérrez
# This file is part of CDSLIB.
#
# CDSLIB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CDSLIB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
#
# This package is authored by:
# Camilo Hincapié (https://www.linkedin.com/in/camilo-hincapie-gutierrez/) (main author)
# Ian Mejía (https://github.com/IanMejia)
# Emil Rueda (https://www.linkedin.com/in/emil-rueda-424012207/)
# Nicole Rivera (https://github.com/nicolerivera1)
# Carolina Rojas Duque (https://github.com/carolinarojasd)

from typing import Optional, Union

from math import fmod
from numpy import ndarray, arctan2, cos, sin, pi, sqrt, inf, frompyfunc, array
from pandas.core.frame import DataFrame, Series

from abmodel.models.population import BoxSize
from abmodel.models.disease import MobilityGroups, DistTitles
from abmodel.utils.distributions import Distribution
from abmodel.utils.utilities import check_field_errors
from abmodel.utils.utilities import check_field_existance, exception_burner


def move_individual_agent(
    row: Series,
    box_size: BoxSize,
    dt: float
) -> Series:
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
    def init_required_fields(
        cls,
        df: DataFrame,
        box_size: BoxSize,
        mobility_groups: MobilityGroups
    ) -> DataFrame:
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
            move_individual_agent : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        # Initialize positions
        df["x"] = Distribution(
            dist_type="numpy",
            dist_name="uniform",
            low=box_size.left,
            high=box_size.right
            ).sample(size=df.shape[0])

        df["y"] = Distribution(
            dist_type="numpy",
            dist_name="uniform",
            low=box_size.bottom,
            high=box_size.top
            ).sample(size=df.shape[0])

        # Initialize velocities
        df = df.assign(vx=inf)
        df = df.assign(vy=inf)

        for mobility_group in mobility_groups.items.keys():
            df = cls.initialize_velocities(
                df=df,
                distribution=mobility_groups.items[
                    mobility_group].dist[DistTitles.mobility.value],
                angle_distribution=Distribution(
                    dist_type="numpy",
                    dist_name="uniform",
                    low=0.0,
                    high=2*pi
                    ),
                group_field="mobility_group",
                group_label=mobility_group,
                preserve_dtypes_dict={"step": int, "agent": int}
                )

        return df

    @classmethod
    def move_agents(
        cls,
        df: DataFrame,
        box_size: BoxSize,
        dt: float  # In scale of the mobility_profile
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
        check_field_errors(df[["x", "y", "vx", "vy"]])
        try:
            df = df.apply(
                lambda row: move_individual_agent(row, box_size, dt),
                axis=1
                )

        except Exception as error:
            exception_burner([
                error,
                check_field_existance(df, ["x", "y", "vx", "vy"])
                ])
        else:
            return df

    @classmethod
    def stop_agents(
        cls,
        df: DataFrame,
        indexes: Union[list, ndarray]
    ) -> DataFrame:
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
        check_field_existance(df, ["vx", "vy"])
        df.loc[indexes, "vx"] = 0
        df.loc[indexes, "vy"] = 0

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
    def vector_angles(cls, df: DataFrame, components: list) -> Series:
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
        except Exception as error:
            exception_burner([
                error,
                check_field_existance(df, components)
                ])
        else:
            return angles

    @classmethod
    def set_velocities(
        cls,
        df: DataFrame,
        distribution: Distribution,
        angle_variance: Optional[float] = None,
        angle_distribution: Optional[Distribution] = None
    ) -> DataFrame:
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
            Exception
                TODO complete explanation

            Notes
            -----
            TODO: include mathematical description and explanatory image

            See Also
            --------
            abmodel.utils.distributions.Distribution : TODO complete
            explanation

            standardize_angle : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        try:
            check_field_existance(df, ["vx", "vy"])
            n_agents = len(df.index)
            new_velocities_norm = distribution.sample(size=n_agents)

            if angle_distribution is None:
                # Use former angles as baseline to create new ones but modified
                # by a normal distribution of scale equal to angle_variance
                angles = cls.vector_angles(df, ["vx", "vy"])

                delta_angles = Distribution(
                    dist_type="numpy",
                    dist_name="normal",
                    loc=0.0,
                    scale=angle_variance
                    ).sample(size=n_agents)

                angles = angles + delta_angles

                # Standardize angles on the interval [0, 2*pi]
                angles = angles.apply(cls.standardize_angle)
            else:
                # Use angle_distribution to create new angles
                # This option is used for initializing velocities
                angles = angle_distribution.sample(size=n_agents)

                # Standardize angles on the interval [0, 2*pi]
                standardize_angle_array = frompyfunc(
                    cls.standardize_angle,
                    nin=1,
                    nout=1
                    )
                angles = array(standardize_angle_array(angles)).astype(float)

            df.loc[df.index, "vx"] = new_velocities_norm * cos(angles)

            df.loc[df.index, "vy"] = new_velocities_norm * sin(angles)

        except Exception as error:
            exception_burner([
                error,
                check_field_existance(df, ["vx", "vy"])
                ])
        else:
            return df

    @classmethod
    def initialize_velocities(
        cls,
        df: DataFrame,
        distribution: Distribution,
        angle_distribution: Distribution,
        indexes: Union[list, ndarray, None] = None,
        group_field: Optional[str] = None,
        group_label: Optional[str] = None,
        preserve_dtypes_dict: Optional[dict] = None
    ) -> DataFrame:
        """
            Initialize the velocity of a given set of agents from a given
            mobility profile (i.e. a velocity distribution) and ...
            TODO

            Parameters
            ----------
            df : DataFrame
                Dataframe to apply transformation.
                Must have `vx` and `vy` columns.

            distribution : Distribution
                Mobility profile. This is the velocity distribution
                to use for updating the population velocities each
                time step.

            angle_distribution : Distribution
                TODO

            indexes : TODO

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
            TODO: insert mathematical description and explanatory image

            See Also
            --------
            set_velocities : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        if indexes is not None and group_field is not None:
            try:
                if group_label in df[group_field].values:
                    filtered_df = df.loc[df[group_field] == group_label].copy()

                    # Filter agents by index
                    filtered_df = filtered_df[
                        filtered_df.index.isin(indexes)
                        ].copy()

                    if filtered_df.shape[0] != 0:
                        # Set velocities only for the filtered_df
                        # Update df using filtered_df
                        df.update(
                            cls.set_velocities(
                                df=filtered_df,
                                distribution=distribution,
                                angle_distribution=angle_distribution
                                )
                            )
                        if preserve_dtypes_dict:
                            df = df.astype(preserve_dtypes_dict)
                else:
                    # group_label not in df[group_field].values
                    # Do nothing and return unaltered df
                    pass
            except Exception as error:
                exception_burner([
                    error,
                    check_field_existance(df, [group_field, "vx", "vy"])
                    ])
            else:
                return df
        elif indexes is not None:
            try:
                # Filter agents by index
                filtered_df = df.iloc[indexes, :].copy()

                # Set velocities only for the filtered_df
                # Update df using filtered_df
                df.update(
                    cls.set_velocities(
                        df=filtered_df,
                        distribution=distribution,
                        angle_distribution=angle_distribution
                        )
                    )
                if preserve_dtypes_dict:
                    df = df.astype(preserve_dtypes_dict)
            except Exception as error:
                exception_burner([
                    error,
                    check_field_existance(df, ["vx", "vy"])
                    ])
            else:
                return df
        elif group_field is not None:
            try:
                if group_label in df[group_field].values:
                    filtered_df = df.loc[df[group_field] == group_label].copy()

                    # Set velocities only for the filtered_df
                    # Update df using filtered_df
                    df.update(
                        cls.set_velocities(
                            df=filtered_df,
                            distribution=distribution,
                            angle_distribution=angle_distribution
                            )
                        )
                    if preserve_dtypes_dict:
                        df = df.astype(preserve_dtypes_dict)
                else:
                    # group_label not in df[group_field].values
                    # Do nothing and return unaltered df
                    pass
            except Exception as error:
                exception_burner([
                    error,
                    check_field_existance(df, [group_field, "vx", "vy"])
                    ])
            else:
                return df
        else:
            try:
                # Set velocities for all the agents in df
                df = cls.set_velocities(
                    df=df,
                    distribution=distribution,
                    angle_distribution=angle_distribution
                    )
            except Exception as error:
                exception_burner([
                    error,
                    check_field_existance(df, ["vx", "vy"])
                    ])
            else:
                return df

    @classmethod
    def update_velocities(
        cls,
        df: DataFrame,
        distribution: Distribution,
        angle_variance: float,
        indexes: Union[list, ndarray, None] = None,
        group_field: Optional[str] = None,
        group_label: Optional[str] = None,
        preserve_dtypes_dict: Optional[dict] = None
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

            angle_variance : float
                Standard deviation of the normal distribution
                used for changing the direction of the velocity
                from its initial value

            indexes : TODO

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
            set_velocities : TODO complete explanation

            Examples
            --------
            TODO: include some examples
        """
        if indexes is not None and group_field is not None:
            try:
                if group_label in df[group_field].values:
                    filtered_df = df.loc[df[group_field] == group_label].copy()

                    # Filter agents by index
                    filtered_df = filtered_df[
                        filtered_df.index.isin(indexes)
                        ].copy()

                    if filtered_df.shape[0] != 0:
                        # Set velocities only for the filtered_df
                        # Update df using filtered_df
                        df.update(
                            cls.set_velocities(
                                df=filtered_df,
                                distribution=distribution,
                                angle_variance=angle_variance
                                )
                            )
                        if preserve_dtypes_dict:
                            df = df.astype(preserve_dtypes_dict)
                else:
                    # group_label not in df[group_field].values
                    # Do nothing and return unaltered df
                    pass
            except Exception as error:
                exception_burner([
                    error,
                    check_field_existance(df, [group_field, "vx", "vy"])
                    ])
            else:
                return df
        elif indexes is not None:
            try:
                # Filter agents by index
                filtered_df = df.iloc[indexes, :].copy()

                # Set velocities only for the filtered_df
                # Update df using filtered_df
                df.update(
                    cls.set_velocities(
                        df=filtered_df,
                        distribution=distribution,
                        angle_variance=angle_variance
                        )
                    )
                if preserve_dtypes_dict:
                    df = df.astype(preserve_dtypes_dict)
            except Exception as error:
                exception_burner([
                    error,
                    check_field_existance(df, ["vx", "vy"])
                    ])
            else:
                return df
        elif group_field is not None:
            # group_field is not None
            try:
                if group_label in df[group_field].values:
                    filtered_df = df.loc[df[group_field] == group_label].copy()

                    # Change velocities only for the filtered_df
                    # Update df using filtered_df
                    df.update(
                        cls.set_velocities(
                            df=filtered_df,
                            distribution=distribution,
                            angle_variance=angle_variance
                            )
                        )
                    if preserve_dtypes_dict:
                        df = df.astype(preserve_dtypes_dict)
                else:
                    # group_label not in df[group_field].values
                    # Do nothing and return unaltered df
                    pass
            except Exception as error:
                exception_burner([
                    error,
                    check_field_existance(df, [group_field, "vx", "vy"])
                    ])
            else:
                return df
        else:
            try:
                # Change velocities for all the agents in df
                df = cls.set_velocities(
                    df=df,
                    distribution=distribution,
                    angle_variance=angle_variance
                    )
            except Exception as error:
                exception_burner([
                    error,
                    check_field_existance(df, ["vx", "vy"])
                    ])
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
        # Random index when there are more than one max value.
        index = \
            greatest_angle_to_avoid.relative_angle.sample().index[0]
        # Standardize angles on the interval [0, 2*pi]
        return cls.standardize_angle(
            greatest_angle_to_avoid["relative_angle"].loc[index] +
            greatest_angle_to_avoid["consecutive_angle"].loc[index]/2
            )

    @classmethod
    def replace_velocities(
        cls,
        row: Series,
        new_angles: Series
    ) -> Series:
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
        try:
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

            df = df.apply(
                lambda row: cls.replace_velocities(row, new_angles),
                axis=1
                )
        except Exception as error:
            exception_burner([
                error,
                check_field_existance(df, ["agent", "x", "y", "vx", "vy"])
                ])
        else:
            return df
