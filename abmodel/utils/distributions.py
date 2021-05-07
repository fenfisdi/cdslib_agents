from numpy import random, genfromtxt
from sklearn.neighbors import KernelDensity


class Distribution:
    """
    """
    def __init__(self, dist_type: str, filename: str = "", **kwargs):
        """
            'empirical': it builts distribution from data.

            'weights': it needs the histogram (xi, pi) without header

            The other way is to pass directly a function from numpy.random
        """
        self.dist_type = dist_type
        self.kwargs = kwargs

        if self.dist_type == "empirical":
            # Using KernelDensity estimator from Scikit-learn
            try:
                data = genfromtxt(filename)
                self.kd_estimator = KernelDensity(**kwargs).fit(
                    data.reshape(-1, 1)
                    )
            except Exception as error:
                raise ValueError(
                    f"Error parsing file: {filename}\n"
                    + error
                    )
        elif self.dist_type == "weights":
            # Using numpy.random.choice
            data = genfromtxt(filename, delimiter=",")

            self.xi = data[:, 0]
            self.pi = data[:, 1]
        else:
            # Using numpy.random
            if self.dist_type in dir(random):
                self.distribution = getattr(random, dist_type)
            else:
                raise ValueError(
                    "'dist_type' is not implemented in "
                    "numpy.random neither corresponds to "
                    "'empirical' nor 'weights'"
                    )

    def sample_one(self):
        """
        """
        if self.dist_type == "empirical":
            # Using KernelDensity estimator from Scikit-learn
            return self.kd_estimator()

        elif self.dist_type == "weights":
            # Using numpy.random.choice
            return random.choice(a=self.xi, p=self.pi)
        else:
            # Using numpy.random
            return self.distribution(**self.kwargs)[0]
