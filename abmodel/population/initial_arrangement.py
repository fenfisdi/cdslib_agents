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

from numpy import full
from numpy.random import choice
from pandas.core.frame import DataFrame

from abmodel.models import SimpleGroups


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
            if req_cols_dict[group_col] is not None:
                if isinstance(req_cols_dict[group_col], SimpleGroups):
                    group_values = req_cols_dict[group_col].names
                else:
                    group_values = list(req_cols_dict[group_col].items.keys())

                # Fill group_values randomly
                df[group_col] = choice(
                    a=group_values,
                    size=df.shape[0]
                    )
            else:
                # req_cols_dict[group_col] is None

                # Fill group_values with None
                df[group_col] = None

        return df
