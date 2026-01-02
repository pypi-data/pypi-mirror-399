"""
import.py

Module providing import functionality for Study class, specifically for importing
oracle and TIMA identification data into consensus features.
"""

from __future__ import annotations

import glob
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
    Import oracle identification data and map it to consensus features.

    This method reads oracle identification results from folder/diag/annotation_full.csv
    and creates lib_df and id_df DataFrames with detailed library and identification information.
    It also updates consensus_df with top identification results.

    Parameters:
        folder (str): Path to oracle folder containing diag/annotation_full.csv
        min_id_level (int, optional): Minimum identification level to include
        max_id_level (int, optional): Maximum identification level to include

    Returns:
        None: Updates consensus_df, creates lib_df and id_df in-place with oracle identification data

    Raises:
        FileNotFoundError: If the oracle annotation file doesn't exist
        ValueError: If consensus_df is empty or doesn't have required columns

    Example:
        >>> study.import_oracle(
        ...     folder="path/to/oracle_results",
        ...     min_id_level=2,
        ...     max_id_level=4
        ... )
    """

    self.logger.info(f"Starting oracle import from folder: {folder}")

    # Validate inputs
    if self.consensus_df is None or self.consensus_df.is_empty():
        raise DataValidationError(
            "Cannot import Oracle annotations: no merged features available.\n\n"
            "Run feature merging first:\n"
            "  study.merge(method='kd')",
        )

    if "consensus_id" not in self.consensus_df.columns:
        available_cols = ", ".join(self.consensus_df.columns)
        raise DataValidationError(
            "Cannot import Oracle annotations: consensus_df missing 'consensus_id' column.\n"
            f"Available columns: {available_cols}\n\n"
            "This usually indicates the consensus DataFrame is incomplete or corrupted.",
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

    # Extract consensus_id from scan_title column (format: "uid:XYZ, ...")
    self.logger.debug(
        "Extracting consensus UIDs from oracle scan_title using pattern 'uid:(\\d+)'",
    )
    oracle_data["consensus_id"] = oracle_data["scan_title"].str.extract(
        r"uid:(\d+)",
        expand=False,
    )

    # Remove rows where consensus_id extraction failed
    initial_count = len(oracle_data)
    oracle_data = oracle_data.dropna(subset=["consensus_id"])
    oracle_data["consensus_id"] = oracle_data["consensus_id"].astype(int)

    self.logger.debug(
        f"Extracted consensus UIDs for {len(oracle_data)}/{initial_count} oracle entries",
    )

    # Check if Oracle UIDs match consensus_df consensus_id
    oracle_uids = set(oracle_data["consensus_id"].unique())
    consensus_ids = set(self.consensus_df["consensus_id"].to_list())
    matching_ids = oracle_uids.intersection(consensus_ids)

    if len(matching_ids) == 0:
        self.logger.error(
            "Oracle UIDs do not match any consensus_id in consensus_df. "
            "This can happen if the study5 file was loaded from an old format and migrated. "
            "Oracle import requires that consensus_df consensus_id matches the UIDs in the Oracle file. "
            "Please re-run merge() and Oracle analysis in the same session.",
        )
        raise DataValidationError(
            "No matching consensus_id found between Oracle annotations and consensus_df.\n\n"
            "This can happen if the study5 file was loaded from an old format.\n"
            "Solution: Re-run study.merge() and Oracle analysis in the same session.",
        )
    if len(matching_ids) < len(oracle_uids):
        self.logger.warning(
            f"Only {len(matching_ids)}/{len(oracle_uids)} Oracle UIDs match consensus_df. "
            f"Filtering to matching features only.",
        )
        oracle_data = oracle_data[oracle_data["consensus_id"].isin(list(matching_ids))]

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
    self.lib_df = lib_df_temp.sort("lib_id").unique(
        subset=["name", "adduct"],
        keep="first",
    )

    self.logger.info(
        f"Created lib_df with {len(self.lib_df)} library entries ({len(lib_data) - len(self.lib_df)} duplicates removed)",
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
        from masster import is_null_value

        if not is_null_value(rt_err_value):
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
            "consensus_id": row["consensus_id"],
            "lib_id": row["lib_id"],
            "mz_delta": mz_delta,
            "rt_delta": rt_delta,
            "id_source": id_source,
            "score": row.get("score", None),
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
    self.id_df = id_df_temp.filter(pl.col("lib_id").is_in(unique_lib_ids))

    self.logger.info(f"Created id_df with {len(self.id_df)} identification matches")

    # === UPDATE CONSENSUS_DF (existing functionality) ===
    self.logger.debug("Updating consensus_df with top identification results")

    # Convert to polars for efficient joining with error handling
    try:
        oracle_pl = pl.DataFrame(oracle_data)
    except Exception as e:
        self.logger.warning(f"Error converting oracle_data to polars: {e}")
        # Convert using from_pandas properly
        oracle_pl = pl.from_pandas(oracle_data.reset_index(drop=True))

    # Group by consensus_id and select the best identification (highest level)
    # In case of ties, take the first one
    best_ids = (
        oracle_pl.group_by("consensus_id")
        .agg([pl.col("level").max().alias("max_level")])
        .join(oracle_pl, on="consensus_id")
        .filter(pl.col("level") == pl.col("max_level"))
        .group_by("consensus_id")
        .first()  # In case of ties, take the first
    )

    self.logger.debug(
        f"Selected best identifications for {len(best_ids)} consensus features",
    )

    # Prepare the identification columns (use name if available, otherwise species)
    id_columns = {
        "id_top_name": best_ids.select(
            "consensus_id",
            pl.coalesce([pl.col("name"), pl.col("species")]).alias("name"),
        ),
        "id_top_adduct": best_ids.select("consensus_id", "ion"),
        "id_top_class": best_ids.select("consensus_id", "hg"),
        "id_top_score": best_ids.select(
            "consensus_id",
            pl.col("score").round(3).alias("score"),
        ),
        "id_source": best_ids.select(
            "consensus_id",
            pl.when(pl.col("level") == 1)
            .then(pl.lit("lipidoracle ms1"))
            .otherwise(pl.lit("lipidoracle ms2"))
            .alias("id_source"),
        ),
    }

    # Initialize identification columns in consensus_df if they don't exist
    for col_name in id_columns:
        if col_name not in self.consensus_df.columns:
            if col_name == "id_top_score":
                self.consensus_df = self.consensus_df.with_columns(
                    pl.lit(None, dtype=pl.Float64).alias(col_name),
                )
            else:
                self.consensus_df = self.consensus_df.with_columns(
                    pl.lit(None, dtype=pl.String).alias(col_name),
                )

    # Update consensus_df with oracle identifications
    for col_name, id_data_col in id_columns.items():
        oracle_column = id_data_col.columns[1]  # second column (after consensus_id)

        # Create update dataframe
        update_data = id_data_col.rename({oracle_column: col_name})

        # Join and update
        self.consensus_df = (
            self.consensus_df.join(
                update_data,
                on="consensus_id",
                how="left",
                suffix="_oracle",
            )
            .with_columns(pl.coalesce([f"{col_name}_oracle", col_name]).alias(col_name))
            .drop(f"{col_name}_oracle")
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
        if col_name in self.consensus_df.columns:
            # For string columns, replace empty strings and "nan" with None
            if col_name != "id_top_score":
                self.consensus_df = self.consensus_df.with_columns(
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
                self.consensus_df = self.consensus_df.with_columns(
                    pl.when(pl.col(col_name).is_null() | pl.col(col_name).is_nan())
                    .then(None)
                    .otherwise(pl.col(col_name))
                    .alias(col_name),
                )

    # Count how many consensus features were updated
    updated_count = self.consensus_df.filter(pl.col("id_top_name").is_not_null()).height
    total_consensus = len(self.consensus_df)

    self.logger.success(
        f"LipidOracle import completed. {updated_count}/{total_consensus} "
        f"consensus features now have identifications ({updated_count / total_consensus * 100:.1f}%)",
    )

    # Update history
    self.update_history(
        ["import_oracle"],
        {
            "folder": folder,
            "min_id_level": min_id_level,
            "max_id_level": max_id_level,
            "updated_features": updated_count,
            "total_features": total_consensus,
            "lib_entries": len(self.lib_df),
            "id_matches": len(self.id_df),
        },
    )


def import_tima(self, folder, file="_min"):
    """
    Import TIMA identification data and map it to consensus features.

    This method reads TIMA identification results from folder/results_annotation_*.tsv
    and creates lib_df and id_df DataFrames with detailed library and identification information.
    It also updates consensus_df with top identification results.

    Parameters:
        folder (str): Path to TIMA folder containing results_annotation_*.tsv files
        file (str, optional): Base name of TIMA results file (default: "results_annotation")

    Returns:
        None: Updates consensus_df, creates lib_df and id_df in-place with TIMA identification data

    Raises:
        FileNotFoundError: If the TIMA results file doesn't exist
        ValueError: If consensus_df is empty or doesn't have required columns

    Example:
        >>> study.import_tima(folder="path/to/tima_results")
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
    if self.consensus_df is None or self.consensus_df.is_empty():
        raise DataValidationError(
            "Cannot import TIMA annotations: no merged features available.\n\n"
            "Run feature merging first:\n"
            "  study.merge(method='kd')",
        )

    if "consensus_id" not in self.consensus_df.columns:
        available_cols = ", ".join(self.consensus_df.columns)
        raise DataValidationError(
            "Cannot import TIMA annotations: consensus_df missing 'consensus_id' column.\n"
            f"Available columns: {available_cols}\n\n"
            "This usually indicates the consensus DataFrame is incomplete or corrupted.",
        )

    # Find TIMA file
    tima_pattern = os.path.join(folder, f"*{file}*.tsv")
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

    # Determine which column in consensus_df to match against
    if is_uuid_like:
        # Match to consensus_uid (UUID column)
        if "consensus_uid" not in self.consensus_df.columns:
            raise DataValidationError(
                "TIMA file contains UUID identifiers but consensus_df doesn't have 'consensus_uid' column\n"
                "Ensure consensus features were generated with UUIDs\n"
                "Available consensus columns: " + str(self.consensus_df.columns),
            )

        target_column = "consensus_uid"
        self.logger.debug(
            f"Matching TIMA '{first_column_name}' to consensus_df 'consensus_uid' (UUID)",
        )

        # Ensure both are strings for comparison
        if "Utf8" not in str(tima_data[first_column_name].dtype):
            tima_data = tima_data.with_columns(
                [pl.col(first_column_name).cast(pl.Utf8)],
            )

        # Rename first column to consensus_uid for consistency
        if first_column_name != "consensus_uid":
            tima_data = tima_data.rename({first_column_name: "consensus_uid"})

        # Get matching IDs
        consensus_ids = set(self.consensus_df["consensus_uid"].to_list())
        tima_ids = set(tima_data["consensus_uid"].to_list())

    else:  # is_integer_like
        # Match to consensus_id (integer column)
        if "consensus_id" not in self.consensus_df.columns:
            raise DataValidationError(
                "TIMA file contains integer identifiers but consensus_df doesn't have 'consensus_id' column\n"
                "Ensure consensus features were generated with integer IDs\n"
                "Available consensus columns: " + str(self.consensus_df.columns),
            )

        target_column = "consensus_id"
        self.logger.debug(
            f"Matching TIMA '{first_column_name}' to consensus_df 'consensus_id' (integer)",
        )

        # Convert TIMA column to integer if it's string
        if "Utf8" in str(tima_data[first_column_name].dtype) or "String" in str(
            tima_data[first_column_name].dtype,
        ):
            tima_data = tima_data.with_columns(
                [pl.col(first_column_name).str.to_integer()],
            )

        # Rename first column to consensus_id for consistency
        if first_column_name != "consensus_id":
            tima_data = tima_data.rename({first_column_name: "consensus_id"})

        # Get matching IDs
        consensus_ids = set(self.consensus_df["consensus_id"].to_list())
        tima_ids = set(tima_data["consensus_id"].to_list())

    # Compare and filter
    matching_ids = consensus_ids.intersection(tima_ids)
    non_matching_ids = tima_ids - consensus_ids

    if non_matching_ids:
        self.logger.warning(
            f"Found {len(non_matching_ids)} identifiers in TIMA data that do not match consensus_df. "
            f"These will be filtered out. Matching: {len(matching_ids)}/{len(tima_ids)}",
        )
        # Filter to only matching identifiers
        tima_data = tima_data.filter(pl.col(target_column).is_in(list(consensus_ids)))

    if len(tima_data) == 0:
        self.logger.error("No TIMA feature_ids match consensus_df consensus_id values")
        raise DataValidationError(
            "No matching features found between TIMA annotations and consensus_df.\n\n"
            f"TIMA file: {tima_file_path}\n"
            "Check that TIMA was run on the same feature set as the current study.",
        )

    self.logger.debug(
        f"Matched {len(tima_data)} TIMA entries to consensus_df consensus_id values",
    )

    # Detect TIMA file format and create column mapping
    # Format 1: *_mini files have columns like label_compound, adduct, smiles_no_stereo, etc.
    # Format 2: *_filtered files have columns like candidate_structure_name, candidate_adduct, etc.
    tima_columns = tima_data.columns

    if "label_compound" in tima_columns:
        # Format 1: mini files
        self.logger.debug("Detected TIMA mini format")
        column_map: dict[str, str | None] = {
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
    name_col = column_map["name"]
    assert name_col is not None, "name column should be mapped"
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
            "db": row.get(library_col, None),
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

    # No global deduplication - the same compound can appear for multiple features
    # Each lib_id represents a unique (feature, compound, adduct) combination
    self.lib_df = lib_df_temp

    self.logger.debug(f"Created lib_df with {len(self.lib_df)} library entries")

    # === CREATE ID_DF ===
    self.logger.debug("Creating id_df from TIMA identification matches")

    # Create a mapping from TIMA identifier to consensus_df consensus_id
    # The TIMA data now has either "consensus_id" or "consensus_uid" column depending on auto-detection
    # We need to map both to consensus_df consensus_id for id_df
    if target_column == "consensus_uid":
        # TIMA has consensus_uid, create mapping: consensus_uid -> consensus_id
        consensus_map = dict(
            zip(
                self.consensus_df["consensus_uid"].to_list(),
                self.consensus_df["consensus_id"].to_list(),
                strict=False,
            ),
        )
        tima_id_column = "consensus_uid"
    else:
        # TIMA has consensus_id, mapping is identity: consensus_id -> consensus_id
        consensus_map = dict(
            zip(
                self.consensus_df["consensus_id"].to_list(),
                self.consensus_df["consensus_id"].to_list(),
                strict=False,
            ),
        )
        tima_id_column = "consensus_id"

    # Create identification matches
    id_data = []
    for row in tima_data.iter_rows(named=True):
        # Map TIMA identifier to consensus_df consensus_id
        tima_identifier = row[tima_id_column]
        consensus_id = consensus_map.get(tima_identifier)

        if consensus_id is None:
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

        # Create id_source as "tima-ms1" for MS1, "tima-ms2-{library}" for MS2
        # Special handling: replace "TIMA MS1" with "ms1"
        id_source = "tima-ms2"  # default fallback
        library_value = row.get(library_col, None)
        if library_value is not None:
            try:
                library = str(library_value)
                if library == "TIMA MS1":
                    id_source = "tima-ms1"
                else:
                    id_source = f"tima-ms2 {library}"
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
            "consensus_id": consensus_id,  # Use mapped consensus_id from consensus_df
            "lib_id": row["lib_id"],
            "mz_delta": mz_delta,
            "rt_delta": rt_delta,
            "id_source": id_source,
            "score": score_value,
        }
        id_data.append(id_entry)

    # Create id_df as Polars DataFrame with explicit schema to avoid inference issues
    # Match consensus_id type to consensus_df
    consensus_id_dtype = self.consensus_df["consensus_id"].dtype
    id_schema = {
        "consensus_id": consensus_id_dtype,  # Match the type from consensus_df
        "lib_id": pl.Int64,
        "mz_delta": pl.Float64,
        "rt_delta": pl.Float64,
        "id_source": pl.Utf8,
        "score": pl.Float64,
    }
    id_df_temp = pl.DataFrame(id_data, schema=id_schema)

    # No filtering - all id_df entries are valid since we keep all lib_df entries
    self.id_df = id_df_temp

    self.logger.debug(f"Created id_df with {len(self.id_df)} identification matches")

    # === UPDATE CONSENSUS_DF ===
    self.logger.debug("Updating consensus_df with top identification results")

    # tima_data is already a polars DataFrame
    tima_pl = tima_data

    # Add id_source column to tima_pl (create "tima-" + library)
    # Special handling: replace "TIMA MS1" with "ms1", and "tima-" with "tima-ms2" if not ms1
    tima_pl = tima_pl.with_columns(
        pl.when(pl.col("library").is_not_null())
        .then(
            pl.when(pl.col("library").cast(pl.Utf8) == "TIMA MS1")
            .then(pl.lit("tima-ms1"))
            .otherwise(
                pl.concat_str([pl.lit("tima-ms2-"), pl.col("library").cast(pl.Utf8)]),
            ),
        )
        .otherwise(pl.lit("tima-ms2"))
        .alias("id_source"),
    )

    # Group by feature_id and select the best identification (highest score)
    # In case of ties, take the first one
    best_ids = (
        tima_pl.group_by("feature_id")
        .agg([pl.col("score").max().alias("max_score")])
        .join(tima_pl, on="feature_id")
        .filter(pl.col("score") == pl.col("max_score"))
        .group_by("feature_id")
        .first()  # In case of ties, take the first
    )

    # Join with consensus_df to map consensus_id to consensus_id
    best_ids = best_ids.join(
        self.consensus_df.select(["consensus_id", "consensus_id"]),
        left_on="feature_id",
        right_on="consensus_id",
        how="left",
    )

    self.logger.debug(
        f"Selected best identifications for {len(best_ids)} consensus features",
    )

    # Count MS1-level matches per feature at max score level
    ms1_match_counts = (
        tima_pl.filter(pl.col("id_source") == "tima-ms1")
        .group_by("feature_id")
        .agg(
            [
                pl.col("score").max().alias("max_ms1_score"),
                pl.col("lib_id").count().alias("total_ms1_matches"),
            ],
        )
        .join(tima_pl.filter(pl.col("id_source") == "tima-ms1"), on="feature_id")
        .filter(pl.col("score") == pl.col("max_ms1_score"))
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
    id_columns = {
        "id_top_name": best_ids_with_names.select(
            "consensus_id",
            pl.coalesce([pl.col("shortname"), pl.col("name")]).alias("name"),
        ),
        "id_top_adduct": best_ids_with_names.select("consensus_id", "adduct"),
        "id_top_score": best_ids_with_names.select(
            "consensus_id",
            pl.col("score").round(3).alias("score"),
        ),
        "id_source": best_ids_with_names.select("consensus_id", "id_source"),
    }

    # Only add id_top_class if label_classyfire column exists
    if "label_classyfire" in best_ids_with_names.columns:
        id_columns["id_top_class"] = best_ids_with_names.select(
            "consensus_id",
            "label_classyfire",
        )

    # Initialize all expected identification columns in consensus_df if they don't exist
    expected_id_columns = [
        "id_top_name",
        "id_top_adduct",
        "id_top_class",
        "id_top_score",
        "id_source",
    ]
    for col_name in expected_id_columns:
        if col_name not in self.consensus_df.columns:
            if col_name == "id_top_score":
                self.consensus_df = self.consensus_df.with_columns(
                    pl.lit(None, dtype=pl.Float64).alias(col_name),
                )
            else:
                self.consensus_df = self.consensus_df.with_columns(
                    pl.lit(None, dtype=pl.String).alias(col_name),
                )

    # Update consensus_df with TIMA identifications
    for col_name, id_data_col in id_columns.items():
        tima_column = id_data_col.columns[1]  # second column (after consensus_id)

        # Create update dataframe
        update_data = id_data_col.rename({tima_column: col_name})

        # Join and update
        self.consensus_df = (
            self.consensus_df.join(
                update_data,
                on="consensus_id",
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
        if col_name in self.consensus_df.columns:
            # For string columns, replace empty strings and "nan" with None
            if col_name not in ["id_top_score"]:
                # For id_top_class, also replace "notClassified" with None
                if col_name == "id_top_class":
                    self.consensus_df = self.consensus_df.with_columns(
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
                    self.consensus_df = self.consensus_df.with_columns(
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
                self.consensus_df = self.consensus_df.with_columns(
                    pl.when(pl.col(col_name).is_null() | pl.col(col_name).is_nan())
                    .then(None)
                    .otherwise(pl.col(col_name))
                    .alias(col_name),
                )

    # Count how many consensus features were updated
    updated_count = self.consensus_df.filter(pl.col("id_top_name").is_not_null()).height
    total_consensus = len(self.consensus_df)

    # Count MS1 and MS2 match counts
    ms1_features = (
        self.id_df.filter(pl.col("id_source") == "tima-ms1")
        .select("consensus_id")
        .n_unique()
    )
    ms2_features = (
        self.id_df.filter(pl.col("id_source").str.starts_with("tima-ms2"))
        .select("consensus_id")
        .n_unique()
    )

    self.logger.success(
        f"TIMA import completed. {updated_count}/{total_consensus} "
        f"consensus features now have identifications ({updated_count / total_consensus * 100:.1f}%) "
        f"[MS1: {ms1_features}, MS2: {ms2_features}]",
    )

    # Update history
    self.update_history(
        ["import_tima"],
        {
            "folder": folder,
            "file": file,
            "updated_features": updated_count,
            "total_features": total_consensus,
            "lib_entries": len(self.lib_df),
            "id_matches": len(self.id_df),
        },
    )
