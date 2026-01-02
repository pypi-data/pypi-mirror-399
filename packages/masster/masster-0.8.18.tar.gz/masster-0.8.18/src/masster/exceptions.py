"""
Custom exceptions for the masster package.

This module defines a hierarchy of exceptions that provide clear,
actionable error messages for common failure scenarios in mass
spectrometry data analysis.
"""

from __future__ import annotations


class MassterError(Exception):
    """Base exception for all masster-specific errors.

    All custom exceptions in masster inherit from this base class,
    allowing users to catch all masster-related errors with a single
    except clause if needed.

    Examples
    --------
    >>> try:
    ...     # masster operation
    ...     pass
    ... except MassterError as e:
    ...     print(f"Masster error: {e}")
    """


class DataValidationError(MassterError):
    """Raised when input data fails validation checks.

    This exception is raised when data is corrupted, has unexpected
    format, or contains invalid values that prevent processing.

    Examples
    --------
    >>> raise DataValidationError("RT values must be positive")
    """


class FileFormatError(MassterError):
    """Raised when a file format is unsupported or incorrectly formatted.

    This exception indicates issues with file format detection or
    parsing, such as unsupported vendor formats or corrupted mzML files.

    Examples
    --------
    >>> raise FileFormatError(
    ...     "Unsupported file format: .xyz\\n"
    ...     "Supported formats: .raw (Thermo), .wiff (SCIEX), .mzML"
    ... )
    """


class ProcessingError(MassterError):
    """Raised when an error occurs during data processing.

    This exception covers errors during feature detection, alignment,
    merging, integration, or other processing steps.

    Examples
    --------
    >>> raise ProcessingError(
    ...     "Feature detection failed: no peaks found\\n"
    ...     "Try adjusting noise_threshold or min_intensity parameters"
    ... )
    """


class ConfigurationError(MassterError):
    """Raised when configuration or parameters are invalid.

    This exception is raised for invalid parameter values, incompatible
    parameter combinations, or missing required configuration.

    Examples
    --------
    >>> raise ConfigurationError(
    ...     "Invalid polarity: 'neutral'\\n"
    ...     "Must be one of: 'positive', 'negative'"
    ... )
    """


class InvalidPolarityError(ConfigurationError):
    """Raised when an invalid polarity value is provided.

    Polarity must be one of: 'positive', 'negative'.

    Examples
    --------
    >>> raise InvalidPolarityError(
    ...     "polarity='neutral' is not valid\\n"
    ...     "Expected: 'positive' or 'negative'"
    ... )
    """


class SampleNotFoundError(MassterError):
    """Raised when a referenced sample cannot be found.

    This exception is raised when trying to access a sample by ID or
    name that doesn't exist in the study or filesystem.

    Examples
    --------
    >>> raise SampleNotFoundError(
    ...     "Sample 'sample_001.mzML' not found in study\\n"
    ...     "Available samples: sample_002.mzML, sample_003.mzML"
    ... )
    """


class FeatureNotFoundError(MassterError):
    """Raised when a referenced feature cannot be found.

    This exception is raised when trying to access a feature by ID
    that doesn't exist in the feature table.

    Examples
    --------
    >>> raise FeatureNotFoundError(
    ...     "Feature ID 12345 not found\\n"
    ...     "Valid feature IDs range: 1-1000"
    ... )
    """


class AlignmentError(ProcessingError):
    """Raised when retention time alignment fails.

    This exception indicates issues during RT alignment such as
    insufficient anchor points or incompatible sample data.

    Examples
    --------
    >>> raise AlignmentError(
    ...     "Alignment failed: only 2 anchor points found\\n"
    ...     "Minimum required: 5. Try increasing rt_tol parameter"
    ... )
    """


class MergeError(ProcessingError):
    """Raised when feature merging across samples fails.

    This exception is raised during consensus feature generation when
    samples cannot be merged due to incompatible data or parameters.

    Examples
    --------
    >>> raise MergeError(
    ...     "Cannot merge samples with different polarities\\n"
    ...     "Found: positive (2 samples), negative (3 samples)"
    ... )
    """


class LibraryError(MassterError):
    """Raised when compound library operations fail.

    This exception covers errors in loading, parsing, or searching
    compound libraries for identification.

    Examples
    --------
    >>> raise LibraryError(
    ...     "Library file 'compounds.json' is corrupted\\n"
    ...     "Expected JSON format with 'name', 'formula', 'mz' fields"
    ... )
    """


class QuantificationError(ProcessingError):
    """Raised when quantification or integration fails.

    This exception is raised when EIC extraction, peak integration,
    or quantification calculations encounter errors.

    Examples
    --------
    >>> raise QuantificationError(
    ...     "Integration failed for feature 123: no data in RT range\\n"
    ...     "RT range: 45.2-45.8s, but sample RT range: 0-40s"
    ... )
    """


class MemoryError(MassterError):
    """Raised when operations would exceed available memory.

    This exception is raised when estimated memory usage for an
    operation exceeds system limits or configured thresholds.

    Note: This shadows the built-in MemoryError but provides more
    context-specific handling for masster operations.

    Examples
    --------
    >>> raise MemoryError(
    ...     "Estimated memory usage (128 GB) exceeds available (64 GB)\\n"
    ...     "Try: enable chunking, reduce ncores, or process in batches"
    ... )
    """


class DependencyError(MassterError):
    """Raised when required dependencies are missing or incompatible.

    This exception is raised when optional dependencies required for
    specific functionality are not installed or have incompatible versions.

    Examples
    --------
    >>> raise DependencyError(
    ...     "pyopenms is required for feature detection\\n"
    ...     "Install with: pip install pyopenms>=3.3.0"
    ... )
    """
