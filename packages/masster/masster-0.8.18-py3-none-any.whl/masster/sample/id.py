# mypy: disable-error-code="misc,assignment,no-any-return"
"""sample/id.py

Identification helpers for Sample: load a Lib and identify features
by matching m/z (and optionally RT).
"""

from __future__ import annotations

import logging
import os
from typing import Any

import polars as pl

from masster.exceptions import ConfigurationError, DataValidationError, LibraryError

logger = logging.getLogger(__name__)


def _resolve_library_path(file: str | None) -> str | None:
    """
    Resolve library name or path to full file path.

    Handles embedded library names (like 'yeast', 'ecoli', 'human') and paths.

    Args:
        file: Library name or path

    Returns:
        str | None: Full path to library file

    Raises:
        FileNotFoundError: If library file cannot be found
    """
    if file is None:
        return None

    # Handle special/embedded library names
    special_libs = {
        "ecoli": "ecoli.json",
        "hsapiens": "hsapiens.json",
        "human": "hsapiens.json",
        "scerevisiae": "scerevisiae.json",
        "sce": "scerevisiae.json",
        "yeast": "scerevisiae.json",
        "aa": "aa.json",
        "core": "core.json",
    }

    file_lower = file.lower() if file else None
    if file_lower and file_lower in special_libs:
        import pathlib

        # Get the path to masster/data/libs/
        masster_data_libs = (
            pathlib.Path(__file__).parent.parent
            / "data"
            / "libs"
            / special_libs[file_lower]
        )
        return str(masster_data_libs)

    # If it's already a full path or has an extension, return as-is
    if os.path.sep in file or "/" in file or "." in file:
        return file

    # Try to find library in standard locations
    # Get the masster package directory
    import masster

    package_dir = os.path.dirname(os.path.dirname(masster.__file__))
    libs_dir = os.path.join(package_dir, "libs")

    # Check for common library extensions
    for ext in [".json", ".csv", "_nort.json", "_nort.csv"]:
        lib_path = os.path.join(libs_dir, file + ext)
        if os.path.exists(lib_path):
            return lib_path

    # If not found, return original (will raise FileNotFoundError later)
    return file


def lib_load(
    sample,
    lib_source: str | Any,
    polarity: str | None = None,
    adducts: list[str] | None = None,
    iso: str | None = None,
) -> None:
    """Load compound library for feature identification.

    Loads spectral library from file or Lib object, filters by polarity, and
    stores in sample.lib_df for use with identify() method.

    Args:
        sample (Sample): Sample instance to load library into.
        lib_source (str | Lib): Library source. Options:
            - Built-in library name: 'hsapiens', 'mmusculus', 'ecoli', 'yeast',
              'scerevisiae', 'athaliana', 'urine', 'plasma'
            - CSV file path: Custom library file
            - JSON file path: Pre-formatted masster library
            - Lib instance: Existing library object
        polarity (str | None): Ionization mode. Options: 'positive', 'pos',
            'negative', 'neg'. If None, uses sample.polarity automatically.
            Defaults to None.
        adducts (list[str] | None): Specific adducts to generate. Format:
            ['[M+H]+', '[M+Na]+', '[M+K]+']. If None, uses default adduct set
            for polarity. Defaults to None.
        iso (str | None): Isotope generation mode. Options: '13C' generates 13C
            isotopes, None for no isotopes. Defaults to None.

    Example:
        Load built-in library::

            >>> sample = masster.Sample("data.mzML")
            >>> sample.lib_load("hsapiens")
            >>> print(f"Loaded {len(sample.lib_df)} library entries")

        Custom library with specific adducts::

            >>> sample.lib_load(
            ...     "my_compounds.csv",
            ...     adducts=['[M+H]+', '[M+Na]+', '[M+NH4]+']
            ... )

        Explicit polarity::

            >>> sample.lib_load("hsapiens", polarity="negative")

        Load with isotopes::

            >>> sample.lib_load("hsapiens", iso="13C")

        Access loaded library::

            >>> sample.lib_load("hsapiens")
            >>> print(sample.lib_df.select(["name", "formula", "adduct", "mz"]))
            >>>
            >>> # Check library size
            >>> unique_compounds = sample.lib_df["cmpd_id"].n_unique()
            >>> print(f"{unique_compounds} unique compounds")

    Note:
        **Built-in libraries:**

        - hsapiens: Human metabolome
        - mmusculus: Mouse metabolome
        - ecoli / yeast / scerevisiae: Microbial metabolomes
        - athaliana: Plant metabolome
        - urine / plasma: Biological fluid metabolomes

        **Library structure (lib_df columns):**

        - lib_id: Unique library entry identifier
        - cmpd_id: Compound identifier (multiple entries per compound)
        - name: Compound name
        - formula: Molecular formula
        - adduct: Adduct type ([M+H]+, [M+Na]+, etc.)
        - mz: Calculated m/z value
        - rt: Retention time (if available)
        - smiles: SMILES notation
        - inchikey: InChI key for database linking
        - probability: Adduct probability for scoring

        **Polarity filtering:**

        Library automatically filtered to match sample polarity. Positive mode
        keeps z=[1,2], negative mode keeps z=[-1,-2].

        **Automatic polarity detection:**

        If polarity=None, uses sample.polarity attribute. Normalizes 'pos'->'positive',
        'neg'->'negative'.

        **Custom libraries:**

        CSV files must contain at minimum: name, formula columns. Optional:
        rt, smiles, inchikey, class, stars (quality rating).

    Raises:
        ValueError: If lib_source is None or library has no data.
        TypeError: If lib_source type is invalid.
        ImportError: If Lib class cannot be imported.

    See Also:
        identify: Match features against loaded library.
        lib_reset: Clear library and identification results.
        lib_select: Query library entries.
        lib_filter: Filter library by criteria.
        get_id: Retrieve identification results.
    """
    # Lazy import to avoid circular imports at module import time
    try:
        from masster.lib.lib import Lib
    except Exception:
        Lib = None

    if lib_source is None:
        raise LibraryError(
            "Cannot load library: lib_source parameter is required.\n\n"
            "Provide either:\n"
            "  1. Path to library file: sample.lib_load(lib_source='libs/hilic.json')\n"
            "  2. A Lib instance: sample.lib_load(lib_source=my_lib_object)",
        )

    # Use sample polarity if not explicitly provided
    if polarity is None:
        sample_polarity = getattr(sample, "polarity", "positive")
        # Normalize polarity names
        if sample_polarity in ["pos", "positive"]:
            polarity = "positive"
        elif sample_polarity in ["neg", "negative"]:
            polarity = "negative"
        else:
            polarity = "positive"  # Default fallback
        sample.logger.debug(f"Using sample polarity: {polarity}")

    # Handle string input (CSV or JSON file path)
    if isinstance(lib_source, str):
        if Lib is None:
            raise ImportError(
                "Could not import masster.lib.lib.Lib - required for CSV/JSON loading",
            )

        # Resolve library name to full path (handles embedded libraries like 'yeast', 'ecoli', etc.)
        lib_source = _resolve_library_path(lib_source)

        if lib_source is None:
            raise FileNotFoundError("Could not resolve library path")

        lib_obj = Lib()

        # Determine file type by extension
        if lib_source.lower().endswith(".json"):
            lib_obj.import_json(lib_source, polarity=polarity, adducts=adducts)
        elif lib_source.lower().endswith(".csv"):
            lib_obj.import_csv(lib_source, polarity=polarity, adducts=adducts)
        else:
            # Default to CSV behavior for backward compatibility
            lib_obj.import_csv(lib_source, polarity=polarity, adducts=adducts)

    # Handle Lib instance
    elif (Lib is not None and isinstance(lib_source, Lib)) or hasattr(
        lib_source,
        "lib_df",
    ):
        lib_obj = lib_source

    else:
        raise TypeError(
            "lib_source must be a CSV/JSON file path (str), a masster.lib.Lib instance, or have a 'lib_df' attribute",
        )

    # Ensure lib_df is populated
    lf = getattr(lib_obj, "lib_df", None)
    if lf is None or (hasattr(lf, "is_empty") and lf.is_empty()):
        raise LibraryError(
            f"Library file loaded but contains no compounds.\n"
            f"Library source: {lib_source}\n\n"
            "Please check that the library file is not empty and is properly formatted.",
        )

    # Filter by polarity to match sample
    # Map polarity to charge signs
    if polarity == "positive":
        target_charges = [1, 2]  # positive charges
    elif polarity == "negative":
        target_charges = [-1, -2]  # negative charges
    else:
        target_charges = [-2, -1, 1, 2]  # all charges

    # Filter library entries by charge sign (which corresponds to polarity)
    filtered_lf = lf.filter(pl.col("z").is_in(target_charges))

    if filtered_lf.is_empty():
        print(
            f"Warning: No library entries found for polarity '{polarity}'. Using all entries.",
        )
        filtered_lf = lf

    # Store pointer and DataFrame on sample
    sample._lib = lib_obj

    # Add lib_source and db columns
    if isinstance(lib_source, str):
        import os

        filename_only = os.path.basename(lib_source)
        # Remove .json or .csv extension
        if filename_only.lower().endswith(".json"):
            filename_only = filename_only[:-5]
        elif filename_only.lower().endswith(".csv"):
            filename_only = filename_only[:-4]
        # Set lib_source to "masster" and db to the filename without extension
        filtered_lf = filtered_lf.with_columns(
            [pl.lit("masster").alias("lib_source"), pl.lit(filename_only).alias("db")],
        )
    else:
        # If not loading from file, still add lib_source="masster" but db will be None
        filtered_lf = filtered_lf.with_columns(
            [
                pl.lit("masster").alias("lib_source"),
                pl.lit(None, dtype=pl.String).alias("db"),
            ],
        )

    # Ensure required columns exist and set correct values
    required_columns = {"quant_group": pl.Int64, "iso": pl.Int64}

    for col_name, col_dtype in required_columns.items():
        if col_name == "quant_group":
            # Set quant_group using cmpd_id (same for isotopomers of same compound)
            if "cmpd_id" in filtered_lf.columns:
                filtered_lf = filtered_lf.with_columns(
                    pl.col("cmpd_id").cast(col_dtype).alias("quant_group"),
                )
            else:
                # Fallback to lib_id if cmpd_id doesn't exist
                filtered_lf = filtered_lf.with_columns(
                    pl.col("lib_id").cast(col_dtype).alias("quant_group"),
                )
        elif col_name == "iso":
            if col_name not in filtered_lf.columns:
                # Default to zero for iso
                filtered_lf = filtered_lf.with_columns(
                    pl.lit(0).cast(col_dtype).alias(col_name),
                )

    # Generate 13C isotopes if requested
    original_count = len(filtered_lf)
    if iso == "13C":
        filtered_lf = _generate_13c_isotopes(filtered_lf)
        # Update the log message to show the correct count after isotope generation
        if isinstance(lib_source, str):
            import os

            filename_only = os.path.basename(lib_source)
            print(
                f"Generated 13C isotopes: {len(filtered_lf)} total entries ({original_count} original + {len(filtered_lf) - original_count} isotopes) from {filename_only}",
            )

    # Append to existing lib_df or create new one
    if (
        hasattr(sample, "lib_df")
        and sample.lib_df is not None
        and not sample.lib_df.is_empty()
    ):
        # Ensure schema compatibility before concatenating
        existing_cols = set(sample.lib_df.columns)
        new_cols = set(filtered_lf.columns)

        # Align schemas
        if existing_cols != new_cols:
            # Add missing columns to new data
            for col in existing_cols - new_cols:
                filtered_lf = filtered_lf.with_columns(pl.lit(None).alias(col))

            # Add missing columns to existing data
            for col in new_cols - existing_cols:
                sample.lib_df = sample.lib_df.with_columns(pl.lit(None).alias(col))

        # Cast columns in new dataframe to match existing schema
        for col in sample.lib_df.columns:
            if col in filtered_lf.columns:
                existing_dtype = sample.lib_df[col].dtype
                new_dtype = filtered_lf[col].dtype
                if existing_dtype != new_dtype:
                    try:
                        filtered_lf = filtered_lf.with_columns(
                            pl.col(col).cast(existing_dtype),
                        )
                    except Exception:
                        # If casting fails, cast existing to string as fallback
                        sample.lib_df = sample.lib_df.with_columns(
                            pl.col(col).cast(pl.String),
                        )
                        filtered_lf = filtered_lf.with_columns(
                            pl.col(col).cast(pl.String),
                        )

        # Ensure column order matches
        filtered_lf = filtered_lf.select(sample.lib_df.columns)

        # Renumber lib_id in new entries to avoid conflicts with existing lib_df
        # Find the maximum lib_id in existing lib_df
        max_existing_lib_id = sample.lib_df.select(pl.col("lib_id").max()).item()
        if max_existing_lib_id is None:
            max_existing_lib_id = -1

        # Renumber lib_id in filtered_lf starting from max_existing_lib_id + 1
        filtered_lf = filtered_lf.with_columns(
            (pl.col("lib_id") - pl.col("lib_id").min() + max_existing_lib_id + 1).alias(
                "lib_id",
            ),
        )

        # Also update quant_group if it references lib_id (only if it's numeric)
        if "quant_group" in filtered_lf.columns:
            # Check if quant_group is numeric type
            quant_group_dtype = filtered_lf["quant_group"].dtype
            if quant_group_dtype in [
                pl.Int64,
                pl.Int32,
                pl.Int16,
                pl.Int8,
                pl.UInt64,
                pl.UInt32,
                pl.UInt16,
                pl.UInt8,
                pl.Float64,
                pl.Float32,
            ]:
                # Only renumber if it's numeric
                filtered_lf = filtered_lf.with_columns(
                    (
                        pl.col("quant_group")
                        - pl.col("quant_group").min()
                        + max_existing_lib_id
                        + 1
                    ).alias("quant_group"),
                )

        # Append new library entries to existing lib_df
        sample.lib_df = pl.concat([sample.lib_df, filtered_lf])

        # Update _lib object to reflect the combined lib_df
        if hasattr(sample, "_lib") and sample._lib is not None:
            sample._lib.lib_df = sample.lib_df

        if logger:
            logger.info(
                f"Appended {len(filtered_lf)} library entries to existing {len(sample.lib_df) - len(filtered_lf)} entries",
            )
    else:
        # Store library as new Polars DataFrame
        sample.lib_df = filtered_lf

    # Store this operation in history
    if hasattr(sample, "update_history"):
        sample.update_history(
            ["lib_load"],
            {
                "lib_source": str(lib_source),
                "polarity": polarity,
                "adducts": adducts,
                "iso": iso,
            },
        )


