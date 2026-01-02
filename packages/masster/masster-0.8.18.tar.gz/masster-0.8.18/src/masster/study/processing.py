# mypy: disable-error-code="misc,no-any-return,assignment,attr-defined"
from __future__ import annotations

from datetime import datetime

import numpy as np
import polars as pl
import pyopenms as oms
from tqdm import tqdm

from masster.exceptions import (
    AlignmentError,
    DataValidationError,
    ProcessingError,
    SampleNotFoundError,
)
from masster.study.defaults import (
    align_defaults,
    find_ms2_defaults,
    integrate_defaults,
)


def align(self, **kwargs) -> None:
    """Align feature retention times across samples using PoseClustering or KD-tree algorithm.

    Cross-sample retention time alignment corrects for chromatographic shifts between runs.
    Original retention times are preserved in rt_original column. Alignment invalidates
    existing consensus features, which must be regenerated with merge().

    Args:
        **kwargs: Alignment parameters. Can provide an align_defaults instance via params=,
            or specify individual parameters:

            **Algorithm Selection:**
                algorithm (str): Alignment algorithm. Options:
                    - "pc": PoseClustering (OpenMS MapAlignerPoseClustering)
                    - "kd": KD-tree with LOWESS warping
                    Defaults to "kd".

            **Tolerance Parameters:**
                rt_tol (float): Maximum retention time difference for feature pairing
                    in seconds. Defaults to 5.0.
                mz_max_diff (float): Maximum m/z difference for feature pairing in Da.
                    Defaults to 0.01.

            **PoseClustering Algorithm (algorithm="pc"):**
                rt_pair_distance_frac (float): Fraction of RT difference used by
                    superimposer for pair distance calculation. Defaults to 0.5.
                mz_pair_max_distance (float): Maximum m/z distance for pair selection
                    in Da. Defaults to 0.01.
                num_used_points (int): Number of anchor points for alignment estimation.
                    Defaults to 1000.

            **KD-tree Algorithm (algorithm="kd"):**
                warp_mz_tol (float): m/z tolerance for LOWESS fit in Da. Defaults to 0.05.

            **General Options:**
                save_features (bool): Save updated features after alignment. Defaults to False.
                skip_blanks (bool): Skip blank samples during alignment. Defaults to False.
                params (align_defaults): Pre-configured parameter object. If provided,
                    other parameters are ignored.

    Example:
        Basic alignment::

            >>> study.align()
            >>> study.plot_alignment()

        Custom parameters::

            >>> study.align(algorithm="pc", rt_tol=10.0, mz_max_diff=0.015)

        Using parameter object::

            >>> from masster.study.defaults import align_defaults
            >>> params = align_defaults(algorithm="kd", rt_tol=8.0)
            >>> study.align(params=params)

    Note:
        - Alignment creates rt_original column if it doesn't exist
        - Existing consensus features, mappings, MS2 spectra, and identifications are reset
        - merge() and find_ms2() history entries are removed (must be re-run)
        - Use plot_alignment() to visualize alignment quality

    See Also:
        align_defaults: Parameter configuration for alignment.
        align_reset: Revert to original retention times.
        plot_alignment: Visualize alignment results.
        merge: Generate consensus features after alignment.
    """
    # parameters initialization
    params = align_defaults()

    # Handle 'params' keyword argument specifically (like merge does)
    if "params" in kwargs:
        provided_params = kwargs.pop("params")
        if isinstance(provided_params, align_defaults):
            params = provided_params
            self.logger.debug(
                "Using provided align_defaults parameters from 'params' argument",
            )
        else:
            self.logger.warning(
                "'params' argument is not an align_defaults instance, ignoring",
            )

    # Process remaining kwargs
    for key, value in kwargs.items():
        if isinstance(value, align_defaults):
            params = value
            self.logger.debug("Using provided align_defaults parameters")
        elif hasattr(params, key):
            if params.set(key, value, validate=True):
                self.logger.debug(f"Updated parameter {key} = {value}")
            else:
                self.logger.warning(
                    f"Failed to set parameter {key} = {value} (validation failed)",
                )
        else:
            self.logger.warning(f"Unknown parameter '{key}' ignored")

    # Check if study has at least two samples
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning(
            "Study has no samples loaded. Please load samples before alignment.",
        )
        return

    if len(self.samples_df) < 2:
        self.logger.warning(
            f"Alignment requires at least 2 samples, but only {len(self.samples_df)} loaded. "
            "Please load more samples before alignment.",
        )
        return

    # Store parameters in the Study object
    self.update_history(["align"], params.to_dict())
    self.logger.debug("Parameters stored to align")

    # Ensure rt_original exists before starting alignment (both algorithms need this)
    if "rt_original" not in self.features_df.columns:
        # add column 'rt_original' after 'rt'
        rt_index = self.features_df.columns.index("rt") + 1
        self.features_df.insert(rt_index, "rt_original", 0)
        self.features_df["rt_original"] = self.features_df["rt"]
        self.logger.debug("Created rt_original column from current rt values")

    # Choose alignment algorithm
    algorithm = params.get("algorithm").lower()

    if algorithm == "pc":
        _align_pose_clustering(self, params)

    elif algorithm == "kd":
        _align_kd_algorithm(self, params)
    else:
        self.logger.error(f"Unknown alignment algorithm '{algorithm}'")
        return

    # Reset consensus data structures after alignment since RT changes invalidate consensus
    consensus_reset_count = 0
    if not self.consensus_df.is_empty():
        self.consensus_df = pl.DataFrame()
        consensus_reset_count += 1
    if not self.consensus_mapping_df.is_empty():
        self.consensus_mapping_df = pl.DataFrame()
        consensus_reset_count += 1
    if not self.consensus_ms2.is_empty():
        self.consensus_ms2 = pl.DataFrame()
        consensus_reset_count += 1
    if not self.id_df.is_empty():
        self.id_df = pl.DataFrame()
        consensus_reset_count += 1

    # Remove merge and find_ms2 parameters from history since they need to be re-run
    keys_to_remove = ["merge", "find_ms2"]
    history_removed_count = 0
    if hasattr(self, "history") and self.history:
        for key in keys_to_remove:
            if key in self.history:
                del self.history[key]
                history_removed_count += 1
                self.logger.debug(f"Removed {key} from history")

    if consensus_reset_count > 0 or history_removed_count > 0:
        self.logger.debug(
            f"Alignment reset: {consensus_reset_count} consensus structures cleared, {history_removed_count} history entries removed",
        )

    if params.get("save_features"):
        self.save_samples()


