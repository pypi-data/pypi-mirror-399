"""
importers.py

Module providing import functionality for Sample class, specifically for importing
oracle identification data into features.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import polars as pl

from masster.exceptions import DataValidationError, FileFormatError


def import_oracle(
    self,
    folder,
    min_id_level=None,
    max_id_level=None,
):
    """
    Import oracle identification data and map it to features.

    This method reads oracle identification results from folder/diag/annotation_full.csv
    and creates lib_df and id_df DataFrames with detailed library and identification information.
    It also updates features_df with top identification results.

    Parameters:
        folder (str): Path to oracle folder containing diag/annotation_full.csv
        min_id_level (int, optional): Minimum identification level to include
        max_id_level (int, optional): Maximum identification level to include

    Returns:
        None: Updates features_df, creates lib_df and id_df in-place with oracle identification data

    Raises:
        FileNotFoundError: If the oracle annotation file doesn't exist
        ValueError: If features_df is empty or doesn't have required columns

    Example:
        >>> sample.import_oracle(
        ...     folder="path/to/oracle_results",
        ...     min_id_level=2,
        ...     max_id_level=4
        ... )
    """

    self.logger.info(f"Starting oracle import from folder: {folder}")

    # Validate inputs
    if self.features_df is None or self.features_df.is_empty():
        raise DataValidationError(
            "Cannot import Oracle annotations: no features detected in sample.\n\n"
            "Run feature detection first:\n"
            "  sample.detect_features()",
        )

    if "feature_id" not in self.features_df.columns:
        available_cols = ", ".join(self.features_df.columns)
        raise DataValidationError(
            "Cannot import Oracle annotations: features_df missing 'feature_id' column.\n"
            f"Available columns: {available_cols}\n\n"
            "This usually indicates the features DataFrame is incomplete.",
        )

    # Check if oracle file exists
    oracle_file_path = os.path.join(folder, "diag", "annotation_full.csv")
    if not os.path.exists(oracle_file_path):
        raise FileNotFoundError(f"Oracle annotation file not found: {oracle_file_path}")

    self.logger.debug(f"Loading oracle data from: {oracle_file_path}")

    try:
        # Read oracle data using pandas first for easier processing
        oracle_data = pd.read_csv(oracle_file_path)
        self.logger.info(
            f"Oracle data loaded successfully with {len(oracle_data)} rows",
        )
    except Exception as e:
        self.logger.error(f"Could not read {oracle_file_path}: {e}")
        raise

    # Extract feature_id from scan_title column (format: "uid:XYZ, ...")
    self.logger.debug(
        "Extracting feature UIDs from oracle scan_title using pattern 'uid:(\\d+)'",
    )
    oracle_data["feature_id"] = oracle_data["scan_title"].str.extract(
        r"uid:(\d+)",
        expand=False,
    )

    # Remove rows where feature_id extraction failed
    initial_count = len(oracle_data)
    oracle_data = oracle_data.dropna(subset=["feature_id"])
    oracle_data["feature_id"] = oracle_data["feature_id"].astype(int)

    self.logger.debug(
        f"Extracted feature UIDs for {len(oracle_data)}/{initial_count} oracle entries",
    )

    # Check if Oracle UIDs match features_df feature_id
    oracle_uids = set(oracle_data["feature_id"].unique())
    features_ids = set(self.features_df["feature_id"].to_list())
    matching_ids = oracle_uids.intersection(features_ids)

    if len(matching_ids) == 0:
        self.logger.error(
            "No matching feature_id found between Oracle annotations and features_df.\n\n"
            "This can happen if the sample5 file was loaded from an old format and migrated. "
            "Oracle import requires that features_df feature_id matches the UIDs in the Oracle file. "
            "Please re-run find_features() and Oracle analysis in the same session.",
        )
        raise ValueError(
            "No matching feature_id found between Oracle data and features_df",
        )
    if len(matching_ids) < len(oracle_uids):
        self.logger.warning(
            f"Only {len(matching_ids)}/{len(oracle_uids)} Oracle UIDs match features_df. "
            f"Filtering to matching features only.",
        )
        oracle_data = oracle_data[oracle_data["feature_id"].isin(list(matching_ids))]

    # Apply id_level filters if specified
    if min_id_level is not None:
        oracle_data = oracle_data[oracle_data["level"] >= min_id_level]
        self.logger.debug(
            f"After min_id_level filter ({min_id_level}): {len(oracle_data)} entries",
        )

    if max_id_level is not None:
        oracle_data = oracle_data[oracle_data["level"] <= max_id_level]
        self.logger.debug(
            f"After max_id_level filter ({max_id_level}): {len(oracle_data)} entries",
        )

    if len(oracle_data) == 0:
        self.logger.warning("No oracle entries remain after filtering")
        return

    # === CREATE LIB_DF ===
    self.logger.debug("Creating lib_df from Oracle annotation data")
    self.logger.debug(f"Oracle data shape before lib_df creation: {oracle_data.shape}")

    # Create unique lib_id for each library entry
    oracle_data["lib_id"] = range(len(oracle_data))

    # Map Oracle columns to lib_df schema
    lib_data = []
    for _, row in oracle_data.iterrows():
        # Convert cmpd_id to integer, using lib_id as fallback
        cmpd_id = row["lib_id"]  # Use lib_id as integer compound identifier
        try:
            if row.get("lib_id") is not None:
                cmpd_id = int(
                    float(str(row["lib_id"])),
                )  # Convert to int, handling potential float strings
        except (ValueError, TypeError):
            pass  # Keep lib_id as fallback

        lib_entry = {
            "lib_id": row["lib_id"],
            "cmpd_id": cmpd_id,  # Integer compound identifier
            "lib_source": "LipidOracle",  # Fixed source identifier
            "name": row.get("name", None),
            "shortname": row.get("species", None),
            "class": row.get("hg", None),
            "smiles": None,  # Not available in Oracle data
            "inchi": None,  # Not available in Oracle data
            "inchikey": None,  # Not available in Oracle data
            "formula": row.get("formula", None),
            "iso": 0,  # Fixed isotope value
            "adduct": row.get("ion", None),
            "probability": row.get("score", None),
            "stars": 0,  # Initialize to 0, can be modified with lib_compare
            "m": None,  # Would need to calculate from formula
            "z": 1
            if row.get("ion", "").find("+") != -1
            else (-1 if row.get("ion", "").find("-") != -1 else None),
            "mz": row.get("mz", None),  # Use mz column from annotation_full.csv
            "rt": None,  # Set to null as requested
            "quant_group": None,  # Set to null as requested
            "db_id": row.get("lib_id", None),
            "db": row.get("lib", None),
        }
        lib_data.append(lib_entry)

    self.logger.debug(f"Created {len(lib_data)} lib_data entries")

    # Create lib_df as Polars DataFrame with error handling for mixed types
    try:
        lib_df_temp = pl.DataFrame(lib_data)
    except Exception as e:
        self.logger.warning(f"Error creating lib_df with polars: {e}")
        # Fallback: convert to pandas first, then to polars
        lib_df_pandas = pd.DataFrame(lib_data)
        lib_df_temp = pl.from_pandas(lib_df_pandas)

    # Ensure uniqueness by name and adduct combination
    # Sort by lib_id and keep first occurrence (earliest in processing order)
    lib_df_new = lib_df_temp.sort("lib_id").unique(
        subset=["name", "adduct"],
        keep="first",
    )

    # Check if lib_df already exists and append with renumbered lib_id
    if (
        hasattr(self, "lib_df")
        and self.lib_df is not None
        and not self.lib_df.is_empty()
    ):
        # Find the maximum lib_id in existing lib_df
        max_existing_lib_id = self.lib_df.select(pl.col("lib_id").max()).item()
        if max_existing_lib_id is None:
            max_existing_lib_id = -1

        # Renumber lib_id in new entries to avoid conflicts
        lib_df_new = lib_df_new.with_columns(
            (pl.col("lib_id") - pl.col("lib_id").min() + max_existing_lib_id + 1).alias(
                "lib_id",
            ),
        )
        # Also update cmpd_id to match
        lib_df_new = lib_df_new.with_columns(
            (
                pl.col("cmpd_id") - pl.col("cmpd_id").min() + max_existing_lib_id + 1
            ).alias("cmpd_id"),
        )

        # Append to existing lib_df
        self.lib_df = pl.concat([self.lib_df, lib_df_new])
        self.logger.info(
            f"Appended {len(lib_df_new)} Oracle library entries ({len(lib_data) - len(lib_df_new)} duplicates removed). Total: {len(self.lib_df)}",
        )
    else:
        # Create new lib_df
        self.lib_df = lib_df_new
        self.logger.info(
            f"Created lib_df with {len(self.lib_df)} Oracle library entries ({len(lib_data) - len(self.lib_df)} duplicates removed)",
        )

    # === CREATE ID_DF ===
    self.logger.debug("Creating id_df from Oracle identification matches")

    # Create identification matches
    id_data = []
    for _, row in oracle_data.iterrows():
        # Use dmz from annotation_full.csv directly for mz_delta
        mz_delta = None
        if row.get("dmz") is not None:
            try:
                mz_delta = float(row["dmz"])
            except (ValueError, TypeError):
                pass

        # Use rt_err from annotation_full.csv for rt_delta, None if NaN
        rt_delta = None
        rt_err_value = row.get("rt_err")
        if rt_err_value is not None and not (
            isinstance(rt_err_value, float) and pd.isna(rt_err_value)
        ):
            try:
                rt_delta = float(rt_err_value)
            except (ValueError, TypeError):
                pass

        # Create id_source as "lipidoracle-" + score_metric from annotation_full.csv
        id_source = "lipidoracle"  # default fallback
        if row.get("score_metric") is not None:
            try:
                score_metric = str(row["score_metric"])
                id_source = f"lipidoracle-{score_metric}"
            except (ValueError, TypeError):
                pass

        id_entry = {
            "feature_id": row["feature_id"],
            "lib_id": row["lib_id"],
            "mz_delta": mz_delta,
            "rt_delta": rt_delta,
            "id_source": id_source,
            "score": row.get("score", None),
            "iso": 0,  # Fixed isotope value for oracle imports
        }
        id_data.append(id_entry)

    # Create id_df as Polars DataFrame with error handling
    try:
        id_df_temp = pl.DataFrame(id_data)
    except Exception as e:
        self.logger.warning(f"Error creating id_df with polars: {e}")
        # Fallback: convert to pandas first, then to polars
        id_df_pandas = pd.DataFrame(id_data)
        id_df_temp = pl.from_pandas(id_df_pandas)

    # Filter id_df to only include lib_ids that exist in the final unique lib_df
    unique_lib_ids = self.lib_df.select("lib_id").to_series()

    # Append to existing id_df or create new one
    if hasattr(self, "id_df") and self.id_df is not None and not self.id_df.is_empty():
        new_id_df = id_df_temp.filter(pl.col("lib_id").is_in(unique_lib_ids))
        self.id_df = pl.concat([self.id_df, new_id_df])
        self.logger.info(
            f"Appended {len(new_id_df)} Oracle identification matches. Total: {len(self.id_df)}",
        )
    else:
        self.id_df = id_df_temp.filter(pl.col("lib_id").is_in(unique_lib_ids))
        self.logger.info(
            f"Created id_df with {len(self.id_df)} Oracle identification matches",
        )

    # === UPDATE FEATURES_DF (adapted from consensus functionality) ===
    self.logger.debug("Updating features_df with top identification results")

    # Convert to polars for efficient joining with error handling
    try:
        oracle_pl = pl.DataFrame(oracle_data)
    except Exception as e:
        self.logger.warning(f"Error converting oracle_data to polars: {e}")
        # Convert using from_pandas properly
        oracle_pl = pl.from_pandas(oracle_data.reset_index(drop=True))

    # Group by feature_id and select the best identification (highest level)
    # In case of ties, take the first one
    best_ids = (
        oracle_pl.group_by("feature_id")
        .agg([pl.col("level").max().alias("max_level")])
        .join(oracle_pl, on="feature_id")
        .filter(pl.col("level") == pl.col("max_level"))
        .group_by("feature_id")
        .first()  # In case of ties, take the first
    )

    self.logger.debug(f"Selected best identifications for {len(best_ids)} features")

    # Prepare the identification columns (use name if available, otherwise species)
    id_columns = {
        "id_top_name": best_ids.select(
            "feature_id",
            pl.coalesce([pl.col("name"), pl.col("species")]).alias("name"),
        ),
        "id_top_adduct": best_ids.select("feature_id", "ion"),
        "id_top_class": best_ids.select("feature_id", "hg"),
        "id_top_score": best_ids.select(
            "feature_id",
            pl.col("score").round(3).alias("score"),
        ),
    }

    # Initialize identification columns in features_df if they don't exist
    for col_name in id_columns:
        if col_name not in self.features_df.columns:
            if col_name == "id_top_score":
                self.features_df = self.features_df.with_columns(
                    pl.lit(None, dtype=pl.Float64).alias(col_name),
                )
            else:
                self.features_df = self.features_df.with_columns(
                    pl.lit(None, dtype=pl.String).alias(col_name),
                )

    # Update features_df with oracle identifications
    for col_name, id_data_col in id_columns.items():
        oracle_column = id_data_col.columns[1]  # second column (after feature_id)

        # Create update dataframe
        update_data = id_data_col.rename({oracle_column: col_name})

        # Join and update
        self.features_df = (
            self.features_df.join(
                update_data,
                on="feature_id",
                how="left",
                suffix="_oracle",
            )
            .with_columns(pl.coalesce([f"{col_name}_oracle", col_name]).alias(col_name))
            .drop(f"{col_name}_oracle")
        )

    # Replace NaN values with None in identification columns
    id_col_names = ["id_top_name", "id_top_adduct", "id_top_class", "id_top_score"]
    for col_name in id_col_names:
        if col_name in self.features_df.columns:
            # For string columns, replace empty strings and "nan" with None
            if col_name != "id_top_score":
                self.features_df = self.features_df.with_columns(
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
                self.features_df = self.features_df.with_columns(
                    pl.when(pl.col(col_name).is_null() | pl.col(col_name).is_nan())
                    .then(None)
                    .otherwise(pl.col(col_name))
                    .alias(col_name),
                )

    # Count how many features were updated
    updated_count = self.features_df.filter(pl.col("id_top_name").is_not_null()).height
    total_features = len(self.features_df)

    self.logger.success(
        f"LipidOracle import completed. {updated_count}/{total_features} "
        f"features now have identifications ({updated_count / total_features * 100:.1f}%)",
    )

    # Update history
    self.update_history(
        ["import_oracle"],
        {
            "folder": folder,
            "min_id_level": min_id_level,
            "max_id_level": max_id_level,
            "updated_features": updated_count,
            "total_features": total_features,
            "lib_entries": len(self.lib_df),
            "id_matches": len(self.id_df),
        },
    )


def import_tima(
    self,
    folder,
    file="*results_mini",
):
    """
    Import TIMA identification data and map it to features.

    This method reads TIMA identification results from folder/*results_{file}.tsv
    and creates lib_df and id_df DataFrames with detailed library and identification information.
    It also updates features_df with top identification results.

    Parameters:
        folder (str): Path to folder containing TIMA results TSV file
        file (str): File suffix to search for (default: "*results_mini")
    Returns:
        None: Updates features_df, creates lib_df and id_df in-place with TIMA identification data

    Raises:
        FileNotFoundError: If the TIMA results file doesn't exist
        ValueError: If features_df is empty or doesn't have required columns

    Example:
        >>> sample.import_tima(
        ...     folder="path/to/tima_results",
        ...     file="mini"
        ... )
    """

    self.logger.info(f"Starting TIMA import from folder: {folder}")

    # Load name translator for InChIKey lookups
    translator_path = (
        Path(__file__).parent.parent / "data" / "libs" / "name_translator.parquet"
    )
    name_translator = None
    if translator_path.exists():
        try:
            name_translator = pl.read_parquet(translator_path)
            # Create lookup dict for faster access (inchikey -> name)
            translator_dict = dict(
                zip(
                    name_translator["inchikey"].to_list(),
                    name_translator["name"].to_list(),
                    strict=False,
                ),
            )
            self.logger.debug(
                f"Loaded name translator with {len(translator_dict)} entries",
            )
        except Exception as e:
            self.logger.warning(f"Could not load name translator: {e}")
            translator_dict = {}
    else:
        self.logger.warning(f"Name translator not found at {translator_path}")
        translator_dict = {}

    # Validate inputs
    if self.features_df is None or self.features_df.is_empty():
        raise DataValidationError(
            "Cannot import TIMA annotations: no features detected in sample.\n\n"
            "Run feature detection first:\n"
            "  sample.detect_features()",
        )

    if "feature_id" not in self.features_df.columns:
        available_cols = ", ".join(self.features_df.columns)
        raise DataValidationError(
            "Cannot import TIMA annotations: features_df missing 'feature_id' column.\n"
            f"Available columns: {available_cols}\n\n"
            "This usually indicates the features DataFrame is incomplete.",
        )

    # Find TIMA file
    import glob

    tima_pattern = os.path.join(folder, f"{file}.tsv")
    tima_files = glob.glob(tima_pattern)

    if not tima_files:
        raise FileNotFoundError(
            f"TIMA results file not found with pattern: {tima_pattern}",
        )

    tima_file_path = tima_files[0]
    self.logger.debug(f"Loading TIMA data from: {tima_file_path}")

    try:
        # Read TIMA data using polars without schema overrides initially
        tima_data = pl.read_csv(
            tima_file_path,
            separator="\t",
            infer_schema_length=10000,
        )
        self.logger.debug(f"TIMA data loaded successfully with {len(tima_data)} rows")
    except Exception as e:
        self.logger.error(f"Could not read {tima_file_path}: {e}")
        raise

    # Auto-detect feature identifier column and type from first column
    if len(tima_data.columns) == 0:
        raise FileFormatError(
            f"TIMA file has no columns: {tima_file_path}\n\n"
            "The file appears to be empty or corrupted. Check that:\n"
            "  1. The file contains valid TSV data\n"
            "  2. The file has at least one column with feature identifiers",
        )

    first_column_name = tima_data.columns[0]
    first_column_dtype = tima_data[first_column_name].dtype
    first_column_sample = (
        tima_data[first_column_name][0] if len(tima_data) > 0 else None
    )

    self.logger.debug(
        f"TIMA first column: '{first_column_name}', dtype: {first_column_dtype}, sample value: {first_column_sample}",
    )

    # Determine if first column contains UUIDs or integers
    is_uuid_like = False

    if "Int" in str(first_column_dtype):
        self.logger.debug("First column detected as integer type")
    elif "Utf8" in str(first_column_dtype) or "String" in str(first_column_dtype):
        # Check if it looks like UUID (36 chars with hyphens) or integer string
        if first_column_sample and len(str(first_column_sample)) >= 32:
            is_uuid_like = True
            self.logger.debug("First column detected as UUID string type")
        else:
            # Could be integer stored as string
            try:
                int(str(first_column_sample))
                self.logger.debug("First column detected as integer stored as string")
            except (ValueError, TypeError):
                is_uuid_like = True  # Default to UUID if not parseable as int
                self.logger.debug(
                    "First column detected as string (defaulting to UUID)",
                )

    # Determine which column in features_df to match against
    if is_uuid_like:
        # Match to feature_uid (UUID column)
        if "feature_uid" not in self.features_df.columns:
            raise ValueError(
                "TIMA file contains UUID identifiers but features_df doesn't have 'feature_uid' column",
            )

        target_column = "feature_uid"
        self.logger.debug(
            f"Matching TIMA '{first_column_name}' to features_df 'feature_uid' (UUID)",
        )

        # Ensure both are strings for comparison
        if "Utf8" not in str(tima_data[first_column_name].dtype):
            tima_data = tima_data.with_columns(
                [pl.col(first_column_name).cast(pl.Utf8)],
            )

        # Rename first column to feature_uid for consistency
        if first_column_name != "feature_uid":
            tima_data = tima_data.rename({first_column_name: "feature_uid"})

        # Get matching IDs
        features_ids = set(self.features_df["feature_uid"].to_list())
        tima_ids = set(tima_data["feature_uid"].to_list())

    else:  # is_integer_like
        # Match to feature_id (integer column)
        if "feature_id" not in self.features_df.columns:
            raise ValueError(
                "TIMA file contains integer identifiers but features_df doesn't have 'feature_id' column",
            )

        target_column = "feature_id"
        self.logger.info(
            f"Matching TIMA '{first_column_name}' to features_df 'feature_id' (integer)",
        )

        # Convert TIMA column to integer if it's string
        if "Utf8" in str(tima_data[first_column_name].dtype) or "String" in str(
            tima_data[first_column_name].dtype,
        ):
            tima_data = tima_data.with_columns(
                [pl.col(first_column_name).str.to_integer()],
            )

        # Rename first column to feature_id for consistency
        if first_column_name != "feature_id":
            tima_data = tima_data.rename({first_column_name: "feature_id"})

        # Get matching IDs
        features_ids = set(self.features_df["feature_id"].to_list())
        tima_ids = set(tima_data["feature_id"].to_list())

    # Compare and filter
    matching_ids = features_ids.intersection(tima_ids)
    non_matching_ids = tima_ids - features_ids

    if non_matching_ids:
        self.logger.warning(
            f"Found {len(non_matching_ids)} identifiers in TIMA data that do not match features_df. "
            f"These will be filtered out. Matching: {len(matching_ids)}/{len(tima_ids)}",
        )
        # Filter to only matching identifiers
        tima_data = tima_data.filter(pl.col(target_column).is_in(list(features_ids)))

    if len(tima_data) == 0:
        self.logger.error("No TIMA feature_ids match features_df feature_id values")
        raise ValueError("No matching features found between TIMA data and features_df")

    self.logger.debug(
        f"Matched {len(tima_data)} TIMA entries to features_df feature_id values",
    )

    # Detect TIMA file format and create column mapping
    # Format 1: *_mini files have columns like label_compound, adduct, smiles_no_stereo, etc.
    # Format 2: *_filtered files have columns like candidate_structure_name, candidate_adduct, etc.
    tima_columns = tima_data.columns

    column_map: dict[str, str | None]
    if "label_compound" in tima_columns:
        # Format 1: mini files
        self.logger.debug("Detected TIMA mini format")
        column_map = {
            "name": "label_compound",
            "adduct": "adduct",
            "smiles": "smiles_no_stereo",
            "inchikey": "inchikey_connectivity_layer",
            "formula": "molecular_formula",
            "mz": "mz",
            "score": "score",
            "library": "library",
            "error_mz": "error_mz",
            "error_rt": "error_rt",
            "class": "label_classyfire",
        }
    elif "candidate_structure_name" in tima_columns:
        # Format 2: filtered files
        self.logger.debug("Detected TIMA filtered format")
        column_map = {
            "name": "candidate_structure_name",
            "adduct": "candidate_adduct",
            "smiles": "candidate_structure_smiles_no_stereo",
            "inchikey": "candidate_structure_inchikey_connectivity_layer",
            "formula": "candidate_structure_molecular_formula",
            "mz": "feature_mz",
            "score": "score_final",
            "library": "candidate_library",
            "error_mz": "candidate_structure_error_mz",
            "error_rt": "candidate_structure_error_rt",
            "class": None,  # Not available in filtered format
        }
    else:
        raise FileFormatError(
            f"Unknown TIMA file format.\n\n"
            f"File: {tima_file_path}\n"
            f"Available columns: {', '.join(tima_columns)}\n\n"
            "Expected columns:\n"
            "  - Format 1 (*_mini): 'label_compound', 'adduct', 'smiles_no_stereo'\n"
            "  - Format 2 (*_filtered): 'candidate_structure_name', 'candidate_adduct'",
        )

    # Filter to only rows with identification data (non-empty name column)
    initial_count = len(tima_data)
    name_col = column_map["name"]
    assert name_col is not None, "name column should be mapped"
    tima_data = tima_data.filter(
        pl.col(name_col).is_not_null()
        & (pl.col(name_col).cast(pl.Utf8).str.strip_chars() != ""),
    )

    self.logger.debug(
        f"Filtered to {len(tima_data)}/{initial_count} TIMA entries with identifications",
    )

    if len(tima_data) == 0:
        self.logger.warning("No TIMA entries with identifications found")
        return

    # === CREATE LIB_DF ===
    self.logger.debug("Creating lib_df from TIMA annotation data")
    self.logger.debug(f"TIMA data shape before lib_df creation: {tima_data.shape}")

    # Suppress RDKit warnings during SMILES processing
    try:
        from rdkit import RDLogger

        rdkit_logger = RDLogger.logger()
        rdkit_logger.setLevel(RDLogger.ERROR)
    except ImportError:
        pass  # RDKit not available

    # Create unique lib_id for each library entry
    tima_data = tima_data.with_columns(pl.arange(0, len(tima_data)).alias("lib_id"))

    # Map TIMA columns to lib_df schema
    # Assert all required columns are mapped
    adduct_col = column_map["adduct"]
    assert adduct_col is not None, "adduct column should be mapped"
    smiles_col = column_map["smiles"]
    assert smiles_col is not None, "smiles column should be mapped"
    mz_col = column_map["mz"]
    assert mz_col is not None, "mz column should be mapped"
    inchikey_col = column_map["inchikey"]
    assert inchikey_col is not None, "inchikey column should be mapped"
    score_col = column_map["score"]
    assert score_col is not None, "score column should be mapped"
    library_col = column_map["library"]
    assert library_col is not None, "library column should be mapped"
    error_mz_col = column_map["error_mz"]
    assert error_mz_col is not None, "error_mz column should be mapped"
    error_rt_col = column_map["error_rt"]
    assert error_rt_col is not None, "error_rt column should be mapped"

    lib_data = []
    for row in tima_data.iter_rows(named=True):
        # Extract z (charge) from adduct
        z = None
        adduct_str = str(row.get(adduct_col, ""))
        if "+" in adduct_str:
            z = 1
        elif "-" in adduct_str:
            z = -1

        # Get SMILES
        smiles = row.get(smiles_col, None)
        if smiles is None or (isinstance(smiles, str) and smiles.strip() == ""):
            smiles = None

        # Calculate InChI from SMILES if available
        inchi = None
        if smiles:
            try:
                # Try to get InChI from SMILES using RDKit if available
                try:
                    from rdkit import Chem

                    mol_rdkit = Chem.MolFromSmiles(smiles)
                    if mol_rdkit:
                        inchi = Chem.MolToInchi(mol_rdkit)
                except ImportError:
                    pass  # RDKit not available
            except Exception:
                pass

        # Calculate formula from SMILES if available
        formula = None
        formula_col = column_map["formula"]
        if formula_col and formula_col in row:
            formula = row.get(formula_col, None)

        # If formula not in data, try to calculate from SMILES
        if not formula and smiles:
            try:
                from rdkit import Chem
                from rdkit.Chem import rdMolDescriptors

                mol_rdkit = Chem.MolFromSmiles(smiles)
                if mol_rdkit:
                    formula = rdMolDescriptors.CalcMolFormula(mol_rdkit)
            except ImportError:
                pass  # RDKit not available
            except Exception:
                pass

        # Calculate mass from m/z and charge
        m = None
        mz_value = row.get(mz_col, None)
        if mz_value is not None and z is not None:
            try:
                m = float(mz_value) * abs(z)
            except (ValueError, TypeError):
                pass

        # Get class and clean NaN values (only if class column is available)
        class_value = None
        class_col = column_map["class"]
        if class_col and class_col in row:
            class_value = row.get(class_col, None)
            if class_value is None or (
                isinstance(class_value, str)
                and (class_value.upper() == "NAN" or class_value == "notClassified")
            ):
                class_value = None

        # Calculate shortname: first check translator, then use first token when splitting at $
        name_value = row.get(name_col, None)
        shortname_value = None

        # First, try to get name from translator using InChIKey
        inchikey_value = row.get(inchikey_col, None)
        if inchikey_value and translator_dict:
            # Try full InChIKey first
            shortname_value = translator_dict.get(inchikey_value)
            # If not found, try short InChIKey (first 14 chars)
            if shortname_value is None and len(inchikey_value) >= 14:
                shortname_value = translator_dict.get(inchikey_value[:14])

        # If not found in translator, fall back to original logic
        if shortname_value is None and name_value:
            tokens = [token.strip() for token in str(name_value).split("$")]
            if tokens:
                shortname_value = tokens[0]
                if len(tokens) > 1:
                    shortname_value += f" {{+{len(tokens) - 1}}}"

        lib_entry = {
            "lib_id": row["lib_id"],
            "cmpd_id": row["lib_id"],  # Use lib_id as compound identifier
            "lib_source": "tima",
            "name": name_value,
            "shortname": shortname_value,
            "class": class_value,
            "smiles": smiles,
            "inchi": inchi,
            "inchikey": row.get(inchikey_col, None),
            "formula": formula,
            "iso": 0,  # Fixed isotope value
            "adduct": row.get(adduct_col, None),
            "probability": row.get(score_col, None),
            "stars": 0,  # Initialize to 0, can be modified with lib_compare
            "m": m,
            "z": z,
            "mz": row.get(mz_col, None),
            "rt": None,  # Set to null as requested
            "quant_group": None,
            "db_id": None,  # Not available in TIMA data
            "db": "tima"
            if row.get(library_col, None) == "TIMA MS1"
            else row.get(library_col, None),
        }
        lib_data.append(lib_entry)

    self.logger.debug(f"Created {len(lib_data)} lib_data entries")

    # Create lib_df as Polars DataFrame with explicit schema to handle mixed types
    lib_schema = {
        "lib_id": pl.Int64,
        "cmpd_id": pl.Int64,
        "lib_source": pl.Utf8,
        "name": pl.Utf8,
        "shortname": pl.Utf8,
        "class": pl.Utf8,
        "smiles": pl.Utf8,
        "inchi": pl.Utf8,
        "inchikey": pl.Utf8,
        "formula": pl.Utf8,
        "iso": pl.Int64,
        "adduct": pl.Utf8,
        "probability": pl.Float64,
        "stars": pl.Int64,
        "m": pl.Float64,
        "z": pl.Int64,
        "mz": pl.Float64,
        "rt": pl.Float64,
        "quant_group": pl.Utf8,
        "db_id": pl.Utf8,
        "db": pl.Utf8,
    }

    try:
        lib_df_temp = pl.DataFrame(lib_data, schema=lib_schema)
    except Exception as e:
        self.logger.warning(f"Error creating lib_df with explicit schema: {e}")
        # Fallback: convert to pandas first, then to polars
        lib_df_pandas = pd.DataFrame(lib_data)
        lib_df_temp = pl.from_pandas(lib_df_pandas)

    # Ensure uniqueness by name and adduct combination
    # Sort by lib_id and keep first occurrence (earliest in processing order)
    lib_df_new = lib_df_temp.sort("lib_id").unique(
        subset=["name", "adduct"],
        keep="first",
    )

    # Store the lib_id mapping for updating id_df later
    old_to_new_lib_id = {}

    # Check if lib_df already exists and append with renumbered lib_id
    if (
        hasattr(self, "lib_df")
        and self.lib_df is not None
        and not self.lib_df.is_empty()
    ):
        # Find the maximum lib_id in existing lib_df
        max_existing_lib_id = self.lib_df.select(pl.col("lib_id").max()).item()
        if max_existing_lib_id is None:
            max_existing_lib_id = -1

        # Create mapping from old lib_id to new lib_id before renumbering
        old_lib_ids = lib_df_new.select("lib_id").to_series().to_list()
        for i, old_uid in enumerate(old_lib_ids):
            old_to_new_lib_id[old_uid] = (
                old_uid - min(old_lib_ids) + max_existing_lib_id + 1
            )

        # Renumber lib_id in new entries to avoid conflicts
        lib_df_new = lib_df_new.with_columns(
            (pl.col("lib_id") - pl.col("lib_id").min() + max_existing_lib_id + 1).alias(
                "lib_id",
            ),
        )
        # Also update cmpd_id to match
        lib_df_new = lib_df_new.with_columns(
            (
                pl.col("cmpd_id") - pl.col("cmpd_id").min() + max_existing_lib_id + 1
            ).alias("cmpd_id"),
        )

        # Append to existing lib_df
        self.lib_df = pl.concat([self.lib_df, lib_df_new])
        self.logger.debug(
            f"Appended {len(lib_df_new)} TIMA library entries ({len(lib_data) - len(lib_df_new)} duplicates removed). Total: {len(self.lib_df)}",
        )
    else:
        # Create new lib_df - no renumbering needed
        self.lib_df = lib_df_new
        self.logger.debug(
            f"Created lib_df with {len(self.lib_df)} TIMA library entries ({len(lib_data) - len(self.lib_df)} duplicates removed)",
        )

    # === CREATE ID_DF ===
    self.logger.debug("Creating id_df from TIMA identification matches")

    # Create a mapping from TIMA identifier to features_df feature_id
    # The TIMA data now has either "feature_id" or "feature_uid" column depending on auto-detection
    # We need to map both to features_df feature_id for id_df
    if target_column == "feature_uid":
        # TIMA has feature_uid, create mapping: feature_uid -> feature_id
        feature_map = dict(
            zip(
                self.features_df["feature_uid"].to_list(),
                self.features_df["feature_id"].to_list(),
                strict=False,
            ),
        )
        tima_id_column = "feature_uid"
    else:
        # TIMA has feature_id, mapping is identity: feature_id -> feature_id
        feature_map = dict(
            zip(
                self.features_df["feature_id"].to_list(),
                self.features_df["feature_id"].to_list(),
                strict=False,
            ),
        )
        tima_id_column = "feature_id"

    # Create identification matches
    id_data = []
    for row in tima_data.iter_rows(named=True):
        # Map TIMA identifier to features_df feature_id
        tima_identifier = row[tima_id_column]
        feature_id = feature_map.get(tima_identifier)

        if feature_id is None:
            # Skip if we can't find the mapping (shouldn't happen after filtering)
            continue

        # Use error_mz for mz_delta
        mz_delta = None
        error_mz = row.get(error_mz_col, None)
        if error_mz is not None:
            try:
                mz_delta = round(float(error_mz), 4)
            except (ValueError, TypeError):
                pass

        # Use error_rt for rt_delta (convert from minutes to seconds)
        rt_delta = None
        rt_err_value = row.get(error_rt_col, None)
        if rt_err_value is not None:
            try:
                rt_delta = round(
                    float(rt_err_value) * 60.0,
                    4,
                )  # Convert minutes to seconds
            except (ValueError, TypeError):
                pass

        # Create matcher as "tima-ms1" for MS1, "tima-ms2-{library}" for MS2
        # Special handling: replace "TIMA MS1" with "ms1"
        matcher = "tima-ms2"  # default fallback
        library_value = row.get(library_col, None)
        if library_value is not None:
            try:
                library = str(library_value)
                if library == "TIMA MS1":
                    matcher = "tima-ms1"
                else:
                    matcher = f"tima-ms2 {library}"
            except (ValueError, TypeError):
                pass

        # Round score to 3 decimal digits
        score_value = row.get(score_col, None)
        if score_value is not None:
            try:
                score_value = round(float(score_value), 3)
            except (ValueError, TypeError):
                pass

        id_entry = {
            "feature_id": feature_id,  # Use mapped feature_id from features_df
            "lib_id": row["lib_id"],
            "mz_delta": mz_delta,
            "rt_delta": rt_delta,
            "matcher": matcher,
            "score": score_value,
            "iso": 0,  # Fixed isotope value for TIMA imports
        }
        id_data.append(id_entry)

    # Create id_df as Polars DataFrame with explicit schema to avoid inference issues
    # Match feature_id type to features_df
    feature_id_dtype = self.features_df["feature_id"].dtype
    id_schema = {
        "feature_id": feature_id_dtype,  # Match the type from features_df
        "lib_id": pl.Int64,
        "mz_delta": pl.Float64,
        "rt_delta": pl.Float64,
        "matcher": pl.Utf8,
        "score": pl.Float64,
        "iso": pl.Int64,
    }
    id_df_temp = pl.DataFrame(id_data, schema=id_schema)

    # Add id_source column based on matcher column
    # Keep matcher for compatibility, but id_source is now the canonical column
    id_df_temp = id_df_temp.with_columns(pl.col("matcher").alias("id_source"))

    # Apply lib_id mapping if we renumbered (when appending to existing lib_df)
    if old_to_new_lib_id:
        # Create a mapping expression using when/then chains
        mapping_expr = pl.col("lib_id")
        for old_uid, new_uid in old_to_new_lib_id.items():
            mapping_expr = (
                pl.when(pl.col("lib_id") == old_uid)
                .then(pl.lit(new_uid))
                .otherwise(mapping_expr)
            )
        id_df_temp = id_df_temp.with_columns(mapping_expr.alias("lib_id"))

    # Filter id_df to only include lib_ids that exist in the final unique lib_df
    unique_lib_ids = self.lib_df.select("lib_id").to_series()

    # Append to existing id_df or create new one
    if hasattr(self, "id_df") and self.id_df is not None and not self.id_df.is_empty():
        new_id_df = id_df_temp.filter(pl.col("lib_id").is_in(unique_lib_ids))
        self.id_df = pl.concat([self.id_df, new_id_df])
        self.logger.debug(
            f"Appended {len(new_id_df)} TIMA identification matches. Total: {len(self.id_df)}",
        )
    else:
        self.id_df = id_df_temp.filter(pl.col("lib_id").is_in(unique_lib_ids))
        self.logger.debug(
            f"Created id_df with {len(self.id_df)} TIMA identification matches",
        )

    # === UPDATE FEATURES_DF ===
    self.logger.debug("Updating features_df with top identification results")

    # tima_data is already a polars DataFrame
    tima_pl = tima_data

    # Add id_source column to tima_pl (create "tima-" + library)
    # Special handling: replace "TIMA MS1" with "ms1", and "tima-" with "tima-ms2" if not ms1
    # Re-assert column names are not None for this section
    assert library_col is not None, "library column should be mapped"
    assert score_col is not None, "score column should be mapped"
    tima_pl = tima_pl.with_columns(
        pl.when(pl.col(library_col).is_not_null())
        .then(
            pl.when(pl.col(library_col).cast(pl.Utf8) == "TIMA MS1")
            .then(pl.lit("tima-ms1"))
            .otherwise(
                pl.concat_str([pl.lit("tima-ms2-"), pl.col(library_col).cast(pl.Utf8)]),
            ),
        )
        .otherwise(pl.lit("tima-ms2"))
        .alias("id_source"),
    )

    # Group by feature_id/feature_uid and select the best identification (highest score)
    # In case of ties, take the first one
    best_ids = (
        tima_pl.group_by(target_column)
        .agg([pl.col(score_col).max().alias("max_score")])
        .join(tima_pl, on=target_column)
        .filter(pl.col(score_col) == pl.col("max_score"))
        .group_by(target_column)
        .first()  # In case of ties, take the first
    )

    # Map TIMA identifier (feature_uid or feature_id) to features_df feature_id
    if target_column == "feature_uid":
        # TIMA has feature_uid, map to feature_id
        best_ids = best_ids.join(
            self.features_df.select(["feature_uid", "feature_id"]),
            on="feature_uid",
            how="left",
        )
    else:
        # TIMA has feature_id, no mapping needed (but keep the structure)
        best_ids = best_ids.with_columns(pl.col("feature_id").alias("feature_id"))

    self.logger.debug(f"Selected best identifications for {len(best_ids)} features")

    # Count MS1-level matches per feature at max score level
    # First map TIMA identifier to feature_id for consistency
    if target_column == "feature_uid":
        tima_pl_with_fid = tima_pl.join(
            self.features_df.select(["feature_uid", "feature_id"]),
            on="feature_uid",
            how="left",
        )
    else:
        tima_pl_with_fid = tima_pl

    ms1_match_counts = (
        tima_pl_with_fid.filter(pl.col("id_source") == "tima-ms1")
        .group_by("feature_id")
        .agg(
            [
                pl.col(score_col).max().alias("max_ms1_score"),
                pl.col("lib_id").count().alias("total_ms1_matches"),
            ],
        )
        .join(
            tima_pl_with_fid.filter(pl.col("id_source") == "tima-ms1"),
            on="feature_id",
        )
        .filter(pl.col(score_col) == pl.col("max_ms1_score"))
        .group_by("feature_id")
        .agg([pl.col("lib_id").n_unique().alias("max_score_ms1_count")])
    )

    # Join with lib_df to get shortname, name, and formula
    best_ids_with_names = best_ids.join(
        self.lib_df.select(["lib_id", "shortname", "name", "formula"]),
        on="lib_id",
        how="left",
    ).join(ms1_match_counts, on="feature_id", how="left")

    # If a feature has >6 MS1 matches at max score level, use formula as shortname
    best_ids_with_names = best_ids_with_names.with_columns(
        pl.when(
            (pl.col("max_score_ms1_count") > 6) & (pl.col("id_source") == "tima-ms1"),
        )
        .then(pl.col("formula"))
        .otherwise(pl.col("shortname"))
        .alias("shortname"),
    )

    # Prepare the identification columns (use shortname if available, otherwise name)
    adduct_col = column_map["adduct"]
    id_columns = {
        "id_top_name": best_ids_with_names.select(
            "feature_id",
            pl.coalesce([pl.col("shortname"), pl.col("name")]).alias("name"),
        ),
        "id_top_adduct": best_ids_with_names.select("feature_id", adduct_col),
        "id_top_score": best_ids_with_names.select(
            "feature_id",
            pl.col(score_col).round(3).alias("score"),
        ),
        "id_source": best_ids_with_names.select("feature_id", "id_source"),
    }

    # Only add id_top_class if class column exists in the data
    class_col = column_map["class"]
    if class_col and class_col in best_ids_with_names.columns:
        id_columns["id_top_class"] = best_ids_with_names.select("feature_id", class_col)

    # Initialize all expected identification columns in features_df if they don't exist
    expected_id_columns = [
        "id_top_name",
        "id_top_adduct",
        "id_top_class",
        "id_top_score",
        "id_source",
    ]
    for col_name in expected_id_columns:
        if col_name not in self.features_df.columns:
            if col_name == "id_top_score":
                self.features_df = self.features_df.with_columns(
                    pl.lit(None, dtype=pl.Float64).alias(col_name),
                )
            else:
                self.features_df = self.features_df.with_columns(
                    pl.lit(None, dtype=pl.String).alias(col_name),
                )

    # Update features_df with TIMA identifications
    for col_name, id_data_col in id_columns.items():
        tima_column = id_data_col.columns[1]  # second column (after feature_id)

        # Create update dataframe
        update_data = id_data_col.rename({tima_column: col_name})

        # Join and update
        self.features_df = (
            self.features_df.join(
                update_data,
                on="feature_id",
                how="left",
                suffix="_tima",
            )
            .with_columns(pl.coalesce([f"{col_name}_tima", col_name]).alias(col_name))
            .drop(f"{col_name}_tima")
        )

    # Replace NaN values with None in identification columns
    id_col_names = [
        "id_top_name",
        "id_top_adduct",
        "id_top_class",
        "id_top_score",
        "id_source",
    ]
    for col_name in id_col_names:
        if col_name in self.features_df.columns:
            # For string columns, replace empty strings and "nan" with None
            if col_name not in ["id_top_score"]:
                # For id_top_class, also replace "notClassified" with None
                if col_name == "id_top_class":
                    self.features_df = self.features_df.with_columns(
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
                    self.features_df = self.features_df.with_columns(
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
                self.features_df = self.features_df.with_columns(
                    pl.when(pl.col(col_name).is_null() | pl.col(col_name).is_nan())
                    .then(None)
                    .otherwise(pl.col(col_name))
                    .alias(col_name),
                )

    # Count how many features were updated
    updated_count = self.features_df.filter(pl.col("id_top_name").is_not_null()).height
    total_features = len(self.features_df)

    # Count MS1 and MS2 match counts
    ms1_features = (
        self.id_df.filter(pl.col("id_source") == "tima-ms1")
        .select("feature_id")
        .n_unique()
    )
    ms2_features = (
        self.id_df.filter(pl.col("id_source").str.starts_with("tima-ms2"))
        .select("feature_id")
        .n_unique()
    )

    self.logger.success(
        f"TIMA import completed. {updated_count}/{total_features} "
        f"features now have identifications ({updated_count / total_features * 100:.1f}%) "
        f"[MS1: {ms1_features}, MS2: {ms2_features}]",
    )

    # Update history
    self.update_history(
        ["import_tima"],
        {
            "folder": folder,
            "file": file,
            "updated_features": updated_count,
            "total_features": total_features,
            "lib_entries": len(self.lib_df),
            "id_matches": len(self.id_df),
        },
    )
