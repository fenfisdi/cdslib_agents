from pydantic import BaseModel


class HealthSystem(BaseModel):
    """
    """
    hospital_capacity: int
    ICU_capacity: int
