# mypy: disable-error-code="no-any-return"
from __future__ import annotations

import polars as pl

# Parameters removed - using hardcoded defaults


def _estimate_memory_usage(self):
    """
    Estimate the memory usage of all dataframes in the Sample object.

    Returns:
        dict: A dictionary containing memory usage estimates for each dataframe
              and the total memory usage in bytes and MB.
    """
    memory_usage = {}
    total_bytes = 0

    # Check features_df
    if self.features_df is not None and len(self.features_df) > 0:
        features_bytes = self.features_df.estimated_size()
        memory_usage["features_df"] = {
            "rows": len(self.features_df),
            "columns": len(self.features_df.columns),
            "bytes": features_bytes,
            "mb": features_bytes / (1024 * 1024),
        }
        total_bytes += features_bytes
    else:
        memory_usage["features_df"] = {"rows": 0, "columns": 0, "bytes": 0, "mb": 0}

    # Check scans_df
    if self.scans_df is not None and len(self.scans_df) > 0:
        scans_bytes = self.scans_df.estimated_size()
        memory_usage["scans_df"] = {
            "rows": len(self.scans_df),
            "columns": len(self.scans_df.columns),
            "bytes": scans_bytes,
            "mb": scans_bytes / (1024 * 1024),
        }
        total_bytes += scans_bytes
    else:
        memory_usage["scans_df"] = {"rows": 0, "columns": 0, "bytes": 0, "mb": 0}

    # Check ms1_df
    if self.ms1_df is not None and len(self.ms1_df) > 0:
        ms1_bytes = self.ms1_df.estimated_size()
        memory_usage["ms1_df"] = {
            "rows": len(self.ms1_df),
            "columns": len(self.ms1_df.columns),
            "bytes": ms1_bytes,
            "mb": ms1_bytes / (1024 * 1024),
        }
        total_bytes += ms1_bytes
    else:
        memory_usage["ms1_df"] = {"rows": 0, "columns": 0, "bytes": 0, "mb": 0}

    # Check chrom_df
    if self.chrom_df is not None and len(self.chrom_df) > 0:
        chrom_bytes = self.chrom_df.estimated_size()
        memory_usage["chrom_df"] = {
            "rows": len(self.chrom_df),
            "columns": len(self.chrom_df.columns),
            "bytes": chrom_bytes,
            "mb": chrom_bytes / (1024 * 1024),
        }
        total_bytes += chrom_bytes
    else:
        memory_usage["chrom_df"] = {"rows": 0, "columns": 0, "bytes": 0, "mb": 0}

    # Add total memory usage
    memory_usage["total"] = {
        "bytes": total_bytes,
        "mb": total_bytes / (1024 * 1024),
        "gb": total_bytes / (1024 * 1024 * 1024),
    }

    # Log the memory usage summary
    if hasattr(self, "logger"):
        self.logger.debug(
            f"Total DataFrame memory usage: {memory_usage['total']['mb']:.2f} MB",
        )
        for df_name, stats in memory_usage.items():
            if df_name != "total" and stats["bytes"] > 0:
                self.logger.debug(
                    f"{df_name}: {stats['rows']} rows, {stats['mb']:.2f} MB",
                )

    return memory_usage["total"]["mb"]


def get_dda_stats(self) -> pl.DataFrame:
    # filter self.scans_df with mslevel 1
    ms1 = self.scans_df.filter(pl.col("ms_level") == 1)
    return ms1


def get_feature(self, feature_id: int) -> dict | None:
    """Retrieve single feature data as dictionary.

    Returns all column values for a specified feature using its unique identifier.

    Args:
        feature_id (int): Unique feature identifier to retrieve.

    Returns:
        dict | None: Dictionary with column names as keys and feature values,
            or None if feature not found.

    Example:
        Retrieve feature data::

            >>> sample = masster.Sample("data.mzML")
            >>> sample.find_features()
            >>> feature = sample.get_feature(42)
            >>> if feature:
            ...     print(f"m/z: {feature['mz']:.4f}")
            ...     print(f"RT: {feature['rt']:.2f} min")
            ...     print(f"Intensity: {feature['intensity']:.0f}")

        Access specific attributes::

            >>> feature = sample.get_feature(100)
            >>> if feature:
            ...     mz = feature['mz']
            ...     rt = feature['rt']
            ...     adduct = feature.get('adduct', 'Unknown')
            ...     has_ms2 = feature.get('ms2_scans') is not None

        Check identification::

            >>> feature = sample.get_feature(42)
            >>> if feature and 'id_top_name' in feature:
            ...     print(f"Identified as: {feature['id_top_name']}")
            ...     print(f"Score: {feature['id_top_score']:.2f}")

    Note:
        - Returns None and logs warning if feature_id not found
        - Dictionary includes all columns from features_df row
        - Common columns: mz, rt, intensity, area, fwhm, quality, charge
        - Optional columns: adduct, adduct_group, id_top_name, ms2_scans
        - Use features_df.filter() for multi-feature queries

    See Also:
        features_select: Query multiple features with filters.
        features_filter: Filter features by multiple criteria.
        get_id: Retrieve identification results for features.
    """


def _get_scan_uids(self, scans=None, verbose=True):
    scans_uids = []
    if scans is None:
        # fromuids scan all get_dfans
        scans_uids = self.scans_df.get_column("scan_id").to_list()
    elif isinstance(scans, list):
        # if scans is a list, ensure all elements are valid scan_ids
        scans_uids = [
            s for s in scans if s in self.scans_df.get_column("scan_id").to_list()
        ]
        if verbose and not scans_uids:
            self.logger.error("No valid scan_ids provided.")

    return scans_uids


def _get_feature_ids(self, features=None, verbose=True):
    """
    Get feature IDs from various input types.

    Parameters:
        features: Can be one of the following:
            - None: Returns all feature IDs from self.features_df
            - list: Returns the list if all elements are valid feature IDs
            - polars.DataFrame: Extracts unique values from 'feature_id' or 'feature_id' column
            - pandas.DataFrame: Extracts unique values from 'feature_id' or 'feature_id' column
        verbose (bool): Whether to log errors for invalid inputs

    Returns:
        list: List of feature IDs
    """
    if features is None:
        # Get all feature IDs from self.features_df
        if self.features_df is None:
            if verbose:
                self.logger.warning("No features_df available.")
            return []
        feature_ids = self.features_df.get_column("feature_id").to_list()
    elif isinstance(features, list):
        # If features is a list, ensure all elements are valid feature_ids
        if self.features_df is None:
            if verbose:
                self.logger.warning(
                    "No features_df available to validate feature IDs.",
                )
            return []

        valid_feature_ids = self.features_df.get_column("feature_id").to_list()
        feature_ids = [f for f in features if f in valid_feature_ids]
        if verbose and not feature_ids:
            self.logger.error("No valid feature_ids provided.")
    else:
        # Handle polars and pandas DataFrames
        try:
            # Check if it's a polars DataFrame
            if hasattr(features, "columns") and hasattr(features, "get_column"):
                # Polars DataFrame
                feature_column = None
                if "feature_id" in features.columns or "feature_id" in features.columns:
                    feature_column = "feature_id"

                if feature_column is None:
                    if verbose:
                        self.logger.error(
                            "No 'feature_id' or 'feature_id' column found in polars DataFrame.",
                        )
                    return []

                # Get unique values from the column
                feature_ids = features.get_column(feature_column).unique().to_list()

            # Check if it's a pandas DataFrame
            elif hasattr(features, "columns") and hasattr(features, "iloc"):
                # Pandas DataFrame
                import pandas as pd

                if not isinstance(features, pd.DataFrame):
                    if verbose:
                        self.logger.error(
                            "Invalid input type. Expected None, list, polars DataFrame, or pandas DataFrame.",
                        )
                    return []

                feature_column = None
                if "feature_id" in features.columns or "feature_id" in features.columns:
                    feature_column = "feature_id"

                if feature_column is None:
                    if verbose:
                        self.logger.error(
                            "No 'feature_id' or 'feature_id' column found in pandas DataFrame.",
                        )
                    return []

                # Get unique values from the column
                feature_ids = features[feature_column].unique().tolist()

            else:
                if verbose:
                    self.logger.error(
                        "Invalid input type. Expected None, list, polars DataFrame, or pandas DataFrame.",
                    )
                return []

        except Exception as e:
            if verbose:
                self.logger.error(f"Error processing DataFrame input: {e}")
            return []

    return feature_ids


