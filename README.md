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

All tests were developed with the python tool pytest.

During test execution with pytest, any output sent to stdout and stderr is
[captured](https://docs.pytest.org/en/6.2.x/capture.html). The `-s` flag disables
all capturing and lets the user looks at all the outputs, this is very important
because the description of all the tests were typed in the docstring of each method
of the class.

The `-v` flag indicates to pytest run in [verbosity](https://docs.pytest.org/en/latest/how-to/output.html)
mode. This controls all the pytest outputs. On the other hand, `-rA` flag, displays
a [“short test summary info”](https://docs.pytest.org/en/6.2.x/usage.html#detailed-summary-report)
at the end of the test session.

Typing flags using pytest might be tedious, however, it is possible to make and
modify a `pytest.init` file. This allows adopts as many flags as you want.
[change default command-line options](https://docs.pytest.org/en/6.2.x/example/simple.html#how-to-change-command-line-options-defaults).
In the `abmodel/tests` directory, you will find this file. In our case, it was
adopted the flags: `-v`, `-s`, `--no-header` and `-rs`, therefore, to run a test
it is only necessary type in the command-line:

```python
$ pytest <name_of_the_test_file.py>
```

For more information about [pytest flags](https://docs.pytest.org/en/6.2.x/usage.html).

Instead of run test by test, you can run all the tests at the same time.
You must be inside of `abmodel/tests`, and just type:

```python
$ pytest
```

For a [short test summary info](https://docs.pytest.org/en/6.2.x/usage.html#detailed-summary-report),
you only need to type in the command-line:

```python
$ pytest -r
```

Finally, if you want to modify the initial conditions of the test, use the
fixtures methods at the beginning of all the tests files.

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