def identify(
    sample,
    features=None,
    params=None,
    only_masster: bool = True,
    only_orphans: bool = True,
    **kwargs,
) -> None:
    """Identify features by matching against spectral library.

    Matches features to library entries using accurate mass (m/z) and optionally
    retention time. Scoring incorporates adduct probabilities and penalties for
    heteroatoms, multiple formulas, or multiple compound matches.

    Args:
        sample (Sample): Sample instance with features_df and lib_df populated.
        features (list[int] | pl.DataFrame | None): Feature IDs to identify. None
            identifies all features. Defaults to None.
        params (identify_defaults | None): Pre-configured parameter object. If None,
            uses defaults. Defaults to None.
        only_masster (bool): If True, only match against lib_df rows where lib_source
            starts with "masster" (loaded via lib_load()). If False, match all
            library entries including imported data. Defaults to True.
        only_orphans (bool): If True, only identify features without existing
            identifications in id_df. If False, re-identify all specified features.
            Defaults to True.
        **kwargs: Individual parameter overrides:

            **Matching Tolerances:**
                mz_tol (float): m/z tolerance in Daltons. Defaults to 0.01.
                rt_tol (float | None): Retention time tolerance in minutes. None
                    disables RT filtering. Defaults to 2.0.

            **Scoring Penalties:**
                heteroatom_penalty (float): Score multiplier for formulas with
                    heteroatoms (Cl, Br, F, I). Range 0.0-1.0. Defaults to 0.7.
                multiple_formulas_penalty (float): Score multiplier when multiple
                    formulas match. Range 0.0-1.0. Defaults to 0.8.
                multiple_compounds_penalty (float): Score multiplier when multiple
                    compounds match. Range 0.0-1.0. Defaults to 0.8.
                heteroatoms (list[str]): Elements to apply penalty for. Defaults
                    to ["Cl", "Br", "F", "I"].

    Example:
        Basic identification::

            >>> sample.lib_load("hsapiens")
            >>> sample.identify()
            >>> print(f"Identified {len(sample.id_df)} matches")

        Custom tolerances::

            >>> sample.identify(mz_tol=0.005, rt_tol=1.0)

        Include all library sources::

            >>> sample.identify(only_masster=False, only_orphans=False)

        Fill gaps after TIMA import::

            >>> sample.import_tima(folder="tima_results")
            >>> sample.lib_load("hsapiens")
            >>> sample.identify(only_orphans=True)

        Re-identify with different library::

            >>> sample.lib_load("ecoli")
            >>> sample.identify(only_orphans=False)

        Target specific features::

            >>> high_quality_ids = sample.features_df.filter(
            ...     pl.col("quality") > 0.8
            ... )["feature_id"].to_list()
            >>> sample.identify(features=high_quality_ids)

    Note:
        - Requires lib_load() before identification
        - RT filtering disabled automatically if library lacks RT data
        - Score calculation: base = adduct probability (0-100), then apply penalties
        - Results stored in id_df with columns:
            - feature_id: Feature identifier
            - lib_id: Library entry identifier
            - mz_delta: Absolute m/z difference (Da)
            - rt_delta: Absolute RT difference (min, nullable)
            - matcher: Identification method ("masster-ms1")
            - id_source: Full source identifier (e.g., "masster-ms1-hsapiens")
            - score: Matching score (0-100, higher is better)
        - Updates features_df with id_top_* columns for best match
        - Use get_id() to retrieve results with full annotations

    Raises:
        ValueError: If lib_df or features_df is empty.

    See Also:
        identify_defaults: Parameter configuration for identification.
        lib_load: Load spectral library.
        get_id: Retrieve identification results with annotations.
        id_reset: Clear identification results.
        export_excel: Export identifications to Excel.
    """
    # Get logger from sample if available
    logger = getattr(sample, "logger", None)

    # Setup parameters
    params = _setup_identify_parameters(params, kwargs)
    effective_mz_tol = getattr(params, "mz_tol", 0.01)
    effective_rt_tol = getattr(params, "rt_tol", 2.0)

    if logger:
        logger.debug(
            f"Starting identification with mz_tolerance={effective_mz_tol}, rt_tolerance={effective_rt_tol}",
        )

    # Validate inputs
    if not _validate_identify_inputs(sample, logger):
        return

    # Prepare features and determine target UIDs
    features_to_process, target_uids = _prepare_features(
        sample,
        features,
        only_orphans,
        logger,
    )
    if features_to_process is None:
        return

    # Smart reset of id_df: only clear results for features being re-identified
    _smart_reset_id_results(sample, target_uids, logger)

    # Cache adduct probabilities (expensive operation)
    adduct_prob_map = _get_cached_adduct_probabilities(sample, logger)

    # Perform identification with optimized matching
    results = _perform_identification_matching(
        features_to_process,
        sample,
        effective_mz_tol,
        effective_rt_tol,
        adduct_prob_map,
        only_masster,
        logger,
    )

    # Update or append results to sample.id_df
    _update_identification_results(sample, results, logger)

    # Apply scoring adjustments and update features_df (only for features just processed)
    _finalize_identification_results(sample, params, target_uids, logger)

    # Store operation in history
    _store_identification_history(
        sample,
        effective_mz_tol,
        effective_rt_tol,
        target_uids,
        params,
        kwargs,
    )

    # Log final statistics
    features_count = len(features_to_process)
    if logger:
        features_with_matches = len([r for r in results if len(r["matches"]) > 0])
        total_matches = sum(len(r["matches"]) for r in results)
        logger.success(
            f"Identification completed: {features_with_matches}/{features_count} features matched, {total_matches} total identifications",
        )


