# mypy: disable-error-code="assignment,attr-defined,index,unreachable"
"""
_export.py

This module provides data export functionality for mass spectrometry analysis results.
It handles saving processed data in various formats for downstream analysis, sharing,
and archival purposes, including spectrum files, feature tables, and custom formats.

Key Features:
- **Multi-Format Export**: Save data as MGF, mzML, CSV, FeatureXML, and custom formats.
- **Spectrum Export**: Export MS/MS spectra for database searching and identification.
- **Feature Export**: Save detected features with quantitative information.
- **Custom Formats**: Support for compressed pickle formats (mzpkl) for fast storage.
- **Metadata Preservation**: Maintain acquisition parameters and processing history.
- **Batch Export**: Export multiple samples or studies simultaneously.

Dependencies:
- `pyopenms`: For standard mass spectrometry file format export.
- `polars` and `pandas`: For tabular data export and manipulation.
- `numpy`: For numerical array operations.
- `pickle` and `bz2`: For custom format compression and serialization.
- `loguru`: For logging export operations and error handling.

Functions:
- `save()`: Main export function with format detection.
- `save_mzpkl()`: Export to compressed pickle format for fast loading.
- `save_featureXML()`: Export features in OpenMS FeatureXML format.
- `export_mgf()`: Export MS/MS spectra in MGF format for database searching.
- `export_csv()`: Export features and metadata in CSV format.

Supported Export Formats:
- MGF (Mascot Generic Format) for MS/MS spectra
- mzML (open standard format) for spectral data
- CSV for tabular feature data
- FeatureXML (OpenMS format) for feature data
- mzpkl (custom compressed format) for complete analysis results

Example Usage:
```python
from _export import save, export_mgf

# Save complete analysis in custom format
save(self, filename="analysis_results.mzpkl")

# Export MS/MS spectra for database searching
export_mgf(self, filename="ms2_spectra.mgf", export_type="all")

# Export feature table
export_csv(self, filename="features.csv", data_type="features")
```

See Also:
- `parameters._export_parameters`: For export-specific parameter configuration.
- `_import.py`: For data import functionality.
- `single.py`: For using export methods with ddafile class.

"""

from datetime import datetime
import json
import os

import numpy as np
import pandas as pd
import polars as pl
from tqdm import tqdm

from masster.exceptions import ConfigurationError, FileFormatError

# Parameters removed - using hardcoded defaults
from masster.spectrum import combine_peaks


def save(self, filename: str | None = None, version: str = "v2") -> None:
    """Save sample to .sample5 format file.

    Saves complete sample object including features, MS2 spectra, identifications,
    and processing history. Supports two format versions with different performance
    characteristics.

    Args:
        filename (str | None): Output file path. If None, uses self.file_path
            with .sample5 extension. Defaults to None.
        version (str): Format version. Options:
            - 'v2': Modern format with columnized chromatogram storage (default)
            - 'v1': Legacy format with JSON serialization (backward compatible)
            Defaults to 'v2'.

    Example:
        Basic save with auto-filename::

            >>> sample = masster.Sample("data.mzML")
            >>> sample.find_features()
            >>> sample.save()  # Creates data.sample5

        Custom filename::

            >>> sample.save("processed_sample.sample5")

        Legacy format for compatibility::

            >>> sample.save(version="v1")

        Complete workflow::

            >>> sample = masster.Sample("data.mzML")
            >>> sample.find_features()
            >>> sample.find_ms2()
            >>> sample.lib_load("hsapiens")
            >>> sample.identify()
            >>> sample.save("complete_analysis.sample5")
            >>>
            >>> # Later, reload saved sample
            >>> sample2 = masster.Sample("complete_analysis.sample5")

    Note:
        **Format version comparison:**

        v2 format (default, recommended):
        - ~80% faster save operations
        - ~60% faster load operations
        - ~30-40% smaller file sizes
        - Better compression of chromatogram data
        - Requires masster v0.8.0+

        v1 format (legacy):
        - Slower save/load operations
        - Larger file sizes
        - JSON serialization overhead
        - Compatible with all masster versions
        - Use for sharing with older installations

        **Saved data includes:**

        - features_df: Feature table with all columns
        - MS1 and MS2 spectral data
        - Identification results (id_df)
        - Library data (lib_df)
        - Adduct groupings (adducts_df)
        - Processing history and parameters
        - File metadata (polarity, acquisition type)

        **File format:**

        - HDF5-based storage
        - Compressed for reduced disk usage
        - Portable across platforms
        - Extension: .sample5

        **Automatic filename:**

        If filename=None, replaces original file extension:
        - "data.mzML" -> "data.sample5"
        - "sample.raw" -> "sample.sample5"

        **Updates file_path:**

        After saving, sample.file_path points to saved .sample5 file, enabling
        subsequent save() calls without filename argument.

        **Recommended workflow:**

        1. Process raw data (find_features, identify, etc.)
        2. Save to .sample5 for fast reload
        3. Distribute .sample5 files (much smaller than raw)
        4. Load .sample5 for analysis (instant, no reprocessing)

    Raises:
        ValueError: If neither filename nor self.file_path provided, or invalid
            version specified.

    See Also:
        Sample.__init__: Load saved .sample5 files.
        export_excel: Export features table to Excel.
        export_mgf: Export MS2 spectra.
    """
    if filename is None:
        # save to default file name
        if self.file_path is not None:
            filename = os.path.splitext(self.file_path)[0] + ".sample5"
        else:
            raise ConfigurationError(
                "Cannot save sample: no output filename specified and sample.file_path is not set.\n\n"
                "Please provide a filename:\n"
                "  sample.save(filename='output.sample5')\n\n"
                "Or load the sample from a file first so file_path is set.",
            )
    # check if filename includes an absolute path
    elif os.path.isabs(self.file_path):
        filename = os.path.splitext(filename)[0] + ".sample5"
    elif self.file_path is not None:
        filename = os.path.splitext(self.file_path)[0] + ".sample5"
    else:
        raise ConfigurationError(
            "Cannot save sample: filename provided without absolute path and sample.file_path is not set.\n\n"
            "Please either:\n"
            "  1. Provide an absolute path: sample.save(filename='/full/path/to/output.sample5')\n"
            "  2. Load the sample from a file first so file_path is set.",
        )

    # Use appropriate save function based on version
    if version == "v2":
        self._save_sample5_v2(filename=filename)
    elif version == "v1":
        self._save_sample5(filename=filename)
    else:
        raise ConfigurationError(
            f"Invalid version '{version}'. Must be 'v1' or 'v2'.\n\n"
            "Supported versions:\n"
            "  - 'v2': Modern format with columnized chromatogram storage (recommended)\n"
            "  - 'v1': Legacy format for backward compatibility",
        )

    self.file_path = filename


"""
def _save_featureXML(self, filename="features.featureXML"):
    if self._oms_features_map is None:
        self.logger.warning("No features found.")
        return
    fh = oms.FeatureXMLFile()
    fh.store(filename, self._oms_features_map)
    self.logger.debug(f"Features Map saved to {filename}")

"""


def export_features(self, filename: str = "features.csv") -> None:
    """
    Export the features DataFrame to a simple CSV or Excel file.

    This method clones the internal features DataFrame, adds a boolean column 'has_ms2' indicating
    whether the 'ms2_scans' column is not null, and exports the resulting DataFrame to the specified file.
    Columns with data types 'List' or 'Object' are excluded from the export.

    Parameters:
        filename (str): The path to the output file. If the filename ends with '.xls' or '.xlsx',
                        the data is exported in Excel format; otherwise, it is exported as CSV.
                        Defaults to 'features.csv'.

    Side Effects:
        Writes the exported data to the specified file and logs the export operation.
    """
    # clone df
    clean_df = self.features_df.clone()
    filename = os.path.abspath(filename)
    # add a column has_ms2=True if column ms2_scans is not None
    if "ms2_scans" in clean_df.columns:
        clean_df = clean_df.with_columns(
            (pl.col("ms2_scans").is_not_null()).alias("has_ms2"),
        )
    clean_df = self.features_df.select(
        [
            col
            for col in self.features_df.columns
            if self.features_df[col].dtype not in (pl.List, pl.Object)
        ],
    )
    if filename.lower().endswith((".xls", ".xlsx")):
        clean_df.to_pandas().to_excel(filename, index=False)
        self.logger.success(f"Features exported to {filename} (Excel format)")
    else:
        clean_df.write_csv(filename)
        self.logger.success(f"Features exported to {filename}")


