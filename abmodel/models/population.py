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
#This package is authored by:
#Camilo Hincapié (https://www.linkedin.com/in/camilo-hincapie-gutierrez/) (main author)
#Ian Mejía (https://github.com/IanMejia)
#Emil Rueda (https://www.linkedin.com/in/emil-rueda-424012207/)
#Nicole Rivera (https://github.com/nicolerivera1)
#Carolina Rojas Duque (https://github.com/carolinarojasd)
#and the conceptual contributions about epidemiology of
#Lina Marcela Ruiz Galvis (mailto:lina.ruiz2@udea.edu.co).
#
#Other remarkably contributors to this work were
#Alejandro Campillo (https://www.linkedin.com/in/alucardcampillo/)
#Daniel Alfonso Montoya (https://www.linkedin.com/in/daniel-montoya-ds/).


from datetime import datetime, timedelta
from collections import namedtuple

from pydantic import BaseModel


BoxSize = namedtuple("BoxSize", "left right bottom top")


class Configutarion(BaseModel):
    """
        TODO: Add brief explanation

        Attributes
        ----------
        TODO

        Examples
        --------
        TODO: include some examples
    """
    population_number: int
    initial_date: datetime
    iteration_time: timedelta
    box_size: BoxSize
    alpha: float  # Reduction factor of spread prob due to hospitalization
    beta: float  # Reduction factor of spread prob due to being isolated
    # box_size_units:
