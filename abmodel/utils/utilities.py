from typing import Union

from pydantic import validate_arguments
from pandas.core.frame import DataFrame
from pandas.core.series import Series


def check_field_existance(df: DataFrame, cols: list) -> str:
    """
        Validate wheter each column exists, if the validation fails,
        raise an error with specific information about the missing columns

        Parameters
        ----------
        df : DataFrame
            Data frame containing the positional information about the agents

        cols : list
            A list containing the columns to validate

        Returns
        -------
        True:
            If the column validation is passed.

        Raises
        ------
        ValueError
            If at least one of the columns to validate is missing.

        Examples
        --------
        TODO: include some examples
    """
    check_cols = []
    if set(cols).issubset(df.columns):
        return ""
    else:
        for col in cols:
            if not {col}.issubset(df.columns):
                check_cols.append(col)

        error_string = "df must contain: " + ", ".join(cols) + ".\n"
        check_string = ", ".join(check_cols) + " must be checked"

        raise ValueError(error_string + check_string)


def exception_burner(errors: list[str]) -> Exception:
    """
        Concatenates all error messages and raises one Exception containing all

        Parameters
        ----------
        errors : list
            List of error messages

        Raises
        ------
        Exception
            Concatenating all errors

        Examples
        --------
        TODO: include some examples
    """
    raise Exception("\n".join(errors))


def check_field_errors(df: DataFrame, debug: bool = False):
    """
        Validate if fields inside a column are correctly set, if the validation
        fails, raise an error about incorrect initialization, if debug is
        enabled, the error message contains specific information about the
        DataFrame.

        Parameters
        ----------
        df : DataFrame
            Dataframe containing the positional information about the agents

        debug : Boolean, optional
            Flag used to tell if extensive explorations over the DataFrame are
            needed

        Raises
        ------
        ValueError
            If the dataframe contains some any column with null values

        Examples
        --------
        TODO: include some examples
    """
    if df.isna().values.any():
        if debug:
            erratic_df = df[df.isna().any(axis=1)]
            error_string = "The following columns contain Null values:\n"
            error_string += ", ".join(list(erratic_df.columns))
            raise ValueError(error_string)
        else:
            error_string = (
                    "Some columns might be initialized incorrectly.\n"
                    "To pinpoint especific errors, "
                    "add `debug=True` as a parameter")
            raise ValueError(error_string)


@validate_arguments(config={"arbitrary_types_allowed": True})
def std_str_join_cols(
    col1: Union[str, Series],
    col2: Union[str, Series],
    separator: str = "-"
) -> Union[str, list[str]]:
    """
        Joins the input strings with the given separator in only one string.
        If the inputs are series, it concatenates vertically the series.

        Parameters
        ----------
        col1 : Union[str, Series]
            Input string 1. Can be a str or a series of strings
        
        col2 : Union[str, Series]
            Input string 2. Can be a str or a series of strings
        
        separator : str, default = "-"
            Separator of the joined strings or series

        Returns
        -------
        join_str : Union[str, list[str]
            Joined strings or concatenated series

        Raises
        ------
        ValueError
            If the input types are not the same or different
            from string or series.
            Must be both strings or both a serie of strings.

        Examples
        --------
        TODO: include some examples
    """
    if type(col1) == str and type(col2) == str:
        return separator.join([col1, col2])
    elif type(col1) == Series and type(col2) == Series:
        return col1.astype(str) + separator + col2.astype(str)
    else:
        error_string = (
                "`col1` or `col2` might be provided incorrectly.\n"
                "Both `col1` and `col2` should have the same type"
                "corresponding to `str` or `pandas Series`")
        raise ValueError(error_string)
