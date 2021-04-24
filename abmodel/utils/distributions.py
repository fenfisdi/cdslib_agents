from numpy import random
import pandas as pd

from sklearn.neighbors import KernelDensity


class Distribution:
    """
    """
    def __init__(self, type: str, **kwargs, n):
        if type is "empirical":
            print("test")
        else:
            if type in dir(random):
                distribution = getattr(random, type)
            else:
                raise ValueError()
