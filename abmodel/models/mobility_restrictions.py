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

from enum import Enum
from typing import Optional, Any, Union
from datetime import datetime
from dataclasses import field
from datetime import timedelta

from pydantic import root_validator
from pydantic.dataclasses import dataclass
from numpy import random

from abmodel.models import SimpleGroups
from abmodel.utils.units import timedelta_to_days

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


def time_interval_to_steps(
    mr_length: int,
    mr_length_units: MRTimeUnits,
    iteration_time: timedelta
) -> float:
    """
        TODO: Add brief explanation
    """
    iteration_time = timedelta_to_days(iteration_time)
    if mr_length_units == MRTimeUnits.days:
        mr_length_in_days = mr_length
    if mr_length_units == MRTimeUnits.weeks:
        mr_length_in_days = 7*mr_length
    if mr_length_units == MRTimeUnits.months:
        mr_length_in_days = 30*mr_length
    mr_length_in_steps = \
        timedelta_to_days(timedelta(days=mr_length_in_days)) / iteration_time
    return mr_length_in_steps


def random_time_interval_to_steps(
    mr_length: int,
    mr_length_units: MRTimeUnits,
    iteration_time: timedelta
) -> float:
    """
        TODO: Add brief explanation
    """
    iteration_time = timedelta_to_days(iteration_time)
    unrestricted_time = int(random.randint(1, mr_length + 1, 1)[0])

    if mr_length_units == MRTimeUnits.days:
        unrestricted_time_in_days = unrestricted_time
    if mr_length_units == MRTimeUnits.weeks:
        unrestricted_time_in_days = 7*unrestricted_time
    if mr_length_units == MRTimeUnits.months:
        unrestricted_time_in_days = 30*unrestricted_time
    unrestricted_time_steps = \
            timedelta_to_days(
                timedelta(days=unrestricted_time_in_days)
                ) / iteration_time
    return unrestricted_time_steps


@dataclass
class MRTracingPolicies:
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
    mr_groups: SimpleGroups
    target_groups: list[str]
    mr_stop_level: Optional[int] = None
    mr_length: Optional[int] = None
    mr_length_units: Optional[MRTimeUnits] = None
    mr_length_in_steps: float = field(default=None, init=False)

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

    def set_mr_length_in_steps(self, iteration_time: timedelta):
        self.mr_length_in_steps = time_interval_to_steps(
            self.mr_length,
            self.mr_length_units,
            iteration_time
        )

# ============================================================================
# Cyclic mobility restrictions (hereinafter abbreviated as CyclicMR)
# ============================================================================


class CyclicMRModes(Enum):
    """
        TODO: Add brief explanation
    """
    random = "random"
    fixed = "fixed"


@dataclass
class GlobalCyclicMR:
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
    unrestricted_time_units: MRTimeUnits
    unrestricted_time: Optional[int] = None
    global_mr_length_steps: float = field(default=False, init=False)
    unrestricted_time_steps: Union[float, None] = None

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

    def set_global_mr_length(self, iteration_time: timedelta):
        self.global_mr_length_steps = time_interval_to_steps(
            self.global_mr_length,
            self.global_mr_length_units,
            iteration_time
        )

    def set_unrestricted_time(self, itertation_time: timedelta):
        if self.unrestricted_time_mode == CyclicMRModes.fixed:
            self.unrestricted_time_steps = time_interval_to_steps(
                self.unrestricted_time,
                self.unrestricted_time_units,
                itertation_time
            )
        if self.unrestricted_time_mode == CyclicMRModes.random:
            self.unrestricted_time_steps = \
                random_time_interval_to_steps(
                    self.global_mr_length,
                    self.unrestricted_time_units,
                    itertation_time
                )

    def set_none_unrestricted_time(self):
        self.unrestricted_time_steps = None


@dataclass
class CyclicMRPolicies:

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
    delay_in_steps: float = field(default=False, init=False)
    mr_length_in_steps: float = field(default=False, init=False)
    time_without_restrictions_steps: float = \
        field(default=False, init=False)

    def set_delay(self, iteration_time: timedelta):
        self.delay_in_steps = time_interval_to_steps(
        self.delay,
        self.delay_units,
        iteration_time
    )

    def set_mr_length(self, iteration_time: timedelta):
        self.mr_length_in_steps = time_interval_to_steps(
            self.mr_length,
            self.mr_length_units,
            iteration_time
        )

    def set_time_without_restrictions(
        self,
        iteration_time: timedelta
    ):
        self.time_without_restrictions_steps = time_interval_to_steps(
            self.time_without_restrictions,
            self.time_without_restrictions_units,
            iteration_time
        )
