.. _contribute-documentation:

========================
Documenting this project
========================

The documentation of the project is developed using the Sphinx framework. All
files related to it can be accessed in the ``~/docs`` directory

Docstring format
================

In this project we use the `NumPy-SciPy docstrings`_ format. In any case,
the docstring must contain at least the first-line general description.
Depending on the object to be documented, it must also include:

- functions and methods:
   * list of parameters with the corresponding data types
   * return data type and description

- classes:
   * list of attributes with descriptions
   * all methods must be appropiately documented

External references
===================

* `Sphinx framework`_
* `NumPy-SciPy docstrings`_
* `Documenting Python Code`_


.. _NumPy-SciPy docstrings: https://numpydoc.readthedocs.io/en/latest/format.html
.. _Sphinx framework: <https://www.sphinx-doc.org/en/master/#>
.. _Documenting Python Code: https://realpython.com/documenting-python-code/