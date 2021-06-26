from abmodel.utils.distributions import Distribution, initialize_distribution


class SusceptibilityGroup:
    """
        Attributes
        ----------
        name : str
            Susceptibility group name.

        si_dist : Distribution
            Susceptibility index distribution for
            this susceptibility group.
    """
    name: str
    si_dist: Distribution

    def __init__(
        self, name: str, dist: dict
    ):
        """
            Parameters
            ----------
            name : str
                Susceptibility group name.

            dist : dict
                Dictionary with the required information
                in order to initialize the
                Susceptibility Index distribution.
        """
        self.name = name
        self.si_dist = initialize_distribution(dist)