def get_id(sample, features=None) -> pl.DataFrame:
    """Get identification results with comprehensive annotation data.

    Combines identification results (id_df) with library and feature information to
    provide complete compound data including names, formulas, adducts, structure
    identifiers, and matching scores.

    Args:
        sample (Sample): Sample instance with id_df, lib_df, and features_df populated.
        features (list[int] | pl.DataFrame | pd.DataFrame | None): Optional filter for
            specific features. Can be:

            - None: Return all identification results (default)
            - list[int]: List of feature_id values to filter
            - DataFrame: DataFrame with feature_id column to extract IDs

    Returns:
        pl.DataFrame: Polars DataFrame with enriched identification data containing:

            - feature_id: Feature identifier
            - cmpd_id: Compound unique identifier (if available)
            - lib_id: Library entry identifier
            - name: Compound name from library
            - shortname: Short name from library (if available)
            - class: Compound class from library (if available)
            - formula: Molecular formula
            - adduct: Adduct type (e.g., "[M+H]+", "[M-H]-")
            - mz: Feature m/z value
            - mz_delta: Absolute m/z difference between feature and library
            - rt: Feature retention time (seconds)
            - rt_delta: Absolute RT difference (nullable)
            - matcher: Identification method (e.g., "masster-ms1", "masster-ms2")
            - score: Matching score (0.0-1.0)
            - stars: Confidence rating from library
            - id_source: Full source identifier
            - smiles: SMILES notation (if available)
            - inchikey: InChIKey identifier (if available)
            - Additional library columns: inchi, db_id, db (if present)

    Example:
        ::

            from masster import Sample

            # Load and identify sample
            s = Sample(file="data.mzML")
            s.find_features()
            s.lib_load("mmc")
            s.identify()

            # Get all identification results
            id_results = s.get_id()
            print(f"Total identifications: {len(id_results)}")

            # Get identifications for specific features
            subset = s.get_id(features=[1, 2, 3])

            # Filter by score and get IDs
            high_score = id_results.filter(pl.col("score") > 0.8)
            print(high_score[["name", "adduct", "score"]])

            # Get identifications for selected features
            selected = s.features_select(has_MS2=True, score=0.7)
            ids = s.get_id(features=selected)

    Note:
        **Prerequisites:**

        Requires three DataFrames to be populated:

        - id_df: Identification results from identify()
        - lib_df: Library data from lib_load()
        - features_df: Feature data from find_features()

        **Column Ordering:**

        Columns are ordered for readability: identification info first, then
        structure data (SMILES, InChI), then deltas and scores.

        **Score Interpretation:**

        Scores range from 0.0 (poor match) to 1.0 (perfect match). Typical
        thresholds:

        - >0.9: Excellent match
        - 0.7-0.9: Good match
        - 0.5-0.7: Fair match
        - <0.5: Poor match

        **Stars Rating:**

        Library confidence stars (typically 1-5):

        - 5: Verified standard
        - 4: High confidence
        - 3: Medium confidence
        - 2: Low confidence
        - 1: Very low confidence

        **Multiple Identifications:**

        Features may have multiple library matches (different scores). Use
        score threshold to filter. The id_top_* columns in features_df contain
        the best (highest score) match only.

    Raises:
        ValueError: If id_df is empty (call identify() first), if lib_df is empty
            (call lib_load() first), if features_df is empty, or if features
            parameter has invalid format.

    See Also:
        - :meth:`identify`: Perform identification to generate id_df
        - :meth:`lib_load`: Load library to generate lib_df
        - :meth:`id_update`: Update id_top_* columns in features_df
        - :meth:`id_reset`: Clear identification results
    """
    # Validate inputs
    if getattr(sample, "id_df", None) is None or sample.id_df.is_empty():
        raise DataValidationError(
            "Cannot convert identifications to DataFrame: no identification results found.\n\n"
            "Run identification first:\n"
            "  sample.identify(ppm_tolerance=10, rt_tolerance=30)",
        )

    if getattr(sample, "lib_df", None) is None or sample.lib_df.is_empty():
        raise LibraryError(
            "Cannot retrieve compound info: library not loaded.\n\n"
            "Load a library first:\n"
            "  sample.lib_load(lib_source='libs/hilic.json')",
        )

    if getattr(sample, "features_df", None) is None or sample.features_df.is_empty():
        raise DataValidationError(
            "Cannot process identifications: no features detected in sample.\n\n"
            "Detect features first:\n"
            "  sample.detect_features()",
        )

    # Start with identification results
    result_df = sample.id_df.clone()

    # Filter by features if provided
    if features is not None:
        if hasattr(features, "columns"):  # DataFrame-like
            if "feature_id" in features.columns:
                uids = features["feature_id"].unique().to_list()
            else:
                available_cols = ", ".join(features.columns)
                raise DataValidationError(
                    f"features DataFrame missing required 'feature_id' column.\n"
                    f"Available columns: {available_cols}\n\n"
                    "Ensure the DataFrame has a 'feature_id' column containing feature UIDs.",
                )
        elif hasattr(features, "__iter__") and not isinstance(
            features,
            str,
        ):  # List-like
            uids = list(features)
        else:
            raise DataValidationError(
                f"Invalid features parameter type: {type(features).__name__}\n\n"
                "features must be either:\n"
                "  1. A DataFrame with 'feature_id' column\n"
                "  2. A list of feature UIDs (integers)\n\n"
                f"Example: sample.id_to_df(features=[1, 2, 3])",
            )

        result_df = result_df.filter(pl.col("feature_id").is_in(uids))

        if result_df.is_empty():
            return pl.DataFrame()

    # Join with features_df to get feature m/z and RT
    features_cols = ["feature_id", "mz", "rt", "ms2_scans"]
    # Only select columns that exist in features_df
    available_features_cols = [
        col for col in features_cols if col in sample.features_df.columns
    ]

    result_df = result_df.join(
        sample.features_df.select(available_features_cols),
        on="feature_id",
        how="left",
        suffix="_feature",
    )

    # Join with lib_df to get library information
    lib_cols = [
        "lib_id",
        "name",
        "shortname",
        "class",
        "formula",
        "adduct",
        "smiles",
        "cmpd_id",
        "inchikey",
        "stars",
    ]
    # Add optional columns if they exist
    optional_lib_cols = ["inchi", "db_id", "db"]
    for col in optional_lib_cols:
        if col in sample.lib_df.columns:
            lib_cols.append(col)

    # Only select columns that exist in lib_df
    available_lib_cols = [col for col in lib_cols if col in sample.lib_df.columns]

    result_df = result_df.join(
        sample.lib_df.select(available_lib_cols),
        on="lib_id",
        how="left",
        suffix="_lib",
    )

    # Reorder columns for better readability
    column_order = [
        "feature_id",
        "cmpd_id" if "cmpd_id" in result_df.columns else None,
        "lib_id",
        "name" if "name" in result_df.columns else None,
        "shortname" if "shortname" in result_df.columns else None,
        "class" if "class" in result_df.columns else None,
        "formula" if "formula" in result_df.columns else None,
        "adduct" if "adduct" in result_df.columns else None,
        "mz" if "mz" in result_df.columns else None,
        "mz_delta",
        "rt" if "rt" in result_df.columns else None,
        "rt_delta",
        "ms2_scans" if "ms2_scans" in result_df.columns else None,
        "matcher" if "matcher" in result_df.columns else None,
        "score" if "score" in result_df.columns else None,
        "stars" if "stars" in result_df.columns else None,
        "id_source" if "id_source" in result_df.columns else None,
        "smiles" if "smiles" in result_df.columns else None,
        "inchikey" if "inchikey" in result_df.columns else None,
    ]

    # Add any remaining columns
    remaining_cols = [col for col in result_df.columns if col not in column_order]
    column_order.extend(remaining_cols)

    # Filter out None values and select existing columns
    final_column_order = [
        col for col in column_order if col is not None and col in result_df.columns
    ]

    result_df = result_df.select(final_column_order)

    return result_df


def id_reset(sample):
    """Reset identification data and remove from history.

    Removes:
    - sample.id_df (identification results DataFrame)
    - Resets id_top_* columns in features_df to null
    - 'identify' from sample.history

    Args:
        sample: Sample instance to reset
    """
    # Get logger from sample if available
    logger = getattr(sample, "logger", None)

    # Remove id_df
    if hasattr(sample, "id_df"):
        if logger:
            logger.debug("Removing id_df")
        delattr(sample, "id_df")

    # Reset id_top_* columns in features_df
    if (
        hasattr(sample, "features_df")
        and sample.features_df is not None
        and not sample.features_df.is_empty()
    ):
        if logger:
            logger.debug("Resetting id_top_* columns in features_df")

        # Check which columns exist before trying to update them
        id_columns_to_reset = []
        for col in ["id_top_name", "id_top_class", "id_top_adduct", "id_top_score"]:
            if col in sample.features_df.columns:
                if col == "id_top_score":
                    id_columns_to_reset.append(
                        pl.lit(None, dtype=pl.Float64).alias(col),
                    )
                else:
                    id_columns_to_reset.append(pl.lit(None, dtype=pl.String).alias(col))

        if id_columns_to_reset:
            sample.features_df = sample.features_df.with_columns(id_columns_to_reset)

    # Remove identify from history
    if hasattr(sample, "history") and "identify" in sample.history:
        if logger:
            logger.debug("Removing 'identify' from history")
        del sample.history["identify"]

    if logger:
        logger.info("Deleted identification data")


def id_update(sample):
    """Update id_* columns in features_df based on current id_df and lib_df.

    This method refreshes the identification columns (id_top_name, id_top_class,
    id_top_adduct, id_top_score, id_source) in features_df to reflect the current
    state of id_df and lib_df. This is useful after filtering or modifying library
    entries.

    Args:
        sample: Sample instance with id_df, lib_df, and features_df populated

    Raises:
        ValueError: If required dataframes are missing

    Example:
        >>> sample.import_tima("tima_results")
        >>> sample.lib_filter('chnops')
        >>> sample.id_update()  # Refresh id_* columns after filtering
    """
    # Get logger from sample if available
    logger = getattr(sample, "logger", None)

    # Validate inputs
    if not hasattr(sample, "id_df") or sample.id_df is None or sample.id_df.is_empty():
        if logger:
            logger.warning("id_df is empty. Nothing to update.")
        return

    if (
        not hasattr(sample, "lib_df")
        or sample.lib_df is None
        or sample.lib_df.is_empty()
    ):
        if logger:
            logger.warning("lib_df is empty. Nothing to update.")
        return

    if (
        not hasattr(sample, "features_df")
        or sample.features_df is None
        or sample.features_df.is_empty()
    ):
        raise DataValidationError(
            "Cannot update identifications: features DataFrame is empty.\n\n"
            "Detect features first:\n"
            "  sample.detect_features()",
        )

    if logger:
        logger.info(
            "Updating id_* columns in features_df from current id_df and lib_df",
        )

    # Check which columns we need from lib_df
    lib_select_cols = ["lib_id", "name", "shortname", "class", "adduct"]
    if "db" in sample.lib_df.columns:
        lib_select_cols.append("db")

    # Only select columns that exist
    available_lib_cols = [
        col for col in lib_select_cols if col in sample.lib_df.columns
    ]

    # Join id_df with lib_df to get identification details (including shortname and db)
    id_with_lib = sample.id_df.join(
        sample.lib_df.select(available_lib_cols),
        on="lib_id",
        how="left",
    )

    # If id_source doesn't exist in id_df, create it from matcher + db
    if "id_source" not in id_with_lib.columns:
        if "matcher" in id_with_lib.columns and "db" in id_with_lib.columns:
            id_with_lib = id_with_lib.with_columns(
                pl.when(pl.col("db").is_not_null())
                .then(pl.concat_str([pl.col("matcher"), pl.lit("-"), pl.col("db")]))
                .otherwise(pl.col("matcher"))
                .alias("id_source"),
            )
        elif "matcher" in id_with_lib.columns:
            id_with_lib = id_with_lib.with_columns(pl.col("matcher").alias("id_source"))
        else:
            id_with_lib = id_with_lib.with_columns(
                pl.lit(None, dtype=pl.String).alias("id_source"),
            )

    # Group by feature_id and select best identification (highest score)
    best_ids = (
        id_with_lib.group_by("feature_id")
        .agg([pl.col("score").max().alias("max_score")])
        .join(id_with_lib, on="feature_id")
        .filter(pl.col("score") == pl.col("max_score"))
        .group_by("feature_id")
        .first()  # In case of ties, take the first
    )

    if logger:
        logger.debug(f"Selected best identifications for {len(best_ids)} features")

    # Prepare the identification columns (use shortname if available, otherwise name)
    # Handle empty strings: coalesce treats "" as valid, so we need to check for both null and empty
    id_columns = {
        "id_top_name": best_ids.select(
            "feature_id",
            pl.when((pl.col("shortname").is_not_null()) & (pl.col("shortname") != ""))
            .then(pl.col("shortname"))
            .otherwise(pl.col("name"))
            .alias("name"),
        ),
        "id_top_adduct": best_ids.select("feature_id", "adduct"),
        "id_top_score": best_ids.select(
            "feature_id",
            pl.col("score").round(3).alias("score"),
        ),
        "id_source": best_ids.select("feature_id", "id_source"),
    }

    # Only add id_top_class if class column exists and has non-null values
    if "class" in best_ids.columns:
        id_columns["id_top_class"] = best_ids.select("feature_id", "class")

    # Initialize all expected identification columns in features_df if they don't exist
    expected_id_columns = [
        "id_top_name",
        "id_top_adduct",
        "id_top_class",
        "id_top_score",
        "id_source",
    ]
    for col_name in expected_id_columns:
        if col_name not in sample.features_df.columns:
            if col_name == "id_top_score":
                sample.features_df = sample.features_df.with_columns(
                    pl.lit(None, dtype=pl.Float64).alias(col_name),
                )
            else:
                sample.features_df = sample.features_df.with_columns(
                    pl.lit(None, dtype=pl.String).alias(col_name),
                )

    # Reset all id_* columns to None first
    id_columns_to_reset = []
    for col in expected_id_columns:
        if col in sample.features_df.columns:
            if col == "id_top_score":
                id_columns_to_reset.append(pl.lit(None, dtype=pl.Float64).alias(col))
            else:
                id_columns_to_reset.append(pl.lit(None, dtype=pl.String).alias(col))

    if id_columns_to_reset:
        sample.features_df = sample.features_df.with_columns(id_columns_to_reset)

    # Update features_df with identification data
    for col_name, id_data_col in id_columns.items():
        source_column = id_data_col.columns[1]  # second column (after feature_id)

        # Create update dataframe
        update_data = id_data_col.rename({source_column: col_name})

        # Join and update
        sample.features_df = (
            sample.features_df.join(
                update_data,
                on="feature_id",
                how="left",
                suffix="_update",
            )
            .with_columns(pl.coalesce([f"{col_name}_update", col_name]).alias(col_name))
            .drop(f"{col_name}_update")
        )

    # Replace NaN and problematic values with None in identification columns
    for col_name in expected_id_columns:
        if col_name in sample.features_df.columns:
            # For string columns, replace empty strings and "nan" with None
            if col_name not in ["id_top_score"]:
                # For id_top_class, also replace "notClassified" with None
                if col_name == "id_top_class":
                    sample.features_df = sample.features_df.with_columns(
                        pl.when(
                            pl.col(col_name).is_null()
                            | (pl.col(col_name) == "")
                            | (pl.col(col_name) == "nan")
                            | (pl.col(col_name) == "NaN")
                            | (pl.col(col_name) == "notClassified"),
                        )
                        .then(None)
                        .otherwise(pl.col(col_name))
                        .alias(col_name),
                    )
                else:
                    sample.features_df = sample.features_df.with_columns(
                        pl.when(
                            pl.col(col_name).is_null()
                            | (pl.col(col_name) == "")
                            | (pl.col(col_name) == "nan")
                            | (pl.col(col_name) == "NaN"),
                        )
                        .then(None)
                        .otherwise(pl.col(col_name))
                        .alias(col_name),
                    )
            # For numeric columns, replace NaN with None
            else:
                sample.features_df = sample.features_df.with_columns(
                    pl.when(pl.col(col_name).is_null() | pl.col(col_name).is_nan())
                    .then(None)
                    .otherwise(pl.col(col_name))
                    .alias(col_name),
                )

    # Count how many features were updated
    updated_count = sample.features_df.filter(
        pl.col("id_top_name").is_not_null(),
    ).height

    if logger:
        logger.success(
            f"Updated id_* columns in features_df. {updated_count} features have identifications.",
        )


