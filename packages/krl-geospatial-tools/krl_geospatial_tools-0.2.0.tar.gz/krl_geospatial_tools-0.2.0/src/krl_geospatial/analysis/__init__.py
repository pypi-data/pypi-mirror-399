"""
Spatial analysis tools for hot spot detection and pattern analysis.

This module provides methods for identifying spatial clusters, hot spots,
and cold spots in geographic data.

© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC.

Classes
-------
GetisOrdGiStar : Getis-Ord Gi* hot spot analysis
LISAAnalysis : Local Indicators of Spatial Association

Functions
---------
spatial_scan : Kulldorff's spatial scan statistic

Examples
--------
>>> from krl_geospatial import analysis
>>> from krl_geospatial.weights import QueenWeights
>>>
>>> # Hot spot analysis
>>> w = QueenWeights()
>>> w.fit(gdf)
>>> gi_star = analysis.GetisOrdGiStar()
>>> gi_star.fit(gdf, w, 'crime_rate')
>>> hot_spots = gdf[gi_star.p_values < 0.05]
"""

from .hotspot import GetisOrdGiStar, spatial_scan
from .pattern import LISAAnalysis, moran_scatterplot

__all__ = [
    "GetisOrdGiStar",
    "spatial_scan",
    "LISAAnalysis",
    "moran_scatterplot",
]