def _get_feature_uids(self, features=None, verbose=True):
    """
    Get feature UIDs from various input types.

    Parameters:
        features: Can be one of the following:
            - None: Returns all feature UIDs from self.features_df
            - list: Returns the list if all elements are valid feature UIDs
            - polars.DataFrame: Extracts unique values from 'feature_uid' or 'feature_id' column
            - pandas.DataFrame: Extracts unique values from 'feature_uid' or 'feature_id' column
        verbose (bool): Whether to log errors for invalid inputs

    Returns:
        list: List of feature UIDs
    """
    if features is None:
        # Get all feature UIDs from self.features_df
        if self.features_df is None:
            if verbose:
                self.logger.warning("No features_df available.")
            return []
        feature_uids = self.features_df.get_column("feature_uid").to_list()
    elif isinstance(features, list):
        # If features is a list, ensure all elements are valid feature_uids
        if self.features_df is None:
            if verbose:
                self.logger.warning(
                    "No features_df available to validate feature UIDs.",
                )
            return []

        valid_feature_uids = self.features_df.get_column("feature_uid").to_list()
        feature_uids = [f for f in features if f in valid_feature_uids]
        if verbose and not feature_uids:
            self.logger.error("No valid feature_uids provided.")
    else:
        # Handle polars and pandas DataFrames
        try:
            # Check if it's a polars DataFrame
            if hasattr(features, "columns") and hasattr(features, "get_column"):
                # Polars DataFrame
                feature_column = None
                if "feature_uid" in features.columns:
                    feature_column = "feature_uid"
                elif "feature_id" in features.columns:
                    feature_column = "feature_id"

                if feature_column is None:
                    if verbose:
                        self.logger.error(
                            "No 'feature_uid' or 'feature_id' column found in polars DataFrame.",
                        )
                    return []

                # Get unique values from the column
                feature_uids = features.get_column(feature_column).unique().to_list()

            # Check if it's a pandas DataFrame
            elif hasattr(features, "columns") and hasattr(features, "iloc"):
                # Pandas DataFrame
                import pandas as pd

                if not isinstance(features, pd.DataFrame):
                    if verbose:
                        self.logger.error(
                            "Invalid input type. Expected None, list, polars DataFrame, or pandas DataFrame.",
                        )
                    return []

                feature_column = None
                if "feature_uid" in features.columns:
                    feature_column = "feature_uid"
                elif "feature_id" in features.columns:
                    feature_column = "feature_id"

                if feature_column is None:
                    if verbose:
                        self.logger.error(
                            "No 'feature_uid' or 'feature_id' column found in pandas DataFrame.",
                        )
                    return []

                # Get unique values from the column
                feature_uids = features[feature_column].unique().tolist()

            else:
                if verbose:
                    self.logger.error(
                        "Invalid input type. Expected None, list, polars DataFrame, or pandas DataFrame.",
                    )
                return []

        except Exception as e:
            if verbose:
                self.logger.error(f"Error processing DataFrame input: {e}")
            return []

    return feature_uids


def get_scan(
    self,
    scans: list | None = None,
    verbose: bool = True,
) -> pl.DataFrame | None:
    scan_uids = self._get_scan_uids(scans, verbose=False)
    if not scan_uids:
        if verbose:
            self.logger.warning("No valid scan_uids provided.")
        return None

    scan = self.scans_df.filter(pl.col("scan_uid").is_in(scan_uids))
    return scan


def select_closest_scan(
    self,
    rt,
    prec_mz=None,
    mz_tol=0.01,
):
    """
    Select the closest scan based on retention time (rt), applying additional filtering on precursor m/z (prec_mz) if provided.
    Parameters:
        rt (float): The target retention time to find the closest scan.
        prec_mz (float, optional): The precursor m/z value used to filter scans. If given, only scans with ms_level 2 are considered
                                    and filtered to include only those within mz_tol of prec_mz.
        mz_tol (float, optional): The tolerance to apply when filtering scans by precursor m/z. Defaults to 0.01.
    Returns:
        polars.DataFrame or None: A DataFrame slice containing the closest scan if a matching scan is found;
                                  otherwise, returns None.
    Notes:
        - If the scans_df attribute is None, the function prints an error message and returns None.
        - When prec_mz is provided, it filters scans where ms_level equals 2 and the precursor m/z is within the given mz_tol range.
        - If prec_mz is not provided, scans with ms_level equal to 1 are considered.
        - The function calculates the absolute difference between each scan's rt and the given rt, sorting the scans by this difference.
        - If no scans match the criteria, an error message is printed before returning None.
    """
    # check if scans_df is None
    if self.scans_df is None:
        self.logger.warning("No scans found.")
        return None
    if prec_mz is not None:
        ms_level = 2
        scans = self.scans_df.filter(pl.col("ms_level") == ms_level)
        # find all scans with prec_mz within mz_tol of prec_mz
        scans = scans.filter(pl.col("prec_mz") > prec_mz - mz_tol)
        scans = scans.filter(pl.col("prec_mz") < prec_mz + mz_tol)
        # sort by distance to rt
        scans = scans.with_columns((pl.col("rt") - rt).abs().alias("rt_diff"))
        scans = scans.sort("rt_diff")
        # return the closest scan
        if len(scans) > 0:
            scan = scans.slice(0, 1)
        else:
            self.logger.warning(
                f"No scans found with prec_mz {prec_mz} within {mz_tol} of rt {rt}.",
            )
            return None
    else:
        mslevel = 1
        scans = self.scans_df.filter(pl.col("ms_level") == mslevel)
        # sort by distance to rt
        scans = scans.with_columns((pl.col("rt") - rt).abs().alias("rt_diff"))
        scans = scans.sort("rt_diff")
        # return the closest scan
        if len(scans) > 0:
            scan = scans.slice(0, 1)
        else:
            self.logger.warning(
                f"No scans found with ms_level {mslevel} within {mz_tol} of rt {rt}.",
            )
            return None
    # return scans_df slice

    return scan


