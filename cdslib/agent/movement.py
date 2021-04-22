from pandas.core.frame import DataFrame

from cdslib.models.population import BoxSize


class AgentMovement:

    @classmethod
    def apply_movement(cls, dataframe: DataFrame, box_size: BoxSize):
        """

        """
        dataframe.x += dataframe.vx
        dataframe.y += dataframe.vy

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
