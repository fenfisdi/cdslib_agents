# Copyright (C) 2021, Camilo Hincapié Gutiérrez
# This file is part of CDSLIB.
#
# CDSLIB is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CDSLIB is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
#
# This package is authored by:
# Camilo Hincapié (https://www.linkedin.com/in/camilo-hincapie-gutierrez/) (main author)
# Ian Mejía (https://github.com/IanMejia)
# Emil Rueda (https://www.linkedin.com/in/emil-rueda-424012207/)
# Nicole Rivera (https://github.com/nicolerivera1)
# Carolina Rojas Duque (https://github.com/carolinarojasd)

from time import time
from typing import Union, Any, Optional

from pydantic import validate_arguments
from numpy import abs, genfromtxt, ndarray, random, ones, full
from sklearn.neighbors import KernelDensity


class Distribution:
    """
        Distribution class

        It computes random numbers from a probability density distribution.

        Methods
        -------
        TODO
    """
    @validate_arguments(config={"arbitrary_types_allowed": True})
    def __init__(self,
                 dist_type: Any,
                 constant: Optional[float] = None,
                 data: Optional[ndarray] = None,
                 filename: Optional[str] = None,
                 dist_name: Optional[str] = None,
                 **kwargs):
        """
            Constructor of Distribution class.

            It specifies which type of distribution is going to be used
            and its corresponding parameters.

            Parameters
            ----------
            dist_type : {None, 'constant', 'empirical', 'weights', 'numpy'}

                None : it allows a `Distribution` object to be set in such
                        way that it always return None.

                'constant' : it numerically implements a "Dirac delta"
                    function, i.e. all points will have the same value
                    specified by the parameter `constant`

                'empirical' : build distributions from empirical data,
                    estimating the overall shape of the distribution using
                    the KDE approach available via Scikit-Learn. If the data is
                    stored in a file, then 'filename' must be passed to specify
                    the path to the file and the data inside that file must be
                    formatted without header in this way:

                    .. code-block::
                        data_0
                        data_1
                        data_2
                        ...

                'weights' : it needs the histogram (xi, pi) data
                    in order to generate a random sample from
                    this given array of points and their corresponding
                    probability weights.
                    It uses Numpy Random Choices [2]_. If the data is
                    stored in a file, then 'filename' must be passed to specify
                    the path to the file and the data inside that file must be
                    formatted without header in this way:

                    .. code-block::
                        x_0, p_0
                        x_1, p_1
                        x_2, p_2
                        ...

                'numpy' : it uses the distributions implemented in
                    Numpy Random Distributions [3]_

            constant : float, optional
                It specifies the constant value to which all point are
                mapped.

            data : ndarray, optional
                It corresponds

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
            ValueError
                TODO: when ?

            SystemError
                TODO: when ?

            References
            ----------
            .. [1] [Scikit-learn: Kernel Density Estimation](https://scikit-learn.org/stable/modules/density.html#kernel-density)
            .. [2] [Numpy Random Choice](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.choice.html#numpy.random.Generator.choice)
            .. [3] [Numpy Random Distributions](https://numpy.org/doc/stable/reference/random/generator.html#distributions)

            Examples
            --------
            TODO: include some exhaustive examples here using each dist_type
        """
        self.dist_type = dist_type
        self.seed = int(time())

        try:
            if self.dist_type is None:
                # Allows a `Distribution` object set to None
                self.constant = None

            elif self.dist_type == "constant":
                # "Dirac delta"-like function
                if constant is not None:
                    self.constant = constant
                else:
                    raise ValueError(
                        "Parameter `constant` should not be None when "
                        "`dist_type` = 'constant'"
                        )

            elif self.dist_type == "empirical":
                # Using KernelDensity estimator from Scikit-learn
                if data is not None and filename is None:
                    pass
                elif data is None and filename is not None:
                    self.filename = filename

                    data = genfromtxt(self.filename)
                else:
                    raise ValueError(
                        "The data is required and must be provided through "
                        "the parameter `data` or `filename` when "
                        "`dist_type` = 'empirical', then one of them should "
                        "not be None"
                        )

                # Check data has the right dimension
                if data.ndim == 1:
                    self.kwargs = kwargs
                    self.kd_estimator = KernelDensity(**self.kwargs).fit(
                        data.reshape(-1, 1)
                        )
                else:
                    raise ValueError(
                        "The data provided should be a 1-D array."
                        )

            elif self.dist_type == "weights":
                # Using numpy.random.choice
                if data is not None and filename is None:
                    pass
                elif data is None and filename is not None:
                    self.filename = filename
                    data = genfromtxt(self.filename, delimiter=",")
                else:
                    raise ValueError(
                        "The data is required and must be provided through "
                        "the parameter `data` or `filename` when "
                        "`dist_type` = 'weights', then one of them should "
                        "not be None"
                        )

                # Check data has the right dimension
                if data.ndim == 2:
                    self.xi = data[:, 0]
                    self.pi = data[:, 1]

                    self.random_number_generator = \
                        random.default_rng(seed=self.seed)
                else:
                    raise ValueError(
                        "The data provided should be a 2-D array."
                        )

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
                        f"Distribution '{dist_name}' is not "
                        "implemented in  numpy.random. See: "
                        "https://numpy.org/doc/stable/reference/random/"
                        "generator.html#distributions"
                        )
            else:
                raise ValueError(
                    "'dist_type' is not in "
                    "{None, 'constant', 'empirical', 'weights', 'numpy'}"
                    )

        except Exception as error:
            self.manage_exception(
                exception=error,
                message="Error initializing distribution."
                )

    @validate_arguments
    def sample(self, size: int = 1) -> Union[ndarray, int, float]:
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
                TODO: when ?

            Examples
            --------
            TODO: include some examples
        """
        if self.dist_type is None:
            # Always return None
            samples = full(size, self.constant)

        elif self.dist_type == "constant":
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

    @validate_arguments
    def sample_positive(self, size: int = 1) -> Union[ndarray, int]:
        """
            Compute one random sample using the defined distribution,
            but restrincting output to be strictly positive.

            Parameters
            ----------
            size : int, default=1

            Raises
            ------
            SystemError
                TODO: when ?

            See Also
            --------
            sample : Compute random sampling using the defined distribution.

            Examples
            --------
            TODO: include some examples
        """
        return abs(self.sample(size))

    @validate_arguments(config={"arbitrary_types_allowed": True})
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
                TODO: when ?

            Examples
            --------
            TODO: include some examples
        """
        raise SystemError(f"{message}\nError: {exception}")