def get_eic(self, mz, mz_tol=None):
    """Extract Extracted Ion Chromatogram (EIC) from MS1 data.

    Filters MS1 data for a target m/z window, aggregates intensities across
    retention time, and returns the chromatographic profile.

    Args:
        mz (float): Target m/z value for extraction.
        mz_tol (float | None): Mass tolerance around target m/z. If None, uses
            parameters.eic_mz_tol or defaults to 0.01. Defaults to None.

    Returns:
        pl.DataFrame | None: Chromatogram with columns ['rt', 'inty'], sorted by
            retention time. Returns None if no data points found or ms1_df missing.

    Example:
        Extract single EIC::

            >>> sample = masster.Sample("data.mzML")
            >>> eic = sample.get_eic(mz=195.0877, mz_tol=0.005)
            >>> if eic is not None:
            ...     print(f"Found {len(eic)} time points")
            ...     max_inty = eic["inty"].max()
            ...     rt_apex = eic.filter(
            ...         pl.col("inty") == max_inty
            ...     )["rt"][0]

        Plot chromatogram::

            >>> import matplotlib.pyplot as plt
            >>> eic = sample.get_eic(mz=195.0877)
            >>> if eic is not None:
            ...     plt.plot(eic["rt"], eic["inty"])
            ...     plt.xlabel("Retention Time (min)")
            ...     plt.ylabel("Intensity")

        Compare multiple compounds::

            >>> compounds = [
            ...     {"name": "Caffeine", "mz": 195.0877},
            ...     {"name": "Theophylline", "mz": 181.0720}
            ... ]
            >>> for cmpd in compounds:
            ...     eic = sample.get_eic(cmpd["mz"], mz_tol=0.01)
            ...     if eic:
            ...         print(f"{cmpd['name']}: {eic['inty'].max():.0f}")

    Note:
        - Result stored in sample.chrom_df (overwritten on each call)
        - If multiple m/z values exist at same RT (within tolerance), intensities
          are summed
        - Returns None and sets chrom_df=None if no points found
        - Tolerance recommendation: 0.005-0.01 Da for high-resolution MS
        - For visualization, consider using plot_eic() method instead

    See Also:
        plot_eic: Visualize extracted ion chromatogram.
        get_feature: Retrieve feature information including RT profile.
        chrom_extract: Extract chromatographic data for features.
    """
    # Use default mz_tol from sample parameters if not provided
    if mz_tol is None:
        if hasattr(self, "parameters") and hasattr(self.parameters, "eic_mz_tol"):
            mz_tol = self.parameters.eic_mz_tol
        else:
            mz_tol = 0.01  # fallback default

    # Validate ms1_df
    if not hasattr(self, "ms1_df") or self.ms1_df is None:
        if hasattr(self, "logger"):
            self.logger.warning("No ms1_df available to build EIC.")
        return None

    try:
        # Filter by mz window
        mz_min = mz - mz_tol
        mz_max = mz + mz_tol
        matches = self.ms1_df.filter(
            (pl.col("mz") >= mz_min) & (pl.col("mz") <= mz_max),
        )

        if len(matches) == 0:
            if hasattr(self, "logger"):
                self.logger.debug(f"No ms1 points found for mz={mz} ± {mz_tol}.")
            # ensure chrom_df is None when nothing found
            self.chrom_df = None
            return None

        # Aggregate intensities per retention time. Use sum in case multiple points per rt.
        chrom = (
            matches.group_by("rt").agg([pl.col("inty").sum().alias("inty")]).sort("rt")
        )

        # Attach to Sample
        self.chrom_df = chrom

        if hasattr(self, "logger"):
            self.logger.debug(f"Built EIC for mz={mz} ± {mz_tol}: {len(chrom)} points.")

        return chrom

    except Exception as e:
        if hasattr(self, "logger"):
            self.logger.error(f"Error building EIC for mz={mz}: {e}")
        return None


