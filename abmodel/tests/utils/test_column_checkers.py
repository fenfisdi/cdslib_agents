import pytest
from numpy import nan
from pandas import DataFrame

from abmodel.utils.utilities import check_field_errors, check_field_existance


class TestCaseFieldExistenceAndErrors:
    """
        Verifies the functionality of the methods check_field_existance and
        check_field_errors from utilities.
    """
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    @pytest.fixture
    def fixture_field_existence(self, scope = 'class') -> None:
        data = {'vx': [0, 10, 20],
                'vy': [2, 2, 2]}
        pytest.df = DataFrame(data)
        pytest.cols_in = ['vx', 'vy']
        pytest.cols_is_not_in = ['x', 'y']
        error_string = "df must contain: " + ", ".join(pytest.cols_is_not_in)
        check_string = \
            ".\n" + ", ".join(pytest.cols_is_not_in) + " must be checked"
        pytest.expected_ouput_cols_is_not_in = error_string + check_string

    @pytest.fixture
    def fixture_field_errors(self, scope='class') -> None:
        data = {'vx': [nan, 1, 2],
                'vy': [0, 1, 2]}
        pytest.df = DataFrame(data)
        error_string = "The following columns contain Null values:\n"
        erratic_df = pytest.df[pytest.df.isna().any(axis=1)]
        error_string += ", ".join(list(erratic_df.columns))
        pytest.expected_string_na_values = error_string
        pytest.expected_string_debug_False = (
            "Some columns might be initialized incorrectly.\nTo pinpoint"
            " especific errors, add `debug=True` as a parameter")

    def test_field_existence_cols_in(self, fixture_field_existence):
        """The List passed contains columns belonging to the DataFrame."""
        assert check_field_existance(pytest.df, pytest.cols_in) == True

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
                    ValueError, match=pytest.expected_ouput_cols_is_not_in):
            assert check_field_existance(pytest.df, pytest.cols_is_not_in)

    def test_field_errors_na_values_debug_True(self, fixture_field_errors):
        """
        Verify whether the output ValueError string corresponds to the expected
        for Null values ==> debug True.
        """
        with pytest.raises(ValueError, match=pytest.expected_string_na_values):
            assert check_field_errors(pytest.df, True)

    def test_field_error_na_values_debug_False(self, fixture_field_errors):
        """
        Verify whether the output ValueError string corresponds to the expected
        for Null values ==> debug False.
        """
        with pytest.raises(ValueError, match=pytest.expected_string_debug_False):
            assert check_field_errors(pytest.df)
