from typing import Any

from abmodel.utils import Distribution


def init_distribution(dist_dict: dict[str, Any]) -> Distribution:
    """
        This helper function should be used for initializing
        a Distribution from `dist_dict` which should
        contain the required information.

        Parameters
        ----------
        dist_dict : dict
            Dictionary with the required information
            in order to initialize the distribution.

        Returns
        -------
        distribution : Distribution
            An initialized distribution from dist_dict.

        See Also
        --------
        abmodel.utils.distributions.Distribution : Distribution class
    """
    if dist_dict["dist_type"] == "constant":
        return Distribution(
            dist_type=dist_dict["dist_type"],
            constant=dist_dict["constant"]
            )
    elif dist_dict["dist_type"] == "empirical":
        return Distribution(
            dist_type=dist_dict["dist_type"],
            data=dist_dict["data"],
            filename=dist_dict["filename"],
            **dist_dict["kwargs"]
            )
    elif dist_dict["dist_type"] == "weights":
        return Distribution(
            dist_type=dist_dict["dist_type"],
            data=dist_dict["data"],
            filename=dist_dict["filename"],
            )
    elif dist_dict["dist_type"] == "numpy":
        return Distribution(
            dist_type=dist_dict["dist_type"],
            dist_name=dist_dict["dist_name"],
            **dist_dict["kwargs"]
            )
    else:
        return Distribution(
            dist_type=dist_dict["dist_type"]
            )
