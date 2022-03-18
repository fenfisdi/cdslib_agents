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