def lib_reset(sample):
    """Reset library and identification data and remove from history.

    Removes:
    - sample.id_df (identification results DataFrame)
    - sample.lib_df (library DataFrame)
    - sample._lib (library object reference)
    - Resets id_top_* columns in features_df to null
    - 'identify' from sample.history
    - 'lib_load' from sample.history (if exists)

    Args:
        sample: Sample instance to reset
    """
    # Get logger from sample if available
    logger = getattr(sample, "logger", None)

    # Remove id_df
    if hasattr(sample, "id_df"):
        if logger:
            logger.debug("Removing id_df")
        delattr(sample, "id_df")

    # Remove lib_df
    if hasattr(sample, "lib_df"):
        if logger:
            logger.debug("Removing lib_df")
        delattr(sample, "lib_df")

    # Remove lib object reference
    if hasattr(sample, "_lib"):
        if logger:
            logger.debug("Removing _lib reference")
        delattr(sample, "_lib")

    # Reset id_top_* columns in features_df
    if (
        hasattr(sample, "features_df")
        and sample.features_df is not None
        and not sample.features_df.is_empty()
    ):
        if logger:
            logger.debug("Resetting id_top_* columns in features_df")

        # Check which columns exist before trying to update them
        id_columns_to_reset = []
        for col in ["id_top_name", "id_top_class", "id_top_adduct", "id_top_score"]:
            if col in sample.features_df.columns:
                if col == "id_top_score":
                    id_columns_to_reset.append(
                        pl.lit(None, dtype=pl.Float64).alias(col),
                    )
                else:
                    id_columns_to_reset.append(pl.lit(None, dtype=pl.String).alias(col))

        if id_columns_to_reset:
            sample.features_df = sample.features_df.with_columns(id_columns_to_reset)

    # Remove from history
    if hasattr(sample, "history"):
        if "identify" in sample.history:
            if logger:
                logger.debug("Removing 'identify' from history")
            del sample.history["identify"]

        if "lib_load" in sample.history:
            if logger:
                logger.debug("Removing 'lib_load' from history")
            del sample.history["lib_load"]

    if logger:
        logger.info("Library and identification data deleted")


def lib_compare(
    sample,
    file=None,
    action: str = "intersect",
    on: str = "inchikey14",
    keep_none: bool = False,
):
    """
    Compare sample's library with another library and perform actions based on matching compounds.

    This is a convenience wrapper around the Lib.compare() method that operates on the sample's lib_df.

    Args:
        sample: Sample instance with lib_df populated
        file: Path to reference library file (CSV or JSON). If None, no comparison is performed.
        action: Action to perform based on comparison results:
            - 'reset_stars' or 'reset_star': Set stars=0 for rows NOT in reference library
            - 'add_stars' or 'add_star': Increment stars by 1 for rows in reference library
            - 'delete': Remove rows that ARE in reference library
            - 'filter' or 'delete_others': Remove rows that are NOT in reference library
            - 'intersect': Return DataFrame of lib_df rows that ARE in reference library
            - 'difference': Return DataFrame of lib_df rows that are NOT in reference library
            - 'missing': Return DataFrame of reference library rows not matched in lib_df
        on: Field to compare on. Valid values: 'formula', 'inchikey', 'inchikey14', 'name'
        keep_none: If True, treat None/null values as valid matches (keep them regardless)

    Returns:
        None for modification actions (modifies sample.lib_df in place)
        pl.DataFrame for query actions ('intersect', 'difference', 'missing')

    Raises:
        ValueError: If sample.lib_df is not loaded or if invalid 'on' or 'action' value provided
        FileNotFoundError: If file doesn't exist

    Example:
        >>> sample.lib_load("my_compounds.csv")
        >>> # Get compounds that exist in both libraries
        >>> common = sample.lib_compare(file="reference.csv", action="intersect")
        >>> # Reset stars for compounds not in reference
        >>> sample.lib_compare(file="reference.csv", action="reset_stars")
    """
    # Check if lib_df exists
    if (
        not hasattr(sample, "lib_df")
        or sample.lib_df is None
        or sample.lib_df.is_empty()
    ):
        raise ValueError("sample.lib_df is empty. Call lib_load() first.")

    # Resolve library path if file is provided
    if file is not None:
        file = _resolve_library_path(file)

    # Check if _lib object exists and is not None (created by lib_load)
    if not hasattr(sample, "_lib") or sample._lib is None:
        # If not, create a temporary Lib object with the current lib_df
        try:
            from masster.lib.lib import Lib
        except ImportError:
            raise ImportError("Cannot import Lib class")

        temp_lib = Lib()
        temp_lib.lib_df = sample.lib_df
        result = temp_lib.compare(file=file, action=action, on=on, keep_none=keep_none)

        # Update sample.lib_df if it was modified in place
        if result is None:
            sample.lib_df = temp_lib.lib_df

            # For modification actions that filter lib_df, also filter id_df
            if action in ["filter", "delete_others", "delete"]:
                if (
                    hasattr(sample, "id_df")
                    and sample.id_df is not None
                    and not sample.id_df.is_empty()
                ):
                    # Get the remaining lib_ids
                    remaining_lib_ids = (
                        sample.lib_df.select("lib_id").to_series().to_list()
                    )
                    # Filter id_df to keep only rows with lib_ids that still exist in lib_df
                    sample.id_df = sample.id_df.filter(
                        pl.col("lib_id").is_in(remaining_lib_ids),
                    )
                    sample.logger.info(
                        f"Filtered id_df to {len(sample.id_df)} identifications matching remaining library entries",
                    )

        return result
    # Use the existing lib object
    result = sample._lib.compare(file=file, action=action, on=on, keep_none=keep_none)

    # Update sample.lib_df reference in case it was modified
    if result is None:
        sample.lib_df = sample._lib.lib_df

        # For modification actions that filter lib_df, also filter id_df
        if action in ["filter", "delete_others", "delete"]:
            if (
                hasattr(sample, "id_df")
                and sample.id_df is not None
                and not sample.id_df.is_empty()
            ):
                # Get the remaining lib_ids
                remaining_lib_ids = sample.lib_df.select("lib_id").to_series().to_list()
                # Filter id_df to keep only rows with lib_ids that still exist in lib_df
                sample.id_df = sample.id_df.filter(
                    pl.col("lib_id").is_in(remaining_lib_ids),
                )
                sample.logger.info(
                    f"Filtered id_df to {len(sample.id_df)} identifications matching remaining library entries",
                )

    return result


