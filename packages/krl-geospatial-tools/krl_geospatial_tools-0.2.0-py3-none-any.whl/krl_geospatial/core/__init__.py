# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: LicenseRef-Proprietary

"""Core module exports."""

from krl_geospatial.core.base import (
    BaseGeospatialAnalyzer,
    GeospatialResult,
    SpatialDataFrame,
    SpatialResult,
    create_geodataframe,
)

__all__ = [
    "BaseGeospatialAnalyzer",
    "SpatialResult",
    "GeospatialResult",
    "SpatialDataFrame",
    "create_geodataframe",
]
