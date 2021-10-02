# CDSLib - Agents

Welcome to **CDSLib - Agents** package.

![repo_logo](https://raw.githubusercontent.com/fenfisdi/cdslib_agents/dev/images/CDSLib_agents_white-background.png "CDSLib - Agents Logo")

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

All the test were developed with the python tool pytest. To see them properly, type 
in the command line: 

`$ pytest -s -v <name_of_test>`

During test execution with pytest, any output sent to stdout and stderr is 
[captured](https://docs.pytest.org/en/6.2.x/capture.html). the `-s` flag  
disable all capturing and let the user look at all the outputs, this is very 
important because the description of all test were typed in the docstring of each method.

The `-v` flag indicate to pytest run in [verbosity](https://docs.pytest.org/en/latest/how-to/output.html) 
mode, this control all the pytest outputs.

If you want to run all the test at the same time, you must be inside of `abmodel/tests`, 
and type in the command line:

`$ pytest -s -v`

For more information about [pytest flags](https://docs.pytest.org/en/6.2.x/usage.html).

For modify the initial conditions of the test, use the fixtures methods at the beggining 
of all the tests files.

For a [short test summary info](https://docs.pytest.org/en/6.2.x/usage.html#detailed-summary-report), 
type in the command line:

`$ pytest -r`

Typing flags using pytest might be tedious, however, it is possible modify the `pytest.init` file for 
[change defaulting command line options](https://docs.pytest.org/en/6.2.x/example/simple.html#how-to-change-command-line-options-defaults).

## How to contribute

Please review our [contributing document](https://github.com/fenfisdi/cdslab/blob/main/contributing.md)


## Contributors

We want to give special thanks to
[Camilo Hincapié](https://www.linkedin.com/in/camilo-hincapie-gutierrez/)
and [Ian Mejía](https://www.linkedin.com/in/ian-mejia-61aaa220b/) for their constant
work on this project, and [Carolina Rojas Duque](https://github.com/carolinarojasd)
for her colaboration on tests development.

Finally, we want to thank Lina Ruiz for the conceptual suggestions she provided in
order to help to specify the package.

## Contact us

For any suggestion on the development of this type of models, please our official
channels of [dicussions](https://github.com/fenfisdi/cdslib_agents/discussions)
provided by GitHub.

## License

[GNU General Public License v3 (GPLv3)](./LICENSE)