def lib_select(
    sample,
    uid=None,
    cmpd_id=None,
    lib_source=None,
    name=None,
    shortname=None,
    class_=None,
    formula=None,
    inchikey=None,
    inchikey14=None,
    adduct=None,
    iso=None,
    mz=None,
    rt=None,
    probability=None,
    stars=None,
    z=None,
    quant_group=None,
    db=None,
) -> pl.DataFrame:
    """
    Select library entries based on specified criteria and return the filtered DataFrame.

    This is a convenience wrapper around Lib.lib_select() that operates on the sample's lib_df.

    Args:
        sample: Sample instance with lib_df populated
        uid: lib_id filter (list of UIDs, tuple for range, or None for all)
        cmpd_id: compound UID filter (list, tuple for range, or single value)
        lib_source: library source filter (str for exact match, list for multiple sources)
        name: compound name filter using regex (str for pattern, list for multiple patterns with OR)
        shortname: short name filter using regex (str for pattern, list for multiple patterns)
        class_: compound class filter using regex (str for pattern, list for multiple patterns)
        formula: molecular formula filter (str for exact match, list for multiple formulas)
        inchikey: InChIKey filter (str for exact match, list for multiple keys)
        inchikey14: InChIKey first 14 chars filter (str for exact match, list for multiple)
        adduct: adduct filter (str for exact match, list for multiple adducts)
        iso: isotope number filter (tuple for range, single value for exact match)
        mz: m/z range filter (tuple for range, single value for minimum)
        rt: retention time range filter (tuple for range, single value for minimum)
        probability: adduct probability filter (tuple for range, single value for minimum)
        stars: stars rating filter (tuple for range, single value for exact match)
        z: charge filter (int for exact match, list for multiple charges)
        quant_group: quantification group filter (int for exact match, list for multiple groups)
        db: database filter (str for exact match, list for multiple databases)

    Returns:
        pl.DataFrame: Filtered library DataFrame

    Raises:
        ValueError: If sample.lib_df is not loaded

    Examples:
        >>> sample.lib_load("compounds.csv")
        >>> # Select by m/z range
        >>> selected = sample.lib_select(mz=(100, 500))
        >>> # Select by adduct and stars
        >>> selected = sample.lib_select(adduct="[M+H]+", stars=(3, 5))
    """
    # Check if lib_df exists
    if (
        not hasattr(sample, "lib_df")
        or sample.lib_df is None
        or sample.lib_df.is_empty()
    ):
        raise ValueError("sample.lib_df is empty. Call lib_load() first.")

    # Always use sample.lib_df (the official version) not _lib
    # Create a temporary Lib object with the current lib_df
    try:
        from masster.lib.lib import Lib
    except ImportError:
        raise ImportError("Cannot import Lib class")

    temp_lib = Lib()
    temp_lib.lib_df = sample.lib_df
    return temp_lib.lib_select(
        uid=uid,
        cmpd_id=cmpd_id,
        lib_source=lib_source,
        name=name,
        shortname=shortname,
        class_=class_,
        formula=formula,
        inchikey=inchikey,
        inchikey14=inchikey14,
        adduct=adduct,
        iso=iso,
        mz=mz,
        rt=rt,
        probability=probability,
        stars=stars,
        z=z,
        quant_group=quant_group,
        db=db,
    )


def lib_filter(sample, entries):
    """
    Keep only the specified library entries and delete all others (modifies sample.lib_df in place).

    This method filters lib_df to keep only specified entries, removing all others.
    Similar to features_filter() but for library entries.

    Args:
        sample: Sample instance with lib_df populated
        entries: Can be one of the following:
            - list: List of lib_id values to keep
            - pl.DataFrame or pd.DataFrame: DataFrame with 'lib_id' column - extracts unique values to keep
            - str: Special action:
                * 'delete_identified': Delete all library entries that appear in id_df
                * 'delete_orphans': Delete all library entries that do NOT appear in id_df
                * 'delete_ms1': Delete all library entries that don't have MS2 identifications (based on matcher or id_source)
                * 'chnops': Delete all library entries whose formula contains elements beyond C, H, N, O, P, S

    Returns:
        None (modifies sample.lib_df in place)

    Raises:
        ValueError: If sample.lib_df is not loaded or if required data is missing

    Examples:
        >>> sample.lib_load("compounds.csv")
        >>> # Keep only specific UIDs
        >>> sample.lib_filter([0, 1, 2, 10, 15])
        >>> # Keep only high-quality entries
        >>> selected = sample.lib_select(stars=(4, 5))
        >>> sample.lib_filter(selected)
        >>> # Delete identified compounds
        >>> sample.lib_filter('delete_identified')
        >>> # Keep only identified compounds (delete orphans)
        >>> sample.lib_filter('delete_orphans')
        >>> # Keep only MS2-identified compounds
        >>> sample.lib_filter('delete_ms1')
        >>> # Keep only CHNOPS compounds
        >>> sample.lib_filter('chnops')
    """
    # Get logger from sample if available
    logger = getattr(sample, "logger", None)

    # Check if lib_df exists
    if (
        not hasattr(sample, "lib_df")
        or sample.lib_df is None
        or sample.lib_df.is_empty()
    ):
        if logger:
            logger.warning("sample.lib_df is empty. Call lib_load() first.")
        else:
            raise LibraryError(
                "Cannot filter library: no library loaded in sample.\n\n"
                "Load a library first:\n"
                "  sample.lib_load(lib_source='libs/hilic.json')",
            )
        return

    if entries is None:
        if logger:
            logger.warning("No entries specified to keep.")
        return

    original_count = len(sample.lib_df)

    # Handle string actions
    if isinstance(entries, str):
        if entries == "delete_identified":
            # Delete all library entries that appear in id_df
            if (
                not hasattr(sample, "id_df")
                or sample.id_df is None
                or sample.id_df.is_empty()
            ):
                if logger:
                    logger.warning("id_df is empty. No identified compounds to delete.")
                return

            # Get lib_ids that are identified
            identified_lib_ids = (
                sample.id_df.select("lib_id").unique().to_series().to_list()
            )

            # Keep only lib_ids that are NOT identified
            sample.lib_df = sample.lib_df.filter(
                ~pl.col("lib_id").is_in(identified_lib_ids),
            )

            if logger:
                deleted_count = original_count - len(sample.lib_df)
                logger.info(
                    f"Deleted {deleted_count} identified library entries. Remaining: {len(sample.lib_df)}",
                )

            # Store filtering in history
            if hasattr(sample, "update_history"):
                sample.update_history(
                    ["lib_filter"],
                    {
                        "action": "delete_identified",
                        "initial_count": original_count,
                        "remaining_count": len(sample.lib_df),
                        "deleted_count": original_count - len(sample.lib_df),
                    },
                )

        elif entries == "delete_orphans":
            # Delete all library entries that do NOT appear in id_df (keep only identified)
            if (
                not hasattr(sample, "id_df")
                or sample.id_df is None
                or sample.id_df.is_empty()
            ):
                if logger:
                    logger.warning(
                        "id_df is empty. All library entries would be deleted. Operation cancelled.",
                    )
                return

            # Get lib_ids that are identified
            identified_lib_ids = (
                sample.id_df.select("lib_id").unique().to_series().to_list()
            )

            # Keep only lib_ids that ARE identified
            sample.lib_df = sample.lib_df.filter(
                pl.col("lib_id").is_in(identified_lib_ids),
            )

            if logger:
                deleted_count = original_count - len(sample.lib_df)
                logger.info(
                    f"Deleted {deleted_count} orphan library entries. Remaining: {len(sample.lib_df)}",
                )

            # Store filtering in history
            if hasattr(sample, "update_history"):
                sample.update_history(
                    ["lib_filter"],
                    {
                        "action": "delete_orphans",
                        "initial_count": original_count,
                        "remaining_count": len(sample.lib_df),
                        "deleted_count": original_count - len(sample.lib_df),
                    },
                )

        elif entries == "delete_ms1":
            # Delete all library entries that don't have ms2 in matcher or id_source
            # This requires checking id_df for MS2 identifications
            if (
                not hasattr(sample, "id_df")
                or sample.id_df is None
                or sample.id_df.is_empty()
            ):
                if logger:
                    logger.warning(
                        "id_df is empty. Cannot filter by MS2 identifications.",
                    )
                return

            # Get lib_ids that have MS2 identifications
            # Check both 'matcher' column (if exists) and 'id_source' column (if exists)
            ms2_conditions = []
            if "matcher" in sample.id_df.columns:
                ms2_conditions.append(
                    pl.col("matcher").str.contains("ms2", literal=False),
                )
            if "id_source" in sample.id_df.columns:
                ms2_conditions.append(
                    pl.col("id_source").str.contains("ms2", literal=False),
                )

            if not ms2_conditions:
                if logger:
                    logger.warning(
                        "Neither 'matcher' nor 'id_source' columns found in id_df. Cannot filter by MS2.",
                    )
                return

            # Combine conditions with OR
            ms2_filter = ms2_conditions[0]
            for condition in ms2_conditions[1:]:
                ms2_filter = ms2_filter | condition

            ms2_lib_ids = (
                sample.id_df.filter(ms2_filter)
                .select("lib_id")
                .unique()
                .to_series()
                .to_list()
            )

            # Keep only lib_ids that have MS2 identifications
            sample.lib_df = sample.lib_df.filter(pl.col("lib_id").is_in(ms2_lib_ids))

            if logger:
                deleted_count = original_count - len(sample.lib_df)
                logger.info(
                    f"Deleted {deleted_count} MS1-only library entries. Remaining: {len(sample.lib_df)}",
                )

            # Store filtering in history
            if hasattr(sample, "update_history"):
                sample.update_history(
                    ["lib_filter"],
                    {
                        "action": "delete_ms1",
                        "initial_count": original_count,
                        "remaining_count": len(sample.lib_df),
                        "deleted_count": original_count - len(sample.lib_df),
                    },
                )

        elif entries == "chnops":
            # Delete all library entries whose formula contains elements beyond C, H, N, O, P, S
            if "formula" not in sample.lib_df.columns:
                if logger:
                    logger.warning(
                        "'formula' column not found in lib_df. Cannot filter by elements.",
                    )
                return

            # Create regex pattern to match formulas containing only C, H, N, O, P, S, +, -
            # Pattern explanation: ^[CHNOPS0-9+\-]+$ means only these letters, numbers, and charge symbols
            chnops_pattern = r"^[CHNOPS0-9+\-]+$"

            # Keep only entries whose formula matches CHNOPS pattern (and handle null formulas)
            sample.lib_df = sample.lib_df.filter(
                pl.col("formula").is_null()
                | pl.col("formula").str.contains(chnops_pattern),
            )

            # Also filter id_df to remove identifications of non-CHNOPS compounds
            if (
                hasattr(sample, "id_df")
                and sample.id_df is not None
                and not sample.id_df.is_empty()
            ):
                # Get remaining lib_ids after filtering
                remaining_lib_ids = (
                    sample.lib_df.select("lib_id").unique().to_series().to_list()
                )
                sample.id_df = sample.id_df.filter(
                    pl.col("lib_id").is_in(remaining_lib_ids),
                )
                if logger:
                    logger.debug(
                        "Also filtered id_df to match remaining CHNOPS library entries",
                    )

            if logger:
                deleted_count = original_count - len(sample.lib_df)
                logger.info(
                    f"Deleted {deleted_count} non-CHNOPS library entries. Remaining: {len(sample.lib_df)}",
                )

            # Store filtering in history
            if hasattr(sample, "update_history"):
                sample.update_history(
                    ["lib_filter"],
                    {
                        "action": "chnops",
                        "initial_count": original_count,
                        "remaining_count": len(sample.lib_df),
                        "deleted_count": original_count - len(sample.lib_df),
                    },
                )

        else:
            raise ConfigurationError(
                f"Invalid action '{entries}'.\n\n"
                "Valid actions:\n"
                "  - 'delete_identified': Remove compounds with identifications\n"
                "  - 'delete_orphans': Remove compounds not found in features\n"
                "  - 'delete_ms1': Remove compounds without MS2 spectra\n"
                "  - 'chnops': Keep only CHNOPS compounds",
            )

        # Update sample._lib if it exists
        if hasattr(sample, "_lib") and sample._lib is not None:
            sample._lib.lib_df = sample.lib_df

        return

    # Handle DataFrame input
    if hasattr(entries, "columns"):
        # Check if it's a polars or pandas DataFrame
        if "lib_id" in entries.columns:
            # Extract unique lib_id values
            if hasattr(entries, "select"):  # Polars
                lib_ids_to_keep = (
                    entries.select("lib_id").unique().to_series().to_list()
                )
            else:  # Pandas
                lib_ids_to_keep = entries["lib_id"].unique().tolist()
        else:
            available_cols = (
                ", ".join(entries.columns) if hasattr(entries, "columns") else "unknown"
            )
            raise DataValidationError(
                f"DataFrame missing required 'lib_id' column.\n"
                f"Available columns: {available_cols}\n\n"
                "Provide a DataFrame with 'lib_id' column.",
            )

    # Handle list input
    elif isinstance(entries, (list, tuple)):
        lib_ids_to_keep = list(entries)

    else:
        raise ConfigurationError(
            f"Invalid entries parameter type: {type(entries).__name__}\n\n"
            "entries must be one of:\n"
            "  1. A list of lib_id values: [1, 2, 3]\n"
            "  2. A DataFrame with 'lib_id' column\n"
            "  3. An action string: 'delete_identified', 'delete_orphans', 'delete_ms1', 'chnops'",
        )

    if not lib_ids_to_keep:
        if logger:
            logger.warning("No valid lib_id values provided to keep.")
        return

    # Filter lib_df to keep only specified entries
    sample.lib_df = sample.lib_df.filter(pl.col("lib_id").is_in(lib_ids_to_keep))

    # Also filter id_df to remove identifications of deleted library entries
    if (
        hasattr(sample, "id_df")
        and sample.id_df is not None
        and not sample.id_df.is_empty()
    ):
        sample.id_df = sample.id_df.filter(pl.col("lib_id").is_in(lib_ids_to_keep))
        if logger:
            logger.debug("Also filtered id_df to match remaining library entries")

    # Update sample._lib if it exists
    if hasattr(sample, "_lib") and sample._lib is not None:
        sample._lib.lib_df = sample.lib_df

    kept_count = len(sample.lib_df)
    deleted_count = original_count - kept_count

    if logger:
        logger.info(
            f"Deleted {deleted_count} library entries. Remaining: {kept_count}",
        )

    # Store filtering in history
    if hasattr(sample, "update_history"):
        sample.update_history(
            ["lib_filter"],
            {
                "action": "keep_selected",
                "initial_count": original_count,
                "remaining_count": kept_count,
                "deleted_count": deleted_count,
            },
        )