def find_ms2(self, **kwargs) -> None:
    """Link MS2 fragmentation spectra to consensus features.

    Associates MS2 spectra from individual samples to their corresponding consensus
    features. MS2 spectra are essential for compound identification and structural
    elucidation.

    Args:
        **kwargs: MS2 linking parameters. Can provide a find_ms2_defaults instance
            via params=, or specify individual parameters:

            **Advanced:**
                params (find_ms2_defaults): Pre-configured parameter object.
                    If provided, other parameters are ignored.

            Note: Current implementation has no user-configurable parameters.
                MS2 linking uses pre-existing MS2 associations from Sample.find_ms2()
                that were called during individual sample processing.

    Example:
        Basic MS2 linking::

            >>> study.find_ms2()
            >>> print(f"Found {len(study.consensus_ms2)} MS2 spectra")

        Check MS2 coverage::

            >>> import polars as pl
            >>> consensus_with_ms2 = study.consensus_ms2["consensus_id"].n_unique()
            >>> total_consensus = len(study.consensus_df)
            >>> coverage = consensus_with_ms2 / total_consensus * 100
            >>> print(f"MS2 coverage: {coverage:.1f}%")

        Export MS2 for identification::

            >>> study.export_mgf("output.mgf")

        Filter high-quality MS2::

            >>> high_quality_ms2 = study.consensus_ms2.filter(
            ...     (pl.col("number_frags") > 3) &
            ...     (pl.col("inty") > 1e5)
            ... )

    Note:
        - Run after merge() to link MS2 to consensus features
        - Requires Sample.find_ms2() to have been called on individual samples
        - Results stored in consensus_ms2 DataFrame with columns:
            - consensus_id: Consensus feature ID
            - sample_id: Source sample ID
            - feature_id: Original feature ID
            - scanid: MS2 scan number
            - inty: Precursor intensity
            - chrom_coherence: Chromatographic quality
            - chrom_prominence_scaled: Peak prominence
            - number_frags: Fragment count
            - spec: Spectrum object with mz/inty arrays
        - Essential prerequisite for identify() method
        - MS2 spectra can be visualized with plot_ms2()

    Raises:
        RuntimeError: If consensus_mapping_df is empty (merge() not run).

    See Also:
        find_ms2_defaults: Parameter configuration (currently no parameters).
        Sample.find_ms2: Link MS2 in individual samples.
        identify: Identify consensus features using MS2.
        export_mgf: Export MS2 spectra for external tools.
        plot_ms2: Visualize MS2 spectra.
    """
    # Reset consensus_ms2 DataFrame at the start
    self.consensus_ms2 = pl.DataFrame()

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

    # Store parameters in the Study object
    self.update_history(["find_ms2"], params.to_dict())
    self.logger.debug("Parameters stored to find_ms2")

    data = []
    if self.consensus_mapping_df.is_empty():
        self.logger.error(
            "No consensus mapping found. Please run merge() first.",
        )
        return
    self.logger.info("Linking MS2 spectra to consensus features...")

    # Build fast lookup for feature_id to features_df row data
    feats = self.features_df
    feature_lookup = {}
    relevant_cols = [
        "ms2_specs",
        "ms2_scans",
        "inty",
        "chrom_coherence",
        "chrom_prominence_scaled",
    ]
    for row in feats.iter_rows(named=True):
        feature_id = row["feature_id"]
        feature_lookup[feature_id] = {
            col: row[col] for col in relevant_cols if col in feats.columns
        }
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    # Process consensus mapping in batch
    for mapping_row in tqdm(
        self.consensus_mapping_df.iter_rows(named=True),
        total=self.consensus_mapping_df.shape[0],
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}MS2 spectra",
        disable=tdqm_disable,
    ):
        feature_id = mapping_row["feature_id"]
        feature_data = feature_lookup.get(feature_id)
        if feature_data is None or feature_data.get("ms2_specs") is None:
            continue
        ms2_specs = feature_data["ms2_specs"]
        ms2_scans = feature_data["ms2_scans"]
        inty = feature_data.get("inty")
        chrom_coherence = feature_data.get("chrom_coherence")
        chrom_prominence_scaled = feature_data.get("chrom_prominence_scaled")
        for j in range(len(ms2_specs)):
            spec = ms2_specs[j]
            scanid = ms2_scans[j]
            data.append(
                {
                    "consensus_id": int(mapping_row["consensus_id"]),
                    "feature_id": int(mapping_row["feature_id"]),
                    "sample_id": int(mapping_row["sample_id"]),
                    "scan_id": int(scanid),
                    "energy": round(spec.energy, 1)
                    if hasattr(spec, "energy") and spec.energy is not None
                    else None,
                    "prec_inty": round(inty, 0) if inty is not None else None,
                    "prec_coherence": round(chrom_coherence, 3)
                    if chrom_coherence is not None
                    else None,
                    "prec_prominence_scaled": round(chrom_prominence_scaled, 3)
                    if chrom_prominence_scaled is not None
                    else None,
                    "number_frags": len(spec.mz),
                    "spec": spec,
                },
            )
    self.consensus_ms2 = pl.DataFrame(data)
    if not self.consensus_ms2.is_empty():
        unique_consensus_features = self.consensus_ms2["consensus_id"].n_unique()
    else:
        unique_consensus_features = 0
    self.logger.success(
        f"Linking completed. Found {len(self.consensus_ms2)} MS2 spectra associated to {unique_consensus_features} consensus features.",
    )


def _integrate_chrom_impl(self, **kwargs):
    """Integrate chromatogram intensities for consensus features.

    Integrates EICs for consensus features using parameters defined in
    :class:`integrate_defaults`. Pass an ``integrate_defaults`` instance via
    ``**kwargs`` or override individual parameters (they will be validated
    against the defaults class).

    Main parameters (from ``integrate_defaults``):

    - uids (Optional[list]): List of consensus UIDs to integrate; ``None`` means all.
    - rt_tol (float): RT tolerance (seconds) used when locating integration boundaries.

    Notes:
        This function batches updates to the study's feature table for efficiency.
    """
    # parameters initialization
    params = integrate_defaults()
    for key, value in kwargs.items():
        if isinstance(value, integrate_defaults):
            params = value
            self.logger.debug("Using provided integrate_chrom_defaults parameters")
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

    # Store parameters in the Study object
    self.update_history(["integrate_chrom"], params.to_dict())
    self.logger.debug("Parameters stored to integrate_chrom")

    # Get parameter values for use in the method
    uids = params.get("uids")
    rt_tol = params.get("rt_tol")

    if uids is None:
        # get all consensus_id from consensus_df
        ids = self.consensus_df["consensus_id"].to_list()
    else:
        # keep only id that are in consensus_df
        ids = [i for i in uids if i in self.consensus_df["consensus_id"].to_list()]

    # Ensure chrom_area column is Float64 to avoid dtype conflicts
    if "chrom_area" in self.features_df.columns:
        self.features_df = self.features_df.with_columns(
            pl.col("chrom_area").cast(pl.Float64, strict=False),
        )

    # Merge consensus_mapping with consensus_df to get rt_start_mean and rt_end_mean
    # Use Polars join operation instead of pandas merge
    consensus_subset = self.consensus_df.select(
        [
            "consensus_id",
            "rt_start_mean",
            "rt_end_mean",
        ],
    )
    df1 = self.consensus_mapping_df.join(
        consensus_subset,
        on="consensus_id",
        how="left",
    )
    df1 = df1.filter(pl.col("consensus_id").is_in(ids))

    # Build a fast lookup for feature_id to row index in features_df
    # Since Polars doesn't have index-based access like pandas, we'll use row position
    feature_id_to_row = {}
    for i, row_dict in enumerate(self.features_df.iter_rows(named=True)):
        if "feature_id" in row_dict:
            feature_id_to_row[row_dict["feature_id"]] = i
        elif "uid" in row_dict:  # fallback column name
            feature_id_to_row[row_dict["uid"]] = i

    # Prepare lists for batch update
    update_rows = []
    chroms: list = []
    rt_starts: list[float] = []
    rt_ends: list[float] = []
    rt_deltas: list[float] = []
    chrom_areas = []

    self.logger.debug(f"Integrating {df1.shape[0]} features using consensus...")
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for row in tqdm(
        df1.iter_rows(named=True),
        total=df1.shape[0],
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Integrate EICs by consensus",
        disable=tdqm_disable,
    ):
        feature_id = row["feature_id"]
        row_idx = feature_id_to_row.get(feature_id)
        if row_idx is None:
            continue

        # Get the feature row from Polars DataFrame
        feature_row = self.features_df.row(row_idx, named=True)
        # get chromatogram for the feature
        chrom = feature_row["chrom"]
        if chrom is None or len(chrom) == 0:
            update_rows.append(row_idx)
            chroms.append(None)
            rt_starts.append(float("nan"))
            rt_ends.append(float("nan"))
            rt_deltas.append(float("nan"))
            chrom_areas.append(-1.0)
            continue
        rt_start = _find_closest_valley(
            chrom,
            row["rt_start_mean"] - rt_tol,
            dir="left",
            threshold=0.9,
        )
        rt_end = _find_closest_valley(
            chrom,
            row["rt_end_mean"] + rt_tol,
            dir="right",
            threshold=0.9,
        )
        chrom.feature_start = rt_start
        chrom.feature_end = rt_end
        chrom.integrate()
        update_rows.append(row_idx)
        chroms.append(chrom)
        rt_starts.append(rt_start)
        rt_ends.append(rt_end)
        rt_deltas.append(rt_end - rt_start)
        chrom_areas.append(float(chrom.feature_area))

    # Batch update DataFrame - Polars style
    if update_rows:
        # Create mapping from row index to new values
        row_to_chrom = {update_rows[i]: chroms[i] for i in range(len(update_rows))}
        row_to_rt_start = {
            update_rows[i]: rt_starts[i] for i in range(len(update_rows))
        }
        row_to_rt_end = {update_rows[i]: rt_ends[i] for i in range(len(update_rows))}
        row_to_rt_delta = {
            update_rows[i]: rt_deltas[i] for i in range(len(update_rows))
        }
        row_to_chrom_area = {
            update_rows[i]: float(chrom_areas[i]) if chrom_areas[i] is not None else 0.0
            for i in range(len(update_rows))
        }

        # Use with_row_index to create a temporary row index column
        df_with_index = self.features_df.with_row_index("__row_idx")

        # Create update masks and values
        update_mask = pl.col("__row_idx").is_in(update_rows)

        # Update columns conditionally
        try:
            self.features_df = df_with_index.with_columns(
                [
                    # Update chrom column - use when() to update only specific rows
                    pl.when(update_mask)
                    .then(
                        pl.col("__row_idx").map_elements(
                            lambda x: row_to_chrom.get(x),
                            return_dtype=pl.Object,
                        ),
                    )
                    .otherwise(pl.col("chrom"))
                    .alias("chrom"),
                    # Update chrom_start column (new - integration boundaries)
                    pl.when(update_mask)
                    .then(
                        pl.col("__row_idx").map_elements(
                            lambda x: row_to_rt_start.get(x),
                            return_dtype=pl.Float64,
                        ),
                    )
                    .otherwise(
                        pl.col("chrom_start")
                        if "chrom_start" in df_with_index.columns
                        else None,
                    )
                    .alias("chrom_start"),
                    # Update chrom_end column (new - integration boundaries)
                    pl.when(update_mask)
                    .then(
                        pl.col("__row_idx").map_elements(
                            lambda x: row_to_rt_end.get(x),
                            return_dtype=pl.Float64,
                        ),
                    )
                    .otherwise(
                        pl.col("chrom_end")
                        if "chrom_end" in df_with_index.columns
                        else None,
                    )
                    .alias("chrom_end"),
                    # Update rt_delta column
                    pl.when(update_mask)
                    .then(
                        pl.col("__row_idx").map_elements(
                            lambda x: row_to_rt_delta.get(x),
                            return_dtype=pl.Float64,
                        ),
                    )
                    .otherwise(pl.col("rt_delta"))
                    .alias("rt_delta"),
                    # Update chrom_area column
                    pl.when(update_mask)
                    .then(
                        pl.col("__row_idx").map_elements(
                            lambda x: row_to_chrom_area.get(x, 0),
                            return_dtype=pl.Float64,
                        ),
                    )
                    .otherwise(pl.col("chrom_area"))
                    .alias("chrom_area"),
                ],
            ).drop("__row_idx")  # Remove the temporary row index column

            self.logger.debug(
                f"Integration step completed. Updated {len(update_rows)} features with chromatogram data.",
            )
        except Exception as e:
            self.logger.error(f"Failed to update features DataFrame: {e}")
    else:
        self.logger.debug("No features were updated during integration.")


