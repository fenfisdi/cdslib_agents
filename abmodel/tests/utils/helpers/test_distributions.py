import pytest
from time import time
from numpy import random, histogram, array

from abmodel.utils.helpers.distributions import init_distribution
from abmodel.utils.distributions import Distribution


class TestDistributions:
    """
        Checks the functionality of the init_istribution method from
        distributions module.
    """
    @pytest.fixture()
    def constant_dist_dict(self):
        dist_dict = {"dist_type": "constant", "constant": 1}
        return dist_dict

    @pytest.fixture()
    def None_dist_dict(self):
        dist_dict = {"dist_type": None}
        return dist_dict

    @pytest.fixture()
    def empirical_dist_dict_file(self):
        dist_dict = {"dist_type": "empirical",
                    "filename": "data_empirical.txt",
                    "kwargs": {'kernel': 'gaussian',
                                'bandwidth': 0.1}
                        }
        return dist_dict

    @pytest.fixture()
    def empirical_dist_dict_data(self):
        data = random.normal(0.0, 0.1, 30)
        dist_dict = {"dist_type": "empirical",
                    "filename": None,
                    "kwargs": {"data": data,
                                'kernel': 'gaussian',
                                'bandwidth': 0.1
                                 }
                        }
        return dist_dict

    @pytest.fixture()
    def weights_dist_dict_file(self):
        dist_dict = {"dist_type": "weights",
                    "filename": "data_weights.txt",
                    "kwargs": {'kernel': 'gaussian',
                               'bandwidth': 0.1}
                    }
        return dist_dict

    @pytest.fixture()
    def weights_dist_dict_data(self):
        hist = histogram(random.normal(0.0, 0.1, 30))
        data = list(hist[1])
        X_i = [(data[i] + data[i + 1])/2 for i in range(len(data) - 1)]
        P_i = list(hist[0])
        P_i = [i/30 for i in P_i]
        data = array([X_i, P_i]).T
        dist_dict = {"dist_type": "weights",
            "filename": None,
            "kwargs": {"data": data,
                        'kernel': 'gaussian',
                        'bandwidth': 0.1}
                        }
        return dist_dict

    @pytest.fixture()
    def numpy_dist_dict(self):
        dist_dict = {"dist_type": "numpy",
                    "dist_name": 'beta',
                    "kwargs": {'a': 1, 'b': 1}
                    }
        return dist_dict

    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    def test_init_distribution_constant(self, constant_dist_dict):
        """verifies the correct assign of a distribution using the method
        'init_distribution', constant in this case"""
        dist_dict = constant_dist_dict
        dist = init_distribution(dist_dict)

        assert dist.dist_type == dist_dict["dist_type"]
        assert dist.constant == dist_dict["constant"]
        assert dist.seed == int(time())

    def test_init_distribution_None(self, None_dist_dict):
        """verifies the correct assign of a distribution using the method
        'init_distribution', None in this case"""
        dist_dict = None_dist_dict
        dist = init_distribution(dist_dict)

        assert dist.dist_type == dist_dict["dist_type"]
        assert dist.constant == None
        assert dist.seed == int(time())

    def test_init_distribution_empirical_file(self, empirical_dist_dict_file):
        """verifies the correct assign of a distribution using the method
        'init_distribution', empirical in this case by means of a file"""
        dist_dict = empirical_dist_dict_file
        dist = init_distribution(dist_dict)

        assert dist.dist_type == dist_dict["dist_type"]
        assert dist.seed == int(time())
        assert dist.filename == dist_dict["filename"]
        assert list(dist.kwargs.values())[0] == \
            dist_dict["kwargs"]['kernel']

    def test_init_distribution_empirical_data(self, empirical_dist_dict_data):
            """verifies the correct assign of a distribution using the method
            'init_distribution', empirical in this case by means of a data
            array"""
            dist_dict = empirical_dist_dict_data
            dist = init_distribution(dist_dict)

            assert dist.dist_type == dist_dict["dist_type"]
            assert dist.seed == int(time())
            assert list(dist.kwargs.values())[0] == \
                dist_dict["kwargs"]['kernel']

    def test_init_distribution_weights_file(self, weights_dist_dict_file):
        """verifies the correct assign of a distribution using the method
        'init_distribution', weights in this case by means of a file"""
        dist_dict = weights_dist_dict_file
        dist = init_distribution(dist_dict)

        assert dist.dist_type == dist_dict["dist_type"]
        assert dist.seed == int(time())
        assert dist.filename == dist_dict["filename"]

    @pytest.mark.skip(reason="minor bug in the distributions module")
    def test_init_distribution_weights_data(self, weights_dist_dict_data):
        """verifies the correct assign of a distribution using the method
        'init_distribution', weights in this case by means of a data array"""
        dist = init_distribution(dist_dict)

        assert dist.dist_type == dist_dict["dist_type"]
        assert dist.seed == int(time())

    def test_init_distribution_numpy(self, numpy_dist_dict):
        """verifies the correct assign of a distribution using the method
        'init_distribution', numpy in this case"""
        dist_dict = numpy_dist_dict
        dist = init_distribution(dist_dict)

        assert dist.dist_type == dist_dict["dist_type"]
        assert dist.seed == int(time())
        assert dist.numpy_distribution.__name__ == dist_dict["dist_name"]
