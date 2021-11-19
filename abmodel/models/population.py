from datetime import datetime, timedelta
from collections import namedtuple

from pydantic import BaseModel


BoxSize = namedtuple("BoxSize", "left right bottom top")


class Configutarion(BaseModel):
    """
        TODO: Add brief explanation

        Attributes
        ----------
        TODO

        Examples
        --------
        TODO: include some examples
    """
    population_number: int
    initial_date: datetime
    iteration_time: timedelta
    box_size: BoxSize
    alpha: float  # Reduction factor of spread prob due to hospitalization
    beta: float  # Reduction factor of spread prob due to being isolated
    # box_size_units:
