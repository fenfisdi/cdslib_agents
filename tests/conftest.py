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

def pytest_report_teststatus(report):
    """
    Changes the words in the status report of the test and adds a UTF-8 symbol.
    """
    if report.when == 'call':
        if report.passed:
            letter = '\u2714'
            longrep = ' \u2714 '
        elif report.skipped:
            letter = 's'
            longrep = ' \u27A5 '
        elif report.failed:
            letter = '\u2717'
            longrep = ' \u2717 '
        return report.outcome, letter, report.outcome.upper() + longrep
