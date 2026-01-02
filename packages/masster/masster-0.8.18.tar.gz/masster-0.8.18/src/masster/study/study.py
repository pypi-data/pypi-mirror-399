"""
study.py

Module providing the Study class, the main entry point for multi-sample mass spectrometry
studies. It manages loading and metadata, cross-sample feature alignment, consensus
generation, integration, MS2 association, plotting, exporting, and parameter/history
management.

Main class:
- Study: high-level orchestrator. Key operations include:
    - I/O: load/save .study5, add/add_sample, set_study_folder
    - Processing: align, merge (consensus), fill, integrate, find_ms2, find_iso/reset_iso
    - Selection/filtering: samples_select/delete, features_select/filter/delete,
        consensus_select/filter/delete
    - Retrieval: get_consensus, get_chrom, get_samples, get_*_stats, get_*_matrix
    - Plotting: plot_alignment, plot_samples_pca/umap/2d, plot_tic/bpc/eic, plot_chrom,
        plot_rt_correction, plot_consensus_2d/stats, plot_heatmap
    - Export: export_mgf, export_mztab, export_excel, export_parquet
    - Identification: lib_load, identify, get_id, id_reset, lib_reset
    - Parameters: get/update parameters, update_history


Quickstart:
>>> from masster import Study
>>> s = Study(folder="./study")
>>> s.add("/data/mzML/*.mzML")            # or s.add_sample("sample.mzML", name="S1")
>>> s.align()
>>> s.plot_alignment()
>>> s.merge()
>>> s.export_excel("consensus.parquet")
>>> s.save("project.study5")

Notes:
- This module re-exports many functions from masster.study.* as Study methods.
- Use Study.info() for a concise study summary.
"""

from __future__ import annotations

import importlib
import os
import sys

import polars as pl

from masster.exceptions import (
    ConfigurationError,
    DataValidationError,
    FileFormatError,
)
from masster.logger import MassterLogger
from masster.sample.defaults.find_adducts_def import find_adducts_defaults
from masster.sample.defaults.find_features_def import find_features_defaults
from masster.sample.defaults.get_spectrum_def import get_spectrum_defaults

# Import sample defaults
from masster.sample.defaults.sample_def import sample_defaults
from masster.sample.parameters import update_history

# Study-specific imports
from masster.study.analysis import analyze_umap, diff_add, diff_reset, get_diff
from masster.study.defaults.align_def import align_defaults
from masster.study.defaults.export_def import export_mgf_defaults
from masster.study.defaults.fill_def import fill_defaults
from masster.study.defaults.find_ms2_def import find_ms2_defaults
from masster.study.defaults.integrate_chrom_def import integrate_chrom_defaults
from masster.study.defaults.integrate_def import integrate_defaults
from masster.study.defaults.merge_def import merge_defaults
from masster.study.defaults.study_def import study_defaults
from masster.study.export import (
    export_csv,
    export_excel,
    export_history,
    export_mgf,
    export_mztab,
    export_parquet,
)

# from masster.study.load import _load_features
from masster.study.h5 import _load_ms1, _load_study5, _save_study5
from masster.study.helpers import (
    _get_consensus_ids,
    _get_consensus_uids,
    _get_feature_ids,
    _get_feature_uids,
    _repair_uids,
    align_reset,
    compress,
    consensus_delete,
    consensus_filter,
    consensus_reset,
    consensus_select,
    decompress,
    features_delete,
    features_filter,
    features_select,
    fill_reset,
    get_chrom,
    get_consensus,
    get_consensus_matches,
    get_consensus_matrix,
    get_consensus_stats,
    get_gaps_matrix,
    get_gaps_stats,
    get_orphans,
)
from masster.study.id import (
    _get_adducts,
    get_id,
    id_reset,
    id_update,
    identify,
    lib_compare,
    lib_filter,
    lib_load,
    lib_reset,
    lib_select,
)
from masster.study.importers import import_oracle, import_tima
from masster.study.load import add, add_sample, fill, load
from masster.study.merge import merge
from masster.study.parameters import (
    get_parameters,
    get_parameters_property,
    history_reset,
    history_update,
    parameters_update,
    set_parameters_property,
)
from masster.study.plot import (
    plot_alignment,
    plot_bpc,
    plot_chrom,
    plot_consensus_2d,
    plot_consensus_stats,
    plot_eic,
    plot_features_stats,
    plot_heatmap,
    plot_ms2,
    plot_rt_correction,
    plot_samples_2d,
    plot_samples_pca,
    plot_samples_umap,
    plot_tic,
    plot_volcano,
)
from masster.study.processing import align, find_iso, find_ms2, integrate, iso_reset