def export_mgf(
    self,
    filename: str = "features.mgf",
    use_cache=True,
    selection="best",
    split_energy=True,
    merge=False,
    mz_start=None,
    mz_end=None,
    rt_start=None,
    rt_end=None,
    include_all_ms1=False,
    full_ms1=False,
    centroid=True,
    inty_min=float("-inf"),
    q1_ratio_min=None,
    q1_ratio_max=None,
    eic_corr_min=None,
    deisotope=True,
    precursor_trim=10.0,
    centroid_algo=None,
    clean=True,
    dia_stats=False,
):
    """Export features as MGF file with MS1 and MS2 spectra.

    Iterates over detected features, retrieves corresponding MS1 isotope patterns
    and MS2 spectra, applies peak filtering, and writes them in Mascot Generic
    Format (MGF) for database searching tools.

    Args:
        filename (str): Output MGF file path. Defaults to "features.mgf".
        use_cache (bool): Use cached MS2 spectra from features_df (faster). If
            False, retrieves spectra from raw data. Defaults to True.
        selection (str): MS2 scan selection strategy. Options:
            - "best": Export highest quality scan per feature
            - "all": Export all associated scans
            Defaults to "best".
        split_energy (bool): Process MS2 scans by unique collision energy. Creates
            separate entries for different energies. Defaults to True.
        merge (bool): If selection="all", merge all MS2 scans into consensus
            spectrum. Ignored if selection="best". Defaults to False.
        mz_start (float | None): Minimum m/z for feature selection filter.
            Defaults to None.
        mz_end (float | None): Maximum m/z for feature selection filter.
            Defaults to None.
        rt_start (float | None): Minimum RT (minutes) for feature selection.
            Defaults to None.
        rt_end (float | None): Maximum RT (minutes) for feature selection.
            Defaults to None.
        include_all_ms1 (bool): Include MS1 spectra even if no MS2 available.
            Useful for isotope pattern export. Defaults to False.
        full_ms1 (bool): Export full MS1 spectrum. If False, trims around
            precursor m/z. Defaults to False.
        centroid (bool): Centroid spectra if in profile mode. Defaults to True.
        inty_min (float): Minimum intensity threshold for peaks. Peaks below this
            value are removed. Defaults to -inf.
        q1_ratio_min (float | None): Minimum Q1 isolation ratio for DIA/ztscan
            peak filtering. None disables. Defaults to None.
        q1_ratio_max (float | None): Maximum Q1 isolation ratio for DIA/ztscan
            peak filtering. None disables. Defaults to None.
        eic_corr_min (float | None): Minimum EIC correlation for peak filtering.
            Removes peaks with poor chromatographic profiles. None disables.
            Defaults to None.
        deisotope (bool): Remove isotope peaks, keeping only monoisotopic.
            Recommended for database searching. Defaults to True.
        precursor_trim (float): m/z window around precursor to remove from MS2
            spectra. Removes unfragmented precursor ion. Defaults to 10.0.
        centroid_algo (str | None): Centroiding algorithm. Options: 'lmp', 'cwt',
            'gaussian'. None uses default. Defaults to None.
        clean (bool): Apply baseline filtering to remove noise peaks. Improves
            spectrum quality. Defaults to True.
        dia_stats (bool): Calculate DIA statistics (Q1 ratio, EIC correlation) for
            each MS2 spectrum. Only applies when use_cache=False. Required for
            q1_ratio_min/max and eic_corr_min filtering on DIA/ztscan data.
            Defaults to False.

    Example:
        Basic MGF export::

            >>> sample = masster.Sample("data.mzML")
            >>> sample.find_features()
            >>> sample.find_ms2()
            >>> sample.export_mgf("output.mgf")

        High-quality spectra for database searching::

            >>> sample.export_mgf(
            ...     "high_quality.mgf",
            ...     selection="best",
            ...     deisotope=True,
            ...     clean=True,
            ...     inty_min=100
            ... )

        Export specific m/z and RT range::

            >>> sample.export_mgf(
            ...     "region.mgf",
            ...     mz_start=200,
            ...     mz_end=800,
            ...     rt_start=5.0,
            ...     rt_end=15.0
            ... )

        Include isotope patterns without MS2::

            >>> sample.export_mgf(
            ...     "isotopes.mgf",
            ...     include_all_ms1=True,
            ...     full_ms1=True
            ... )

        DIA data with Q1 filtering and statistics::

            >>> sample.export_mgf(
            ...     "dia.mgf",
            ...     use_cache=False,
            ...     dia_stats=True,
            ...     q1_ratio_min=0.7,
            ...     q1_ratio_max=1.0,
            ...     eic_corr_min=0.8,
            ...     clean=True
            ... )

    Note:
        **MGF metadata fields:**

        - TITLE: Feature description (id, rt, mz, energy)
        - FEATURE_UID: UUID7 string (stable across operations)
        - FEATURE_ID: Integer feature index
        - CHARGE: Ion charge state (e.g., "1+", "2-")
        - PEPMASS: Precursor m/z
        - RTINSECONDS: Retention time in seconds
        - MSLEVEL: MS level (1 or 2)
        - ENERGY: Collision energy (MS2 only)
        - PRECURSORINTENSITY: Maximum intensity (MS1 only)

        **Export workflow:**

        1. Filter features by m/z and RT ranges
        2. Export MS1 isotope patterns (first pass)
        3. Export MS2 fragmentation spectra (second pass)
        4. Apply peak filters (intensity, Q1 ratio, EIC correlation)
        5. Process spectra (centroid, deisotope, clean)

        **Selection strategies:**

        - "best": Fastest, exports one spectrum per feature (highest quality)
        - "all": Complete data, exports every associated scan
        - "all" + merge=True: Consensus spectrum from all scans

        **Feature identifiers:**

        - feature_id: Integer index (0, 1, 2...), may change if features deleted
        - feature_uid: UUID string, stable across file operations

        **Peak filtering recommendations:**

        - Database searching: clean=True, deisotope=True, inty_min=100
        - DIA data: use_cache=False, dia_stats=True, q1_ratio_min/max, eic_corr_min
        - Isotope analysis: include_all_ms1=True, full_ms1=True, deisotope=False

        **DIA/ztscan data processing:**

        When working with DIA or ztscan data, set use_cache=False and dia_stats=True
        to calculate Q1 ratio and EIC correlation for each peak. These statistics
        help identify genuine fragment ions versus interference. The clean() method
        will properly filter all arrays including dia_stats arrays.

        **Charge assignment:**

        Automatically adjusted based on sample polarity (positive/negative mode).

    Raises:
        ValueError: If features_df is None (call find_features() first).

    See Also:
        find_features: Detect features before export.
        find_ms2: Link MS2 spectra to features.
        export_excel: Export feature table to Excel.
        export_csv: Export feature table to CSV.
        get_spectrum: Retrieve individual spectra.
    """

    if self.features_df is None:
        if self._oms_features_map is None:
            self.logger.warning("Please find features first.")
            return
        self.features_df = self._oms_features_map.get_df()

    # Apply filtering at DataFrame level for better performance
    features = self.features_df
    if mz_start is not None:
        features = features.filter(pl.col("mz") >= mz_start)
    if mz_end is not None:
        features = features.filter(pl.col("mz") <= mz_end)
    if rt_start is not None:
        features = features.filter(pl.col("rt") >= rt_start)
    if rt_end is not None:
        features = features.filter(pl.col("rt") <= rt_end)
    # Note: We no longer filter out features without MS2 data here since we want to export
    # MS1 spectra for ALL features with isotope data. The MS2 filtering is done in the
    # second pass where we specifically check for ms2_scans.

    # Convert to list of dictionaries for faster iteration
    features_list = features.to_dicts()

    def filter_peaks(
        spec,
        inty_min=None,
        q1_min=None,
        eic_min=None,
        q1_max=None,
        clean=False,
    ):
        # create a copy of the spectrum
        spec = spec.copy()

        # Apply baseline filtering first if clean=True
        if clean:
            spec = spec.clean()

        spec_len = len(spec.mz)
        mask = np.ones(spec_len, dtype=bool)  # Initialize as numpy array
        if inty_min is not None and inty_min > 0:
            mask = mask & (spec.inty >= inty_min)
        # check if q1_ratio is an attribute of spec
        if q1_min is not None and hasattr(spec, "q1_ratio"):
            mask = mask & (spec.q1_ratio >= q1_min)
        # check if eic_corr is an attribute of spec
        if q1_max is not None and hasattr(spec, "q1_ratio"):
            mask = mask & (spec.q1_ratio <= q1_max)
        # check if eic_corr is an attribute of spec
        if eic_min is not None and hasattr(spec, "eic_corr"):
            mask = mask & (spec.eic_corr >= eic_min)
        # apply mask to all attributes of spec with the same length as mz
        for attr in spec.__dict__:
            attr_val = getattr(spec, attr)
            # check it attr is a list or an array:
            if isinstance(attr_val, (list, np.ndarray)):
                # check if attr has length equal to spec_len:
                if hasattr(attr_val, "__len__") and len(attr_val) == spec_len:
                    if isinstance(attr_val, list):
                        # Convert list to numpy array, apply mask, convert back to list
                        setattr(spec, attr, np.array(attr_val)[mask].tolist())
                    else:
                        # Direct numpy array indexing
                        setattr(spec, attr, attr_val[mask])
        return spec

    def write_ion(f, title, fuid, fid, mz, rt, charge, spect):
        if spect is None:
            return "none"

        # For MSLEVEL=2 ions, don't write empty spectra
        ms_level = spect.ms_level if spect.ms_level is not None else 1
        if ms_level > 1 and (len(spect.mz) == 0 or len(spect.inty) == 0):
            return "empty_ms2"

        # Create dynamic title based on MS level
        if ms_level == 1:
            # MS1: id, rt, mz
            dynamic_title = f"id:{fid}, rt:{rt:.2f}, mz:{mz:.4f}"
        else:
            # MS2: id, rt, mz, energy
            energy = spect.energy if hasattr(spect, "energy") else 0
            dynamic_title = f"id:{fid}, rt:{rt:.2f}, mz:{mz:.4f}, energy:{energy}"

        f.write(f"BEGIN IONS\nTITLE={dynamic_title}\n")
        f.write(f"FEATURE_ID={fuid}\n")
        # Format charge: positive as "1+", "2+", negative as "1-", "2-"
        if charge < 0:
            charge_str = f"{abs(charge)}-"
        else:
            charge_str = f"{charge}+"
        f.write(f"CHARGE={charge_str}\nPEPMASS={mz}\nRTINSECONDS={rt}\n")

        if spect.ms_level is None:
            f.write("MSLEVEL=1\n")
            # Add PRECURSORINTENSITY for MS1 spectra
            if len(spect.inty) > 0:
                precursor_intensity = max(spect.inty)
                f.write(f"PRECURSORINTENSITY={precursor_intensity:.0f}\n")
        else:
            f.write(f"MSLEVEL={spect.ms_level}\n")
            # Add PRECURSORINTENSITY for MS1 spectra
            if spect.ms_level == 1 and len(spect.inty) > 0:
                precursor_intensity = max(spect.inty)
                f.write(f"PRECURSORINTENSITY={precursor_intensity:.0f}\n")

        if spect.ms_level is not None:
            if spect.ms_level > 1 and hasattr(spect, "energy"):
                # Always use absolute value for energy
                energy_val = abs(spect.energy) if spect.energy is not None else 0
                f.write(f"ENERGY={energy_val}\n")
        # Use list comprehension for better performance
        peak_lines = [
            f"{mz_val:.5f} {inty_val:.0f}\n"
            for mz_val, inty_val in zip(spect.mz, spect.inty, strict=False)
        ]
        f.writelines(peak_lines)
        f.write("END IONS\n\n")
        return "written"

    if centroid_algo is None:
        if hasattr(self.parameters, "centroid_algo"):
            centroid_algo = self.parameters.centroid_algo
        else:
            centroid_algo = "cr"

    # count how many features have charge < 0
    if (
        self.features_df.filter(pl.col("charge") < 0).shape[0]
        - self.features_df.filter(pl.col("charge") > 0).shape[0]
        > 0
    ):
        preferred_charge = -1
    else:
        preferred_charge = 1

    # For negative polarity, ensure charges are negative
    if hasattr(self, "polarity") and self.polarity is not None:
        if self.polarity.lower() in ["negative", "neg"]:
            if preferred_charge > 0:
                preferred_charge = -preferred_charge

    c = 0
    skip = 0
    empty_ms2_count = 0
    ms1_spec_used_count = 0
    ms1_fallback_count = 0
    # check if features is empty
    if len(features_list) == 0:
        self.logger.warning("No features found.")
        return
    filename = os.path.abspath(filename)
    with open(filename, "w", encoding="utf-8") as f:
        tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

        # First pass: Export MS1 spectra for ALL features with ms1_spec data
        for row in tqdm(
            features_list,
            total=len(features_list),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Export MS1 spectra",
            disable=tdqm_disable,
        ):
            # Pre-calculate common values
            feature_uid = row["feature_uid"]
            feature_id = row.get("feature_id", feature_uid)
            mz = row["mz"]
            rt = row["rt"]

            # Export MS1 spectrum for ALL features with ms1_spec data
            if "ms1_spec" in row and row["ms1_spec"] is not None:
                # Create spectrum from ms1_spec isotope pattern data
                from masster.spectrum import Spectrum

                iso_data = row["ms1_spec"]
                if len(iso_data) >= 2:  # Ensure we have mz and intensity arrays
                    ms1_mz = iso_data[0]
                    ms1_inty = iso_data[1]

                    # Create a Spectrum object from the isotope data
                    spect = Spectrum(
                        mz=np.array(ms1_mz),
                        inty=np.array(ms1_inty),
                        ms_level=1,
                    )

                    charge = preferred_charge
                    if row["charge"] is not None and row["charge"] != 0:
                        charge = row["charge"]
                    elif row["charge"] == 0:
                        # Replace charge 0 with polarity-based charge
                        charge = preferred_charge

                    # For negative polarity, ensure charge is negative
                    if hasattr(self, "polarity") and self.polarity is not None:
                        if self.polarity.lower() in ["negative", "neg"] and charge > 0:
                            charge = -charge

                    write_ion(
                        f,
                        f"id:{feature_id}",
                        feature_uid,
                        feature_id,
                        mz,
                        rt,
                        charge,
                        spect,
                    )
                    ms1_spec_used_count += 1
                else:
                    ms1_fallback_count += 1
            else:
                # No MS1 spectrum exported for features without ms1_spec data
                ms1_fallback_count += 1

        # Second pass: Export MS2 spectra for features with MS2 data
        for row in tqdm(
            features_list,
            total=len(features_list),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Export MS2 spectra",
            disable=tdqm_disable,
        ):
            # Pre-calculate common values
            feature_uid = row["feature_uid"]
            feature_id = row.get("feature_id", feature_uid)
            mz = row["mz"]
            rt = row["rt"]

            # Initialize charge for this feature
            charge = preferred_charge
            if row["charge"] is not None and row["charge"] != 0:
                charge = row["charge"]
            elif row["charge"] == 0:
                # Replace charge 0 with polarity-based charge
                charge = preferred_charge

            # For negative polarity, ensure charge is negative
            if hasattr(self, "polarity") and self.polarity is not None:
                if self.polarity.lower() in ["negative", "neg"] and charge > 0:
                    charge = -charge

            # Skip features without MS2 data (unless include_all_ms1 is True, but we already handled MS1 above)
            if row["ms2_scans"] is None:
                skip = skip + 1
                continue
            if use_cache:
                spect = row["ms2_specs"]
                if spect is None:
                    # No cached spectra, fall through to fetch from scan_id
                    use_cache = False
                # check if spec is a list of spectra
                elif isinstance(spect, list):
                    if selection == "best":
                        s = spect[0]
                        # Energy is already stored in cached spectrum - no need to fetch it again
                        spect = [s]
                        scan_uids = [row["ms2_scans"][0]]
                    else:
                        scan_uids = row["ms2_scans"]

                    for i, s in enumerate(spect):
                        if s is None:
                            print(
                                f"No MS2 spectrum for feature {feature_id} is cached.",
                            )
                            continue
                        # check if s is a spectrum
                        if type(s).__name__ == "Spectrum":
                            s = filter_peaks(
                                s,
                                inty_min=inty_min,
                                q1_min=q1_ratio_min,
                                eic_min=eic_corr_min,
                                q1_max=q1_ratio_max,
                                clean=clean,
                            )
                            # Get the corresponding scan_id from the list
                            scan_uids[i] if i < len(scan_uids) else "unknown"
                            result = write_ion(
                                f,
                                f"id:{feature_id}",
                                feature_uid,
                                feature_id,
                                mz,
                                rt,
                                charge,
                                s,
                            )
                            if result == "written":
                                c += 1
                            elif result == "empty_ms2":
                                empty_ms2_count += 1
                    continue  # Skip the rest of the processing for this feature

            # If we reach here, either use_cache=False or no cached spectra were available
            # Check if we can access raw data
            if self.file_interface is None:
                # Try to index the raw data file automatically
                self.logger.info(
                    "File interface not available. Attempting to index raw data...",
                )
                try:
                    self.index_raw()
                except Exception as e:
                    self.logger.warning(
                        f"Feature {feature_id}: Failed to index raw data: {e}. "
                        "Skipping MS2 export for this feature.",
                    )
                    skip += 1
                    continue

                # Check again after attempting to index
                if self.file_interface is None:
                    self.logger.warning(
                        f"Feature {feature_id}: No cached spectra and no file interface available. "
                        "Skipping MS2 export for this feature. Load the original raw data file to export uncached spectra.",
                    )
                    skip += 1
                    continue

            if split_energy:
                # get energy of all scans with scan_id in ms2_scans by fetching them
                ms2_scan_uids = row["ms2_scans"]
                if isinstance(ms2_scan_uids, list) and len(ms2_scan_uids) > 0:
                    # Fetch spectra to get energy information
                    spectra_with_energy = []
                    for scan_uid in ms2_scan_uids:
                        spec = self.get_spectrum(scan_uid)
                        if spec is not None:
                            spectra_with_energy.append(
                                (
                                    scan_uid,
                                    spec.energy if hasattr(spec, "energy") else 0,
                                ),
                            )

                    # Group by energy
                    energy_groups: dict[float, list[int]] = {}
                    for scan_uid, energy in spectra_with_energy:
                        if energy not in energy_groups:
                            energy_groups[energy] = []
                        energy_groups[energy].append(scan_uid)

                    for energy, scan_uids_for_energy in energy_groups.items():
                        if selection == "best":
                            # Keep only the first scan for this energy
                            scan_uids_for_energy = [scan_uids_for_energy[0]]

                        for scan_uid in scan_uids_for_energy:
                            spect = self.get_spectrum(
                                scan_uid,
                                centroid=centroid,
                                deisotope=deisotope,
                                precursor_trim=precursor_trim,
                                centroid_algo=centroid_algo,
                                dia_stats=dia_stats,
                            )
                            spect = filter_peaks(
                                spect,
                                inty_min=inty_min,
                                q1_min=q1_ratio_min,
                                eic_min=eic_corr_min,
                                q1_max=q1_ratio_max,
                            )
                            result = write_ion(
                                f,
                                f"id:{feature_id}",
                                feature_uid,
                                feature_id,
                                mz,
                                rt,
                                charge,
                                spect,
                            )
                            if result == "written":
                                c += 1
                            elif result == "empty_ms2":
                                empty_ms2_count += 1
            elif selection == "best":
                ms2_scans = row["ms2_scans"][0]
                spect = self.get_spectrum(
                    ms2_scans,
                    centroid=centroid,
                    deisotope=deisotope,
                    precursor_trim=precursor_trim,
                    dia_stats=dia_stats,
                    centroid_algo=centroid_algo,
                )
                spect = filter_peaks(
                    spect,
                    inty_min=inty_min,
                    q1_min=q1_ratio_min,
                    eic_min=eic_corr_min,
                    q1_max=q1_ratio_max,
                    clean=clean,
                )
                result = write_ion(
                    f,
                    f"id:{feature_id}",
                    feature_uid,
                    feature_id,
                    mz,
                    rt,
                    charge,
                    spect,
                )
                if result == "written":
                    c += 1
                elif result == "empty_ms2":
                    empty_ms2_count += 1
            elif selection == "all":
                if merge:
                    specs = []
                    for ms2_scans in row["ms2_scans"]:
                        specs.append(
                            self.get_spectrum(
                                ms2_scans,
                                centroid=centroid,
                                deisotope=deisotope,
                                dia_stats=dia_stats,
                                precursor_trim=precursor_trim,
                            ),
                        )
                    spect = combine_peaks(specs)
                    if centroid:
                        spect = spect.denoise()
                        if spect.ms_level == 1:
                            spect = spect.centroid(
                                tolerance=self.parameters["mz_tol_ms1_da"],
                                ppm=self.parameters["mz_tol_ms1_ppm"],
                                min_points=self.parameters["centroid_min_points_ms1"],
                                algo=centroid_algo,
                            )
                        elif spect.ms_level == 2:
                            spect = spect.centroid(
                                tolerance=self.parameters["mz_tol_ms2_da"],
                                ppm=self.parameters["mz_tol_ms2_ppm"],
                                min_points=self.parameters["centroid_min_points_ms2"],
                                algo=centroid_algo,
                            )
                    if deisotope:
                        spect = spect.deisotope()
                    title = f"id:{feature_id}"
                    spect = filter_peaks(
                        spect,
                        inty_min=inty_min,
                        q1_min=q1_ratio_min,
                        eic_min=eic_corr_min,
                        q1_max=q1_ratio_max,
                        clean=clean,
                    )
                    result = write_ion(
                        f,
                        title,
                        feature_uid,
                        feature_id,
                        mz,
                        rt,
                        charge,
                        spect,
                    )
                    if result == "written":
                        c += 1
                    elif result == "empty_ms2":
                        empty_ms2_count += 1
                else:
                    for ms2_scans in row["ms2_scans"]:
                        spect = self.get_spectrum(
                            ms2_scans,
                            centroid=centroid,
                            deisotope=deisotope,
                            precursor_trim=precursor_trim,
                            dia_stats=dia_stats,
                            centroid_algo=centroid_algo,
                        )
                        spect = filter_peaks(
                            spect,
                            inty_min=inty_min,
                            q1_min=q1_ratio_min,
                            eic_min=eic_corr_min,
                            q1_max=q1_ratio_max,
                            clean=clean,
                        )
                        result = write_ion(
                            f,
                            f"id:{feature_id}",
                            feature_uid,
                            feature_id,
                            mz,
                            rt,
                            charge,
                            spect,
                        )
                        if result == "written":
                            c += 1
                        elif result == "empty_ms2":
                            empty_ms2_count += 1

    if empty_ms2_count > 0:
        self.logger.info(f"Skipped {empty_ms2_count} empty MS2 spectra")
    if ms1_fallback_count > 0:
        self.logger.info(
            f"Skipped MS1 export for {ms1_fallback_count} features without isotope patterns",
        )

    # Handle None values in logging
    inty_min_str = f"{inty_min:.3f}" if inty_min != float("-inf") else "None"
    q1_ratio_min_str = f"{q1_ratio_min:.3f}" if q1_ratio_min is not None else "None"
    eic_corr_min_str = f"{eic_corr_min:.3f}" if eic_corr_min is not None else "None"

    self.logger.debug(
        f"MGF created with int>{inty_min_str}, q1_ratio>{q1_ratio_min_str}, eic_corr>{eic_corr_min_str}",
    )
    self.logger.debug(
        f"- Exported {c} MS2 spectra for {len(features_list) - skip} precursors. Average spectra/feature is {c / (len(features_list) - skip + 0.000000001):.0f}",
    )
    self.logger.debug(
        f"- Skipped {skip} features because no MS2 scans were available.",
    )

    self.logger.success(
        f"Exported {ms1_spec_used_count} MS1 spectra and {c} MS2 spectra to {filename}",
    )


