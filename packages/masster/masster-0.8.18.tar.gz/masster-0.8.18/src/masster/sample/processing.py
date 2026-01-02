# mypy: disable-error-code="attr-defined,union-attr,arg-type,unreachable,no-any-return"
from __future__ import annotations

from datetime import datetime

import numpy as np
import polars as pl
import pyopenms as oms
from tqdm import tqdm

from masster.chromatogram import Chromatogram
from masster.spectrum import Spectrum

from .defaults.find_features_def import find_features_defaults
from .defaults.find_ms2_def import find_ms2_defaults
from .defaults.get_spectrum_def import get_spectrum_defaults


def get_spectrum(self, scan: int, **kwargs) -> Spectrum | None:
    """Retrieve and post-process single spectrum.

    Locates scan in scans_df and returns Spectrum object with optional processing
    (centroiding, deisotoping, precursor trimming, DIA statistics).

    Args:
        scan (int): Scan identifier (scan_id) to retrieve.
        **kwargs: Individual parameter overrides for :class:`get_spectrum_defaults`:

            centroid (bool): Whether to centroid the spectrum. Reduces noise and
                simplifies peak lists. Defaults to True.
            centroid_algo (str | None): Centroiding algorithm. Options: 'lmp'
                (local maximum), 'cwt' (continuous wavelet transform), 'gaussian'
                (Gaussian fitting). None uses sample default. Defaults to None.
            deisotope (bool): Whether to remove isotope peaks, keeping only
                monoisotopic. Defaults to True.
            max_peaks (int | None): Maximum peaks to keep after filtering. None
                keeps all. Useful for reducing large spectra. Defaults to None.
            precursor_trim (int): m/z window to remove precursor from MS2. Negative
                values disable trimming. Defaults to -10.
            dia_stats (bool): Collect DIA/ztscan statistics (Q1 ratio, EIC
                correlation). Only relevant for DIA data. Defaults to False.
            feature (int | None): Feature ID for computing DIA statistics. Required
                when dia_stats=True. Defaults to None.
            label (str | None): Custom label for returned Spectrum. None generates
                automatic label. Defaults to None.
            clean (bool): Remove peaks below baseline noise level. Uses 1.5× mean
                of lowest 10% peaks as threshold. Adds "t[CL]" to history.
                Defaults to False.

    Returns:
        Spectrum | None: Processed spectrum object with mz, inty arrays and
            metadata. Returns None if scan not found.

    Example:
        Basic spectrum retrieval::

            >>> sample = masster.Sample("data.mzML")
            >>> spec = sample.get_spectrum(scan=500)
            >>> print(f"{len(spec.mz)} peaks, max: {spec.inty.max():.0f}")

        Raw (unprocessed) spectrum::

            >>> spec_raw = sample.get_spectrum(
            ...     scan=500,
            ...     centroid=False,
            ...     deisotope=False
            ... )

        Specific centroiding algorithm::

            >>> spec_lmp = sample.get_spectrum(scan=500, centroid_algo="lmp")
            >>> spec_cwt = sample.get_spectrum(scan=500, centroid_algo="cwt")

        Limit peak count::

            >>> spec = sample.get_spectrum(scan=500, max_peaks=100)

        DIA statistics collection::

            >>> spec = sample.get_spectrum(
            ...     scan=500,
            ...     dia_stats=True,
            ...     feature=42
            ... )
            >>> print(spec.q1_ratio, spec.eic_corr)

        Noise filtering::

            >>> spec = sample.get_spectrum(scan=500, clean=True)
            >>> print("t[CL]" in spec.history)  # True

        Access spectrum properties::

            >>> spec = sample.get_spectrum(scan=500)
            >>> base_peak_mz = spec.mz[spec.inty.argmax()]
            >>> total_intensity = spec.inty.sum()
            >>> spectrum_name = spec.name

    Note:
        - Automatic label generation:
          MS1: "MS1, rt X.XX s, scan Y"
          MS2: "MS2 of mz X.X, rt Y.YY s, scan Z"
        - Centroid_algo uses sample.parameters default if not specified
        - Spectrum object includes: mz, inty, ms_level, rt, energy, name
        - For DIA data, dia_stats computes isolation window metrics
        - Precursor_trim removes precursor ±N Da from MS2 (reduces chimeric peaks)
        - Empty spectrum returned if scan data unavailable (not None)
        - File interface automatically reloaded if needed
        - Clean parameter filters noise same as export_mgf clean=True

    See Also:
        get_spectrum_defaults: Parameter configuration object.
        Spectrum: Spectrum class with processing methods.
        find_ms2: Link MS2 spectra to features.
        export_mgf: Export spectra to MGF format.
    """

    # parameters initialization
    params = get_spectrum_defaults(scan=[scan])
    for key, value in kwargs.items():
        if isinstance(value, get_spectrum_defaults):
            params = value
            self.logger.debug("Using provided get_spectrum_defaults parameters")
        elif hasattr(params, key):
            if params.set(key, value, validate=True):
                self.logger.debug(f"Updated parameter {key} = {value}")
            else:
                self.logger.warning(
                    f"Failed to set parameter {key} = {value} (validation failed)",
                )
        else:
            self.logger.debug(f"Unknown parameter {key} ignored")
    # end of parameter initialization

    # Extract parameter values
    scan = params.get("scan")
    # Unwrap scan from list (it's stored as list in defaults)
    if isinstance(scan, list) and len(scan) > 0:
        scan = scan[0]
    precursor_trim = params.get("precursor_trim")
    max_peaks = params.get("max_peaks")
    centroid = params.get("centroid")
    deisotope = params.get("deisotope")
    dia_stats = params.get("dia_stats")
    feature_id = params.get("feature")
    label = params.get("label")
    centroid_algo = params.get("centroid_algo")
    clean = params.get("clean")

    # get energy, ms_level, rt from scans_df
    scan_id = scan  # Preserve original scan ID
    scan_info = self.scans_df.filter(pl.col("scan_id") == scan_id)
    if len(scan_info) == 0:
        self.logger.warning(f"Scan {scan_id} not found.")
        return None
    scan_info = scan_info[0]
    energy = scan_info["energy"][0]
    ms_level = scan_info["ms_level"][0]
    rt = scan_info["rt"][0]
    if label is None:
        if ms_level == 1:
            name = f"MS1, rt {rt:.2f} s, scan {scan_id}"
        else:
            name = f"MS2 of mz {scan_info['prec_mz'][0]:0.1f}, rt {rt:.2f} s, scan {scan_id}"
    else:
        name = label

    if centroid_algo is None:
        if "centroid_algo" in self.parameters:
            centroid_algo = self.parameters.get("centroid_algo")
        else:
            # this is for backward compatibility. This is the old default
            self.parameters.centroid_algo = "lmp"
        centroid_algo = self.parameters.get("centroid_algo")

    spec0 = Spectrum(mz=np.array([]), inty=np.array([]))
    if self.file_interface == "oms":
        # if check that file_obj is not None
        if self.file_obj is None:
            self.logger.info("Reloading raw data from file...")
            self.index_raw()
        try:
            spect = self.file_obj.getSpectrum(scan_id).get_peaks()
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return spec0
        if len(spect[0]) == 0:
            return spec0
        if len(spect[0]) == 1:
            mz = np.array([spect[0][0]])
            inty = np.array([spect[1][0]])
        else:
            mz = np.array(spect[0])
            inty = np.array(spect[1])

        # Filter out invalid m/z values (negative or zero)
        if len(mz) > 0:
            valid_mask = mz > 0
            if not np.all(valid_mask):
                # Check if there's a pattern in the invalid data
                invalid_intensities = inty[~valid_mask]
                unique_invalid_intys = np.unique(invalid_intensities)
                self.logger.warning(
                    f"Scan {scan_id}: Removed {np.sum(~valid_mask)} invalid m/z values (≤0). "
                    f"Invalid intensities: {unique_invalid_intys[:10]}",
                )
                mz = mz[valid_mask]
                inty = inty[valid_mask]

        if ms_level == 1:
            spect = Spectrum(
                mz=mz,
                inty=inty,
                ms_level=ms_level,
                rt=rt,
                energy=None,
                precursor_mz=None,
                label=name,
            )
        else:
            spect = Spectrum(
                mz=mz,
                inty=inty,
                ms_level=ms_level,
                rt=rt,
                energy=energy,
                precursor_mz=scan_info["prec_mz"][0],
                label=name,
            )
        if centroid and not spect.centroided:
            spect = spect.denoise()
            if spect.ms_level == 1:
                spect = spect.centroid(
                    algo=centroid_algo,
                    tolerance=self.parameters.get("mz_tol_ms1_da"),
                    ppm=self.parameters.get("mz_tol_ms1_ppm"),
                    min_points=self.parameters.get("centroid_min_points_ms1"),
                    smooth=self.parameters.get("centroid_smooth_ms1"),
                    prominence=self.parameters.get("centroid_prominence"),
                    refine=self.parameters.get("centroid_refine_ms1"),
                    refine_window=self.parameters.get("centroid_refine_mz_tol"),
                )
            elif spect.ms_level == 2:
                spect = spect.centroid(
                    algo=centroid_algo,
                    tolerance=self.parameters.get("mz_tol_ms2_da"),
                    ppm=self.parameters.get("mz_tol_ms2_ppm"),
                    min_points=self.parameters.get("centroid_min_points_ms2"),
                    smooth=self.parameters.get("centroid_smooth_ms2"),
                    prominence=self.parameters.get("centroid_prominence"),
                    refine=self.parameters.get("centroid_refine_ms2"),
                    refine_window=self.parameters.get("centroid_refine_mz_tol"),
                )

    elif self.file_interface == "alpharaw":
        if self.file_obj is None:
            self.logger.info("Reloading raw data from file...")
            self.index_raw()
        spec_df = self.file_obj.spectrum_df
        spect = (
            spec_df.filter(pl.col("spec_idx") == scan_id).row(0, named=True)
            if isinstance(spec_df, pl.DataFrame)
            else spec_df.loc[scan_id]
        )
        peak_stop_idx = spect["peak_stop_idx"]
        peak_start_idx = spect["peak_start_idx"]

        if isinstance(self.file_obj.peak_df, pl.DataFrame):
            peaks = self.file_obj.peak_df.slice(
                peak_start_idx,
                peak_stop_idx - peak_start_idx,
            )
            mz_values = peaks.select("mz").to_numpy().flatten()
            intensity_values = peaks.select("intensity").to_numpy().flatten()
        else:
            peaks = self.file_obj.peak_df.loc[peak_start_idx : peak_stop_idx - 1]
            mz_values = peaks.mz.values
            intensity_values = peaks.intensity.values

        # Filter out invalid m/z values (negative or zero)
        if len(mz_values) > 0:
            valid_mask = mz_values > 0
            if not np.all(valid_mask):
                # Check if there's a pattern in the invalid data
                invalid_intensities = intensity_values[~valid_mask]
                unique_invalid_intys = np.unique(invalid_intensities)
                self.logger.warning(
                    f"Scan {scan_id}: Removed {np.sum(~valid_mask)} invalid m/z values (≤0). "
                    f"Invalid intensities: {unique_invalid_intys[:10]}",
                )
                mz_values = mz_values[valid_mask]
                intensity_values = intensity_values[valid_mask]

        if spect["ms_level"] > 1:
            spect = Spectrum(
                mz=np.asarray(mz_values, dtype=np.float64),
                inty=np.asarray(intensity_values, dtype=np.float64),
                ms_level=ms_level,
                centroided=False,
                precursor_mz=spect["precursor_mz"],
                energy=energy,
                rt=rt,
                label=name,
            )
        else:
            spect = Spectrum(
                mz=np.asarray(mz_values, dtype=np.float64),
                inty=np.asarray(intensity_values, dtype=np.float64),
                ms_level=ms_level,
                centroided=False,
                precursor_mz=None,
                energy=None,
                rt=rt,
                label=name,
            )

        if len(spect) and centroid and not spect.centroided:
            spect = spect.denoise()
            if spect.ms_level == 1:
                spect = spect.centroid(
                    algo=centroid_algo,
                    tolerance=self.parameters.get("mz_tol_ms1_da"),
                    ppm=self.parameters.get("mz_tol_ms1_ppm"),
                    min_points=self.parameters.get("centroid_min_points_ms1"),
                    smooth=self.parameters.get("centroid_smooth_ms1"),
                    prominence=self.parameters.get("centroid_prominence"),
                    refine=self.parameters.get("centroid_refine_ms1"),
                    refine_window=self.parameters.get("centroid_refine_mz_tol"),
                )
            elif spect.ms_level == 2:
                spect = spect.centroid(
                    algo=centroid_algo,
                    tolerance=self.parameters.get("mz_tol_ms2_da"),
                    ppm=self.parameters.get("mz_tol_ms2_ppm"),
                    min_points=self.parameters.get("centroid_min_points_ms2"),
                    smooth=self.parameters.get("centroid_smooth_ms2"),
                    prominence=self.parameters.get("centroid_prominence"),
                    refine=self.parameters.get("centroid_refine_ms2"),
                    refine_window=self.parameters.get("centroid_refine_mz_tol"),
                )

    else:
        # Attempt to reload raw data if file interface is not available
        if self.file_interface is None:
            self.logger.info(
                "File interface not available. Attempting to index raw data...",
            )
            try:
                self.index_raw()
                # Retry get_spectrum after indexing
                if self.file_interface == "oms":
                    return self.get_spectrum(scan=scan, **kwargs)
            except Exception as e:
                self.logger.error(
                    f"Failed to index raw data: {e}. Cannot retrieve spectrum.",
                )
                return spec0

        self.logger.error(
            f"File interface {self.file_interface} not supported. Reload data.",
        )
        return spec0

    # Deisotope before cleaning - removes isotope peaks that would bias baseline
    if deisotope and spect.centroided:
        spect = spect.deisotope()

    # Clean after deisotoping but before other filtering
    # This ensures baseline calculation sees the full deisotoped spectrum
    if clean:
        spect = spect.clean()

    # Trim precursor region (filtering operation)
    if precursor_trim is not None and spect.ms_level is not None and spect.ms_level > 1:
        spect = spect.trim(mz_min=None, mz_max=spect.precursor_mz - precursor_trim)

    # Limit spectrum size (final filtering)
    if max_peaks is not None:
        spect = spect.keep_top(max_peaks)

    # Always calculate size
    spect.size = spect.mz.size

    # Calculate DIA statistics on final filtered spectrum
    if dia_stats:
        if self.type in ["ztscan", "dia", "swath"]:
            spect = self._get_ztscan_stats(
                spec=spect,
                scan_id=scan_id,
                feature_id=scan_info["feature_id"][0]
                if "feature_id" in scan_info and scan_info["feature_id"][0] is not None
                else feature_id,
                q1_step=2,
                deisotope=deisotope,
                centroid=centroid,
            )

    return spect


