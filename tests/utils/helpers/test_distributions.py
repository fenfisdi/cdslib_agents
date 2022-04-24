import pytest

from numpy import random, histogram, array

from abmodel.utils.helpers import init_distribution


class TestDistribution:
    """
        Checks the functionality of the init_distribution function from
        distribution module.
    """
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    @pytest.fixture
    def fixture_constant_distribution(self) -> dict:
        dist_dict = {
            "dist_type": "constant",
            "constant": 2.9
        }
        return dist_dict

    @pytest.fixture
    def fixture_empirical_distribution(self) -> dict:
        data = random.normal(0.0, 0.1, 30)
        dist_dict = {
            "dist_type": "empirical",
            "data": data,
            "filename": None,
            "kwargs": {
                "kernel": "gaussian",
                "bandwidth": 0.1
            }
        }
        return dist_dict

    @pytest.fixture
    def fixture_weights_distribution(self) -> dict:
        hist = histogram(random.normal(0.0, 0.1, 30))
        data = list(hist[1])
        X_i = [(data[i] + data[i + 1])/2 for i in range(len(data) - 1)]
        P_i = list(hist[0])
        P_i = [i/30 for i in P_i]
        data = array([X_i, P_i]).T

        dist_dict = {
            "dist_type": "weights",
            "data": data,
            "filename": None,
        }
        return dist_dict

    @pytest.fixture
    def fixture_numpy_distribution(self) -> dict:
        dist_dict = {
            "dist_type": "numpy",
            "dist_name": "beta",
            "kwargs": {
                "a": 1,
                "b": 1
            }
        }
        return dist_dict

    @pytest.fixture
    def fixture_none_distribution(self) -> dict:
        dist_dict = {
            "dist_type": None
        }
        return dist_dict

    def test_constant_distribution(self, fixture_constant_distribution):
        """
            verifies whether create a constant distribution, assigns correct
            value to the constant.
        """
        dist_dict = fixture_constant_distribution

        constant_dist = init_distribution(dist_dict)

        assert constant_dist.dist_type == "constant"
        assert constant_dist.constant == 2.9

    def test_empirical_distribution(self, fixture_empirical_distribution):
        """
            verifies whether creates an empirical type distribution correctly.
        """

        dist_dict = fixture_empirical_distribution

        empirical_dist = init_distribution(dist_dict)

        assert empirical_dist.dist_type == "empirical"

    def test_weights_distribution(self, fixture_weights_distribution):
        """
            verifies whether creates a weights type distribution correctly.
        """

        dist_dict = fixture_weights_distribution

        weights_dist = init_distribution(dist_dict)

        assert weights_dist.dist_type == "weights"

    def test_numpy_distribution(self, fixture_numpy_distribution):
        """
            verifies whether creates a numpy distribution correctly.
        """

        dist_dict = fixture_numpy_distribution

        numpy_dist = init_distribution(dist_dict)

        assert numpy_dist.dist_type == "numpy"

    def test_none_distribution(self, fixture_none_distribution):
        """
            verifies whether creates a numpy distribution correctly.
        """

        dist_dict = fixture_none_distribution

        none_dist = init_distribution(dist_dict)

        assert none_dist.dist_type == None
        assert none_dist.constant == None
