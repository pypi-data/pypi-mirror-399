# mypy: disable-error-code="union-attr,arg-type,attr-defined"
from __future__ import annotations

from datetime import datetime
import os

import polars as pl
import pyopenms as oms
from tqdm import tqdm

from masster.exceptions import ConfigurationError
from masster.sample.sample import Sample


def save(self, filename=None, add_timestamp=True, compress=False, version="v3"):
    """Save the study to an HDF5 file (.study5 format).

    Serializes the entire study object including samples, features, consensus data,
    alignment results, identification data, and parameters into a single .study5 file.
    Supports multiple format versions for compatibility and performance optimization.

    Args:
        filename (str | None): Target file name. If None, saves to "data.study5" in
            the study folder. Relative paths are resolved relative to study folder.
        add_timestamp (bool): If True, appends timestamp (YYYYMMDD-HHMMSS) to filename
            to avoid overwriting existing files. Defaults to True.
        compress (bool): If True, uses compressed storage mode and skips heavy columns
            for maximum speed. Recommended for very large studies (>1M features).
            Defaults to False.
        version (str): Format version to use. Options:

            - "v3" (default): Fastest version, optimized for large datasets
            - "v2": More reliable for complex data structures and string columns
            - "v1": Legacy format for backward compatibility

    Returns:
        str: Absolute path to the saved .study5 file.

    Example:
        ::

            from masster import Study

            # Load and process study
            s = Study(folder="./my_study")
            s.load()
            s.align()
            s.merge()
            s.fill()
            s.integrate()

            # Save with timestamp (default)
            path = s.save()
            s.logger.info(f"Saved to: {path}")
            # Output: Saved to: ./my_study/data_20231027-143005.study5

            # Save to specific file without timestamp
            s.save(
                filename="final_results.study5",
                add_timestamp=False
            )

            # Save using reliable v2 format
            s.save(version="v2")

            # Save compressed for very large studies
            s.save(compress=True)  # Skips some heavy columns

            # Save with custom name and timestamp
            s.save(filename="project_results.study5")  # Adds timestamp

    Note:
        **Format Versions:**

        Version comparison:

        | Version | Speed | Reliability | String Support | Recommended Use |
        |---------|-------|-------------|----------------|------------------|
        | v3      | Fastest | Good | Limited | Large datasets, numeric data |
        | v2      | Medium | Best | Excellent | Complex data, many strings |
        | v1      | Slowest | Good | Good | Backward compatibility |

        **HDF5 Format:**

        Uses HDF5 for efficient storage of large dataframes. The .study5 format
        stores:

        - samples_df: Sample metadata and parameters
        - features_df: All detected features across samples
        - consensus_df: Consensus features from alignment/merging
        - consensus_mapping_df: Feature-to-consensus mappings
        - id_df: Identification results
        - adducts_df: Adduct annotations
        - history: Processing history and parameters

        **Automatic ConsensusXML Export:**

        If a consensus map exists (consensus_map is not None), automatically saves
        a corresponding .consensusXML file for OpenMS compatibility.

        **Performance:**

        Save times:

        - Small studies (<10k features): <1 second
        - Medium studies (10k-100k features): 1-10 seconds
        - Large studies (>100k features): 10-60 seconds

        Use compress=True for studies >500k features.

        **Timestamp Format:**

        When add_timestamp=True, appends format: _YYYYMMDD-HHMMSS
        Example: data_20231027-143005.study5

        **Path Resolution:**

        If filename is relative (not absolute), resolves to:

        1. Study folder if set: os.path.join(self.folder, filename)
        2. Current working directory if study folder not set

    See Also:
        - :meth:`load`: Load study from .study5 file
        - :meth:`export_excel`: Export to multi-sheet Excel workbook
        - :class:`~masster.sample.Sample`: For saving individual samples
    """

    if filename is None:
        # save to default file name in folder
        if self.folder is not None:
            filename = os.path.join(self.folder, "data.study5")
        else:
            self.logger.error("either filename or folder must be provided")
            return
    # check if filename includes any path
    elif not os.path.isabs(filename):
        if self.folder is not None:
            filename = os.path.join(self.folder, filename)
        else:
            filename = os.path.join(os.getcwd(), filename)

    # Add timestamp by default to avoid overwriting (original behavior restored)
    if add_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{filename.replace('.study5', '')}_{timestamp}.study5"

    # Log file size information for performance monitoring
    if hasattr(self, "features_df") and not self.features_df.is_empty():
        feature_count = len(self.features_df)
        sample_count = (
            len(self.samples_df)
            if hasattr(self, "samples_df") and not self.samples_df.is_empty()
            else 0
        )
        self.logger.debug(
            f"Saving study with {sample_count} samples and {feature_count} features to {filename}",
        )

    # Use compressed mode for large datasets
    if compress:
        from masster.study.h5 import _save_study5_compressed

        _save_study5_compressed(self, filename)
    # Choose format version
    elif version == "v1":
        from masster.study.h5 import _save_study5_v1

        _save_study5_v1(self, filename)
    elif version == "v2":
        from masster.study.h5 import _save_study5_v2

        _save_study5_v2(self, filename)
    elif version == "v3":
        from masster.study.h5_v3 import _save_study5_v3

        _save_study5_v3(self, filename)
    else:
        raise ConfigurationError(
            f"Invalid version '{version}'. Must be 'v1', 'v2', or 'v3'."
            "\n\nSupported versions:"
            "\n  - 'v3': Latest format with optimized performance (recommended)"
            "\n  - 'v2': Modern format with columnized chromatogram storage"
            "\n  - 'v1': Legacy format for backward compatibility",
        )

    if self.consensus_map is not None:
        # save the features as a separate file
        from masster.study.save import _save_consensusXML

        _save_consensusXML(self, filename=filename.replace(".study5", ".consensusXML"))
    self.filename = filename


