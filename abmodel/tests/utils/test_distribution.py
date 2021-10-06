import pytest
from numpy import random, ones, abs

from abmodel.utils.distributions import Distribution


class TestDistribution():
    """
        Checks the functionality of the Distribution constructor from
        distribution module.
    """
    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    @pytest.fixture
    def fixture_distributions(self, scope = 'method'):
        pytest.dist_name = 'beta'
        pytest.wrong_name = 'Normall'
        pytest.wrong_type = 'NumPyy'

    @pytest.mark.skip(
        reason="Pydantic decorator does not allows to create a None type"
        "distribution")
    def test_None_distribution(self):
        """
        Creates a None type distribution and assigns the attribute constant
        """
        None_dist = Distribution(dist_type=None)

        assert None_dist.constant == None

    def test_constant_distribution(self):
        """
        Creates a constant distribution and assigns the attribute constant.
        """
        constant_dist = Distribution('constant')
        constant = constant_dist.constant

        assert constant == 0.0

    def test_empirical_distribution(self):
        """
        Raises a SystemError creating an empirical type distribution with a
        wrong filename.
        """
        FileName = 'filename'

        with pytest.raises(SystemError):
            Distribution(dist_type='empirical', filename=FileName)

    def test_weights_distribution(self):
        """
        Raises a SystemError creating a weights type distribution with a
        wrong filename.
        """
        FileName = 'filename'

        with pytest.raises(SystemError):
            assert Distribution(dist_type='weights', filename=FileName)

    def test_numpy_distribution(self, fixture_distributions):
        """
        Creates a numpy distribution and assigns the attribute
        numpy_distribution.
        """
        numpy_dist = Distribution(
            dist_type='numpy', dist_name=pytest.dist_name)
        name = numpy_dist.numpy_distribution.__name__

        assert name == pytest.dist_name

    def test_worong_numpy_name(self, fixture_distributions):
        """
        Raises a SystemError creating a numpy distribution with a wrong
        dist_name.
        """
        with pytest.raises(SystemError):
            assert Distribution(dist_type='numpy', dist_name=pytest.wrong_name)

    def test_wrong_type(self, fixture_distributions):
        """Raises a ValueError when wrong type distribution is passed."""
        with pytest.raises(ValueError):
            assert Distribution(dist_type=pytest.wrong_type)

    def test_sample_constant(self):
        """Returns a constant sample distribution."""
        constant_dist = Distribution(dist_type='constant')
        sample = constant_dist.sample()
        expected = constant_dist.constant*ones(1)

        assert sample == expected

    def test_sample_numpy(self):
        """Returns a numpy sample distribution."""
        numpy_dist = Distribution(
            dist_type='numpy', dist_name='beta', a=1, b=1)
        sample = numpy_dist.sample()
        expected = random.default_rng(seed=numpy_dist.seed).beta(1, 1)

        assert sample == expected

    def test_sample_potivie_constant(self):
        """Returns a constant positive sample distribution."""
        constant_dist = Distribution(dist_type='constant')
        sample = constant_dist.sample_positive()
        expected = constant_dist.constant*ones(1)

        assert sample == expected

    def test_sample_positivie_numpy(self):
        """Returns a numpy positive sample distribution."""
        numpy_dist = Distribution(
            dist_type='numpy', dist_name='normal', loc=-10, scale=0.2)
        sample = numpy_dist.sample_positive()
        expected = abs(
            random.default_rng(seed=numpy_dist.seed).normal(-10, 0.2))

        assert sample == expected
