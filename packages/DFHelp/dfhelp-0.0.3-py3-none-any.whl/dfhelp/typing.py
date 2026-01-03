"""DFHelp type-hint definitions.

This module defines type-hints used throughout the package.
"""

from typing import TypeAlias

import polars._typing as plt


__all__ = [
    "PolarsDataType",
]


PolarsDataType: TypeAlias = plt.PolarsDataType
"""A data type compatible with Polars data types."""