def _get_ztscan_stats(
    self,
    spec,
    scan_id=None,
    feature_id=None,
    q1_step=2,
    mz_tol=0.005,
    deisotope=False,  # Hardcoded: SpectrumParameters not available
    centroid=True,  # Hardcoded: no centroid_algo parameter exists
):
    # spec.ms_entropy = spec.entropy()

    if self.scans_df is None:
        self.logger.warning("No scans found.")
        return spec
    scan = self.scans_df.filter(pl.col("scan_id") == scan_id)
    if len(scan) == 0:
        self.logger.warning(f"Scan {scan_id} not found.")
        return spec
    scan = scan[0]
    if scan["ms_level"][0] != 2:
        self.logger.warning(f"Scan {scan_id} is not a MS2 scan.")
    # Q1
    lscan = self.scans_df.filter(pl.col("scan_id") == scan_id - q1_step)
    if len(lscan) == 0:
        self.logger.warning(f"Scan {scan_id - q1_step} not found.")
        return spec
    lscan = lscan[0]
    # check that lscan['ms_level'] == 2 and lscan['cycle'] == scan['cycle']
    if lscan["ms_level"][0] != 2:
        self.logger.warning(f"Scan {scan_id - q1_step} is not a MS2 scan.")
        return spec
    if lscan["cycle"][0] != scan["cycle"][0]:
        self.logger.warning(
            f"Scan {scan_id - q1_step} is not in the same cycle as scan {scan_id}.",
        )
        return spec
    rscan = self.scans_df.filter(pl.col("scan_id") == scan_id + q1_step)
    if len(rscan) == 0:
        self.logger.warning(f"Scan {scan_id + q1_step} not found.")
        return spec
    rscan = rscan[0]
    # check that rscan['ms_level'] == 2 and rscan['cycle'] == scan['cycle']
    if rscan["ms_level"][0] != 2:
        self.logger.warning(f"Scan {scan_id + q1_step} is not a MS2 scan.")
        return spec
    if rscan["cycle"][0] != scan["cycle"][0]:
        self.logger.warning(
            f"Scan {scan_id + q1_step} is not in the same cycle as scan {scan_id}.",
        )
        return spec
    intymat = self._spec_to_mat(
        scan_ids=[scan_id - q1_step, scan_id, scan_id + q1_step],
        mz_ref=spec.mz,
        mz_tol=mz_tol,
        deisotope=deisotope,
        centroid=centroid,
    )
    # pick only mzs that are close to spec.mz
    if intymat is None:
        return spec
    if intymat.shape[1] < 3:
        self.logger.warning(f"Not enough data points for scan {scan_id}.")
        return spec
    q1_ratio = (2 * intymat[:, 1] + 0.01) / (intymat[:, 0] + intymat[:, 2] + 0.01)
    spec.q1_ratio = np.round(np.log2(q1_ratio), 3)
    # where intymat[:, 0] + intymat[:, 2]==0, set q1_ratio to -1
    spec.q1_ratio[np.isclose(intymat[:, 0] + intymat[:, 2], 0)] = -10

    # EIC correlation
    # find rt_start and rt_end of the feature_id
    if self.features_df is None:
        self.logger.warning("No features found.")
        return spec
    if feature_id is None:
        return spec
    # spec.precursor_mz = feature['mz']
    feature = self.features_df.filter(pl.col("feature_id") == feature_id)
    if len(feature) == 0:
        self.logger.warning(f"Feature {feature_id} not found.")
        return spec
    feature = feature.row(0, named=True)
    rt_start = feature["rt_start"]
    rt_end = feature["rt_end"]
    # get the cycle at rt_start and the cycle at rt_end from the closest scan with ms_level == 1
    scans = self.scans_df.filter(pl.col("ms_level") == 1)
    scans = scans.filter(pl.col("rt") > rt_start)
    scans = scans.filter(pl.col("rt") < rt_end)
    if len(scans) == 0:
        self.logger.warning(f"No scans found between {rt_start} and {rt_end}.")
        return spec
    scan_ids = scans["scan_id"].to_list()
    eic_prec = self._spec_to_mat(
        scan_ids=scan_ids,
        mz_ref=feature["mz"],
        mz_tol=mz_tol,
        deisotope=deisotope,
        centroid=centroid,
    )
    # find width at half maximum of the eic_prec
    # hm = np.max(eic_prec[0, :]) / 3
    # find index of maximum
    # eic_prec_max_idx = np.argmax(eic_prec[0, :])
    # find index of the closest point to half maximum
    # idx = np.argmin(np.abs(eic_prec[0, :] - hm))
    # eic_fwhm_prec = abs(eic_prec_max_idx - idx)

    # get all unique cycles from scans
    cycles = scans["cycle"].unique()
    scandids = []
    # iterate over all cycles and get the scan_id of scan with ms_level == 2 and closest precursor_mz to spec.precursor_mz
    for cycle in cycles:
        scans = self.scans_df.filter(pl.col("cycle") == cycle)
        scans = scans.filter(pl.col("ms_level") == 2)
        scans = scans.filter(pl.col("prec_mz") > feature["mz"] - 4)
        scans = scans.filter(pl.col("prec_mz") < feature["mz"] + 4)
        if len(scans) == 0:
            self.logger.warning(f"No scans found for cycle {cycle}.")
            continue
        scan = scans[(scans["prec_mz"] - feature["mz"]).abs().arg_sort()[:1]]
        scandids.append(scan["scan_id"][0])

    eic_prod = self._spec_to_mat(
        scan_ids=scandids,
        mz_ref=spec.mz,
        mz_tol=mz_tol,
        deisotope=deisotope,
        centroid=centroid,
    )
    # eic_prod = eic_prod.T
    # eic_prec = eic_prec.T
    # calculate correlation between eic_prec and all columns of eic_prod, column by column
    eic_corr = np.zeros(eic_prod.shape[0])
    # eic_width_ratio = np.zeros(eic_prod.shape[0])
    for i in range(eic_prod.shape[0]):
        try:
            with np.errstate(divide="ignore", invalid="ignore"):
                eic_corr[i] = np.corrcoef(eic_prod[i, :], eic_prec[0, :])[0, 1]
        except (ValueError, RuntimeWarning):
            # Correlation calculation failed (e.g., constant arrays, NaN values)
            # Leave as zero (default)
            pass

    spec.eic_corr = np.round(eic_corr, 3)
    return spec


