from pydantic import BaseModel


class HealthSystem(BaseModel):
    """
        TODO
    """
    hospital_capacity: int
    ICU_capacity: int
