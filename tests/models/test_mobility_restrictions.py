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

from pydantic import ValidationError
import pytest

from datetime import timedelta, datetime

from abmodel.models.mobility_restrictions import time_interval_to_steps
from abmodel.models.mobility_restrictions import random_time_interval_to_steps
from abmodel.models import InterestVariables, MRTStopModes, MRTimeUnits
from abmodel.models import MRTracingPolicies, CyclicMRModes
from abmodel.models import GlobalCyclicMR, CyclicMRPolicies
from abmodel.models import SimpleGroups


class TestClassDisease:
    """
        Verifies the functionality of all class
        in the mobility_restrictions module.
    """
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    # ========================================================================
    # Fixtures
    # ========================================================================

    @pytest.fixture
    def fixture_MRTracingPolicies_error_validation(self) -> tuple[dict]:
        s_g = SimpleGroups(names=["m_group_1", "m_group_2", "m_group_3"])
        kwargs_not_mr_stop_level = {
            "variable": InterestVariables.dead,
            "mr_start_level": 10,
            "mr_stop_mode": MRTStopModes.level_number,
            "mr_groups": s_g,
            "target_groups": ["m_group_2"]
        }
        kwargs_mr_stop_mode_level_number = {
            "variable": InterestVariables.dead,
            "mr_start_level": 10,
            "mr_stop_mode": MRTStopModes.level_number,
            "mr_groups": s_g,
            "target_groups": ["m_group_2"],
            "mr_stop_level": 10,
            "mr_length": 10,
            "mr_length_units": MRTimeUnits.days
        }
        kwargs_not_mr_length = {
            "variable": InterestVariables.dead,
            "mr_start_level": 10,
            "mr_stop_mode": MRTStopModes.length,
            "mr_groups": s_g,
            "target_groups": ["m_group_2"]
        }
        kwargs_not_mr_length_units = {
            "variable": InterestVariables.dead,
            "mr_start_level": 10,
            "mr_stop_mode": MRTStopModes.length,
            "mr_groups": s_g,
            "target_groups": ["m_group_2"],
            "mr_length": 10
        }
        kwargs_mr_stop_level = {
            "variable": InterestVariables.dead,
            "mr_start_level": 10,
            "mr_stop_mode": MRTStopModes.length,
            "mr_groups": s_g,
            "mr_stop_level": 10,
            "target_groups": ["m_group_2"],
            "mr_length": 10,
            "mr_length_units": MRTimeUnits.days
        }
        kwargs_target_groups_not_in_mr_groups_in = {
            "variable": InterestVariables.dead,
            "mr_start_level": 10,
            "mr_stop_mode": MRTStopModes.length,
            "mr_groups": s_g,
            "target_groups": ["m_group_10"],
            "mr_length": 10,
            "mr_length_units": MRTimeUnits.days
        }
        set_up_tuple = (
            kwargs_not_mr_stop_level,
            kwargs_mr_stop_mode_level_number,
            kwargs_not_mr_length,
            kwargs_not_mr_length_units,
            kwargs_mr_stop_level,
            kwargs_target_groups_not_in_mr_groups_in
        )

        return set_up_tuple

    @pytest.fixture
    def fixture_MRTracingPolicies_level_number(self) -> dict:
        s_g = SimpleGroups(names=["m_group_1", "m_group_2", "m_group_3"])
        kwargs = {
            "variable": InterestVariables.diagnosed,
            "mr_start_level": 10,
            "mr_stop_mode": MRTStopModes.level_number,
            "mr_groups": s_g,
            "target_groups": ["m_group_2"],
            "mr_stop_level": 30
        }
        return kwargs

    @pytest.fixture
    def fixture_MRTracingPolicies_length(self) -> dict:
        s_g = SimpleGroups(names=["m_group_1", "m_group_2", "m_group_3"])
        kwargs = {
            "variable": InterestVariables.diagnosed,
            "mr_start_level": 10,
            "mr_stop_mode": MRTStopModes.length,
            "mr_groups": s_g,
            "target_groups": ["m_group_2"],
            "mr_length": 2,
            "mr_length_units": MRTimeUnits.weeks
        }
        return kwargs

    @pytest.fixture
    def fixture_GlobalCyclicMR_error_validation(self) -> tuple[dict]:
        kwargs_unrestricted_time_mode_random = {
            "enabled": True,
            "grace_time": datetime.now(),
            "global_mr_length": 10,
            "global_mr_length_units": MRTimeUnits.days,
            "unrestricted_time_mode": CyclicMRModes.random,
            "unrestricted_time_units": MRTimeUnits.days,
            "unrestricted_time": 5
        }
        kwargs_not_unrestricted_time = {
            "enabled": True,
            "grace_time": datetime.now(),
            "global_mr_length": 10,
            "global_mr_length_units": MRTimeUnits.days,
            "unrestricted_time_mode": CyclicMRModes.fixed,
            "unrestricted_time_units": MRTimeUnits.days,
        }
        set_up_tuple = (
            kwargs_unrestricted_time_mode_random,
            kwargs_not_unrestricted_time
        )

        return set_up_tuple

    @pytest.fixture
    def fixture_GlobalCyclicMR_random(self) -> tuple[dict]:
        kwargs_random = {
            "enabled": True,
            "grace_time": datetime.now(),
            "global_mr_length": 10,
            "global_mr_length_units": MRTimeUnits.days,
            "unrestricted_time_mode": CyclicMRModes.random,
            "unrestricted_time_units": MRTimeUnits.days
        }
        kwargs_fixed = {
            "enabled": True,
            "grace_time": datetime.now(),
            "global_mr_length": 10,
            "global_mr_length_units": MRTimeUnits.days,
            "unrestricted_time_mode": CyclicMRModes.fixed,
            "unrestricted_time_units": MRTimeUnits.days,
            "unrestricted_time": 1
        }
        kwargs = (kwargs_random, kwargs_fixed)

        return kwargs

    @pytest.fixture
    def fixture_CyclicMRPolicies(self) -> tuple[dict]:
        s_g = SimpleGroups(names=["m_group_1", "m_group_2", "m_group_3"])
        kwargs = {
            "mr_groups": s_g,
            "target_group": "m_group_2",
            "delay": 1,
            "delay_units": MRTimeUnits.weeks,
            "mr_length": 5,
            "mr_length_units": MRTimeUnits.months,
            "time_without_restrictions": 3,
            "time_without_restrictions_units": MRTimeUnits.months
        }
        return kwargs
    # ========================================================================
    # Tests
    # ========================================================================

    @pytest.mark.parametrize(
        "mr_length, mr_length_units, iteration_time, steps",
        [
            (10, MRTimeUnits.days, timedelta(days=1), 10),
            (7, MRTimeUnits.weeks, timedelta(days=1), 49),
            (1, MRTimeUnits.months, timedelta(weeks=1), 4.285714285714286)
        ],
        ids=["days", "weeks", "months"]
    )
    def test_time_interval_to_steps(
        self,
        mr_length,
        mr_length_units,
        iteration_time,
        steps
    ):
        """
            Verifies whether MRTimeUnits class
            enumerates correctly the time units.
        """

        expected_steps = time_interval_to_steps(
            mr_length,
            mr_length_units,
            iteration_time
        )

        assert expected_steps == steps

    @pytest.mark.parametrize(
        "mr_length, mr_length_units, iteration_time",
        [
            (90, MRTimeUnits.days, timedelta(days=1)),
            (15, MRTimeUnits.weeks, timedelta(days=1)),
            (2, MRTimeUnits.months, timedelta(days=1))
        ],
        ids=["days", "weeks", "months"]
    )
    def test_random_time_interval_to_steps(
        self,
        mr_length,
        mr_length_units,
        iteration_time,
    ):
        """
            Verifies whether MRTimeUnits class
            enumerates correctly the time units.
        """

        expected_steps = random_time_interval_to_steps(
            mr_length,
            mr_length_units,
            iteration_time
        )
        if mr_length_units == MRTimeUnits.days:
            assert expected_steps <= mr_length and expected_steps >= 1
        if mr_length_units == MRTimeUnits.weeks:
            assert expected_steps <= 7*mr_length and expected_steps >= 1
        if mr_length_units == MRTimeUnits.months:
            assert expected_steps <= 30*mr_length and expected_steps >= 1

    def test_InterestVariables(self):
        """
            Verifies whether InterestVariables class
            enumerates correctly the variables of interest.
        """
        variables_list = [
            "dead_by_disease",
            "diagnosed",
            "ICU_capacity",
            "hospital_capacity"
        ]

        for intereste_variable, variable in zip(
            InterestVariables,
            variables_list
        ):
            assert intereste_variable.value == variable

    def test_MRTStopModes(self):
        """
            Verifies whether MRTStopModes class
            enumerates correctly the stop modes.
        """
        variables_list = [
            "level_number",
            "length"
        ]

        for mrt_stop_mode, variable in zip(
            MRTStopModes,
            variables_list
        ):
            assert mrt_stop_mode.value == variable

    def test_MRTimeUnits(self):
        """
            Verifies whether MRTimeUnits class
            enumerates correctly the time units.
        """
        variables_list = [
            "days",
            "weeks",
            "months"
        ]

        for mr_time_unit, variable in zip(
            MRTimeUnits,
            variables_list
        ):
            assert mr_time_unit.value == variable

    def test_MRTracingPolicies_raise_error_mrt_stop_mode_level_number_1(
        self,
        fixture_MRTracingPolicies_error_validation
    ):
        """
            Verifies whether MRTracingPolicies class raises a ValidationError
            when mr_stop_mode is setting as level_number,
            and unrestricted_time attribute is not provided.
        """
        kwargs = fixture_MRTracingPolicies_error_validation[0]

        with pytest.raises(
            ValidationError,
            match="A valid value for `mr_stop_level` was expected"
        ):
            MRTracingPolicies(**kwargs)

    def test_MRTracingPolicies_raise_error_mrt_stop_mode_level_number_2(
        self,
        fixture_MRTracingPolicies_error_validation
    ):
        """
            Verifies whether MRTracingPolicies class raises a ValidationError
            when mr_stop_mode is setting as level_number,
            and mr_length & mr_length_units attribute is provided.
        """
        kwargs = fixture_MRTracingPolicies_error_validation[1]

        with pytest.raises(
            ValidationError,
            match=(f"`mr_stop_mode` was set to\n\
                        `{MRTStopModes.level_number}`.\n\
                        So, `mr_length` and `mr_length_units`\n\
                        should not be provided.")
        ):
            MRTracingPolicies(**kwargs)

    def test_MRTracingPolicies_raise_error_mrt_stop_mode_level_length_1(
        self,
        fixture_MRTracingPolicies_error_validation
    ):
        """
            Verifies whether MRTracingPolicies class raises a ValidationError
            when mr_stop_mode is setting as length,
            and mr_length is not provided.
        """
        kwargs = fixture_MRTracingPolicies_error_validation[2]

        with pytest.raises(
            ValidationError,
            match="A valid value for `mr_length` was expected"
        ):
            MRTracingPolicies(**kwargs)

    def test_MRTracingPolicies_raise_error_mrt_stop_mode_level_length_2(
        self,
        fixture_MRTracingPolicies_error_validation
    ):
        """
            Verifies whether MRTracingPolicies class raises a ValidationError
            when mr_stop_mode is setting as length,
            and mr_length_units attribute is not provided.
        """
        kwargs = fixture_MRTracingPolicies_error_validation[3]

        with pytest.raises(
            ValidationError,
            match="A valid value for `mr_length_units` was expected"
        ):
            MRTracingPolicies(**kwargs)

    def test_MRTracingPolicies_raise_error_mrt_stop_mode_level_length_3(
        self,
        fixture_MRTracingPolicies_error_validation
    ):
        """
            Verifies whether MRTracingPolicies class raises a
            ValidationError when mr_stop_mode is setting as length,
            and mr_stop_level is provided.
        """
        kwargs = fixture_MRTracingPolicies_error_validation[4]

        with pytest.raises(
            ValidationError,
            match=(f"`mr_stop_mode` was set to\n\
                        `{MRTStopModes.length}`.\n\
                        So, `mr_stop_level` should not be provided.")
        ):
            MRTracingPolicies(**kwargs)

    def test_MRTracingPolicies_raise_error_mr_groups(
        self,
        fixture_MRTracingPolicies_error_validation
    ):
        """
            Verifies whether MRTracingPolicies class raises a
            ValidationError when target_groups are not in mr_groups.
        """
        kwargs = fixture_MRTracingPolicies_error_validation[5]

        with pytest.raises(
            ValidationError,
            match=("All `target_groups` must be in")
        ):
            MRTracingPolicies(**kwargs)

    def test_MRTracingPolicies_level_number(
        self,
        fixture_MRTracingPolicies_level_number
    ):
        """
            Verifies whether MRTracingPolicies assigns correctly each initial
            attribute when mr_stop_mode is setted as level_number.
        """
        kwargs = fixture_MRTracingPolicies_level_number

        tracing_policies = MRTracingPolicies(**kwargs)

        for k, v in zip(kwargs.keys(), kwargs.values()):
            assert getattr(tracing_policies, k) == v

    def test_MRTracingPolicies_length(
        self,
        fixture_MRTracingPolicies_length
    ):
        """
            Verifies whether MRTracingPolicies assigns correctly each initial
            attributte passed and assigns a rigth value to mr_length_in_steps
            when mr_stop_mode is setted as length.
        """
        kwargs = fixture_MRTracingPolicies_length

        tracing_policies = MRTracingPolicies(**kwargs)
        tracing_policies.set_mr_length_in_steps(
            timedelta(days=0.5)
        )

        for k, v in zip(kwargs.keys(), kwargs.values()):
            assert getattr(tracing_policies, k) == v

        assert tracing_policies.mr_length_in_steps == 28

    def test_CyclicMRModes(self):
        """
            Verifies whether InterestVariables class
            enumerates correctly the variables of interest.
        """
        variables_list = [
            "random",
            "fixed"
        ]

        for cyclic_mr_mode, variable in zip(
            CyclicMRModes,
            variables_list
        ):
            assert cyclic_mr_mode.value == variable

    def test_MRTracingPolicies_raise_error_unrestricted_time_mode_random(
        self,
        fixture_GlobalCyclicMR_error_validation
    ):
        """
            Verifies whether MRTracingPolicies class raises a
            ValidationError when unrestricted_time_mode is setting
            to random, and unrestricted_time attribute is provided.
        """
        kwargs = fixture_GlobalCyclicMR_error_validation[0]

        with pytest.raises(
            ValidationError,
            match=f"""
                    `unrestricted_time_mode` was set to
                    `{CyclicMRModes.random}`.
                    So, `unrestricted_time` should not be provided.
                """
        ):
            GlobalCyclicMR(**kwargs)

    def test_MRTracingPolicies_raise_error_unrestricted_time_mode_fixed(
        self,
        fixture_GlobalCyclicMR_error_validation
    ):
        """
            Verifies whether MRTracingPolicies class raises a
            ValidationError when unrestricted_time_mode is setting
            to fixed, and unrestricted_time attribute is not provided.
        """
        kwargs = fixture_GlobalCyclicMR_error_validation[1]

        with pytest.raises(
            ValidationError,
            match=f"""
                    `unrestricted_time_mode` was set to
                    `{CyclicMRModes.fixed}`.
                    So, `unrestricted_time` should be provided.
                """
        ):
            GlobalCyclicMR(**kwargs)

    def test_GlobalCyclicMR_random_1(
        self,
        fixture_GlobalCyclicMR_random
    ):
        """
            Verifies whether MRTracingPolicies assigns correctly each initial
            attributte passed and assigns a rigth value to mr_length_in_steps
            when mr_stop_mode is setted as length.
        """
        kwargs = fixture_GlobalCyclicMR_random[0]

        global_cyclic_mr = GlobalCyclicMR(**kwargs)
        global_cyclic_mr.set_global_mr_length(
            timedelta(days=0.1)
        )

        for k, v in zip(kwargs.keys(), kwargs.values()):
            assert getattr(global_cyclic_mr, k) == v

        assert global_cyclic_mr.global_mr_length_steps == 100

    def test_GlobalCyclicMR_random_2(
        self,
        fixture_GlobalCyclicMR_random
    ):
        """
            Verifies whether GlobalCyclicMR assigns correctly each
            initial attributte passed and assigns a rigth value to
            mr_length_in_steps and unrestricted_time_steps when
            unrestricted_time_mode is setted as random.
        """
        kwargs = fixture_GlobalCyclicMR_random[0]

        global_cyclic_mr = GlobalCyclicMR(**kwargs)
        iteration_time = timedelta(days=0.1)
        global_cyclic_mr.set_global_mr_length(
            iteration_time
        )
        global_cyclic_mr.set_unrestricted_time(
            iteration_time
        )
        mr_length = global_cyclic_mr.global_mr_length_steps
        unrestricted_time = global_cyclic_mr.unrestricted_time_steps

        for k, v in zip(kwargs.keys(), kwargs.values()):
            assert getattr(global_cyclic_mr, k) == v

        assert mr_length == 100
        assert unrestricted_time >= 1 and unrestricted_time <= mr_length

    def test_GlobalCyclicMR_fixed_1(
        self,
        fixture_GlobalCyclicMR_random
    ):
        """
            Verifies whether GlobalCyclicMR assigns correctly each
            initial attributte passed and assigns a rigth value to
            mr_length_in_steps and unrestricted_time_steps when
            unrestricted_time_mode is setted as fixed.
        """
        kwargs = fixture_GlobalCyclicMR_random[1]

        global_cyclic_mr = GlobalCyclicMR(**kwargs)
        iteration_time = timedelta(days=0.1)
        global_cyclic_mr.set_global_mr_length(
            iteration_time
        )
        global_cyclic_mr.set_unrestricted_time(
            iteration_time
        )
        mr_length = global_cyclic_mr.global_mr_length_steps
        unrestricted_time = global_cyclic_mr.unrestricted_time_steps

        for k, v in zip(kwargs.keys(), kwargs.values()):
            assert getattr(global_cyclic_mr, k) == v

        assert mr_length == 100
        assert unrestricted_time == 10

    def test_GlobalCyclicMR_fixed_2(
        self,
        fixture_GlobalCyclicMR_random
    ):
        """
            Verifies whether GlobalCyclicMR sets unrestricted_time_steps
            to None when set_none_unrestricted_time method is calling.
        """
        kwargs = fixture_GlobalCyclicMR_random[1]

        global_cyclic_mr = GlobalCyclicMR(**kwargs)
        global_cyclic_mr.set_none_unrestricted_time()

        assert global_cyclic_mr.unrestricted_time_steps == None

    def test_CyclicMRPolicies(
        self,
        fixture_CyclicMRPolicies
    ):
        """
            Verifies whether GlobalCyclicMR assigns correctly each
            initial attributte passed and assigns a rigth value to
            mr_length_in_steps and unrestricted_time_steps when
            unrestricted_time_mode is setted as fixed.
        """
        kwargs = fixture_CyclicMRPolicies

        cyclic_mr_policies = CyclicMRPolicies(**kwargs)
        iteration_time = timedelta(days=0.2)
        cyclic_mr_policies.set_delay(
            iteration_time
        )
        cyclic_mr_policies.set_mr_length(
            iteration_time
        )
        cyclic_mr_policies.set_time_without_restrictions(
            iteration_time
        )

        for k, v in zip(kwargs.keys(), kwargs.values()):
            assert getattr(cyclic_mr_policies, k) == v

        assert cyclic_mr_policies.delay_in_steps == 35
        assert cyclic_mr_policies.mr_length_in_steps == 750
        assert cyclic_mr_policies.time_without_restrictions_steps == 450