def _spec_to_mat(
    self,
    scan_ids,
    mz_ref=None,
    mz_tol=0.01,
    deisotope=False,
    centroid=True,
    precursor_trim=5,
    **kwargs,
):
    # get all spectra in scan_uids

    if mz_ref is None:
        return None

    if not isinstance(mz_ref, np.ndarray):
        if isinstance(mz_ref, list):
            mz_ref = np.array(mz_ref)
        else:
            mz_ref = np.array([mz_ref])

    def align_mzs(ar1, ar2, tol):
        closest_indices = []
        # find the closest pair between each element in ar1 and ar2, within a maximum tolerance of tol
        for i, val1 in enumerate(ar1):
            closest_index = np.argmin(np.abs(ar2 - val1))
            closest_indices.append((i, closest_index))
        # filter out pairs that are not within the specified tolerance
        closest_indices = [
            (i, j) for i, j in closest_indices if np.abs(ar1[i] - ar2[j]) <= tol
        ]
        # remove duplicates from the list of indices
        closest_indices = list(set(closest_indices))
        # sort the list of indices by the first element (i) in ascending order
        closest_indices = sorted(closest_indices, key=lambda x: x[0])

        # Convert the list of indices into an array for easier indexing in subsequent operations
        return np.array(closest_indices)

    specs = []
    for scan_id in scan_ids:
        spec = self.get_spectrum(
            scan_id,
            centroid=centroid,
            deisotope=False,  # Deisotoping handled separately below
            dia_stats=False,
            precursor_trim=precursor_trim,
            **kwargs,
        )
        if deisotope:
            spec = spec.deisotope()
        # align to reference spectrum
        if spec.mz.size == 0:
            continue
        if mz_ref.size == 0:
            continue
        closest_indices = align_mzs(spec.mz, mz_ref, mz_tol)
        # store the aligned spectrum in the list
        aligned_inty = np.zeros(len(mz_ref))
        for i, j in closest_indices:
            if abs(spec.mz[i] - mz_ref[j]) <= mz_tol:
                aligned_inty[j] = max(aligned_inty[j], spec.inty[i])
        specs.append(aligned_inty)

    if len(specs) == 0:
        return None
    # create a matrix with the aligned spectra. Each spec goes into a column
    mat = np.column_stack(specs)

    return mat


