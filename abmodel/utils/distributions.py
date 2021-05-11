from time import time
from typing import Union

from numpy import abs, genfromtxt, ndarray, random
from sklearn.neighbors import KernelDensity


class Distribution:
    """
        Distribution class

        It computes random numbers from a probability density distribution.
    """
    def __init__(self, dist_type: str, filename: str = "",
                 distribution: str = "", **kwargs):
        """
            Constructor of Distribution class.

            It specifies which type of distribution is going to be used
            and its corresponding parameters.

            Parameters
            ----------
            dist_type : {'empirical', 'weights', 'numpy'}

                'empirical' : build distributions from empirical data,
                estimating the overall shape of the distribution using
                the KDE approach available via Scikit-Learn

                'weights' : it needs the histogram (xi, pi) data without
                    header in order to generates a random sample from
                    this given 1-D array and its corresponding weights.
                    It uses Numpy Random Choices [2]_

                'numpy' : it uses the distributions implemented in
                    Numpy Random Distributions [3]_

            filename : str, optional
                It specifies the path for the required data in order to build
                a distribution from this data. It is required by
                `dist_type = 'empirical'` or `dist_type = 'weights'`.

            distribution : str, optional
                It specifies the distribution to use from numpy when
                `dist_type = 'numpy'`.

            **kwargs : dict, optional
                Extra arguments that must to be passed to the
                Scikit-Learn's Kernel Density constructor [1]_ or
                to the Numpy Random Distributions [3]_. In the latter
                case, keyword argument must not be passed since it is used
                directly in the sampling methods.

            References
            ----------
            .. [1] [Scikit-learn: Kernel Density Estimation](https://scikit-learn.org/stable/modules/density.html#kernel-density)
            .. [2] [Numpy Random Choice](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.choice.html#numpy.random.Generator.choice)
            .. [3] [Numpy Random Distributions](https://numpy.org/doc/stable/reference/random/generator.html#distributions)
        """
        self.dist_type = dist_type
        self.seed = int(time())

        if self.dist_type == "empirical":
            # Using KernelDensity estimator from Scikit-learn
            try:
                self.filename = filename
                self.kwargs = kwargs

                data = genfromtxt(self.filename)

            except Exception as error:
                raise ValueError(
                    f"Error parsing file: {self.filename}\n",
                    error
                    )

            try:
                self.kd_estimator = KernelDensity(**self.kwargs).fit(
                    data.reshape(-1, 1)
                    )
            except Exception as error:
                raise ValueError(
                    "Error using KernelDensity: \n",
                    error
                    )

        elif self.dist_type == "weights":
            # Using numpy.random.choice
            try:
                self.filename = filename

                data = genfromtxt(self.filename, delimiter=",")

                self.xi = data[:, 0]
                self.pi = data[:, 1]

            except Exception as error:
                raise ValueError(
                    f"Error parsing file: {self.filename}\n",
                    error
                    )
            else:
                self.random_number_generator = \
                    random.default_rng(seed=self.seed)

        elif self.dist_type == "numpy":
            # Using numpy.random
            try:
                self.kwargs = kwargs

                self.random_number_generator = \
                    random.default_rng(seed=self.seed)

                if distribution in dir(random):
                    self.distribution = getattr(
                        self.random_number_generator,
                        distribution
                        )
                else:
                    raise ValueError(
                        "'distribution' is not implemented in "
                        "numpy.random. See: "
                        "https://numpy.org/doc/stable/reference/random/generator.html#distributions"
                        )
            except Exception as error:
                raise ValueError(
                    "Error using numpy.random distributions:\n",
                    error
                    )

        else:
            raise TypeError(
                "'dist_type' is not in {'empirical', 'weights', 'numpy'}"
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

            References
            ----------
            .. [1] [Scikit-learn: Kernel Density Estimation](https://scikit-learn.org/stable/modules/density.html#kernel-density)
            .. [2] [Numpy Random Choice](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.choice.html#numpy.random.Generator.choice)
            .. [3] [Numpy Random Distributions](https://numpy.org/doc/stable/reference/random/generator.html#distributions)
        """
        if self.dist_type == "empirical":
            # Using KernelDensity estimator from Scikit-learn
            try:
                samples = self.kd_estimator.sample(
                    n_samples=size, random_state=self.seed).flatten()
            except Exception as error:
                raise Exception(
                    "Exception with Kernel Density Estimation. "
                    f"Error: {error}"
                    )

        elif self.dist_type == "weights":
            # Using numpy.random.choice
            try:
                samples = self.random_number_generator.choice(
                    a=self.xi, p=self.pi, size=size)
            except Exception as error:
                raise Exception(
                    "Exception with numpy random choice. "
                    f"Error: {error}"
                    )

        elif self.dist_type == "numpy":
            # Using numpy.random
            try:
                samples = self.distribution(**self.kwargs, size=size)
            except Exception as error:
                raise Exception(
                    "Exception with numpy random distributions. "
                    f"Error: {error}"
                    )

        else:
            raise TypeError(
                "'dist_type' is not in {'empirical', 'weights', 'numpy'}"
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
