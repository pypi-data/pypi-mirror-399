"""
Typing aliases and data structures for OpenNetics.
"""

from dataclasses import dataclass
from sklearn.mixture import GaussianMixture

class SensorData:
    """
    Encapsulates Gaussian Mixture models for sensors, with their 
    `threshold`, `random state`, and `n components` parameters.
    """
    models: list[GaussianMixture] = ...
    threshold: float = ...
    random_state: int = ...
    n_components: int = ...


@dataclass(frozen=True)
class GestureMatch:
    """
    Immutable container for gesture checker. Holds the `value` and `status` of a gesture match,
    where value is the matching score and status indicates if the gesture is recognised.
    """
    value: float
    status: bool
    ...


data_dict_t = dict[str, SensorData]

