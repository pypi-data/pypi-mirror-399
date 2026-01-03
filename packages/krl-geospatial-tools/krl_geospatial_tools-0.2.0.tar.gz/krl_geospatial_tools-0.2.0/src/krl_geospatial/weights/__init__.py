"""
Spatial weights package.

This module provides classes for constructing various types of spatial weight matrices,
including contiguity-based, distance-based, and kernel weights.
"""

from .base import SpatialWeights
from .contiguity import QueenWeights, RookWeights
from .distance import DistanceBandWeights, InverseDistanceWeights, KNNWeights
from .kernel import EpanechnikovWeights, GaussianWeights, KernelWeights, TriangularWeights

__all__ = [
    "SpatialWeights",
    "QueenWeights",
    "RookWeights",
    "KNNWeights",
    "DistanceBandWeights",
    "InverseDistanceWeights",
    "KernelWeights",
    "GaussianWeights",
    "EpanechnikovWeights",
    "TriangularWeights",
]
