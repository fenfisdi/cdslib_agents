from unittest import TestCase

import numpy as np
import pandas as pd

from abmodel.utils.utilities import check_column_errors, check_column_existance


class ColumnErrorsTestCase(TestCase):

    def setUp(self) -> None:
        data = {'vx': [np.nan, 10, 20],
                'vy': [2, 2, 2]}

        self.df = pd.DataFrame(data)

    def test_column_errors(self):
        with self.assertRaises(ValueError):
            check_column_errors(self.df)

    def test_column_existance(self):
        with self.assertRaises(ValueError):
            check_column_existance(self.df, ['x', 'vx', 'vy'])