def export_dda_stats(self, filename="stats.csv"):
    """
    Save DDA statistics into a CSV file.

    This method computes basic statistics from the DDA analysis, such as:
        - Total number of MS1 scans.
        - Total number of MS2 scans.
        - Total number of detected features.
        - Number of features linked with MS2 data.
        - Average cycle time (if available in the scans data).

    The resulting statistics are saved in CSV format.

    Parameters:
        filename (str): The name/path of the CSV file to be saved. Defaults to "stats.csv".

    Returns:
        None
    """
    # Compute counts from scans_df and features_df
    ms1_count = len(self.scans_df.filter(pl.col("ms_level") == 1))
    ms2_count = len(self.scans_df.filter(pl.col("ms_level") == 2))
    features_count = len(self.features_df) if self.features_df is not None else 0
    features_with_ms2 = (
        self.features_df.filter(pl.col("ms2_scans").is_not_null()).height
        if self.features_df is not None
        else 0
    )

    # Initialize a dictionary to hold statistics
    stats = {
        "MS1_scans": ms1_count,
        "MS2_scans": ms2_count,
        "Total_features": features_count,
        "Features_with_MS2": features_with_ms2,
    }

    # Calculate the average cycle time if available.
    if "time_cycle" in self.scans_df.columns:
        ms1_df = self.scans_df.filter(pl.col("ms_level") == 1)
        avg_cycle_time = ms1_df["time_cycle"].mean()
        stats["Average_cycle_time"] = (
            avg_cycle_time if avg_cycle_time is not None else ""
        )
    else:
        stats["Average_cycle_time"] = 0

    # Convert stats dict to a Pandas DataFrame and save as CSV.
    df_stats = pd.DataFrame(list(stats.items()), columns=["Metric", "Value"])
    df_stats.to_csv(filename, index=False)
    lines = []
    lines.append(f"Filename,{self.file_path}")
    lines.append(
        f"Number of cycles,{len(self.scans_df.filter(pl.col('ms_level') == 1))}",
    )
    lines.append(
        f"Number of MS2 scans,{len(self.scans_df.filter(pl.col('ms_level') == 2))}",
    )
    # retrieve scans with mslevel 1 from
    ms1 = self.scans_df.filter(pl.col("ms_level") == 1)
    lines.append(f"Maximal number of MS2 scans per cycle (N),{ms1['ms2_n'].max()}")
    # average number of MS2 scans per cycle, skip null values
    ms2n_mean = ms1.filter(pl.col("ms2_n") >= 0)["ms2_n"].mean()
    lines.append(f"Average number of MS2 scans per cycle,{ms2n_mean:.0f}")
    lines.append(f"Maximal cycle time,{ms1['time_cycle'].max():.3f}")
    # find spectra with ms2_n = 0
    ms1_ms2_0 = ms1.filter(pl.col("ms2_n") == 0)
    if len(ms1_ms2_0) > 0:
        lines.append(
            f"Average cycle time at MS1-only,{ms1_ms2_0['time_cycle'].mean():.3f}",
        )
    else:
        lines.append("Average cycle time at MS1-only,")
    # find spectra with ms2_n = 1
    ms1_ms2_1 = ms1.filter(pl.col("ms2_n") == 1)
    if len(ms1_ms2_1) > 0:
        lines.append(
            f"Average cycle time with 1 MS2,{ms1_ms2_1['time_cycle'].mean():.3f}",
        )
    else:
        lines.append("Average cycle time with 1 MS2,")
    # find spectra with ms2_n = 2
    ms1_ms2_2 = ms1.filter(pl.col("ms2_n") == 2)
    if len(ms1_ms2_2) > 0:
        lines.append(
            f"Average cycle time with 2 MS2,{ms1_ms2_2['time_cycle'].mean():.3f}",
        )
    else:
        lines.append("Average cycle time with 2 MS2,")
    # find spectra with ms2_n = 2
    ms1_ms2_3 = ms1.filter(pl.col("ms2_n") == 3)
    if len(ms1_ms2_3) > 0:
        lines.append(
            f"Average cycle time with 3 MS2,{ms1_ms2_3['time_cycle'].mean():.3f}",
        )
    else:
        lines.append("Average cycle time with 3 MS2,")
    max_ms2_n = ms1["ms2_n"].max()
    ms1_ms2_n1 = ms1.filter(pl.col("ms2_n") == max_ms2_n - 1)
    if len(ms1_ms2_n1) > 0:
        lines.append(
            f"Average cycle time with N-1 MS2,{ms1_ms2_n1['time_cycle'].mean():.3f}",
        )
    else:
        lines.append("Average cycle time with N-1 MS2,")
    # find specgtra with maximal ms2_n
    ms1_max_ms2_n = ms1.filter(pl.col("ms2_n") == max_ms2_n)
    lines.append(
        f"Average cycle time with N MS2,{ms1_max_ms2_n['time_cycle'].mean():.3f}",
    )
    # average time_MS1, skip null values
    a = ms1.filter(pl.col("time_ms1_to_ms1") >= 0)["time_ms1_to_ms1"].mean()
    if a is not None:
        lines.append(f"Average MS1-to-MS1 scan time,{a:.3f}")
    else:
        lines.append("Average MS1-to-MS1 scan time,")
    a = ms1.filter(pl.col("time_ms1_to_ms2") >= 0)["time_ms1_to_ms2"].mean()
    if a is not None:
        lines.append(f"Average MS1-to-MS2 scan time,{a:.3f}")
    else:
        lines.append("Average MS1-to-MS2 scan time,")
    ms2_mean = ms1.filter(pl.col("time_ms2_to_ms2") >= 0)["time_ms2_to_ms2"].mean()
    if ms2_mean is not None:
        lines.append(f"Average MS2-to-MS2 scan time,{ms2_mean:.3f}")
    else:
        lines.append("Average MS2-to-MS2 scan time,")
    a = ms1.filter(pl.col("time_ms2_to_ms1") >= 0)["time_ms2_to_ms1"].mean()
    if a is not None:
        lines.append(f"Average MS2-to-MS1 scan time,{a:.3f}")
    else:
        lines.append("Average MS2-to-MS1 scan time,")
    # number of features
    if self.features_df is not None:
        lines.append(f"Number of features,{self.features_df.height}")
        a = self.features_df.filter(pl.col("ms2_scans").is_not_null()).height
        lines.append(f"Number of features with MS2 data,{a}")
        b = self.scans_df.filter(pl.col("feature_id") >= 0).height
        lines.append(f"Number of MS2 scans with features,{b}")
        if a > 0:
            lines.append(f"Redundancy of MS2 scans with features,{b / a:.3f}")
        else:
            lines.append("Redundancy of MS2 scans with features,")
    else:
        lines.append("Number of features,")
        lines.append("Number of features with MS2 data,")
        lines.append("Number of MS2 scans with features,")
        lines.append("Redundancy of MS2 scans with features,")

    # write to file
    with open(filename, "w") as f:
        for line in lines:
            f.write(line + "\n")

    self.logger.success(f"DDA statistics exported to {filename}")


