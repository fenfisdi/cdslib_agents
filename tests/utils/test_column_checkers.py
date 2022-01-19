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

import pytest
from numpy import nan, all
from pandas import DataFrame, Series

from abmodel.utils.utilities import check_field_errors
from abmodel.utils.utilities import check_field_existance, std_str_join_cols


class TestCaseFieldExistenceAndErrors:
    """
        Verifies the functionality of the methods check_field_existance and
        check_field_errors from utilities.
    """
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    @pytest.fixture
    def fixture_field_existence(self) -> None:
        data = {
            "vx": [0, 10, 20],
            "vy": [2, 2, 2]
        }
        pytest.df = DataFrame(data)
        pytest.cols_in = ["vx", "vy"]
        pytest.cols_is_not_in = ["x", "y"]
        error_string = "df must contain: " + ", ".join(pytest.cols_is_not_in)
        check_string = \
            ".\n" + ", ".join(pytest.cols_is_not_in) + " must be checked"
        pytest.expected_ouput_cols_is_not_in = error_string + check_string

    @pytest.fixture
    def fixture_field_errors(self) -> None:
        data = {
            "vx": [nan, 1, 2],
            "vy": [0, 1, 2]
        }
        pytest.df = DataFrame(data)
        error_string = "The following columns contain Null values:\n"
        erratic_df = pytest.df[pytest.df.isna().any(axis=1)]
        error_string += ", ".join(list(erratic_df.columns))
        pytest.expected_string_na_values = error_string
        pytest.expected_string_debug_False = (
            "Some columns might be initialized incorrectly.\nTo pinpoint"
            " especific errors, add `debug=True` as a parameter"
        )

    @pytest.fixture
    def fixture_std_str_join_cols(self) -> None:
        data = {
            "vulnerability_group": [
                "not_vulnerable",
                "vulnerable"
            ],
            "disease_group": [
                "immune",
                "susceptible"
                ]
        }
        expected = [
            vul + '-' + dis for (vul, dis) in zip(
                data["vulnerability_group"], data["disease_group"]
                )
        ]
        error_string = (
                "`col1` or `col2` might be provided incorrectly.\n"
                "Both `col1` and `col2` should have the same type"
                "corresponding to `str` or `pandas Series`"
        )
        return data, expected, error_string

    def test_field_existence_cols_in(self, fixture_field_existence):
        """The List passed contains columns belonging to the DataFrame."""
        assert check_field_existance(pytest.df, pytest.cols_in) == ""

    def test_field_existence_cols_is_not_in(self, fixture_field_existence):
        """
        Raises a ValueError when the list containing columns do not belong to
        the DataFrame.
        """
        with pytest.raises(ValueError):
            assert check_field_existance(pytest.df, pytest.cols_is_not_in)

    def test_field_existence_output_string(self, fixture_field_existence):
        """
        Raises a ValueError when the columns input list is not in the
        DataFrame.
        """
        with pytest.raises(
            ValueError,
            match=pytest.expected_ouput_cols_is_not_in
        ):
            assert check_field_existance(pytest.df, pytest.cols_is_not_in)

    def test_field_errors_na_values_debug_True(self, fixture_field_errors):
        """
        Verifies whether the output ValueError string corresponds to the
        expected for Null values ==> debug True.
        """
        with pytest.raises(ValueError, match=pytest.expected_string_na_values):
            assert check_field_errors(pytest.df, True)

    def test_field_error_na_values_debug_False(self, fixture_field_errors):
        """
        Verifies whether the output ValueError string corresponds to the
        expected for Null values ==> debug False.
        """
        with pytest.raises(
            ValueError,
            match=pytest.expected_string_debug_False
        ):
            assert check_field_errors(pytest.df)

    def test_std_str_join_cols_str(self, fixture_std_str_join_cols):
        """
        Verifies whether the output ValueError string corresponds to the
        expected for Null values ==> debug False.
        """
        output_str = std_str_join_cols(
            "not_vulnerable",
            "immune",
        )
        expected = "not_vulnerable-immune"

        assert expected == output_str

    def test_std_str_join_cols_Series(self, fixture_std_str_join_cols):
        """
        Verifies whether the output ValueError string corresponds to the
        expected.
        """
        S1 = Series(fixture_std_str_join_cols[0]["vulnerability_group"])
        S2 = Series(fixture_std_str_join_cols[0]["disease_group"])

        output_list = std_str_join_cols(
            S1,
            S2,
            )
        expected = fixture_std_str_join_cols[1]

        assert all(expected == output_list)

    def test_std_str_join_cols_raise_error(self, fixture_std_str_join_cols):
        """
        Verifies whether the output ValueError string corresponds to the
        expected.
        """
        S1 = Series(fixture_std_str_join_cols[0]["vulnerability_group"])

        with pytest.raises(
            ValueError,
            match=fixture_std_str_join_cols[2]
        ):
            assert std_str_join_cols(S1, "immune")
