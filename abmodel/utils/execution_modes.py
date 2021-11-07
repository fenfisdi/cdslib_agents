from enum import Enum


class ExecutionModes(Enum):
    """
        This class enumerates the different execution modes
        that are avaible across agent module
        TODO: expand explanation
    """
    iterative = "iterative"
    vectorized = "vectorized"
    dask = "dask"
    swifter = "swifter"


class EvolutionModes(Enum):
    """
        This class enumerates the evolution modes that can be used in
        the method Population.evolve() and determines if cumulative
        storing data or not.
    """
    steps = "steps"
    cumulative = "cumulative"
