from numpy import full
from numpy.random import choice
from pandas.core.frame import DataFrame

from abmodel.models.base import SimpleGroups


class InitialArrangement:
    """
        TODO: Add brief explanation

        Methods
        -------
        TODO
    """
    @classmethod
    def setup(
        cls,
        df: DataFrame,
        core_var: str,
        nested_vars: list,
        settings: dict
    ) -> DataFrame:
        """
            I take a json-like input, a df contaning `agent` data and
            modify such df with the necessary data inside the json-like input.
            TODO: Improve explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Examples
            --------
            TODO: include some examples
        """
        if not nested_vars:
            # Get values and probabilities
            values = list(settings.keys())
            probabilities = list(settings.values())

            # All values are assigned randomly with the given probabilities
            df[core_var] = choice(a=values, p=probabilities, size=df.shape[0])
        else:
            # Create the new column with assigned value None
            df[core_var] = full(df.shape[0], None)

            # aux_df is going to have all nested_vars values
            aux_df = df[nested_vars].drop_duplicates()

            for _, row in aux_df.iterrows():
                # Retrieve (keys, items) from the row
                row_keys = list(row.keys())
                row_items = row.to_list()

                # Use row_items to get inner_settings dict
                inner_settings = settings
                for item in row_items:
                    inner_settings = inner_settings[item]

                # Get values and probabilities
                values = list(inner_settings.keys())
                probabilities = list(inner_settings.values())

                # Generate condition_list for filtering
                condition_list = [
                    f'(df["{key}"] == "{item}")'
                    for (key, item) in zip(row_keys, row_items)
                    ]

                # Get filtering condition
                _condition = ' & '.join(condition_list)

                # Assign values
                # All values are assigned randomly with the given probabilities
                df.loc[eval(_condition), core_var] = \
                    choice(
                        a=values,
                        p=probabilities,
                        size=df[eval(_condition)].shape[0]
                        )

        return df

    @classmethod
    def fulfill_setup(
        cls,
        df: DataFrame,
        missing_cols: list[str],
        req_cols_dict: dict
    ) -> DataFrame:
        """
            TODO: Add brief explanation

            Parameters
            ----------
            TODO

            Returns
            -------
            TODO

            Examples
            --------
            TODO: include some examples
        """
        for group_col in missing_cols:
            if isinstance(req_cols_dict[group_col], SimpleGroups):
                group_values = req_cols_dict[group_col].names
            else:
                group_values = list(req_cols_dict[group_col].items.keys())

            # Fill group_values randomly
            df[group_col] = choice(
                a=group_values,
                size=df.shape[0]
                )

        return df
