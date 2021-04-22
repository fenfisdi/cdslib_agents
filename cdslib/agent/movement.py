from pandas.core.frame import DataFrame

from cdslib.models.population import BoxSize


class AgentMovement:

    @classmethod
    def apply_movement(cls, dataframe: DataFrame, box_size: BoxSize, dt: float):
        """
        Function to apply as transformation in a pandas Dataframe to update
        coordinates from the agent with its velocities.

        Parameters
        ----------
        dataframe: DataFrame
            Dataframe to apply transformation, must have x, y, vx, vy columns.
        box_size: BoxSize
            Parameter according to the region coordinates.
        dt: float
            Local time step, representing how often to take a measure.

        Returns
        -------
        DataFrame
            Dataframe with the transformations in columns x and y
        """

        # Update current position of the agent with its velocities
        dataframe.x += dataframe.vx * dt
        dataframe.y += dataframe.vy * dt

        # Verify if coordinates are out of the box, its return to the box limit
        if dataframe.x < box_size.left:
            dataframe.vx = -dataframe.vx
            dataframe.x = box_size.left
        if dataframe.x > box_size.right:
            dataframe.vx = -dataframe.vx
            dataframe.x = box_size.right

        if dataframe.y < box_size.bottom:
            dataframe.vy = -dataframe.vy
            dataframe.y = box_size.bottom
        if dataframe.y > box_size.top:
            dataframe.vy = -dataframe.vy
            dataframe.y = box_size.top

        return dataframe
