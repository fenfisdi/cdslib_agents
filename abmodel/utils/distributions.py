from time import time
from typing import Union

from numpy import abs, genfromtxt, ndarray, random, ones
from sklearn.neighbors import KernelDensity


class Distribution:
    """
        Distribution class

        It computes random numbers from a probability density distribution.
    """
    def __init__(self, dist_type: str, constant: float = 0.0, filename: str = "",
                 dist_name: str = "", **kwargs):
        """
            Constructor of Distribution class.

            It specifies which type of distribution is going to be used
            and its corresponding parameters.

            Parameters
            ----------
            dist_type : {'constant', 'empirical', 'weights', 'numpy'}

                'constant': it numerically implements a "Dirac delta" function,
                    i.e. all points will have the same value specified
                    by the parameter `constant`

                'empirical' : build distributions from empirical data,
                estimating the overall shape of the distribution using
                the KDE approach available via Scikit-Learn

                'weights' : it needs the histogram (xi, pi) data without
                    header in order to generates a random sample from
                    this given 1-D array and its corresponding weights.
                    It uses Numpy Random Choices [2]_

                'numpy' : it uses the distributions implemented in
                    Numpy Random Distributions [3]_

            constant : float, optional
                It specifies the constant value to which all point are
                mapped.

            filename : str, optional
                It specifies the path for the required data in order to build
                a distribution from this data. It is required by
                `dist_type = 'empirical'` or `dist_type = 'weights'`.

            dist_name : str, optional
                It specifies the distribution to use from numpy when
                `dist_type = 'numpy'`.

            **kwargs : dict, optional
                Extra arguments that must to be passed to the
                Scikit-Learn's Kernel Density constructor [1]_ or
                to the Numpy Random Distributions [3]_, except the parameter
                `size`. In the latter case, keyword argument must not be
                passed since it is used directly in the sampling methods.

            Raises
            ------
            SystemError

            References
            ----------
            .. [1] [Scikit-learn: Kernel Density Estimation](https://scikit-learn.org/stable/modules/density.html#kernel-density)
            .. [2] [Numpy Random Choice](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.choice.html#numpy.random.Generator.choice)
            .. [3] [Numpy Random Distributions](https://numpy.org/doc/stable/reference/random/generator.html#distributions)
        """
        self.dist_type = dist_type
        self.seed = int(time())

        try:
            if self.dist_type == "constant":
                # "Dirac delta"-like function
                self.constant = constant

            elif self.dist_type == "empirical":
                # Using KernelDensity estimator from Scikit-learn
                self.filename = filename
                self.kwargs = kwargs

                data = genfromtxt(self.filename)

                self.kd_estimator = KernelDensity(**self.kwargs).fit(
                    data.reshape(-1, 1)
                    )

            elif self.dist_type == "weights":
                # Using numpy.random.choice
                self.filename = filename

                data = genfromtxt(self.filename, delimiter=",")

                self.xi = data[:, 0]
                self.pi = data[:, 1]

                self.random_number_generator = \
                    random.default_rng(seed=self.seed)

            elif self.dist_type == "numpy":
                # Using numpy.random
                self.kwargs = kwargs

                self.random_number_generator = \
                    random.default_rng(seed=self.seed)

                if dist_name in dir(random):
                    self.numpy_distribution = getattr(
                        self.random_number_generator,
                        dist_name
                        )
                else:
                    raise ValueError(
                        f"Distribution '{dist_name}' is not implemented in "
                        "numpy.random. See: "
                        "https://numpy.org/doc/stable/reference/random/generator.html#distributions"
                        )
            else:
                raise ValueError(
                    "'dist_type' is not in "
                    "{'constant', 'empirical', 'weights', 'numpy'}"
                    )

        except Exception as error:
            self.manage_exception(
                exception=error,
                message="Error initializing distribution."
                )

    def sample(self, size: int = 1) -> Union[ndarray, int]:
        """
            Compute random sampling using the defined distribution.

            Parameters
            ----------
            size : int, default=1
                Number of samples to generate.

            Returns
            -------
            samples : int or numpy.array
                Samples generated.

            Raises
            ------
            SystemError
        """
        if self.dist_type == "constant":
            # "Dirac delta"-like function
            samples = self.constant*ones(size)
        elif self.dist_type == "empirical":
            # Using KernelDensity estimator from Scikit-learn
            try:
                samples = self.kd_estimator.sample(
                    n_samples=size, random_state=self.seed).flatten()
            except Exception as error:
                self.manage_exception(
                    exception=error,
                    message="Error using KernelDensity estimator."
                    )
        elif self.dist_type == "weights":
            # Using numpy.random.choice
            try:
                samples = self.random_number_generator.choice(
                    a=self.xi, p=self.pi, size=size)
            except Exception as error:
                self.manage_exception(
                    exception=error,
                    message="Exception with numpy random choice."
                    )

        elif self.dist_type == "numpy":
            # Using numpy.random
            try:
                samples = self.numpy_distribution(**self.kwargs, size=size)
            except Exception as error:
                self.manage_exception(
                    exception=error,
                    message="Exception with numpy random distributions."
                    )

        else:
            raise ValueError(
                "'dist_type' is not in "
                "{'constant', 'empirical', 'weights', 'numpy'}"
                )

        if size == 1:
            return samples[0]
        else:
            return samples

    def sample_positive(self, size: int = 1) -> Union[ndarray, int]:
        """
            Compute one random sample using the defined distribution,
            but restrincting output to be strictly positive.

            Parameters
            ----------
            size : int, default=1

            See Also
            --------
            sample
        """
        return abs(self.sample(size))

    def manage_exception(self, exception: Exception, message: str):
        """
            Internal function for managing exceptions

            Parameters
            ----------
            exception : Exception
                Exception raised by the workflow.

            message : str
                String with the error message.

            Raises
            ------
            SystemError
        """
        raise SystemError(f"{message}\nError: {exception}")