def integrate(self, **kwargs) -> None:
    """Integrate chromatograms to calculate peak areas and quality metrics.

    Calculates area under the curve (AUC) for each feature using consensus RT
    boundaries. Also computes quality metrics like chromatographic coherence
    and prominence to help identify low-quality signals.

    Args:
        **kwargs: Integration parameters. Can provide an integrate_defaults instance
            via params=, or specify individual parameters:

            **Feature Selection:**
                uids (list[int] | None): Consensus IDs to integrate. None processes all.
                    Defaults to None.

            **Integration Window:**
                rt_tol (float): Retention time tolerance in seconds for integration
                    window adjustment. Defaults to None (uses consensus boundaries).

            **Advanced:**
                params (integrate_defaults): Pre-configured parameter object.
                    If provided, other parameters are ignored.

    Example:
        Basic integration::

            >>> study.integrate()
            >>> study.features_df.select([
            ...     "feature_id", "chrom_area", "chrom_coherence"
            ... ]).head()

        Filter by quality metrics::

            >>> import polars as pl
            >>> high_quality = study.features_df.filter(
            ...     (pl.col("chrom_coherence") > 0.7) &
            ...     (pl.col("chrom_prominence_scaled") > 0.5)
            ... )
            >>> print(f"High quality features: {len(high_quality)}")

        Integrate specific features::

            >>> target_ids = study.consensus_df.filter(
            ...     pl.col("number_samples") > 50
            ... )["consensus_id"].to_list()
            >>> study.integrate(uids=target_ids)

    Note:
        - Run after merge() and fill() in typical workflow
        - Uses consensus RT boundaries (rt_start_mean, rt_end_mean)
        - Updates features_df with integration results:
            - chrom_area: Integrated peak area
            - chrom_coherence: Quality metric (0-1)
            - chrom_prominence_scaled: Prominence metric
            - chrom_sanity: Peak shape sanity check
        - Automatically runs chromatogram sanity check after integration
        - Quality metrics help identify poorly integrated peaks

    See Also:
        integrate_defaults: Parameter configuration for integration.
        fill: Fill missing features before integration.
        get_consensus_matrix: Extract quantification matrix.
        plot_chrom: Visualize individual chromatograms.
    """
    # parameters initialization
    params = integrate_defaults()
    for key, value in kwargs.items():
        if isinstance(value, integrate_defaults):
            params = value
            self.logger.debug("Using provided integrate_defaults parameters")
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

    # Store parameters in the Study object
    self.update_history(["integrate"], params.to_dict())
    self.logger.debug("Parameters stored to integrate")

    # Call the original integrate_chrom function with extracted parameters
    _integrate_chrom_impl(
        self,
        uids=params.get("uids"),
        rt_tol=params.get("rt_tol"),
    )

    # Run chromatogram sanity check
    _chrom_check(self)

    # Log success after both operations complete
    features_count = len(self.features_df) if self.features_df is not None else 0
    self.logger.success(
        f"Integration completed. Processed {features_count} features.",
    )


# Backward compatibility alias
integrate_chrom = integrate


def _compute_chrom_metrics(chrom, rt_start_mean, rt_end_mean, rt_start, rt_end):
    """Compute sanity and coherence metrics for a single chromatogram.

    Returns (sanity, coherence) tuple, or (None, None) if invalid.
    """
    if chrom is None:
        return None, None

    # Fast attribute check
    try:
        chrom_rt = chrom.rt
        chrom_inty = chrom.inty
        if len(chrom_rt) == 0:
            return None, None
    except (AttributeError, TypeError):
        return None, None

    # Convert to numpy arrays if needed (usually already are)
    if not isinstance(chrom_rt, np.ndarray):
        chrom_rt = np.asarray(chrom_rt, dtype=np.float64)
        chrom_inty = np.asarray(chrom_inty, dtype=np.float64)

    # Find indices for RT window using searchsorted (faster than argmin for sorted arrays)
    start_idx = np.searchsorted(chrom_rt, rt_start_mean)
    end_idx = np.searchsorted(chrom_rt, rt_end_mean)

    # Clamp indices
    start_idx = max(0, min(start_idx, len(chrom_rt) - 1))
    end_idx = max(start_idx, min(end_idx, len(chrom_rt) - 1))

    # Find apex within this window
    window_inty = chrom_inty[start_idx : end_idx + 1]
    if len(window_inty) == 0:
        return 0.0, 0.0

    local_apex_idx = np.argmax(window_inty)
    apex_idx = start_idx + local_apex_idx
    apex_rt = chrom_rt[apex_idx]
    apex_inty = chrom_inty[apex_idx]

    # Check if apex RT is within consensus boundaries
    if not (rt_start_mean < apex_rt < rt_end_mean):
        return 0.0, 0.0

    # Use feature rt_start/rt_end if available, otherwise use consensus means
    if rt_start is None or (isinstance(rt_start, float) and np.isnan(rt_start)):
        rt_start = rt_start_mean
    if rt_end is None or (isinstance(rt_end, float) and np.isnan(rt_end)):
        rt_end = rt_end_mean

    # Get mask for chromatogram between rt_start and rt_end
    mask = (chrom_rt >= rt_start) & (chrom_rt <= rt_end)
    mask_sum = mask.sum()

    if mask_sum < 3:
        return 0.0, 0.0

    masked_inty = chrom_inty[mask]
    masked_rt = chrom_rt[mask]

    # Calculate coherence: 1 - (zero crossings of derivative) / (n - 3)
    if len(masked_inty) > 3:
        diff1 = np.diff(masked_inty)
        sign_diff = np.sign(diff1)
        zero_crossings = np.sum(np.diff(sign_diff) != 0)
        coherence = 1.0 - zero_crossings / (len(masked_inty) - 3)
    else:
        coherence = 0.0

    # Find apex index within masked window using searchsorted
    masked_apex_idx = np.searchsorted(masked_rt, apex_rt)
    masked_apex_idx = min(masked_apex_idx, len(masked_rt) - 1)

    # Count monotonic violations
    total_transitions = 0
    monotonic_violations = 0

    # Before apex: should be increasing or flat (diff >= 0)
    if masked_apex_idx > 0:
        diffs_before = np.diff(masked_inty[: masked_apex_idx + 1])
        total_transitions += len(diffs_before)
        monotonic_violations += int(np.sum(diffs_before < 0))

    # After apex: should be decreasing or flat (diff <= 0)
    if masked_apex_idx < len(masked_inty) - 1:
        diffs_after = np.diff(masked_inty[masked_apex_idx:])
        total_transitions += len(diffs_after)
        monotonic_violations += int(np.sum(diffs_after > 0))

    # Calculate monotonicity score
    if total_transitions > 0:
        monotonicity = 1.0 - (monotonic_violations / total_transitions)
    else:
        monotonicity = 0.0

    # Get intensity at boundaries using searchsorted
    bound_start_idx = np.searchsorted(chrom_rt, rt_start)
    bound_end_idx = np.searchsorted(chrom_rt, rt_end)
    bound_start_idx = min(bound_start_idx, len(chrom_rt) - 1)
    bound_end_idx = min(bound_end_idx, len(chrom_rt) - 1)

    inty_at_start = chrom_inty[bound_start_idx]
    inty_at_end = chrom_inty[bound_end_idx]

    # Calculate scaling factor: 1 - abs(inty_start - inty_end) / apex_inty
    if apex_inty > 0:
        boundary_diff = abs(inty_at_start - inty_at_end)
        scalar = max(0.0, min(1.0, 1.0 - boundary_diff / apex_inty))
    else:
        scalar = 0.0

    # Sanity = monotonicity * scalar
    sanity = round(monotonicity * scalar, 3)
    coherence = round(coherence, 3)

    return sanity, coherence