def find_features(self, **kwargs) -> None:
    """Detect chromatographic features (m/z with retention time profiles).

    Implements untargeted feature detection using OpenMS MassTraceDetection and
    ElutionPeakDetection algorithms. Extracts mass traces, deconvolves overlapping
    peaks, and assembles features with quality metrics.

    Args:
        **kwargs: Individual parameter overrides for :class:`find_features_defaults`:

            **Chromatographic Parameters:**
                chrom_fwhm (float): Expected chromatographic peak full width at half
                    maximum in seconds. Critical tuning parameter. Typical ranges:
                    5-10 (UHPLC), 10-20 (HPLC), 20-40 (LC-MS). Defaults to 10.0.
                mass_error_ppm (float): Mass accuracy in ppm for mass trace extraction.
                    Defaults to 10.0.
                reestimate_mt_sd (bool): Re-estimate mass trace standard deviation
                    during extraction. Defaults to True.
                quant_method (str): Quantification method for peak areas. Options:
                    "area" (default), "median".

            **Detection Thresholds:**
                noise (float): Intensity threshold for mass trace detection. Points
                    below this value are ignored. Critical for reducing false
                    positives. Defaults to 500.0.
                chrom_peak_snr (float): Signal-to-noise ratio threshold for elution
                    peak detection. Higher values = fewer, higher quality features.
                    Defaults to 3.0.
                min_sample_rate (float): Minimum fraction of scans required for valid
                    mass traces. Range 0.0-1.0. Defaults to 0.5.
                min_trace_length (float): Minimum mass trace duration in seconds.
                    Defaults to 5.0.
                max_trace_length (float): Maximum mass trace duration in seconds.
                    -1 disables limit. Defaults to -1.0.

            **Isotope Processing:**
                use_smoothed_intensities (bool): Apply Gaussian smoothing before
                    isotope detection. Defaults to True.
                min_isotope_fit (float): Minimum isotope pattern fit score (0.0-1.0).
                    Defaults to 0.6.
                max_charge (int): Maximum charge state to consider. Defaults to 3.

            **Quality Filters:**
                min_fwhm (float): Minimum FWHM in seconds. Filters very narrow peaks.
                    Defaults to 1.0.
                max_fwhm (float): Maximum FWHM in seconds. Filters very broad peaks.
                    Defaults to 60.0.
                min_mz (float): Minimum m/z value. Defaults to 50.0.
                max_mz (float): Maximum m/z value. Defaults to 2000.0.
                min_rt (float): Minimum retention time in minutes. Defaults to 0.0.
                max_rt (float): Maximum retention time in minutes. Defaults to 1000.0.
                coherence (float | None): Minimum mass trace coherence score
                    (0.0-1.0). None disables filter. Defaults to 0.6.
                prominence (float | None): Minimum peak prominence score (0.0-1.0).
                    None disables filter. Defaults to None.
                height_scaled (float | None): Minimum height-scaled quality score.
                    None disables filter. Defaults to None.

    Example:
        Basic feature detection::

            >>> sample = masster.Sample("data.mzML")
            >>> sample.find_features()
            >>> print(f"Found {len(sample.features_df)} features")

        Optimize for UHPLC::

            >>> sample.find_features(chrom_fwhm=7.0, noise=1000, chrom_peak_snr=5.0)

        Systematic parameter tuning workflow::

            >>> # Step 1: Adjust chromatographic width
            >>> sample.find_features(chrom_fwhm=15.0)
            >>>
            >>> # Step 2: Adjust noise threshold if too many/few features
            >>> sample.find_features(chrom_fwhm=15.0, noise=1000)
            >>>
            >>> # Step 3: Fine-tune SNR for quality
            >>> sample.find_features(chrom_fwhm=15.0, noise=1000, chrom_peak_snr=5.0)

        Apply strict quality filters::

            >>> sample.find_features(
            ...     coherence=0.8,
            ...     prominence=0.5,
            ...     min_fwhm=3.0,
            ...     max_fwhm=30.0
            ... )

    Note:
        **Three-tier tuning approach:**

        1. **chrom_fwhm**: Start here. Too low = missed peaks, peak splitting.
           Too high = merged peaks, poor resolution.
        2. **noise**: Adjust if feature count is far from expected. Higher noise
           = fewer features, lower false positive rate.
        3. **chrom_peak_snr**: Fine-tune quality. Higher SNR = fewer but more
           reliable features.

        **Results stored in features_df with columns:**

        - feature_id: Unique identifier
        - mz: Mass-to-charge ratio
        - rt: Retention time (minutes)
        - rtmin, rtmax: RT bounds (minutes)
        - intensity: Peak intensity
        - area: Integrated area (quantification value)
        - fwhm: Full width at half maximum (seconds)
        - quality: Overall quality score (0-1)
        - charge: Assigned charge state
        - convexity: Peak shape metric
        - quality_height_scaled, quality_prominence, quality_coherence: Individual
          quality metrics

        **Post-processing recommendations:**

        - Use find_iso() to link isotopologue groups
        - Use find_adducts() to detect adduct relationships
        - Use find_ms2() to link MS2 spectra
        - Use identify() for library matching

    Raises:
        ValueError: If MS1 spectra are empty or parameters invalid.
        RuntimeError: If OpenMS feature detection fails.

    See Also:
        find_features_defaults: Parameter configuration object.
        find_iso: Link isotopologue features.
        find_adducts: Detect adduct relationships.
        find_ms2: Link MS2 spectra to features.
        identify: Match features to spectral library.
        features_filter: Apply post-detection filters.
    """
    if self.ms1_df is None:
        self.logger.error("No MS1 data found. Please load a file first.")
        return
    if len(self.ms1_df) == 0:
        self.logger.error("MS1 data is empty. Please load a file first.")
        return
    # parameters initialization
    params = find_features_defaults()
    for key, value in kwargs.items():
        if isinstance(value, find_features_defaults):
            # set
            params = value
            self.logger.debug("Using provided find_features_defaults parameters")
        elif hasattr(params, key):
            if params.set(key, value, validate=True):
                self.logger.debug(f"Updated parameter {key} = {value}")
            else:
                self.logger.warning(
                    f"Failed to set parameter {key} = {value} (validation failed)",
                )
        else:
            self.logger.warning(f"Unknown parameter {key} ignored")

    # Set global parameters
    if hasattr(params, "threads") and params.threads is not None:
        try:
            # Try setting via OpenMP environment variable first (newer approach)
            import os

            os.environ["OMP_NUM_THREADS"] = str(params.threads)
            self.logger.debug(
                f"Set thread count to {params.threads} via OMP_NUM_THREADS",
            )
        except Exception:
            self.logger.warning(
                f"Could not set thread count to {params.threads} - using default",
            )

    # Set debug mode if enabled
    if hasattr(params, "debug") and params.debug:
        self.logger.debug("Debug mode enabled")
    elif hasattr(params, "no_progress") and params.no_progress:
        self.logger.debug("No progress mode enabled")

    self.logger.info("Starting feature detection...")
    self.logger.debug(
        f"Parameters: chrom_fwhm={params.get('chrom_fwhm')}, noise={params.get('noise')}, tol_ppm={params.get('tol_ppm')}, isotope_filtering_model={params.get('isotope_filtering_model')}",
    )
    # check that noise is not lower than 1% quantile of ms1_df inty
    noise_threshold = self.ms1_df.select(pl.col("inty")).quantile(0.01)[0, 0]
    if params.get("noise") < noise_threshold / 10:
        self.logger.warning(
            f"Warning: noise threshold {params.get('noise')} is lower than 1% quantile of MS1 intensities ({noise_threshold:.1f}). This may lead to many false positives.",
        )

    exp = oms.MSExperiment()
    # find max number of cycles in self.ms1_df
    max_cycle = self.ms1_df["cycle"].max()
    # iterate over all cycles, find rows with 1 cycle and append to exp2
    for cycle in range(1, max_cycle + 1):
        cycle_df = self.ms1_df.filter(pl.col("cycle") == cycle)
        # check if len(cycle_df) > 0
        if len(cycle_df) > 0:
            spectrum = oms.MSSpectrum()
            spectrum.setRT(cycle_df[0]["rt"].item())
            spectrum.setMSLevel(1)  # MS1
            mz = cycle_df["mz"]
            inty = cycle_df["inty"]
            spectrum.set_peaks([mz, inty])
            spectrum.sortByPosition()
            exp.addSpectrum(spectrum)

    # exp.sortSpectra(True)
    # mass trace detection
    mass_traces: list = []
    mtd = oms.MassTraceDetection()
    mtd_par = mtd.getDefaults()

    # Apply MTD parameters
    mtd_par.setValue("mass_error_ppm", float(params.get("tol_ppm")))
    mtd_par.setValue("noise_threshold_int", float(params.get("noise")))
    mtd_par.setValue(
        "min_trace_length",
        float(params.get("min_trace_length_multiplier"))
        * float(params.get("chrom_fwhm_min")),
    )
    mtd_par.setValue(
        "trace_termination_outliers",
        int(params.get("trace_termination_outliers")),
    )
    mtd_par.setValue("chrom_peak_snr", float(params.get("chrom_peak_snr")))

    # Additional MTD parameters
    mtd_par.setValue("min_sample_rate", float(params.get("min_sample_rate")))
    mtd_par.setValue("min_trace_length", float(params.get("min_trace_length")))
    mtd_par.setValue(
        "trace_termination_criterion",
        params.get("trace_termination_criterion"),
    )
    mtd_par.setValue(
        "reestimate_mt_sd",
        "true" if params.get("reestimate_mt_sd") else "false",
    )
    mtd_par.setValue("quant_method", params.get("quant_method"))

    mtd.setParameters(mtd_par)  # set the new parameters
    mtd.run(exp, mass_traces, 0)  # run mass trace detection

    # elution peak detection
    mass_traces_deconvol: list = []
    epd = oms.ElutionPeakDetection()
    epd_par = epd.getDefaults()

    # Apply EPD parameters using our parameter class
    epd_par.setValue("width_filtering", params.get("width_filtering"))
    epd_par.setValue("min_fwhm", float(params.get("chrom_fwhm_min")))
    epd_par.setValue("max_fwhm", float(params.get("chrom_fwhm_max")))
    epd_par.setValue("chrom_fwhm", float(params.get("chrom_fwhm")))
    epd_par.setValue("chrom_peak_snr", float(params.get("chrom_peak_snr")))
    if params.get("masstrace_snr_filtering"):
        epd_par.setValue("masstrace_snr_filtering", "true")
    if params.get("mz_scoring_13C"):
        epd_par.setValue("mz_scoring_13C", "true")

    epd.setParameters(epd_par)
    epd.detectPeaks(mass_traces, mass_traces_deconvol)

    # feature detection
    feature_map = oms.FeatureMap()  # output features
    chrom_out: list = []  # output chromatograms
    ffm = oms.FeatureFindingMetabo()
    ffm_par = ffm.getDefaults()

    # Apply FFM parameters using our parameter class
    ffm_par.setValue(
        "remove_single_traces",
        "true" if params.get("remove_single_traces") else "false",
    )
    ffm_par.setValue(
        "report_convex_hulls",
        "true" if params.get("report_convex_hulls") else "false",
    )
    ffm_par.setValue(
        "report_summed_ints",
        "true" if params.get("report_summed_ints") else "false",
    )
    ffm_par.setValue(
        "report_chromatograms",
        "true" if params.get("report_chromatograms") else "false",
    )
    ffm_par.setValue(
        "report_smoothed_intensities",
        "true" if params.get("report_smoothed_intensities") else "false",
    )
    # Additional FFM parameters
    ffm_par.setValue("local_rt_range", float(params.get("local_rt_range")))
    ffm_par.setValue("local_mz_range", float(params.get("local_mz_range")))
    ffm_par.setValue("charge_lower_bound", int(params.get("charge_lower_bound")))
    ffm_par.setValue("charge_upper_bound", int(params.get("charge_upper_bound")))
    ffm_par.setValue("isotope_filtering_model", params.get("isotope_filtering_model"))

    ffm.setParameters(ffm_par)

    self.logger.debug("Running feature finding with parameters:")
    self.logger.debug(ffm_par)
    ffm.run(mass_traces_deconvol, feature_map, chrom_out)
    # Assigns a new, valid unique id per feature
    feature_map.ensureUniqueId()
    df = feature_map.get_df(export_peptide_identifications=False)
    # Sets the file path to the primary MS run (usually the mzML file)
    feature_map.setPrimaryMSRunPath([self.file_path.encode()])

    # Store feature map in both attributes for compatibility
    self.features = feature_map
    self._oms_features_map = feature_map
    # remove peaks with quality == 0
    df = self._clean_features_df(df)

    # desotope features
    df = self._features_deisotope(
        df,
        mz_tol=params.get("deisotope_mz_tol"),
        rt_tol=params.get("chrom_fwhm") * params.get("deisotope_rt_tol_factor"),
    )
    if params.get("deisotope"):
        # record size before deisotoping
        size_before_deisotope = len(df)
        df = df.filter(pl.col("iso") == 0)
        self.logger.debug(
            f"Deisotoping features: {size_before_deisotope - len(df)} features removed.",
        )

    # update eic - create lists to collect results
    chroms: list[Chromatogram | None] = []
    sanities: list[float | None] = []
    coherences: list[float | None] = []
    prominences: list[float | None] = []
    prominence_scaleds: list[float | None] = []
    height_scaleds: list[float | None] = []

    mz_tol = self.parameters.get("eic_mz_tol")
    rt_tol = self.parameters.get("eic_rt_tol")

    # iterate over all rows in df using polars iteration
    self.logger.debug("Extracting EICs...")
    for row in df.iter_rows(named=True):
        # select data in ms1_df with mz in range [mz_start - mz_tol, mz_end + mz_tol] and rt in range [rt_start - rt_tol, rt_end + rt_tol]
        d = self.ms1_df.filter(
            (pl.col("rt") >= row["rt_start"] - rt_tol)
            & (pl.col("rt") <= row["rt_end"] + rt_tol)
            & (pl.col("mz") >= row["mz"] - mz_tol)
            & (pl.col("mz") <= row["mz"] + mz_tol),
        )
        # for all unique rt values, find the maximum inty
        eic_rt = d.group_by("rt").agg(pl.col("inty").max())
        if len(eic_rt) < 4:
            chroms.append(None)
            sanities.append(None)
            coherences.append(None)
            prominences.append(None)
            prominence_scaleds.append(None)
            height_scaleds.append(None)
            continue

        eic = Chromatogram(
            eic_rt["rt"].to_numpy(),
            eic_rt["inty"].to_numpy(),
            label=f"EIC mz={row['mz']:.4f}",
            file=self.file_path,
            mz=row["mz"],
            mz_tol=mz_tol,
            feature_start=row["rt_start"],
            feature_end=row["rt_end"],
            feature_apex=row["rt"],
        ).find_peaks()

        # collect results
        chroms.append(eic)
        if len(eic.peak_widths) > 0:
            sanities.append(
                round(eic.feature_sanity, 3)
                if eic.feature_sanity is not None
                else None,
            )
            coherences.append(round(eic.feature_coherence, 3))
            prominences.append(round(eic.peak_prominences[0], 3))
            prominence_scaleds.append(
                round(eic.peak_prominences[0] / (np.mean(eic.inty) + 1e-10), 3),
            )
            height_scaleds.append(
                round(eic.peak_heights[0] / (np.mean(eic.inty) + 1e-10), 3),
            )
        else:
            sanities.append(None)
            coherences.append(None)
            prominences.append(None)
            prominence_scaleds.append(None)
            height_scaleds.append(None)

    # Add the computed columns to the dataframe
    df = df.with_columns(
        [
            pl.Series("chrom", chroms, dtype=pl.Object),
            pl.Series("chrom_sanity", sanities, dtype=pl.Float64),
            pl.Series("chrom_coherence", coherences, dtype=pl.Float64),
            pl.Series("chrom_prominence", prominences, dtype=pl.Float64),
            pl.Series("chrom_prominence_scaled", prominence_scaleds, dtype=pl.Float64),
            pl.Series("chrom_height_scaled", height_scaleds, dtype=pl.Float64),
        ],
    )

    # Apply chrom_height_scaled filtering if specified
    chrom_height_scaled_threshold = params.get("chrom_height_scaled")
    if chrom_height_scaled_threshold is not None:
        size_before = len(df)
        df = df.filter(
            (pl.col("chrom_height_scaled").is_null())
            | (pl.col("chrom_height_scaled") >= chrom_height_scaled_threshold),
        )
        if len(df) < size_before:
            self.logger.debug(
                f"Filtered {size_before - len(df)} features with chrom_height_scaled < {chrom_height_scaled_threshold}",
            )

    # Apply chrom_coherence filtering if specified
    chrom_coherence_threshold = params.get("chrom_coherence")
    if chrom_coherence_threshold is not None:
        size_before = len(df)
        df = df.filter(
            (pl.col("chrom_coherence").is_null())
            | (pl.col("chrom_coherence") >= chrom_coherence_threshold),
        )
        if len(df) < size_before:
            self.logger.debug(
                f"Filtered {size_before - len(df)} features with chrom_coherence < {chrom_coherence_threshold}",
            )

    # Apply chrom_prominence_scaled filtering if specified
    chrom_prominence_scaled_threshold = params.get("chrom_prominence_scaled")
    if chrom_prominence_scaled_threshold is not None:
        size_before = len(df)
        df = df.filter(
            (pl.col("chrom_prominence_scaled").is_null())
            | (pl.col("chrom_prominence_scaled") >= chrom_prominence_scaled_threshold),
        )
        if len(df) < size_before:
            self.logger.debug(
                f"Filtered {size_before - len(df)} features with chrom_prominence_scaled < {chrom_prominence_scaled_threshold}",
            )

    self.features_df = df
    # self._features_sync()
    self.logger.success(f"Feature detection completed. Total features: {len(df)}")

    # store params
    self.update_history(["find_features"], params.to_dict())
    self.logger.debug(
        "Parameters stored to find_features",
    )
    keys_to_remove = ["find_adducts", "find_ms2"]
    for key in keys_to_remove:
        if key in self.history:
            del self.history[key]
            self.logger.debug(f"Removed {key} from history")


