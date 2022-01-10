from typing import Optional, Union

from math import fmod
from numpy import ndarray, arctan2, cos, sin, pi, sqrt, inf, frompyfunc
from pandas.core.frame import DataFrame

from abmodel.models.population import BoxSize
from abmodel.models.disease import MobilityGroups, DistTitles
from abmodel.utils.distributions import Distribution
from abmodel.utils.utilities import check_field_errors
from abmodel.utils.utilities import check_field_existance, exception_burner


def move_individual_agent(
    row: DataFrame,
    box_size: BoxSize,
    dt: float
) -> DataFrame:
    """
    Moves spatially each agent by updating its positions,
    each agent is represented by a row containing its positions and 
    velocities.

    Parameters
    ----------
    row : DataFrame
        A row from a DataFrame. 
        Must have x, y, vx and vy columns. 
    
    box_size : BoxSize
        Named tuple that contains the box dimensions. 
        Must have top, bottom, right and left names.   
    
    dt : float
        Time step for the movement.

    Returns
    -------
    row : DataFrame
        Agent's position and velocity updated according to its movement.

    Notes
    -----
    The new position is calculated as x = x_0 + v_x * dt according to 
    classical mechanics equations of motion.
    If the new coordinates are outside the box, the agent's new position will 
    be the box boundary and the velocity will be changed in the opposite direction.

    TODO: explanatory image

    Examples
    --------
    `>>> box_size = BoxSize(-10, 10, -20, 20)`

    `>>> df = pandas.DataFrame({`

    `...                        "x": [1, 1, -30],`

    `...                        "y": [20, 5, 0],`

    `...                        "vx": [0, 1, 15],`

    `...                        "vy": [5, 1, 15]})`

    `>>> move_individual_agent(df.iloc[0], box_size, 2)`

    `x      1`  

    `y      20`

    `vx     0`

    `vy    -5`

    `Name: 0, dtype: int64`

    `>>> move_individual_agent(df.iloc[1], box_size, 2)`

    `x     3`

    `y     7`

    `vx    1`

    `vy    1`
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
        Class containing all the methods used to move the agents.
        No initialization is required. 

        Methods
        -------
        init_required_fields()
            Initializes each required column of the DataFrame that contains all
            the agent's information for it's movement.

        move_agents()
            Applies a transformation in pandas DataFrame to update agent's
            coordinates and velocities.
        
        stop_agents()
            Sets the velocity of a given set of agents to zero.

        standardize_angle()
            Standardizes angles to be in the interval [-pi, pi].

        angle()
            Returns the standardized angle formed by the components `x` and `y`.

        vector_angles()
            Calculates vector angles from their euclidean components.

        set_velocities()
            Assigns the velocities' components vx and vy according to the mobility profile 
            (ie. velocity distribution) and the angle distribution for each agent.
        
        initialize_velocities()
            Initializes the velocity of a given set of agents from a given
            mobility profile (i.e. a velocity distribution) and assign an angle
            to the velocity according to the angle distribution defined.

        update_velocities()
            Update the velocity of a given set of agents from a given
            mobility profile (i.e. a velocity distribution) and
            deviating the resulting angles using a normal distribution
            with a standard deviation equal to `angle_variance`.

        replace_velocities()
            Calculates the agent's velocity components, vx and vy, according to
            the new direction of movement in new_angle. The velocity norm
            remains unchanged.

        avoid_agents()
            Changes agent's movement direction acoording to the position of the
            agents to avoid.
    """
    @classmethod
    def init_required_fields(
        cls,
        df: DataFrame,
        box_size: BoxSize,
        mobility_groups: MobilityGroups
    ) -> DataFrame:
        """
            Initializes each required column of the DataFrame that contains all the agent's
            information for it's movement. 
            The agent's positions are initialized randomly and their velocities are initialized
            according to the velocities distribution for each mobility group.
            The velocities distribution follows one or few mobility profiles from our pakage. It
            allows to build an empirical distribution from the data or a theorical distribution
            following some numpy distributions. It also allows to build a step by step probability
            of movement or a constant velocity.  

            Parameters
            ----------
            df : DataFrame
                DataFrame to initialize agent's information. 
                Must have `x`, `y`, `vx` and `vy` columns.

            box_size : BoxSize
                Parameter with the region coordinates.

            mobility_groups : MobilityGroups
                Dataclass that wraps all mobility groups.

            Returns
            -------
            df : DataFrame
                DataFrame containing all agent's information initialized

            Raises
            ------
            ValueError
                If the dataframe contains some any column with null values.

            Notes
            -----
            The new position is calculated as x = x_0 + v_x * dt for each direction
            according to classical mechanics equations of motion.
            If the new coordinates are outside the box, the agent's new position will 
            be the box boundary and the velocity will be changed in the opposite direction.
            
            See Also
            --------
            move_individual_agent : Moves spatially each agent by updating its positions,
            each agent is represented by a row containing its positions and velocities.

            Examples
            --------
            `>>> box_size = BoxSize(-10, 10, -20, 20)`

            `>>> df = pandas.DataFrame({`

            `...                        "mobility_group": ["MG_1" for i in range(11)],`

            `...                        "agent": [i for i in range(11)],`

            `...                        "step": [i for i in range(11)]`

            `...                         }`)`

            `>>> dist_title = "MobilityGroup_test_dist"`

            `>>> group_info = [`

            `...             {`

            `...                 "name": "MG_1",`

            `...                 "angle_variance": 0.5,`

            `...                 "dist_info": {`

            `...                     "dist_title": "mobility_profile",`

            `...                     "dist_type": "numpy",`

            `...                     "constant": None,`

            `...                     "dist_name": "standard_t",`

            `...                     "filename": None,`

            `...                     "data": None,`

            `...                     "kwargs": {"df": 12}`

            `...                     }`

            `...             }`

            `...         ]`

            `>>>  mobility_groups = MobilityGroups(`

            `...             dist_title=dist_title,`

            `...             group_info=group_info`

            `...             )`

            Using a t-student distribution for initializing the velocity columns
            of the agents:

            `>>> AgentMovement.init_required_fields(`

            `...             df,`

            `...             box_size,`

            `...             mobility_groups`

            `...             )`

            `   mobility_group  agent  step         x          y        vx        vy`

            0            MG_1      0     0  2.142089   4.284179 -0.346793 -0.276421

            1            MG_1      1     1 -6.153857 -12.307714  0.036282  0.095668

            2            MG_1      2     2 -0.246706  -0.493411 -0.058564  0.004548

            3            MG_1      3     3 -3.287691  -6.575382  0.282031 -0.472708

            4            MG_1      4     4 -9.744158 -19.488316  0.671520  0.054090

            5            MG_1      5     5  3.851982   7.703964 -0.177289 -0.470067

            6            MG_1      6     6 -1.624530  -3.249060 -0.648740  0.363186

            7            MG_1      7     7 -5.100455 -10.200910  0.036275  1.149052

            8            MG_1      8     8  7.303318  14.606637  0.448418 -0.507563

            9            MG_1      9     9 -0.888201  -1.776402  0.061069 -0.017497

            10           MG_1     10    10  1.474884   2.949768  0.101585  0.050754

            Using a numpy array with empirical data for initializing the velocity columns
            of the agents:

            `data = numpy.array([  0.21098677,   0.78064842, -17.54581766,   2.01904915,`

            `...         3.1266283 ,   0.87632915,  -8.27963531,   4.16632438,`

            `...         9.71253144,  -5.34824282,])`   

            `group_info = [`

            `...             {`

            `...                 "name": "MG_1",`

            `...                 "angle_variance": 0.1,`

            `...                 "dist_info": {`

            `...                     "dist_title": "mobility_profile",`

            `...                     "dist_type": "empirical",`

            `...                     "constant": 0.4,`

            `...                     "dist_name": None,`

            `...                     "filename": None,`

            `...                     "data": data,`

            `...                     "kwargs": {`

            `...                         "kernel": "gaussian",`

            `...                         "bandwidth": 0.1`

            `...                         }`

            `...                     }`

            `...             }`

            `...         ]`

            `>>>  mobility_groups = MobilityGroups(`

            `...             dist_title=dist_title,`

            `...             group_info=group_info`

            `...             )`

            `>>> AgentMovement.init_required_fields(`

            `...             df,`

            `...             box_size,`

            `...             mobility_groups`

            `...             )`

            `        mobility_group  agent  step         x          y         vx         vy`

            0            MG_1      0     0  5.954352  11.908703   4.586353 -14.835973

            1            MG_1      1     1 -9.692957 -19.385914  16.088107   1.556695

            2            MG_1      2     2 -2.616717  -5.233434 -10.961765  11.796639

            3            MG_1      3     3 -5.339758 -10.679516   0.115379   1.076844

            4            MG_1      4     4  8.271661  16.543323 -14.966665   9.032067

            5            MG_1      5     5  4.300905   8.601811  -0.668186  -2.993292

            6            MG_1      6     6  8.491871  16.983742   2.774055  -1.422387

            7            MG_1      7     7 -2.494255  -4.988510  -6.738378   6.714099

            8            MG_1      8     8 -7.919017 -15.838034 -13.957463 -10.693572

            9            MG_1      9     9 -1.260219  -2.520439 -14.960231   6.253076

            10           MG_1     10    10  6.470672  12.941344  -7.757426  15.577985

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
            
            ValueError
                If the dataframe contains some any column with null values.

            Notes
            -----
            The new position is calculated as x = x_0 + v_x * dt according to 
            classical mechanics equations of motion.
            If the new coordinates are outside the box, the agent's new position will 
            be the box boundary and the velocity will be changed in the opposite direction.
            TODO: explanatory image (same as move_individual_agent)

            See Also
            --------
            move_individual_agent :
                Moves spatially each agent by updating its positions,
                each agent is represented by a row containing its positions and 
                velocities.
                This function is applied over a DataFrame's row and returns the
                agent's position and velocity updated according to its movement.

            Examples
            --------
            `>>> df = pandas.DataFrame({`
            `...                         "x": [1, 2, 4, 8],`

            `...                         "y": [0, 10, 1, 3],`

            `...                         "vx": [1, 2, 0, 1],`

            `...                         "vy": [10, 12, 4, 0]`

            `...                          })`

            `>>> box_size = BoxSize(-20, 20, -20, 20)`

            `>>> dt = 1`

            `>>> AgentMovement.move_agents(df, box_size, dt)`

            `   x   y  vx  vy`

            3  9   3   1   0

            0  2  10   1  10

            1  4  20   2 -12

            2  4   5   0   4

            3  9   3   1   0
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
            `>>> df = pandas.DataFrame({`

            `...                          "x": [1, 3, 4, 6],`

            `...                          "y": [0, 0, 7, 3],`

            `...                          "vx": [1, 9, 0, 1],`

            `...                           "vy": [11, 12, 4, 6]`

            `...                            })`

            `>>> AgentMovement.stop_agents(df, [1, 2])`

            `   x  y  vx  vy`

            0  1  0   1  11

            1  3  0   0   0

            2  4  7   0   0

            3  6  3   1   6
        """
        try:
            df.loc[indexes, "vx"] = 0
            df.loc[indexes, "vy"] = 0
        except Exception as error:
            exception_burner([
                error,
                check_field_existance(df, ["vx", "vy"])
                ])
        else:
            return df

    @classmethod
    def standardize_angle(cls, angle: float) -> float:
        """
            Standardize angles to be in the interval [0, 2pi)

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
            The equivalent angle is calculated as the remainder of the division
            (angle+2pi) / 2pi. This means any angle will be mapped to the interval
            [0, 2pi) in order to improve succiding calculation's performance. 
            This new standardized angle is aim to be used to calculate the velocity
            components by means of the cosine trigonometric function, so the equivalence
            is valid.
            TODO: explanatory image (mapeo)

            Examples
            --------
            `>>> AgentMovement.standardize_angle(13*np.pi/4)`

            3.9269908169872423

            `>>> AgentMovement.standardize_angle(18*np.pi/8)`

            0.7853981633974492
        """
        return fmod(angle + 2*pi, 2*pi)

    @classmethod
    def angle(cls, x: float, y: float) -> float:
        """
            Returns the standardized angle formed by the components
            `x` and `y`.

            Parameters
            ----------
            x : float
                'x' component of the angle

            y : float 
                'y' component of the angle 

            Returns
            -------
            angle : float
                standardized angle formed by the components 'x' and 'y'

            Notes
            -----
            Using the definition from a right triangle, the angle formed
            by the components `x` and `y` is calculated as arctan(y/x) where
            `y` is the opposite cathetus and `x` is the adjacent cathetus. 
            The element-wise function numpy.arctan2 is used in order to 
            assure values in the interval [-pi, pi]. 
            All resulting angles are mapped to the interval [0, 2pi) in order
            to improve succiding calculation's performance.
            TODO: explanatory image (right triangle calculation)

            See Also
            --------
            standardize_angle : 
                Standardize angles to be in the interval [0, 2pi).
                The equivalent angle is calculated as the remainder of 
                the division (angle+2pi) / 2pi. 

            Examples
            --------
            `>>> AgentMovement.angle(1, 0)`

            0.0

            `>>> AgentMovement.angle(-1, -1)`

            3.9269908169872414
        """
        # Standardize angles on the interval [0, 2*pi)
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
            Using the definition from a right triangle, the angle formed
            by the components `x` and `y` is calculated as arctan(y/x) where
            `y` is the opposite cathetus and `x` is the adjacent cathetus.
            All resulting angles are mapped to the interval [0, 2pi) in order
            to improve succiding calculation's performance.
            TODO: explanatory image (same as angle)

            See Also
            --------
            angle :
                Element-wise function.
                Returns the standardized angle formed by the given components
                `x` and `y`. 

            Examples
            --------
            `>>> df = pandas.DataFrame({`

            `...                        "x": [1, 3, 4],`

            `...                        "y": [1, 0, 7],`

            `...                       "vx": [1, 9, 0],`

            `...                       "vy": [3, 2, 0]`

            `...                        })`

            `>>> AgentMovement.vector_angles(df, ["x", "y" ])`

            0    0.785398

            1    0.000000

            2    1.051650

            dtype: float640

            `>>> AgentMovement.vector_angles(df, ["vx", "vy" ])`

            0    1.249046

            1    0.218669

            2    0.000000

            dtype: float640
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
            Assigns the velocities' components vx and vy according to the mobility profile 
            (ie. velocity distribution) and the angle distribution for each agent. 
            If no angle distribution is specified, the function deviates the resulting
            angles using a normal distribution with a standard deviation equal to `angle_variance`.

            Parameters
            ----------
            df : DataFrame
                Dataframe to apply transformation.
                Must have `vx` and `vy` columns.

            distribution : Distribution
                Mobility profile. This is the velocity distribution
                to use for updating the population velocities each
                time step.

            angle_variance : float, optional
                Standard deviation of the normal distribution
                used for changing the direction of the velocity
                from its initial value

            angle_distribution : Distribution, optional
                Angle profile to assign an angle following a certain distribution
                to the agent's information.

            Returns
            -------
            df : DataFrame
                Dataframe with applied transformation. 

            Raises
            ------
            ValueError
                If the dataframe `df` does not have `vx` and `vy` columns.

            Notes
            -----
            The velocity components are calculated as vx = v_norm * cos(angle) and 
            vy = v_norm * sin(angle) respectively. 
            The velocity norm (v_norm) is set as a random sample of size n equals
            to the lenght of the DataFrame index using 
            abmodel.utils.distributions.Distribution's method sample.
            The velocity angle is computed according to the given angle distribution. 
            If no angle distribution is specified, the velocity angles are computed 
            using a normal distribution with a standard deviation equal to `angle_variance`. 
            TODO: explanatory image (same as angle)

            See Also
            --------
            abmodel.utils.distributions.Distribution : 
                Distribution class
                It computes random numbers from a probability density distribution.

            standardize_angle :
                Standardize angles to be in the interval [0, 2pi).
                The equivalent angle is calculated as the remainder of 
                the division (angle+2pi) / 2pi.

            Examples
            --------
            Without passing angle_distribution:

            `>>> df = pandas.DataFrame({"vx": [1, 9, 0], "vy": [3, 2, 0]})`

            `>>> distribution = Distribution(`

            `...             dist_type="numpy",`

            `...             dist_name="gamma",`

            `...             shape=5`

            `...             )`

            `>>> AgentMovement.set_velocities(df, distribution, 0.1)`

            `         vx        vy`

            0  0.730606  3.411171

            1  2.395679  0.261366

            2  1.421091 -0.131577

            Usign a standard_t angle_distribution:

            `>>> angle_distribution = Distribution(`

            `...             dist_type="numpy",`

            `...             dist_name="standard_t",`

            `...              df=6)`

            `>>> AgentMovement.set_velocities(df, distribution, None, angle_distribution)`

            `         vx        vy`

            0  6.599700  3.566292

            1 -3.392121  7.139459

            2  3.884318 -2.316200
        """
        try:
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
                angles = standardize_angle_array(angles).astype(float)

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
            Initializes the velocity of a given set of agents from a given
            mobility profile (i.e. a velocity distribution) and assign an angle
            to the velocity according to the angle distribution defined. 
            The velocity is initilized by defining it's components vx and vy. 

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
                Angle profile to assign an angle following a certain distribution
                to the agent's information.

            indexes : list or ndarray
                DataFrame indexes over which to filter the set of agents.
                If not provided, then the set of agents used is
                going to be the whole set of agents.

            group_field : str, optional
                The field over which to filter the set of agents.
                If not provided, then the set of agents used is
                going to be the whole set of agents.

            group_label : str, optional
                The value of the `group_filed` used to filter
                the set of agents. If `group_field` is not provided,
                then this parameter is ignored.

            preserve_dtypes_dict : dict, optional
                Dict that contains all the data types of the agent's information
                to keep it unchanged over the initialization.

            Returns
            -------
            df : DataFrame
                DataFrame with applied transformation

            Raises
            ------
            ValueError
                If the dataframe `df` does not have `vx` and `vy` columns

            Notes
            -----
            The method filters the whole DataFrame in order to apply the set.velocities()
            function only on the specified set of agents using the given mobility profile
            and angle distribution. 
            If no set of agents is specified, the whole DataFrame is initialized according
            to the given mobility profile and angle distribution.

            See Also
            --------
            set_velocities :
                Assigns the velocities' components vx and vy according to the mobility profile 
                (ie. velocity distribution) and the angle distribution for each agent. 
                If no angle distribution is specified, the function deviates the resulting
                angles using a normal distribution with a standard deviation equal to `angle_variance`.
                The velocity components are calculated as vx = v_norm * cos(angle) and 
                vy = v_norm * sin(angle) respectively.
                The velocity norm (v_norm) is set as a random sample of size n equals
                to the lenght of the DataFrame index using 
                abmodel.utils.distributions.Distribution's method sample.
                The velocity angle is computed according to the given angle distribution. 
                If no angle distribution is specified, the velocity angles are computed 
                using a normal distribution with a standard deviation equal to `angle_variance`.

            Examples
            --------
            Using a list of indexes:

            `>>> df = pandas.DataFrame({"vx": [1, 5, 12], "vy": [4, 2, 1]})`

            `>>> distribution = Distribution(`

            `...             dist_type="numpy",`

            `...             dist_name="gamma",`

            `...             shape=2`

            `...             )`

            `>>> angle_dist = Distribution(`

            `...             dist_type="constant",`

            `...             constant=pi/4`

            `...             )`

            `>>> indexes = [0, 1, 2]`

            `>>> AgentMovement.initialize_velocities(`

            `...             df,`

            `...             distribution,`

            `...             angle_dist,`

            `...             indexes,`

            `...             None,`

            `...             None,`

            `...             None,`

            `...             )`

            `         vx        vy`

            0  1.273968  1.273968

            1  0.630820  0.630820

            2  5.195250  5.195250

            Using a 'group_field':  

            `>>> df = pandas.DataFrame({`

            `...                       "vx": [1, 5, 12],`

            `...                       "vy": [4, 2, 1],`

            `...                        "mobility_group": ["MG_1", "MG_1", " MG_2"]`

            `...                        })`

            `>>> AgentMovement.initialize_velocities(`

            `...                 df,`

            `...                 distribution,`

            `...                 angle_dist,`

            `...                 None,`

            `...                 "mobility_group",`

            `...                 "MG_1", None`

            `...                 ) `     

            `        vx        vy        mobility_group`

            0   1.046147  1.046147           MG_1

            1   1.008751  1.008751           MG_1

            2  12.000000  1.000000           MG_2
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

            indexes : list or ndarray
                DataFrame indexes over which to filter the set of agents.
                If not provided, then the set of agents used is
                going to be the whole set of agents.

            group_field : str, optional
                The field over which to filter the set of agents.
                If not provided, then the set of agents used is
                going to be the whole set of agents.

            group_label : str, optional
                The value of the `group_filed` used to filter
                the set of agents. If `group_field` is not provided,
                then this parameter is ignored.

            preserve_dtypes_dict : dict, optional
                Dict that contains all the data types of the agent's information
                to keep it unchanged over the initialization.

            Returns
            -------
            df : DataFrame
                Dataframe that contains all agent's updated velocities 

            Raises
            ------
            ValueError
                If the dataframe `df` does not have `vx` and `vy` columns

            Notes
            -----
            The velocity direction change is calculated as:

            .. math::
                \theta_{new} = \theta_{former} + \Delta \theta

            Where :math: `\Delta \theta` is a random variable which
            follows a normal distribution with mean :math: `\mu = 0.0`
            and standard deviation equals to `angle_variance`.

            See Also
            --------
            set_velocities :
                Assigns the velocities' components vx and vy according to the mobility profile 
                (ie. velocity distribution) and the angle distribution for each agent. 
                If no angle distribution is specified, the function deviates the resulting
                angles using a normal distribution with a standard deviation equal to `angle_variance`.
                The velocity components are calculated as vx = v_norm * cos(angle) and 
                vy = v_norm * sin(angle) respectively.
                The velocity norm (v_norm) is set as a random sample of size n equals
                to the lenght of the DataFrame index using 
                abmodel.utils.distributions.Distribution's method sample.
                The velocity angle is computed according to the given angle distribution. 
                If no angle distribution is specified, the velocity angles are computed 
                using a normal distribution with a standard deviation equal to `angle_variance`.

            Examples
            --------
            Using 'group_field' and indexes at the same time:

            `>>> df = pandas.DataFrame({`

            `...                         "vx": [2, 1, 5],`

            `...                          "vy": [3, 0, 1],`

            `...                          "mobility_group": ["MG_1", "MG_1", " MG_2"]`

            `...                        })`

            `>>> indexes = [0, 2]`

            `>>> distribution = Distribution(`

            `...             dist_type="numpy",`

            `...             dist_name="normal",`

            `...             loc=5,`

            `...             scale  = 3`

            `...             )`

            `>>> AgentMovement.update_velocities(`

            `...                 df,`

            `...                 distribution,`

            `...                 0.2,`

            `...                 indexes,`

            `...                 "mobility_group",`

            `...                 "MG_1", None`

            `...                 )`        

            `        vx        vy mobility_group`

            0  0.150929  0.268848           MG_1

            1  1.000000  0.000000           MG_1

            2  5.000000  1.000000           MG_2

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
            Calculates the standardized deviation angle of an agent in order to 
            avoid some specific agents.

            Parameters
            ----------
            grouped_df : DataFrame
                DataFrame containing the relative angle to all the agents to avoid
                for each agent grouped by agent.
                Must have 'relative_angle' column.

            Returns
            -------
            angle : float
                Calculated agent's deviation angle to avoid some specific agents. 

            Notes
            -----
            The deviation angle is calculated as the middle angle in the greatest
            aperture window of all the consecutive angles between the agents to avoid.
            The consecutive angles are calculated as the difference between 
            the relative angles sorted ascending. 
            The hypothesis is that the agent will take the path that has, from the
            biggest aperture window midpoint, the greatest distance to any other 
            agent that it must avoid.
            TODO: explanatory image (apperture window and path)

            See Also
            --------
            standardize_angle : 
                Standardize angles to be in the interval [0, 2pi).
                The equivalent angle is calculated as the remainder of 
                the division (angle+2pi) / 2pi.

            Examples
            --------
            One agent with different relative angles

            `>>> df = pandas.DataFrame({`

            `...                        "Agent": [1, 1],`

            `...                         "relative_angle": [pi/4, pi/2]`

            `...                         })`

            `>>> df.groupby("Agent").apply(AgentMovement.deviation_angle)`

            Agent

            1    4.31969

            dtype: float64

            One agent with the same relative angle

            `>>> df = pandas.DataFrame({"Agent": [1, 1], "relative_angle": [pi/4, pi/4]})`

            `>>> df.groupby("Agent").apply(AgentMovement.deviation_angle)`

            Agent

            1    3.926991

            dtype: float64
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
            Calculates the agent's velocity components, vx and vy, according to
            the new direction of movement in new_angle. The velocity norm
            remains unchanged. 

            Parameters
            ----------
            row : DataFrame
                DataFrame's row containing the agent's position and velocity
                Must have 'agent', 'vx' and 'vy' columns.

            new_angles : DataFrame
                DataFrame that contains the new angles calculated in order to 
                continue it's movement.

            Returns
            -------
            row : DataFrame
                DataFrame's row containing the agent's new velocity.

            Notes
            -----
            The new velocity components are calculated according to the norm
            of the existing velocities and the new angle (ie. direction of 
            movement) as
            vx = velocity_norm * cos(new_angle)
            vy = velocity_norm * sin(new_angle)
            TODO: Explanatory image (same as angle)

            Examples
            --------
            `>>> df = pandas.DataFrame({`

            `...                       "agent": [1, 2, 3]`

            `...                       "vx": [1, 4, 8],`

            `...                        "vy": [2, 3, 0],`

            `...                         })`

            `>>>new_angles = pandas.Series({1: [numpy.pi], 2:[numpy.pi/2], 3:[numpy.pi/4]})`

            `>>>df = df.apply(`

            `...              lambda row: AgentMovement.replace_velocities(row, new_angles),`

            `...              axis=1)`

            `   agent  vx  vy`

            0      1  -2   0

            1      2   0   5

            2      3   5   5
        """
        if row.agent in new_angles.index:
            velocity_norm = sqrt(row.vx**2 + row.vy**2)
            row.vx = velocity_norm * cos(new_angles[row.agent])
            row.vy = velocity_norm * sin(new_angles[row.agent])
        return row

    @classmethod
    def avoid_agents(cls, df: DataFrame, df_to_avoid: DataFrame) -> DataFrame:
        """
            Changes agent's movement direction acoording to the position of the
            agents to avoid.

            Parameters
            ----------
            df : DataFrame
                Must have 'agent', 'x', 'y', 'vx' and 'vy' columns

            df_to_avoid : DataFrame
                Must have 'agent' and 'agent_to_avoid' columns

            Returns
            -------
            df : DataFrame
                Dataframe containing all the agent's new velocities and positions. 

            Raises
            ------
            ValueError
                If the dataframe `df` does not have: `agent`, `x`, `y`, `vx` and `vy` columns.

            Notes
            -----
            The method organizes all the information about the agents and their corresponding
            agents to avoid in order to update its movement taking into account the shift in 
            the agent's velocity by means of the calculated deviation angle according to the
            angles of their 'scary' agents.
            TODO: explanatory image (same as deviation_angle)

            See Also
            --------
            deviation_angle : 
                Calculates the standardized deviation angle of an agent in order to 
                avoid some specific agents.
                The deviation angle is calculated as the middle angle in the greatest
                aperture window of all the consecutive angles between the agents to avoid.
                The consecutive angles are calculated as the difference between 
                the relative angles sorted ascending. 
                The hypothesis is that the agent will take the path that has, from the
                biggest aperture window midpoint, the greatest distance to any other 
                agent that it must avoid.

            replace_velocities : 
                Calculates the agent's velocity components, vx and vy, according to
                the new direction of movement in order to avoid some specific agents.
                The velocity norm remains unchanged.
                The new velocity components are calculated according to the norm
                of the existing velocities and the new angle (ie. direction of 
                movement) as
                vx = velocity_norm * cos(new_angle)
                vy = velocity_norm * sin(new_angle)

            Examples
            --------
            One agent avoids two agents with different relative angles.

            `>>> df = pandas.DataFrame({`

            `...                        "agent": [1, 2, 3],`

            `...                         "x": [0, 1, 1],`

            `...                         "y": [0, 1, -1],`

            `...                         "vx": [1.0, 2.0, 0],`

            `...                         "vy": [0, 2.0,0],`

            `...                          })`

            `>>> df_avoid = pandas.DataFrame({`

            `...                             "agent": [1, 1],`

            `...                              "agent_to_avoid": [2, 3]`

            `...                              })`

            `>>> AgentMovement.avoid_agents(df,  df_avoid)`

            `   agent    x    y   vx            vy`

            0    1.0  0.0  0.0 -1.0  1.224647e-16

            1    2.0  1.0  1.0  2.0  2.000000e+00

            2    3.0  1.0 -1.0  0.0  0.000000e+00


            Two agents avoid one agent with different relative angles.

            `>>> df = pandas.DataFrame({`

            `...                        "agent": [1, 2, 3]`

            `...                        "x": [0, 1, 0]`

            `...                        "y": [0, 0, 1]`

            `...                        "vx": [1.0, 0.0, 10]`

            `...                        "vy": [0, 1, 10]`

            `...                         })

            ``>>> df_avoid = pandas.DataFrame({`

            `...                              "agent": [1, 2],`

            `...                               "agent_to_avoid": [3, 3]`

            `...                               })`

            `>>> AgentMovement.avoid_agents(df,  df_avoid)`

            `   agent    x    y            vx         vy`

            0    1.0  0.0  0.0 -1.836970e-16  -1.000000

            1    2.0  1.0  0.0  7.071068e-01  -0.707107

            2    3.0  0.0  1.0  1.000000e+01  10.000000
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
