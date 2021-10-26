import pytest

from abmodel.utils.execution_modes import ExecutionModes

class TestExecutionModes:

    def setup_method(self, method):
        """Allows to see a brief description of the test in the report."""
        print('\u21B4' + '\n' + '\u273C' + method.__doc__.strip())

    @pytest.mark.parametrize(
    "ExecutionModes, expected", [
        (getattr(getattr(ExecutionModes, "iterative"), 'value'), "iterative"),
        (getattr(getattr(ExecutionModes, "vectorized"), 'value'), "vectorized"),
        (getattr(getattr(ExecutionModes, "dask"), 'value'), "dask"),
        ],
        ids=["iterative", "vectorized", "dask"]
    )
    def test_execution_modes(self, ExecutionModes, expected):
        """Verifies the correct enumerates of the different execution modes."""
        assert ExecutionModes == expected
