from pandas.core.frame import DataFrame


def check_column_existance(df: DataFrame, cols: list) -> bool:
    """
        Validate wheter each column exists, if the validation fails,
        raise an error with specific information about the missing columns

        Parameters
        ----------
        df: DataFrame
            Data frame containing the positional information about the agents

        cols: list
            A list containing the columns to validate

        Returns
        -------
        True:
            If the column validation is passed.
    """
    check_cols = []
    if set(cols).issubset(df.columns):
        return True
    else:
        for col in cols:
            if not {col}.issubset(df.columns):
                check_cols.append(col)

        error_string = "df must contain: " + ", ".join(cols) + ".\n"
        check_string = ", ".join(check_cols) + " must be checked"

        raise ValueError(error_string + check_string)


def check_column_errors(df: DataFrame, debug: bool = False):
    """
        Validate if fields inside a column are correctly set, if the validation
        fails, raise an error about incorrect initialization, if debug is
        enabled, the error message contains specific information about the
        DataFrame.

        Parameters
        ----------
        df: DataFrame
            Data frame containing the positional information about the agents

        debug: Boolean
            Flag used to tell if extensive explorations over the DataFrame are
            needed
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
