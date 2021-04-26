from numpy import genfromtxt, random
from sklearn.neighbors import KernelDensity


class Distribution:
    """
    """
    def __init__(self, dist_type: str, filename: str = "", **kwargs):
        """
        """
        self.dist_type = dist_type
        self.kwargs = kwargs

        if dist_type == "empirical":
            try:
                data = genfromtxt(filename)
                self.kd_estimator = KernelDensity(**kwargs).fit(data)
            except Exception as error:
                raise ValueError(f"Error parsing file: {filename}\n", error)
        else:
            if dist_type in dir(random):
                self.distribution = getattr(random, dist_type)
            else:
                raise ValueError(
                    "'dist_type' is not implemented in "
                    "numpy.random"
                    )

    def sample_one(self):
        """
        """
        if self.dist_type == "empirical":
            return self.kd_estimator.sample(n_samples=1,
                                            random_state=None)[0][0]
        else:
            # Using numpy.random
            return self.distribution(**self.kwargs)[0]