def _chrom_check(self, **kwargs):
    """Calculate chromatogram sanity values for all consensus features.

    For each feature, calculates a sanity value based on:
    1. Whether the apex (max intensity) RT falls within rt_start_mean and rt_end_mean
    2. The coherence of the chromatogram between rt_start and rt_end
    3. A scaling factor based on intensity difference at boundaries vs apex

    Results are stored in features_df.chrom_sanity, features_df.chrom_coherence,
    consensus_df.chrom_sanity_mean, and consensus_df.chrom_coherence_mean.
    """
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.warning("No consensus features found. Run merge() first.")
        return

    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features found.")
        return

    # Reset existing chrom_sanity and chrom_coherence columns to null
    if "chrom_sanity" in self.features_df.columns:
        self.features_df = self.features_df.with_columns(
            pl.lit(None).cast(pl.Float64).alias("chrom_sanity"),
        )
    if "chrom_coherence" in self.features_df.columns:
        self.features_df = self.features_df.with_columns(
            pl.lit(None).cast(pl.Float64).alias("chrom_coherence"),
        )

    # Get consensus info with rt boundaries
    consensus_subset = self.consensus_df.select(
        [
            "consensus_id",
            "rt_start_mean",
            "rt_end_mean",
        ],
    )

    # Join features with consensus mapping to get consensus boundaries
    features_with_consensus = self.features_df.join(
        self.consensus_mapping_df.select(["feature_id", "sample_id", "consensus_id"]),
        on=["feature_id", "sample_id"],
        how="left",
    ).join(
        consensus_subset,
        on="consensus_id",
        how="left",
    )

    # Filter to only features with consensus association (non-null rt boundaries)
    features_with_consensus = features_with_consensus.filter(
        pl.col("rt_start_mean").is_not_null() & pl.col("rt_end_mean").is_not_null(),
    )

    n_rows = features_with_consensus.shape[0]
    if n_rows == 0:
        self.logger.warning("No features with consensus associations found.")
        return

    # Extract columns as lists/arrays for faster iteration
    feature_ids = features_with_consensus["feature_id"].to_numpy()
    sample_ids = features_with_consensus["sample_id"].to_numpy()
    chroms = features_with_consensus["chrom"].to_list()
    rt_start_means = features_with_consensus["rt_start_mean"].to_numpy()
    rt_end_means = features_with_consensus["rt_end_mean"].to_numpy()

    # Get rt_start and rt_end columns
    if "rt_start" in features_with_consensus.columns:
        rt_starts = features_with_consensus["rt_start"].to_numpy()
    elif "chrom_start" in features_with_consensus.columns:
        rt_starts = features_with_consensus["chrom_start"].to_numpy()
    else:
        rt_starts = np.full(n_rows, np.nan)

    if "rt_end" in features_with_consensus.columns:
        rt_ends = features_with_consensus["rt_end"].to_numpy()
    elif "chrom_end" in features_with_consensus.columns:
        rt_ends = features_with_consensus["chrom_end"].to_numpy()
    else:
        rt_ends = np.full(n_rows, np.nan)

    # Pre-allocate result arrays for the filtered features
    sanity_values = np.empty(n_rows, dtype=np.float64)
    coherence_values = np.empty(n_rows, dtype=np.float64)
    sanity_values[:] = np.nan
    coherence_values[:] = np.nan

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    for i in tqdm(
        range(n_rows),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Sanity check",
        disable=tdqm_disable,
    ):
        sanity, coherence = _compute_chrom_metrics(
            chroms[i],
            rt_start_means[i],
            rt_end_means[i],
            rt_starts[i],
            rt_ends[i],
        )

        if sanity is not None:
            sanity_values[i] = sanity
            coherence_values[i] = coherence

    # Create a dataframe with results for the filtered features
    results_df = pl.DataFrame(
        {
            "feature_id": feature_ids,
            "sample_id": sample_ids,
            "chrom_sanity": sanity_values,
            "chrom_coherence": coherence_values,
        },
    )

    # Drop existing columns if present
    if "chrom_sanity" in self.features_df.columns:
        self.features_df = self.features_df.drop("chrom_sanity")
    if "chrom_coherence" in self.features_df.columns:
        self.features_df = self.features_df.drop("chrom_coherence")

    # Join results back to features_df (features without consensus will have null values)
    self.features_df = self.features_df.join(
        results_df,
        on=["feature_id", "sample_id"],
        how="left",
    )

    # Reorder columns to place chrom_sanity and chrom_coherence after mz_end_mean (if it exists)
    cols = self.features_df.columns
    if "mz_end_mean" in cols:
        # Remove the new columns from their current position
        cols_without_new = [
            c for c in cols if c not in ["chrom_sanity", "chrom_coherence"]
        ]
        # Find position after mz_end_mean
        insert_idx = cols_without_new.index("mz_end_mean") + 1
        # Insert new columns after mz_end_mean
        new_order = (
            cols_without_new[:insert_idx]
            + ["chrom_sanity", "chrom_coherence"]
            + cols_without_new[insert_idx:]
        )
        self.features_df = self.features_df.select(new_order)

    # Calculate mean sanity and coherence per consensus feature
    features_with_sanity = self.features_df.join(
        self.consensus_mapping_df.select(["feature_id", "sample_id", "consensus_id"]),
        on=["feature_id", "sample_id"],
        how="left",
    )

    means_df = features_with_sanity.group_by("consensus_id").agg(
        [
            pl.col("chrom_sanity").mean().alias("chrom_sanity_mean"),
            pl.col("chrom_coherence").mean().alias("chrom_coherence_mean"),
        ],
    )

    # Update consensus_df with mean values
    if "chrom_sanity_mean" in self.consensus_df.columns:
        self.consensus_df = self.consensus_df.drop("chrom_sanity_mean")
    if "chrom_coherence_mean" in self.consensus_df.columns:
        self.consensus_df = self.consensus_df.drop("chrom_coherence_mean")

    self.consensus_df = self.consensus_df.join(
        means_df,
        on="consensus_id",
        how="left",
    ).with_columns(
        [
            pl.col("chrom_sanity_mean").round(3),
            pl.col("chrom_coherence_mean").round(3),
        ],
    )

    # Reorder columns to place chrom_sanity_mean and chrom_coherence_mean after mz_end_mean (if it exists)
    cols = self.consensus_df.columns
    if "mz_end_mean" in cols:
        # Remove the new columns from their current position
        cols_without_new = [
            c for c in cols if c not in ["chrom_sanity_mean", "chrom_coherence_mean"]
        ]
        # Find position after mz_end_mean
        insert_idx = cols_without_new.index("mz_end_mean") + 1
        # Insert new columns after mz_end_mean
        new_order = (
            cols_without_new[:insert_idx]
            + ["chrom_sanity_mean", "chrom_coherence_mean"]
            + cols_without_new[insert_idx:]
        )
        self.consensus_df = self.consensus_df.select(new_order)

    self.logger.debug(
        f"Chromatogram sanity check completed for {n_rows} features.",
    )