def _clean_features_df(self, df):
    """Clean and standardize features DataFrame."""
    # Convert pandas DataFrame to polars if needed
    if hasattr(df, "index"):  # pandas DataFrame
        from uuid6 import uuid7

        df = df.copy()
        df["feature_id"] = [str(uuid7()) for _ in range(len(df))]

    if hasattr(df, "columns") and not isinstance(df, pl.DataFrame):
        df_pl = pl.from_pandas(df)
    else:
        df_pl = df

    # Filter out rows with quality == 0
    df2 = df_pl.filter(pl.col("quality") != 0)

    # Create new dataframe with required columns and transformations
    # Normalize column names to handle both uppercase (legacy) and lowercase formats
    col_map = {c.lower(): c for c in df2.columns}
    rt_col = col_map.get("rt", "RT")
    rt_start_col = col_map.get("rt_start", col_map.get("rtstart", "RTstart"))
    rt_end_col = col_map.get("rt_end", col_map.get("rtend", "RTend"))
    mz_start_col = col_map.get("mz_start", col_map.get("mzstart", "MZstart"))
    mz_end_col = col_map.get("mz_end", col_map.get("mzend", "MZend"))

    df_result = df2.select(
        [
            pl.int_range(pl.len()).alias("feature_id"),
            pl.col("feature_id").cast(pl.String).alias("feature_uid"),
            pl.col("mz").round(5),
            pl.col(rt_col).round(3).alias("rt"),
            pl.col(rt_col).round(3).alias("rt_original"),
            pl.col(rt_start_col).round(3).alias("rt_start"),
            pl.col(rt_end_col).round(3).alias("rt_end"),
            (pl.col(rt_end_col) - pl.col(rt_start_col)).round(3).alias("rt_delta"),
            pl.col(mz_start_col).round(5).alias("mz_start"),
            pl.col(mz_end_col).round(5).alias("mz_end"),
            pl.col("intensity").alias("inty"),
            pl.col("quality"),
            pl.col("charge"),
            pl.lit(0).alias("iso"),
            pl.lit(None, dtype=pl.Int64).alias("iso_of"),
            pl.lit(None, dtype=pl.Utf8).alias("adduct"),
            pl.lit(None, dtype=pl.Float64).alias("adduct_charge"),
            pl.lit(None, dtype=pl.Float64).alias("adduct_mass_shift"),
            pl.lit(None, dtype=pl.Float64).alias("adduct_mass_neutral"),
            pl.lit(None, dtype=pl.Int64).alias("adduct_group"),
            pl.lit(None, dtype=pl.Object).alias("chrom"),
            pl.lit(None, dtype=pl.Float64).alias("chrom_coherence"),
            pl.lit(None, dtype=pl.Float64).alias("chrom_prominence"),
            pl.lit(None, dtype=pl.Float64).alias("chrom_prominence_scaled"),
            pl.lit(None, dtype=pl.Float64).alias("chrom_height_scaled"),
            pl.lit(None, dtype=pl.Float64).alias("chrom_sanity"),
            pl.lit(None, dtype=pl.Object).alias("ms2_scans"),
            pl.lit(None, dtype=pl.Object).alias("ms2_specs"),
        ],
    )

    return df_result


