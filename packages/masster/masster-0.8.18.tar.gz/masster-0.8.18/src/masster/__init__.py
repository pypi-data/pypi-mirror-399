"""
masster - Mass Spectrometry Analysis Assistant

A comprehensive Python package for processing and analyzing untargeted metabolomics data,
supporting both DDA (Data-Dependent Acquisition) and DIA (Data-Independent Acquisition)
mass spectrometry workflows.
"""

from __future__ import annotations

from typing import Any
import warnings

# Suppress pyOpenMS environment variable warnings globally
warnings.filterwarnings("ignore", message=".*OPENMS_DATA_PATH.*", category=UserWarning)
warnings.filterwarnings(
    "ignore",
    message="Warning: OPENMS_DATA_PATH.*",
    category=UserWarning,
)

from masster import constants  # Mass spectrometry analysis constants
from masster._version import __version__

# from masster._version import get_version
from masster.chromatogram import Chromatogram
from masster.exceptions import (
    AlignmentError,
    ConfigurationError,
    DataValidationError,
    DependencyError,
    FeatureNotFoundError,
    FileFormatError,
    InvalidPolarityError,
    LibraryError,
    MassterError,
    MergeError,
    ProcessingError,
    QuantificationError,
    SampleNotFoundError,
)
from masster.lib import Lib
from masster.sample.sample import Sample
from masster.spectrum import Spectrum
from masster.study.study import Study
from masster.wizard import Wizard


def is_null_value(val: Any) -> bool:
    """Check if a value is None or NaN without pandas dependency.

    Args:
        val (Any): Any scalar value to check.

    Returns:
        bool: True if value is None or NaN, False otherwise.
    """
    if val is None:
        return True
    if isinstance(val, float):
        return val != val  # NaN check (NaN != NaN is True)
    return False


__all__ = [
    "AlignmentError",
    "Chromatogram",
    "ConfigurationError",
    "DataValidationError",
    "DependencyError",
    "FeatureNotFoundError",
    "FileFormatError",
    "InvalidPolarityError",
    "Lib",
    "LibraryError",
    "MassterError",
    "MemoryError",
    "MergeError",
    "ProcessingError",
    "QuantificationError",
    "Sample",
    "SampleNotFoundError",
    "Spectrum",
    "Study",
    "Wizard",
    "__version__",
    "constants",
    "is_null_value",
]