# Helper functions (private)


def _setup_identify_parameters(params, kwargs):
    """Setup identification parameters with fallbacks and overrides."""
    # Import defaults class
    try:
        from masster.sample.defaults.identify_def import identify_defaults
    except ImportError:
        identify_defaults = None

    # Use provided params or create defaults
    if params is None:
        if identify_defaults is not None:
            params = identify_defaults()
        else:
            # Fallback if imports fail
            class FallbackParams:
                mz_tol = 0.01
                rt_tol = 2.0
                heteroatom_penalty = 0.7
                multiple_formulas_penalty = 0.8
                multiple_compounds_penalty = 0.8
                heteroatoms = ["Cl", "Br", "F", "I"]

            params = FallbackParams()

    # Override parameters with any provided kwargs
    if kwargs:
        # Handle parameter name mapping for backwards compatibility
        param_mapping = {"rt_tolerance": "rt_tol", "mz_tolerance": "mz_tol"}

        for param_name, value in kwargs.items():
            # Check if we need to map the parameter name
            mapped_name = param_mapping.get(param_name, param_name)

            if hasattr(params, mapped_name):
                setattr(params, mapped_name, value)
            elif hasattr(params, param_name):
                setattr(params, param_name, value)

    return params


def _smart_reset_id_results(sample, target_uids, logger):
    """Smart reset of identification results - only clear what's being re-identified."""
    if target_uids is not None:
        # Selective reset: only clear results for features being re-identified
        if (
            hasattr(sample, "id_df")
            and sample.id_df is not None
            and not sample.id_df.is_empty()
        ):
            sample.id_df = sample.id_df.filter(~pl.col("feature_id").is_in(target_uids))
            if logger:
                logger.debug(
                    f"Cleared previous results for {len(target_uids)} specific features",
                )
        elif not hasattr(sample, "id_df"):
            sample.id_df = pl.DataFrame()
    else:
        # Full reset: clear all results
        sample.id_df = pl.DataFrame()
        if logger:
            logger.debug("Cleared all previous identification results")


def _get_cached_adduct_probabilities(sample, logger):
    """Get adduct probabilities with caching to avoid repeated expensive computation."""
    # Check if we have cached results and cache key matches current parameters
    current_cache_key = _get_adduct_cache_key(sample)

    if (
        hasattr(sample, "_cached_adduct_probs")
        and hasattr(sample, "_cached_adduct_key")
        and sample._cached_adduct_key == current_cache_key
    ):
        if logger:
            logger.debug("Using cached adduct probabilities")
        return sample._cached_adduct_probs

    # Compute and cache
    if logger:
        logger.debug("Computing adduct probabilities...")
    adduct_prob_map = _get_adduct_probabilities(sample)
    sample._cached_adduct_probs = adduct_prob_map
    sample._cached_adduct_key = current_cache_key

    if logger:
        logger.debug(
            f"Computed and cached probabilities for {len(adduct_prob_map)} adducts",
        )
    return adduct_prob_map


def _get_adduct_cache_key(sample):
    """Generate a cache key based on adduct-related parameters."""
    if hasattr(sample, "parameters") and hasattr(sample.parameters, "adducts"):
        adducts_str = (
            "|".join(sorted(sample.parameters.adducts))
            if sample.parameters.adducts
            else ""
        )
        min_prob = getattr(sample.parameters, "adduct_min_probability", 0.04)
        return f"adducts:{adducts_str}:min_prob:{min_prob}"
    return "default"


def clear_identification_cache(sample):
    """Clear cached identification data (useful when parameters change)."""
    cache_attrs = ["_cached_adduct_probs", "_cached_adduct_key"]
    for attr in cache_attrs:
        if hasattr(sample, attr):
            delattr(sample, attr)


def _perform_identification_matching(
    features_to_process,
    sample,
    effective_mz_tol,
    effective_rt_tol,
    adduct_prob_map,
    only_masster,
    logger,
):
    """Perform optimized identification matching using vectorized operations where possible."""
    results = []

    # Get library data as arrays for faster access
    lib_df = sample.lib_df

    # Filter library by only_masster if requested
    if only_masster and "lib_source" in lib_df.columns:
        initial_lib_count = len(lib_df)
        lib_df = lib_df.filter(pl.col("lib_source").str.starts_with("masster"))
        if logger:
            logger.debug(
                f"Filtering library by only_masster: {initial_lib_count} entries -> {len(lib_df)} masster entries",
            )

    if logger:
        features_count = len(features_to_process)
        lib_count = len(lib_df)
        logger.debug(
            f"Identifying {features_count} features against {lib_count} library entries",
        )

    # Process each feature
    for feat_row in features_to_process.iter_rows(named=True):
        feat_uid = feat_row.get("feature_id")
        feat_mz = feat_row.get("mz")
        feat_rt = feat_row.get("rt")

        if feat_mz is None:
            if logger:
                logger.debug(f"Skipping feature {feat_uid} - no m/z value")
            results.append({"feature_id": feat_uid, "matches": []})
            continue

        # Find matches using vectorized filtering
        matches = _find_matches_vectorized(
            lib_df,
            feat_mz,
            feat_rt,
            effective_mz_tol,
            effective_rt_tol,
            logger,
            feat_uid,
        )

        # Convert matches to result format
        match_results = []
        if not matches.is_empty():
            for match_row in matches.iter_rows(named=True):
                mz_delta = (
                    abs(feat_mz - match_row.get("mz"))
                    if match_row.get("mz") is not None
                    else None
                )
                lib_rt = match_row.get("rt")
                rt_delta = (
                    abs(feat_rt - lib_rt)
                    if (feat_rt is not None and lib_rt is not None)
                    else None
                )

                # Get library probability as base score, then multiply by adduct probability
                lib_probability = (
                    match_row.get("probability", 1.0)
                    if match_row.get("probability") is not None
                    else 1.0
                )
                adduct = match_row.get("adduct")
                adduct_probability = adduct_prob_map.get(adduct, 1.0) if adduct else 1.0
                score = lib_probability * adduct_probability
                # Round to 3 decimal places (0 to 1.0)
                score = round(score, 3)

                # Get db column for creating id_source later
                db = match_row.get("db")

                match_results.append(
                    {
                        "lib_id": match_row.get("lib_id"),
                        "mz_delta": mz_delta,
                        "rt_delta": rt_delta,
                        "matcher": "masster-ms1",
                        "db": db,
                        "score": score,
                    },
                )

        results.append({"feature_id": feat_uid, "matches": match_results})

    return results


def _find_matches_vectorized(
    lib_df,
    feat_mz,
    feat_rt,
    mz_tol,
    rt_tol,
    logger,
    feat_uid,
):
    """Find library matches using optimized vectorized operations."""
    # Filter by m/z tolerance using vectorized operations
    matches = lib_df.filter(
        (pl.col("mz") >= feat_mz - mz_tol) & (pl.col("mz") <= feat_mz + mz_tol),
    )

    initial_match_count = len(matches)

    # Apply RT filter if available
    if rt_tol is not None and feat_rt is not None and not matches.is_empty():
        # First, check if any m/z matches have RT data
        rt_candidates = matches.filter(pl.col("rt").is_not_null())

        if not rt_candidates.is_empty():
            # Apply RT filtering to candidates with RT data
            rt_matches = rt_candidates.filter(
                (pl.col("rt") >= feat_rt - rt_tol) & (pl.col("rt") <= feat_rt + rt_tol),
            )

            if not rt_matches.is_empty():
                matches = rt_matches
                if logger:
                    logger.debug(
                        f"Feature {feat_uid}: {initial_match_count} m/z matches, {len(rt_candidates)} with RT, {len(matches)} after RT filter",
                    )
            else:
                # NO FALLBACK - if RT filtering finds no matches, return empty
                matches = rt_matches  # This is empty
                if logger:
                    logger.debug(
                        f"Feature {feat_uid}: RT filtering eliminated all {len(rt_candidates)} candidates (rt_tol={rt_tol}s) - no matches returned",
                    )
        # No RT data in library matches - fall back to m/z-only matching
        elif logger:
            logger.debug(
                f"Feature {feat_uid}: {initial_match_count} m/z matches but none have library RT data - using m/z-only matching",
            )
            # Keep the m/z matches (don't return empty DataFrame)

    # Add stricter m/z validation - prioritize more accurate matches
    if not matches.is_empty():
        strict_mz_tol = mz_tol * 0.5  # Use 50% of tolerance as strict threshold
        strict_matches = matches.filter(
            (pl.col("mz") >= feat_mz - strict_mz_tol)
            & (pl.col("mz") <= feat_mz + strict_mz_tol),
        )

        if not strict_matches.is_empty():
            # Use strict matches if available
            matches = strict_matches
            if logger:
                logger.debug(
                    f"Feature {feat_uid}: Using {len(matches)} strict m/z matches (within {strict_mz_tol:.6f} Da)",
                )
        elif logger:
            logger.debug(
                f"Feature {feat_uid}: No strict matches, using {len(matches)} loose matches",
            )

    # Improved deduplication - prioritize by m/z accuracy
    if not matches.is_empty() and len(matches) > 1:
        if "formula" in matches.columns and "adduct" in matches.columns:
            pre_dedup_count = len(matches)

            # Calculate m/z error for sorting
            matches = matches.with_columns(
                [(pl.col("mz") - feat_mz).abs().alias("mz_error_abs")],
            )

            # Group by formula and adduct, but keep the most accurate m/z match
            matches = (
                matches.sort(
                    ["mz_error_abs", "lib_id"],
                )  # Sort by m/z accuracy first, then lib_id for consistency
                .group_by(["formula", "adduct"], maintain_order=True)
                .first()
                .drop("mz_error_abs")  # Remove the temporary column
            )

            post_dedup_count = len(matches)
            if logger and post_dedup_count < pre_dedup_count:
                logger.debug(
                    f"Feature {feat_uid}: deduplicated {pre_dedup_count} to {post_dedup_count} matches (m/z accuracy prioritized)",
                )

    return matches


