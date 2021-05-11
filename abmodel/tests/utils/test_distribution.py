from unittest import TestCase

from abmodel.utils.distributions import Distribution


class DistributionTest(TestCase):

    def setUp(self) -> None:
        self.distribution_wrong_type = Distribution(dist_type = "EmpIrIcAAAL")
        self.distribution_empirical_type = Distribution(dist_type = "empirical")

    def test_distribution_error(self):
        with self.assertRaises(ValueError):
            self.distribution_wrong_type.sample_positive()

    def test_incomplete_distribution(self):
        with self.assertRaises(ValueError):
            self.distribution_empirical_type.sample()
