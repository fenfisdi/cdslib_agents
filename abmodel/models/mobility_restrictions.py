from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, root_validator
from pydantic.dataclasses import dataclass

from abmodel.models.base import SimpleGroups

# ============================================================================
# Mobility restrictions by tracing interest variables
# (hereinafter abbreviated as MRT)
#
# Mobility restrictions (hereinafter abbreviated as MR or mr)
# ============================================================================


class InterestVariables(Enum):
    """
        This class enumerates the interest variables
        for tracing and determining mobility restriction policies.
    """
    dead = "dead by disease"
    diagnosed = "diagnosed"
    ICU = "ICU capacity"
    hospital = "hospital capacity"


class MRTStopModes(Enum):
    level_number = "level_number"
    length = "length"


class MRTLengthUnits(Enum):
    days = "days"
    weeks = "weeks"
    months = "months"


class MRTracing(BaseModel):
    """
        TODO
    """
    variable: InterestVariables
    mr_start_level: int
    mr_stop_mode: MRTStopModes
    mr_stop_level: Optional[int]
    mr_length: Optional[int]
    mr_length_units: Optional[MRTLengthUnits]
    target_groups: list[str]

    @root_validator(pre=True)
    def validate(
        cls,
        v: dict[str, Any]
    ) -> dict[str, Any]:
        """
            TODO
        """
        mode = v.get("mr_stop_mode")
        if mode == MRTStopModes.level_number:
            if not v.get("mr_stop_level"):
                raise ValueError(
                    "A valid value for `mr_stop_level` was expected"
                    )
            if v.get("mr_length") and v.get("mr_length_units"):
                raise ValueError(
                    f"""
                        `mr_stop_mode` was set to
                        `{MRTStopModes.level_number}`.
                        So, `mr_length` and `mr_length_units`
                        should not be provided.
                    """
                    )
        if mode == MRTStopModes.length:
            if not v.get("mr_length"):
                raise ValueError(
                    "A valid value for `mr_length` was expected"
                    )
            if not v.get("mr_length_units"):
                raise ValueError(
                    "A valid value for `mr_length_units` was expected"
                    )
            if v.get("mr_stop_level"):
                raise ValueError(
                    f"""
                        `mr_stop_mode` was set to
                        `{MRTStopModes.length}`.
                        So, `mr_stop_level` should not be provided.
                    """
                    )
        # TODO: validate target_groups
        # if v.get("target_groups")
        return v


@dataclass
class MRTPolicies(BaseModel):
    """
        TODO
    """
    policies: dict[InterestVariables, MRTracing]


# ============================================================================
# Cyclic mobility restrictions (hereinafter abbreviated as CMR)
# ============================================================================