def _update_identification_results(sample, results, logger):
    """Update sample.id_df with new identification results."""
    # Flatten results into records
    records = []
    for result in results:
        feature_id = result["feature_id"]
        for match in result["matches"]:
            records.append(
                {
                    "feature_id": feature_id,
                    "lib_id": match["lib_id"],
                    "mz_delta": match["mz_delta"],
                    "rt_delta": match["rt_delta"],
                    "matcher": match["matcher"],
                    "db": match.get("db"),
                    "score": match["score"],
                    "iso": 0,  # Default to zero
                },
            )

    # Convert to DataFrame and append to existing results
    new_results_df = pl.DataFrame(records) if records else pl.DataFrame()

    if not new_results_df.is_empty():
        # Create id_source from matcher + db
        # Format: "masster-ms1-hsapiens" (matcher + "-" + database_name)
        if "db" in new_results_df.columns and "matcher" in new_results_df.columns:
            new_results_df = new_results_df.with_columns(
                pl.when(pl.col("db").is_not_null())
                .then(pl.concat_str([pl.col("matcher"), pl.lit("-"), pl.col("db")]))
                .otherwise(pl.col("matcher"))
                .alias("id_source"),
            ).drop("db")
            if logger:
                logger.debug("Created 'id_source' column from matcher + db")
        else:
            # Add id_source column matching matcher if db not available
            if "matcher" in new_results_df.columns:
                new_results_df = new_results_df.with_columns(
                    pl.col("matcher").alias("id_source"),
                )
            else:
                new_results_df = new_results_df.with_columns(
                    pl.lit(None, dtype=pl.String).alias("id_source"),
                )
            if logger:
                logger.debug("No db available; id_source set to matcher value")

        if (
            hasattr(sample, "id_df")
            and sample.id_df is not None
            and not sample.id_df.is_empty()
        ):
            # Check if existing id_df has the iso column
            if "iso" not in sample.id_df.columns:
                # Add iso column to existing id_df with default value 0
                sample.id_df = sample.id_df.with_columns(pl.lit(0).alias("iso"))
                if logger:
                    logger.debug(
                        "Added 'iso' column to existing id_df for schema compatibility",
                    )

            # Check if existing id_df has the id_source column
            if "id_source" not in sample.id_df.columns:
                # Add id_source column to existing id_df with None
                sample.id_df = sample.id_df.with_columns(
                    pl.lit(None, dtype=pl.String).alias("id_source"),
                )
                if logger:
                    logger.debug(
                        "Added 'id_source' column to existing id_df for schema compatibility",
                    )

            # Check if existing id_df has the matcher column (legacy compatibility)
            if "matcher" not in sample.id_df.columns:
                # Add matcher column to existing id_df, copy from id_source if available
                if "id_source" in sample.id_df.columns:
                    sample.id_df = sample.id_df.with_columns(
                        pl.col("id_source").alias("matcher"),
                    )
                else:
                    sample.id_df = sample.id_df.with_columns(
                        pl.lit(None, dtype=pl.String).alias("matcher"),
                    )
                if logger:
                    logger.debug(
                        "Added 'matcher' column to existing id_df for schema compatibility",
                    )

            sample.id_df = pl.concat([sample.id_df, new_results_df])
        else:
            sample.id_df = new_results_df

        if logger:
            logger.debug(f"Added {len(records)} identification results to sample.id_df")
    elif not hasattr(sample, "id_df"):
        sample.id_df = pl.DataFrame()


def _finalize_identification_results(sample, params, target_uids, logger):
    """Apply final scoring adjustments and update features columns."""
    # Apply scoring adjustments based on compound and formula counts
    _apply_scoring_adjustments(sample, params)

    # Update features_df with top-scoring identification results (only for processed features)
    _update_features_id_columns(sample, target_uids, logger)


def _store_identification_history(
    sample,
    effective_mz_tol,
    effective_rt_tol,
    target_uids,
    params,
    kwargs,
):
    """Store identification operation in sample history."""
    if hasattr(sample, "store_history"):
        history_params = {"mz_tol": effective_mz_tol, "rt_tol": effective_rt_tol}
        if target_uids is not None:
            history_params["features"] = target_uids
        if params is not None and hasattr(params, "to_dict"):
            history_params["params"] = params.to_dict()
        if kwargs:
            history_params["kwargs"] = kwargs
        sample.update_history(["identify"], history_params)


def _validate_identify_inputs(sample, logger=None):
    """Validate inputs for identification process."""
    if getattr(sample, "features_df", None) is None or sample.features_df.is_empty():
        if logger:
            logger.warning("No features found for identification")
        return False

    if getattr(sample, "lib_df", None) is None or sample.lib_df.is_empty():
        if logger:
            logger.error("Library (sample.lib_df) is empty; call lib_load() first")
        raise LibraryError(
            "Cannot identify features: no library loaded.\n\n"
            "Load a library first:\n"
            "  sample.lib_load(lib_source='libs/hilic.json')",
        )

    return True


def _prepare_features(sample, features, only_orphans, logger=None):
    """Prepare features for identification."""
    target_uids = None
    if features is not None:
        if hasattr(features, "columns"):  # DataFrame-like
            if "feature_id" in features.columns:
                target_uids = features["feature_id"].unique().to_list()
            else:
                available_cols = ", ".join(features.columns)
                raise DataValidationError(
                    f"features DataFrame missing required 'feature_id' column.\n"
                    f"Available columns: {available_cols}\n\n"
                    "Ensure the DataFrame has a 'feature_id' column containing feature UIDs.",
                )
        elif hasattr(features, "__iter__") and not isinstance(
            features,
            str,
        ):  # List-like
            target_uids = list(features)
        else:
            raise DataValidationError(
                f"Invalid features parameter type: {type(features).__name__}\n\n"
                "features must be either:\n"
                "  1. A DataFrame with 'feature_id' column\n"
                "  2. A list of feature UIDs (integers)\n\n"
                f"Example: sample.identify(features=[1, 2, 3])",
            )

        if logger:
            logger.debug(f"Identifying {len(target_uids)} specified features")

    # Filter features if target_uids specified
    features_to_process = sample.features_df
    if target_uids is not None:
        features_to_process = sample.features_df.filter(
            pl.col("feature_id").is_in(target_uids),
        )
        if features_to_process.is_empty():
            if logger:
                logger.warning(
                    "No features found matching specified features",
                )
            return None, target_uids

    # Filter orphans if only_orphans is True
    if (
        only_orphans
        and hasattr(sample, "id_df")
        and sample.id_df is not None
        and not sample.id_df.is_empty()
    ):
        # Get features that already have identifications
        matched_feature_ids = (
            sample.id_df.select("feature_id").unique().to_series().to_list()
        )
        if matched_feature_ids:
            initial_count = len(features_to_process)
            features_to_process = features_to_process.filter(
                ~pl.col("feature_id").is_in(matched_feature_ids),
            )
            if logger:
                logger.debug(
                    f"Filtering orphans: {initial_count} features -> {len(features_to_process)} orphans (excluding {initial_count - len(features_to_process)} already matched)",
                )
            if features_to_process.is_empty():
                if logger:
                    logger.info(
                        "All features already have identifications - nothing to identify",
                    )
                return None, target_uids

            # CRITICAL FIX: Update target_uids to be the actual orphan UIDs being processed
            # This ensures _smart_reset_id_results only clears these specific features,
            # preserving existing identifications for non-orphan features
            target_uids = features_to_process.select("feature_id").to_series().to_list()
            if logger:
                logger.debug(
                    f"Set target_uids to {len(target_uids)} orphan features to preserve existing identifications",
                )

    return features_to_process, target_uids


def _get_adduct_probabilities(sample):
    """Get adduct probabilities from _get_adducts() results."""
    from masster.sample.adducts import _get_adducts

    adducts_df = _get_adducts(sample)
    adduct_prob_map = {}
    if not adducts_df.is_empty():
        for row in adducts_df.iter_rows(named=True):
            adduct_prob_map[row.get("name")] = row.get("probability", 1.0)
    return adduct_prob_map


def _apply_scoring_adjustments(sample, params):
    """Apply scoring adjustments based on compound and formula counts using optimized operations."""
    if (
        not sample.id_df.is_empty()
        and hasattr(sample, "lib_df")
        and not sample.lib_df.is_empty()
    ):
        # Get penalty parameters
        heteroatoms = getattr(params, "heteroatoms", ["Cl", "Br", "F", "I"])
        heteroatom_penalty = getattr(params, "heteroatom_penalty", 0.7)
        formulas_penalty = getattr(params, "multiple_formulas_penalty", 0.8)
        compounds_penalty = getattr(params, "multiple_compounds_penalty", 0.8)

        # Single join to get all needed library information
        lib_columns = ["lib_id", "cmpd_id", "formula"]
        id_with_lib = sample.id_df.join(
            sample.lib_df.select(lib_columns),
            on="lib_id",
            how="left",
        )

        # Calculate all statistics in one group_by operation
        stats = id_with_lib.group_by("feature_id").agg(
            [
                pl.col("cmpd_id").n_unique().alias("num_cmpds"),
                pl.col("formula")
                .filter(pl.col("formula").is_not_null())
                .n_unique()
                .alias("num_formulas"),
            ],
        )

        # Join stats back and apply all penalties in one with_columns operation
        heteroatom_conditions = [
            pl.col("formula").str.contains(atom) for atom in heteroatoms
        ]
        has_heteroatoms = (
            pl.fold(
                acc=pl.lit(False),
                function=lambda acc, x: acc | x,
                exprs=heteroatom_conditions,
            )
            if heteroatom_conditions
            else pl.lit(False)
        )

        sample.id_df = (
            id_with_lib.join(stats, on="feature_id", how="left")
            .with_columns(
                [
                    # Apply all penalties in sequence using case-when chains
                    pl.when(pl.col("formula").is_not_null() & has_heteroatoms)
                    .then(pl.col("score") * heteroatom_penalty)
                    .otherwise(pl.col("score"))
                    .alias("score_temp1"),
                ],
            )
            .with_columns(
                [
                    pl.when(pl.col("num_formulas") > 1)
                    .then(pl.col("score_temp1") * formulas_penalty)
                    .otherwise(pl.col("score_temp1"))
                    .alias("score_temp2"),
                ],
            )
            .with_columns(
                [
                    pl.when(pl.col("num_cmpds") > 1)
                    .then(pl.col("score_temp2") * compounds_penalty)
                    .otherwise(pl.col("score_temp2"))
                    .round(4)
                    .alias("score"),
                ],
            )
            .select(
                [
                    "feature_id",
                    "lib_id",
                    "mz_delta",
                    "rt_delta",
                    "matcher",
                    "score",
                ],
            )
        )