# Sample-related imports from samples.py
from masster.study.samples import (
    _get_sample_ids,
    get_samples,
    get_samples_stats,
    metadata_import,
    metadata_reset,
    samples_delete,
    samples_name_reset,
    samples_select,
    set_samples_color,
    set_samples_name,
    set_samples_source,
    set_study_folder,
)
from masster.study.save import save, save_consensus, save_samples

# Warning symbols for info display
_WARNING_SYMBOL = "[!]"  # Yellow warning triangle


class Study:
    """
    Main class for managing and analyzing multi-sample mass spectrometry studies.

    The Study class provides comprehensive tools for handling collections of mass
    spectrometry files, performing cross-sample feature alignment, generating consensus
    features, and conducting study-level analysis and visualization.

    Key Features:
        - Multi-sample data management and metadata handling
        - Cross-sample feature alignment with multiple algorithms
        - Consensus feature generation and merging
        - Gap filling and chromatogram integration
        - MS2 spectrum association and identification
        - Comprehensive visualization and export capabilities
        - Version-tracked parameter history for reproducibility

    Main Attributes:
        folder (str): Default directory for study files and outputs
        samples_df (pl.DataFrame): Sample metadata and statistics
        features_df (pl.DataFrame): Combined features from all samples
        consensus_df (pl.DataFrame): Consensus features after alignment and merging
        consensus_mapping_df (pl.DataFrame): Maps features to consensus features
        consensus_ms2 (pl.DataFrame): MS2 spectra associated with consensus features
        lib_df (pl.DataFrame): Reference library for identification
        id_df (pl.DataFrame): Identification results
        history (dict): Version-tracked processing history

    Core Workflow:
        1. Load samples: add() or add_sample()
        2. Align features: align()
        3. Generate consensus: merge()
        4. Fill gaps: fill()
        5. Integrate: integrate()
        6. Find MS2: find_ms2()
        7. Identify: lib_load(), identify()
        8. Export: export_parquet(), export_excel(), export_mgf()

    Example:
        >>> from masster import Study
        >>> s = Study(folder="./study")
        >>> s.add("/data/mzML/*.mzML")
        >>> s.align()
        >>> s.merge()
        >>> s.fill()
        >>> s.integrate()
        >>> s.find_ms2()
        >>> s.plot_alignment()
        >>> s.export_parquet("results.parquet")
        >>> s.save("project.study5")

    See Also:
        Sample: For individual sample processing
        Wizard: For automated batch processing
    """

    # Defaults class attributes
    study_defaults = study_defaults
    sample_defaults = sample_defaults
    find_features_defaults = find_features_defaults
    find_adducts_defaults = find_adducts_defaults
    find_ms2_defaults = find_ms2_defaults
    get_spectrum_defaults = get_spectrum_defaults
    export_mgf_defaults = export_mgf_defaults
    align_defaults = align_defaults
    merge_defaults = merge_defaults
    integrate_defaults = integrate_defaults
    integrate_chrom_defaults = integrate_chrom_defaults

    def __init__(
        self,
        filename=None,
        **kwargs,
    ):
        """Initialize a Study instance for multi-sample mass spectrometry analysis.

        Creates a new Study object for managing and analyzing multiple mass spectrometry
        samples. Can automatically load an existing .study5 file if provided.

        Args:
            filename (str | None): Path to an existing .study5 file to load. If provided,
                the study is loaded automatically and the folder is set to the file's
                directory. Defaults to None.
            **kwargs: Keyword arguments for study configuration. Options include:

                **Quick Initialization:**
                    folder (str): Default directory for study files and outputs.
                    label (str): Optional identifier for the study.
                    log_level (str): Logging level ("DEBUG", "INFO", "WARNING", "ERROR").
                        Defaults to "INFO".
                    log_label (str): Optional label for log messages.
                    log_sink (str): Log output destination. Defaults to "sys.stdout".

                **Advanced Configuration:**
                    params (study_defaults): Pre-configured parameter object.
                        If provided, other parameters are ignored.

        Example:
            Create new study::

                >>> from masster import Study
                >>> study = Study(folder="./my_study")
                >>> study.add("data/*.mzML")
                >>> study.align()
                >>> study.merge()

            Load existing study::

                >>> study = Study(filename="project.study5")
                >>> study.info()
                >>> study.plot_alignment()

            Advanced configuration::

                >>> from masster.study.defaults import study_defaults
                >>> params = study_defaults(
                ...     folder="./study",
                ...     label="Treatment_Study",
                ...     log_level="DEBUG"
                ... )
                >>> study = Study(params=params)

        Attributes:
            After initialization, the Study object has these key attributes:

            folder (str): Default directory for study operations.
            label (str | None): Study identifier.
            filename (str | None): Path to loaded .study5 file.
            samples_df (pl.DataFrame): Sample metadata and statistics.
            features_df (pl.DataFrame | None): Combined features from all samples.
            consensus_df (pl.DataFrame | None): Consensus features after merging.
            consensus_mapping_df (pl.DataFrame | None): Feature-to-consensus mappings.
            consensus_ms2 (pl.DataFrame | None): MS2 spectra for consensus features.
            lib_df (pl.DataFrame | None): Identification library.
            id_df (pl.DataFrame | None): Identification results.
            matrix_df (pl.DataFrame | None): Quantification matrix.
            parameters (study_defaults): Processing parameters.
            history (dict): Processing history for reproducibility.
            logger (MassterLogger): Instance logger.

        Raises:
            ValueError: If filename is provided but not a .study5 file.
            FileNotFoundError: If filename is provided but file doesn't exist.

        See Also:
            study_defaults: Default parameter configuration.
            Sample: Individual sample processing.
            Wizard: Automated batch processing.
        """
        # ===== PARAMETER INITIALIZATION =====
        auto_load_filename = self._init_parameters(filename, kwargs)

        # ===== DATA STRUCTURES INITIALIZATION =====
        self._init_data_structures()

        # ===== LOGGER INITIALIZATION =====
        self._init_logger()

        # ===== AUTO-LOAD FILE IF PROVIDED =====
        if auto_load_filename is not None:
            self.load(filename=auto_load_filename)

        # ===== SAMPLE CACHE =====
        self._samples_cache = {}

    def _init_parameters(self, filename, kwargs):
        """Initialize parameters and handle filename for auto-loading."""
        # Handle filename parameter for automatic loading
        auto_load_filename = None
        if filename is not None:
            if not filename.endswith(".study5"):
                raise FileFormatError(
                    f"Invalid study file format: {os.path.splitext(filename)[1]}\\n"
                    f"Expected: .study5\\n"
                    f"File: {filename}",
                )
            if not os.path.exists(filename):
                raise FileNotFoundError(
                    f"Study file not found: {filename}\\n"
                    f"Current working directory: {os.getcwd()}\\n"
                    f"Check file path and try again",
                )

            # Set folder to the directory containing the file if not already specified
            if "folder" not in kwargs:
                kwargs["folder"] = os.path.dirname(os.path.abspath(filename))

            auto_load_filename = filename

        # Check if a study_defaults instance was passed
        if "params" in kwargs and isinstance(kwargs["params"], study_defaults):
            params = kwargs.pop("params")
        else:
            # Create default parameters and update with provided values
            params = study_defaults()

            # Update with any provided parameters
            for key, value in kwargs.items():
                if hasattr(params, key):
                    params.set(key, value, validate=True)

        # Store parameter instance and initialize history
        self.filename = None  # Keeps a pointer to study5 whenever it's saved or loaded
        self.parameters = params
        self.history = {}
        self.history_update(["study"], params.to_dict())

        # Set instance attributes (ensure proper string values for logger)
        self.folder = params.folder
        self.label = params.label
        self.log_level = params.log_level.upper() if params.log_level else "INFO"
        self.log_label = params.log_label + " | " if params.log_label else ""
        self.log_sink = params.log_sink

        # Create folder if it doesn't exist
        if self.folder is not None and not os.path.exists(self.folder):
            os.makedirs(self.folder)

        return auto_load_filename

    def _init_data_structures(self):
        """Initialize all data structures used by the Study."""
        # Sample information DataFrame
        self.samples_df = pl.DataFrame(
            {
                "sample_id": [],
                "sample_name": [],
                "sample_path": [],
                "sample_type": [],
                "sample_uid": [],
                "sample_source": [],
                "sample_color": [],
                "sample_group": [],
                "sample_batch": [],
                "sample_sequence": [],
                "num_features": [],
                "num_ms1": [],
                "num_ms2": [],
            },
            schema={
                "sample_id": pl.Int64,
                "sample_name": pl.Utf8,
                "sample_path": pl.Utf8,
                "sample_type": pl.Utf8,
                "sample_uid": pl.Utf8,
                "sample_source": pl.Utf8,
                "sample_color": pl.Utf8,
                "sample_group": pl.Utf8,
                "sample_batch": pl.Int64,
                "sample_sequence": pl.Int64,
                "num_features": pl.Int64,
                "num_ms1": pl.Int64,
                "num_ms2": pl.Int64,
            },
        )

        # Feature-related data structures
        self.features_maps = []
        self.features_df = pl.DataFrame()

        # Consensus-related data structures
        self.consensus_ms2 = pl.DataFrame()
        self.consensus_df = pl.DataFrame()
        self.consensus_map = None
        self.consensus_mapping_df = pl.DataFrame()
        self.alignment_ref_index = None

        # Library and identification data structures
        self.lib_df = pl.DataFrame()  # populated by lib_load
        self.id_df = pl.DataFrame()  # populated by identify

        # Differential analysis data structure
        self.diff_df = None  # populated by diff_add

    def _init_logger(self):
        """Initialize the logger for this Study instance."""
        self.logger = MassterLogger(
            instance_type="study",
            level=self.log_level.upper(),
            label=self.log_label,
            sink=self.log_sink,
        )
        self.logger.debug(f"Study folder: {self.folder}")
        polarity_str = (
            self.parameters.polarity
            if self.parameters.polarity is not None
            else "not set (will be determined from first sample)"
        )
        self.logger.debug(f"Polarity: {polarity_str}")

    # === File I/O Operations ===
    load = load
    save = save
    save_consensus = save_consensus
    save_samples = save_samples
    set_study_folder = set_study_folder
    _load_ms1 = _load_ms1
    _load_study5 = _load_study5
    _save_study5 = _save_study5

    # === Sample Management ===
    add = add
    add_sample = add_sample

    # === Core Processing Operations ===
    align = align
    merge = merge

    find_ms2 = find_ms2
    find_iso = find_iso
    iso_reset = iso_reset
    integrate = integrate

    fill = fill
    # _estimate_rt_original_for_filled_feature = _estimate_rt_original_for_filled_feature

    # === Data Retrieval and Access ===
    get_consensus = get_consensus
    get_chrom = get_chrom
    get_samples = get_samples
    get_consensus_matches = get_consensus_matches
    get_consensus_matrix = get_consensus_matrix
    get_gaps_matrix = get_gaps_matrix
    get_gaps_stats = get_gaps_stats
    get_orphans = get_orphans
    get_samples_stats = get_samples_stats
    get_consensus_stats = get_consensus_stats
    _get_adducts = _get_adducts

    # === Data Selection and Filtering ===
    samples_select = samples_select
    samples_delete = samples_delete

    features_select = features_select
    features_filter = features_filter
    features_filters = features_filter  # Alias for user preference
    features_delete = features_delete
    consensus_select = consensus_select
    consensus_filter = consensus_filter
    consensus_delete = consensus_delete

    # === Utility and Repair Operations ===
    _repair_uids = _repair_uids

    # === Sample Metadata and Styling ===
    set_samples_source = set_samples_source
    set_samples_color = set_samples_color

    set_samples_name = set_samples_name
    samples_name_reset = samples_name_reset

    metadata_import = metadata_import
    metadata_reset = metadata_reset

    # === Data Compression and Storage ===
    compress = compress
    decompress = decompress

    # === Reset Operations ===
    consensus_reset = consensus_reset
    fill_reset = fill_reset
    align_reset = align_reset

    # === Plotting and Visualization ===
    plot_alignment = plot_alignment
    plot_chrom = plot_chrom
    plot_consensus_2d = plot_consensus_2d
    plot_consensus_stats = plot_consensus_stats
    plot_samples_pca = plot_samples_pca
    plot_samples_umap = plot_samples_umap
    plot_samples_2d = plot_samples_2d
    plot_bpc = plot_bpc
    plot_rt_correction = plot_rt_correction
    plot_tic = plot_tic
    plot_eic = plot_eic
    plot_heatmap = plot_heatmap
    plot_ms2 = plot_ms2
    plot_volcano = plot_volcano
    plot_features_stats = plot_features_stats

    # === Analysis Operations ===
    analyze_umap = analyze_umap
    get_diff = get_diff
    diff_add = diff_add
    diff_reset = diff_reset

    # === Export Operations ===
    export_mgf = export_mgf
    export_mztab = export_mztab
    export_excel = export_excel
    export_parquet = export_parquet
    export_csv = export_csv
    export_history = export_history

    # === Identification and Library Matching ===
    lib_load = lib_load

    def lib_to_consensus(self, **kwargs):
        """Create consensus features from library entries."""
        from masster.study.id import lib_to_consensus as _lib_to_consensus

        return _lib_to_consensus(self, **kwargs)

    identify = identify
    get_id = get_id
    id_reset = id_reset
    lib_reset = lib_reset
    lib_compare = lib_compare
    lib_select = lib_select
    lib_filter = lib_filter
    id_update = id_update

    # === Import Operations ===
    import_oracle = import_oracle
    import_tima = import_tima

    # === Parameter Management ===
    update_history = update_history
    history_update = history_update
    history_reset = history_reset
    get_parameters = get_parameters
    parameters_update = parameters_update
    get_parameters_property = get_parameters_property
    set_parameters_property = set_parameters_property

    # === Private/Internal Methods ===
    _get_consensus_ids = _get_consensus_ids
    _get_consensus_uids = _get_consensus_uids
    _get_feature_ids = _get_feature_ids
    _get_feature_uids = _get_feature_uids
    _get_sample_ids = _get_sample_ids

    # === Default Parameters ===
    study_defaults = study_defaults
    align_defaults = align_defaults
    export_mgf_defaults = export_mgf_defaults
    fill_defaults = fill_defaults
    find_ms2_defaults = find_ms2_defaults
    integrate_chrom_defaults = integrate_chrom_defaults
    integrate_defaults = integrate_defaults
    merge_defaults = merge_defaults

    def _reload(self):
        """
        Reloads all masster modules to pick up any changes to their source code,
        and updates the instance's class reference to the newly reloaded class version.
        This ensures that the instance uses the latest implementation without restarting the interpreter.
        """
        # Reset logger configuration flags to allow proper reconfiguration after reload
        """        try:
            import masster.sample.logger as logger_module

            if hasattr(logger_module, "_STUDY_LOGGER_CONFIGURED"):
                logger_module._STUDY_LOGGER_CONFIGURED = False
        except Exception:
            pass"""

        # Get the base module name (masster)
        base_modname = self.__class__.__module__.split(".")[0]
        current_module = self.__class__.__module__

        # Dynamically find all study submodules
        study_modules = []
        study_module_prefix = f"{base_modname}.study."

        # Get all currently loaded modules that are part of the study package
        for module_name in sys.modules:
            if (
                module_name.startswith(study_module_prefix)
                and module_name != current_module
            ):
                study_modules.append(module_name)

        # Add core masster modules
        core_modules = [
            f"{base_modname}._version",
            f"{base_modname}.chromatogram",
            f"{base_modname}.spectrum",
            f"{base_modname}.logger",
        ]

        # Add sample submodules
        sample_modules = []
        sample_module_prefix = f"{base_modname}.sample."
        for module_name in sys.modules:
            if (
                module_name.startswith(sample_module_prefix)
                and module_name != current_module
            ):
                sample_modules.append(module_name)

        # Add lib submodules
        lib_modules = []
        lib_module_prefix = f"{base_modname}.lib."
        for module_name in sys.modules:
            if (
                module_name.startswith(lib_module_prefix)
                and module_name != current_module
            ):
                lib_modules.append(module_name)

        all_modules_to_reload = (
            core_modules + sample_modules + study_modules + lib_modules
        )

        # Reload all discovered modules
        for full_module_name in all_modules_to_reload:
            try:
                if full_module_name in sys.modules:
                    mod = sys.modules[full_module_name]
                    importlib.reload(mod)
                    self.logger.debug(f"Reloaded module: {full_module_name}")
            except Exception as e:
                self.logger.warning(f"Failed to reload module {full_module_name}: {e}")

        # Finally, reload the current module (sample.py)
        try:
            mod = __import__(current_module, fromlist=[current_module.split(".")[0]])
            importlib.reload(mod)

            # Get the updated class reference from the reloaded module
            new = getattr(mod, self.__class__.__name__)
            # Update the class reference of the instance
            self.__class__ = new

            self.logger.debug("Module reload completed")
        except Exception as e:
            self.logger.error(f"Failed to reload current module {current_module}: {e}")

    def __dir__(self):
        """
        Custom __dir__ implementation to hide internal methods starting with '_'
        from tab completion and dir() calls, while keeping them accessible to
        class methods.

        Returns:
            list: List of public attribute and method names
        """
        # Get all attributes from the class
        all_attrs: set[str] = set()

        # Add attributes from the class and all its bases
        for cls in self.__class__.__mro__:
            all_attrs.update(cls.__dict__.keys())

        # Add instance attributes
        all_attrs.update(self.__dict__.keys())

        # Filter out attributes starting with '_' (but keep special methods like __init__, __str__, etc.)
        public_attrs = [
            attr
            for attr in all_attrs
            if not attr.startswith("_")
            or (attr.startswith("__") and attr.endswith("__"))
        ]

        return sorted(public_attrs)

    def __str__(self):
        """
        Return a short summary string with number of samples and consensus features.
        """
        samples = (
            len(self.samples_df)
            if (self.samples_df is not None and not self.samples_df.is_empty())
            else 0
        )
        consensus = (
            len(self.consensus_df)
            if (self.consensus_df is not None and not self.consensus_df.is_empty())
            else 0
        )
        return f"{samples} samples, {consensus} consensus"

    def logger_update(
        self,
        level: str | None = None,
        label: str | None = None,
        sink: str | None = None,
    ):
        """Update the logging configuration for this Study instance.

        Args:
            level: New logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
            label: New label for log messages
            sink: New output sink (file path, file object, or "sys.stdout")
        """
        if level is not None:
            self.log_level = level.upper()
            self.logger.update_level(level)

        if label is not None:
            self.log_label = label + " | " if len(label) > 0 else ""
            self.logger.update_label(self.log_label)

        if sink is not None:
            if sink == "sys.stdout":
                self.log_sink = sys.stdout
            else:
                self.log_sink = sink
            self.logger.update_sink(self.log_sink)

    def info(self):
        """
        Display study information with optimized performance.

        Returns a summary string of the study including folder, features count,
        samples count, and various statistics. Shows warning symbols for values
        that are out of normal range.
        """
        if self.consensus_df is None or self.consensus_df.is_empty():
            self.consensus_df = pl.DataFrame()
            consensus_df_len = 0
        else:
            consensus_df_len = len(self.consensus_df)

        samples_df_len = (
            len(self.samples_df)
            if (self.samples_df is not None and not self.samples_df.is_empty())
            else 0
        )

        # Calculate consensus statistics only if consensus_df exists and has data
        if consensus_df_len > 0:
            # Execute the aggregation once
            stats_result = self.consensus_df.select(
                [
                    pl.col("number_samples").min().alias("min_samples"),
                    pl.col("number_samples").mean().alias("mean_samples"),
                    pl.col("number_samples").max().alias("max_samples"),
                ],
            ).row(0)

            min_samples = stats_result[0] if stats_result[0] is not None else 0
            mean_samples = stats_result[1] if stats_result[1] is not None else 0
            max_samples = stats_result[2] if stats_result[2] is not None else 0
        else:
            min_samples = 0
            mean_samples = 0
            max_samples = 0

        # Count only features where 'filled' == False
        if (
            self.features_df is not None
            and not self.features_df.is_empty()
            and "filled" in self.features_df.columns
        ):
            unfilled_features_count = self.features_df.filter(
                ~self.features_df["filled"],
            ).height
        else:
            unfilled_features_count = 0

        # Calculate features in consensus vs not in consensus (only for unfilled features)
        if (
            self.features_df is not None
            and not self.features_df.is_empty()
            and self.consensus_mapping_df is not None
            and not self.consensus_mapping_df.is_empty()
        ):
            # Get unfilled features only
            unfilled_features = (
                self.features_df.filter(~self.features_df["filled"])
                if "filled" in self.features_df.columns
                else self.features_df
            )

            # Ensure the column and list have matching data types
            consensus_feature_ids = self.consensus_mapping_df["feature_id"].to_list()

            # Check if we need to cast either side to match types
            unfilled_dtype = unfilled_features["feature_id"].dtype
            consensus_dtype = self.consensus_mapping_df["feature_id"].dtype

            if unfilled_dtype != consensus_dtype:
                # Cast both to Int64 if possible, otherwise keep as string
                try:
                    unfilled_features = unfilled_features.with_columns(
                        pl.col("feature_id").cast(pl.Int64),
                    )
                    consensus_feature_ids = [int(uid) for uid in consensus_feature_ids]
                except Exception:
                    # If casting fails, ensure both are strings
                    unfilled_features = unfilled_features.with_columns(
                        pl.col("feature_id").cast(pl.Utf8),
                    )
                    consensus_feature_ids = [str(uid) for uid in consensus_feature_ids]

            # Count unfilled features that are in consensus
            in_consensus_count = unfilled_features.filter(
                pl.col("feature_id").is_in(consensus_feature_ids),
            ).height

            # Calculate ratios that sum to 100%
            total_unfilled = unfilled_features.height
            ratio_in_consensus_to_total = (
                (in_consensus_count / total_unfilled * 100) if total_unfilled > 0 else 0
            )
            ratio_not_in_consensus_to_total = (
                100 - ratio_in_consensus_to_total if total_unfilled > 0 else 0
            )
        else:
            ratio_in_consensus_to_total = 0
            ratio_not_in_consensus_to_total = 0

        # Optimize chrom completeness calculation
        if (
            consensus_df_len > 0
            and samples_df_len > 0
            and self.features_df is not None
            and not self.features_df.is_empty()
        ):
            # Ensure matching data types for join keys
            features_dtype = self.features_df["feature_id"].dtype
            consensus_dtype = self.consensus_mapping_df["feature_id"].dtype

            if features_dtype != consensus_dtype:
                # Try to cast both to Int64, fallback to string if needed
                try:
                    self.features_df = self.features_df.with_columns(
                        pl.col("feature_id").cast(pl.Int64),
                    )
                    self.consensus_mapping_df = self.consensus_mapping_df.with_columns(
                        pl.col("feature_id").cast(pl.Int64),
                    )
                except Exception:
                    # If casting to Int64 fails, cast both to string
                    self.features_df = self.features_df.with_columns(
                        pl.col("feature_id").cast(pl.Utf8),
                    )
                    self.consensus_mapping_df = self.consensus_mapping_df.with_columns(
                        pl.col("feature_id").cast(pl.Utf8),
                    )

            # Use more efficient counting - count non-null chroms only for features in consensus mapping
            if (
                self.consensus_mapping_df is not None
                and not self.consensus_mapping_df.is_empty()
            ):
                non_null_chroms = (
                    self.features_df.join(
                        self.consensus_mapping_df.select("feature_id"),
                        on="feature_id",
                        how="inner",
                    )
                    .select(
                        pl.col("chrom").is_not_null().sum().alias("count"),
                    )
                    .item()
                )
            else:
                non_null_chroms = 0
            total_possible = samples_df_len * consensus_df_len
            chrom_completeness = (
                non_null_chroms / total_possible if total_possible > 0 else 0
            )
        else:
            chrom_completeness = 0

        # Calculate consensus features with MS2 (count unique consensus_ids with MS2)
        if self.consensus_ms2 is not None and not self.consensus_ms2.is_empty():
            consensus_with_ms2_count = self.consensus_ms2["consensus_id"].n_unique()
        else:
            consensus_with_ms2_count = 0

        if self.consensus_df is not None and not self.consensus_df.is_empty():
            # Compute RT spread using only consensus rows with number_samples >= half the number of samples
            threshold = (
                self.consensus_df.select(pl.col("number_samples").max()).item() / 2
                if (self.samples_df is not None and not self.samples_df.is_empty())
                else 0
            )
            filtered = self.consensus_df.filter(pl.col("number_samples") >= threshold)
            if filtered.is_empty():
                rt_spread = -1.0
            else:
                rt_spread_row = filtered.select(
                    (pl.col("rt_max") - pl.col("rt_min")).mean(),
                ).row(0)
                rt_spread = (
                    float(rt_spread_row[0])
                    if rt_spread_row and rt_spread_row[0] is not None
                    else 0.0
                )
        else:
            rt_spread = -1.0

        # Calculate percentage of consensus features with MS2
        consensus_with_ms2_percentage = (
            (consensus_with_ms2_count / consensus_df_len * 100)
            if consensus_df_len > 0
            else 0
        )

        # Total MS2 spectra count
        total_ms2_count = (
            len(self.consensus_ms2)
            if (self.consensus_ms2 is not None and not self.consensus_ms2.is_empty())
            else 0
        )

        # Estimate memory usage
        memory_usage = (
            (self.samples_df.estimated_size() if self.samples_df is not None else 0)
            + (self.features_df.estimated_size() if self.features_df is not None else 0)
            + (
                self.consensus_df.estimated_size()
                if self.consensus_df is not None
                else 0
            )
            + (
                self.consensus_ms2.estimated_size()
                if self.consensus_ms2 is not None
                else 0
            )
            + (
                self.consensus_mapping_df.estimated_size()
                if self.consensus_mapping_df is not None
                else 0
            )
        )

        # Calculate tight clusters count
        tight_clusters_count = 0
        if consensus_df_len > 0:
            try:
                from masster.study.merge import _count_tight_clusters

                tight_clusters_count = _count_tight_clusters(
                    self,
                    mz_tol=0.04,
                    rt_tol=0.3,
                )
            except Exception:
                # If tight clusters calculation fails, just use 0
                tight_clusters_count = 0

        # Add warning symbols for out-of-range values
        consensus_warning = f" {_WARNING_SYMBOL}" if consensus_df_len < 50 else ""

        rt_spread_text = "N/A" if rt_spread < 0 else f"{rt_spread:.3f}s"
        rt_spread_warning = (
            f" {_WARNING_SYMBOL}"
            if rt_spread >= 0 and (rt_spread > 5 or rt_spread < 0.1)
            else ""
        )

        chrom_completeness_pct = chrom_completeness * 100
        chrom_warning = (
            f" {_WARNING_SYMBOL}"
            if chrom_completeness_pct < 10 and chrom_completeness_pct >= 0
            else ""
        )

        max_samples_warning = ""
        if (
            isinstance(max_samples, (int, float))
            and samples_df_len > 0
            and max_samples > 0
        ):
            if max_samples < samples_df_len / 3.0 or max_samples < samples_df_len * 0.8:
                max_samples_warning = f" {_WARNING_SYMBOL}"

        # Add warning for tight clusters
        tight_clusters_warning = (
            f" {_WARNING_SYMBOL}" if tight_clusters_count > 10 else ""
        )

        summary = (
            f"Study folder:           {self.folder}\n"
            f"Last save:              {self.filename}\n"
            f"Samples:                {samples_df_len}\n"
            f"Polarity:               {self.parameters.polarity}\n"
            f"Features:               {unfilled_features_count}\n"
            f"- in consensus:         {ratio_in_consensus_to_total:.0f}%\n"
            f"- not in consensus:     {ratio_not_in_consensus_to_total:.0f}%\n"
            f"Consensus:              {consensus_df_len}{consensus_warning}\n"
            f"- RT spread:            {rt_spread_text}{rt_spread_warning}\n"
            f"- Tight clusters:       {tight_clusters_count}{tight_clusters_warning}\n"
            f"- Min samples count:    {min_samples:.0f}\n"
            f"- Mean samples count:   {mean_samples:.0f}\n"
            f"- Max samples count:    {max_samples:.0f}{max_samples_warning}\n"
            f"- with MS2:             {consensus_with_ms2_percentage:.0f}%\n"
            f"- total MS2:            {total_ms2_count}\n"
            f"Chrom completeness:     {chrom_completeness_pct:.0f}%{chrom_warning}\n"
            f"Memory usage:           {memory_usage / (1024**2):.2f} MB\n"
        )

        self.logger.info(summary)


if __name__ == "__main__":
    pass