def features_select(
    self,
    ids=None,
    uids=None,
    mz=None,
    rt=None,
    rt_delta=None,
    inty=None,
    sanity=None,
    coherence=None,
    prominence_scaled=None,
    prominence=None,
    height_scaled=None,
    height=None,
    iso=None,
    iso_of=None,
    has_MS2=None,
    adduct_group=None,
    identified=None,
    id_top_name=None,
    id_top_class=None,
    id_top_adduct=None,
    id_top_score=None,
    # Short aliases
    score=None,
    name=None,
    # Backward compatibility
    uid=None,
):
    """Select features based on multi-criteria filtering and return filtered DataFrame.

    Flexible feature selection supporting numeric ranges, Boolean filters, regex patterns,
    and DataFrame-based selection. All filters are combined with AND logic.

    Args:
        ids (list[int] | tuple[int, int] | pl.DataFrame | pd.DataFrame | None): Feature
            ID filter. Can be list of IDs, tuple for range (min, max), or DataFrame
            with feature_id column.
        uids (list[str] | pl.DataFrame | pd.DataFrame | None): Feature UID filter. Can
            be list of UIDs or DataFrame with feature_uid column.
        mz (tuple[float, float] | float | None): m/z filter. Tuple for range (min, max)
            or single value for minimum.
        rt (tuple[float, float] | float | None): Retention time filter in seconds. Tuple
            for range (min, max) or single value for minimum.
        rt_delta (tuple[float, float] | float | None): RT delta filter. Tuple for range
            or single value for minimum.
        inty (tuple[float, float] | float | None): Intensity filter. Tuple for range or
            single value for minimum.
        sanity (tuple[float, float] | float | None): Chromatogram sanity score filter
            (0.0-1.0). Tuple for range or single value for minimum.
        coherence (tuple[float, float] | float | None): Chromatogram coherence filter
            (0.0-1.0). Tuple for range or single value for minimum.
        prominence_scaled (tuple[float, float] | float | None): Scaled prominence filter.
            Tuple for range or single value for minimum.
        prominence (tuple[float, float] | float | None): Prominence filter. Tuple for
            range or single value for minimum.
        height_scaled (tuple[float, float] | float | None): Scaled height filter. Tuple
            for range or single value for minimum.
        height (tuple[float, float] | float | None): Height filter. Tuple for range or
            single value for minimum.
        iso (tuple[int, int] | int | None): Isotope number filter. Tuple for range or
            single value for exact match. 0 = monoisotopic peak.
        iso_of (tuple[int, int] | int | None): Isotope parent filter. Tuple for range
            or single value for exact match. Filter for isotope peaks of specific parent.
        has_MS2 (bool | None): Filter for features with (True) or without (False) MS2
            spectra.
        adduct_group (int | list[int] | tuple[int, int] | None): Adduct group filter.
            Single value, list of values, or tuple for range.
        identified (bool | None): Filter for features with (True) or without (False)
            identification.
        id_top_name (str | list[str] | None): Top identification name filter using regex.
            Single pattern or list of patterns (combined with OR). Alias: name.
        id_top_class (str | list[str] | None): Top identification class filter using
            regex. Single pattern or list of patterns (combined with OR).
        id_top_adduct (str | list[str] | None): Top identification adduct filter. Single
            value for exact match or list for multiple adducts.
        id_top_score (tuple[float, float] | float | None): Top identification score
            filter. Tuple for range (min, max) or single value for minimum. Alias: score.
        score (tuple[float, float] | float | None): Short alias for id_top_score.
        name (str | list[str] | None): Short alias for id_top_name.
        uid (deprecated): Use ids parameter instead.

    Returns:
        pl.DataFrame: Filtered features DataFrame. Returns empty DataFrame if no
            features match criteria.

    Example:
        ::

            from masster import Sample

            s = Sample(file="data.mzML")
            s.find_features()
            s.find_ms2()
            s.identify(lib="mmc")

            # Select features with MS2 and high intensity
            selected = s.features_select(
                has_MS2=True,
                inty=1e6
            )

            # Select by m/z range and score
            selected = s.features_select(
                mz=(200, 400),
                score=0.8
            )

            # Select identified features by name pattern
            selected = s.features_select(
                name="Glucose|Fructose",
                identified=True
            )

            # Select features in specific RT window with quality filters
            selected = s.features_select(
                rt=(300, 600),
                sanity=0.7,
                coherence=0.8
            )

            # Select specific feature IDs
            selected = s.features_select(ids=[1, 5, 10, 15])

            # Select isotope peaks
            selected = s.features_select(iso=(1, 3))  # M+1 to M+3

    Note:
        **Filter Logic:**

        All non-None filters are combined with AND logic. Empty result if no features
        satisfy all criteria.

        **Range vs. Minimum:**

        Most numeric filters accept tuple (min, max) for range or single value for
        minimum threshold.

        **Regex Patterns:**

        id_top_name and id_top_class support regex patterns. Use | for OR logic:
        name="Glucose|Fructose" matches either compound.

        **Short Aliases:**

        - score -> id_top_score
        - name -> id_top_name

        These improve code readability for common filters.

        **DataFrame-Based Selection:**

        ids and uids parameters accept DataFrames for complex selections. Useful for
        filtering based on external data or previous selections.

        **Performance:**

        Efficient filtering using Polars expressions. For large feature sets (>100k),
        apply most restrictive filters first by ordering parameters.

    See Also:
        - :meth:`features_filter`: Delete features based on criteria
        - :meth:`features_delete`: Delete features by ID
        - :meth:`get_feature`: Retrieve single feature data
    """
    # Apply short aliases
    if score is not None:
        id_top_score = score
    if name is not None:
        id_top_name = name

    # Backward compatibility for uid
    if uid is not None and ids is None:
        ids = uid

    # remove all features with coherence < coherence
    if self.features_df is None:
        # self.logger.info("No features found. R")
        return None
    feats = self.features_df.clone()

    # Filter by feature IDs if provided
    if ids is not None:
        if isinstance(ids, tuple) and len(ids) == 2:
            # Handle tuple as range of feature IDs
            min_id, max_id = ids
            feats_len_before_filter = len(feats)
            feats = feats.filter(
                (pl.col("feature_id") >= min_id) & (pl.col("feature_id") <= max_id),
            )
            self.logger.debug(
                f"Selected features by ID range ({min_id}-{max_id}). Features removed: {feats_len_before_filter - len(feats)}",
            )
        else:
            # Handle list or DataFrame input
            feature_ids_to_keep = self._get_feature_ids(features=ids, verbose=True)
            if not feature_ids_to_keep:
                self.logger.warning("No valid feature IDs provided.")
                return feats.limit(0)  # Return empty DataFrame with same structure

            feats_len_before_filter = len(feats)
            feats = feats.filter(pl.col("feature_id").is_in(feature_ids_to_keep))
            self.logger.debug(
                f"Selected features by IDs. Features removed: {feats_len_before_filter - len(feats)}",
            )

    # Filter by feature UIDs if provided
    if uids is not None:
        feature_ids_to_keep = self._get_feature_ids(features=uids, verbose=True)
        if not feature_ids_to_keep:
            self.logger.warning("No valid feature UIDs provided.")
            return feats.limit(0)

        feats_len_before_filter = len(feats)
        feats = feats.filter(pl.col("feature_id").is_in(feature_ids_to_keep))
        self.logger.debug(
            f"Selected features by UIDs. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if sanity is not None:
        has_sanity = "chrom_sanity" in self.features_df.columns
        if not has_sanity:
            self.logger.warning("No sanity data found in features.")
        else:
            feats_len_before_filter = len(feats)
            if isinstance(sanity, tuple) and len(sanity) == 2:
                min_sanity, max_sanity = sanity
                feats = feats.filter(
                    (pl.col("chrom_sanity") >= min_sanity)
                    & (pl.col("chrom_sanity") <= max_sanity),
                )
            else:
                feats = feats.filter(pl.col("chrom_sanity") >= sanity)
            self.logger.debug(
                f"Selected features by sanity. Features removed: {feats_len_before_filter - len(feats)}",
            )

    if coherence is not None:
        has_coherence = "chrom_coherence" in self.features_df.columns
        if not has_coherence:
            self.logger.warning("No coherence data found in features.")
        else:
            # record len for logging
            feats_len_before_filter = len(feats)
            if isinstance(coherence, tuple) and len(coherence) == 2:
                min_coherence, max_coherence = coherence
                feats = feats.filter(
                    (pl.col("chrom_coherence") >= min_coherence)
                    & (pl.col("chrom_coherence") <= max_coherence),
                )
            else:
                feats = feats.filter(pl.col("chrom_coherence") >= coherence)
            self.logger.debug(
                f"Selected features by coherence. Features removed: {feats_len_before_filter - len(feats)}",
            )

    if mz is not None:
        feats_len_before_filter = len(feats)
        if isinstance(mz, tuple) and len(mz) == 2:
            min_mz, max_mz = mz
            feats = feats.filter((pl.col("mz") >= min_mz) & (pl.col("mz") <= max_mz))
        else:
            feats = feats.filter(pl.col("mz") >= mz)
        self.logger.debug(
            f"Selected features by mz. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if rt is not None:
        feats_len_before_filter = len(feats)
        if isinstance(rt, tuple) and len(rt) == 2:
            min_rt, max_rt = rt
            feats = feats.filter((pl.col("rt") >= min_rt) & (pl.col("rt") <= max_rt))
        else:
            feats = feats.filter(pl.col("rt") >= rt)
        self.logger.debug(
            f"Selected features by rt. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if inty is not None:
        feats_len_before_filter = len(feats)
        if isinstance(inty, tuple) and len(inty) == 2:
            min_inty, max_inty = inty
            feats = feats.filter(
                (pl.col("inty") >= min_inty) & (pl.col("inty") <= max_inty),
            )
        else:
            feats = feats.filter(pl.col("inty") >= inty)
        self.logger.debug(
            f"Selected features by intensity. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if rt_delta is not None:
        feats_len_before_filter = len(feats)
        if "rt_delta" not in feats.columns:
            self.logger.warning("No rt_delta data found in features.")
            return None
        if isinstance(rt_delta, tuple) and len(rt_delta) == 2:
            min_rt_delta, max_rt_delta = rt_delta
            feats = feats.filter(
                (pl.col("rt_delta") >= min_rt_delta)
                & (pl.col("rt_delta") <= max_rt_delta),
            )
        else:
            feats = feats.filter(pl.col("rt_delta") >= rt_delta)
        self.logger.debug(
            f"Selected features by rt_delta. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if iso is not None:
        feats_len_before_filter = len(feats)
        if isinstance(iso, tuple) and len(iso) == 2:
            min_iso, max_iso = iso
            feats = feats.filter(
                (pl.col("iso") >= min_iso) & (pl.col("iso") <= max_iso),
            )
        else:
            feats = feats.filter(pl.col("iso") == iso)
        self.logger.debug(
            f"Selected features by iso. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if iso_of is not None:
        feats_len_before_filter = len(feats)
        if isinstance(iso_of, tuple) and len(iso_of) == 2:
            min_iso_of, max_iso_of = iso_of
            feats = feats.filter(
                (pl.col("iso_of") >= min_iso_of) & (pl.col("iso_of") <= max_iso_of),
            )
        else:
            feats = feats.filter(pl.col("iso_of") == iso_of)
        self.logger.debug(
            f"Selected features by iso_of. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if has_MS2 is not None:
        feats_len_before_filter = len(feats)
        if has_MS2:
            feats = feats.filter(pl.col("ms2_scans").is_not_null())
        else:
            feats = feats.filter(pl.col("ms2_scans").is_null())
        self.logger.debug(
            f"Selected features by MS2 presence. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if prominence_scaled is not None:
        feats_len_before_filter = len(feats)
        if isinstance(prominence_scaled, tuple) and len(prominence_scaled) == 2:
            min_prominence_scaled, max_prominence_scaled = prominence_scaled
            feats = feats.filter(
                (pl.col("chrom_prominence_scaled") >= min_prominence_scaled)
                & (pl.col("chrom_prominence_scaled") <= max_prominence_scaled),
            )
        else:
            feats = feats.filter(pl.col("chrom_prominence_scaled") >= prominence_scaled)
        self.logger.debug(
            f"Selected features by prominence_scaled. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if height_scaled is not None:
        feats_len_before_filter = len(feats)
        if isinstance(height_scaled, tuple) and len(height_scaled) == 2:
            min_height_scaled, max_height_scaled = height_scaled
            feats = feats.filter(
                (pl.col("chrom_height_scaled") >= min_height_scaled)
                & (pl.col("chrom_height_scaled") <= max_height_scaled),
            )
        else:
            feats = feats.filter(pl.col("chrom_height_scaled") >= height_scaled)
        self.logger.debug(
            f"Selected features by height_scaled. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if prominence is not None:
        feats_len_before_filter = len(feats)
        if isinstance(prominence, tuple) and len(prominence) == 2:
            min_prominence, max_prominence = prominence
            feats = feats.filter(
                (pl.col("chrom_prominence") >= min_prominence)
                & (pl.col("chrom_prominence") <= max_prominence),
            )
        else:
            feats = feats.filter(pl.col("chrom_prominence") >= prominence)
        self.logger.debug(
            f"Selected features by prominence. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if height is not None:
        feats_len_before_filter = len(feats)
        # Check if chrom_height column exists, if not use chrom_height_scaled
        height_col = (
            "chrom_height" if "chrom_height" in feats.columns else "chrom_height_scaled"
        )
        if isinstance(height, tuple) and len(height) == 2:
            min_height, max_height = height
            feats = feats.filter(
                (pl.col(height_col) >= min_height) & (pl.col(height_col) <= max_height),
            )
        else:
            feats = feats.filter(pl.col(height_col) >= height)
        self.logger.debug(
            f"Selected features by {height_col}. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if adduct_group is not None:
        feats_len_before_filter = len(feats)
        if "adduct_group" not in feats.columns:
            self.logger.warning("No adduct_group data found in features.")
        else:
            if isinstance(adduct_group, tuple) and len(adduct_group) == 2:
                min_adduct_group, max_adduct_group = adduct_group
                feats = feats.filter(
                    (pl.col("adduct_group") >= min_adduct_group)
                    & (pl.col("adduct_group") <= max_adduct_group),
                )
            elif isinstance(adduct_group, list):
                feats = feats.filter(pl.col("adduct_group").is_in(adduct_group))
            else:
                feats = feats.filter(pl.col("adduct_group") == adduct_group)
            self.logger.debug(
                f"Selected features by adduct_group. Features removed: {feats_len_before_filter - len(feats)}",
            )

    if identified is not None:
        feats_len_before_filter = len(feats)
        if "id_top_name" not in feats.columns:
            self.logger.warning("No identification data found in features.")
        else:
            if identified:
                # Filter for features with identification (non-null id_top_name)
                feats = feats.filter(pl.col("id_top_name").is_not_null())
            else:
                # Filter for features without identification (null id_top_name)
                feats = feats.filter(pl.col("id_top_name").is_null())
            self.logger.debug(
                f"Selected features by identification presence. Features removed: {feats_len_before_filter - len(feats)}",
            )

    if id_top_name is not None:
        feats_len_before_filter = len(feats)
        if "id_top_name" not in feats.columns:
            self.logger.warning("No id_top_name data found in features.")
        else:
            if isinstance(id_top_name, list):
                # Use regex matching for each pattern in the list (OR logic)
                pattern = "|".join(id_top_name)
                feats = feats.filter(pl.col("id_top_name").str.contains(pattern))
            else:
                # Use regex matching for single pattern
                feats = feats.filter(pl.col("id_top_name").str.contains(id_top_name))
            self.logger.debug(
                f"Selected features by id_top_name (regex). Features removed: {feats_len_before_filter - len(feats)}",
            )

    if id_top_class is not None:
        feats_len_before_filter = len(feats)
        if "id_top_class" not in feats.columns:
            self.logger.warning("No id_top_class data found in features.")
        else:
            if isinstance(id_top_class, list):
                # Use regex matching for each pattern in the list (OR logic)
                pattern = "|".join(id_top_class)
                feats = feats.filter(pl.col("id_top_class").str.contains(pattern))
            else:
                # Use regex matching for single pattern
                feats = feats.filter(pl.col("id_top_class").str.contains(id_top_class))
            self.logger.debug(
                f"Selected features by id_top_class (regex). Features removed: {feats_len_before_filter - len(feats)}",
            )

    if id_top_adduct is not None:
        feats_len_before_filter = len(feats)
        if "id_top_adduct" not in feats.columns:
            self.logger.warning("No id_top_adduct data found in features.")
        else:
            if isinstance(id_top_adduct, list):
                feats = feats.filter(pl.col("id_top_adduct").is_in(id_top_adduct))
            else:
                feats = feats.filter(pl.col("id_top_adduct") == id_top_adduct)
            self.logger.debug(
                f"Selected features by id_top_adduct. Features removed: {feats_len_before_filter - len(feats)}",
            )

    if id_top_score is not None:
        feats_len_before_filter = len(feats)
        if "id_top_score" not in feats.columns:
            self.logger.warning("No id_top_score data found in features.")
        else:
            if isinstance(id_top_score, tuple) and len(id_top_score) == 2:
                min_score, max_score = id_top_score
                feats = feats.filter(
                    (pl.col("id_top_score") >= min_score)
                    & (pl.col("id_top_score") <= max_score),
                )
            else:
                feats = feats.filter(pl.col("id_top_score") >= id_top_score)
            self.logger.debug(
                f"Selected features by id_top_score. Features removed: {feats_len_before_filter - len(feats)}",
            )

    if len(feats) == 0:
        self.logger.warning("No features remaining after applying selection criteria.")
    else:
        self.logger.debug(f"Selected features. Features remaining: {len(feats)}")
    return feats


'''
def _features_sync(self):
    """
    Synchronizes the cached FeatureMap with features_df.

    This ensures that the cached FeatureMap (_oms_features_map) contains only features
    that exist in both the FeatureMap and the features_df. This is important
    after operations that modify features_df but not the FeatureMap (like filtering).

    Side Effects:
        Updates self._oms_features_map and self.features_df to contain only common features.
        Logs information about removed features.
    """
    if self.features_df is None or len(self.features_df) == 0:
        self.logger.debug("No features_df to synchronize")
        if hasattr(self, "_oms_features_map"):
            self._oms_features_map = None
        return

    # Check if we have a cached feature map
    if not hasattr(self, "_oms_features_map") or self._oms_features_map is None:
        self.logger.debug("No cached feature map to synchronize")
        return

    try:
        import pyopenms as oms
    except ImportError:
        self.logger.warning("PyOpenMS not available, cannot sync FeatureMap")
        return

    try:
        # Get feature IDs from both sources
        if "feature_id" in self.features_df.columns:
            df_feature_ids = set(
                self.features_df.get_column("feature_id").cast(str).to_list(),
            )
        else:
            self.logger.warning(
                "No feature_id column in features_df, cannot synchronize",
            )
            return

        # Get feature IDs from FeatureMap
        feature_map_ids = set()
        for i in range(self._oms_features_map.size()):
            feature = self._oms_features_map[i]
            unique_id = str(
                feature.getUniqueId(),
            )  # Convert to string to match DataFrame
            feature_map_ids.add(unique_id)

        # Find features that exist in both
        common_feature_ids = df_feature_ids & feature_map_ids

        # Safety check: log error and exit if no features are matching
        if not common_feature_ids:
            self.logger.error(
                f"No matching features found between FeatureMap and features_df. "
                f"FeatureMap has {len(feature_map_ids)} features, "
                f"features_df has {len(df_feature_ids)} features. "
                f"Cannot synchronize - this indicates a data inconsistency. Exiting without changes.",
            )
            return

        # Create new synchronized FeatureMap with only common features
        synced_feature_map = oms.FeatureMap()
        for i in range(self._oms_features_map.size()):
            feature = self._oms_features_map[i]
            unique_id = str(feature.getUniqueId())
            if unique_id in common_feature_ids:
                synced_feature_map.push_back(feature)

        # Filter features_df to only include features that exist in FeatureMap
        synced_features_df = self.features_df.filter(
            pl.col("feature_id").is_in(list(common_feature_ids)),
        )

        # Update the objects
        original_map_size = self._oms_features_map.size()
        original_df_size = len(self.features_df)

        self._oms_features_map = synced_feature_map
        self.features_df = synced_features_df

        # Log the synchronization results
        map_removed = original_map_size - self._oms_features_map.size()
        df_removed = original_df_size - len(self.features_df)

        # only log if features were removed
        if map_removed > 0 or df_removed > 0:
            self.logger.debug(
                f"Features synchronized. FeatureMap: {original_map_size} -> {self._oms_features_map.size()} "
                f"({map_removed} removed), DataFrame: {original_df_size} -> {len(self.features_df)} "
                f"({df_removed} removed)",
            )
        else:
            self.logger.debug(
                f"Features synchronized. FeatureMap: {original_map_size} -> {self._oms_features_map.size()} "
                f"({map_removed} removed), DataFrame: {original_df_size} -> {len(self.features_df)} "
                f"({df_removed} removed)",
            )

    except ImportError:
        self.logger.warning("PyOpenMS not available, cannot sync FeatureMap")
    except Exception as e:
        self.logger.error(f"Error during feature synchronization: {e}")
'''


def features_delete(self, features: list | None = None) -> None:
    """
    Delete features from both self.features_df and self._oms_features_map based on a list of feature UIDs.

    Parameters:
        features (list, optional): List of feature UIDs to delete. If None, all features will be deleted.

    Returns:
        None

    Side Effects:
        Updates self.features_df by removing specified features.
        Updates self._oms_features_map (OpenMS FeatureMap) by creating a new FeatureMap with only the remaining features.
        Updates self.scans_df by removing feature_id associations for deleted features.

    Note:
        The function preserves all OpenMS FeatureMap information by creating a new FeatureMap
        containing only the features that should remain after deletion.
    """
    if self.features_df is None:
        self.logger.warning("No features found.")
        return

    # Get the feature UIDs to delete
    feature_ids_to_delete = self._get_feature_ids(features=features, verbose=True)

    if not feature_ids_to_delete:
        self.logger.warning("No valid feature UIDs provided for deletion.")
        return

    original_count = len(self.features_df)

    # Update features_df by filtering out the features to delete
    self.features_df = self.features_df.filter(
        ~pl.col("feature_id").is_in(feature_ids_to_delete),
    )

    # Update the OpenMS FeatureMap by creating a new one with only features to keep
    if hasattr(self, "_oms_features_map") and self._oms_features_map is not None:
        try:
            # Import pyopenms
            import pyopenms as oms

            # Create new FeatureMap with only features to keep
            filtered_map = oms.FeatureMap()

            # Get the feature UIDs that should remain after deletion
            remaining_feature_ids = self.features_df.get_column(
                "feature_id",
            ).to_list()

            # Iterate through existing features and keep only those not in deletion list
            for i in range(self._oms_features_map.size()):
                feature = self._oms_features_map[i]
                # Since feature UIDs in DataFrame are sequential (0, 1, 2, ...) and correspond to indices
                # we can check if the current index is in the remaining UIDs
                if i in remaining_feature_ids:
                    filtered_map.push_back(feature)

            # Replace the original FeatureMap with the filtered one
            self._oms_features_map = filtered_map
            self.logger.debug(
                f"OpenMS FeatureMap updated with {filtered_map.size()} remaining features.",
            )

        except ImportError:
            self.logger.warning("PyOpenMS not available, only updating features_df")
        except Exception as e:
            self.logger.warning(
                f"Could not update OpenMS FeatureMap: {e}. FeatureMap may be out of sync.",
            )

    # Update scans_df to remove feature_id associations for deleted features
    if hasattr(self, "scans_df") and self.scans_df is not None:
        self.scans_df = self.scans_df.with_columns(
            pl.when(pl.col("feature_id").is_in(feature_ids_to_delete))
            .then(None)
            .otherwise(pl.col("feature_id"))
            .alias("feature_id"),
        )

    deleted_count = original_count - len(self.features_df)
    self.logger.info(
        f"Deleted {deleted_count} features. Remaining features: {len(self.features_df)}",
    )


def _delete_ms2(self):
    """
    Unlinks MS2 spectra from features in the dataset.
    This method removes the association between MS2 spectra and features in the features dataframe by setting
    the 'ms2_scans' and 'ms2_specs' columns to None. It also updates the scans dataframe to remove the feature
    id (feature_id) association for the linked MS2 spectra.
    Parameters:
    Returns:
        None
    Side Effects:
        Updates self.features_df by setting 'ms2_scans' and 'ms2_specs' columns to None. Also, updates self.scans_df
        by resetting the 'feature_id' column for linked MS2 spectra.
    """
    if self.features_df is None:
        # self.logger.warning("No features found.")
        return

    self.logger.debug("Unlinking MS2 spectra from features...")

    # Set ms2_scans and ms2_specs to None using Polars syntax
    self.features_df = self.features_df.with_columns(
        [
            pl.lit(None).alias("ms2_scans"),
            pl.lit(None).alias("ms2_specs"),
        ],
    )

    # Update scans_df to remove feature_id association for linked MS2 spectra
    self.scans_df = self.scans_df.with_columns(
        pl.when(pl.col("ms_level") == 2)
        .then(None)
        .otherwise(pl.col("feature_id"))
        .alias("feature_id"),
    )
    self.logger.info("MS2 spectra unlinked from features.")


def features_filter(self, features=None, **kwargs) -> None:
    """Keep only specified features, delete all others.

    Filters features_df to retain only specified features. Opposite of
    features_delete(). Updates OpenMS FeatureMap and unlinks deleted features
    from scans_df.

    Args:
        features (list | pl.DataFrame | pd.DataFrame | None): Features to keep.
            Options:
            - list: Feature IDs to retain
            - DataFrame: Must contain 'feature_id' column
            - None: Use **kwargs for selection criteria (passed to features_select)
        **kwargs: If features=None, selection criteria passed to features_select().
            Common filters: mz, rt, inty, quality, coherence, has_MS2, identified.

    Example:
        Filter by DataFrame::

            >>> sample = masster.Sample("data.mzML")
            >>> sample.find_features()
            >>>
            >>> # Keep high-quality features
            >>> high_quality = sample.features_df.filter(
            ...     pl.col("quality") > 0.8
            ... )
            >>> sample.features_filter(high_quality)

        Filter by ID list::

            >>> good_features = [1, 5, 10, 15, 20]
            >>> sample.features_filter(good_features)

        Filter using kwargs::

            >>> # Keep features with MS2 data
            >>> sample.features_filter(has_MS2=True)
            >>>
            >>> # Keep high-intensity features in RT range
            >>> sample.features_filter(
            ...     inty=(1e6, None),
            ...     rt=(5.0, 15.0)
            ... )

        Multi-criteria filtering::

            >>> sample.features_filter(
            ...     quality=(0.7, None),
            ...     coherence=(0.6, None),
            ...     identified=True
            ... )

        Check results::

            >>> before = 1000
            >>> sample.features_filter(quality=(0.8, None))
            >>> after = len(sample.features_df)
            >>> print(f"Removed {before - after} features")

    Note:
        **Irreversible operation:**

        Permanently removes features from sample. Deleted features cannot be
        recovered without reloading/reprocessing file.

        **Side effects:**

        - Updates features_df by removing rows
        - Synchronizes OpenMS FeatureMap (removes OpenMS Feature objects)
        - Unlinks deleted features from scans_df (sets feature_id=None)
        - Stores operation in history with kept/deleted counts

        **OpenMS FeatureMap sync:**

        If _oms_features_map exists, creates new FeatureMap containing only
        retained features. Preserves all OpenMS metadata.

        **Scan unlinking:**

        MS2 scans previously linked to deleted features are unlinked (feature_id
        set to None in scans_df). Scan data itself is not deleted.

        **Use features_select() first:**

        To preview which features will be kept::

            >>> preview = sample.features_select(quality=(0.8, None))
            >>> print(f"Will keep {len(preview)} features")
            >>> sample.features_filter(preview)

        **Alternatives:**

        - features_delete(): Delete specified features, keep rest
        - features_select(): Query features without modification

    Raises:
        Warning: If no features or criteria specified.

    See Also:
        features_delete: Delete specified features (opposite operation).
        features_select: Query features without modification.
        find_features: Detect features before filtering.
    """
    if self.features_df is None:
        self.logger.warning("No features found.")
        return

    if features is None and not kwargs:
        self.logger.warning(
            "No features or selection criteria specified to keep. Use features_delete() to delete all features.",
        )
        return

    if features is None and kwargs:
        features = self.features_select(**kwargs)

    # Get the feature UIDs to keep
    feature_ids_to_keep = self._get_feature_ids(features=features, verbose=True)

    if not feature_ids_to_keep:
        self.logger.warning("No valid feature UIDs provided to keep.")
        return

    original_count = len(self.features_df)

    # Update features_df by keeping only the specified features
    self.features_df = self.features_df.filter(
        pl.col("feature_id").is_in(feature_ids_to_keep),
    )

    # Calculate which features were deleted (all except the ones to keep)
    all_feature_ids = set(range(original_count))  # Assuming sequential UIDs
    feature_ids_to_delete = list(all_feature_ids - set(feature_ids_to_keep))

    # Update the OpenMS FeatureMap by creating a new one with only features to keep
    if hasattr(self, "_oms_features_map") and self._oms_features_map is not None:
        try:
            # Import pyopenms
            import pyopenms as oms

            # Create new FeatureMap with only features to keep
            filtered_map = oms.FeatureMap()

            # Iterate through existing features and keep only those in the keep list
            for i in range(self._oms_features_map.size()):
                feature = self._oms_features_map[i]
                # Since feature UIDs in DataFrame are sequential (0, 1, 2, ...) and correspond to indices
                # we can check if the current index is in the keep UIDs
                if i in feature_ids_to_keep:
                    filtered_map.push_back(feature)

            # Replace the original FeatureMap with the filtered one
            self._oms_features_map = filtered_map
            self.logger.debug(
                f"OpenMS FeatureMap updated with {filtered_map.size()} remaining features.",
            )

        except ImportError:
            self.logger.warning("PyOpenMS not available, only updating features_df")
        except Exception as e:
            self.logger.warning(
                f"Could not update OpenMS FeatureMap: {e}. FeatureMap may be out of sync.",
            )

    # Update scans_df to remove feature_id associations for deleted features
    if (
        hasattr(self, "scans_df")
        and self.scans_df is not None
        and feature_ids_to_delete
    ):
        self.scans_df = self.scans_df.with_columns(
            pl.when(pl.col("feature_id").is_in(feature_ids_to_delete))
            .then(None)
            .otherwise(pl.col("feature_id"))
            .alias("feature_id"),
        )

    kept_count = len(self.features_df)
    deleted_count = original_count - kept_count
    self.logger.info(
        f"Kept {kept_count} features, deleted {deleted_count} features. Remaining features: {kept_count}",
    )

    # Store filtering parameters in history
    self.update_history(
        ["features_filter"],
        {
            "kept_count": kept_count,
            "deleted_count": deleted_count,
            "total_count": original_count,
        },
    )


def set_source(self, filename):
    """
    Reassign file_source. If filename contains only a path, keep the current basename
    and build an absolute path. Check that the new file exists before overwriting
    the old file_source.

    Parameters:
        filename (str): New file path or directory path

    Returns:
        None
    """
    import os

    # Store the old file_source for logging
    old_file_source = getattr(self, "file_source", None)

    # Check if filename is just a directory path
    if os.path.isdir(filename):
        if old_file_source is None:
            self.logger.error("Cannot build path: no current file_source available")
            return

        # Get the basename from current file_source
        current_basename = os.path.basename(old_file_source)
        # Build new absolute path
        new_file_path = os.path.join(filename, current_basename)
    else:
        # filename is a full path, make it absolute
        new_file_path = os.path.abspath(filename)

    # Check if the new file exists
    if not os.path.exists(new_file_path):
        self.logger.error(f"File does not exist: {new_file_path}")
        return

    # Update file_source
    self.file_source = new_file_path

    # Log the change
    if old_file_source is not None:
        self.logger.info(
            f"Updated file_source from {old_file_source} to {self.file_source}",
        )
    else:
        self.logger.info(f"Set file_source to {self.file_source}")


def _recreate_feature_map(self):
    """
    Recreate OpenMS FeatureMap from features_df.

    This helper function creates a new OpenMS FeatureMap using the data from features_df.
    This allows us to avoid storing and loading featureXML files by default, while still
    being able to recreate the feature map when needed for OpenMS operations like
    find_features() or saving to featureXML format.

    Returns:
        oms.FeatureMap: A new FeatureMap with features from features_df, or None if no features

    Side Effects:
        Caches the created feature map in self._oms_features_map for reuse
    """
    if self.features_df is None or len(self.features_df) == 0:
        self.logger.debug("No features_df available to recreate feature map")
        return None

    try:
        import pyopenms as oms
    except ImportError:
        self.logger.warning("PyOpenMS not available, cannot recreate feature map")
        return None

    # Create new FeatureMap
    feature_map = oms.FeatureMap()

    # Set the primary MS run path if available
    if hasattr(self, "file_path") and self.file_path:
        feature_map.setPrimaryMSRunPath([self.file_path.encode()])

    # Convert DataFrame features to OpenMS Features
    for i, feature_row in enumerate(self.features_df.iter_rows(named=True)):
        feature = oms.Feature()

        # Set basic properties from DataFrame (handle missing values gracefully)
        try:
            if feature_row.get("feature_id") is not None:
                feature.setUniqueId(int(feature_row["feature_id"]))
            else:
                feature.setUniqueId(i)  # Use index as fallback

            if feature_row.get("mz") is not None:
                feature.setMZ(float(feature_row["mz"]))
            if feature_row.get("rt") is not None:
                feature.setRT(float(feature_row["rt"]))
            if feature_row.get("inty") is not None:
                feature.setIntensity(float(feature_row["inty"]))
            if feature_row.get("quality") is not None:
                feature.setOverallQuality(float(feature_row["quality"]))
            if feature_row.get("charge") is not None:
                feature.setCharge(int(feature_row["charge"]))

            # Add to feature map
            feature_map.push_back(feature)

        except (ValueError, TypeError) as e:
            self.logger.warning(f"Skipping feature due to conversion error: {e}")
            continue

    # Ensure unique IDs
    feature_map.ensureUniqueId()

    # Cache the feature map
    self._oms_features_map = feature_map

    self.logger.debug(
        f"Recreated FeatureMap with {feature_map.size()} features from features_df",
    )
    return feature_map


def _get_feature_map(self):
    """
    Get the OpenMS FeatureMap, creating it from features_df if needed.

    This property-like method returns the cached feature map if available,
    or recreates it from features_df if not. This allows lazy loading of
    feature maps only when needed for OpenMS operations.

    Returns:
        oms.FeatureMap or None: The feature map, or None if not available
    """
    # Return cached feature map if available
    if hasattr(self, "_oms_features_map") and self._oms_features_map is not None:
        return self._oms_features_map

    # Otherwise recreate from features_df
    return self._recreate_feature_map()


def features_compare(
    self,
    reference=None,
    mz_tol=0.005,
    rt_tol=10,
    selection="sample",
):
    """
    Compare features between this sample and a reference sample.

    Finds common and unique features based on m/z and retention time tolerances,
    and returns a subset based on the selection parameter.

    Parameters:
        reference (Sample): Reference sample to compare against. Required.
        mz_tol (float): m/z tolerance for matching features (default: 0.005 Da)
        rt_tol (float): Retention time tolerance for matching features (default: 10 seconds)
        selection (str): Which features to return. Options:
            - "sample": Features unique to this sample (default)
            - "common": Features common to both samples
            - "reference": Features unique to the reference sample

    Returns:
        pl.DataFrame: Polars DataFrame containing the selected features
    """
    if reference is None:
        self.logger.error("Reference sample is required for comparison")
        return None

    if self.features_df is None or len(self.features_df) == 0:
        self.logger.error("No features found in current sample")
        return None

    if reference.features_df is None or len(reference.features_df) == 0:
        self.logger.error("No features found in reference sample")
        return None

    # Validate selection parameter
    valid_selections = ["sample", "common", "reference"]
    if selection not in valid_selections:
        self.logger.error(
            f"Invalid selection '{selection}'. Must be one of {valid_selections}",
        )
        return None

    # Work on copies
    feats_self = self.features_df.clone()
    feats_ref = reference.features_df.clone()

    self.logger.info(
        f"Comparing {len(feats_self)} features from sample vs {len(feats_ref)} features from reference",
    )

    # Add row indices to track features
    feats_self = feats_self.with_row_index("_idx_self")
    feats_ref = feats_ref.with_row_index("_idx_ref")

    # Initialize comparison status columns
    feats_self = feats_self.with_columns(
        pl.lit("unique_self").alias("comparison_status"),
    )
    feats_ref = feats_ref.with_columns(pl.lit("unique_ref").alias("comparison_status"))

    # Find common features using cross join with tolerance conditions
    common_self_indices = set()
    common_ref_indices = set()

    # Extract mz and rt as numpy arrays for faster iteration
    self_mz = feats_self["mz"].to_numpy()
    self_rt = feats_self["rt"].to_numpy()
    ref_mz = feats_ref["mz"].to_numpy()
    ref_rt = feats_ref["rt"].to_numpy()

    for idx_self in range(len(feats_self)):
        mz_self = self_mz[idx_self]
        rt_self = self_rt[idx_self]

        # Find matching features in reference
        mz_match = abs(ref_mz - mz_self) <= mz_tol
        rt_match = abs(ref_rt - rt_self) <= rt_tol
        matches = mz_match & rt_match

        if matches.any():
            common_self_indices.add(idx_self)
            common_ref_indices.update(matches.nonzero()[0].tolist())

    # Update comparison status using polars
    feats_self = feats_self.with_columns(
        pl.when(pl.col("_idx_self").is_in(list(common_self_indices)))
        .then(pl.lit("common"))
        .otherwise(pl.col("comparison_status"))
        .alias("comparison_status"),
    )

    feats_ref = feats_ref.with_columns(
        pl.when(pl.col("_idx_ref").is_in(list(common_ref_indices)))
        .then(pl.lit("common"))
        .otherwise(pl.col("comparison_status"))
        .alias("comparison_status"),
    )

    # Get feature counts
    unique_self = feats_self.filter(pl.col("comparison_status") == "unique_self")
    common_features = feats_self.filter(pl.col("comparison_status") == "common")
    unique_ref = feats_ref.filter(pl.col("comparison_status") == "unique_ref")

    self.logger.info(
        f"Found {len(unique_self)} unique to sample, {len(common_features)} common, {len(unique_ref)} unique to reference",
    )

    # Select and return the requested subset
    if selection == "sample":
        result_df = unique_self.drop(["comparison_status", "_idx_self"])
        self.logger.info(f"Returning {len(result_df)} features unique to sample")
    elif selection == "common":
        result_df = common_features.drop(["comparison_status", "_idx_self"])
        self.logger.info(f"Returning {len(result_df)} common features")
    elif selection == "reference":
        result_df = unique_ref.drop(["comparison_status", "_idx_ref"])
        self.logger.info(f"Returning {len(result_df)} features unique to reference")

    return result_df
