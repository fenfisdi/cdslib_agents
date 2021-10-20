import pytest
from numpy import random, ones, abs, array, histogram, genfromtxt, full
from time import time
from sklearn.neighbors import KernelDensity

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

    @pytest.fixture
    def fixture_constant_distribution(self):
        pytest.constant = 10
        pytest.error_message = "Error initializing distribution."

    @pytest.fixture
    def fixture_empirical_distribution(self):
        pytest.error_message = "Error initializing distribution."
        pytest.data_1D = random.normal(0.0, 0.1, 30)
        pytest.data_3D = random.normal(0.0, 0.1, (1, 3))
        pytest.wrong_filename = "filename"
        pytest.data_file = genfromtxt('data_empirical.txt')
        pytest.filename = "data_empirical.txt"

    @pytest.fixture
    def fixture_weights_distribution(self):
        pytest.error_message = "Error initializing distribution."
        pytest.wrong_filename = "filename"
        pytest.filename = "data_weights.txt"
        hist = histogram(random.normal(0.0, 0.1, 30))
        data = list(hist[1])
        X_i = [(data[i] + data[i + 1])/2 for i in range(len(data) - 1)]
        P_i = list(hist[0])
        P_i = [i/30 for i in P_i]
        pytest.data_2D = array([X_i, P_i]).T
        pytest.data_3D = array([[X_i, P_i]])
        pytest.data_file = genfromtxt('data_weights.txt', delimiter=',')

    @pytest.fixture
    def fixture_numpy_distribution(self):
        pytest.dist_name = 'beta'
        pytest.wrong_name = 'Normall'
        pytest.error_message = "Error initializing distribution."

    def test_None_distribution(self):
        """
        Creates a None type distribution and assigns the attributes: constant,
        dist_type and seed
        """
        None_dist = Distribution(dist_type=None)

        assert None_dist.constant == None
        assert None_dist.dist_type == None
        assert None_dist.seed == int(time())

    def test_constant_distribution(self, fixture_constant_distribution):
        """
        Creates a constant distribution and assigns the attributes: constant,
        dist_type and seed.
        """
        constant_dist = Distribution(
            dist_type="constant",
            constant=pytest.constant
            )

        assert constant_dist.constant == pytest.constant
        assert constant_dist.dist_type == "constant"
        assert constant_dist.seed == int(time())

    def test_constant_distribution_ValueError_no_constant(
            self, fixture_constant_distribution):
        """
        Raises a SystemError creating a constant type distribution when no
        constant is passing to the constructor method.
        """
        with pytest.raises(SystemError, match=pytest.error_message):
            assert Distribution(dist_type='constant')

    def test_empirical_distribution_using_data(
            self, fixture_empirical_distribution):
        """
        Creates an empirical type distribution using the data parameter and
        assigns the attributes: dist_type, seed and kd_estimator.
        """
        empirical_dist = Distribution(
            dist_type="empirical",
            data=pytest.data_1D,
            filename=None,
            kernel='gaussian',
            bandwidth=0.1)

        expected_kd_stimator = str(
            KernelDensity(
                kernel='gaussian',
                bandwidth=0.1).fit(pytest.data_1D.reshape(-1, 1)
                )
            )

        kd_estimator = str(empirical_dist.kd_estimator)

        assert empirical_dist.dist_type == "empirical"
        assert empirical_dist.seed == int(time())
        assert kd_estimator == expected_kd_stimator

    def test_empirical_distribution_SystemError_data_ndim_is_incorrect(
            self, fixture_empirical_distribution):
        """
        Raises a SystemError creating an empirical type distribution when
        data is not a 1-D array.
        """
        with pytest.raises(SystemError, match=pytest.error_message):
            assert Distribution(
                        dist_type="empirical",
                        data=pytest.data_3D,
                        filename=None,
                        kernel='gaussian',
                        bandwidth=0.1
                        )

    def test_empirical_distribution_using_file(
                self, fixture_empirical_distribution):
        """
        Creates an empirical type distribution using the filename parameter and
        assigns the attributes: dist_type, seed and kd_estimator.
        """
        empirical_dist = Distribution(
            dist_type="empirical",
            data=None,
            filename=pytest.filename,
            kernel='gaussian',
            bandwidth=0.1
            )

        expected_kd_stimator = KernelDensity(
            kernel='gaussian',
            bandwidth=0.1
            ).fit(pytest.data_file.reshape(-1, 1)).sample(
                n_samples=10,
                random_state=0
                )

        kd_estimator = empirical_dist.kd_estimator.sample(
            n_samples=10,
            random_state=0
            )

        assert empirical_dist.dist_type == "empirical"
        assert empirical_dist.seed == int(time())
        assert empirical_dist.filename == pytest.filename
        assert all(kd_estimator == expected_kd_stimator)

    def test_empirical_distribution_SystemError_filename_does_not_exist(self):
        """
        Raises a SystemError creating an empirical type distribution with a
        wrong filename.
        """
        with pytest.raises(SystemError, match=pytest.error_message):
            Distribution(dist_type="empirical", filename=pytest.wrong_filename)

    def test_empirical_distribution_SystemError_KernelDensity_estimator(
            self, fixture_empirical_distribution):
        """Raises an error when wrong a KernelDensity estimator is passed."""
        with pytest.raises(SystemError, match=pytest.error_message):
            assert Distribution(
                dist_type='empirical',
                data=pytest.data_1D,
                kernel='Gaussian',
                bandwidth=0.1
                )

    def test_weights_distribution_data(self, fixture_weights_distribution):
        """
        Creates a weights type distribution using the data parameter and
        assigns the attributes: dist_type, seed, xi and pi.
        """
        weights_dist = Distribution(
            dist_type="weights",
            data=pytest.data_2D
            )

        assert weights_dist.dist_type == "weights"
        assert weights_dist.seed == int(time())
        assert all(weights_dist.xi == pytest.data_2D[:, 0])
        assert all(weights_dist.pi == pytest.data_2D[:, 1])

    def test_weights_distribution_filename(self, fixture_weights_distribution):
        """
        Creates a weights type distribution using the filename parameter
        and assigns the attributes: dist_type, seed, xi and pi.
        """
        weights_dist = Distribution(
            dist_type="weights",
            filename=pytest.filename
            )

        assert weights_dist.dist_type == "weights"
        assert weights_dist.seed == int(time())
        assert all(weights_dist.xi == pytest.data_file[:, 0])
        assert all(weights_dist.pi == pytest.data_file[:, 1])

    def test_weights_distribution_SystemError_filename_does_not_exist(self, fixture_weights_distribution):
        """
        Raises a SystemError creating a weights type distribution with a
        wrong filename.
        """
        with pytest.raises(SystemError, match=pytest.error_message):
            assert Distribution(
                dist_type='weights',
                filename=pytest.wrong_filename
                )

    def test_weights_distribution_SystemError_data_ndim_is_incorrect(
            self, fixture_weights_distribution):
        """
        Raises a SystemError creating a weights type distribution with a
        wrong filename.
        """
        with pytest.raises(SystemError, match=pytest.error_message):
            assert Distribution(dist_type='weights', data=pytest.data_3D)

    def test_numpy_distribution(self, fixture_numpy_distribution):
        """
        Creates a numpy distribution and assigns the attribute
        numpy_distribution.
        """
        numpy_dist = Distribution(
            dist_type='numpy',
            dist_name=pytest.dist_name
            )

        name = numpy_dist.numpy_distribution.__name__
        gen = numpy_dist.random_number_generator
        expected_gen = random.default_rng(seed=int(time()))

        assert numpy_dist.dist_type == "numpy"
        assert numpy_dist.seed == int(time())
        assert all(gen.random(size=3) == expected_gen.random(size=3))
        assert name == pytest.dist_name

    def test_wrong_numpy_name(self, fixture_numpy_distribution):
        """
        Raises a SystemError creating a numpy distribution with a wrong
        dist_name.
        """
        with pytest.raises(SystemError, match=pytest.error_message):
            assert Distribution(dist_type='numpy', dist_name=pytest.wrong_name)

    def test_wrong_type(self):
        """Raises a SystemErrorError when wrong type distribution is passed."""
        with pytest.raises(SystemError, ):
            assert Distribution(dist_type='NumPyy')

    def test_sample_None_distribution(self):
        """Returns a None sample distribution."""
        None_dist = Distribution(dist_type=None)
        sample = None_dist.sample(size=10)
        expected_sample = full(10, None)

        assert all(sample == expected_sample)

    def test_sample_constant_distribution(self):
        """Returns a constant sample distribution."""
        constant_dist = Distribution(dist_type='constant', constant=1)
        sample = constant_dist.sample(5)
        expected_sample = constant_dist.constant*ones(5)

        assert all(sample == expected_sample)

    def test_sample_empirical_distribution_data(
            self, fixture_empirical_distribution):
        """Returns an empirical sample distribution from a data array."""
        empirical_dist = Distribution(
            dist_type='empirical',
            data=pytest.data_1D,
            kernel='gaussian',
            bandwidth=0.1
            )

        sample = empirical_dist.sample(5)

        expected_sample = KernelDensity(
            kernel='gaussian',
            bandwidth=0.1).fit(pytest.data_1D.reshape(-1, 1)).sample(
                n_samples=5, random_state=int(time())
                ).flatten()

        assert all(sample == expected_sample)

    def test_sample_empirical_distribution_file(self, fixture_empirical_distribution):
        """Returns an empirical sample distribution from a file."""
        empirical_dist = Distribution(
            dist_type='empirical',
            data=pytest.data_1D,
            kernel='gaussian',
            bandwidth=0.1
            )

        sample = empirical_dist.sample(5)

        expected_sample = KernelDensity(
            kernel='gaussian',
            bandwidth=0.1).fit(pytest.data_1D.reshape(-1, 1)).sample(
                n_samples=5, random_state=int(time())
                ).flatten()

        assert all(sample == expected_sample)

    def test_sample_weights_distribution_data(
            self, fixture_weights_distribution):
        """Returns a weights sample distribution from a data array."""
        weights_dist = Distribution(
            dist_type='weights',
            data=pytest.data_2D
            )

        sample = weights_dist.sample(5)
        expected_sample = random.default_rng(int(time())).choice(
                    a=pytest.data_2D[:, 0],
                    p=pytest.data_2D[:, 1],
                    size=5
                    )

        assert all(sample == expected_sample)

    def test_sample_numpy_distribution(self):
        """Returns a numpy sample distribution."""
        numpy_dist = Distribution(
            dist_type='numpy',
            dist_name='beta',
            a=1, b=1
            )

        sample = numpy_dist.sample(5)
        expected = random.default_rng(seed=numpy_dist.seed).beta(1, 1, 5)

        assert all(sample == expected)

    def test_sample_positive_constant_distribution(self):
        """Returns a constant positive sample distribution."""
        constant_dist = Distribution(dist_type='constant', constant=1)
        sample = constant_dist.sample_positive()
        expected = constant_dist.constant*ones(1)

        assert sample == expected

    def test_sample_positive_empirical_distribution_data(
            self, fixture_empirical_distribution):
        """Returns an empirical sample distribution from a data array."""
        empirical_dist = Distribution(
            dist_type='empirical',
            data=pytest.data_1D,
            kernel='gaussian',
            bandwidth=0.1
            )

        sample = empirical_dist.sample_positive(5)

        expected_sample = abs(
            KernelDensity(
                kernel='gaussian',
                bandwidth=0.1).fit(pytest.data_1D.reshape(-1, 1)).sample(
                    n_samples=5, random_state=int(time())
                ).flatten()
            )

        assert all(sample == expected_sample)

    def test_sample_positive_empirical_distribution_file(
            self, fixture_empirical_distribution):
        """Returns an empirical sample distribution from a file."""
        empirical_dist = Distribution(
            dist_type='empirical',
            filename=pytest.filename,
            kernel='gaussian',
            bandwidth=0.1
            )

        sample = empirical_dist.sample_positive(5)

        expected_sample = abs(
            KernelDensity(
                kernel='gaussian',
                bandwidth=0.1).fit(pytest.data_file.reshape(-1, 1)).sample(
                    n_samples=5, random_state=int(time())
                    ).flatten()
            )

        assert all(sample == expected_sample)

    def test_sample_positive_weights_distribution_data(
            self, fixture_weights_distribution):
        """Returns a weights sample distribution from a data array."""
        weights_dist = Distribution(
            dist_type='weights',
            data=pytest.data_2D
            )

        sample = weights_dist.sample_positive(5)
        expected_sample = abs(
            random.default_rng(int(time())).choice(
                    a=pytest.data_2D[:, 0], p=pytest.data_2D[:, 1], size=5
                    )
                )

        assert all(sample == expected_sample)

    def test_sample_positive_weights_distribution_file(
            self, fixture_weights_distribution):
        """Returns a weights sample distribution from a file."""
        weights_dist = Distribution(
            dist_type='weights', filename=pytest.filename
            )

        sample = weights_dist.sample_positive(5)
        expected_sample = abs(
            random.default_rng(int(time())).choice(
                a=pytest.data_file[:, 0],
                p=pytest.data_file[:, 1],
                size=5
                )
            )

        assert all(sample == expected_sample)

    def test_sample_positivie_numpy(self):
        """Returns a numpy positive sample distribution."""
        numpy_dist = Distribution(
            dist_type='numpy',
            dist_name='normal',
            loc=-10, scale=0.2
            )

        sample = numpy_dist.sample_positive()
        expected = abs(
            random.default_rng(
                seed=numpy_dist.seed).normal(-10, 0.2)
                )

        assert sample == expected
