import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame

class InitialPopulation:
    """
        Here I would put my wonderful documentation...
        IF I HAD IT!
    """
    def __init__(self, core_var: str, nested_vars: list):
        self.nesting = nested_vars
        self.core = core_var

    def _filler(self, values, probabilities):
        """
            insert.Docs()
        """
        sample = np.random.random_sample()
        cummulative_probability = 0.

        for value, probability in zip(values, probabilities):
            cummulative_probability += probability

            if sample <= cummulative_probability:
                return value

    def setup(self, settings_json, agents: DataFrame):
        """
            I take a json-like input, a df contaning `agent` data and modify such df
            with the necessary data inside the json-like input.
        """
        for field in self.nesting:
            nested_content = settings_json[field]
            population_df = pd.DataFrame(columns=self.nesting)

            for (col_index, col_name) in enumerate(self.nesting):
                if col_index != 0:
                    row_number = population_df.shape[0]
                    column = eval(f'select.{col_name}s')

                    placeholder = population_df.copy()
                    population_df = pd.DataFrame(columns=self.nesting)

                    for item in column:
                        array = [item for _ in range(row_number)]
                        placeholder[col_name] = array
                        population_df = population_df.append(placeholder, ignore_index=True)
                else:
                    population_df[col_name] = eval(f'self.{col_name}s')

            df_copy = population_df.copy()
            population_df['probability'] = [None for _ in range(population_df.shape[0])]

            for _, row in df_copy.iterrows():
                row_keys = list(row.keys())
                row_items = row.to_list()
                condition_list = [f'population_df["{key}"] == "{item}"'
                        for (key, item) in zip(row_keys, row_items)]

                val = nested_content
                for item in row_items:
                    val = val[item]

                _condition = ' & '.join(condition_list)
                population_df.loc[eval(_condition), 'probability'] = val

            for _, row in df_copy.iterrows():
                row_keys = list(row.keys())
                row_items = row.to_list()

                field = row_keys[:-2]
                filter_fields = row_keys[:-2]
                filter_values = row_items[:-2]

                condition_list = [f'population_df["{key}"] == "{item}"'
                        for (key, item) in zip(filter_fields, filter_values)]

                _condition = ' & '.join(condition_list)

                values = population_df.loc[eval(_condition), field].to_list()
                probabilities = population_df.loc[eval(_condition), 'probability'].to_list()

                condition_list = [f'population_df["{key}"] == "{item}"'
                        for (key, item) in zip(filter_fields, filter_values)]

                _condition = ' & '.join(condition_list)

                agent_list = agents.loc[eval(_condition), 'agent'].to_list()

                for agent_index in agent_list:
                    agents.loc[agents['agent'] == agent_index, field] = self._filler(values, probabilities)