def _find_closest_valley(chrom, rt, dir="left", threshold=0.9):
    """Find the closest valley in a chromatogram from a given RT position.

    Uses vectorized NumPy operations for efficiency.
    """
    chrom_rt = np.asarray(chrom.rt, dtype=np.float64)
    chrom_inty = np.asarray(chrom.inty, dtype=np.float64)
    idx = np.abs(chrom_rt - rt).argmin()

    if dir == "left":
        # Search leftward: find where intensity stops decreasing
        if idx == 0:
            return chrom_rt[0]
        # Get intensities from idx going left (reversed for easier processing)
        left_inty = chrom_inty[: idx + 1][::-1]  # reversed: idx, idx-1, ..., 0
        # Calculate ratio of each point to previous minimum
        cummin = np.minimum.accumulate(left_inty)
        # Find where intensity exceeds threshold * cumulative minimum
        exceeds = left_inty > cummin * (1.0 / threshold)
        exceeds[0] = False  # First point is always valid
        if exceeds.any():
            # Stop at first point that exceeds threshold
            stop_idx = np.argmax(exceeds)
            valley_idx = idx - (stop_idx - 1)
        else:
            # No break found, use leftmost point
            valley_idx = 0
    else:  # dir == "right"
        # Search rightward: find where intensity stops decreasing
        if idx >= len(chrom_inty) - 1:
            return chrom_rt[-1]
        # Get intensities from idx going right
        right_inty = chrom_inty[idx:]
        # Calculate cumulative minimum from the start
        cummin = np.minimum.accumulate(right_inty)
        # Find where intensity exceeds threshold * cumulative minimum
        exceeds = right_inty > cummin * (1.0 / threshold)
        exceeds[0] = False  # First point is always valid
        if exceeds.any():
            # Stop at first point that exceeds threshold
            stop_idx = np.argmax(exceeds)
            valley_idx = idx + (stop_idx - 1)
        else:
            # No break found, use rightmost point
            valley_idx = len(chrom_inty) - 1

    return chrom_rt[valley_idx]


def _align_pose_clustering(study_obj, params):
    """Perform alignment using PoseClustering algorithm."""
    from datetime import datetime

    import polars as pl
    import pyopenms as oms
    from tqdm import tqdm

    # Generate temporary feature maps on-demand from features_df for PoseClustering
    study_obj.logger.debug(
        "Generating feature maps on-demand from features_df for PoseClustering alignment",
    )

    tdqm_disable = study_obj.log_level not in ["TRACE", "DEBUG", "INFO"]
    fmaps: list = []
    sample_index_to_uid = {}  # Track mapping of feature map index to sample_id

    # Process each sample in order with progress bar
    for sample_index, row_dict in tqdm(
        list(enumerate(study_obj.samples_df.iter_rows(named=True))),
        total=len(study_obj.samples_df),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {study_obj.log_label}Generate feature maps",
        disable=tdqm_disable,
    ):
        sample_id = row_dict["sample_id"]
        sample_name = row_dict["sample_name"]
        sample_index_to_uid[len(fmaps)] = (
            sample_id  # Map feature map index to sample_id
        )

        # Get features for this sample from features_df
        sample_features = study_obj.features_df.filter(pl.col("sample_id") == sample_id)

        # Create new FeatureMap
        feature_map = oms.FeatureMap()

        # Convert DataFrame features to OpenMS Features
        for feature_row in sample_features.iter_rows(named=True):
            feature = oms.Feature()

            # Set properties from DataFrame (handle missing values gracefully)
            try:
                # Skip features with missing critical data
                if feature_row["mz"] is None:
                    study_obj.logger.warning("Skipping feature due to missing mz")
                    continue
                if feature_row["rt"] is None:
                    study_obj.logger.warning("Skipping feature due to missing rt")
                    continue
                if feature_row["inty"] is None:
                    study_obj.logger.warning("Skipping feature due to missing inty")
                    continue

                feature.setUniqueId(int(feature_row["feature_id"]))
                feature.setMZ(float(feature_row["mz"]))
                feature.setRT(float(feature_row["rt"]))
                feature.setIntensity(float(feature_row["inty"]))

                # Handle optional fields that might be None
                if feature_row.get("quality") is not None:
                    feature.setOverallQuality(float(feature_row["quality"]))
                if feature_row.get("charge") is not None:
                    feature.setCharge(int(feature_row["charge"]))

                # Add to feature map
                feature_map.push_back(feature)
            except (ValueError, TypeError) as e:
                study_obj.logger.warning(
                    f"Skipping feature due to conversion error: {e}",
                )
                continue

        fmaps.append(feature_map)

    study_obj.logger.debug(
        f"Generated {len(fmaps)} feature maps from features_df for PoseClustering alignment",
    )

    # Create PC-specific OpenMS parameters
    params_oms = oms.Param()
    params_oms.setValue("pairfinder:distance_intensity:log_transform", "disabled")
    params_oms.setValue("pairfinder:ignore_charge", "true")
    params_oms.setValue("max_num_peaks_considered", 1000)
    params_oms.setValue("pairfinder:distance_RT:max_difference", params.get("rt_tol"))
    params_oms.setValue(
        "pairfinder:distance_MZ:max_difference",
        params.get("mz_max_diff"),
    )
    params_oms.setValue(
        "superimposer:rt_pair_distance_fraction",
        params.get("rt_pair_distance_frac"),
    )
    params_oms.setValue(
        "superimposer:mz_pair_max_distance",
        params.get("mz_pair_max_distance"),
    )
    params_oms.setValue("superimposer:num_used_points", params.get("num_used_points"))
    params_oms.setValue("pairfinder:distance_MZ:exponent", 3.0)
    params_oms.setValue("pairfinder:distance_RT:exponent", 2.0)

    aligner = oms.MapAlignmentAlgorithmPoseClustering()
    study_obj.logger.info(
        f"Align RTs with Pose clustering: rt_tol={params.get('rt_tol')}",
    )

    # Set ref_index to feature map index with largest number of features, excluding QC and blank samples
    # Build list of (index, size, sample_type) tuples
    candidates = []
    for i, fm in enumerate(fmaps):
        sample_id = sample_index_to_uid.get(i)
        sample_type = None
        if sample_id is not None:
            # Find sample_type from samples_df
            sample_row = study_obj.samples_df.filter(pl.col("sample_id") == sample_id)
            if not sample_row.is_empty() and "sample_type" in sample_row.columns:
                sample_type = sample_row.row(0, named=True).get("sample_type")

        # Exclude QC and blank samples from being reference
        if sample_type not in ["qc", "blank"]:
            candidates.append((i, fm.size()))

    # Select reference from valid candidates, or fallback to any sample if none available
    if candidates:
        ref_index = max(candidates, key=lambda x: x[1])[0]
        study_obj.logger.debug(
            f"Selected reference from {len(candidates)} non-QC/blank samples",
        )
    else:
        ref_index = max(enumerate([fm.size() for fm in fmaps]), key=lambda x: x[1])[0]
        study_obj.logger.warning(
            "No non-QC/blank samples available, using sample with most features as reference",
        )

    aligner.setParameters(params_oms)
    aligner.setReference(fmaps[ref_index])
    study_obj.logger.debug(f"Parameters for alignment: {params}")

    # Perform alignment and transformation of feature maps to the reference map (exclude reference map)
    for index, fm in tqdm(
        list(enumerate(fmaps)),
        total=len(fmaps),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {study_obj.log_label}Align feature maps",
        disable=tdqm_disable,
    ):
        if index == ref_index:
            continue
        if (
            params.get("skip_blanks")
            and study_obj.samples_df.row(index, named=True)["sample_type"] == "blank"
        ):
            continue

        # Skip feature maps with insufficient data points for alignment
        if fm.size() < 2:
            sample_name = study_obj.samples_df.row(index, named=True)["sample_name"]
            study_obj.logger.warning(
                f"Skipping alignment for sample '{sample_name}' - insufficient features ({fm.size()} features)",
            )
            continue

        try:
            trafo = oms.TransformationDescription()
            aligner.align(fm, trafo)
            transformer = oms.MapAlignmentTransformer()
            transformer.transformRetentionTimes(fm, trafo, True)
        except RuntimeError as e:
            sample_name = study_obj.samples_df.row(index, named=True)["sample_name"]
            study_obj.logger.warning(f"Failed to align sample '{sample_name}': {e}")
            continue

    study_obj.alignment_ref_index = ref_index

    # Process feature maps and update features_df with transformed retention times
    # Build a fast lookup for (sample_id, featureUid) to index in features_df
    feats = study_obj.features_df

    # Pre-build sample_id lookup for faster access
    study_obj.logger.debug("Build sample_id lookup for fast access...")
    sample_id_lookup = {
        idx: row_dict["sample_id"]
        for idx, row_dict in enumerate(study_obj.samples_df.iter_rows(named=True))
    }

    # Build the main lookup using feature_id (not feature_id)
    if "feature_id" in feats.columns:
        # Create lookup mapping (sample_id, feature_id) to DataFrame index using Polars
        # Since we need a pandas-style index lookup, we'll create a simple dict
        sample_ids = feats.get_column("sample_id").to_list()

        # Handle feature_id column - it might be Object type due to conversion
        feature_id_col = feats.get_column("feature_id")
        if feature_id_col.dtype == pl.Object:
            # If it's Object type, convert to list and let Python handle the conversion
            feature_ids = feature_id_col.to_list()
            # Convert to strings if they're not already
            feature_ids = [str(fid) if fid is not None else None for fid in feature_ids]
        else:
            # Safe to cast normally
            feature_ids = feature_id_col.cast(pl.Utf8).to_list()

        lookup = {
            (sample_id, feature_id): idx
            for idx, (sample_id, feature_id) in enumerate(
                zip(sample_ids, feature_ids, strict=True),
            )
        }
    else:
        # fallback: skip if feature_id column missing
        lookup = {}
        study_obj.logger.warning("feature_id column not found in features_df")

    # Pre-allocate update lists for better performance
    all_update_idx = []
    all_update_rt = []
    all_update_rt_original: list[float] = []

    for index, fm in tqdm(
        list(enumerate(fmaps)),
        total=len(fmaps),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {study_obj.log_label}Extract RTs",
        disable=tdqm_disable,
    ):
        sample_id = sample_id_lookup.get(index)
        if sample_id is None:
            continue

        # Collect all updates for this feature map
        for f in fm:
            feature_id = str(f.getUniqueId())
            idx = lookup.get((sample_id, feature_id))
            if idx is not None:
                rt = round(f.getRT(), 3)
                # rt_or = round(f.getMetaValue("original_RT"), 3) if f.metaValueExists("original_RT") else rt
                all_update_idx.append(idx)
                all_update_rt.append(rt)
                # all_update_rt_original.append(rt_or)

    # Single batch update for all features at once
    if all_update_idx:
        # Build a full-length Python list of rt values, update specified indices,
        # then replace the DataFrame column with a Series that has the same length
        try:
            current_rt = study_obj.features_df["rt"].to_list()
        except Exception:
            current_rt = [None] * study_obj.features_df.height

        # Defensive: ensure list length equals dataframe height
        if len(current_rt) != study_obj.features_df.height:
            current_rt = [None] * study_obj.features_df.height

        for idx, new_rt in zip(all_update_idx, all_update_rt, strict=False):
            current_rt[idx] = new_rt

        new_cols = [pl.Series("rt", current_rt)]

        # Update rt_original if corresponding updates were collected
        if "all_update_rt_original" in locals() and all_update_rt_original:
            try:
                current_rt_orig = (
                    study_obj.features_df["rt_original"].to_list()
                    if "rt_original" in study_obj.features_df.columns
                    else [None] * study_obj.features_df.height
                )
            except Exception:
                current_rt_orig = [None] * study_obj.features_df.height

            if len(current_rt_orig) != study_obj.features_df.height:
                current_rt_orig = [None] * study_obj.features_df.height

            for idx, new_orig in zip(
                all_update_idx,
                all_update_rt_original,
                strict=False,
            ):
                current_rt_orig[idx] = new_orig

            new_cols.append(pl.Series("rt_original", current_rt_orig))

        # Replace columns in one call
        study_obj.features_df = study_obj.features_df.with_columns(*new_cols)

    # Clean up temporary feature maps to release memory
    del fmaps
    study_obj.logger.debug("Temporary feature maps deleted to release memory")

    # Resolve reference sample UID from the reference index
    ref_sample_id = sample_id_lookup.get(ref_index)
    study_obj.logger.success(
        f"Alignment completed. Reference sample UID {ref_sample_id}.",
    )