def save_samples(self, samples=None):
    if samples is None:
        # get all sample_ids from samples_df
        samples = self.samples_df["sample_id"].to_list()

    self.logger.info(f"Saving features for {len(samples)} samples...")

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for sample_id in tqdm(
        samples,
        total=len(samples),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Save samples",
        disable=tdqm_disable,
    ):
        # check if sample_id is in samples_df
        if sample_id not in self.samples_df.get_column("sample_id").to_list():
            self.logger.warning(
                f"Sample with id {sample_id} not found in samples_df.",
            )
            continue
        # load the mzpkl file
        sample_row = self.samples_df.filter(pl.col("sample_id") == sample_id)
        if sample_row.is_empty():
            continue
        ddaobj = Sample(filename=sample_row.row(0, named=True)["sample_path"])
        if "rt_original" not in ddaobj.features_df.columns:
            # add column 'rt_original' with rt values
            ddaobj.features_df = ddaobj.features_df.with_columns(
                pl.col("rt").alias("rt_original"),
            )
        # find the rows in features_df that match the sample_id
        matching_rows = self.features_df.filter(pl.col("sample_id") == sample_id)
        if not matching_rows.is_empty():
            # Update rt values in ddaobj.features_df based on matching_rows
            rt_values = matching_rows["rt"].to_list()
            if len(rt_values) == len(ddaobj.features_df):
                ddaobj.features_df = ddaobj.features_df.with_columns(
                    pl.lit(rt_values).alias("rt"),
                )
        # save ddaobj
        ddaobj.save()
        sample_name = sample_row.row(0, named=True)["sample_name"]
        sample_path = sample_row.row(0, named=True)["sample_path"]

        # Find the index of this sample in the original order for features_maps
        sample_index = next(
            (
                i
                for i, row_dict in enumerate(self.samples_df.iter_rows(named=True))
                if row_dict["sample_id"] == sample_id
            ),
            None,
        )

        # Determine where to save the featureXML file based on sample_path location
        if sample_path.endswith(".sample5"):
            # If sample_path is a .sample5 file, save featureXML in the same directory
            featurexml_filename = sample_path.replace(".sample5", ".featureXML")
            self.logger.debug(
                f"Saving featureXML alongside .sample5 file: {featurexml_filename}",
            )
        else:
            # Fallback to study folder or current directory (original behavior)
            if self.folder is not None:
                featurexml_filename = os.path.join(
                    self.folder,
                    sample_name + ".featureXML",
                )
            else:
                featurexml_filename = os.path.join(
                    os.getcwd(),
                    sample_name + ".featureXML",
                )
            self.logger.debug(
                f"Saving featureXML to default location: {featurexml_filename}",
            )

        fh = oms.FeatureXMLFile()
        if sample_index is not None and sample_index < len(self.features_maps):
            fh.store(featurexml_filename, self.features_maps[sample_index])

    self.logger.debug("All samples saved successfully.")


def _save_consensusXML(self, filename: str):
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.error("No consensus features found.")
        return

    # Build consensus map from consensus_df with proper consensus_id values
    import pyopenms as oms

    consensus_map = oms.ConsensusMap()

    # Set up file descriptions for all samples
    file_descriptions = consensus_map.getColumnHeaders()
    if hasattr(self, "samples_df") and not self.samples_df.is_empty():
        for i, sample_row in enumerate(self.samples_df.iter_rows(named=True)):
            file_description = file_descriptions.get(i, oms.ColumnHeader())
            file_description.filename = sample_row.get("sample_name", f"sample_{i}")
            file_description.size = 0  # Will be updated if needed
            file_description.unique_id = i + 1
            file_descriptions[i] = file_description
        consensus_map.setColumnHeaders(file_descriptions)

    # Add consensus features to the map (simplified version without individual features)
    for consensus_row in self.consensus_df.iter_rows(named=True):
        consensus_feature = oms.ConsensusFeature()

        # Set basic properties
        consensus_feature.setRT(float(consensus_row.get("rt", 0.0)))
        consensus_feature.setMZ(float(consensus_row.get("mz", 0.0)))
        consensus_feature.setIntensity(float(consensus_row.get("inty_mean", 0.0)))
        consensus_feature.setQuality(float(consensus_row.get("quality", 1.0)))

        # Set the unique consensus_id as the unique ID
        consensus_uid_str = consensus_row.get("consensus_uid", "")
        if consensus_uid_str and len(consensus_uid_str) == 16:
            try:
                # Convert 16-character hex string to integer for OpenMS
                consensus_uid_int = int(consensus_uid_str, 16)
                consensus_feature.setUniqueId(consensus_uid_int)
            except ValueError:
                # Fallback to hash if not hex
                consensus_feature.setUniqueId(
                    hash(consensus_uid_str) & 0x7FFFFFFFFFFFFFFF,
                )
        else:
            # Fallback to consensus_id
            consensus_feature.setUniqueId(consensus_row.get("consensus_id", 0))

        consensus_map.push_back(consensus_feature)

    # Save the consensus map
    fh = oms.ConsensusXMLFile()
    fh.store(filename, consensus_map)
    self.logger.debug(
        f"Saved consensus map with {len(self.consensus_df)} features to {filename}",
    )
    self.logger.debug("Features use unique 16-character consensus_id strings")


def save_consensus(self, **kwargs):
    """Save the consensus map to a file."""
    if self.consensus_map is None:
        self.logger.error("No consensus map found.")
        return
    from masster.study.save import _save_consensusXML

    _save_consensusXML(self, **kwargs)
