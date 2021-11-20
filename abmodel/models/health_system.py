from pydantic import BaseModel


class HealthSystem(BaseModel):
    """
        TODO: Add brief explanation

        Attributes
        ----------
        TODO

        Examples
        --------
        TODO: include some examples
    """
    hospital_capacity: int
    ICU_capacity: int
