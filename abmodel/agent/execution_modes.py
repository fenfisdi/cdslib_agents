from enum import Enum


class ExecutionModes(Enum):
    """
        This class enumerates the different execution modes
        that are avaible across agent module
    """
    pandas = "pandas"
    vectorized = "vectorized"
    dask = "dask"
    swifter = "swifter"
