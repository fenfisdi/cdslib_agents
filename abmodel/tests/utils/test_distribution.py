from unittest import TestCase

from abmodel.utils.distributions import Distribution


class DistributionTest(TestCase):

    def setUp(self) -> None:
        self.distribution_wrong_type = "EmpIrIcAAAL"

        self.distribution_type_numpy = "numpy"
        self.numpy_distribution = "thing that looks like a ghost"

        self.distribution_type = "empirical"
        self.wrong_file_path = "/hello/world"

    def test_wrong_type(self):
        with self.assertRaises(ValueError):
            Distribution(dist_type = self.distribution_wrong_type)

    def test_numpy_distributions(self):
        with self.assertRaises(ValueError):
            Distribution(dist_type = self.distribution_type_numpy,
                         distribution = self.numpy_distribution)

    def test_wront_path(self):
        with self.assertRaises(ValueError):
            Distribution(dist_type = self.distribution_type,
                         filename = self.wrong_file_path)