def export_excel(self, filename: str | None = None) -> None:
    """Export features DataFrame and results to Excel workbook.

    Exports features table, identification results, and processing history to a
    multi-sheet Excel (.xlsx) file. Automatically filters incompatible data types
    and adds MS2 availability indicator.

    Args:
        filename (str | None): Output Excel file path. Must end with '.xlsx' or
            '.xls'. If None, uses sample file_path with .xlsx extension.
            Defaults to None.

    Example:
        Basic export::

            >>> sample = masster.Sample("data.mzML")
            >>> sample.find_features()
            >>> sample.identify()
            >>> sample.export_excel("results.xlsx")

        Auto-filename from sample path::

            >>> sample.export_excel()  # Creates data.xlsx

        Access exported data::

            >>> import pandas as pd
            >>> features = pd.read_excel("results.xlsx", sheet_name="features")
            >>> ids = pd.read_excel("results.xlsx", sheet_name="id")
            >>> history = pd.read_excel("results.xlsx", sheet_name="history")

    Note:
        **Worksheet structure:**

        - features: Main feature table with quality metrics, adducts, identifications
        - id: Full identification results (if id_df exists)
        - history: Processing parameters and operation log (if history exists)

        **Data cleaning:**

        - Columns with List or Object types automatically excluded (Excel incompatible)
        - Complex objects (spectra, arrays) not exported
        - JSON serialization for nested parameters in history sheet

        **Added columns:**

        - has_ms2: Boolean indicating MS2 data availability per feature

        **Automatic filename:**

        If filename=None, replaces sample file extension with .xlsx
        (e.g., "data.mzML" -> "data.xlsx")

        **Excel engine:**

        Uses openpyxl for multi-sheet writing with proper formatting.

    Raises:
        ValueError: If filename doesn't end with '.xlsx' or '.xls', or if
            filename is None and sample.file_path not set.
        Warning: If features_df is None (no data to export).

    See Also:
        export_csv: Export features to CSV format.
        export_mgf: Export MS2 spectra to MGF format.
        get_id: Retrieve identification results for export.
        save: Save complete sample object to HDF5.
    """
    if self.features_df is None:
        self.logger.warning("No features found. Cannot export to Excel.")
        return

    # Handle None filename by using sample.file_path
    if filename is None:
        if self.file_path is None:
            raise ConfigurationError(
                "Cannot export to Excel: no filename provided and sample.file_path is not set.\n\n"
                "Please provide a filename:\n"
                "  sample.export_xlsx(filename='features.xlsx')",
            )
        # Replace extension with .xlsx
        base_path = os.path.splitext(self.file_path)[0]
        filename = f"{base_path}.xlsx"
        self.logger.debug(f"filename not provided, using sample file path: {filename}")

    # Validate filename extension
    if not filename.lower().endswith((".xlsx", ".xls")):
        current_ext = os.path.splitext(filename)[1] or "(no extension)"
        raise FileFormatError(
            f"Invalid file extension for Excel export: {current_ext}\n\n"
            f"Filename: {filename}\n"
            "Supported extensions: .xlsx, .xls\n\n"
            "Example: sample.export_xlsx(filename='features.xlsx')",
        )

    filename = os.path.abspath(filename)

    # Clone the DataFrame to avoid modifying the original
    clean_df = self.features_df.clone()

    # Add a column has_ms2=True if column ms2_scans is not None
    if "ms2_scans" in clean_df.columns:
        clean_df = clean_df.with_columns(
            (pl.col("ms2_scans").is_not_null()).alias("has_ms2"),
        )

    # Filter out columns with List or Object data types that can't be exported to Excel
    exportable_columns = [
        col
        for col in clean_df.columns
        if clean_df[col].dtype not in (pl.List, pl.Object)
    ]

    clean_df = clean_df.select(exportable_columns)

    # Convert to pandas
    pandas_df = clean_df.to_pandas()

    # Check if we have identification data to export
    has_id_data = (
        hasattr(self, "id_df") and self.id_df is not None and not self.id_df.is_empty()
    )

    # Check if we have history to export
    has_history = (
        hasattr(self, "history") and self.history is not None and bool(self.history)
    )

    # Always use ExcelWriter if we have id_data or history
    if has_id_data or has_history:
        # Export multiple sheets using ExcelWriter
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            # Export features to 'features' sheet
            pandas_df.to_excel(writer, sheet_name="features", index=False)

            # Get identification data and export to 'id' sheet
            if has_id_data:
                id_data = self.get_id()
                if id_data is not None and not id_data.is_empty():
                    # Filter out columns with List or Object data types
                    id_exportable_columns = [
                        col
                        for col in id_data.columns
                        if id_data[col].dtype not in (pl.List, pl.Object)
                    ]
                    id_clean = id_data.select(id_exportable_columns)
                    id_pandas = id_clean.to_pandas()
                    id_pandas.to_excel(writer, sheet_name="id", index=False)
                    self.logger.debug(f"Exported {len(id_clean)} identifications")

            # Export history to 'history' sheet
            if has_history:
                import json

                history_rows = []

                # Add sample parameters as the first entries if available
                if hasattr(self, "parameters") and self.parameters is not None:
                    params_dict = self.parameters.to_dict()
                    for subkey, subvalue in params_dict.items():
                        history_rows.append(
                            {
                                "category": "parameters",
                                "parameter": subkey,
                                "value": json.dumps(subvalue)
                                if isinstance(subvalue, (dict, list))
                                else str(subvalue),
                            },
                        )

                # Add all history entries
                for key, value in self.history.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            history_rows.append(
                                {
                                    "category": key,
                                    "parameter": subkey,
                                    "value": json.dumps(subvalue)
                                    if isinstance(subvalue, (dict, list))
                                    else str(subvalue),
                                },
                            )
                    else:
                        history_rows.append(
                            {
                                "category": key,
                                "parameter": "",
                                "value": json.dumps(value)
                                if isinstance(value, (dict, list))
                                else str(value),
                            },
                        )

                if history_rows:
                    history_pandas = pd.DataFrame(history_rows)
                    history_pandas.to_excel(writer, sheet_name="history", index=False)
                    self.logger.debug(f"Exported {len(history_rows)} history entries")

            self.logger.success(f"Sample exported to {filename} (Excel format)")
            self.logger.debug(f"Exported {len(clean_df)} features")
    else:
        # No identification data or history, export features only
        pandas_df.to_excel(filename, index=False)
        self.logger.success(f"Features exported to {filename} (Excel format)")
        self.logger.debug(
            f"Exported {len(clean_df)} features with {len(exportable_columns)} columns",
        )