def _features_deisotope(
    self,
    df,
    mz_tol=None,
    rt_tol=None,
):
    """Perform isotope detection and assignment on features."""
    if mz_tol is None:
        mz_tol = 0.02
    if rt_tol is None:
        rt_tol = 0.2

    # Convert to polars if needed
    if not isinstance(df, pl.DataFrame):
        df = pl.from_pandas(df)

    # Initialize new columns
    df = df.with_columns(
        [
            pl.lit(0).alias("iso"),
            pl.col("feature_id").alias("iso_of"),
        ],
    )

    # Sort by 'mz'
    df = df.sort("mz")

    # Get arrays for efficient processing
    rt_arr = df["rt"].to_numpy()
    mz_arr = df["mz"].to_numpy()
    intensity_arr = df["inty"].to_numpy()
    feature_id_arr = df["feature_id"].to_numpy()
    n = len(df)
    mz_diff = 1.003355

    # Create arrays to track isotope assignments
    iso_arr = np.zeros(n, dtype=int)
    iso_of_arr = feature_id_arr.copy()

    for i in range(n):
        base_rt = rt_arr[i]
        base_mz = mz_arr[i]
        base_int = intensity_arr[i]
        base_feature_id = feature_id_arr[i]

        # Search for isotope candidates
        for isotope_offset in [1, 2, 3]:
            offset_mz = isotope_offset * mz_diff
            tolerance_factor = 1.0 if isotope_offset == 1 else 1.5

            t_lower = base_mz + offset_mz - tolerance_factor * mz_tol
            t_upper = base_mz + offset_mz + tolerance_factor * mz_tol

            li = np.searchsorted(mz_arr, t_lower, side="left")
            ri = np.searchsorted(mz_arr, t_upper, side="right")

            if li < ri:
                cand_idx = np.arange(li, ri)
                mask = (
                    (rt_arr[cand_idx] > base_rt - rt_tol)
                    & (rt_arr[cand_idx] < base_rt + rt_tol)
                    & (intensity_arr[cand_idx] < 2 * base_int)
                )
                valid_cand = cand_idx[mask]

                for cand in valid_cand:
                    if cand != i and iso_of_arr[cand] == feature_id_arr[cand]:
                        iso_arr[cand] = iso_arr[i] + isotope_offset
                        iso_of_arr[cand] = base_feature_id

    # Update the dataframe with isotope assignments
    df = df.with_columns(
        [
            pl.Series("iso", iso_arr),
            pl.Series("iso_of", iso_of_arr),
        ],
    )

    return df


def analyze_dda(self) -> None:
    """Calculate DDA cycle statistics and timing metrics.

    Analyzes Data-Dependent Acquisition (DDA) scan patterns to compute cycle
    statistics including MS2 count per cycle and inter-scan timing intervals.
    Essential for quality control and method optimization.

    Example:
        Automatic analysis on load::

            >>> sample = masster.Sample("data.mzML")  # analyze_dda called
            >>> print(sample.scans_df.select([
            ...     "scan_id", "ms_level", "ms2_n", "time_cycle"
            ... ]).head())

        Manual re-analysis::

            >>> sample.analyze_dda()
            >>> cycle_stats = sample.scans_df.filter(
            ...     pl.col("ms_level") == 1
            ... ).select(["ms2_n", "time_cycle"])

        Quality control metrics::

            >>> # Average MS2 per cycle
            >>> avg_ms2 = sample.scans_df.filter(
            ...     pl.col("ms_level") == 1
            ... )["ms2_n"].mean()
            >>> print(f"Average MS2/cycle: {avg_ms2:.1f}")
            >>>
            >>> # Cycle time distribution
            >>> ms1_scans = sample.scans_df.filter(pl.col("ms_level") == 1)
            >>> print(f"Mean cycle: {ms1_scans['time_cycle'].mean():.2f}s")
            >>> print(f"Std cycle: {ms1_scans['time_cycle'].std():.2f}s")

        Identify slow cycles::

            >>> slow_cycles = sample.scans_df.filter(
            ...     (pl.col("ms_level") == 1) &
            ...     (pl.col("time_cycle") > 2.0)
            ... )
            >>> print(f"Found {len(slow_cycles)} slow cycles (>2s)")

    Note:
        **Columns added to scans_df:**

        - ms2_n: Number of MS2 scans in this cycle (MS1 rows only)
        - time_cycle: Total cycle duration (s)
        - time_ms1_to_ms1: MS1-to-MS1 interval (s, -1 if no consecutive MS1)
        - time_ms1_to_ms2: MS1-to-first-MS2 interval (s)
        - time_ms2_to_ms2: Average MS2-to-MS2 interval (s)
        - time_ms2_to_ms1: Last-MS2-to-MS1 interval (s)

        **Automatic execution:**

        - Called automatically during mzML/Thermo RAW loading
        - Skipped for 'ztscan' sample types
        - Re-run manually after scan filtering/modification

        **Cycle definition:**

        A cycle starts with an MS1 scan and includes all following MS2 scans
        until the next MS1 scan.

        **Timing calculations:**

        All timing values in seconds, calculated from scan retention times.
        -1 indicates missing/unavailable measurement.

        **Use cases:**

        - Method optimization (target MS2/cycle, cycle time)
        - Quality control (identify duty cycle issues)
        - Troubleshooting (find slow scans, gaps)
        - Performance monitoring (compare runs)

    See Also:
        get_dda_stats: Summarize DDA performance metrics.
        scans_df: Scan-level metadata table.
        find_ms2: Link MS2 scans to features.
    """
    # Preallocate variables
    cycle_records = []
    previous_rt = 0
    previous_level = 0
    ms1_index = None
    cyclestart = None
    ms2_n = 0
    ms1_duration = 0
    ms2_duration: list[float] = []

    for row in self.scans_df.iter_rows(named=True):
        if row["ms_level"] == 1:
            if previous_level == 2:
                ms2_to_ms2 = float(np.mean(ms2_duration)) if ms2_duration else -1.0
                d = {
                    "scan_id": ms1_index,
                    "ms2_n": ms2_n,
                    "time_cycle": row["rt"] - cyclestart,
                    "time_ms1_to_ms1": -1.0,
                    "time_ms1_to_ms2": ms1_duration,
                    "time_ms2_to_ms2": ms2_to_ms2,
                    "time_ms2_to_ms1": row["rt"] - previous_rt,
                }
                cycle_records.append(d)
            elif previous_level == 1:
                d = {
                    "scan_id": ms1_index,
                    "ms2_n": 0,
                    "time_cycle": row["rt"] - cyclestart,
                    "time_ms1_to_ms1": row["rt"] - cyclestart,
                    "time_ms1_to_ms2": -1.0,
                    "time_ms2_to_ms2": -1.0,
                    "time_ms2_to_ms1": -1.0,
                }
                cycle_records.append(d)

            ms1_index = row["scan_id"]
            cyclestart = row["rt"]
            ms2_n = 0
            ms1_duration = 0
            ms2_duration = []
        elif previous_level == 2:
            ms2_n += 1
            ms2_duration.append(row["rt"] - previous_rt)
        elif previous_level == 1:
            ms1_duration = row["rt"] - cyclestart
            ms2_n += 1
        previous_level = row["ms_level"]
        previous_rt = row["rt"]

    # Create DataFrame once at the end
    if cycle_records:
        cycle_data = pl.DataFrame(cycle_records)
        # Drop existing columns if they exist to avoid duplicate column error
        cols_to_drop = [
            "ms2_n",
            "time_cycle",
            "time_ms1_to_ms1",
            "time_ms1_to_ms2",
            "time_ms2_to_ms2",
            "time_ms2_to_ms1",
        ]
        existing_cols = [col for col in cols_to_drop if col in self.scans_df.columns]
        if existing_cols:
            self.scans_df = self.scans_df.drop(existing_cols)
        self.scans_df = self.scans_df.join(cycle_data, on="scan_id", how="left")
    else:
        self.scans_df = self.scans_df.with_columns(
            [
                pl.lit(None).alias("ms2_n"),
                pl.lit(None).alias("time_cycle"),
                pl.lit(None).alias("time_ms1_to_ms1"),
                pl.lit(None).alias("time_ms1_to_ms2"),
                pl.lit(None).alias("time_ms2_to_ms2"),
                pl.lit(None).alias("time_ms2_to_ms1"),
            ],
        )


