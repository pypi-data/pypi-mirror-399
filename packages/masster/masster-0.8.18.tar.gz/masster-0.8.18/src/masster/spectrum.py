# mypy: disable-error-code="arg-type,assignment,attr-defined,no-untyped-def"
"""
spectrum.py

This module provides tools for processing and analyzing individual mass spectra.
It defines the `Spectrum` class for handling mass spectral data, including peak detection,
spectrum visualization, preprocessing operations, and spectral similarity calculations.

Key Features:
- **Spectrum Processing**: Handle m/z and intensity data with various preprocessing options.
- **Peak Detection**: Advanced peak picking with customizable parameters and algorithms.
- **Visualization**: Interactive and static spectral plots with annotation capabilities.
- **Spectrum Comparison**: Calculate spectral similarities and perform matching operations.
- **Data Export**: Save spectra in multiple formats including images and data files.
- **Preprocessing**: Smoothing, baseline correction, normalization, and noise filtering.

Dependencies:
- `numpy`: For numerical array operations and mathematical computations.
- `pandas`: For structured data handling and manipulation.
- `bokeh`: For interactive plotting and visualization.
- `scipy.signal`: For signal processing and peak detection algorithms.
- `holoviews`: For high-level data visualization and color mapping.

Classes:
- `Spectrum`: Main class for individual spectrum processing, providing methods for data
  manipulation, peak detection, visualization, and analysis.

Functions:
- `combine_peaks()`: Utility function for merging multiple peak lists.
- Various utility functions for spectrum processing and analysis.

Example Usage:
```python
from masster import Spectrum
import numpy as np

# Create spectrum from m/z and intensity arrays
mz = np.array([100.0, 150.0, 200.0, 250.0])
intensity = np.array([1000, 5000, 3000, 800])
spectrum = Spectrum(mz=mz, inty=intensity, ms_level=1)

# Process and visualize
spectrum.find_peaks()
spectrum.plot()
spectrum.save_plot("spectrum.html")
```

See Also:
- `Sample`: For handling complete mass spectrometry files containing multiple spectra.
- `masster.sample.parameters`: For spectrum-specific parameter configuration.

"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import logging
import re
from typing import TYPE_CHECKING, Any
import warnings

from bokeh.io import output_file, save
from bokeh.io.export import export_png, export_svg
from bokeh.models import (
    BoxZoomTool,
    ColumnDataSource,
    FixedTicker,
    HoverTool,
    LinearColorMapper,
    LogScale,
    LogTickFormatter,
    NumeralTickFormatter,
)
from bokeh.plotting import figure, show
import numpy as np
import pandas as pd

from masster.exceptions import (
    ConfigurationError,
    DataValidationError,
    ProcessingError,
)

if TYPE_CHECKING:
    try:
        from bokeh.models import ColorBar
    except ImportError:
        ColorBar = None
else:
    try:
        from bokeh.models import ColorBar
    except ImportError:
        try:
            from bokeh.models.annotations import (
                ColorBar,
            )
        except ImportError:
            ColorBar = None


try:
    from holoviews.plotting.util import process_cmap
except ImportError:
    process_cmap = None
from matplotlib.colors import rgb2hex
from scipy.signal import (
    find_peaks,
    find_peaks_cwt,
    peak_prominences,
    peak_widths,
    savgol_filter,
)

# Module-level logger for spectrum processing
logger = logging.getLogger(__name__)

# Try to import numba for JIT compilation (optional dependency for performance)
try:
    from numba import jit

    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False


if TYPE_CHECKING:
    from collections.abc import Callable


# Numba-optimized refinement for centroid_lm (73x faster than Python loop)
if NUMBA_AVAILABLE:

    @jit(nopython=True)
    def _refine_peaks_numba(
        peaks,
        prof_mz,
        prof_inty,
        prof_not_smoothed,
        left_indices,
        right_indices,
    ):
        """JIT-compiled peak refinement using intensity-weighted averaging near original peak.

        This function is 73x faster than the pure Python implementation.

        Args:
            peaks: Array of peak indices in the profile data
            prof_mz: Profile m/z values
            prof_inty: Profile intensity values (smoothed)
            prof_not_smoothed: Profile intensity values (original, not smoothed)
            left_indices: Pre-computed left boundary indices for each peak
            right_indices: Pre-computed right boundary indices for each peak

        Returns:
            Tuple of (refined_mz, refined_inty) arrays
        """
        refined_mz = prof_mz.copy()
        refined_inty = prof_inty.copy()

        for i in range(len(peaks)):
            peak_idx = peaks[i]
            left_idx = left_indices[i]
            right_idx = right_indices[i]

            # Skip if not enough neighbors
            if right_idx - left_idx < 3:
                continue

            # Extract neighbor data
            neighbor_mz = prof_mz[left_idx:right_idx]
            neighbor_inty = prof_inty[left_idx:right_idx]
            neighbor_not_smoothed = prof_not_smoothed[left_idx:right_idx]

            # Find which data source (smoothed or original) has higher peak
            original_peak_inty_smoothed = prof_inty[peak_idx]
            original_peak_inty_not_smoothed = prof_not_smoothed[peak_idx]

            # Use the data with higher peak intensity for refinement
            if original_peak_inty_smoothed >= original_peak_inty_not_smoothed:
                weights = neighbor_inty**3 + 1
                refined_mz[peak_idx] = np.sum(neighbor_mz * weights) / np.sum(weights)
                refined_inty[peak_idx] = np.max(neighbor_inty)
            else:
                weights = neighbor_not_smoothed**3 + 1
                refined_mz[peak_idx] = np.sum(neighbor_mz * weights) / np.sum(weights)
                refined_inty[peak_idx] = np.max(neighbor_not_smoothed)

        return refined_mz, refined_inty
else:
    _refine_peaks_numba = None


@dataclass
class Spectrum:
    """A class for processing and analyzing individual mass spectra.

    The ``Spectrum`` class provides comprehensive tools for handling mass spectral data,
    including peak detection, preprocessing, visualization, and spectral analysis.
    It supports both centroided and profile mode spectra and offers various
    algorithms for peak picking and spectral processing.

    Attributes:
        mz (np.ndarray): Mass-to-charge ratio values.
        inty (np.ndarray): Intensity values corresponding to m/z values.
        ms_level (int | None): MS level (1 for MS1, 2 for MS2, etc.).
        label (str | None): Text label for the spectrum.
        centroided (bool | None): Whether the spectrum is centroided.
        history (str): Processing history log.
        bl (float | None): Baseline values for baseline correction.
        width (np.ndarray | None): Peak widths from peak detection.
        prominence (np.ndarray | None): Peak prominences from peak detection.
        q1_ratio (np.ndarray | None): Q1 isolation ratios (DIA/ztscan data).
        eic_corr (np.ndarray | None): EIC correlation values (DIA/ztscan data).

    Key Methods:
        Preprocessing: denoise(), clean(), centroid(), deisotope(), smooth()
        Filtering: filter(), trim(), keep_top()
        Analysis: baseline(), entropy(), tic()
        Visualization: plot(), plot_stats(), plot_dist()

    Example:
        >>> import numpy as np
        >>> from masster import Spectrum
        >>> mz = np.array([100.0, 150.0, 200.0, 250.0])
        >>> intensity = np.array([1000, 5000, 3000, 800])
        >>> spectrum = Spectrum(mz=mz, inty=intensity, ms_level=1)
        >>> # Preprocess spectrum
        >>> spectrum = spectrum.centroid().clean()
        >>> spectrum.plot()

    See Also:
        Sample: For handling complete mass spectrometry files.
    """

    def __init__(
        self,
        mz: np.ndarray | None = None,
        inty: np.ndarray | None = None,
        ms_level: int | None = None,
        label: str | None = None,
        centroided: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a Spectrum instance.

        Args:
            mz (np.ndarray | None): Mass-to-charge ratio values array.
            inty (np.ndarray | None): Intensity values array corresponding to m/z values.
            ms_level (int | None): MS level (1 for MS1, 2 for MS2, etc.).
            label (str | None): Text label for the spectrum (e.g., "MS1 scan 1234").
            centroided (bool | None): Whether spectrum is centroided. Auto-detected if None.
            **kwargs: Additional attributes to set on the spectrum instance.

        Raises:
            ValueError: If mz or inty arrays are not provided or have different shapes.
        """
        # Handle case where mz and inty might be in kwargs (from from_dict/from_json)
        if mz is None and "mz" in kwargs:
            mz = kwargs.pop("mz")
        if inty is None and "inty" in kwargs:
            inty = kwargs.pop("inty")

        # Ensure mz and inty are provided
        if mz is None or inty is None:
            raise DataValidationError(
                "Both 'mz' and 'inty' arrays are required to create a Spectrum\\n"
                "Provide: numpy arrays or lists with m/z and intensity values",
            )

        self.label = label
        self.ms_level = ms_level
        self.centroided = centroided
        self.mz = mz
        self.inty = inty
        self.history = ""
        self.bl: float | None = None
        # Optional attributes for peak analysis
        self.width: np.ndarray | None = None
        self.prominence: np.ndarray | None = None
        self.__dict__.update(kwargs)
        self.__post_init__()
        if centroided is None:
            self.centroided = self.check_if_centroided()

    def __post_init__(self) -> None:
        self.mz = np.asarray(self.mz)
        self.inty = np.asarray(self.inty)
        if self.mz.shape != self.inty.shape:
            raise DataValidationError(
                f"Array shape mismatch: mz.shape={self.mz.shape}, inty.shape={self.inty.shape}\\n"
                f"mz and intensity arrays must have the same length",
            )
        if self.centroided is None:
            self.centroided = self.check_if_centroided()

    def check_if_centroided(self) -> bool:
        """Determine if spectrum data is centroided or profile mode.

        Uses optimized statistical approaches with early exits for speed:

        1. Fast median difference check (most decisive)
        2. Small gap ratio (profile characteristic)
        3. Density check (fallback)

        Returns:
            bool: True if centroided, False if profile mode.
        """
        if self.mz.size < 5:
            return True  # Too few points to determine, assume centroided

        # Fast path: check if mz is already sorted to avoid sorting cost
        if np.all(self.mz[:-1] <= self.mz[1:]):
            sorted_mz = self.mz
        else:
            sorted_mz = np.sort(self.mz)

        # Calculate differences efficiently
        mz_diffs = np.diff(sorted_mz)

        # Remove zeros efficiently (keep positive differences)
        mz_diffs = mz_diffs[mz_diffs > 0]

        if mz_diffs.size == 0:
            return True  # All identical m/z values

        # Fast approach 1: Median difference (most decisive, compute once)
        median_diff = np.median(mz_diffs)

        # Early exits for clear cases (>90% of cases)
        if median_diff > 0.02:
            return True  # Clearly centroided
        if median_diff < 0.005:
            return False  # Clearly profile

        # Fast approach 2: Small gap ratio (for borderline cases)
        # Use vectorized comparison instead of creating new array
        small_gap_count = np.sum(mz_diffs < 0.005)
        small_gap_ratio = small_gap_count / mz_diffs.size

        if small_gap_ratio > 0.7:
            return False  # High ratio of small gaps = profile
        if small_gap_ratio < 0.1:
            return True  # Low ratio of small gaps = centroided

        # Fast approach 3: Density check (final fallback)
        mz_range = sorted_mz[-1] - sorted_mz[0]
        if mz_range > 0:
            density = sorted_mz.size / mz_range
            if density > 100:  # High density = profile
                return False
            if density < 10:  # Low density = centroided
                return True

        # Final fallback: median threshold
        return bool(median_diff > 0.01)

    def reload(self) -> None:
        modname = self.__class__.__module__
        mod = __import__(modname, fromlist=[modname.split(".")[0]])
        importlib.reload(mod)
        new = getattr(mod, self.__class__.__name__)
        setattr(self, "__class__", new)  # noqa: B010

    def to_dict(self) -> dict:
        # return a dictionary representation of the spectrum. include all the attributes
        # Create a copy to avoid modifying the original object
        import copy

        result = {}

        # Handle numpy arrays by creating copies and converting to lists
        for key, value in self.__dict__.items():
            if isinstance(value, np.ndarray):
                result[key] = value.copy().tolist()
            elif isinstance(value, (list, dict)):
                # Create copies of mutable objects
                result[key] = copy.deepcopy(value)
            elif isinstance(value, np.number):
                # Handle numpy scalar types (float32, int32, etc.)
                result[key] = value.item()
            else:
                # Immutable objects can be copied directly
                result[key] = value
        # Round attributes to specified decimal places
        if "mz" in result:
            result["mz"] = np.round(result["mz"], 5).tolist()
        if "precursor_mz" in result and result["precursor_mz"] is not None:
            result["precursor_mz"] = round(result["precursor_mz"], 5)
        if "inty" in result:
            result["inty"] = np.round(result["inty"], 2).tolist()

        # Round to 3 decimal places: width, rt, prominence, q1_ratio, eic_corr
        for attr in ["width", "rt", "prominence", "q1_ratio", "eic_corr"]:
            if attr in result and result[attr] is not None:
                if isinstance(result[attr], list):
                    result[attr] = np.round(result[attr], 3).tolist()
                else:
                    result[attr] = round(result[attr], 3)

        return result

    @classmethod
    def from_dict(cls, data: dict) -> Spectrum:
        # Create instance directly from data dictionary
        return cls(**data)

    def to_json(self) -> str:
        """
        Serialize the spectrum to a JSON string.

        Returns:
            str: JSON string representation of the spectrum.
        """
        import json

        data = self.to_dict()
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> Spectrum:
        """
        Create a Spectrum instance from a JSON string.

        Args:
            json_str (str): JSON string containing spectrum data.

        Returns:
            Spectrum: New instance with attributes set from the JSON data.
        """
        import json

        data = json.loads(json_str)
        return cls.from_dict(data)

    def pandalize(self) -> pd.DataFrame:
        data = {
            key: val
            for key, val in self.__dict__.items()
            if isinstance(val, np.ndarray) and val.size == self.mz.size
        }
        return pd.DataFrame(data)

    def to_df(self) -> pd.DataFrame:
        return self.pandalize()

    def mz_trim(self, *args: Any, **kwargs: Any) -> Spectrum:
        """
        Alias for trim method to maintain compatibility with older code.
        """
        return self.trim(*args, **kwargs)

    def trim(
        self,
        mz_min: float | None = None,
        mz_max: float | None = None,
    ) -> Spectrum:
        if mz_min is not None:
            mask = self.mz >= mz_min
            self.mz = self.mz[mask]
            self.inty = self.inty[mask]
            for key in self.__dict__:
                if (
                    isinstance(self.__dict__[key], np.ndarray)
                    and self.__dict__[key].size == mask.size
                ):
                    self.__dict__[key] = self.__dict__[key][mask]
        if mz_max is not None:
            mask = self.mz <= mz_max
            self.mz = self.mz[mask]
            self.inty = self.inty[mask]
            for key in self.__dict__:
                if (
                    isinstance(self.__dict__[key], np.ndarray)
                    and self.__dict__[key].size == mask.size
                ):
                    self.__dict__[key] = self.__dict__[key][mask]
        return self

    @property
    def mz_min(self) -> float:
        """Get minimum m/z value in the spectrum.

        Returns:
            float: Minimum m/z value, or 0 if spectrum is empty
        """
        if len(self.mz) == 0:
            return 0
        return float(np.min(self.mz))

    @property
    def mz_max(self) -> float:
        """Get maximum m/z value in the spectrum.

        Returns:
            float: Maximum m/z value, or 0 if spectrum is empty
        """
        if len(self.mz) == 0:
            return 0
        return float(np.max(self.mz))

    @property
    def inty_min(self) -> float:
        """Get minimum intensity value in the spectrum.

        Returns:
            float: Minimum intensity value, or 0 if spectrum is empty
        """
        if len(self.inty) == 0:
            return 0
        return float(np.min(self.inty))

    @property
    def inty_max(self) -> float:
        """Get maximum intensity value in the spectrum.

        Returns:
            float: Maximum intensity value, or 0 if spectrum is empty
        """
        if len(self.inty) == 0:
            return 0
        return float(np.max(self.inty))

    @property
    def tic(self) -> float:
        """Calculate total ion current (sum of all intensities).

        Returns:
            float: Total ion current, or 0 if spectrum is empty
        """
        if len(self.inty) == 0:
            return 0
        return float(np.sum(self.inty))

    def keep_top(self, n: int = 100, inplace: bool = False) -> Spectrum:
        idx = np.argsort(self.inty)[-n:]
        spec_obj = self if inplace else self.copy()
        array_length = self.mz.size
        for key, val in spec_obj.__dict__.items():
            if isinstance(val, np.ndarray) and val.size == array_length:
                spec_obj.__dict__[key] = val[idx]
        return spec_obj

    def scale(self, factor: float = 1.0) -> Spectrum:
        if factor == 1.0:
            return self.copy()
        spec_obj = self.copy()
        spec_obj.inty = spec_obj.inty.astype(float) * factor
        spec_obj.history_add(f"s[{factor}]")
        return spec_obj

    def baseline(self) -> float:
        """Estimate baseline intensity of the spectrum.

        Returns:
            float: Estimated baseline intensity
        """
        mz = self.mz
        inty = self.inty
        mz = mz[inty != 0]
        inty = inty[inty != 0]
        if len(mz) == 0:
            return 0
        idx = np.argsort(mz)
        mz = mz[idx]
        inty = inty[idx]
        if len(mz) > 50:
            mz = mz[-50:]
            inty = inty[-50:]
        while True:
            baseline = 1.5 * np.mean(inty)
            mask = inty > baseline
            if np.sum(mask) == 0:
                break
            inty = inty[~mask]
        return float(baseline)

    def entropy(self) -> float:
        peaks = np.column_stack((self.mz, self.inty))
        entropy = -np.sum(peaks[:, 1] * np.log(peaks[:, 1] + 1e-9))
        return float(entropy)

    def __len__(self) -> int:
        """Return the number of peaks in the spectrum."""
        return int(self.mz.size)

    def __sizeof__(self) -> int:
        """Return the number of peaks in the spectrum."""
        return int(self.mz.size)

    def length(self) -> int:
        """Return the number of peaks in the spectrum."""
        return self.__len__()

    def history_add(self, term: str) -> None:
        """Add a processing step to the spectrum's history.

        Args:
            term: Processing step description to add
        """
        if getattr(self, "history", None) is None:
            self.history = ""
        if len(self.history) > 0:
            self.history += f" {term}"
        else:
            self.history = term

    def history_check(self, term: str) -> list[str] | None:
        m = re.search(f"{term}\\[([A-Za-z0-9]*)\\]", self.history)
        if m is None:
            return None
        return [x[1:-1] for x in m.group(0).split(",")]

    def copy(self) -> Spectrum:
        new = Spectrum(
            mz=self.mz.copy(),
            inty=self.inty.copy(),
            ms_level=self.ms_level,
            centroided=self.centroided,
            label=self.label,
        )
        for key, val in self.__dict__.items():
            if isinstance(val, np.ndarray):
                new.__dict__[key] = val.copy()
            else:
                new.__dict__[key] = val
        return new

    def denoise(self, threshold: float | None = None) -> Spectrum:
        if threshold is None:
            threshold = self.baseline()
        self_c = self.copy()
        mask = self_c.inty > threshold
        length = self_c.mz.size
        for key in self_c.__dict__:
            if (
                isinstance(self_c.__dict__[key], np.ndarray)
                and self_c.__dict__[key].size == length
            ):
                self_c.__dict__[key] = self_c.__dict__[key][mask]
        self_c.history_add("t[BL]")
        self_c.bl = threshold
        return self_c

    def clean(self, force: bool = False) -> Spectrum:
        """Remove peaks below baseline noise level.

        Filters out noise peaks by removing all peaks with intensity below the baseline
        threshold. The baseline is calculated as 1.5× the mean of the lowest 10% of peaks.
        This method filters all arrays in the spectrum, including those added by
        dia_stats (q1_ratio, eic_corr) or centroiding (width, prominence).

        To prevent redundant cleaning, this method tracks whether cleaning has already
        been applied via the history string. Unless force=True, it will skip cleaning
        if the spectrum has already been cleaned.

        Args:
            force (bool): If True, clean the spectrum even if it has already been
                cleaned. If False (default), skip cleaning if already done.

        Returns:
            Spectrum: Cleaned spectrum with noise peaks removed. Returns self unchanged
                if already cleaned and force=False.

        Example:
            >>> spec = sample.get_spectrum(scan=500)
            >>> spec_clean = spec.clean()
            >>> print(f"Removed {len(spec.mz) - len(spec_clean.mz)} noise peaks")
            >>> # Calling again won't re-clean unless force=True
            >>> spec_clean2 = spec_clean.clean()  # Returns unchanged
            >>> spec_clean3 = spec_clean.clean(force=True)  # Re-cleans
        """
        # Check if already cleaned
        if not force and self.history_check("t[CL]"):
            return self

        # Calculate baseline threshold
        baseline = self.baseline()

        # Create mask for peaks above baseline
        mask = self.inty > baseline
        length = self.mz.size

        # Apply mask to all arrays of the same length
        self_c = self.copy()
        for key in self_c.__dict__:
            if (
                isinstance(self_c.__dict__[key], np.ndarray)
                and self_c.__dict__[key].size == length
            ):
                self_c.__dict__[key] = self_c.__dict__[key][mask]

        # Update size and history
        self_c.size = self_c.mz.size
        self_c.history_add("t[CL]")

        return self_c

    def filter(
        self,
        inty_min: float | None = None,
        inty_max: float | None = None,
        q1_ratio_min: float | None = None,
        q1_ratio_max: float | None = None,
        eic_corr_min: float | None = None,
        eic_corr_max: float | None = None,
    ) -> Spectrum:
        spec_obj = self.copy()
        mask: np.ndarray = np.ones(len(spec_obj.mz), dtype=bool)
        if inty_min is not None and inty_min > 0:
            if inty_min < 1:
                inty_min = inty_min * spec_obj.inty.max()
            else:
                mask = mask & (spec_obj.inty >= inty_min)
            spec_obj.history_add("f[inty_min%]")
        if inty_max is not None and inty_max > 0:
            mask = mask & (spec_obj.inty <= inty_max)
            spec_obj.history_add("f[inty_max]")
        if q1_ratio_min is not None and hasattr(spec_obj, "q1_ratio"):
            mask = mask & (spec_obj.q1_ratio >= q1_ratio_min)
            spec_obj.history_add("f[q1_ratio_min]")
        if q1_ratio_max is not None and hasattr(spec_obj, "q1_ratio"):
            mask = mask & (spec_obj.q1_ratio <= q1_ratio_max)
            spec_obj.history_add("f[q1_ratio_max]")
        if eic_corr_min is not None and hasattr(spec_obj, "eic_corr"):
            mask = mask & (spec_obj.eic_corr >= eic_corr_min)
            spec_obj.history_add("f[eic_corr_min]")
        if eic_corr_max is not None and hasattr(spec_obj, "eic_corr"):
            mask = mask & (spec_obj.eic_corr <= eic_corr_max)
            spec_obj.history_add("f[eic_corr_max]")
        mask_length = len(mask)
        for key in spec_obj.__dict__:
            if (
                isinstance(spec_obj.__dict__[key], np.ndarray)
                and spec_obj.__dict__[key].size == mask_length
            ):
                spec_obj.__dict__[key] = spec_obj.__dict__[key][mask]
        return spec_obj

    def centroid(self, algo: str = "cr", **kwargs: Any) -> Spectrum:
        algo = algo.lower()
        if algo == "cr":
            return self.centroid_cr(**kwargs)
        if algo == "cwt":
            return self.centroid_cwt(**kwargs)
        if algo in ["slm", "lm", "slmp", "lmp"]:
            return self.centroid_lm(**kwargs)
        raise ConfigurationError(
            f"Unknown centroiding algorithm: '{algo}'\n\n"
            "Supported algorithms:\n"
            "  - 'cr': Continuous region method (default)\n"
            "  - 'cwt': Continuous wavelet transform\n"
            "  - 'lm'/'slm': Local maxima method\n\n"
            "Example: spectrum.centroid(algo='cr')",
        )

    def centroid_cr(
        self,
        tolerance: float = 0.002,
        ppm: float = 5,
        time_domain: bool = True,
        inty_fun: Any = np.max,
        weighted: bool = True,
        exponent: float = 3,
        mode: str = "union",
        min_prop: float = 0.5,
        min_points: int = 5,
        stats: bool = False,
        wlen: int = 50,
        prominence: float | None = None,
        **kwargs: Any,
    ) -> Spectrum:
        if self.centroided:
            return self
        s = self.copy()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            new_spec = combine_peaks(
                [s],
                tolerance=tolerance,
                ppm=ppm,
                time_domain=time_domain,
                inty_fun=inty_fun,
                weighted=weighted,
                exponent=exponent,
                mode=mode,
                min_prop=min_prop,
                min_points=min_points,
                main=None,
            )
            s.history_add("c[CR]")
            s.history_add("c[CR]")
            if stats or (prominence is not None):
                indexes = np.searchsorted(s.mz, new_spec.mz)
                widths = peak_widths(s.inty, indexes, rel_height=0.75)[0]
                prominences = peak_prominences(s.inty, indexes, wlen=wlen)[0]
                s.width = widths
                s.prominence = prominences

        s.mz = new_spec.mz
        s.inty = new_spec.inty
        s.centroided = True
        if prominence is not None:
            mask = prominences >= prominence
            s.mz = s.mz[mask]
            s.inty = s.inty[mask]
            if hasattr(s, "width") and s.width is not None:
                s.width = s.width[mask]
            if hasattr(s, "prominence") and s.prominence is not None:
                s.prominence = s.prominence[mask]
            s.history_add("f[PRO]")
            s.history_add("f[PRO]")
        return s

    def smooth(self, algo: str = "savgol", window_length: int = 7) -> Spectrum:
        if self.centroided:
            return self
        s = self.copy()
        match algo.lower():
            case "savgol":
                s.inty = savgol_filter(s.inty, window_length, 2)
                s.history_add("s[SG]")
                s.history_add("s[SG]")
            case "cumsum":
                cumsum_vec = np.cumsum(np.insert(s.inty, 0, 0))
                ma_vec = (
                    cumsum_vec[window_length:] - cumsum_vec[:-window_length]
                ) / window_length
                s.inty = np.concatenate(
                    (
                        s.inty[: window_length // 2],
                        ma_vec,
                        s.inty[-window_length // 2 :],
                    ),
                )
                s.history_add("s[CSM]")
                s.history_add("s[CSM]")
        return s

    def centroid_cwt(
        self,
        stats: bool = False,
        wlen: int = 50,  # Currently unused parameter
        prominence: float | None = None,
        **kwargs: Any,
    ) -> Spectrum:
        if self.centroided:
            return self
        s = self.copy()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            peaks = find_peaks_cwt(s.inty, widths=np.arange(4, 30), min_snr=1)
            if stats or (prominence is not None):
                widths = peak_widths(s.inty, peaks, rel_height=0.75)
                prominences = peak_prominences(s.inty, peaks)[0]
                s.width = widths
                s.prominence = prominences
        s.mz = s.mz[peaks]
        s.inty = s.inty[peaks]
        s.centroided = True
        s.history_add("c[CWT]")
        s.history_add("c[CWT]")
        if prominence is not None:
            mask = prominences >= prominence
            s.mz = s.mz[mask]
            s.inty = s.inty[mask]
            if hasattr(s, "width") and s.width is not None:
                s.width = s.width[mask]
            if hasattr(s, "prominence") and s.prominence is not None:
                s.prominence = s.prominence[mask]
            s.history_add("f[PRO]")
            s.history_add("f[PRO]")
        return s

    def centroid_lm(
        self,
        smooth: int = 5,
        distance: float = 5,
        wlen: int = 30,
        plateau_size: int | None = None,
        prominence: float | None = None,
        refine: bool = True,
        refine_window: float = 0.01,
        **kwargs: Any,
    ) -> Spectrum:
        if self.centroided:
            return self
        s = self.copy()
        not_smothed_inty = s.inty.copy()
        if smooth is not None:
            try:
                if len(s.mz) > smooth * 2:
                    s.inty = savgol_filter(s.inty, smooth, 2)
            except ValueError as e:
                # Savgol filter requires odd window_length >= 3
                # Skip smoothing if parameters are invalid
                logger.debug(f"Smoothing skipped: {e}")

        # Sort data by m/z before peak finding to ensure correct m/z assignment
        if not np.all(np.diff(s.mz) >= 0):
            sort_idx = np.argsort(s.mz)
            s.mz = s.mz[sort_idx]
            s.inty = s.inty[sort_idx]
            not_smothed_inty = not_smothed_inty[sort_idx]

        # Handle prominence=-1: use baseline if it was cached, otherwise calculate now
        # This ensures baseline is calculated on the original spectrum before denoising
        if prominence is not None and prominence < 0:
            if s.bl is not None:
                prominence = s.bl
            else:
                # Baseline wasn't cached, calculate it now on current (post-denoise) data
                # Note: This should ideally be avoided by caching baseline before denoise
                prominence = s.baseline()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            peaks, props = find_peaks(
                s.inty,
                height=0,
                width=1,
                distance=distance,
                plateau_size=plateau_size,
                rel_height=0.75,
                wlen=wlen,
            )
            peak_widths_arr = props["widths"]
            peak_prominences_arr = props["prominences"]
        if refine:
            # CRITICAL: Use .copy() to prevent modifying array during iteration
            prof_mz = s.mz.copy()
            prof_inty = s.inty.copy()
            prof_not_smoothed = not_smothed_inty.copy()

            # Optimized vectorized refinement using searchsorted for neighbor finding
            mz_window = refine_window  # Da - window for weighted m/z averaging during refinement

            # Pre-compute all left and right indices (vectorized searchsorted)
            peak_mzs = prof_mz[peaks]
            left_bounds = peak_mzs - mz_window
            right_bounds = peak_mzs + mz_window
            left_indices = np.searchsorted(prof_mz, left_bounds, side="left")
            right_indices = np.searchsorted(prof_mz, right_bounds, side="right")

            # Use numba-optimized refinement if available (73x faster)
            if NUMBA_AVAILABLE:
                s.mz, s.inty = _refine_peaks_numba(
                    peaks,
                    prof_mz,
                    prof_inty,
                    prof_not_smoothed,
                    left_indices,
                    right_indices,
                )
            else:
                # Fallback to Python loop if numba not available
                for i, peak_idx in enumerate(peaks):
                    left_idx = left_indices[i]
                    right_idx = right_indices[i]

                    # Skip if not enough neighbors
                    if right_idx - left_idx < 3:
                        continue

                    # Use the neighbors for refinement
                    neighbor_mz = prof_mz[left_idx:right_idx]
                    neighbor_inty = prof_inty[left_idx:right_idx]
                    neighbor_not_smoothed = prof_not_smoothed[left_idx:right_idx]

                    # Find which data source (smoothed or original) has higher peak
                    original_peak_inty_smoothed = prof_inty[peak_idx]
                    original_peak_inty_not_smoothed = prof_not_smoothed[peak_idx]

                    # Use the data with higher peak intensity for refinement
                    if original_peak_inty_smoothed >= original_peak_inty_not_smoothed:
                        weights = neighbor_inty**3 + 1
                        s.mz[peak_idx] = np.average(neighbor_mz, weights=weights)
                        s.inty[peak_idx] = neighbor_inty.max()
                    else:
                        weights = neighbor_not_smoothed**3 + 1
                        s.mz[peak_idx] = np.average(neighbor_mz, weights=weights)
                        s.inty[peak_idx] = neighbor_not_smoothed.max()

            # Extract peak values and their properties
            s.mz = s.mz[peaks]
            s.inty = s.inty[peaks]
            s.width = peak_widths_arr
            s.prominence = peak_prominences_arr

            # CRITICAL: Re-sort after refinement since weighted averaging can change order
            sort_idx = np.argsort(s.mz)
            s.mz = s.mz[sort_idx]
            s.inty = s.inty[sort_idx]
            s.width = s.width[sort_idx]
            s.prominence = s.prominence[sort_idx]

            # Remove duplicate centroids that are closer than 1/10 of mz_window
            # Keep only the highest intensity peak among duplicates
            duplicate_threshold = mz_window / 10.0
            if len(s.mz) > 1:
                keep_mask = np.ones(len(s.mz), dtype=bool)
                i = 0
                while i < len(s.mz) - 1:
                    if not keep_mask[i]:
                        i += 1
                        continue
                    # Find all peaks within threshold of current peak
                    j = i + 1
                    duplicate_indices = [i]
                    while j < len(s.mz) and (s.mz[j] - s.mz[i]) < duplicate_threshold:
                        duplicate_indices.append(j)
                        j += 1

                    # If duplicates found, keep only the one with highest intensity
                    if len(duplicate_indices) > 1:
                        intensities = s.inty[duplicate_indices]
                        max_idx = duplicate_indices[np.argmax(intensities)]
                        for idx in duplicate_indices:
                            if idx != max_idx:
                                keep_mask[idx] = False

                    i = j if j > i + 1 else i + 1

                # Apply mask to remove duplicates
                if not np.all(keep_mask):
                    s.mz = s.mz[keep_mask]
                    s.inty = s.inty[keep_mask]
                    s.width = s.width[keep_mask]
                    s.prominence = s.prominence[keep_mask]

            s.history_add("c[SLMR]")
            s.centroided = True
        else:
            s.mz = s.mz[peaks]
            s.inty = props["peak_heights"]
            s.width = peak_widths_arr
            s.prominence = peak_prominences_arr
            s.history_add("c[SLM]")
            s.centroided = True
        if prominence is not None:
            mask = s.prominence >= prominence
            s.mz = s.mz[mask]
            s.inty = s.inty[mask]
            s.width = s.width[mask]
            s.prominence = s.prominence[mask]
            s.history_add("f[PRO]")

        return s

    def deisotope(self, mz_tol: float = 0.02, ratio_max: float = 1.5) -> Spectrum:
        self_c = self.copy()
        mzs = self_c.mz
        intys = self_c.inty
        is_isotopolog_of = np.zeros(len(mzs)).astype(np.int32)
        i = 0
        j = 1
        while j < len(mzs) and i < len(mzs):
            isodelta = mzs[j] - mzs[i] - 1.00335
            if isodelta < -mz_tol:
                j += 1
            elif isodelta <= mz_tol:
                if intys[j] < intys[i] * ratio_max:
                    if is_isotopolog_of[i] == 0:
                        is_isotopolog_of[j] = i
                    else:
                        is_isotopolog_of[j] = is_isotopolog_of[i]
                j += 1
            else:
                i += 1
        mask = np.where(is_isotopolog_of == 0)[0]
        for key in self_c.__dict__:
            if isinstance(self_c.__dict__[key], np.ndarray) and self_c.__dict__[
                key
            ].size == len(is_isotopolog_of):
                self_c.__dict__[key] = self_c.__dict__[key][mask]
        if self_c.label is not None:
            self_c.label = self_c.label + " deiso."
        self_c.history_add("f[iso]")
        return self_c

    def plot(
        self,
        mz_start: float | None = None,
        mz_stop: float | None = None,
        ylog: bool = False,
        title: str | None = None,
        width: int = 1000,
        height: int = 250,
        colorby: str | None = None,
        cmap: str = "rainbow",
        cmap_provider: str = "colorcet",
        cmap_min: float = -1,
        cmap_max: float = 1,
        filename: str | None = None,
    ) -> None:
        cvalues = None
        colors = ["black"] * len(self.mz)
        if colorby is not None:
            if not hasattr(self, colorby):
                raise ValueError(f"{colorby} is not a valid attribute of the spectrum")
            if not isinstance(self.__dict__[colorby], np.ndarray):
                raise ValueError(f"{colorby} is not a valid attribute of the spectrum")
            if len(self.__dict__[colorby]) != len(self.mz):
                raise ValueError(f"{colorby} is not a valid attribute of the spectrum")
            cvalues = self.__dict__[colorby].copy()
            cvalues[cvalues < cmap_min] = cmap_min
            cvalues[cvalues > cmap_max] = cmap_max
            cvalues = (cvalues - cmap_min) / (cmap_max - cmap_min) * 255
            cm = process_cmap(cmap, ncolors=255, provider=cmap_provider)
            colors = [
                rgb2hex(cm[int(i * (len(cm) - 1) / 255)])
                if not np.isnan(i)
                else rgb2hex((0, 0, 0))
                for i in cvalues
            ]
        p = figure(
            width=width,
            height=height,
            title=title,
        )
        label = None
        if self.label is not None:
            label = self.label
        mz = self.mz
        inty = self.inty
        if mz_start is not None:
            mask = mz >= mz_start
            mz = mz[mask]
            inty = inty[mask]
            colors = np.array(colors)[mask].tolist()
        if mz_stop is not None:
            mask = mz <= mz_stop
            mz = mz[mask]
            inty = inty[mask]
            colors = np.array(colors)[mask].tolist()
        if len(mz) == 0:
            logger.warning("No peaks in spectrum after trimming")
            return
        if not self.centroided:
            mz_diff = np.diff(mz)
            new_mzs: list[float] = []
            new_inty: list[float] = []
            last_good_step = 1
            for i in range(len(mz_diff)):
                if mz_diff[i] > last_good_step * 4:
                    new_mzs.append(mz[i] + last_good_step)
                    new_inty.append(0)
                    new_mzs.append(mz[i + 1] - last_good_step)
                    new_inty.append(0)
                else:
                    last_good_step = mz_diff[i]
            if len(new_mzs) > 0:
                new_mzs_array = np.array(new_mzs)
                new_inty_array = np.array(new_inty)
                mz = np.append(mz, new_mzs_array)
                inty = np.append(inty, new_inty_array)
                idx = np.argsort(mz)
                mz = mz[idx]
                inty = inty[idx]
            p.line(mz, inty, line_color="black", legend_label=label)
        else:
            # Build data dictionary from spectrum attributes (numpy arrays)
            data = {}
            for key, val in self.__dict__.items():
                if isinstance(val, np.ndarray) and val.size == mz.size:
                    data[key] = val
            if ylog:
                data["zeros"] = np.ones_like(mz)
            else:
                data["zeros"] = np.zeros_like(mz)
            data["color"] = colors
            source = ColumnDataSource(data)
            p.segment(
                x0="mz",
                y0="zeros",
                x1="mz",
                y1="inty",
                line_color="black",
                legend_label=label,
                source=source,
            )
            if cvalues is not None:
                sc = p.scatter(
                    x="mz",
                    y="inty",
                    size=5,
                    fill_color="color",
                    line_color="color",
                    legend_label=label,
                    source=source,
                )
            else:
                sc = p.scatter(
                    x="mz",
                    y="inty",
                    size=3,
                    fill_color="black",
                    line_color="black",
                    legend_label=label,
                    source=source,
                )
            tooltips = [(k, "@" + k) for k in source.data if k != "zeros"]
            hover_tool = HoverTool(renderers=[sc], tooltips=tooltips)
            p.add_tools(hover_tool)
            box_zoom_tools = [
                tool for tool in p.toolbar.tools if isinstance(tool, BoxZoomTool)
            ]
            if box_zoom_tools:
                p.toolbar.active_drag = box_zoom_tools[0]
            if colorby is not None:
                mapper = LinearColorMapper(
                    palette=[rgb2hex(c) for c in cm],
                    low=cmap_min,
                    high=cmap_max,
                )
                if ColorBar is not None:
                    color_bar = ColorBar(
                        color_mapper=mapper,
                        location=(0, 0),
                        title=colorby,
                    )
                    p.add_layout(color_bar, "right")
        if ylog:
            p.y_scale = LogScale()
            p.yaxis.formatter = LogTickFormatter()
        else:
            p.yaxis.formatter = NumeralTickFormatter(format="0.0e0")
        if filename is not None:
            if filename.endswith(".html"):
                output_file(filename)
                save(p)
            elif filename.endswith(".png"):
                export_png(p, filename=filename)
            else:
                show(p)
        else:
            show(p)

    def plot_stats(self) -> None:
        df = self.pandalize()
        from bokeh.plotting import show
        from hvplot.plotting import parallel_coordinates

        p = parallel_coordinates(
            df,
            color="black",
            width=1000,
            height=250,
            line_width=1,
            hover_color="red",
        )
        show(p)

    def plot_dist(self) -> None:
        from bokeh.plotting import figure, show

        for _i, attr in enumerate(self.__dict__):
            if isinstance(self.__dict__[attr], np.ndarray):
                hist, edges = np.histogram(self.__dict__[attr], bins=100)
                p = figure(
                    width=250,
                    height=250,
                    title=attr,
                )
                p.quad(
                    top=hist,
                    bottom=0,
                    left=edges[:-1],
                    right=edges[1:],
                    fill_color="navy",
                    line_color="white",
                    alpha=0.5,
                )
                show(p)


def group_peaks(
    mz_values: np.ndarray,
    tolerance: float = 0,
    ppm: float = 0,
    time_domain: bool = False,
) -> np.ndarray:
    """
    Group peaks based on m/z values using tolerance and ppm.

    Args:
        mz_values: Array of m/z values
        tolerance: Absolute tolerance for grouping
        ppm: Parts per million tolerance
        time_domain: If True, grouping is done on sqrt(mz)

    Returns:
        Array of group indices for each peak
    """
    values = np.sqrt(mz_values) if time_domain else mz_values
    values = np.sqrt(mz_values) if time_domain else mz_values

    # Initialize groups
    groups = np.zeros(len(values), dtype=int)
    current_group = 0

    for i in range(1, len(values)):
        diff = values[i] - values[i - 1]
        ppm_tolerance = values[i - 1] * ppm * 1e-6 if ppm else 0
        max_diff = max(tolerance, ppm_tolerance)

        if diff > max_diff:
            current_group += 1
        groups[i] = current_group

    return groups


def combine_peaks(
    spectra: list[Spectrum],
    inty_fun: Callable = np.sum,
    mz_fun: Callable = np.mean,
    weighted: bool = False,
    exponent: float = 3,
    tolerance: float = 0.002,
    ppm: float = 5,
    time_domain: bool = True,
    mode: str = "union",
    main: int | None = None,
    min_points: int | None = None,
    min_prop: float = 0.5,
) -> Spectrum:
    """
    Combine multiple spectra into a single spectrum.
    Args:
        spectra: List of PeakMatrix objects to combine
        inty_fun: Function to combine intensities
        mz_fun: Function to combine m/z values
        weighted: Use intensity-weighted mean for m/z values
        exponent: Exponent for intensity weighting
        tolerance: Absolute tolerance for peak grouping
        ppm: Parts per million tolerance for peak grouping
        time_domain: If True, grouping is done on sqrt(mz)
        mode: Strategy for combining peaks ("union" or "intersect")
        main: Index of main spectrum to keep peaks from
        min_points: Minimum number of points to retain a peak
        min_prop: Minimum proportion for intersect strategy

    Returns:
        Combined Spectrum

    """

    if len(spectra) == 1:
        all_mz = spectra[0].mz
        all_inty = spectra[0].inty
        spectrum_indices: np.ndarray = np.zeros(all_mz.size)
    else:
        # Concatenate all m/z and intensity values
        all_mz = np.concatenate([pm.mz for pm in spectra])
        all_inty = np.concatenate([pm.inty for pm in spectra])

        # Track which spectrum each peak came from
        spectrum_indices = np.concatenate(
            [np.full(len(pm.mz), i) for i, pm in enumerate(spectra)],
        )

    if all_mz.size < 2:
        return Spectrum(
            mz=all_mz,
            inty=all_inty,
            ms_level=spectra[0].ms_level,
            centroided=True,
        )
    # Sort by m/z
    sort_idx = np.argsort(all_mz)
    all_mz = all_mz[sort_idx]
    all_inty = all_inty[sort_idx]
    spectrum_indices = spectrum_indices[sort_idx]

    # Group peaks
    groups = group_peaks(all_mz, tolerance, ppm, time_domain)
    unique_groups = np.unique(groups)

    # Process each group
    combined_mz = []
    combined_inty = []

    for group in unique_groups:
        mask = groups == group
        # check if the number of points is greater than min_points
        if min_points is not None and np.sum(mask) < min_points:
            continue
        if min_points is not None and np.sum(mask) < min_points:
            continue
        group_mz = all_mz[mask]
        group_inty = all_inty[mask]
        group_spectra = spectrum_indices[mask]

        # Handle intersect strategy
        if mode == "intersect":
            unique_spectra = len(np.unique(group_spectra))
            if unique_spectra < (len(spectra) * min_prop):
                continue

        # Handle main spectrum filtering
        if main is not None and main not in group_spectra:
            continue
        if main is not None and main not in group_spectra:
            continue

        # Calculate combined values

        if weighted:
            combined_mz.append(np.average(group_mz, weights=group_inty**exponent))
        else:
            combined_mz.append(mz_fun(group_mz))

        combined_inty.append(inty_fun(group_inty))

    if not combined_mz:
        return Spectrum(mz=np.array([]), inty=np.array([]))

    return Spectrum(
        mz=np.array(combined_mz),
        inty=np.array(combined_inty),
        ms_level=spectra[0].ms_level,
        centroided=True,
    )


def plot_spectra(
    spectra: list[Spectrum],
    labels: list[str] | None = None,
    mz_start: float | None = None,
    mz_stop: float | None = None,
    title: str | None = None,
    width: int = 1000,
    height: int = 250,
    cmap: str = "rainbow",
    cmap_provider: str = "colorcet",
    filename: str | None = None,
    colorby: str | None = None,
    ylog: bool = False,
    stacked: bool = False,
) -> None:
    """
    Plot multiple mass spectrometry spectra on a single Bokeh figure.
    This function displays profile spectra as continuous lines and centroided spectra as vertical segments
    (with circles at the peak tops) on a Bokeh plot. Spectra can be optionally trimmed by m/z range using the
    mz_start and mz_stop parameters. Additionally, a colormap is applied to differentiate between spectra.
    Parameters:
        spectra (List[spectrum]): A list of spectrum objects to be plotted. Each object must have attributes
                                    'mz' (mass-to-charge ratio), 'inty' (intensity), and 'centroided' (a boolean
                                    indicating if the spectrum is centroided).
        labels (List[str], optional): A list of labels for the spectra. If provided and its length is at least as
                                        long as the number of spectra, these labels override the default spectrum
                                        naming.
        mz_start (float, optional): The lower bound for m/z values. Peaks with m/z values below this threshold
                                    are excluded from the plot.
        mz_stop (float, optional): The upper bound for m/z values. Peaks with m/z values above this threshold
                                    are excluded from the plot.
        title (str, optional): The title of the plot.
        width (int, optional): The width of the plot in pixels. Default is 1000.
        height (int, optional): The height of the plot in pixels. Default is 250.
        cmap (str, optional): The colormap name used to assign colors to the spectra. Default is "rainbow".
        cmap_provider (str, optional): The provider for the specified colormap. Default is "colorcet".
        filename (str, optional): If provided, the plot is saved to a file. The export format is determined by the
                                    file extension—HTML for ".html" and PNG for ".png". If the filename does not
                                    have an appropriate extension, the plot is simply displayed.
        ylog (bool, optional): If True, the y-axis is set to a logarithmic scale. Default is False.
        colorby (str, optional): If provided, the color of each spectrum is determined by this attribute.
        stacked (bool, optional): If True, each spectrum is plotted in a separate vertically stacked subplot with
                                    synchronized x-axes for zooming. Default is False.

    Returns:
        None
    Side Effects:
        - Displays the Bokeh plot in a browser window if no filename is provided.
        - Exports the plot to a file if a valid filename is provided.
        - Prints a message to the console if a spectrum contains no peaks after applying the m/z trimming.
    """
    from bokeh.io import output_file, save
    from bokeh.io.export import export_png
    from bokeh.models import (
        BoxZoomTool,
        ColumnDataSource,
        HoverTool,
        LogScale,
        LogTickFormatter,
        NumeralTickFormatter,
    )
    from bokeh.plotting import figure, show
    from holoviews.plotting.util import process_cmap
    from matplotlib.colors import rgb2hex
    import numpy as np

    num_plots = len(spectra)
    cm = process_cmap(cmap, ncolors=num_plots, provider=cmap_provider)
    colors = [
        rgb2hex(cm[int(i * (len(cm) - 1) / (num_plots - 1))])
        if num_plots > 1
        else rgb2hex(cm[0])
        for i in range(num_plots)
    ]

    # Create stacked plots or single plot
    if stacked:
        from bokeh.layouts import column
        from bokeh.plotting import figure as Figure

        plots: list[Figure] = []

        for spec_idx, spec in enumerate(spectra):
            # Create individual plot for each spectrum
            if plots:
                # Sync x and y axes with first plot
                p = figure(
                    width=width,
                    height=height,
                    title=None,
                    x_range=plots[0].x_range,
                    y_range=plots[0].y_range,
                )
            else:
                # First plot gets the title
                p = figure(
                    width=width,
                    height=height,
                    title=title,
                )

            try:
                label = f"Spectrum {spec_idx}"
                if spec.label is not None:
                    label = spec.label
                if labels is not None and len(labels) >= num_plots:
                    label = labels[spec_idx]

                mcvalues = None
                mcolors = ["black"] * len(spec.mz)
                if colorby is not None:
                    if not hasattr(spec, colorby):
                        raise ValueError(
                            f"{colorby} is not a valid attribute of the spectrum {spec_idx}",
                        )
                    if not isinstance(spec.__dict__[colorby], np.ndarray):
                        raise ValueError(
                            f"{colorby} is not a valid attribute of the spectrum {spec_idx}",
                        )
                    if len(spec.__dict__[colorby]) != len(spec.mz):
                        raise ValueError(
                            f"{colorby} is not a valid attribute of the spectrum {spec_idx}",
                        )
                    mcvalues = spec.__dict__[colorby].copy()
                    mcvalues[mcvalues < -1] = -1
                    mcvalues[mcvalues > 1] = 1
                    mcvalues = (mcvalues + 1) / 2 * 255
                    cm_markers = process_cmap(cmap, ncolors=255, provider=cmap_provider)
                    mcolors = [
                        rgb2hex(cm_markers[int(i * (len(cm_markers) - 1) / 255)])
                        if not np.isnan(i)
                        else rgb2hex((0, 0, 0))
                        for i in mcvalues
                    ]

                color = colors[spec_idx]
                mz = spec.mz.copy()
                inty = spec.inty.copy()

                # Build mask for trimming
                mask = np.ones(len(mz), dtype=bool)
                if mz_start is not None:
                    mask &= mz >= mz_start
                if mz_stop is not None:
                    mask &= mz <= mz_stop

                # Apply mask
                mz = mz[mask]
                inty = inty[mask]
                if len(mcolors) == len(mask):
                    mcolors = np.array(mcolors)[mask].tolist()

                if len(mz) == 0:
                    logger.warning(f"No peaks in spectrum {spec_idx} after trimming")
                    continue

                if not spec.centroided:
                    if not np.all(np.diff(mz) >= 0):
                        idx = np.argsort(mz)
                        mz = mz[idx]
                        inty = inty[idx]

                    mz_diff = np.diff(mz)
                    new_mzs: list[float] = []
                    new_inty: list[float] = []
                    last_good_step = 0.01

                    for i in range(len(mz_diff)):
                        if mz_diff[i] > last_good_step * 4:
                            step = min(last_good_step, mz_diff[i] / 4)
                            mz_before = min(mz[i] + step, mz[i + 1] - 0.001)
                            mz_after = max(mz[i + 1] - step, mz[i] + 0.001)
                            if mz_before < mz[i + 1]:
                                new_mzs.append(mz_before)
                                new_inty.append(0)
                            if mz_after > mz[i] and mz_after < mz[i + 1]:
                                new_mzs.append(mz_after)
                                new_inty.append(0)
                        else:
                            last_good_step = mz_diff[i]
                    if len(new_mzs) > 0:
                        new_mzs_array = np.array(new_mzs)
                        new_inty_array = np.array(new_inty)
                        mz = np.append(mz, new_mzs_array)
                        inty = np.append(inty, new_inty_array)
                        idx = np.argsort(mz)
                        mz = mz[idx]
                        inty = inty[idx]

                    p.line(mz, inty, line_color=color, legend_label=label)
                else:
                    data = {"mz": mz, "inty": inty}
                    if ylog:
                        data["zeros"] = np.ones_like(mz)
                    else:
                        data["zeros"] = np.zeros_like(mz)

                    for key, val in spec.__dict__.items():
                        if (
                            key not in data
                            and isinstance(val, np.ndarray)
                            and val.size == len(spec.mz)
                        ):
                            data[key] = val[mask]

                    if colorby is not None:
                        data[colorby] = mcolors

                    source = ColumnDataSource(data)

                    # Plot vertical segments (sticks)
                    p.segment(
                        x0="mz",
                        y0="zeros",
                        x1="mz",
                        y1="inty",
                        line_color=color,
                        legend_label=label,
                        source=source,
                    )

                    # Add scatter points on top
                    if colorby is not None:
                        sc = p.scatter(
                            x="mz",
                            y="inty",
                            size=5,
                            fill_color=colorby,
                            line_color=colorby,
                            legend_label=label,
                            source=source,
                        )
                    else:
                        sc = p.scatter(
                            x="mz",
                            y="inty",
                            size=3,
                            fill_color=color,
                            line_color=color,
                            legend_label=label,
                            source=source,
                        )
                    tooltips = [(k, "@" + k) for k in source.data if k != "zeros"]
                    hover_tool = HoverTool(renderers=[sc], tooltips=tooltips)
                    p.add_tools(hover_tool)
                    box_zoom_tools = [
                        tool
                        for tool in p.toolbar.tools
                        if isinstance(tool, BoxZoomTool)
                    ]
                    if box_zoom_tools:
                        p.toolbar.active_drag = box_zoom_tools[0]
            except Exception as e:
                logger.exception(f"Error plotting spectrum {spec_idx}: {e}")

            # Configure y-axis
            if ylog:
                p.y_scale = LogScale()
                p.yaxis.formatter = LogTickFormatter()
            else:
                p.yaxis.formatter = NumeralTickFormatter(format="0.0e0")

            p.legend.click_policy = "hide"
            plots.append(p)

        # Combine all plots in a column layout
        layout = column(*plots)

        if filename is not None:
            if filename.endswith(".html"):
                output_file(filename)
                save(layout)
            elif filename.endswith(".svg"):
                for plot in plots:
                    plot.output_backend = "svg"
                export_svg(layout, filename=filename)
            elif filename.endswith(".png"):
                export_png(layout, filename=filename)
            else:
                show(layout)
        else:
            from bokeh.io import output_notebook, reset_output

            reset_output()
            output_notebook()
            show(layout)
    else:
        # Original single plot behavior
        p = figure(
            width=width,
            height=height,
            title=title,
        )

        for spec_idx, spec in enumerate(spectra):
            try:
                label = f"Spectrum {spec_idx}"
                if spec.label is not None:
                    label = spec.label
                if labels is not None and len(labels) >= num_plots:
                    label = labels[spec_idx]

                mcvalues = None
                mcolors = ["black"] * len(spec.mz)
                if colorby is not None:
                    if not hasattr(spec, colorby):
                        raise ValueError(
                            f"{colorby} is not a valid attribute of the spectrum {spec_idx}",
                        )
                    if not isinstance(spec.__dict__[colorby], np.ndarray):
                        raise ValueError(
                            f"{colorby} is not a valid attribute of the spectrum {spec_idx}",
                        )
                    if len(spec.__dict__[colorby]) != len(spec.mz):
                        raise ValueError(
                            f"{colorby} is not a valid attribute of the spectrum {spec_idx}",
                        )
                    mcvalues = spec.__dict__[colorby].copy()
                    mcvalues[mcvalues < -1] = -1
                    mcvalues[mcvalues > 1] = 1
                    mcvalues = (mcvalues + 1) / 2 * 255
                    cm_markers = process_cmap(cmap, ncolors=255, provider=cmap_provider)
                    mcolors = [
                        rgb2hex(cm_markers[int(i * (len(cm_markers) - 1) / 255)])
                        if not np.isnan(i)
                        else rgb2hex((0, 0, 0))
                        for i in mcvalues
                    ]

                color = colors[spec_idx]
                mz = spec.mz.copy()
                inty = spec.inty.copy()

                # Build mask for trimming
                mask = np.ones(len(mz), dtype=bool)
                if mz_start is not None:
                    mask &= mz >= mz_start
                if mz_stop is not None:
                    mask &= mz <= mz_stop

                # Apply mask
                mz = mz[mask]
                inty = inty[mask]
                if len(mcolors) == len(mask):
                    mcolors = np.array(mcolors)[mask].tolist()

                if len(mz) == 0:
                    logger.warning("No peaks in spectrum after trimming")
                    return

                if not spec.centroided:
                    if not np.all(np.diff(mz) >= 0):
                        idx = np.argsort(mz)
                        mz = mz[idx]
                        inty = inty[idx]

                    mz_diff = np.diff(mz)
                    new_mzs = []
                    new_inty = []
                    last_good_step = 0.01

                    for i in range(len(mz_diff)):
                        if mz_diff[i] > last_good_step * 4:
                            step = min(last_good_step, mz_diff[i] / 4)
                            mz_before = min(mz[i] + step, mz[i + 1] - 0.001)
                            mz_after = max(mz[i + 1] - step, mz[i] + 0.001)
                            if mz_before < mz[i + 1]:
                                new_mzs.append(mz_before)
                                new_inty.append(0)
                            if mz_after > mz[i] and mz_after < mz[i + 1]:
                                new_mzs.append(mz_after)
                                new_inty.append(0)
                        else:
                            last_good_step = mz_diff[i]
                    if len(new_mzs) > 0:
                        new_mzs_array = np.array(new_mzs)
                        new_inty_array = np.array(new_inty)
                        mz = np.append(mz, new_mzs_array)
                        inty = np.append(inty, new_inty_array)
                        idx = np.argsort(mz)
                        mz = mz[idx]
                        inty = inty[idx]

                    p.line(mz, inty, line_color=color, legend_label=label)
                else:
                    data = {"mz": mz, "inty": inty}
                    if ylog:
                        data["zeros"] = np.ones_like(mz)
                    else:
                        data["zeros"] = np.zeros_like(mz)

                    for key, val in spec.__dict__.items():
                        if (
                            key not in data
                            and isinstance(val, np.ndarray)
                            and val.size == len(spec.mz)
                        ):
                            data[key] = val[mask]

                    if colorby is not None:
                        data[colorby] = mcolors

                    source = ColumnDataSource(data)

                    # Plot vertical segments (sticks)
                    p.segment(
                        x0="mz",
                        y0="zeros",
                        x1="mz",
                        y1="inty",
                        line_color=color,
                        legend_label=label,
                        source=source,
                    )

                    # Add scatter points on top
                    if colorby is not None:
                        sc = p.scatter(
                            x="mz",
                            y="inty",
                            size=5,
                            fill_color=colorby,
                            line_color=colorby,
                            legend_label=label,
                            source=source,
                        )
                    else:
                        sc = p.scatter(
                            x="mz",
                            y="inty",
                            size=3,
                            fill_color=color,
                            line_color=color,
                            legend_label=label,
                            source=source,
                        )
                    tooltips = [(k, "@" + k) for k in source.data if k != "zeros"]
                    hover_tool = HoverTool(renderers=[sc], tooltips=tooltips)
                    p.add_tools(hover_tool)
                    box_zoom_tools = [
                        tool
                        for tool in p.toolbar.tools
                        if isinstance(tool, BoxZoomTool)
                    ]
                    if box_zoom_tools:
                        p.toolbar.active_drag = box_zoom_tools[0]
            except Exception as e:
                logger.exception(f"Error plotting spectrum {spec_idx}: {e}")

        if colorby is not None:
            color_mapper = LinearColorMapper(palette=cm_markers, low=-1, high=1)
            if ColorBar is not None:
                color_bar = ColorBar(
                    color_mapper=color_mapper,
                    ticker=FixedTicker(ticks=[-1, -0.5, 0, 0.5, 1]),
                    location=(0, 0),
                )
                p.add_layout(color_bar, "right")

        if ylog:
            p.y_scale = LogScale()
            p.yaxis.formatter = LogTickFormatter()
        else:
            p.yaxis.formatter = NumeralTickFormatter(format="0.0e0")
        p.legend.click_policy = "hide"

        if filename is not None:
            if filename.endswith(".html"):
                output_file(filename)
                save(p)
            elif filename.endswith(".svg"):
                p.output_backend = "svg"
                export_svg(p, filename=filename)
            elif filename.endswith(".png"):
                export_png(p, filename=filename)
            else:
                show(p)
        else:
            from bokeh.io import output_notebook, reset_output

            reset_output()
            output_notebook()
            show(p)


if __name__ == "__main__":
    pass