def _align_kd_algorithm(study_obj, params):
    """
    Custom KD-tree / reference-based alignment working directly with features_df.
    """
    import bisect
    import statistics

    import polars as pl
    import pyopenms as oms

    # Pull parameter values - map standard align params to our algorithm
    # Use rt_tol (standard align param) instead of warp_rt_tol for RT tolerance
    rt_pair_tol = (
        float(params.get("rt_tol")) if params.get("rt_tol") is not None else 2.0
    )
    # Use mz_max_diff (standard align param) converted to ppm
    mz_max_diff_da = (
        float(params.get("mz_max_diff"))
        if params.get("mz_max_diff") is not None
        else 0.02
    )
    # Convert Da to ppm (assuming ~400 m/z average for metabolomics): 0.01 Da / 400 * 1e6 = 25 ppm
    ppm_tol = mz_max_diff_da / 400.0 * 1e6
    # Allow override with warp_mz_tol if specifically set (but not from defaults)
    try:
        warp_mz_from_params = params.get("warp_mz_tol")
        if (
            warp_mz_from_params is not None
            and warp_mz_from_params != params.__class__().warp_mz_tol
        ):
            ppm_tol = float(warp_mz_from_params)
    except (KeyError, AttributeError):
        pass

    # Safely retrieve optional parameter max_anchor_points (not yet part of defaults)
    try:
        _raw_mp = params.get("max_anchor_points")
    except KeyError:
        _raw_mp = None
    max_points = int(_raw_mp) if _raw_mp is not None else 1000
    study_obj.logger.info(
        f"Align RTs with KD-Tree: rt_tol={params.get('rt_tol')}, max_points={max_points}",
    )

    # Work directly with features_df instead of feature maps
    if study_obj.features_df is None or study_obj.features_df.is_empty():
        study_obj.logger.error(
            "No features_df available for alignment. Cannot proceed with KD alignment.",
        )
        raise AlignmentError(
            "No features detected for alignment\n"
            "This usually indicates that feature detection failed or samples were not loaded properly.\n"
            "Try:\n"
            "  1. Check that samples were loaded with detected features\n"
            "  2. Verify feature detection parameters\n"
            "  3. Inspect sample quality with study.get_samples_stats()",
        )

    # OPTIMIZATION 1: Group all features by sample_id in ONE operation instead of filtering repeatedly
    study_obj.logger.debug("Grouping features efficiently (major speedup)...")

    # rt_original should already exist (created in main align() function)
    if "rt_original" not in study_obj.features_df.columns:
        raise DataValidationError(
            "Missing 'rt_original' column in features_df\n"
            "This should have been created by the align() function.\n"
            "This is likely a bug - please report it.",
        )

    sample_groups = study_obj.features_df.group_by("sample_id", maintain_order=True)
    sample_feature_data = sample_groups.agg(
        [
            pl.len().alias("feature_count"),
            pl.col("mz").alias("mzs"),
            pl.col("rt_original").alias(
                "rt_originals",
            ),  # Use original RT values for alignment
        ],
    ).sort("feature_count", descending=True)

    if sample_feature_data.is_empty():
        study_obj.logger.error("No features found in any sample for alignment.")
        raise AlignmentError(
            "No features found in any sample for alignment\n"
            "Ensure samples have been loaded and feature detection has been performed.\n"
            "Check: study.get_samples_stats() to see feature counts per sample",
        )

    # Choose reference sample (sample with most features, excluding QC and blank samples)
    # Filter out QC and blank samples from candidates
    ref_candidates = sample_feature_data
    if "sample_type" in study_obj.samples_df.columns:
        # Join with samples_df to get sample_type
        ref_candidates = ref_candidates.join(
            study_obj.samples_df.select(["sample_id", "sample_type"]),
            on="sample_id",
            how="left",
        )
        # Filter out QC and blank samples
        non_qc_blank = ref_candidates.filter(
            (~pl.col("sample_type").is_in(["qc", "blank"]))
            | pl.col("sample_type").is_null(),
        )

        if not non_qc_blank.is_empty():
            ref_sample_id = non_qc_blank.row(0, named=True)["sample_id"]
            study_obj.logger.debug(
                f"Selected reference from {len(non_qc_blank)} non-QC/blank samples (excluded {len(ref_candidates) - len(non_qc_blank)} QC/blank samples)",
            )
        else:
            ref_sample_id = sample_feature_data.row(0, named=True)["sample_id"]
            study_obj.logger.warning(
                "No non-QC/blank samples available, using sample with most features as reference",
            )
    else:
        ref_sample_id = sample_feature_data.row(0, named=True)["sample_id"]
        study_obj.logger.debug(
            "sample_type column not found, selecting reference by feature count only",
        )

    # Find the index of this sample in samples_df
    ref_index = None
    sample_id_to_index = {}
    for idx, row_dict in enumerate(study_obj.samples_df.iter_rows(named=True)):
        sample_id = row_dict["sample_id"]
        sample_id_to_index[sample_id] = idx
        if sample_id == ref_sample_id:
            ref_index = idx

    if ref_index is None:
        study_obj.logger.error(
            f"Could not find reference sample {ref_sample_id} in samples_df",
        )
        available_ids = [
            row["sample_id"] for row in sample_feature_data.iter_rows(named=True)
        ]
        raise SampleNotFoundError(
            f"Reference sample '{ref_sample_id}' not found in study.\n"
            f"Available sample IDs: {', '.join(map(str, available_ids))}\n\n"
            "Check the sample_id and ensure the sample is loaded in the study.",
        )

    study_obj.alignment_ref_index = ref_index

    # OPTIMIZATION 2: Get reference features efficiently from pre-grouped data
    # Always use rt_original for alignment input to ensure consistent results
    ref_row = sample_feature_data.filter(pl.col("sample_id") == ref_sample_id).row(
        0,
        named=True,
    )
    ref_mzs_list = ref_row["mzs"]
    ref_rts_list = ref_row["rt_originals"]  # Use original RT values

    # Create sorted reference features for binary search
    ref_features = list(zip(ref_mzs_list, ref_rts_list, strict=False))
    ref_features.sort(key=lambda x: x[0])
    ref_mzs = [mz for mz, _ in ref_features]

    study_obj.logger.debug(
        f"Reference sample UID {ref_sample_id} (index {ref_index}, sample: {study_obj.samples_df.row(ref_index, named=True)['sample_name']}) has {len(ref_features)} features",
    )

    def find_best_match(mz: float, rt: float):
        mz_tol_abs = mz * ppm_tol * 1e-6
        left = bisect.bisect_left(ref_mzs, mz - mz_tol_abs)
        right = bisect.bisect_right(ref_mzs, mz + mz_tol_abs)
        best = None
        best_drt = None
        for idx in range(left, right):
            ref_mz, ref_rt = ref_features[idx]
            drt = abs(ref_rt - rt)
            ppm_err = abs(ref_mz - mz) / ref_mz * 1e6 if ref_mz else 1e9
            if ppm_err <= ppm_tol:
                if best_drt is None or drt < best_drt:
                    best = (rt, ref_rt)
                    best_drt = drt
        return best

    def _set_pairs(
        td_obj: oms.TransformationDescription,
        pairs,
    ):  # Helper for pyopenms API variability
        # Always provide list of lists to satisfy strict type expectations
        conv = [[float(a), float(b)] for a, b in pairs]
        try:
            td_obj.setDataPoints(conv)
        except Exception:
            # Fallback: attempt tuple form (older bindings) if list of lists fails
            try:
                td_obj.setDataPoints([tuple(p) for p in conv])
            except Exception:
                pass

    # OPTIMIZATION 3: Process samples using pre-grouped data (eliminates expensive filtering)
    transformations = {}

    for row in sample_feature_data.iter_rows(named=True):
        sample_id = row["sample_id"]
        sample_mzs = row["mzs"]
        sample_rts = row["rt_originals"]  # Use original RT values for alignment input

        td = oms.TransformationDescription()
        sample_index = sample_id_to_index.get(sample_id)

        if sample_index is None:
            study_obj.logger.warning(
                f"Sample UID {sample_id} not found in samples_df, skipping",
            )
            continue

        # Skip empty samples
        if not sample_mzs or not sample_rts:
            transformations[sample_id] = td
            continue

        # Identity for reference sample
        if sample_id == ref_sample_id:
            rts = [rt for rt in sample_rts if rt is not None]
            lo, hi = (min(rts), max(rts)) if rts else (0.0, 0.0)
            try:
                _set_pairs(td, [(lo, lo), (hi, hi)])
                td.fitModel("linear", oms.Param())
            except Exception:
                pass
            transformations[sample_id] = td
            continue

        # OPTIMIZATION 4: Process pairs using pre-loaded data arrays (no DataFrame operations)
        pairs_raw = []
        for mz, rt in zip(sample_mzs, sample_rts, strict=False):
            if mz is not None and rt is not None:
                match = find_best_match(mz, rt)
                if match:
                    obs_rt, ref_rt = match
                    if abs(obs_rt - ref_rt) <= rt_pair_tol:
                        pairs_raw.append((obs_rt, ref_rt))

        if not pairs_raw:
            # Fallback identity
            rts = [rt for rt in sample_rts if rt is not None]
            lo, hi = (min(rts), max(rts)) if rts else (0.0, 0.0)
            try:
                _set_pairs(td, [(lo, lo), (hi, hi)])
                td.fitModel("linear", oms.Param())
            except Exception:
                pass
            transformations[sample_id] = td
            study_obj.logger.debug(
                f"Sample {sample_id}: no anchors -> identity transform",
            )
            continue

        # Deduplicate and downsample
        seen_obs = set()
        pairs_unique = []
        for obs_rt, ref_rt in sorted(pairs_raw):
            key = round(obs_rt, 6)
            if key in seen_obs:
                continue
            seen_obs.add(key)
            pairs_unique.append((obs_rt, ref_rt))

        if len(pairs_unique) > max_points:
            stride = len(pairs_unique) / max_points
            sampled: list[tuple] = []
            idx = 0.0
            while int(idx) < len(pairs_unique) and len(sampled) < max_points:
                sampled.append(pairs_unique[int(idx)])
                idx += stride
            pairs_use = sampled
        else:
            pairs_use = pairs_unique

        shifts = [ref - obs for (obs, ref) in pairs_use]
        med_shift = statistics.median(shifts) if shifts else 0.0
        model = "lowess" if len(pairs_use) >= 20 else "linear"
        try:
            _set_pairs(td, pairs_use)
            td.fitModel(model, oms.Param())
        except Exception as e:
            study_obj.logger.debug(
                f"Sample {sample_id}: {model} fitting failed ({e}); fallback to linear two-point shift",
            )
            rts = [rt for rt in sample_rts if rt is not None]
            lo, hi = (min(rts), max(rts)) if rts else (0.0, 1.0)
            td = oms.TransformationDescription()
            try:
                _set_pairs(td, [(lo, lo + med_shift), (hi, hi + med_shift)])
                td.fitModel("linear", oms.Param())
            except Exception:
                pass

        study_obj.logger.debug(
            f"Sample {sample_id}: anchors raw={len(pairs_raw)} used={len(pairs_use)} model={model} median_shift={med_shift:.4f}s",
        )
        transformations[sample_id] = td

    # OPTIMIZATION 5: Apply transformations efficiently using vectorized operations
    study_obj.logger.debug("Applying RT transformations efficiently...")

    # Apply transformations to RT values starting from rt_original
    def transform_rt_vectorized(sample_id: int, rt_original: float) -> float:
        if sample_id in transformations and rt_original is not None:
            try:
                trafo = transformations[sample_id]
                return trafo.apply(float(rt_original))
            except Exception:
                return rt_original
        return rt_original

    # Use Polars' efficient struct operations for vectorized transformation
    # Apply transformation to rt_original and store result in rt column
    study_obj.features_df = study_obj.features_df.with_columns(
        pl.struct(["sample_id", "rt_original"])
        .map_elements(
            lambda x: transform_rt_vectorized(x["sample_id"], x["rt_original"]),
            return_dtype=pl.Float64,
        )
        .alias("rt"),
    )

    study_obj.logger.success(
        f"Alignment completed. Reference sample UID {ref_sample_id}.",
    )


