import pytest
import re
import numpy as np

from abmodel.utils.distributions import Distribution



class TestDistribution():

    """
        Check the functionality of constructor Distribution from distribution module,
        using unitary test with the Python testing tool pytest.
    """

    def setup_method(self, method):
        print('==>')
        print(method.__doc__)

    @pytest.fixture
    def fixture_distributions(self, scope = 'method'):
        pytest.dist_name = 'beta'
        pytest.wrong_name = 'Normall'
        pytest.wrong_type = 'NumPyy'


    @pytest.mark.skip(reason="Pydantic decorator does not allow create None distribution")
    def test_None_distribution(self):
        """Create a None type distributions and assing the atributte constant"""

        None_dist = Distribution(dist_type = None)

        assert None_dist.constant == None


    def test_constant_distribution(self):
        """Create a constant distribution and assing the atributte constant"""

        constant_dist = Distribution('constant')
        constant = constant_dist.constant

        assert constant == 0.0


    def test_empirical_distribution(self):
        """Raising SystemError creating an empirical type distributions with a wrong filename"""

        FileName = 'filename'

        with pytest.raises(SystemError):
            Distribution(dist_type = 'empirical', filename = FileName)


    def test_weights_distribution(self):
        """Raising SystemError creating an empirical type distributions with a wrong filename"""

        FileName = 'filename'

        with pytest.raises(SystemError):
            assert Distribution(dist_type = 'empirical', filename = FileName)

    def test_numpy_distribution(self, fixture_distributions):
        """Create a numpy distributions and assing the atributte numpy_distribution"""

        numpy_dist = \
        Distribution(dist_type = 'numpy', dist_name = pytest.dist_name)
        name = numpy_dist.numpy_distribution.__name__

        assert name == pytest.dist_name


    def test_worong_numpy_name(self, fixture_distributions):
        """SystemError creating a numpy distribution with a wrong dist_name"""

        with pytest.raises(SystemError):
            assert Distribution(dist_type = 'numpy', dist_name = pytest.wrong_name)


    def test_wrong_type(self, fixture_distributions):
        """Raising ValueError Wrong type distribution."""

        with pytest.raises(ValueError):
            assert Distribution(dist_type = pytest.wrong_type)

    def test_sample_constant(self):
        """Return a constant sample distribution."""

        constant_dist = \
        Distribution(dist_type = 'constant')
        sample = constant_dist.sample()
        expected = constant_dist.constant*np.ones(1)

        assert sample == expected


    def test_sample_numpy(self):
        """Return a numpy sample distribution."""

        numpy_dist = \
        Distribution(dist_type = 'numpy', dist_name = 'beta', a = 1, b = 1)
        sample = numpy_dist.sample()
        expected = np.random.default_rng(seed=numpy_dist.seed).beta(1, 1)

        assert sample == expected


    def test_sample_potivie_constant(self):
        """Return a constant positive sample distribution."""

        constant_dist = \
        Distribution(dist_type = 'constant')
        sample = constant_dist.sample_positive()
        expected = constant_dist.constant*np.ones(1)

        assert sample == expected

    def test_sample_positivie_numpy(self):
        """Return a numpy positive sample distribution."""

        numpy_dist = \
        Distribution(dist_type = 'numpy', dist_name = 'normal', loc = -10, scale = 0.2)
        sample = numpy_dist.sample_positive()
        expected = np.abs(np.random.default_rng(seed=numpy_dist.seed).normal(-10, 0.2))

        assert sample == expected