def find_ms2(self, **kwargs) -> None:
    """Link MS2 spectra to detected features based on RT and precursor m/z.

    Matches MS2 scans from scans_df to features in features_df using retention
    time and precursor m/z criteria. Essential for compound identification workflows
    where fragmentation data is needed.

    Args:
        **kwargs: Individual parameter overrides for :class:`find_ms2_defaults`:

            mz_tol (float): Precursor m/z tolerance in Daltons for matching. For DDA
                acquisitions, 0.5 Da is typical. For DIA/ztscan, use mz_tol_ztscan
                instead. Defaults to 0.5.
            centroid (bool): Whether to centroid retrieved spectra. Centroiding
                reduces noise and simplifies peak lists. Defaults to True.
            deisotope (bool): Whether to deisotope spectra before returning. Removes
                isotope peaks, keeping only monoisotopic peaks. Defaults to False.
            dia_stats (bool): Collect additional DIA/ztscan statistics during
                spectrum retrieval. Enables advanced DIA processing metrics.
                Defaults to False.
            features (int | list[int] | None): Specific feature UID(s) to process.
                None processes all features. Empty list treated as None.
                Defaults to None.
            mz_tol_ztscan (float): m/z tolerance for ztscan/DIA file types.
                Wider tolerance needed due to quadrupole isolation windows.
                Defaults to 4.0.

    Example:
        Basic MS2 linking::

            >>> sample = masster.Sample("data.mzML")
            >>> sample.find_features()
            >>> sample.find_ms2()
            >>>
            >>> # Check features with MS2
            >>> features_with_ms2 = sample.features_df.filter(
            ...     pl.col("ms2_scans").is_not_null()
            ... )
            >>> print(f"{len(features_with_ms2)} features have MS2")

        Tight tolerance for high-resolution DDA::

            >>> sample.find_ms2(mz_tol=0.02)

        DIA data processing::

            >>> sample.find_ms2(mz_tol_ztscan=5.0, dia_stats=True)

        Process specific features::

            >>> high_intensity_ids = sample.features_df.filter(
            ...     pl.col("intensity") > 1e6
            ... )["feature_id"].to_list()
            >>> sample.find_ms2(features=high_intensity_ids)

        Access MS2 spectra::

            >>> feature = sample.features_df[0]
            >>> if feature["ms2_scans"]:
            ...     for scan_id, spectrum in zip(
            ...         feature["ms2_scans"], feature["ms2_specs"]
            ...     ):
            ...         print(f"Scan {scan_id}: {len(spectrum.mz)} peaks")

    Note:
        **Implementation details:**

        - Uses vectorized operations for efficient matching across thousands of
          features and scans
        - Bidirectional lookup: Updates both features_df (adds ms2_scans, ms2_specs)
          and scans_df (sets feature_id for matched scans)
        - RT matching: MS2 scan RT must fall within [rt_start, rt_end] of feature
        - m/z matching: |precursor_mz - feature_mz| <= mz_tol
        - Spectrum objects in ms2_specs contain full peak data for visualization
          and identification

        **Columns added to features_df:**

        - ms2_scans: List of scan IDs linked to this feature
        - ms2_specs: List of Spectrum objects with peak data

        **Updates to scans_df:**

        - feature_id: Set to matched feature UID for bidirectional lookup

        **Tolerance recommendations:**

        - DDA (high-res): 0.01-0.05 Da
        - DDA (low-res): 0.5-1.0 Da
        - DIA/SWATH: 2.0-5.0 Da (use mz_tol_ztscan)
        - All-ion fragmentation: 4.0-10.0 Da

    Raises:
        ValueError: If features_df is None (call find_features() first).

    See Also:
        find_features: Detect features before linking MS2.
        find_ms2_defaults: Parameter configuration object.
        get_spectrum: Retrieve individual MS2 spectra.
        identify: Match features to spectral library using MS2.
        export_mgf: Export MS2 spectra in MGF format.
    """

    # parameters initialization
    params = find_ms2_defaults()
    for key, value in kwargs.items():
        if isinstance(value, find_ms2_defaults):
            params = value
            self.logger.debug("Using provided find_ms2_defaults parameters")
        elif hasattr(params, key):
            if params.set(key, value, validate=True):
                self.logger.debug(f"Updated parameter {key} = {value}")
            else:
                self.logger.warning(
                    f"Failed to set parameter {key} = {value} (validation failed)",
                )
        else:
            self.logger.debug(f"Unknown parameter {key} ignored")
    # end of parameter initialization

    # Extract parameter values
    features = params.get("features")
    mz_tol = params.get_mz_tolerance(self.type)
    centroid = params.get("centroid")
    deisotope = params.get("deisotope")
    dia_stats = params.get("dia_stats")

    self.logger.debug("Starting MS2 spectra linking...")
    self.logger.debug(
        f"Parameters: mz_tol={mz_tol}, centroid={centroid}, deisotope={deisotope}",
    )

    # Ensure features_df is loaded and has the MS2 columns
    if self.features_df is None:
        self.logger.error("Please find features first.")
        return
    if "ms2_scans" not in self.features_df.columns:
        self.features_df["ms2_scans"] = None
    if "ms2_specs" not in self.features_df.columns:
        self.features_df["ms2_specs"] = None

    feature_id_list = []
    self.logger.debug("Building lookup lists")
    if features == []:
        features = None  # If empty list, treat as None
    feature_id_list = self._get_feature_ids(features)

    if len(feature_id_list) == 0:
        self.logger.warning("No features to process.")
        return

    ms2_df = self.scans_df.filter(pl.col("ms_level") == 2)
    if len(ms2_df) == 0:
        self.logger.warning("No MS2 spectra found in file.")
        return

    ms2_index_arr = ms2_df["scan_id"].to_numpy()
    ms2_rt = ms2_df["rt"].to_numpy()
    ms2_precursor = ms2_df["prec_mz"].to_numpy()
    ms2_cycle = ms2_df["cycle"].to_numpy()

    features_df = self.features_df
    c = 0

    if self.file_interface is None:
        self.index_raw()

    # Vectorize the entire operation for better performance
    features_subset = features_df.filter(pl.col("feature_id").is_in(feature_id_list))

    if len(features_subset) == 0:
        return

    # Convert to numpy arrays for vectorized operations
    feature_rt = features_subset.select("rt").to_numpy().flatten()
    feature_mz = features_subset.select("mz").to_numpy().flatten()
    feature_rt_start = features_subset.select("rt_start").to_numpy().flatten()
    feature_rt_end = features_subset.select("rt_end").to_numpy().flatten()
    feature_ids = features_subset.select("feature_id").to_numpy().flatten()
    feature_indices = (
        features_subset.with_row_index().select("index").to_numpy().flatten()
    )

    # Pre-compute RT radius for all features
    rt_radius = np.minimum(feature_rt - feature_rt_start, feature_rt_end - feature_rt)

    # Batch process all features
    scan_id_lists: list[list[int] | None] = []
    spec_lists: list[list[Spectrum] | None] = []
    updated_feature_ids = []
    updated_scan_ids = []

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    for i, (rt_center, mz_center, radius, feature_id, idx) in enumerate(
        tqdm(
            zip(
                feature_rt,
                feature_mz,
                rt_radius,
                feature_ids,
                feature_indices,
                strict=False,
            ),
            total=len(features_subset),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Link MS2 spectra",
            disable=tdqm_disable,
        ),
    ):
        # Vectorized filtering
        rt_mask = np.abs(ms2_rt - rt_center) <= radius
        mz_mask = np.abs(ms2_precursor - mz_center) <= mz_tol
        valid_mask = rt_mask & mz_mask

        if not np.any(valid_mask):
            scan_id_lists.append(None)
            spec_lists.append(None)
            continue

        valid_indices = np.nonzero(valid_mask)[0]
        rt_diffs = np.abs(ms2_rt[valid_indices] - rt_center)
        sorted_indices = valid_indices[np.argsort(rt_diffs)]

        # Get unique cycles and their first occurrences
        cycles = ms2_cycle[sorted_indices]
        _, first_idx = np.unique(cycles, return_index=True)
        final_indices = sorted_indices[first_idx]

        # Sort by RT difference again
        final_rt_diffs = np.abs(ms2_rt[final_indices] - rt_center)
        final_indices = final_indices[np.argsort(final_rt_diffs)]

        scan_ids = ms2_index_arr[final_indices].tolist()
        scan_id_lists.append(scan_ids)
        spec_lists.append(
            [
                self.get_spectrum(
                    scan_ids[0],
                    centroid=centroid,
                    deisotope=deisotope,
                    dia_stats=dia_stats,
                    feature_id=feature_id,
                ),
            ],
        )

        # Collect updates for batch processing
        updated_feature_ids.extend([feature_id] * len(final_indices))
        updated_scan_ids.extend(ms2_index_arr[final_indices])
        c += 1

    self.logger.debug("Update features.")
    # Convert to polars if needed and batch update features_df
    # Convert to polars if needed and batch update features_df
    if not isinstance(features_df, pl.DataFrame):
        features_df = pl.from_pandas(features_df)

    # Update the features_df
    update_df = pl.DataFrame(
        {
            "temp_idx": feature_indices,
            "ms2_scans": pl.Series("ms2_scans", scan_id_lists, dtype=pl.Object),
            "ms2_specs": pl.Series("ms2_specs", spec_lists, dtype=pl.Object),
        },
    )

    # Join and update
    features_df = (
        features_df.with_row_index("temp_idx")
        .join(
            update_df,
            on="temp_idx",
            how="left",
            suffix="_new",
        )
        .with_columns(
            [
                pl.when(pl.col("ms2_scans_new").is_not_null())
                .then(pl.col("ms2_scans_new"))
                .otherwise(pl.col("ms2_scans"))
                .alias("ms2_scans"),
                pl.when(pl.col("ms2_specs_new").is_not_null())
                .then(pl.col("ms2_specs_new"))
                .otherwise(pl.col("ms2_specs"))
                .alias("ms2_specs"),
            ],
        )
        .drop(["temp_idx", "ms2_scans_new", "ms2_specs_new"])
    )

    # Batch update scans_df
    if updated_scan_ids:
        scan_feature_id_updates = dict(
            zip(updated_scan_ids, updated_feature_ids, strict=True),
        )

        # Check if feature_id column exists, if not initialize it
        if "feature_id" not in self.scans_df.columns:
            self.scans_df = self.scans_df.with_columns(
                pl.lit(None, dtype=pl.Int64).alias("feature_id"),
            )

        self.scans_df = (
            self.scans_df.with_columns(
                pl.col("scan_id")
                .map_elements(
                    lambda x: scan_feature_id_updates.get(x),
                    return_dtype=pl.Int64,
                )
                .alias("feature_id_update"),
            )
            .with_columns(
                pl.when(pl.col("feature_id_update").is_not_null())
                .then(pl.col("feature_id_update"))
                .otherwise(pl.col("feature_id"))
                .alias("feature_id"),
            )
            .drop("feature_id_update")
        )

    # Log completion
    self.logger.success(
        f"MS2 linking completed. Features with MS2 data: {c}.",
    )
    self.features_df = features_df

    # store params
    self.update_history(["find_ms2"], params.to_dict())
    self.logger.debug(
        "Parameters stored to find_ms2",
    )