def _align_pose_clustering_fallback(study_obj, fmaps, params):
    """Fallback PoseClustering alignment with minimal parameters."""
    import pyopenms as oms

    aligner = oms.MapAlignmentAlgorithmPoseClustering()
    ref_index = [
        i[0] for i in sorted(enumerate([fm.size() for fm in fmaps]), key=lambda x: x[1])
    ][-1]

    # Set up basic parameters for pose clustering
    pc_params = oms.Param()
    pc_params.setValue("max_num_peaks_considered", 1000)
    pc_params.setValue("pairfinder:distance_RT:max_difference", params.get("rt_tol"))
    pc_params.setValue(
        "pairfinder:distance_MZ:max_difference",
        params.get("mz_max_diff"),
    )

    aligner.setParameters(pc_params)
    aligner.setReference(fmaps[ref_index])

    for index, fm in enumerate(fmaps):
        if index == ref_index:
            continue
        trafo = oms.TransformationDescription()
        aligner.align(fm, trafo)
        transformer = oms.MapAlignmentTransformer()
        transformer.transformRetentionTimes(fm, trafo, True)

    study_obj.alignment_ref_index = ref_index


def find_iso(self, rt_tol=0.1, mz_tol=0.01, uids=None):
    """
    Find isotope patterns for consensus features by searching raw MS1 data.
    OPTIMIZED VERSION: Each sample file is loaded only once for maximum efficiency.

    For each consensus feature:
    1. Find the associated feature with highest intensity
    2. Load the corresponding sample5 file to access raw MS1 data
    3. Use original_rt (before alignment) to find the correct scan
    4. Search for isotope patterns in raw MS1 spectra
    5. Look for isotope patterns: 0.33, 0.50, 0.66, 1.00, 1.50, 2.00, 3.00, 4.00, 5.00 Da
    6. Store results as numpy arrays with [mz, inty] in the iso column

    Parameters:
        rt_tol (float): RT tolerance for scan matching in seconds
        mz_tol (float): Additional m/z tolerance for isotope matching in Da
        uids (list, optional): List of consensus_id values to process. If None, process all consensus features.
    """
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.error("No consensus features found. Please run merge() first.")
        return

    if self.consensus_mapping_df is None or self.consensus_mapping_df.is_empty():
        self.logger.error("No consensus mapping found. Please run merge() first.")
        return

    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features found.")
        return

    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.error("No samples found.")
        return

    # Add iso column if it doesn't exist
    if "iso" not in self.consensus_df.columns:
        self.consensus_df = self.consensus_df.with_columns(
            pl.lit(None, dtype=pl.Object).alias("iso"),
        )

    self.logger.info("Extracting isotopomers from raw MS1 data...")

    # Filter consensus features if uids is specified
    if uids is not None:
        if not isinstance(uids, (list, tuple)):
            uids = [uids]
        # Filter consensus_df to only process specified UIDs
        consensus_df_filtered = self.consensus_df.filter(
            pl.col("consensus_id").is_in(uids),
        )
        if consensus_df_filtered.is_empty():
            self.logger.warning(
                f"No consensus features found with specified UIDs: {uids}",
            )
            return
        self.logger.debug(
            f"Processing {len(consensus_df_filtered)} consensus features (UIDs: {uids})",
        )
    else:
        consensus_df_filtered = self.consensus_df
        self.logger.debug(
            f"Processing all {len(consensus_df_filtered)} consensus features",
        )

    # Isotope mass shifts to search for (up to 7x 13C isotopes)
    isotope_shifts = [
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
    ]

    consensus_iso_data: dict[int, np.ndarray | None] = {}

    # SUPER OPTIMIZATION: Vectorized pre-calculation using joins (10-100x faster)
    self.logger.debug(
        "Building sample-to-consensus mapping using vectorized operations...",
    )

    # Step 1: Join consensus_mapping with features to get intensities in one operation
    # Apply UID filtering if specified
    if uids is not None:
        consensus_mapping_filtered = self.consensus_mapping_df.filter(
            pl.col("consensus_id").is_in(uids),
        )
    else:
        consensus_mapping_filtered = self.consensus_mapping_df

    consensus_with_features = consensus_mapping_filtered.join(
        self.features_df.select(
            ["feature_id", "sample_id", "inty", "mz", "rt", "rt_original"],
        ),
        on=["feature_id", "sample_id"],
        how="left",
    )

    # Step 2: Find the best feature (highest intensity) for each consensus using window functions
    best_features = (
        consensus_with_features.with_columns(
            pl.col("inty").fill_null(0),  # Handle null intensities
        )
        .with_columns(pl.col("inty").max().over("consensus_id").alias("max_inty"))
        .filter(pl.col("inty") == pl.col("max_inty"))
        .group_by("consensus_id")
        .first()
    )  # Take first if there are ties

    # Step 3: Join with samples to get sample paths in one operation
    best_features_with_paths = best_features.join(
        self.samples_df.select(["sample_id", "sample_path"]),
        on="sample_id",
        how="left",
    ).filter(pl.col("sample_path").is_not_null())

    # Step 4: Group by sample path for batch processing (much faster than nested loops)
    sample_to_consensus: dict[str, dict] = {}
    for row in best_features_with_paths.iter_rows(named=True):
        sample_path = row["sample_path"]
        consensus_id = row["consensus_id"]

        # Create feature data dictionary for compatibility
        feature_data = {
            "mz": row["mz"],
            "rt": row["rt"],
            "rt_original": row.get("rt_original", row["rt"]),
            "inty": row["inty"],
        }

        if sample_path not in sample_to_consensus:
            sample_to_consensus[sample_path] = []

        sample_to_consensus[sample_path].append((consensus_id, feature_data))

    # Initialize failed consensus features (those not in the mapping)
    processed_consensus_ids = set(best_features_with_paths["consensus_id"].to_list())
    for consensus_row in consensus_df_filtered.iter_rows(named=True):
        consensus_id = consensus_row["consensus_id"]
        if consensus_id not in processed_consensus_ids:
            consensus_iso_data[consensus_id] = None

    self.logger.debug(
        f"Will read {len(sample_to_consensus)} unique sample files for {len(consensus_df_filtered)} consensus features",
    )

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    # OPTIMIZATION 2: Process by sample file (load each file only once)
    for sample_path, consensus_list in tqdm(
        sample_to_consensus.items(),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Extract iso data",
        disable=tdqm_disable,
    ):
        try:
            # Load MS1 data once per sample
            ms1_df = self._load_ms1(sample_path)

            if ms1_df is None or ms1_df.is_empty():
                # Mark all consensus features from this sample as failed
                for consensus_id, _ in consensus_list:
                    consensus_iso_data[consensus_id] = None
                continue

            # Process all consensus features for this sample
            for consensus_id, best_feature in consensus_list:
                # Get the original RT (before alignment correction)
                base_mz = best_feature["mz"]
                original_rt = best_feature.get("rt_original", best_feature["rt"])

                # Skip if RT or mz is None or invalid
                if original_rt is None:
                    original_rt = best_feature["rt"]
                    self.logger.debug("original_rt is None. Using aligned rt instead")

                if base_mz is None:
                    self.logger.warning(
                        f"Skipping consensus_id {consensus_id}: base_mz is None",
                    )
                    consensus_iso_data[consensus_id] = None
                    continue

                # Find MS1 scans near the original RT
                rt_min = original_rt - rt_tol
                rt_max = original_rt + rt_tol

                # Filter MS1 data for scans within RT window
                ms1_window = ms1_df.filter(
                    (pl.col("rt") >= rt_min) & (pl.col("rt") <= rt_max),
                )

                if ms1_window.is_empty():
                    consensus_iso_data[consensus_id] = None
                    continue

                isotope_matches = []

                # Search for each isotope shift
                for shift in isotope_shifts:
                    target_mz = base_mz + shift
                    mz_min_iso = target_mz - mz_tol
                    mz_max_iso = target_mz + mz_tol

                    # Find peaks in MS1 data within m/z tolerance
                    isotope_peaks = ms1_window.filter(
                        (pl.col("mz") >= mz_min_iso) & (pl.col("mz") <= mz_max_iso),
                    )

                    if not isotope_peaks.is_empty():
                        # Get the peak with maximum intensity for this isotope
                        max_peak = isotope_peaks.filter(
                            pl.col("inty") == pl.col("inty").max(),
                        ).row(0, named=True)

                        # Store as float with specific precision: m/z to 4 decimals, intensity rounded to integer
                        mz_formatted = round(float(max_peak["mz"]), 4)
                        inty_formatted = float(
                            round(max_peak["inty"]),
                        )  # Round to integer, but keep as float
                        isotope_matches.append([mz_formatted, inty_formatted])

                # Store results as numpy array
                if isotope_matches:
                    consensus_iso_data[consensus_id] = np.array(isotope_matches)
                else:
                    consensus_iso_data[consensus_id] = None

        except Exception as e:
            self.logger.warning(f"Failed to load MS1 data from {sample_path}: {e}")
            # Mark all consensus features from this sample as failed
            for consensus_id, _ in consensus_list:
                consensus_iso_data[consensus_id] = None
            continue

    # Update consensus_df with isotope data
    # Create mapping function for update
    def get_iso_data(uid):
        return consensus_iso_data.get(uid)

    # Update the iso column
    self.consensus_df = self.consensus_df.with_columns(
        pl.col("consensus_id")
        .map_elements(lambda uid: get_iso_data(uid), return_dtype=pl.Object)
        .alias("iso"),
    )

    # Count how many consensus features have isotope data
    iso_count = sum(
        1 for data in consensus_iso_data.values() if data is not None and len(data) > 0
    )

    self.logger.success(
        f"Isotope detection completed. Found isotope patterns for {iso_count}/{len(self.consensus_df)} consensus features.",
    )


def iso_reset(self):
    """
    Reset the iso column in consensus_df to None, clearing all isotope data.

    This function clears any previously computed isotope patterns from the
    consensus_df, setting the 'iso' column to None for all features. This
    is useful before re-running isotope detection with different parameters
    or to clear isotope data entirely.

    Returns:
        None
    """
    if self.consensus_df is None:
        self.logger.warning("No consensus_df found. Nothing to reset.")
        return

    if "iso" not in self.consensus_df.columns:
        self.logger.warning("No 'iso' column found in consensus_df. Nothing to reset.")
        return

    # Count how many features currently have isotope data
    iso_count = self.consensus_df.select(
        pl.col("iso").is_not_null().sum().alias("count"),
    ).item(0, "count")

    # Reset the iso column to None
    self.consensus_df = self.consensus_df.with_columns(
        pl.lit(None, dtype=pl.Object).alias("iso"),
    )

    self.logger.info(
        f"Reset isotope data for {iso_count} features. All 'iso' values set to None.",
    )
