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
#This package is authored by:
#Camilo Hincapié (https://www.linkedin.com/in/camilo-hincapie-gutierrez/) (main author)
#Ian Mejía (https://github.com/IanMejia)
#Emil Rueda (https://www.linkedin.com/in/emil-rueda-424012207/)
#Nicole Rivera (https://github.com/nicolerivera1)
#Carolina Rojas Duque (https://github.com/carolinarojasd)
#and the conceptual contributions about epidemiology of
#Lina Marcela Ruiz Galvis (mailto:lina.ruiz2@udea.edu.co).
#
#Other remarkably contributors to this work were
#Alejandro Campillo (https://www.linkedin.com/in/alucardcampillo/)
#Daniel Alfonso Montoya (https://www.linkedin.com/in/daniel-montoya-ds/).


from enum import Enum
from typing import Optional, Any
from datetime import datetime

from pydantic import BaseModel, root_validator

from abmodel.models import SimpleGroups

# ============================================================================
# Mobility restrictions by tracing variables of interest
# (hereinafter abbreviated as MRT)
#
# Mobility restrictions (hereinafter abbreviated as MR or mr)
# ============================================================================


class InterestVariables(Enum):
    """
        This class enumerates the variables of interest
        for tracing and determining mobility restriction policies.
    """
    dead = "dead_by_disease"
    diagnosed = "diagnosed"
    ICU = "ICU_capacity"
    hospital = "hospital_capacity"


class MRTStopModes(Enum):
    """
        TODO: Add brief explanation
    """
    level_number = "level_number"
    length = "length"


class MRTimeUnits(Enum):
    """
        TODO: Add brief explanation
    """
    days = "days"
    weeks = "weeks"
    months = "months"


class MRTracingPolicies(BaseModel):
    """
        TODO: Add brief explanation

        Attributes
        ----------
        TODO

        Examples
        --------
        TODO: include some examples
    """
    variable: InterestVariables
    mr_start_level: int
    mr_stop_mode: MRTStopModes
    mr_stop_level: Optional[int]
    mr_length: Optional[int]
    mr_length_units: Optional[MRTimeUnits]
    mr_groups: SimpleGroups
    target_groups: list[str]

    @root_validator
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
        # Check if all elements of `target_groups` are in `mr_groups`
        mr_groups = v.get("mr_groups").names
        target_groups = v.get("target_groups")
        if not all(elem in mr_groups for elem in target_groups):
            raise ValueError(
                f"""
                    All `target_groups` must be in
                    `mr_groups = {mr_groups}`.
                """
                )
        return v


# ============================================================================
# Cyclic mobility restrictions (hereinafter abbreviated as CyclicMR)
# ============================================================================

class CyclicMRModes(Enum):
    """
        TODO: Add brief explanation
    """
    random = "random"
    fixed = "fixed"


class GlobalCyclicMR(BaseModel):
    """
        TODO: Add brief explanation

        Attributes
        ----------
        TODO

        Examples
        --------
        TODO: include some examples
    """
    enabled: bool
    grace_time: datetime
    global_mr_length: int
    global_mr_length_units: MRTimeUnits
    unrestricted_time_mode: CyclicMRModes
    unrestricted_time: Optional[int]
    unrestricted_time_units: MRTimeUnits

    @root_validator
    def validate(
        cls,
        v: dict[str, Any]
    ) -> dict[str, Any]:
        """
            TODO
        """
        mode = v.get("unrestricted_time_mode")

        if mode == CyclicMRModes.random and v.get("unrestricted_time"):
            raise ValueError(
                f"""
                    `unrestricted_time_mode` was set to
                    `{CyclicMRModes.random}`.
                    So, `unrestricted_time` should not be provided.
                """
                )
        if mode == CyclicMRModes.fixed and not v.get("unrestricted_time"):
            raise ValueError(
                f"""
                    `unrestricted_time_mode` was set to
                    `{CyclicMRModes.fixed}`.
                    So, `unrestricted_time` should be provided.
                """
                )
        return v


class CyclicMRPolicies(BaseModel):
    """
        TODO: Add brief explanation

        Attributes
        ----------
        TODO

        Examples
        --------
        TODO: include some examples
    """
    mr_groups: SimpleGroups
    target_group: str
    delay: int
    delay_units: MRTimeUnits
    mr_length: int
    mr_length_units: MRTimeUnits
    time_without_restrictions: int
    time_without_restrictions_units: MRTimeUnits