def export_csv(self, filename="features.csv"):
    """Export features DataFrame to CSV file in SLAW-compatible format.

    Exports comprehensive feature information including m/z, RT, adduct annotations,
    isotopic patterns, MS2 data, and intensity values. Output format is compatible
    with SLAW (Scalable Automated Workflow) specifications.

    Args:
        filename (str): Output CSV file path. Defaults to "features.csv".

    Example:
        ::\

            from masster import Sample

            # Process sample and export
            s = Sample(file="data.mzML")
            s.find_features()
            s.find_adducts()
            s.export_csv()

            # Export to specific path
            s.export_csv("results/sample_features.csv")

            # Load exported CSV
            import pandas as pd
            features = pd.read_csv("features.csv")
            print(features.columns)

    Note:
        **SLAW Compatibility:**

        Output columns follow SLAW specification:\n
        - feature_id: UUID7 string (stable across operations)\n        - mz, rt: Mass and retention time\n        - group: Adduct group identifier\n        - annotation: Adduct + isotope (e.g., "M+H", "M+H +1")\n        - neutral_mass, charge: Calculated from adduct\n        - main_id: Primary feature identifier\n        - ion, iso: Adduct and isotope information\n        - num_detection, total_detection: Sample counts (always 1 for single sample)\n        - mz_mean/min/max: m/z statistics\n        - rt_mean/min/max: RT window (rt_start to rt_end)\n        - height_mean/min/max: Peak height\n        - intensity_mean/min/max: Integrated intensity\n        - SN_mean/min/max: Signal-to-noise ratio\n        - peakwidth_mean/min/max: Peak width (seconds)\n        - ms2_mgf_id: MGF spectrum identifier\n        - ms2_num_fused: Number of MS2 scans per feature\n        - isotopic_pattern_*: Isotope pattern annotations\n        - quant_{sample_name}.csv: Quantification column

        **Charge Handling:**

        Automatically assigns charge based on sample polarity if adduct_charge is
        missing or zero: +1 for positive mode, -1 for negative mode.

        **Grouping:**

        Features are grouped by adduct_group. Features without a group (adduct_group=0)
        are assigned unique group indices starting from max(adduct_group) + 1.

        **Annotation Logic:**

        Annotations combine adduct and isotope information:\n
        - Monoisotopic (iso=0): Uses adduct only (e.g., "M+H")\n        - Isotopes (iso>0): Adds isotope number (e.g., "M+H +1", "M+H +2")

        **MS2 Integration:**

        If MS2 data available, exports ms2_mgf_id and number of fused MS2 scans.

        **Quantification Column:**

        Column name format: quant_{sample_name}.csv where sample_name is extracted
        from file_path (or "sample" if file_path not set).

    See Also:
        - :meth:`export_excel`: Export to multi-sheet Excel workbook
        - :meth:`export_mgf`: Export MS2 spectra to MGF format
        - :meth:`find_adducts`: Detect adduct groups before export
    """
    if self.features_df is None:
        self.logger.warning("No features found. Cannot export features.")
        return

    filename = os.path.abspath(filename)

    # Get base filename for quant column
    if self.file_path is not None:
        base_name = os.path.splitext(os.path.basename(self.file_path))[0]
    else:
        base_name = "sample"

    quant_column_name = f"quant_{base_name}.csv"

    # Prepare the SLAW dataframe with required columns
    import polars as pl

    df = self.features_df

    # Evaluate the charge column first if adduct_charge exists
    if "adduct_charge" in df.columns:
        charge_series = df.select(
            pl.when(pl.col("adduct_charge") == 0)
            .then(1 if self.polarity == "positive" else -1)
            .otherwise(pl.col("adduct_charge"))
            .alias("charge"),
        ).get_column("charge")
    else:
        charge_series = pl.Series([1 if self.polarity == "positive" else -1] * len(df))

    # Evaluate the group column (from adduct_group)
    # Features with adduct_group == 0 should each get a unique group index
    if "adduct_group" in df.columns:
        max_adduct_group = df.get_column("adduct_group").max()
        if max_adduct_group is None:
            max_adduct_group = 0

        # Create a row number starting from max_adduct_group + 1 for features with adduct_group == 0
        group_series = df.select(
            pl.when(pl.col("adduct_group") == 0)
            .then(
                max_adduct_group
                + 1
                + pl.int_range(pl.len()).over(pl.col("adduct_group") == 0),
            )
            .otherwise(pl.col("adduct_group"))
            .alias("group"),
        ).get_column("group")
    else:
        group_series = pl.Series([None] * len(df))

    # Evaluate the annotation column (adduct + isotope info)
    # annotation = adduct for iso==0, adduct + " +{iso}" for iso>0
    if "adduct" in df.columns and "iso" in df.columns:
        annotation_series = df.select(
            pl.when(pl.col("iso") == 0)
            .then(pl.col("adduct").str.replace(r"\?", "H"))
            .otherwise(
                pl.col("adduct").str.replace(r"\?", "H")
                + " +"
                + pl.col("iso").cast(pl.Utf8),
            )
            .alias("annotation"),
        ).get_column("annotation")
    elif "adduct" in df.columns:
        annotation_series = df.get_column("adduct").str.replace(r"\?", "H")
    else:
        annotation_series = pl.Series([""] * len(df))

    # Create SLAW columns with appropriate mappings from features_df
    # Columns are ordered according to SLAW specification
    slaw_data = {
        "feature_id": df.get_column("feature_uid")
        if "feature_uid" in df.columns
        else pl.Series([None] * len(df)),
        "mz": df.get_column("mz")
        if "mz" in df.columns
        else pl.Series([None] * len(df)),
        "rt": df.get_column("rt")
        if "rt" in df.columns
        else pl.Series([None] * len(df)),
        "group": group_series,
        "annotation": annotation_series,
        "neutral_mass": df.get_column("adduct_neutral_mass")
        if "adduct_neutral_mass" in df.columns
        else pl.Series([None] * len(df)),
        "charge": charge_series,
        "main_id": df.get_column("main_id")
        if "main_id" in df.columns
        else df.get_column("feature_id")
        if "feature_id" in df.columns
        else pl.Series(range(1, len(df) + 1)),
        "ion": df.get_column("adduct").str.replace(r"\?", "H")
        if "adduct" in df.columns
        else pl.Series([""] * len(df)),
        "iso": df.get_column("iso")
        if "iso" in df.columns
        else pl.Series([0] * len(df)),
        "clique": df.get_column("clique")
        if "clique" in df.columns
        else pl.Series([None] * len(df)),
        "num_detection": pl.Series([1] * len(df)),  # Single sample always 1
        "total_detection": pl.Series([1] * len(df)),  # Single sample always 1
        "mz_mean": df.get_column("mz")
        if "mz" in df.columns
        else pl.Series([None] * len(df)),
        "mz_min": df.get_column("mz")
        if "mz" in df.columns
        else pl.Series([None] * len(df)),
        "mz_max": df.get_column("mz")
        if "mz" in df.columns
        else pl.Series([None] * len(df)),
        "rt_mean": df.get_column("rt")
        if "rt" in df.columns
        else pl.Series([None] * len(df)),
        "rt_min": df.get_column("rt_start")
        if "rt_start" in df.columns
        else df.get_column("rt")
        if "rt" in df.columns
        else pl.Series([None] * len(df)),
        "rt_max": df.get_column("rt_end")
        if "rt_end" in df.columns
        else df.get_column("rt")
        if "rt" in df.columns
        else pl.Series([None] * len(df)),
        "rt_cor_mean": df.get_column("rt")
        if "rt" in df.columns
        else pl.Series([None] * len(df)),
        "rt_cor_min": df.get_column("rt_start")
        if "rt_start" in df.columns
        else df.get_column("rt")
        if "rt" in df.columns
        else pl.Series([None] * len(df)),
        "rt_cor_max": df.get_column("rt_end")
        if "rt_end" in df.columns
        else df.get_column("rt")
        if "rt" in df.columns
        else pl.Series([None] * len(df)),
        "height_mean": df.get_column("height")
        if "height" in df.columns
        else pl.Series([None] * len(df)),
        "height_min": df.get_column("height")
        if "height" in df.columns
        else pl.Series([None] * len(df)),
        "height_max": df.get_column("height")
        if "height" in df.columns
        else pl.Series([None] * len(df)),
        "intensity_mean": df.get_column("inty")
        if "inty" in df.columns
        else pl.Series([None] * len(df)),
        "intensity_min": df.get_column("inty")
        if "inty" in df.columns
        else pl.Series([None] * len(df)),
        "intensity_max": df.get_column("inty")
        if "inty" in df.columns
        else pl.Series([None] * len(df)),
        "SN_mean": df.get_column("sn")
        if "sn" in df.columns
        else pl.Series([None] * len(df)),
        "SN_min": df.get_column("sn")
        if "sn" in df.columns
        else pl.Series([None] * len(df)),
        "SN_max": df.get_column("sn")
        if "sn" in df.columns
        else pl.Series([None] * len(df)),
        "peakwidth_mean": (df.get_column("rt_end") - df.get_column("rt_start"))
        if ("rt_end" in df.columns and "rt_start" in df.columns)
        else pl.Series([None] * len(df)),
        "peakwidth_min": (df.get_column("rt_end") - df.get_column("rt_start"))
        if ("rt_end" in df.columns and "rt_start" in df.columns)
        else pl.Series([None] * len(df)),
        "peakwidth_max": (df.get_column("rt_end") - df.get_column("rt_start"))
        if ("rt_end" in df.columns and "rt_start" in df.columns)
        else pl.Series([None] * len(df)),
        "ms2_mgf_id": df.get_column("ms2_mgf_id")
        if "ms2_mgf_id" in df.columns
        else pl.Series([""] * len(df)),
        "ms2_num_fused": df.get_column("ms2_scans").list.len()
        if "ms2_scans" in df.columns and df["ms2_scans"].dtype == pl.List
        else pl.Series([None] * len(df)),
        "ms2_source": df.get_column("ms2_source")
        if "ms2_source" in df.columns
        else pl.Series([""] * len(df)),
        "isotopic_pattern_annot": df.get_column("isotopic_pattern_annot")
        if "isotopic_pattern_annot" in df.columns
        else pl.Series([""] * len(df)),
        "isotopic_pattern_rel": df.get_column("isotopic_pattern_rel")
        if "isotopic_pattern_rel" in df.columns
        else pl.Series([""] * len(df)),
        "isotopic_pattern_abs": df.get_column("isotopic_pattern_abs")
        if "isotopic_pattern_abs" in df.columns
        else pl.Series([""] * len(df)),
        quant_column_name: df.get_column("inty")
        if "inty" in df.columns
        else pl.Series([None] * len(df)),
    }

    # Create the polars DataFrame
    slaw_df = pl.DataFrame(slaw_data)

    # Convert to pandas for CSV export with comma separator
    pandas_df = slaw_df.to_pandas()

    # Export to CSV with comma separator - only quote when necessary (QUOTE_MINIMAL)
    try:
        pandas_df.to_csv(
            filename,
            sep=",",
            index=False,
            quoting=0,
        )  # quoting=0 means QUOTE_MINIMAL
        self.logger.success(f"Features exported to {filename}")
        self.logger.debug(
            f"Exported {len(slaw_df)} features with {len(slaw_df.columns)} columns",
        )
    except PermissionError:
        self.logger.error(
            f"Permission denied: Cannot write to {filename}. The file may be open in another program. Please close it and try again.",
        )


