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


"""Contagious diseases simulation using Agent-Based Models"""

__version__ = "0.0.2"

from abmodel import agent
from abmodel import models
from abmodel.analysis import Aggregator
from abmodel.population import Population
from abmodel.utils import Distribution
from abmodel.utils import ExecutionModes
from abmodel.utils import EvolutionModes


__all__ = [
    "agent",
    "models",
    "Aggregator",
    "Population",
    "Distribution",
    "ExecutionModes",
    "EvolutionModes"
    ]
