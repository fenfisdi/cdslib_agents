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

from typing import Callable

from pandas.core.frame import DataFrame
from pandas import concat

from abmodel.utils import ExecutionModes


class Aggregator:
    """
        TODO: Add brief explanation

        Attributes
        ----------
        TODO

        Methods
        -------
        TODO
    """
    def __init__(
        self,
        col_name: str,
        col_values: list,
        read_method: Callable,
        prefix: str = "sim_",
        execmode: ExecutionModes = ExecutionModes.iterative.value
    ) -> None:
        """
            Constructor of Population class.

            TODO: Add brief explanation

            Parameters
            ----------
            TODO
        """
        # Store configuration
        self.col_name = col_name
        self.col_values = col_values
        self.read_method = read_method
        self.prefix = prefix
        self.execmode = execmode

    def __step_count_func(
        self,
        df: DataFrame,
        simulation_number: int,
    ) -> DataFrame:
        """
            TODO
        """
        grouped_df = df[[self.col_name, "agent"]] \
            .groupby(self.col_name) \
            .count().rename(
                columns={"agent": "_".join([self.prefix, simulation_number])}
            )

        grouped_df = grouped_df.reindex(self.col_values, fill_value=0)

        return grouped_df

    def aggregation_by_step(
        self,
        total_steps: int,
        filepaths_dict: dict
    ) -> DataFrame:
        """
            TODO
        """
        # For storing all aggregated df (one by step)
        all_steps_df = []

        for step in range(total_steps):

            filepaths = filepaths_dict[step]

            df_list = [self.read_method(filepath) for filepath in filepaths]

            # datetime = df_list[0]["datetime"][0]

            # df_list = [
            #     self.__step_count_func(df=df, simulation_number=i)
            #     for i, df in enumerate(df_list)
            #     ]

            df_list = [
                self.__count_func(df=df, simulation_number=i)
                for i, df in enumerate(df_list)
                ]

            df = concat(df_list, axis=1)

            # df = df.assign(step=step)
            # df = df.assign(datetime=datetime)

            # df.reset_index(inplace=True)

            all_steps_df.append(df)

        df = concat(all_steps_df)

        df = df.set_index(["step", "datetime", self.col_name])

        df.insert(0, "mean", df.mean(axis=1))
        df.insert(1, "std", df.std(axis=1))
        df.insert(2, "min", df.min(axis=1))
        df.insert(3, "max", df.max(axis=1))

        df.reset_index(inplace=True)

        return df

    def __count_func(
        self,
        df: DataFrame,
        simulation_number: int,
    ) -> DataFrame:
        """
            TODO
        """
        index_cols = ["step", "datetime"]
        cols = index_cols + [self.col_name]
        target = "agent"
        label = "_".join([self.prefix, simulation_number])

        partial_df = df[cols + [target]] \
            .groupby(cols) \
            .count().rename(
                columns={target: label}
            ).reset_index()

        agg_df = partial_df.groupby(index_cols).apply(
            lambda grouped_df: grouped_df[[self.col_name, label]]
            .set_index(self.col_name)
            .reindex(self.col_values, fill_value=0)
            .reset_index()
            ).reset_index()[cols + [label]]

        return agg_df

    def aggregation_of_cumulatives(
        self,
        filepaths: list
    ) -> DataFrame:
        """
            TODO
        """
        df_list = [self.read_method(filepath) for filepath in filepaths]

        df_list = [
            self.__count_func(df=df, simulation_number=i)
            for i, df in enumerate(df_list)
            ]

        df = concat(df_list)

        df = df.set_index(["step", "datetime", self.col_name])

        df.insert(0, "mean", df.mean(axis=1))
        df.insert(1, "std", df.std(axis=1))
        df.insert(2, "min", df.min(axis=1))
        df.insert(3, "max", df.max(axis=1))

        df.reset_index(inplace=True)

        return df
