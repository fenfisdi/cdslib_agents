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

import pytest

from abmodel.models.population import BoxSize


class TestBoxSizeCase:
    """
        Verifies the functionality of the BoxSize namedtuple from population.
    """
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    @pytest.fixture
    def fixture_box_size_instance(self) -> None:
        pytest.test_BoxSize = BoxSize(0, 100, 0, 100)
        pytest.expected = [0, 100, 0, 100]
        pytest.sides = BoxSize._fields

    def test_box_size_instance(self, fixture_box_size_instance):
        """Checks whether all values of the BoxSize are correctly assigned."""
        for side, expected in zip(pytest.sides, pytest.expected):
            test_BoxSize_value = getattr(pytest.test_BoxSize, side)

            assert test_BoxSize_value == expected