def _update_features_id_columns(sample, target_uids=None, logger=None):
    """
    Update features_df with top-scoring identification results using safe in-place updates.

    Args:
        sample: Sample instance
        target_uids: Optional list of feature_ids to update. If None, updates all features.
        logger: Optional logger instance
    """
    try:
        if (
            not hasattr(sample, "id_df")
            or sample.id_df is None
            or sample.id_df.is_empty()
        ):
            if logger:
                logger.debug("No identification results to process")
            return

        if (
            not hasattr(sample, "lib_df")
            or sample.lib_df is None
            or sample.lib_df.is_empty()
        ):
            if logger:
                logger.debug("No library data available")
            return

        if (
            not hasattr(sample, "features_df")
            or sample.features_df is None
            or sample.features_df.is_empty()
        ):
            if logger:
                logger.debug("No features data available")
            return

        # Get library columns we need
        lib_columns = ["lib_id", "name", "adduct"]
        if "class" in sample.lib_df.columns:
            lib_columns.append("class")
        if "db" in sample.lib_df.columns:
            lib_columns.append("db")

        # Filter id_df to only target_uids if specified
        id_df_to_process = sample.id_df
        if target_uids is not None:
            id_df_to_process = sample.id_df.filter(
                pl.col("feature_id").is_in(target_uids),
            )
            if id_df_to_process.is_empty():
                if logger:
                    logger.debug("No identifications found for target features")
                return

        # Check if id_source exists in id_df
        has_id_source = "id_source" in id_df_to_process.columns
        has_matcher = "matcher" in id_df_to_process.columns

        # Get top-scoring identification for each feature
        top_ids = (
            id_df_to_process.sort(["feature_id", "score"], descending=[False, True])
            .group_by("feature_id", maintain_order=True)
            .first()
            .join(sample.lib_df.select(lib_columns), on="lib_id", how="left")
        )

        # Construct id_source if it doesn't exist in id_df
        if not has_id_source:
            if has_matcher and "db" in lib_columns:
                # Create id_source from matcher + "-" + db
                top_ids = top_ids.with_columns(
                    pl.when(pl.col("db").is_not_null())
                    .then(pl.concat_str([pl.col("matcher"), pl.lit("-"), pl.col("db")]))
                    .otherwise(pl.col("matcher"))
                    .alias("id_source"),
                )
            elif has_matcher:
                # Fallback to just matcher
                top_ids = top_ids.with_columns(pl.col("matcher").alias("id_source"))
            else:
                # No matcher either, use null
                top_ids = top_ids.with_columns(
                    pl.lit(None, dtype=pl.String).alias("id_source"),
                )

        # Select final columns
        top_ids = top_ids.select(
            [
                "feature_id",
                "name",
                pl.col("class").alias("id_top_class")
                if "class" in lib_columns
                else pl.lit(None, dtype=pl.String).alias("id_top_class"),
                pl.col("adduct").alias("id_top_adduct"),
                pl.col("score").alias("id_top_score"),
                "id_source",
            ],
        ).rename({"name": "id_top_name"})

        # Ensure we have the id_top columns in features_df
        for col_name, dtype in [
            ("id_top_name", pl.String),
            ("id_top_class", pl.String),
            ("id_top_adduct", pl.String),
            ("id_top_score", pl.Float64),
            ("id_source", pl.String),
        ]:
            if col_name not in sample.features_df.columns:
                sample.features_df = sample.features_df.with_columns(
                    pl.lit(None, dtype=dtype).alias(col_name),
                )

        # Update features_df with top identifications
        if not top_ids.is_empty():
            if target_uids is not None:
                # Selective update: only update features that were just processed
                # Use join with coalesce to preserve existing values for non-updated features
                sample.features_df = (
                    sample.features_df.join(
                        top_ids.select(
                            [
                                "feature_id",
                                "id_top_name",
                                "id_top_class",
                                "id_top_adduct",
                                "id_top_score",
                                "id_source",
                            ],
                        ),
                        on="feature_id",
                        how="left",
                        suffix="_new",
                    )
                    .with_columns(
                        [
                            pl.coalesce(["id_top_name_new", "id_top_name"]).alias(
                                "id_top_name",
                            ),
                            pl.coalesce(["id_top_class_new", "id_top_class"]).alias(
                                "id_top_class",
                            ),
                            pl.coalesce(["id_top_adduct_new", "id_top_adduct"]).alias(
                                "id_top_adduct",
                            ),
                            pl.coalesce(["id_top_score_new", "id_top_score"]).alias(
                                "id_top_score",
                            ),
                            pl.coalesce(["id_source_new", "id_source"]).alias(
                                "id_source",
                            ),
                        ],
                    )
                    .drop(
                        [
                            "id_top_name_new",
                            "id_top_class_new",
                            "id_top_adduct_new",
                            "id_top_score_new",
                            "id_source_new",
                        ],
                    )
                )
            else:
                # Full update: use map_elements for all features
                id_mapping = {}
                for row in top_ids.iter_rows(named=True):
                    feature_id = row["feature_id"]
                    id_mapping[feature_id] = {
                        "id_top_name": row["id_top_name"],
                        "id_top_class": row["id_top_class"],
                        "id_top_adduct": row["id_top_adduct"],
                        "id_top_score": row["id_top_score"],
                        "id_source": row["id_source"],
                    }

                sample.features_df = sample.features_df.with_columns(
                    [
                        pl.col("feature_id")
                        .map_elements(
                            lambda uid: id_mapping.get(uid, {}).get("id_top_name"),
                            return_dtype=pl.String,
                        )
                        .alias("id_top_name"),
                        pl.col("feature_id")
                        .map_elements(
                            lambda uid: id_mapping.get(uid, {}).get("id_top_class"),
                            return_dtype=pl.String,
                        )
                        .alias("id_top_class"),
                        pl.col("feature_id")
                        .map_elements(
                            lambda uid: id_mapping.get(uid, {}).get("id_top_adduct"),
                            return_dtype=pl.String,
                        )
                        .alias("id_top_adduct"),
                        pl.col("feature_id")
                        .map_elements(
                            lambda uid: id_mapping.get(uid, {}).get("id_top_score"),
                            return_dtype=pl.Float64,
                        )
                        .alias("id_top_score"),
                        pl.col("feature_id")
                        .map_elements(
                            lambda uid: id_mapping.get(uid, {}).get("id_source"),
                            return_dtype=pl.String,
                        )
                        .alias("id_source"),
                    ],
                )

        if logger:
            num_updated = len(top_ids)
            logger.debug(
                f"Updated features_df with top identifications for {num_updated} features",
            )

    except Exception as e:
        if logger:
            logger.error(f"Error updating features_df with identification results: {e}")
        # Don't re-raise to avoid breaking the identification process


def _generate_13c_isotopes(lib_df):
    """
    Generate 13C isotope variants for library entries.

    For each compound with n carbon atoms, creates n+1 entries:
    - iso=0: original compound (no 13C)
    - iso=1: one 13C isotope (+1.00335 Da)
    - iso=2: two 13C isotopes (+2.00670 Da)
    - ...
    - iso=n: n 13C isotopes (+n*1.00335 Da)

    All isotopomers share the same quant_group.

    Args:
        lib_df: Polars DataFrame with library entries

    Returns:
        Polars DataFrame with additional 13C isotope entries
    """
    if lib_df.is_empty():
        return lib_df

    # First, ensure all original entries have iso=0
    original_df = lib_df.with_columns(pl.lit(0).alias("iso"))

    isotope_entries = []
    next_lib_id = lib_df["lib_id"].max() + 1 if len(lib_df) > 0 else 1

    # Mass difference for one 13C isotope
    c13_mass_shift = 1.00335  # Mass difference between 13C and 12C

    for row in original_df.iter_rows(named=True):
        formula = row.get("formula", "")
        if not formula:
            continue

        # Count carbon atoms in the formula
        carbon_count = _count_carbon_atoms(formula)
        if carbon_count == 0:
            continue

        # Get the original quant_group to keep it consistent across isotopes
        quant_group = row.get("quant_group", row.get("cmpd_id", row.get("lib_id", 1)))

        # Generate isotope variants (1 to n 13C atoms)
        for iso_num in range(1, carbon_count + 1):
            # Calculate mass shift for this number of 13C isotopes
            mass_shift = iso_num * c13_mass_shift

            # Create new entry
            isotope_entry = dict(row)  # Copy all fields
            isotope_entry["lib_id"] = next_lib_id
            isotope_entry["iso"] = iso_num
            isotope_entry["m"] = row["m"] + mass_shift
            isotope_entry["mz"] = (
                (row["m"] + mass_shift) / abs(row["z"])
                if row["z"] != 0
                else row["m"] + mass_shift
            )
            isotope_entry["quant_group"] = quant_group  # Keep same quant_group

            isotope_entries.append(isotope_entry)
            next_lib_id += 1

    # Combine original entries (now with iso=0) with isotope entries
    if isotope_entries:
        isotope_df = pl.DataFrame(isotope_entries)
        # Ensure schema compatibility by aligning data types
        try:
            return pl.concat([original_df, isotope_df])
        except Exception:
            # If concat fails due to schema mismatch, convert to compatible types
            # Get common schema
            original_schema = original_df.schema

            # Cast isotope_df columns to match original_df schema where possible
            cast_exprs = []
            for col_name in isotope_df.columns:
                if col_name in original_schema:
                    target_dtype = original_schema[col_name]
                    cast_exprs.append(pl.col(col_name).cast(target_dtype, strict=False))
                else:
                    cast_exprs.append(pl.col(col_name))

            isotope_df_cast = isotope_df.select(cast_exprs)
            return pl.concat([original_df, isotope_df_cast])
    else:
        return original_df


def _count_carbon_atoms(formula: str) -> int:
    """
    Count the number of carbon atoms in a molecular formula.

    Args:
        formula: Molecular formula string like "C6H12O6"

    Returns:
        Number of carbon atoms
    """
    import re

    if not formula or not isinstance(formula, str):
        return 0

    # Look for carbon followed by optional number
    # C followed by digits, or just C (which means 1)
    carbon_matches = re.findall(r"C(\d*)", formula)

    total_carbons = 0
    for match in carbon_matches:
        if match == "":
            # Just 'C' without number means 1 carbon
            total_carbons += 1
        else:
            # 'C' followed by number
            total_carbons += int(match)

    return total_carbons