def find_iso(self, rt_tolerance: float = 0.1, **kwargs):
    """Extract isotopic distributions from MS1 data and add to features_df.

    This method processes each feature to find isotopic distributions from MS1 data,
    similar to the study.find_iso() method but for individual samples. The method
    adds a new 'ms1_spec' column to features_df containing numpy arrays with
    isotopic distribution data.

    Args:
        rt_tolerance (float): RT tolerance in minutes for matching MS1 scans. Default 0.1.
        **kwargs: Additional parameters

    Notes:
        - Adds a new 'ms1_spec' column to features_df containing numpy arrays
        - Each array contains [mz, intensity] pairs for the isotopic distribution
        - Uses the same isotope shift pattern as study.find_iso()
        - Only processes features that don't already have ms1_spec data
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features found. Run find_features() first.")
        return

    if self.ms1_df is None or self.ms1_df.is_empty():
        self.logger.warning("No MS1 data found.")
        return

    # Check if ms1_spec column already exists
    if "ms1_spec" in self.features_df.columns:
        features_without_spec = self.features_df.filter(pl.col("ms1_spec").is_null())
        if features_without_spec.is_empty():
            self.logger.info("All features already have isotopic distributions.")
            return
        self.logger.info(
            f"Processing {len(features_without_spec)} features without isotopic distributions.",
        )
    else:
        # Add the ms1_spec column with None values
        self.features_df = self.features_df.with_columns(
            pl.lit(None, dtype=pl.Object).alias("ms1_spec"),
        )
        features_without_spec = self.features_df
        self.logger.info(
            f"Processing {len(features_without_spec)} features for isotopic distributions.",
        )

    # Define isotope shifts (same as study.find_iso)
    isotope_shifts = np.array(
        [
            0.33,
            0.50,
            0.66,
            1.00335,
            1.50502,
            2.00670,
            3.01005,
            4.01340,
            5.01675,
            6.02010,
            7.02345,
        ],
    )

    # Convert rt_tolerance from minutes to seconds
    rt_tolerance_s = rt_tolerance * 60

    # Process each feature
    ms1_specs: list[Spectrum | None] = []
    feature_indices = []

    for i, row in enumerate(
        tqdm(
            features_without_spec.rows(named=True),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Extracting isotope patterns",
        ),
    ):
        feature_rt = row["rt"]
        feature_mz = row["mz"]

        # Find MS1 scans within RT tolerance
        rt_mask = (self.ms1_df["rt"] >= (feature_rt - rt_tolerance_s)) & (
            self.ms1_df["rt"] <= (feature_rt + rt_tolerance_s)
        )
        ms1_in_range = self.ms1_df.filter(rt_mask)

        if ms1_in_range.is_empty():
            ms1_specs.append(None)
            feature_indices.append(row["feature_id"])
            continue

        # Extract isotopic pattern
        isotope_pattern = []

        # Start with the monoisotopic peak (M+0)
        base_intensity = 0
        mz_tolerance = 0.01  # 10 ppm at 1000 Da

        # Find the base peak intensity
        base_mask = (ms1_in_range["mz"] >= (feature_mz - mz_tolerance)) & (
            ms1_in_range["mz"] <= (feature_mz + mz_tolerance)
        )
        base_peaks = ms1_in_range.filter(base_mask)

        if not base_peaks.is_empty():
            base_intensity = base_peaks["inty"].max()
            isotope_pattern.append([feature_mz, base_intensity])

        # Look for isotope peaks
        for shift in isotope_shifts:
            isotope_mz = feature_mz + shift
            isotope_mask = (ms1_in_range["mz"] >= (isotope_mz - mz_tolerance)) & (
                ms1_in_range["mz"] <= (isotope_mz + mz_tolerance)
            )
            isotope_peaks = ms1_in_range.filter(isotope_mask)

            if not isotope_peaks.is_empty():
                max_intensity = isotope_peaks["inty"].max()
                # Only keep isotope peaks that are at least 1% of base peak
                if base_intensity > 0 and max_intensity >= 0.01 * base_intensity:
                    # Get the mz of the most intense peak
                    max_peak = isotope_peaks.filter(
                        pl.col("inty") == max_intensity,
                    ).row(0, named=True)
                    isotope_pattern.append([max_peak["mz"], max_intensity])

        # Convert to numpy array or None if empty
        if (
            len(isotope_pattern) > 1
        ):  # Need at least 2 points (monoisotopic + 1 isotope)
            ms1_spec = np.array(isotope_pattern, dtype=np.float64)
        else:
            ms1_spec = None

        ms1_specs.append(ms1_spec)
        feature_indices.append(row["feature_id"])

    # Update the features_df with the isotopic spectra
    update_df = pl.DataFrame(
        {
            "feature_id": feature_indices,
            "ms1_spec_new": pl.Series("ms1_spec_new", ms1_specs, dtype=pl.Object),
        },
    )

    # Join and update
    self.features_df = (
        self.features_df.join(update_df, on="feature_id", how="left")
        .with_columns(
            [
                pl.when(pl.col("ms1_spec_new").is_not_null())
                .then(pl.col("ms1_spec_new"))
                .otherwise(pl.col("ms1_spec"))
                .alias("ms1_spec"),
            ],
        )
        .drop("ms1_spec_new")
    )

    # Log results
    non_null_count = len([spec for spec in ms1_specs if spec is not None])
    self.logger.success(
        f"Extracted isotopic distributions for {non_null_count}/{len(ms1_specs)} features.",
    )

    # Store parameters in history
    params_dict = {"rt_tolerance": rt_tolerance}
    params_dict.update(kwargs)
    self.update_history(["find_iso"], params_dict)