def export_chrom(self, filename="chrom.csv"):
    # saves self.chrom_df to a csv file. Remove the scan_id and chrom columns if the file already exists
    if self.chrom_df is None:
        self.logger.warning("No chromatogram definitions found.")
        return
    data = self.chrom_df.clone()
    # Convert to pandas for CSV export
    if hasattr(data, "to_pandas"):
        data = data.to_pandas()
    # remove scan_id and chrom columns if they exist
    if "scan_id" in data.columns:
        data = data.drop("scan_id")
    if "chrom" in data.columns:
        data = data.drop("chrom")
    data.to_csv(filename, index=False)


def export_mztab(
    self,
    filename=None,
    title=None,
    description=None,
    include_mgf=False,
    **kwargs,
):
    """
    Export the sample as a fully compliant mzTab-M file.

    Args:
        filename (str, optional): Path to the output mzTab-M file. Defaults to "sample.mztab".
        title (str, optional): Human-readable title for the file.
        description (str, optional): Human-readable description.
        include_mgf (bool, optional): Include MGF table with MS2 spectra. Defaults to False.
        **kwargs: Additional metadata or export options.
    """
    from masster._version import __version__

    def safe_str(value, default="null"):
        """Convert value to string, replacing empty strings with 'null'"""
        if value is None:
            return default
        str_val = str(value)
        return str_val if str_val.strip() != "" else default

    if filename is None:
        filename = "sample.mztab"
    if not os.path.isabs(filename):
        filename = os.path.abspath(filename)

    # Get identification data if available using get_id() function
    top_id_data = None
    full_id_data = None

    try:
        # Import get_id function from sample.id module
        from masster.sample.id import get_id

        # Get full enriched identification data
        full_id_data = get_id(self)
        if full_id_data is not None and not full_id_data.is_empty():
            # Get top scoring identification for each feature_id for SML section
            top_id_data = (
                full_id_data.group_by("feature_id")
                .agg(pl.all().sort_by("score", descending=True).first())
                .sort("feature_id")
            )
            # Keep raw id_data for backward compatibility (if needed elsewhere)
            self.id_df if hasattr(self, "id_df") and self.id_df is not None else None
        else:
            self.logger.info("No identification data available for mzTab export")
    except Exception as e:
        self.logger.debug(f"Could not retrieve identification data: {e}")
        top_id_data = None
        full_id_data = None

    # Get MGF data only if requested
    mgf_data = None
    mgf_mapping: dict[int, list[int]] = {}
    if include_mgf:
        # Create MGF data from features_df
        if self.features_df is not None:
            mgf_rows = []
            mgf_index = 1

            for feature_row in self.features_df.iter_rows(named=True):
                feature_id = feature_row["feature_id"]
                feature_id = feature_row.get("feature_id", feature_id)

                # Check if this feature has MS2 scans
                if feature_row.get("ms2_scans") is None:
                    continue

                ms2_scans = feature_row["ms2_scans"]
                if not isinstance(ms2_scans, list):
                    ms2_scans = [ms2_scans]

                # Process each MS2 scan
                for scan_uid in ms2_scans:
                    spec = self.get_spectrum(scan_uid)
                    if spec is None or len(spec.mz) == 0:
                        continue

                    mgf_row = {
                        "mgf_index": mgf_index,
                        "feature_id": feature_id,
                        "rtinseconds": feature_row.get("rt", 0),
                        "pepmass": feature_row.get("mz", 0),
                        "energy": spec.energy if hasattr(spec, "energy") else 0,
                        "mslevel": spec.ms_level if hasattr(spec, "ms_level") else 2,
                        "title": f"id:{feature_id}, rt:{feature_row.get('rt', 0):.2f}, mz:{feature_row.get('mz', 0):.4f}",
                        "spec_mz": spec.mz,
                        "spec_int": spec.inty,
                        "spec_len": len(spec.mz),
                    }
                    mgf_rows.append(mgf_row)

                    # Track mapping
                    if feature_id not in mgf_mapping:
                        mgf_mapping[feature_id] = []
                    mgf_mapping[feature_id].append(mgf_index)

                    mgf_index += 1

            if mgf_rows:
                mgf_data = pl.DataFrame(mgf_rows)

    # --- Prepare MTD (metadata) section ---
    mtd_lines = []
    mtd_lines.append(
        f"COM\tfile generated by MASSter {__version__} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    )
    mtd_lines.append("\nMTD\tmzTab-version\t2.2.0-M")

    # Use sample name or filename as mzTab-id
    sample_name = (
        getattr(self, "label", None)
        or os.path.splitext(os.path.basename(self.file_path))[0]
        if hasattr(self, "file_path") and self.file_path
        else "sample"
    )
    mtd_lines.append(f"MTD\tmzTab-id\t{sample_name}")
    mtd_lines.append("")

    # CV definitions
    mtd_lines.append("MTD\tcv[1]-label\tMS")
    mtd_lines.append("MTD\tcv[1]-full_name\tPSI-MS controlled vocabulary")
    mtd_lines.append("MTD\tcv[1]-version\t4.1.199")
    mtd_lines.append(
        "MTD\tcv[1]-uri\thttps://raw.githubusercontent.com/HUPO-PSI/psi-ms-CV/master/psi-ms.obo",
    )
    mtd_lines.append("")

    # Quantification units
    mtd_lines.append(
        "MTD\tsmall_molecule-quantification_unit\t[MS, MS:1001844, MS1 feature area, ]",
    )
    mtd_lines.append(
        "MTD\tsmall_molecule_feature-quantification_unit\t[MS, MS:1001844, MS1 feature area, ]",
    )
    mtd_lines.append(
        "MTD\tsmall_molecule-identification_reliability\t[MS, MS:1002955, hr-ms compound identification confidence level, ]",
    )

    # Identification confidence
    mtd_lines.append(
        "MTD\tid_confidence_measure[1]\t[MS, MS:1002888, small molecule confidence measure, ]",
    )
    mtd_lines.append("")

    # Software
    mtd_lines.append("MTD\tsoftware[1]\t[MS, MS:1003430, OpenMS, unknown]")
    mtd_lines.append(f"MTD\tsoftware[2]\t[MS, MS:1002878, MASSter, {__version__}]")
    mtd_lines.append(
        "MTD\tquantification_method\t[MS, MS:1001834, LC-MS label-free quantitation analysis, ]",
    )
    mtd_lines.append("")

    # Database information - updated based on identification data
    if (
        full_id_data is not None
        and hasattr(self, "lib_df")
        and self.lib_df is not None
        and not self.lib_df.is_empty()
    ):
        mtd_lines.append('MTD\tdatabase[1]\t[, , "compound library", ]')
        mtd_lines.append("MTD\tdatabase[1]-prefix\tcmpd")
        mtd_lines.append("MTD\tdatabase[1]-version\tUnknown")
        mtd_lines.append("MTD\tdatabase[1]-uri\thttps://pubchem.ncbi.nlm.nih.gov/")
    else:
        mtd_lines.append('MTD\tdatabase[1]\t[, , "PubChem", ]')
        mtd_lines.append("MTD\tdatabase[1]-prefix\tCID")
        mtd_lines.append("MTD\tdatabase[1]-version\tUnknown")
        mtd_lines.append("MTD\tdatabase[1]-uri\thttps://pubchem.ncbi.nlm.nih.gov/")

    # Single sample metadata
    mtd_lines.append(f"\nMTD\tsample[1]\t{sample_name}")
    mtd_lines.append(f"MTD\tsample[1]-description\t{sample_name}")
    mtd_lines.append("MTD\tms_run[1]-location\tfile://unknown")

    # Scan polarity
    sample_polarity = getattr(self, "polarity", "positive")
    if sample_polarity in ["negative", "neg"]:
        scan_polarity_cv = "[MS, MS:1000129, negative scan, ]"
    else:
        scan_polarity_cv = "[MS, MS:1000130, positive scan, ]"
    mtd_lines.append(f"MTD\tms_run[1]-scan_polarity\t{scan_polarity_cv}")

    mtd_lines.append("MTD\tassay[1]\tAssay_1")
    mtd_lines.append("MTD\tassay[1]-sample_ref\tsample[1]")
    mtd_lines.append("MTD\tassay[1]-ms_run_ref\tms_run[1]")
    mtd_lines.append("")
    mtd_lines.append("MTD\tstudy_variable[1]\tundefined")
    mtd_lines.append("MTD\tstudy_variable[1]-assay_refs\tassay[1]")
    mtd_lines.append("MTD\tstudy_variable[1]-description\tSingle sample")

    with open(filename, "w", encoding="utf-8") as f:
        for line in mtd_lines:
            f.write(line + "\n")

    # --- SML (Small Molecule) table ---
    sml_lines = []
    sml_header = [
        "SMH",
        "SML_ID",
        "SMF_ID_REFS",
        "database_identifier",
        "chemical_formula",
        "smiles",
        "inchi",
        "chemical_name",
        "uri",
        "theoretical_neutral_mass",
        "adduct_ions",
        "reliability",
        "best_id_confidence_measure",
        "best_id_confidence_value",
        "opt_global_mgf_index",
        "abundance_assay[1]",
        "abundance_study_variable[1]",
        "abundance_variation_study_variable[1]",
    ]
    sml_lines.append("\t".join(sml_header))

    # Get adducts from features_df['adduct']
    adduct_list = []
    for row in self.features_df.iter_rows(named=True):
        adduct = "null"
        if "adduct" in row and row["adduct"] is not None:
            adduct = str(row["adduct"]).replace("?", "H")
        adduct_list.append(adduct)

    for idx, row in enumerate(self.features_df.iter_rows(named=True), 1):
        feature_id = row["feature_id"]

        # Get identification information for this feature_id if available
        id_info = None
        if top_id_data is not None:
            id_matches = top_id_data.filter(pl.col("feature_id") == feature_id)
            if id_matches.height > 0:
                id_info = id_matches.row(0, named=True)

        # Populate identification fields
        database_identifier = "null"
        chemical_formula = "null"
        smiles_val = "null"
        inchi_val = "null"
        chemical_name = "null"
        best_id_confidence_measure = "null"
        best_id_confidence_value = "null"
        reliability = "4"  # Default: unknown compound
        theoretical_neutral_mass = "null"

        if id_info:
            # Use cmpd_id as database identifier with prefix
            if id_info.get("cmpd_id") is not None:
                database_identifier = f"cmpd:{id_info['cmpd_id']}"

            # Chemical formula
            if id_info.get("formula") is not None and id_info["formula"] != "":
                chemical_formula = safe_str(id_info["formula"])

            # SMILES
            if id_info.get("smiles") is not None and id_info["smiles"] != "":
                smiles_val = safe_str(id_info["smiles"])

            # InChI
            if id_info.get("inchi") is not None and id_info["inchi"] != "":
                inchi_val = safe_str(id_info["inchi"])

            # Chemical name
            if id_info.get("name") is not None and id_info["name"] != "":
                chemical_name = safe_str(id_info["name"])

            # Theoretical neutral mass
            if id_info.get("neutral_mass") is not None:
                theoretical_neutral_mass = safe_str(id_info["neutral_mass"])
            elif id_info.get("mass") is not None:
                theoretical_neutral_mass = safe_str(id_info["mass"])

            # Identification confidence
            if id_info.get("matcher") is not None:
                best_id_confidence_measure = f"[MS, MS:1002888, {id_info['matcher']}, ]"

            if id_info.get("score") is not None:
                best_id_confidence_value = safe_str(id_info["score"])

            # Set reliability based on identification quality
            if id_info.get("score", 0) >= 0.8:
                reliability = "2a"  # High confidence compound match
            elif id_info.get("score", 0) >= 0.5:
                reliability = "2b"  # Moderate confidence match
            elif id_info.get("score", 0) >= 0.2:
                reliability = "3"  # Compound class level
            else:
                reliability = "4"  # Unknown compound

        # Get MGF indexes for this feature
        mgf_indexes = mgf_mapping.get(feature_id, [])

        # Get intensity value for abundance
        abundance_value = row.get("inty", None)
        abundance_str = (
            safe_str(abundance_value) if abundance_value is not None else "null"
        )

        sml_row = [
            "SML",
            str(idx),
            str(idx),  # SMF_ID_REFS - same as SML_ID for single features
            database_identifier,
            chemical_formula,
            smiles_val,
            inchi_val,
            chemical_name,
            safe_str(row.get("uri", "null")),
            theoretical_neutral_mass,
            adduct_list[idx - 1],
            reliability,
            best_id_confidence_measure,
            best_id_confidence_value,
            ",".join(map(str, mgf_indexes)) if mgf_indexes else "null",
            abundance_str,  # abundance_assay[1]
            abundance_str,  # abundance_study_variable[1] (same for single sample)
            "null",  # abundance_variation_study_variable[1] (no variation for single sample)
        ]
        sml_lines.append("\t".join(sml_row))

    with open(filename, "a", encoding="utf-8") as f:
        f.write("\n")
        for line in sml_lines:
            f.write(line + "\n")

    # --- SMF (Small Molecule Feature) table ---
    smf_lines = []
    smf_header = [
        "SFH",
        "SMF_ID",
        "SME_ID_REFS",
        "SME_ID_REF_ambiguity_code",
        "adduct_ion",
        "isotopomer",
        "exp_mass_to_charge",
        "charge",
        "retention_time_in_seconds",
        "retention_time_in_seconds_start",
        "retention_time_in_seconds_end",
        "abundance_assay[1]",
        "abundance_study_variable[1]",
        "abundance_variation_study_variable[1]",
    ]
    smf_lines.append("\t".join(smf_header))

    for idx, row in enumerate(self.features_df.iter_rows(named=True), 1):
        feature_id = row["feature_id"]

        # References to SME entries
        SME_refs = "null"
        SME_ambiguity = "null"

        if full_id_data is not None:
            # Find all SME entries for this feature_id
            SME_matches = full_id_data.filter(pl.col("feature_id") == feature_id)
            if SME_matches.height > 0:
                # Generate SME IDs
                SME_ids = []
                for i, SME_row in enumerate(SME_matches.iter_rows(named=True)):
                    SME_id_base = feature_id * 1000
                    SME_id = SME_id_base + i + 1
                    SME_ids.append(str(SME_id))

                if SME_ids:
                    SME_refs = "|".join(SME_ids)
                    # Set ambiguity code
                    if len(SME_ids) > 1:
                        unique_cmpds = {
                            match["cmpd_id"]
                            for match in SME_matches.iter_rows(named=True)
                            if match.get("cmpd_id") is not None
                        }
                        if len(unique_cmpds) > 1:
                            SME_ambiguity = "1"  # Ambiguous identification
                        else:
                            SME_ambiguity = "2"  # Multiple evidence for same molecule
                    else:
                        SME_ambiguity = "null"

        # Format isotopomer
        iso_value = row.get("iso", 0)
        if iso_value is not None and round(iso_value) != 0:
            isotopomer = f'[MS,MS:1002957,"isotopomer MS peak","+{round(iso_value)}"]'
        else:
            isotopomer = "null"

        # Get abundance value
        abundance_value = row.get("inty", None)
        abundance_str = (
            safe_str(abundance_value) if abundance_value is not None else "null"
        )

        smf_row = [
            "SMF",
            str(idx),
            SME_refs,
            SME_ambiguity,
            adduct_list[idx - 1],  # adduct_ion
            isotopomer,
            safe_str(row.get("mz", "null")),  # exp_mass_to_charge
            safe_str(
                f"{abs(row.get('charge', 1))}+"
                if row.get("charge", 1) >= 0
                else f"{abs(row.get('charge', 1))}-",
            )
            if row.get("charge") is not None and row.get("charge") != "null"
            else "null",  # charge with sign
            safe_str(row.get("rt", "null")),  # retention_time_in_seconds
            safe_str(row.get("rt_start", "null")),
            safe_str(row.get("rt_end", "null")),
            abundance_str,  # abundance_assay[1]
            abundance_str,  # abundance_study_variable[1]
            "null",  # abundance_variation_study_variable[1]
        ]
        smf_lines.append("\t".join(smf_row))

    with open(filename, "a", encoding="utf-8") as f:
        f.write("\n")
        for line in smf_lines:
            f.write(line + "\n")

    # --- SME (Small Molecule Evidence) table ---
    if full_id_data is not None and not full_id_data.is_empty():
        SME_lines = []
        SME_lines.append(
            "COM\tThe spectra_ref are dummy placeholders, as the annotation was based on aggregated data",
        )
        SME_header = [
            "SEH",
            "SME_ID",
            "evidence_input_id",
            "database_identifier",
            "chemical_formula",
            "smiles",
            "inchi",
            "chemical_name",
            "uri",
            "derivatized_form",
            "adduct_ion",
            "exp_mass_to_charge",
            "charge",
            "theoretical_mass_to_charge",
            "spectra_ref",
            "identification_method",
            "ms_level",
            "id_confidence_measure[1]",
            "rank",
        ]
        SME_lines.append("\t".join(SME_header))

        # Create SME entries for all identification results
        for feature_id in self.features_df.select("feature_id").to_series().unique():
            # Get feature data
            feature_data = self.features_df.filter(pl.col("feature_id") == feature_id)
            if feature_data.height == 0:
                continue
            feature_row = feature_data.row(0, named=True)

            # Get all identification results for this feature
            SME_matches = full_id_data.filter(pl.col("feature_id") == feature_id)

            if SME_matches.height > 0:
                # Sort by score descending
                SME_matches = SME_matches.sort("score", descending=True)

                for i, SME_row in enumerate(SME_matches.iter_rows(named=True)):
                    # Generate unique SME_ID
                    SME_id_base = feature_id * 1000
                    SME_id = SME_id_base + i + 1

                    # Create evidence input ID
                    feature_mz = feature_row.get("mz", 0)
                    feature_rt = feature_row.get("rt", 0)
                    feature_id = feature_row.get("feature_id", feature_id)
                    evidence_id = f"feature_id={feature_id}:feature_id={feature_id}:mz={feature_mz:.4f}:rt={feature_rt:.2f}"

                    # Database identifier
                    db_id = "null"
                    if SME_row.get("db_id") is not None and SME_row["db_id"] != "":
                        db_id = safe_str(SME_row["db_id"])
                    elif SME_row.get("cmpd_id") is not None:
                        db_id = f"cmpd:{SME_row['cmpd_id']}"

                    # Get adduct information
                    adduct_ion = "null"
                    if SME_row.get("adduct") is not None and SME_row["adduct"] != "":
                        adduct_ion = safe_str(SME_row["adduct"]).replace("?", "H")

                    # Spectra reference
                    spectra_ref = "ms_run[1]:spectrum=0"

                    # Identification method
                    id_method = "[MS, MS:1002888, small molecule confidence measure, ]"
                    if SME_row.get("matcher") is not None:
                        id_method = f"[MS, MS:1002888, {SME_row['matcher']}, ]"

                    # MS level - check if ms1 exists in matched
                    if "ms1" in SME_row["matcher"].lower():
                        ms_level = "[MS, MS:1000511, ms level, 1]"
                    else:
                        ms_level = "[MS,MS:1000511, ms level, 2]"

                    # Experimental mass-to-charge
                    exp_mz = safe_str(feature_mz)

                    # Theoretical mass-to-charge
                    theoretical_mz = "null"
                    if SME_row.get("mz") is not None:
                        theoretical_mz = safe_str(SME_row["mz"])

                    SME_line = [
                        "SME",
                        str(SME_id),
                        evidence_id,
                        db_id,
                        safe_str(SME_row.get("formula", "null")),
                        safe_str(SME_row.get("smiles", "null")),
                        safe_str(SME_row.get("inchi", "null")),
                        safe_str(SME_row.get("name", "null")),
                        "null",  # uri
                        "null",  # derivatized_form
                        adduct_ion,
                        exp_mz,
                        safe_str(
                            f"{abs(feature_row.get('charge', 1))}+"
                            if feature_row.get("charge", 1) >= 0
                            else f"{abs(feature_row.get('charge', 1))}-",
                        )
                        if feature_row.get("charge") is not None
                        and feature_row.get("charge") != "null"
                        else "1+",  # charge with sign
                        theoretical_mz,
                        spectra_ref,
                        id_method,
                        ms_level,
                        safe_str(SME_row.get("score", "null")),
                        str(i + 1),  # rank
                    ]
                    SME_lines.append("\t".join(SME_line))

        # Write SME table
        with open(filename, "a", encoding="utf-8") as f:
            f.write("\n")
            for line in SME_lines:
                f.write(line + "\n")

    # --- MGF table ---
    if include_mgf and mgf_data is not None and len(mgf_data) > 0:
        mgf_lines = []
        # Header
        mgf_header = [
            "COM",
            "MGH",
            "mgf_id",
            "prec_id",
            "prec_rt",
            "prec_mz",
            "prec_int",
            "energy",
            "level",
            "title",
            "spec_tic",
            "spec_len",
            "spec_mz",
            "spec_int",
        ]
        mgf_lines.append("\t".join(mgf_header))

        # Data rows
        for row in mgf_data.iter_rows(named=True):
            # Calculate spectrum TIC
            spectrum_mz = row["spec_mz"]
            spectrum_inty = row["spec_int"]
            spec_tic = sum(spectrum_inty) if spectrum_inty else 0
            spec_len = row["spec_len"] if row["spec_len"] is not None else 0

            # Format spectrum data as pipe-separated strings
            spec_mz_str = (
                "|".join([f"{mz:.4f}" for mz in spectrum_mz]) if spectrum_mz else ""
            )
            spec_int_str = (
                "|".join([f"{int(inty)}" for inty in spectrum_inty])
                if spectrum_inty
                else ""
            )

            mgf_row = [
                "COM",
                "MGF",
                str(row["mgf_index"]) if row["mgf_index"] is not None else "null",
                str(row["feature_id"]) if row["feature_id"] is not None else "null",
                f"{row['rtinseconds']:.2f}"
                if row["rtinseconds"] is not None
                else "null",
                f"{row['pepmass']:.4f}" if row["pepmass"] is not None else "null",
                "null",  # prec_int
                str(row["energy"]) if row["energy"] is not None else "null",
                str(row["mslevel"]) if row["mslevel"] is not None else "null",
                str(row["title"]) if row["title"] is not None else "null",
                f"{int(spec_tic)}" if spec_tic > 0 else "null",
                str(spec_len) if spec_len > 0 else "null",
                spec_mz_str if spec_mz_str else "null",
                spec_int_str if spec_int_str else "null",
            ]
            mgf_lines.append("\t".join(mgf_row))

        # Write MGF table
        with open(filename, "a", encoding="utf-8") as f:
            f.write("\n")
            for line in mgf_lines:
                f.write(line + "\n")

    self.logger.success(f"Exported mzTab-M to {filename}")


def export_history(self, filename: str | None = None) -> None:
    """
    Export the processing history as a JSON file.

    The history dict contains all important processing steps that have been applied
    to the sample, including parameters and timestamps.

    Args:
        filename (str, optional): Path to the output JSON file. Defaults to "history.json"
                                 in the sample folder if available, otherwise current directory.
    """
    # Set default filename
    if filename is None:
        filename = "history.json"

    # Make filename absolute if not already
    if not os.path.isabs(filename):
        # Try to use sample folder if available
        if hasattr(self, "folder") and self.folder is not None:
            filename = os.path.join(self.folder, filename)
        else:
            filename = os.path.join(os.getcwd(), filename)

    # Check if history exists and has content
    if not hasattr(self, "history") or self.history is None:
        self.logger.warning("No history available to export")
        return

    if not self.history:
        self.logger.warning("History is empty, nothing to export")
        return

    # Prepare history with parameters at the top
    export_dict = {}

    # Add sample parameters as the first entry if available
    if hasattr(self, "parameters") and self.parameters is not None:
        export_dict["parameters"] = self.parameters.to_dict()

    # Add all history entries
    export_dict.update(self.history)

    # Write history to JSON file
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_dict, f, indent=2, ensure_ascii=False)

        self.logger.success(f"History exported to {filename}")
        self.logger.debug(f"Exported {len(export_dict)} history entries")
    except Exception as e:
        self.logger.error(f"Error writing history file: {e}")
