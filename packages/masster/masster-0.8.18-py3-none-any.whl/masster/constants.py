"""
constants.py - Mass Spectrometry Analysis Constants

This module defines commonly used constants for mass spectrometry data analysis.
These values are used throughout the masster package for various operations including
peak detection, alignment, tolerance calculations, and data processing.

All constants are documented with their physical meaning and typical use cases.
Adjust these values only when you understand their impact on analysis results.
"""

from __future__ import annotations

# ============================================================================
# Mass Spectrometry Tolerances
# ============================================================================

# Mass-to-charge ratio (m/z) tolerances in Daltons
# These tolerances define the acceptable deviation when matching peaks or features
MZ_TOLERANCE_TIGHT = 0.005  # High-resolution instruments (Orbitrap, Q-TOF)
MZ_TOLERANCE_DEFAULT = 0.01  # Standard tolerance for metabolomics
MZ_TOLERANCE_MEDIUM = 0.02  # Medium tolerance for lower resolution
MZ_TOLERANCE_WIDE = (
    0.04  # Wider tolerance for alignment or lower resolution instruments
)
MZ_TOLERANCE_VERY_WIDE = 0.05  # Very wide tolerance for LOWESS warping

# Retention time (RT) tolerances in seconds or minutes (context-dependent)
RT_TOLERANCE_TIGHT = 0.1  # Tight RT window for isotope detection
RT_TOLERANCE_DEFAULT = 10.0  # Standard RT tolerance for feature alignment
RT_TOLERANCE_CHROM = 6.0  # Chromatogram extraction window

# Parts-per-million (ppm) tolerances for high-resolution mass spectrometry
PPM_TOLERANCE_DEFAULT = 5  # Standard ppm tolerance
PPM_TOLERANCE_CALCULATED = 25  # Converted from Da (e.g., 0.01 Da / 400 m/z * 1e6)

# ============================================================================
# Peak Detection and Processing
# ============================================================================

# Maximum number of peaks to consider in various operations
# These limits prevent excessive memory usage and improve performance
MAX_PEAKS_CONSIDERED = 1000  # Maximum peaks for feature detection algorithms
MAX_POINTS_PER_SAMPLE = 10000  # Maximum data points per sample in visualizations

# Peak filtering thresholds
PEAK_TOP_N_LIMIT = 50  # Maximum number of top peaks to keep in baseline calculation

# Smoothing parameters for spectral processing
SMOOTHING_WINDOW_DEFAULT = 5  # Default Savitzky-Golay filter window size
SMOOTHING_DISTANCE = 5  # Minimum distance between peaks for local maxima
SMOOTHING_PROMINENCE_WINDOW = 30  # Window length for prominence calculation

# ============================================================================
# Spectrum Classification Thresholds
# ============================================================================

# Density thresholds for determining if spectrum is profile or centroided
# Density = number of data points per m/z unit
PROFILE_DENSITY_THRESHOLD = 100  # Above this = profile mode (high density)
CENTROIDED_DENSITY_THRESHOLD = 10  # Below this = centroided mode (low density)

# Median difference threshold for spectrum mode detection (m/z units)
CENTROIDED_MEDIAN_DIFF_THRESHOLD = 0.02  # Larger differences indicate centroided data

# ============================================================================
# Statistical and Analysis Parameters
# ============================================================================

# Quantile for baseline intensity calculation
BASELINE_QUANTILE = 0.001  # Use 0.1% quantile as baseline

# Sample size thresholds for quality control
MIN_FEATURES_PER_SAMPLE = 100  # Minimum features for quality sample
MAX_FEATURES_PER_SAMPLE = 1000  # Maximum features for quality sample (upper bound)
LARGE_SAMPLE_DELETE_THRESHOLD = 100  # Show warning when deleting many samples

# Test file selection for automated workflows
TEST_FILE_PERCENTAGE = 0.03  # Use 3% of files for test analysis

# ============================================================================
# Visualization Parameters
# ============================================================================

# Plot dimensions (pixels)
PLOT_WIDTH_DEFAULT = 1000  # Default plot width
PLOT_HEIGHT_DEFAULT = 250  # Default plot height for spectra

# Marker size scaling for 2D plots
MARKER_SIZE_SCALE_FACTOR = 0.0005  # Dynamic radius calculation factor

# Number formatting for tooltips
RT_FORMAT_DECIMALS = "0.00"  # 2 decimal places for retention time
MZ_FORMAT_DECIMALS = "0.0000"  # 4 decimal places for m/z values

# ============================================================================
# Numerical Constants
# ============================================================================

# Small epsilon for numerical stability
EPSILON = 1e-9  # Avoid log(0) and division by zero

# Peak refinement exponent for weighted centroid calculation
PEAK_WEIGHT_EXPONENT = 3  # Use intensity^3 for peak position refinement

# ============================================================================
# Usage Notes
# ============================================================================
# Common usage patterns:
#
# 1. Feature alignment:
#    study.align(rt_tol=RT_TOLERANCE_DEFAULT, mz_tol=MZ_TOLERANCE_DEFAULT)
#
# 2. Peak detection:
#    sample.find_features(noise_threshold=1000, max_peaks=MAX_PEAKS_CONSIDERED)
#
# 3. Isotope detection:
#    study.find_iso(rt_tol=RT_TOLERANCE_TIGHT, mz_tol=MZ_TOLERANCE_DEFAULT)
#
# 4. Chromatogram extraction:
#    sample.chrom_extract(rt_tol=RT_TOLERANCE_CHROM, mz_tol=MZ_TOLERANCE_TIGHT)
#
# To override a constant for a specific analysis:
#    # Don't modify this file - pass custom values to functions
#    sample.find_features(noise_threshold=2000)  # Custom threshold
