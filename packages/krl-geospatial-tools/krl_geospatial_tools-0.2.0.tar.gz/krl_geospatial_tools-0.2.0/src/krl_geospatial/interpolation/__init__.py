"""
Spatial interpolation methods.

This module provides various spatial interpolation techniques for estimating
values at unsampled locations based on observed data.

© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC.

Classes
-------
OrdinaryKriging : Ordinary kriging interpolation
UniversalKriging : Universal kriging with trend
IDW : Inverse Distance Weighting
ThinPlateSpline : Thin plate spline interpolation

Examples
--------
>>> from krl_geospatial import interpolation
>>>
>>> # Kriging interpolation
>>> kriging = interpolation.OrdinaryKriging(variogram_model='spherical')
>>> kriging.fit(gdf, 'elevation')
>>> predictions = kriging.predict(new_points)
>>>
>>> # IDW interpolation
>>> idw = interpolation.IDW(power=2, radius=1000)
>>> idw.fit(gdf, 'temperature')
>>> predictions = idw.predict(new_points)
"""

from .idw import IDW
from .kriging import OrdinaryKriging, UniversalKriging
from .splines import RegularizedSpline, ThinPlateSpline

__all__ = [
    "OrdinaryKriging",
    "UniversalKriging",
    "IDW",
    "ThinPlateSpline",
    "RegularizedSpline",
]
