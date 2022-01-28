# CDSLib - Agents

Welcome to **CDSLib - Agents** package.

[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![PyPI](https://img.shields.io/pypi/v/cdslib-agents?color=color=%2310d510)](https://pypi.org/project/cdslib-agents/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cdslib-agents?color=%2310d510)](https://pypi.org/project/cdslib-agents/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/fenfisdi/cdslib_agents/graphs/commit-activity)
[![GitHub contributors](https://img.shields.io/github/contributors/fenfisdi/cdslib_agents)](https://github.com/fenfisdi/cdslib_agents/graphs/contributors)

## License

[![license](https://img.shields.io/github/license/fenfisdi/cdslib_agents)](./LICENSE)

## Sponsors

| [![Sponsored by](https://img.shields.io/badge/sponsored%20by-UdeA-yellow)](https://www.udea.edu.co/) | [![Sponsored by](https://img.shields.io/badge/sponsored%20by-minciencias-yellow)](https://minciencias.gov.co/) | [![Sponsored by](https://img.shields.io/badge/sponsored%20by-sena-yellow)](https://www.sena.edu.co/) |
| :---: | :---: | :---: |
| <img src="https://raw.githubusercontent.com/fenfisdi/cdslib_agents/2335693f162e3cca97f7bba8591db9b0076a3823/images/Escudo-UdeA.svg" alt="UdeA logo" height="34"> | <img src="https://raw.githubusercontent.com/fenfisdi/cdslib_agents/1755d1fc4e45e94fcdc4275709b93fdf4eabd5f2/images/Minciencias_Colombia.svg" alt="Minciencias logo" width="160" height="34"> | <img src="https://raw.githubusercontent.com/fenfisdi/cdslib_agents/2335693f162e3cca97f7bba8591db9b0076a3823/images/Sena_Colombia_logo.svg" alt="Sena logo" height="34"> |


## Code quality metrics

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=fenfisdi_cdslib_agents&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=fenfisdi_cdslib_agents)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=fenfisdi_cdslib_agents&metric=bugs)](https://sonarcloud.io/summary/new_code?id=fenfisdi_cdslib_agents)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=fenfisdi_cdslib_agents&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=fenfisdi_cdslib_agents)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=fenfisdi_cdslib_agents&metric=coverage)](https://sonarcloud.io/summary/new_code?id=fenfisdi_cdslib_agents)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=fenfisdi_cdslib_agents&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=fenfisdi_cdslib_agents)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=fenfisdi_cdslib_agents&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=fenfisdi_cdslib_agents)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=fenfisdi_cdslib_agents&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=fenfisdi_cdslib_agents)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=fenfisdi_cdslib_agents&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=fenfisdi_cdslib_agents)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=fenfisdi_cdslib_agents&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=fenfisdi_cdslib_agents)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=fenfisdi_cdslib_agents&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=fenfisdi_cdslib_agents)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=fenfisdi_cdslib_agents&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=fenfisdi_cdslib_agents)

## Description

As part of the **Contagious Disease Simulation Library**, the
**CDSLib - Agents** package is intended to be used for modelling and simulating
contagious diseases using Agent-Based Models and it has been used for the development
of the [Contagious Disease Simulation Laboratory](https://github.com/fenfisdi/cdslab).

The package consists of different implementations of a heterogeneous population
of agents following rules of behavior that determine their movement and the evolution
of their infectious and clinical states.

The current implementation allows Agents to move in a bidemensional space following
a distribution of velocities based on population data. This can be achieved thanks to
the inclusion Distribution module which is a wrapper for different tools that provides
distribution-like function support.

In regards to the disease states, the current implementation also allows the user to
add as much states as preferred, and to create custom natural history of the disease
(i.e. the design a custom graph for evolution of disease states).

For more information, please refer to the official documentation of the project.

## Testing

All the tests were developed with the python tool pytest. To see them properly, type
in the command line:

`$ poetry run pytest <name_of_test_file>`

in the same ubication of the test file.

Flags are used with pytest for modifying the aspect of the output
report. Typing flags using pytest might be tedious, however, it is possible modify the `pytest.init` file for
[change defaulting command line options](https://docs.pytest.org/en/6.2.x/example/simple.html#how-to-change-command-line-options-defaults). This allows to adopt as many flags
as necesary. In our case, it was adopted the flags: `-s`, `--no-header`, `-rA`, `-vv`,
`--cov`, `--cov-branch`.

During test execution with pytest, any output sent to stdout and stderr is
[captured](https://docs.pytest.org/en/6.2.x/capture.html). The `-s` flag  
disable all capturing and lets the user look at all the outputs, this is very
important because the description of all tests was typed in the docstring of each method.

The `--no-header` flag disables the [initial header](https://docs.pytest.org/en/stable/changelog.html#id33).

The `-rA` flag shows extra test [summary info](https://docs.pytest.org/en/6.2.x/usage.html#detailed-summary-report) of all the tests.

The `-vv` flag indicates to pytest run in [verbosity](https://docs.pytest.org/en/latest/how-to/output.html) mode, this controls all the pytest outputs.

The flag `--cov` produces a [coverage](https://pytest-cov.readthedocs.io/en/latest/#welcome-to-pytest-cov-s-documentation) reports. It shows the percentage of code lines covered by the test, while `--cov-branch` shows the branches covered. A branch is
a decision taken by the code when it finds an if sentence or similar.

For more information about [pytest flags](https://docs.pytest.org/en/6.2.x/usage.html).

Instead of running one test, it is possible to run all the tests at the same time. You must be inside of `tests` directory, and type in the command line:

`$ poetry run pytest`

So as to Modify the initial conditions of the test, use the fixtures methods at the beginning
of all the tests files.

![repo_logo](https://raw.githubusercontent.com/fenfisdi/cdslib_agents/main/images/CDSLib_agents_white-background.png "CDSLib - Agents Logo")

## Authors and main contributors

[![GitHub contributors](https://img.shields.io/github/contributors/fenfisdi/cdslib_agents)](https://github.com/fenfisdi/cdslib_agents/graphs/contributors)

This package is authored by 
[Camilo Hincapié](https://www.linkedin.com/in/camilo-hincapie-gutierrez/) (main author),
[Ian Mejía](https://github.com/IanMejia),
[Emil Rueda](https://www.linkedin.com/in/emil-rueda-424012207/),
[Nicole Rivera](https://github.com/nicolerivera1)
and
[Carolina Rojas Duque](https://github.com/carolinarojasd)
and the conceptual contributions about epidemiology of
[Lina Marcela Ruiz Galvis](mailto:lina.ruiz2@udea.edu.co).

Other remarkably contributors to this work were
[Alejandro Campillo](https://www.linkedin.com/in/alucardcampillo/)
and
[Daniel Alfonso Montoya](https://www.linkedin.com/in/daniel-montoya-ds/).




## Contact us

For any suggestion on the development of this type of models, please our official
channels of [dicussions](https://github.com/fenfisdi/cdslib_agents/discussions)
provided by GitHub.

## Development

### Create the virtualenv

This package is managed using [Pyenv](https://github.com/pyenv/pyenv) and 
[Poetry](https://python-poetry.org/docs/). In order to create the
virtualenv correctly use:

```
$ pyenv install 3.9.7
$ poetry env use 3.9.7
$ poetry install
```

Then activate the virtualenv running `poetry shell`, and to deactivate the virtual
environment and exit this new shell type `exit`.
