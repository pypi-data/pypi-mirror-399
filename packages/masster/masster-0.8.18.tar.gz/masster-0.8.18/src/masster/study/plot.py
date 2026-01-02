from __future__ import annotations

from datetime import datetime
from typing import Any

# Import cmap for colormap handling
from cmap import Colormap
import holoviews as hv
import numpy as np
import panel
import polars as pl
from tqdm import tqdm

from masster.exceptions import ConfigurationError

# Initialize bokeh extension - check if in notebook environment
try:
    from IPython import get_ipython

    ipython = get_ipython()
    if ipython is not None and "IPKernelApp" in ipython.config:
        # We're in a Jupyter notebook
        if "bokeh" not in hv.Store.loaded_backends():
            hv.extension("bokeh")
        panel.extension(comms="default", inline=True)
    # Not in notebook, use default bokeh extension
    elif "bokeh" not in hv.Store.loaded_backends():
        hv.extension("bokeh")
except (ImportError, AttributeError):
    # Not in IPython environment, use default bokeh extension
    if "bokeh" not in hv.Store.loaded_backends():
        hv.extension("bokeh")


# Replace any unaliased import that could be shadowed:
# from bokeh.layouts import row
from bokeh.layouts import row as bokeh_row


def _export_with_webdriver_manager(plot_obj, filename, format_type, logger=None):
    """
    Export plot to PNG or SVG using webdriver-manager for automatic driver management.

    Parameters:
        plot_obj: Bokeh plot object or holoviews object to export
        filename: Output filename
        format_type: Either "png" or "svg"
        logger: Logger for error reporting (optional)

    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        # Convert holoviews to bokeh if needed
        if hasattr(plot_obj, "opts"):  # Likely a holoviews object
            import holoviews as hv

            bokeh_plot = hv.render(plot_obj)
        else:
            bokeh_plot = plot_obj

        # Try webdriver-manager export first
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager

            # Set up Chrome options for headless operation
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")

            # Use webdriver-manager to automatically get the correct ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Export with managed webdriver
            if format_type == "png":
                from bokeh.io import export_png

                export_png(bokeh_plot, filename=filename, webdriver=driver)
            elif format_type == "svg":
                from bokeh.io import export_svg

                export_svg(bokeh_plot, filename=filename, webdriver=driver)
            else:
                raise ConfigurationError(
                    f"Unsupported export format: {format_type}\n\n"
                    "Supported formats: 'png', 'svg'\n\n"
                    "Example: study.plot_2d(filename='plot.png', format='png')",
                )

            driver.quit()
            return True

        except ImportError:
            if logger:
                logger.debug(
                    f"webdriver-manager not available, using default {format_type.upper()} export",
                )
            # Fall back to default export
            if format_type == "png":
                from bokeh.io import export_png

                export_png(bokeh_plot, filename=filename)
            elif format_type == "svg":
                from bokeh.io import export_svg

                export_svg(bokeh_plot, filename=filename)
            return True

        except Exception as e:
            if logger:
                logger.debug(
                    f"{format_type.upper()} export with webdriver-manager failed: {e}, using default {format_type.upper()} export",
                )
            try:
                # Final fallback to default export
                if format_type == "png":
                    from bokeh.io import export_png

                    export_png(bokeh_plot, filename=filename)
                elif format_type == "svg":
                    from bokeh.io import export_svg

                    export_svg(bokeh_plot, filename=filename)
                return True
            except Exception as e2:
                if logger:
                    logger.error(f"{format_type.upper()} export failed: {e2}")
                return False

    except Exception as e:
        if logger:
            logger.error(f"Export preparation failed: {e}")
        return False


def _isolated_save_plot(plot_object, filename, abs_filename, logger, plot_title="Plot"):
    """
    Save a plot using isolated file saving that doesn't affect global Bokeh state.
    This prevents browser opening issues when mixing file and notebook outputs.
    """
    if filename.endswith(".html"):
        # Use isolated file saving that doesn't affect global output state
        from bokeh.embed import file_html
        from bokeh.resources import Resources

        # Create HTML content without affecting global state
        resources = Resources(mode="cdn")
        html = file_html(plot_object, resources, title=plot_title)

        # Write directly to file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"Plot saved to: {abs_filename}")

    elif filename.endswith(".png"):
        success = _export_with_webdriver_manager(plot_object, filename, "png", logger)
        if success:
            logger.info(f"Plot saved to: {abs_filename}")
        else:
            # Fall back to HTML if PNG export not available
            html_filename = filename.replace(".png", ".html")
            abs_html_filename = (
                html_filename
                if abs_filename == filename
                else abs_filename.replace(".png", ".html")
            )
            from bokeh.embed import file_html
            from bokeh.resources import Resources

            resources = Resources(mode="cdn")
            html = file_html(plot_object, resources, title=plot_title)

            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(html)

            logger.warning(
                f"PNG export not available. Saved as HTML instead: {abs_html_filename}",
            )
    elif filename.endswith(".svg"):
        success = _export_with_webdriver_manager(plot_object, filename, "svg", logger)
        if success:
            logger.info(f"Plot saved to: {abs_filename}")
        else:
            # Fall back to HTML if SVG export not available
            html_filename = filename.replace(".svg", ".html")
            abs_html_filename = (
                html_filename
                if abs_filename == filename
                else abs_filename.replace(".svg", ".html")
            )
            from bokeh.embed import file_html
            from bokeh.resources import Resources

            resources = Resources(mode="cdn")
            html = file_html(plot_object, resources, title=plot_title)

            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(html)

            logger.warning(
                f"SVG export not available. Saved as HTML instead: {abs_html_filename}",
            )
            html = file_html(plot_object, resources, title=plot_title)

            with open(html_filename, "w", encoding="utf-8") as f:
                f.write(html)

            logger.warning(
                f"SVG export not available. Saved as HTML instead: {abs_html_filename}",
            )
    else:
        # Default to HTML for unknown extensions using isolated approach
        from bokeh.embed import file_html
        from bokeh.resources import Resources

        resources = Resources(mode="cdn")
        html = file_html(plot_object, resources, title=plot_title)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"Plot saved to: {abs_filename}")


def _isolated_show_notebook(plot_object):
    """
    Show a plot in notebook using isolated display that resets Bokeh state.
    This prevents browser opening issues when mixing file and notebook outputs.
    """
    import logging
    import warnings

    from bokeh.io import output_notebook, reset_output, show
    import holoviews as hv

    # Suppress both warnings and logging messages for the specific Bokeh callback warnings
    # that occur when Panel components with Python callbacks are converted to standalone Bokeh
    bokeh_logger = logging.getLogger("bokeh.embed.util")
    original_level = bokeh_logger.level
    bokeh_logger.setLevel(logging.ERROR)  # Suppress WARNING level messages

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=".*standalone HTML/JS output.*",
            category=UserWarning,
        )
        warnings.filterwarnings(
            "ignore",
            message=".*real Python callbacks.*",
            category=UserWarning,
        )

        try:
            # First clear all output state
            reset_output()

            # Set notebook mode
            output_notebook(hide_banner=True)

            # Reset Holoviews to notebook mode
            if "bokeh" not in hv.Store.loaded_backends():
                hv.extension("bokeh", logo=False)
            hv.output(backend="bokeh", mode="jupyter")

            # Ensure panel extension is initialized for inline display
            try:
                from IPython import get_ipython

                ipython = get_ipython()
                if ipython is not None and "IPKernelApp" in ipython.config:
                    panel.extension(comms="default", inline=True)
            except (ImportError, AttributeError):
                pass

            # Show in notebook
            show(plot_object)
        finally:
            # Restore original logging level
            bokeh_logger.setLevel(original_level)


def _isolated_save_panel_plot(panel_obj, filename, abs_filename, logger, plot_title):
    """
    Save a Panel plot using isolated approach that doesn't affect global Bokeh state.

    Args:
        panel_obj: Panel object to save
        filename: Target filename
        abs_filename: Absolute path for logging
        logger: Logger instance
        plot_title: Title for logging
    """
    import os  # Import os for path operations

    if filename.endswith(".html"):
        # Panel save method should be isolated but let's be sure
        try:
            # Save directly without affecting global Bokeh state
            panel_obj.save(filename, embed=True)
            logger.info(f"{plot_title} saved to: {abs_filename}")
        except Exception as e:
            logger.error(f"Failed to save {plot_title}: {e}")

    elif filename.endswith(".png"):
        try:
            from panel.io.save import save_png

            # Convert Panel to Bokeh models before saving
            bokeh_layout = panel_obj.get_root()
            save_png(bokeh_layout, filename=filename)
            logger.info(f"{plot_title} saved to: {abs_filename}")
        except Exception:
            # Fall back to HTML if PNG export not available
            html_filename = filename.replace(".png", ".html")
            abs_html_filename = os.path.abspath(html_filename)
            try:
                panel_obj.save(html_filename, embed=True)
                logger.warning(
                    f"PNG export not available, saved as HTML instead: {abs_html_filename}",
                )
            except Exception as e:
                logger.error(f"Failed to save {plot_title} as HTML fallback: {e}")

    elif filename.endswith(".pdf"):
        # Try to save as PDF, fall back to HTML if not available
        try:
            from bokeh.io.export import export_pdf

            bokeh_layout = panel_obj.get_root()
            export_pdf(bokeh_layout, filename=filename)
            logger.info(f"{plot_title} saved to: {abs_filename}")
        except ImportError:
            # Fall back to HTML if PDF export not available
            html_filename = filename.replace(".pdf", ".html")
            abs_html_filename = os.path.abspath(html_filename)
            try:
                panel_obj.save(html_filename, embed=True)
                logger.warning(
                    f"PDF export not available, saved as HTML instead: {abs_html_filename}",
                )
            except Exception as e:
                logger.error(f"Failed to save {plot_title} as HTML fallback: {e}")
    elif filename.endswith(".svg"):
        # Try to save as SVG, fall back to HTML if not available
        try:
            from bokeh.io.export import export_svg

            bokeh_layout = panel_obj.get_root()
            export_svg(bokeh_layout, filename=filename)
            logger.info(f"{plot_title} saved to: {abs_filename}")
        except Exception as e:
            # Fall back to HTML if SVG export not available
            html_filename = filename.replace(".svg", ".html")
            abs_html_filename = os.path.abspath(html_filename)
            try:
                panel_obj.save(html_filename, embed=True)
                logger.warning(
                    f"SVG export not available ({e!s}), saved as HTML instead: {abs_html_filename}",
                )
            except Exception as e:
                logger.error(f"Failed to save {plot_title} as HTML fallback: {e}")
    else:
        # Default to HTML for unknown extensions
        try:
            panel_obj.save(filename, embed=True)
            logger.info(f"{plot_title} saved to: {abs_filename}")
        except Exception as e:
            logger.error(f"Failed to save {plot_title}: {e}")


def _isolated_show_panel_notebook(panel_obj):
    """
    Show a Panel plot in notebook with state isolation to prevent browser opening.

    Args:
        panel_obj: Panel object to display
    """
    # Reset Bokeh state completely to prevent browser opening if output_file was called before
    from bokeh.io import output_notebook, reset_output
    import holoviews as hv

    # First clear all output state
    reset_output()

    # Set notebook mode
    output_notebook(hide_banner=True)

    # Reset Holoviews to notebook mode
    hv.extension("bokeh", logo=False)
    hv.output(backend="bokeh", mode="jupyter")

    # For Panel objects in notebooks, use on.extension and display inline
    import panel as on

    try:
        # Configure Panel for notebook display
        on.extension("bokeh", inline=True, comms="vscode")
        # Use IPython display to show inline instead of show()
        from IPython.display import display

        display(panel_obj)
    except Exception:
        # Fallback to regular Panel show
        panel_obj.show()


def plot_alignment(
    self,
    samples=50,
    filename: str | None = None,
    width: int = 450,
    height: int = 450,
    markersize: int = 3,
):
    """Visualize retention time alignment using two synchronized Bokeh scatter plots.

    Uses ``features_df`` to create side-by-side plots showing Original RT (left)
    and Current/Aligned RT (right). If no alignment has been performed yet,
    both plots show the current RT values.

    Parameters:
    - samples: List of sample identifiers (sample_ids or sample_names), or single int for random selection, or None for all samples.
    - filename: optional HTML file path to save the plot.
    - width/height: pixel size of each subplot.
    - markersize: base marker size.

    Returns:
    - Bokeh layout (row) containing the two synchronized plots.
    """
    # Local imports so the module can be used even if bokeh isn't needed elsewhere
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.plotting import figure
    import pandas as pd

    # Check if features_df exists
    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found. Load features first.")
        return None

    # Check required columns
    required_cols = ["rt", "mz", "inty"]
    missing = [c for c in required_cols if c not in self.features_df.columns]
    if missing:
        self.logger.error(f"Missing required columns in features_df: {missing}")
        return None

    # Check if alignment has been performed
    has_alignment = "rt_original" in self.features_df.columns
    if not has_alignment:
        self.logger.warning(
            "Column 'rt_original' not found - alignment has not been performed yet.",
        )
        self.logger.info(
            "Showing current RT values for both plots. Run align() first to see alignment comparison.",
        )

    # Get sample_ids to filter by if specified
    sample_ids = self._get_sample_ids(samples) if samples is not None else None

    # Start with full features_df
    features_df = self.features_df

    # Filter by selected samples if specified
    if sample_ids is not None:
        features_df = features_df.filter(pl.col("sample_id").is_in(sample_ids))
        if features_df.is_empty():
            self.logger.error("No features found for the selected samples.")
            return None

    # Determine sample column
    sample_col = "sample_id" if "sample_id" in features_df.columns else "sample_name"
    if sample_col not in features_df.columns:
        self.logger.error("No sample identifier column found in features_df.")
        return None

    # Get unique samples
    samples_list = features_df.select(pl.col(sample_col)).unique().to_series().to_list()

    # Build plotting data
    before_data: list[dict[str, Any]] = []
    after_data: list[dict[str, Any]] = []

    for sample_idx, sample in enumerate(samples_list):
        # Filter sample data
        sample_data = features_df.filter(pl.col(sample_col) == sample)

        # Sample data if too large for performance
        max_points_per_sample = 10000
        if sample_data.height > max_points_per_sample:
            self.logger.info(
                f"Sample {sample}: Sampling {max_points_per_sample} points from {sample_data.height} features for performance",
            )
            sample_data = sample_data.sample(n=max_points_per_sample, seed=42)

        # Calculate max intensity for alpha scaling
        max_inty = sample_data.select(pl.col("inty").max()).item() or 1

        # Get sample information
        sample_id = (
            sample
            if sample_col == "sample_id"
            else sample_data.select(pl.col("sample_id")).item()
            if "sample_id" in sample_data.columns
            else sample
        )

        # Try to get actual sample name from samples_df if available
        sample_name = str(sample)  # fallback
        if (
            hasattr(self, "samples_df")
            and self.samples_df is not None
            and sample_id is not None
        ):
            try:
                sample_name_result = (
                    self.samples_df.filter(pl.col("sample_id") == sample_id)
                    .select("sample_name")
                    .to_series()
                )
                if len(sample_name_result) > 0 and sample_name_result[0] is not None:
                    sample_name = str(sample_name_result[0])
            except Exception:
                # Keep the fallback value
                pass

        # Select columns to process
        cols_to_select = ["rt", "mz", "inty"]
        if has_alignment:
            cols_to_select.append("rt_original")

        sample_dict = sample_data.select(cols_to_select).to_dicts()

        for row_dict in sample_dict:
            rt_original = (
                row_dict.get("rt_original", row_dict["rt"])
                if has_alignment
                else row_dict["rt"]
            )
            rt_current = row_dict["rt"]
            mz = row_dict["mz"]
            inty = row_dict["inty"]
            # Skip if inty is None
            if inty is None:
                continue
            alpha = inty / max_inty
            size = markersize + 2 if sample_idx == 0 else markersize

            before_data.append(
                {
                    "rt": rt_original,
                    "mz": mz,
                    "inty": inty,
                    "alpha": alpha,
                    "sample_idx": sample_idx,
                    "sample_name": sample_name,
                    "sample_id": sample_id,
                    "size": size,
                },
            )
            after_data.append(
                {
                    "rt": rt_current,
                    "mz": mz,
                    "inty": inty,
                    "alpha": alpha,
                    "sample_idx": sample_idx,
                    "sample_name": sample_name,
                    "sample_id": sample_id,
                    "size": size,
                },
            )

    # Check if we have any data to plot
    if not before_data:
        self.logger.error("No data to plot.")
        return None

    # Get sample colors from samples_df
    sample_idx_to_uid = {}
    for item in before_data:
        if item["sample_idx"] not in sample_idx_to_uid:
            sample_idx_to_uid[item["sample_idx"]] = item["sample_id"]

    # Get colors from samples_df if available
    sample_ids_list = list(sample_idx_to_uid.values())
    color_map: dict[int, str] = {}

    if sample_ids_list and hasattr(self, "samples_df") and self.samples_df is not None:
        try:
            sample_colors = (
                self.samples_df.filter(pl.col("sample_id").is_in(sample_ids_list))
                .select(["sample_id", "sample_color"])
                .to_dict(as_series=False)
            )
            uid_to_color = dict(
                zip(
                    sample_colors["sample_id"],
                    sample_colors["sample_color"],
                    strict=False,
                ),
            )

            for sample_idx, sample_id in sample_idx_to_uid.items():
                color_map[sample_idx] = uid_to_color.get(sample_id, "#1f77b4")
        except Exception:
            # Fallback to default colors if sample colors not available
            for sample_idx in sample_idx_to_uid:
                color_map[sample_idx] = "#1f77b4"
    else:
        # Default colors
        for sample_idx in sample_idx_to_uid:
            color_map[sample_idx] = "#1f77b4"

    # Add sample_color to data
    for item in before_data + after_data:
        item["sample_color"] = color_map.get(item["sample_idx"], "#1f77b4")

    # Create DataFrames
    before_df = pd.DataFrame(before_data)
    after_df = pd.DataFrame(after_data)

    # Create Bokeh figures
    title_before = "Original RT" if has_alignment else "Current RT (No Alignment)"
    title_after = "Aligned RT" if has_alignment else "Current RT (Copy)"

    p1 = figure(
        width=width,
        height=height,
        title=title_before,
        x_axis_label="Retention Time (s)",
        y_axis_label="m/z",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    p1.outline_line_color = None
    p1.background_fill_color = "white"
    p1.border_fill_color = "white"
    p1.min_border = 0

    p2 = figure(
        width=width,
        height=height,
        title=title_after,
        x_axis_label="Retention Time (s)",
        y_axis_label="m/z",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        x_range=p1.x_range,
        y_range=p1.y_range,
    )
    p2.outline_line_color = None
    p2.background_fill_color = "white"
    p2.border_fill_color = "white"
    p2.min_border = 0

    # Plot data by sample
    unique_samples = sorted(list({item["sample_idx"] for item in before_data}))
    renderers_before = []
    renderers_after = []

    for sample_idx in unique_samples:
        sb = before_df[before_df["sample_idx"] == sample_idx]
        sa = after_df[after_df["sample_idx"] == sample_idx]
        color = color_map.get(sample_idx, "#1f77b4")

        if not sb.empty:
            src = ColumnDataSource(sb)
            r = p1.scatter(
                "rt",
                "mz",
                size="size",
                color=color,
                alpha="alpha",
                source=src,
            )
            renderers_before.append(r)

        if not sa.empty:
            src = ColumnDataSource(sa)
            r = p2.scatter(
                "rt",
                "mz",
                size="size",
                color=color,
                alpha="alpha",
                source=src,
            )
            renderers_after.append(r)

    # Add hover tools
    hover1 = HoverTool(
        tooltips=[
            ("Sample UID", "@sample_id"),
            ("Sample Name", "@sample_name"),
            ("Sample Color", "$color[swatch]:sample_color"),
            ("RT", "@rt{0.00}"),
            ("m/z", "@mz{0.0000}"),
            ("Intensity", "@inty{0.0e0}"),
        ],
        renderers=renderers_before,
    )
    p1.add_tools(hover1)

    hover2 = HoverTool(
        tooltips=[
            ("Sample UID", "@sample_id"),
            ("Sample Name", "@sample_name"),
            ("Sample Color", "$color[swatch]:sample_color"),
            ("RT", "@rt{0.00}"),
            ("m/z", "@mz{0.0000}"),
            ("Intensity", "@inty{0.0e0}"),
        ],
        renderers=renderers_after,
    )
    p2.add_tools(hover2)

    # Create layout
    layout = bokeh_row(p1, p2, sizing_mode="fixed", width=width, height=height)

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(
            layout,
            filename,
            abs_filename,
            self.logger,
            "Alignment Plot",
        )
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(layout)

    return layout


def plot_consensus_2d(
    self,
    filename=None,
    colorby="number_samples",
    cmap="viridis",
    alpha=0.7,
    markersize=8,
    sizeby="inty_mean",
    scaling="static",
    width=600,
    height=450,
    mz_range=None,
    rt_range=None,
    legend="bottom_right",
    show_none=True,
):
    """
    Plot consensus features in a 2D scatter plot with retention time vs m/z.

    Parameters:
        filename (str, optional): Path to save the plot
        colorby (str): Column name to use for color mapping (default: "number_samples")
                      Automatically detects if column contains categorical (string) or
                      numeric data and applies appropriate color mapping:
                      - Categorical: Uses factor_cmap with distinct colors and legend
                      - Numeric: Uses LinearColorMapper with continuous colorbar
        sizeby (str): Column name to use for size mapping (default: "inty_mean")
        markersize (int): Base marker size (default: 6)
        scaling (str): Controls whether points scale with zoom. Options:
                   'dynamic' - points use circle() and scale with zoom
                   'static' - points use scatter() and maintain fixed pixel size
        alpha (float): Transparency level (default: 0.7)
        cmap (str, optional): Color map name
        width (int): Plot width in pixels (default: 900)
        height (int): Plot height in pixels (default: 900)
        mz_range (tuple, optional): m/z range for filtering consensus features (min_mz, max_mz)
        rt_range (tuple, optional): Retention time range for filtering consensus features (min_rt, max_rt)
        legend (str, optional): Legend position for categorical data. Options: 'top_right', 'top_left',
                               'bottom_right', 'bottom_left', 'right', 'left', 'top', 'bottom'.
                               If None, legend is hidden. Only applies to categorical coloring (default: "bottom_right")
        show_none (bool): Whether to display points with None values for colorby column (default: True)
    """
    if self.consensus_df is None:
        self.logger.error("No consensus map found.")
        return None
    data = self.consensus_df.clone()

    # Filter by mz_range and rt_range if provided
    if mz_range is not None:
        data = data.filter(
            (pl.col("mz") >= mz_range[0]) & (pl.col("mz") <= mz_range[1]),
        )
    if rt_range is not None:
        data = data.filter(
            (pl.col("rt") >= rt_range[0]) & (pl.col("rt") <= rt_range[1]),
        )

    if colorby not in data.columns:
        self.logger.error(f"Column {colorby} not found in consensus_df.")
        return None
    if sizeby is not None and sizeby not in data.columns:
        self.logger.warning(f"Column {sizeby} not found in consensus_df.")
        sizeby = None
    # if sizeby is not None, set markersize to sizeby
    if sizeby is not None:
        # set markersize to sizeby
        if sizeby in ["inty_mean"]:
            # use log10 of sizeby
            # Filter out empty or all-NA entries before applying np.log10
            data = data.with_columns(
                [
                    pl.when(
                        (pl.col(sizeby).is_not_null())
                        & (pl.col(sizeby).is_finite())
                        & (pl.col(sizeby) > 0),
                    )
                    .then((pl.col(sizeby).log10() * markersize / 12).pow(1.5))
                    .otherwise(markersize)
                    .alias("markersize"),
                ],
            )
        else:
            max_size = data[sizeby].max()
            data = data.with_columns(
                [
                    (pl.col(sizeby) / max_size * markersize).alias("markersize"),
                ],
            )
    else:
        data = data.with_columns([pl.lit(markersize).alias("markersize")])
    # sort by ascending colorby
    data = data.sort(colorby)
    # convert consensus_id to string - check if column exists
    if "consensus_id" in data.columns:
        # Handle Object dtype by converting to string first
        data = data.with_columns(
            [
                pl.col("consensus_id")
                .map_elements(
                    lambda x: str(x) if x is not None else None,
                    return_dtype=pl.Utf8,
                )
                .alias("consensus_id"),
            ],
        )
    elif "consensus_id" in data.columns:
        data = data.with_columns(
            [
                pl.col("consensus_id").cast(pl.Utf8).alias("consensus_id"),
            ],
        )

    if cmap is None:
        cmap = "viridis"
    elif cmap == "grey":
        cmap = "greys"

    # plot with bokeh
    from bokeh.models import BasicTicker, ColumnDataSource, HoverTool, LinearColorMapper
    import bokeh.plotting as bp
    from bokeh.transform import factor_cmap

    try:
        from bokeh.models import ColorBar
    except ImportError:
        from bokeh.models.annotations import ColorBar
    from bokeh.palettes import Category20, viridis

    # Filter out None values for colorby column if show_none=False
    if not show_none and colorby in data.columns:
        data = data.filter(pl.col(colorby).is_not_null())

    # Convert Polars DataFrame to pandas for Bokeh compatibility
    data_pd = data.to_pandas()
    source = ColumnDataSource(data_pd)

    # Handle colormap using cmap.Colormap
    try:
        # Get colormap palette using cmap
        if isinstance(cmap, str):
            colormap = Colormap(cmap)
            # Generate 256 colors and convert to hex
            import matplotlib.colors as mcolors
            import numpy as np

            colors = colormap(np.linspace(0, 1, 256))
            palette = [mcolors.rgb2hex(color) for color in colors]
        else:
            colormap = cmap
            # Try to use to_bokeh() method first
            try:
                palette = colormap.to_bokeh()
                # Ensure we got a color palette, not another mapper
                if not isinstance(palette, (list, tuple)):
                    # Fall back to generating colors manually
                    import matplotlib.colors as mcolors
                    import numpy as np

                    colors = colormap(np.linspace(0, 1, 256))
                    palette = [mcolors.rgb2hex(color) for color in colors]
            except AttributeError:
                # Fall back to generating colors manually
                import matplotlib.colors as mcolors
                import numpy as np

                colors = colormap(np.linspace(0, 1, 256))
                palette = [mcolors.rgb2hex(color) for color in colors]
    except (AttributeError, ValueError, TypeError) as e:
        # Fallback to viridis if cmap interpretation fails
        self.logger.warning(
            f"Could not interpret colormap '{cmap}': {e}, falling back to viridis",
        )
        palette = viridis(256)

    # Check if colorby column contains categorical data (string/object)
    colorby_values = data[colorby].to_list()
    is_categorical = (
        data_pd[colorby].dtype in ["object", "string", "category"]
        or isinstance(colorby_values[0], str)
        if colorby_values
        else False
    )

    if is_categorical:
        # Handle categorical coloring
        # Use natural order of unique values - don't sort to preserve correct legend mapping
        # Sorting would break the correspondence between legend labels and point colors
        unique_values = [v for v in data_pd[colorby].unique() if v is not None]

        # Use the custom palette from cmap if available, otherwise fall back to defaults
        if len(palette) >= len(unique_values):
            # Use custom colormap palette - sample evenly across the palette
            import numpy as np

            indices = np.linspace(0, len(palette) - 1, len(unique_values)).astype(int)
            categorical_palette = [palette[i] for i in indices]
        elif len(unique_values) <= 20:
            # Fall back to Category20 if custom palette is too small
            categorical_palette = Category20[min(20, max(3, len(unique_values)))]
        else:
            # For many categories, use a subset of the viridis palette
            categorical_palette = viridis(min(256, len(unique_values)))

        color_mapper = factor_cmap(colorby, categorical_palette, unique_values)
    else:
        # Handle numeric coloring with LinearColorMapper
        color_mapper = LinearColorMapper(
            palette=palette,
            low=data[colorby].min(),
            high=data[colorby].max(),
        )
    # scatter plot rt vs mz
    p = bp.figure(
        width=width,
        height=height,
        title=f"Consensus features, colored by {colorby}",
    )
    p.xaxis.axis_label = "RT [s]"
    p.yaxis.axis_label = "m/z [Th]"
    scatter_renderer: Any = None
    if is_categorical:
        # For categorical data, create separate renderers for each category
        # This enables proper legend interactivity where each category can be toggled independently
        all_unique_values = list(data_pd[colorby].unique())
        unique_values = [v for v in all_unique_values if v is not None]
        has_none_values = None in all_unique_values

        # Use the custom palette from cmap if available, otherwise fall back to defaults
        if len(palette) >= len(unique_values):
            # Use custom colormap palette - sample evenly across the palette
            import numpy as np

            indices = np.linspace(0, len(palette) - 1, len(unique_values)).astype(int)
            categorical_palette = [palette[i] for i in indices]
        elif len(unique_values) <= 20:
            # Fall back to Category20 if custom palette is too small
            categorical_palette = Category20[min(20, max(3, len(unique_values)))]
        else:
            categorical_palette = viridis(min(256, len(unique_values)))

        # Handle None values with black color FIRST so they appear in the background
        if has_none_values and show_none:
            # Filter data for None values
            none_data = data.filter(pl.col(colorby).is_null())
            none_data_pd = none_data.to_pandas()
            none_source = bp.ColumnDataSource(none_data_pd)

            if scaling.lower() in ["dyn", "dynamic"]:
                # Calculate appropriate radius for dynamic scaling
                rt_range = data["rt"].max() - data["rt"].min()
                mz_range = data["mz"].max() - data["mz"].min()
                dynamic_radius = min(rt_range, mz_range) * 0.0005 * markersize

                p.circle(
                    x="rt",
                    y="mz",
                    radius=dynamic_radius,
                    fill_color="lightgray",
                    line_color=None,
                    alpha=alpha,
                    source=none_source,
                    legend_label="None",
                    muted_alpha=0.0,
                )
            else:
                p.scatter(
                    x="rt",
                    y="mz",
                    size="markersize",
                    fill_color="lightgray",
                    line_color=None,
                    alpha=alpha,
                    source=none_source,
                    legend_label="None",
                    muted_alpha=0.0,
                )

        # Create a separate renderer for each non-None category (plotted on top of None values)
        for i, category in enumerate(unique_values):
            # Filter data for this category
            category_data = data.filter(pl.col(colorby) == category)
            category_data_pd = category_data.to_pandas()
            category_source = bp.ColumnDataSource(category_data_pd)

            color = categorical_palette[i % len(categorical_palette)]

            if scaling.lower() in ["dyn", "dynamic"]:
                # Calculate appropriate radius for dynamic scaling
                rt_range = data["rt"].max() - data["rt"].min()
                mz_range = data["mz"].max() - data["mz"].min()
                dynamic_radius = min(rt_range, mz_range) * 0.0005 * markersize

                p.circle(
                    x="rt",
                    y="mz",
                    radius=dynamic_radius,
                    fill_color=color,
                    line_color=None,
                    alpha=alpha,
                    source=category_source,
                    legend_label=str(category),
                    muted_alpha=0.0,
                )
            else:
                p.scatter(
                    x="rt",
                    y="mz",
                    size="markersize",
                    fill_color=color,
                    line_color=None,
                    alpha=alpha,
                    source=category_source,
                    legend_label=str(category),
                    muted_alpha=0.0,
                )

        # No single scatter_renderer for categorical data
        scatter_renderer = None

    # Handle numeric coloring - single renderer with color mapping
    elif scaling.lower() in ["dyn", "dynamic"]:
        # Calculate appropriate radius for dynamic scaling
        rt_range = data["rt"].max() - data["rt"].min()
        mz_range = data["mz"].max() - data["mz"].min()
        dynamic_radius = min(rt_range, mz_range) * 0.0005 * markersize

        scatter_renderer = p.circle(
            x="rt",
            y="mz",
            radius=dynamic_radius,
            fill_color={"field": colorby, "transform": color_mapper},
            line_color=None,
            alpha=alpha,
            source=source,
        )
    else:
        scatter_renderer = p.scatter(
            x="rt",
            y="mz",
            size="markersize",
            fill_color={"field": colorby, "transform": color_mapper},
            line_color=None,
            alpha=alpha,
            source=source,
        )
    # add hover tool
    # Start with base tooltips - rt and mz moved to top, removed consensus_id and iso_mean
    tooltips = [
        ("rt", "@rt"),
        ("mz", "@mz"),
        ("consensus_id", "@consensus_id"),
        ("number_samples", "@number_samples"),
        ("number_ms2", "@number_ms2"),
        ("inty_mean", "@inty_mean"),
    ]

    # Add id_top_* columns if they exist and have non-null values
    id_top_columns = ["id_top_name", "id_top_adduct", "id_top_score", "id_source"]
    for col in id_top_columns:
        if col in data.columns:
            # Check if the column has any non-null values
            if data.filter(pl.col(col).is_not_null()).height > 0:
                # Format score column with decimal places, others as strings
                if col == "id_top_score":
                    tooltips.append((col, f"@{col}{{0.00}}"))
                else:
                    tooltips.append((col, f"@{col}"))

    hover = HoverTool(
        tooltips=tooltips,
    )
    # For categorical data, hover will work on all renderers automatically
    # For numeric data, specify the single renderer
    if not is_categorical and scatter_renderer:
        hover.renderers = [scatter_renderer]

    p.add_tools(hover)

    # add colorbar only for numeric data (LinearColorMapper)
    if not is_categorical:
        color_bar = ColorBar(
            color_mapper=color_mapper,
            label_standoff=12,
            location=(0, 0),
            title=colorby,
            ticker=BasicTicker(desired_num_ticks=8),
        )
        p.add_layout(color_bar, "right")
    # For categorical data, configure the legend that was automatically created
    elif legend is not None:
        # Map legend position parameter to Bokeh legend position
        legend_position_map = {
            "top_right": "top_right",
            "top_left": "top_left",
            "bottom_right": "bottom_right",
            "bottom_left": "bottom_left",
            "right": "right",
            "left": "left",
            "top": "top",
            "bottom": "bottom",
        }

        bokeh_legend_pos = legend_position_map.get(legend, "bottom_right")
        p.legend.location = bokeh_legend_pos
        p.legend.click_policy = "hide"
    else:
        # Hide legend when legend=None
        p.legend.visible = False

    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "Consensus 2D Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)
    return p


def plot_samples_2d(
    self,
    samples=100,
    filename=None,
    markersize=2,
    size="dynamic",
    alpha_max=0.8,
    alpha="inty",
    max_features=50000,
    width=600,
    height=600,
    mz_range=None,
    rt_range=None,
):
    """
    Plot all feature maps for sample_id in parameter uids in an overlaid scatter plot.
    Each sample is a different color. Alpha scales with intensity.
    OPTIMIZED VERSION: Uses vectorized operations and batch processing.

    Parameters:
        samples: Sample UIDs to plot
        filename (str, optional): Path to save the plot
        markersize (int): Base marker size (default: 2)
        size (str): Controls whether points scale with zoom. Options:
                   'dynamic' or 'dyn' - points use circle() and scale with zoom
                   'const', 'static' or other - points use scatter() and maintain fixed pixel size
        alpha_max (float): Maximum transparency level (default: 0.8)
        alpha (str): Column name to use for alpha mapping (default: "inty")
        cmap (str): Color map name (default: "Turbo256")
        max_features (int): Maximum number of features to plot (default: 50000)
        width (int): Plot width in pixels (default: 900)
        height (int): Plot height in pixels (default: 900)
        mz_range (tuple, optional): m/z range for filtering features (min_mz, max_mz)
        rt_range (tuple, optional): Retention time range for filtering features (min_rt, max_rt)
    """

    # Local bokeh imports to avoid heavy top-level dependency
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.plotting import figure

    sample_ids = self._get_sample_ids(samples)

    if not sample_ids:
        self.logger.error("No valid sample_ids provided.")
        return

    # Get sample colors from samples_df
    sample_colors = (
        self.samples_df.filter(pl.col("sample_id").is_in(sample_ids))
        .select(["sample_id", "sample_color"])
        .to_dict(as_series=False)
    )
    color_map = dict(
        zip(sample_colors["sample_id"], sample_colors["sample_color"], strict=False),
    )

    p = figure(
        width=width,
        height=height,
        title="Sample Features",
    )
    p.xaxis.axis_label = "Retention Time (RT)"
    p.yaxis.axis_label = "m/z"

    # OPTIMIZATION 1: Batch filter all features for selected samples at once
    features_batch = self.features_df.filter(pl.col("sample_id").is_in(sample_ids))

    # Filter by mz_range and rt_range if provided
    if mz_range is not None:
        features_batch = features_batch.filter(
            (pl.col("mz") >= mz_range[0]) & (pl.col("mz") <= mz_range[1]),
        )
    if rt_range is not None:
        features_batch = features_batch.filter(
            (pl.col("rt") >= rt_range[0]) & (pl.col("rt") <= rt_range[1]),
        )

    if features_batch.is_empty():
        self.logger.error("No features found for the selected samples.")
        return

    # OPTIMIZATION 8: Fast sampling for very large datasets to maintain interactivity
    max_features_per_plot = max_features  # Limit for interactive performance
    total_features = len(features_batch)

    if total_features > max_features_per_plot:
        # OPTIMIZED: Much faster random sampling without groupby operations
        sample_ratio = max_features_per_plot / total_features
        self.logger.info(
            f"Large dataset detected ({total_features:,} features). "
            f"Sampling {sample_ratio:.1%} for visualization performance.",
        )

        # FAST: Use simple random sampling instead of expensive stratified sampling
        n_samples = min(max_features_per_plot, total_features)
        features_batch = features_batch.sample(n=n_samples, seed=42)

    # OPTIMIZATION 2: Join with samples_df to get sample names in one operation
    samples_info = self.samples_df.filter(pl.col("sample_id").is_in(sample_ids))
    features_with_names = features_batch.join(
        samples_info.select(["sample_id", "sample_name"]),
        on="sample_id",
        how="left",
    )

    # OPTIMIZATION 4: Fast pre-calculation of alpha values for all features
    if alpha == "inty":
        # OPTIMIZED: Use efficient Polars operations instead of pandas groupby transform
        # Calculate max intensity per sample in Polars (much faster)
        max_inty_per_sample = features_with_names.group_by("sample_id").agg(
            pl.col("inty").max().alias("max_inty"),
        )

        # Join back and calculate alpha efficiently
        features_batch = (
            features_with_names.join(
                max_inty_per_sample,
                on="sample_id",
                how="left",
            )
            .with_columns(
                (pl.col("inty") / pl.col("max_inty") * alpha_max).alias("alpha"),
            )
            .drop("max_inty")
        )

        # Convert to pandas once after all Polars operations
        features_pd = features_batch.to_pandas()
    else:
        # Convert to pandas and add constant alpha
        features_pd = features_with_names.to_pandas()
        features_pd["alpha"] = alpha_max

    # OPTIMIZATION 9: NEW - Batch create all ColumnDataSources at once
    # Group all data by sample_id and create sources efficiently
    sources = {}
    renderers: list[Any] = []

    # Pre-compute color mapping to avoid repeated lookups
    color_values = {}
    sample_names = {}

    # Decide whether to show tqdm based on log level (show for INFO/DEBUG/TRACE)
    tqdm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    for uid in tqdm(sample_ids, desc="Plotting BPCs", disable=tqdm_disable):
        sample_data = features_pd[features_pd["sample_id"] == uid]
        if sample_data.empty:
            continue

        sample_name = sample_data["sample_name"].iloc[0]
        sample_names[uid] = sample_name
        color_values[uid] = color_map[uid]

    # OPTIMIZATION 10: Batch renderer creation with pre-computed values
    for uid in sample_ids:
        sample_data = features_pd[features_pd["sample_id"] == uid]
        if sample_data.empty:
            continue

        sample_name = sample_names[uid]
        color_values[uid]

        # OPTIMIZATION 11: Direct numpy array access for better performance
        source = ColumnDataSource(
            data={
                "rt": sample_data["rt"].values,
                "mz": sample_data["mz"].values,
                "inty": sample_data["inty"].values,
                "alpha": sample_data["alpha"].values,
                "sample": np.full(len(sample_data), sample_name, dtype=object),
                "sample_color": np.full(
                    len(sample_data),
                    color_values[uid],
                    dtype=object,
                ),
            },
        )

        sources[uid] = source

        # OPTIMIZATION 12: Use pre-computed color value
        # Create renderer with pre-computed values
        renderer: Any
        if size.lower() in ["dyn", "dynamic"]:
            renderer = p.circle(
                x="rt",
                y="mz",
                radius=markersize / 10,
                color=color_values[uid],
                alpha="alpha",
                legend_label=sample_name,
                source=source,
                muted_alpha=0.0,
            )
        else:
            renderer = p.scatter(
                x="rt",
                y="mz",
                size=markersize,
                color=color_values[uid],
                alpha="alpha",
                legend_label=sample_name,
                source=source,
                muted_alpha=0.0,
            )
        renderers.append(renderer)

    # OPTIMIZATION 13: Simplified hover tool for better performance with many samples
    if renderers:
        hover = HoverTool(
            tooltips=[
                ("sample", "@sample"),
                ("sample_color", "$color[swatch]:sample_color"),
                ("rt", "@rt{0.00}"),
                ("mz", "@mz{0.0000}"),
                ("intensity", "@inty{0.0e+0}"),
            ],
            renderers=renderers,
        )
        p.add_tools(hover)

    # Remove legend from plot
    # Only set legend properties if a legend was actually created to avoid Bokeh warnings
    if getattr(p, "legend", None) and len(p.legend) > 0:
        p.legend.visible = False

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "Samples 2D Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)
    return


def plot_bpc(
    self,
    samples=100,
    title: str | None = None,
    filename: str | None = None,
    width: int = 1000,
    height: int = 300,
    original: bool = False,
):
    """
    Plot Base Peak Chromatograms (BPC) for selected samples overlaid using Bokeh.

    This collects per-sample BPCs via `get_bpc(self, sample=uid)` and overlays them.
    Colors are mapped per-sample using the same Turbo256 palette as `plot_samples_2d`.
    Parameters:
        original (bool): If True, attempt to map RTs back to original RTs using `features_df`.
                         If False (default), return current/aligned RTs.
    """
    # Local imports to avoid heavy top-level deps / circular imports
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.plotting import figure

    from masster.study.helpers import get_bpc

    sample_ids = self._get_sample_ids(samples)
    if not sample_ids:
        self.logger.error("No valid sample_ids provided for BPC plotting.")
        return None

    # Debug: show which sample_ids we will process
    self.logger.debug(f"plot_bpc: sample_ids={sample_ids}")

    # Get sample colors from samples_df
    sample_colors = (
        self.samples_df.filter(pl.col("sample_id").is_in(sample_ids))
        .select(["sample_id", "sample_color"])
        .to_dict(as_series=False)
    )
    color_map = dict(
        zip(sample_colors["sample_id"], sample_colors["sample_color"], strict=False),
    )

    # If plotting original (uncorrected) RTs, use the requested title.
    if original:
        plot_title = "Base Peak Chromatogarms (uncorrected)"
    else:
        plot_title = title or "Base Peak Chromatograms"

    # Get rt_unit from the first chromatogram, default to "s" if not available
    rt_unit = "s"
    for uid in sample_ids:
        try:
            first_chrom = get_bpc(self, sample=uid, label=None, original=original)
            if hasattr(first_chrom, "rt_unit"):
                rt_unit = first_chrom.rt_unit
                break
        except Exception:
            continue

    p = figure(
        width=width,
        height=height,
        title=plot_title,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    p.xaxis.axis_label = f"Retention Time ({rt_unit})"
    p.yaxis.axis_label = "Intensity"

    renderers = []

    # Build sample name mapping once
    samples_info = None
    if hasattr(self, "samples_df") and self.samples_df is not None:
        try:
            samples_info = self.samples_df.to_pandas()
        except Exception:
            samples_info = None

    for uid in sample_ids:
        try:
            chrom = get_bpc(self, sample=uid, label=None, original=original)
        except Exception as e:
            # log and skip samples we can't compute BPC for
            self.logger.debug(f"Skipping sample {uid} for BPC: {e}")
            continue

        # extract arrays
        try:
            # prefer Chromatogram API
            chrom_dict = (
                chrom.to_dict()
                if hasattr(chrom, "to_dict")
                else {"rt": chrom.rt, "inty": chrom.inty}
            )
            rt = chrom_dict.get("rt")
            inty = chrom_dict.get("inty")
        except Exception:
            try:
                rt = chrom.rt
                inty = chrom.inty
            except Exception as e:
                self.logger.debug(f"Invalid chromatogram for sample {uid}: {e}")
                continue

        if rt is None or inty is None:
            continue

        # Ensure numpy arrays
        import numpy as _np

        rt = _np.asarray(rt)
        inty = _np.asarray(inty)
        if rt.size == 0 or inty.size == 0:
            continue

        # Sort by rt
        idx = _np.argsort(rt)
        rt = rt[idx]
        inty = inty[idx]

        sample_name = str(uid)
        if samples_info is not None:
            try:
                row = samples_info[samples_info["sample_id"] == uid]
                if not row.empty:
                    sample_name = row.iloc[0].get("sample_name", sample_name)
            except Exception:
                pass
        # Determine color for this sample early so we can log it
        color = color_map.get(uid, "#000000")

        # Debug: log sample processing details
        self.logger.debug(
            f"Processing BPC for sample_id={uid}, sample_name={sample_name}, rt_len={rt.size}, color={color}",
        )

        data = {
            "rt": rt,
            "inty": inty,
            "sample": [sample_name] * len(rt),
            "sample_color": [color] * len(rt),
        }
        src = ColumnDataSource(data)

        r_line = p.line(
            "rt",
            "inty",
            source=src,
            line_width=1,
            color=color,
            legend_label=str(sample_name),
        )
        p.scatter("rt", "inty", source=src, size=2, color=color, alpha=0.6)
        renderers.append(r_line)

    if not renderers:
        self.logger.warning("No BPC curves to plot for the selected samples.")
        return None

    hover = HoverTool(
        tooltips=[
            ("sample", "@sample"),
            ("sample_color", "$color[swatch]:sample_color"),
            ("rt", "@rt{0.00}"),
            ("inty", "@inty{0.00e0}"),
        ],
        renderers=renderers,
    )
    p.add_tools(hover)

    # Only set legend properties if a legend was actually created to avoid Bokeh warnings
    if getattr(p, "legend", None) and len(p.legend) > 0:
        p.legend.visible = False

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "BPC Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)

    return p


def plot_eic(
    self,
    mz,
    mz_tol=None,
    samples=100,
    title: str | None = None,
    filename: str | None = None,
    width: int = 1000,
    height: int = 300,
    original: bool = False,
):
    """Plot extracted ion chromatograms (EIC) for a target m/z across multiple samples.

    Extracts and overlays chromatograms for a specific m/z value (within a tolerance window)
    from selected samples in the study. This visualization is essential for verifying the
    presence, retention time, and peak shape of specific ions across different samples,
    particularly useful for targeted compound verification and quality control.

    The method retrieves raw data for each sample, performs on-the-fly EIC extraction,
    and generates an interactive Bokeh plot with automatic color-coding based on sample
    metadata. Chromatograms are overlaid with consistent colors matching other study
    visualizations.

    Args:
        mz (float): Target mass-to-charge ratio to extract. The method will extract all
            intensity values within ``mz ± mz_tol`` Da for each sample.
        mz_tol (float | None): m/z tolerance window in Daltons. If ``None``, uses the
            study's ``eic_mz_tol`` parameter (typically 0.01 Da). Larger values capture
            more intensity but may include off-target signals.
        samples (int | list): Number of samples to plot (if int) or specific sample IDs
            to include (if list). Default is ``100`` samples. When an int is provided,
            the first N samples from ``samples_df`` are used.
        title (str | None): Custom title for the plot. If ``None``, generates a
            descriptive title with the m/z value and tolerance.
        filename (str | None): Path to save the plot as an HTML file. If ``None``, displays
            the plot in Jupyter notebook. Relative paths are resolved relative to the
            study folder.
        width (int): Plot width in pixels. Default is ``1000``.
        height (int): Plot height in pixels. Default is ``300``.
        original (bool): Whether to use original (unprocessed) chromatographic data if
            available. Default is ``False`` (uses processed data). Currently not fully
            implemented in this method.

    Returns:
        bokeh.plotting.Figure: Interactive Bokeh figure object containing the overlaid
            EICs. Returns ``None`` if no valid chromatograms could be extracted. The
            figure includes:

            - Overlaid line plots for each sample with automatic color-coding
            - Scatter points on each chromatogram for precise peak identification
            - Interactive hover tooltips showing sample name, retention time, and intensity
            - Legend with sample names (initially hidden; toggle by clicking legend icon)
            - Pan, zoom, box zoom, reset, and save tools for data exploration

    Example:
        Plot EIC for a specific m/z across all samples::

            import masster as ms

            # Load study with processed samples
            study = ms.Study()
            study.load()

            # Plot EIC for a target compound (e.g., caffeine [M+H]+ at m/z 195.0877)
            study.plot_eic(mz=195.0877)

        Plot EIC with custom tolerance for selected samples::

            # Verify presence of a compound in specific samples
            study.plot_eic(
                mz=123.4567,
                mz_tol=0.01,
                samples=[1, 2, 3, 10, 15],
                title="Compound X verification"
            )

        Save EIC plot to file with custom dimensions::

            # Generate publication-quality EIC plot
            fig = study.plot_eic(
                mz=195.0877,
                mz_tol=0.005,
                filename="results/caffeine_eic.html",
                width=1200,
                height=400
            )

        Compare EIC across all samples in a batch::

            # Quality control: check consistency of internal standard
            study.plot_eic(
                mz=121.0508,  # Benzoic acid [M+H]+
                mz_tol=0.01,
                samples=len(study.samples_df),  # All samples
                title="Internal Standard: Benzoic Acid"
            )

        Extract specific samples using sample_id list::

            # Compare controls vs. treatments
            control_ids = [1, 2, 3]
            treatment_ids = [10, 11, 12]

            study.plot_eic(
                mz=195.0877,
                samples=control_ids + treatment_ids,
                title="Caffeine: Controls vs. Treatments"
            )

    Note:
        **Prerequisites**

        - Study must be loaded with ``study.load()`` or created with processed samples
        - Samples must have raw chromatographic data available (MS1 level)
        - Study's ``samples_df`` must contain sample metadata including colors

        **Targeted Extraction**

        The method performs on-the-fly extraction for the specified m/z window. Unlike
        feature-based methods that work with pre-detected peaks, ``plot_eic()`` directly
        queries raw data, making it ideal for:

        - Verifying expected compounds not automatically detected
        - Checking detection limits and signal-to-noise ratios
        - Quality control of specific internal standards
        - Investigating potential false negatives in feature detection

        **Multi-Sample Overlay**

        Chromatograms are automatically overlaid using colors from ``samples_df``:

        - Colors are consistent with other study visualizations (``plot_bpc``, etc.)
        - Legend shows sample names (hover over lines for detailed information)
        - Visual comparison helps identify retention time shifts or intensity variations
        - Missing or failed extractions are logged and skipped

        **Interactive Visualization**

        The Bokeh plot provides interactive features:

        - **Pan Tool**: Click and drag to move the view
        - **Wheel Zoom**: Scroll to zoom in/out on retention time axis
        - **Box Zoom**: Draw a box to zoom to specific region
        - **Hover Tool**: Displays sample name, RT, and intensity at cursor position
        - **Save Tool**: Export current view as PNG image
        - **Reset Tool**: Return to original view

        **Retention Time Units**

        Retention time units (seconds or minutes) are automatically detected from the
        first successfully extracted chromatogram and applied to the x-axis label.

        **Performance Considerations**

        - Extraction is performed on-the-fly for each sample (not pre-computed)
        - Large numbers of samples may take time to process
        - Wide m/z tolerance windows increase extraction time
        - Failed extractions (e.g., missing data) are logged and skipped

        **File Saving**

        When ``filename`` is provided:

        - HTML files preserve full interactivity
        - Relative paths are resolved relative to study folder
        - Absolute paths are used as-is
        - File saving is isolated to avoid Bokeh context conflicts

    See Also:
        get_eic : Extract raw EIC data for a single sample
        plot_bpc : Plot base peak chromatograms for samples
        Sample.get_eic : Extract EIC at sample level
        Sample.plot_eic : Plot EIC for individual sample
    """
    # Local imports to avoid heavy top-level deps / circular imports
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.plotting import figure

    from masster.study.helpers import get_eic

    # Use study's eic_mz_tol parameter as default if not provided
    if mz_tol is None:
        mz_tol = self.parameters.eic_mz_tol

    if mz is None:
        self.logger.error("mz must be provided for EIC plotting")
        return None

    sample_ids = self._get_sample_ids(samples)
    if not sample_ids:
        self.logger.error("No valid sample_ids provided for EIC plotting.")
        return None

    # Get sample colors from samples_df
    sample_colors = (
        self.samples_df.filter(pl.col("sample_id").is_in(sample_ids))
        .select(["sample_id", "sample_color"])
        .to_dict(as_series=False)
    )
    color_map = dict(
        zip(sample_colors["sample_id"], sample_colors["sample_color"], strict=False),
    )

    plot_title = title or f"Extracted Ion Chromatograms (m/z={mz:.4f} ± {mz_tol})"

    # Get rt_unit from the first chromatogram, default to "s" if not available
    rt_unit = "s"
    for uid in sample_ids:
        try:
            first_chrom = get_eic(self, sample=uid, mz=mz, mz_tol=mz_tol, label=None)
            if hasattr(first_chrom, "rt_unit"):
                rt_unit = first_chrom.rt_unit
                break
        except Exception:
            continue

    p = figure(
        width=width,
        height=height,
        title=plot_title,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    p.xaxis.axis_label = f"Retention Time ({rt_unit})"
    p.yaxis.axis_label = "Intensity"

    renderers = []

    # Build sample name mapping once
    samples_info = None
    if hasattr(self, "samples_df") and self.samples_df is not None:
        try:
            samples_info = self.samples_df.to_pandas()
        except Exception:
            samples_info = None

    for uid in sample_ids:
        try:
            chrom = get_eic(self, sample=uid, mz=mz, mz_tol=mz_tol, label=None)
        except Exception as e:
            # log and skip samples we can't compute EIC for
            self.logger.debug(f"Skipping sample {uid} for EIC: {e}")
            continue

        # extract arrays
        try:
            # prefer Chromatogram API
            chrom_dict = (
                chrom.to_dict()
                if hasattr(chrom, "to_dict")
                else {"rt": chrom.rt, "inty": chrom.inty}
            )
            rt = chrom_dict.get("rt")
            inty = chrom_dict.get("inty")
        except Exception:
            try:
                rt = chrom.rt
                inty = chrom.inty
            except Exception as e:
                self.logger.debug(f"Invalid chromatogram for sample {uid}: {e}")
                continue

        if rt is None or inty is None:
            continue

        import numpy as _np

        rt = _np.asarray(rt)
        inty = _np.asarray(inty)
        if rt.size == 0 or inty.size == 0:
            continue

        # Sort by rt
        idx = _np.argsort(rt)
        rt = rt[idx]
        inty = inty[idx]

        sample_name = str(uid)
        if samples_info is not None:
            try:
                row = samples_info[samples_info["sample_id"] == uid]
                if not row.empty:
                    sample_name = row.iloc[0].get("sample_name", sample_name)
            except Exception:
                pass

        color = color_map.get(uid, "#000000")

        data = {
            "rt": rt,
            "inty": inty,
            "sample": [sample_name] * len(rt),
            "sample_color": [color] * len(rt),
        }
        src = ColumnDataSource(data)

        r_line = p.line(
            "rt",
            "inty",
            source=src,
            line_width=1,
            color=color,
            legend_label=str(sample_name),
        )
        p.scatter("rt", "inty", source=src, size=2, color=color, alpha=0.6)
        renderers.append(r_line)

    if not renderers:
        self.logger.warning("No EIC curves to plot for the selected samples.")
        return None

    hover = HoverTool(
        tooltips=[
            ("sample", "@sample"),
            ("sample_color", "$color[swatch]:sample_color"),
            ("rt", "@rt{0.00}"),
            ("inty", "@inty{0.0e0}"),
        ],
        renderers=renderers,
    )
    p.add_tools(hover)

    if getattr(p, "legend", None) and len(p.legend) > 0:
        p.legend.visible = False

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "EIC Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)

    return p


def plot_rt_correction(
    self,
    samples=200,
    title: str | None = None,
    filename: str | None = None,
    width: int = 1000,
    height: int = 300,
):
    """
    Plot RT correction per sample: (rt - rt_original) vs rt overlaid for selected samples.

    Only features with filled==False are used for the RT correction plot.
    This uses the same color mapping as `plot_bpc` so curves for the same samples match.
    """
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.plotting import figure

    # Validate features dataframe
    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found. Load features first.")
        return None

    if "rt_original" not in self.features_df.columns:
        self.logger.error(
            "Column 'rt_original' not found in features_df. Alignment/backup RTs missing.",
        )
        return None

    sample_ids = self._get_sample_ids(samples)
    if not sample_ids:
        self.logger.error("No valid sample_ids provided for RT correction plotting.")
        return None

    # Get sample colors from samples_df
    sample_colors = (
        self.samples_df.filter(pl.col("sample_id").is_in(sample_ids))
        .select(["sample_id", "sample_color"])
        .to_dict(as_series=False)
    )
    color_map = dict(
        zip(sample_colors["sample_id"], sample_colors["sample_color"], strict=False),
    )

    # For RT correction plots, default to "s" since we're working with features_df directly
    rt_unit = "s"

    p = figure(
        width=width,
        height=height,
        title=title or "RT correction",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    p.xaxis.axis_label = f"Retention Time ({rt_unit})"
    p.yaxis.axis_label = "RT - RT_original (s)"

    # Create sample name lookup dictionary from samples_df (all in Polars)
    sample_names_dict = {}
    if hasattr(self, "samples_df") and self.samples_df is not None:
        try:
            sample_name_mapping = self.samples_df.filter(
                pl.col("sample_id").is_in(sample_ids),
            ).select(
                [
                    "sample_id",
                    "sample_name",
                ],
            )
            sample_names_dict = dict(
                zip(
                    sample_name_mapping["sample_id"].to_list(),
                    sample_name_mapping["sample_name"].to_list(),
                    strict=False,
                ),
            )
        except Exception:
            pass

    renderers = []

    # Check sample identifier column
    if "sample_id" not in self.features_df.columns:
        if "sample_name" in self.features_df.columns:
            sample_id_col = "sample_name"
        else:
            self.logger.debug("No sample identifier column in features_df")
            return None
    else:
        sample_id_col = "sample_id"

    # OPTIMIZED: Filter once, group once instead of per-sample filtering
    try:
        # Filter all data once for selected samples and required conditions
        all_sample_feats = self.features_df.filter(
            pl.col(sample_id_col).is_in(sample_ids),
        )

        if all_sample_feats.is_empty():
            self.logger.warning("No features found for the selected samples.")
            return None

        # Filter to only use features with filled==False if column exists
        if "filled" in all_sample_feats.columns:
            all_sample_feats = all_sample_feats.filter(~pl.col("filled"))
            if all_sample_feats.is_empty():
                self.logger.warning(
                    "No non-filled features found for the selected samples.",
                )
                return None

        # Check required columns
        if (
            "rt" not in all_sample_feats.columns
            or "rt_original" not in all_sample_feats.columns
        ):
            self.logger.error(
                "Required columns 'rt' or 'rt_original' not found in features_df.",
            )
            return None

        # Filter nulls, add delta column, and sort - all in one operation
        all_sample_feats = (
            all_sample_feats.filter(
                pl.col("rt").is_not_null() & pl.col("rt_original").is_not_null(),
            )
            .with_columns([(pl.col("rt") - pl.col("rt_original")).alias("delta")])
            .sort([sample_id_col, "rt"])
        )

        if all_sample_feats.is_empty():
            self.logger.warning("No valid RT data found for the selected samples.")
            return None

        # Group by sample and process each group (much faster than individual filtering)
        for (sample_id,), sample_group in all_sample_feats.group_by(sample_id_col):
            if sample_group.is_empty():
                continue

            # Extract arrays directly from Polars
            rt = sample_group["rt"].to_numpy()
            delta = sample_group["delta"].to_numpy()

            # Get sample name efficiently from pre-built dictionary
            sample_name = sample_names_dict.get(sample_id, str(sample_id))
            color = color_map.get(sample_id, "#000000")

            data = {
                "rt": rt,
                "delta": delta,
                "sample": [sample_name] * len(rt),
                "sample_color": [color] * len(rt),
            }
            src = ColumnDataSource(data)

            r_line = p.line("rt", "delta", source=src, line_width=1, color=color)
            p.scatter("rt", "delta", source=src, size=2, color=color, alpha=0.6)
            renderers.append(r_line)

    except Exception as e:
        self.logger.error(f"Error in optimized RT correction plotting: {e}")
        return None

    if not renderers:
        self.logger.warning("No RT correction curves to plot for the selected samples.")
        return None

    hover = HoverTool(
        tooltips=[
            ("sample", "@sample"),
            ("sample_color", "$color[swatch]:sample_color"),
            ("rt", "@rt{0.00}"),
            ("rt - rt_original", "@delta{0.00}"),
        ],
        renderers=renderers,
    )
    p.add_tools(hover)

    # Only set legend properties if a legend was actually created to avoid Bokeh warnings
    if getattr(p, "legend", None) and len(p.legend) > 0:
        p.legend.visible = False

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(
            p,
            filename,
            abs_filename,
            self.logger,
            "RT Correction Plot",
        )
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)

    return p


def plot_chrom(
    self,
    uids=None,
    samples=100,
    filename=None,
    aligned=True,
    width=800,
    height=300,
):
    cons_uids = self._get_consensus_ids(uids)
    sample_ids = self._get_sample_ids(samples)

    chroms = self.get_chrom(uids=cons_uids, samples=sample_ids)

    if chroms is None or chroms.is_empty():
        self.logger.error("No chromatogram data found.")
        return

    # Get sample colors for alignment plots
    # Need to map sample names to colors since chromatogram data uses sample names as columns
    sample_names = [col for col in chroms.columns if col not in ["consensus_id"]]
    if not sample_names:
        self.logger.error("No sample names found in chromatogram data.")
        return

    # Create color mapping by getting sample_color for each sample_name
    samples_info = self.samples_df.select(
        ["sample_name", "sample_color", "sample_id"],
    ).to_dict(as_series=False)
    sample_name_to_color = dict(
        zip(samples_info["sample_name"], samples_info["sample_color"], strict=False),
    )
    sample_name_to_uid = dict(
        zip(samples_info["sample_name"], samples_info["sample_id"], strict=False),
    )
    color_map = {
        name: sample_name_to_color.get(name, "#1f77b4") for name in sample_names
    }  # fallback to blue

    plots = []
    self.logger.info(f"Plotting {chroms.shape[0]} chromatograms...")
    tqdm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for row in tqdm(
        chroms.iter_rows(named=True),
        total=chroms.shape[0],
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Plot chromatograms",
        disable=tqdm_disable,
    ):
        consensus_id = row["consensus_id"]  # Get consensus_id from the row
        consensus_id = consensus_id  # Use the same value for consensus_id
        curves = []
        rt_min = np.inf
        rt_max = 0
        for sample in sample_names:
            chrom = row[sample]
            if chrom is not None:
                # check if chrom is nan
                if isinstance(chrom, float) and np.isnan(chrom):
                    continue

                chrom = chrom.to_dict()
                rt = chrom["rt"].copy()
                if len(rt) == 0:
                    continue
                if aligned and "rt_shift" in chrom:
                    rt_shift = chrom["rt_shift"]
                    if rt_shift is not None:
                        # Convert to numpy array if it's a list, then add scalar
                        if isinstance(rt, list):
                            rt = np.array(rt)
                        rt = rt + rt_shift  # Add scalar to array

                # update rt_min and rt_max
                rt_min = min(rt_min, rt[0])
                rt_max = max(rt_max, rt[-1])

                inty = chrom["inty"]

                # Convert both rt and inty to numpy arrays if they're lists
                if isinstance(rt, list):
                    rt = np.array(rt)
                if isinstance(inty, list):
                    inty = np.array(inty)

                # Ensure both rt and inty are arrays and have the same length and are not empty
                if rt.size > 0 and inty.size > 0 and rt.shape == inty.shape:
                    # sort rt and inty by rt
                    sorted_indices = np.argsort(rt)
                    rt = rt[sorted_indices]
                    inty = inty[sorted_indices]

                    # Get sample uid for this sample name
                    sample_id = sample_name_to_uid.get(sample)
                    sample_color = color_map.get(sample, "#1f77b4")

                    # Create arrays with sample information for hover tooltips
                    sample_names_array = [sample] * len(rt)
                    sample_ids_array = [sample_id] * len(rt)
                    sample_colors_array = [sample_color] * len(rt)

                    curve = hv.Curve(
                        (
                            rt,
                            inty,
                            sample_names_array,
                            sample_ids_array,
                            sample_colors_array,
                        ),
                        kdims=["RT"],
                        vdims=["inty", "sample_name", "sample_id", "sample_color"],
                    ).opts(
                        color=color_map[sample],
                        line_width=1,
                        tools=["hover"],
                        hover_tooltips=[
                            ("RT", "@RT{0.00}"),
                            ("Intensity", "@inty{0,0}"),
                            ("Sample Name", "@sample_name"),
                            ("Sample UID", "@sample_id"),
                            ("Sample Color", "$color[swatch]:sample_color"),
                        ],
                    )
                    curves.append(curve)

                    if "feature_start" in chrom and "feature_end" in chrom:
                        # Add vertical lines for feature start and end
                        feature_start = chrom["feature_start"]
                        feature_end = chrom["feature_end"]
                        if aligned and "rt_shift" in chrom:
                            rt_shift = chrom["rt_shift"]
                            if rt_shift is not None:
                                if feature_start is not None:
                                    feature_start += rt_shift
                                if feature_end is not None:
                                    feature_end += rt_shift
                        if feature_start is not None and feature_start < rt_min:
                            rt_min = feature_start
                        if feature_end is not None and feature_end > rt_max:
                            rt_max = feature_end
                        # Add vertical lines to the curves
                        if feature_start is not None:
                            curves.append(
                                hv.VLine(feature_start).opts(
                                    color=color_map[sample],
                                    line_dash="dotted",
                                    line_width=1,
                                ),
                            )
                        if feature_end is not None:
                            curves.append(
                                hv.VLine(feature_end).opts(
                                    color=color_map[sample],
                                    line_dash="dotted",
                                    line_width=1,
                                ),
                            )
        if curves:
            # find row in consensus_df with consensus_id
            consensus_row = self.consensus_df.filter(
                pl.col("consensus_id") == consensus_id,
            )
            rt_start_mean = consensus_row["rt_start_mean"][0]
            rt_end_mean = consensus_row["rt_end_mean"][0]
            # Add vertical lines to overlay
            curves.append(hv.VLine(rt_start_mean).opts(color="black", line_width=2))
            curves.append(hv.VLine(rt_end_mean).opts(color="black", line_width=2))

            overlay = hv.Overlay(curves).opts(
                height=height,
                width=width,
                title=f"Consensus UID: {consensus_id}, mz: {consensus_row['mz'][0]:.4f}, rt: {consensus_row['rt'][0]:.2f}{' (aligned)' if aligned else ''}",
                xlim=(rt_min, rt_max),
                shared_axes=False,
            )
            plots.append(overlay)

    if not plots:
        self.logger.warning("No valid chromatogram curves to plot.")
        return

    # stack vertically.
    # Stack all plots vertically in a Panel column
    layout = panel.Column(*[panel.panel(plot) for plot in plots])

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated Panel saving
        _isolated_save_panel_plot(
            panel.panel(layout),
            filename,
            abs_filename,
            self.logger,
            "Chromatogram Plot",
        )
    else:
        # Show in notebook when no filename provided
        # Convert Panel layout to Bokeh layout for consistent isolated display
        try:
            panel_obj = panel.panel(layout)
            bokeh_layout = panel_obj.get_root()
            # Use the regular isolated show method for Bokeh objects
            _isolated_show_notebook(bokeh_layout)
        except Exception:
            # Fallback to Panel display if conversion fails
            _isolated_show_panel_notebook(panel.panel(layout))


def plot_consensus_stats(
    self,
    filename=None,
    width=840,  # Reduced from 1200 (30% smaller)
    height=None,
    alpha=0.6,
    bins=30,
    n_cols=4,
):
    """
    Plot histograms/distributions for specific consensus statistics in the requested order.

    Shows the following properties in order:
    1. rt: Retention time
    2. rt_delta_mean: Chromatogram retention time delta
    3. mz: Mass-to-charge ratio
    4. mz_range: Mass range (mz_max - mz_min)
    5. log10_inty_mean: Log10 of mean intensity
    6. number_samples: Number of samples
    7. number_ms2: Number of MS2 spectra
    8. charge_mean: Mean charge
    9. quality: Feature quality
    10. chrom_coherence_mean: Mean chromatographic coherence
    11. chrom_height_scaled_mean: Mean scaled chromatographic height
    12. chrom_prominence_scaled_mean: Mean scaled chromatographic prominence

    Parameters:
        filename (str, optional): Output filename for saving the plot
        width (int): Overall width of the plot (default: 840)
        height (int, optional): Overall height of the plot (auto-calculated if None)
        alpha (float): Histogram transparency (default: 0.6)
        bins (int): Number of histogram bins (default: 30)
        n_cols (int): Number of columns in the grid layout (default: 4)
    """
    from bokeh.layouts import gridplot
    from bokeh.plotting import figure
    import numpy as np
    import polars as pl

    # Get the consensus statistics data using the new helper method
    data_df = self.get_consensus_stats()

    if data_df is None or data_df.is_empty():
        self.logger.error("No consensus statistics data available.")
        return None

    # Remove consensus_id column for plotting (keep only numeric columns)
    if "consensus_id" in data_df.columns:
        data_df_clean = data_df.drop("consensus_id")
    else:
        data_df_clean = data_df

    # Define specific columns to plot in the exact order requested (excluding consensus_id)
    desired_columns = [
        "rt",
        "rt_delta_mean",
        "mz",
        "mz_range",  # mz_max-mz_min
        "log10_inty_mean",  # log10(inty_mean)
        "number_samples",
        "number_ms2",
        "charge_mean",
        "quality",
        "chrom_coherence_mean",
        "chrom_height_scaled_mean",
        "chrom_prominence_scaled_mean",
    ]

    # Filter to only include columns that exist in the dataframe, preserving order
    numeric_columns = [col for col in desired_columns if col in data_df_clean.columns]

    # Check if the numeric columns are actually numeric
    final_numeric_columns = []
    for col in numeric_columns:
        dtype = data_df_clean[col].dtype
        if dtype in [
            pl.Int8,
            pl.Int16,
            pl.Int32,
            pl.Int64,
            pl.UInt8,
            pl.UInt16,
            pl.UInt32,
            pl.UInt64,
            pl.Float32,
            pl.Float64,
        ]:
            final_numeric_columns.append(col)

    numeric_columns = final_numeric_columns

    if len(numeric_columns) == 0:
        self.logger.error(
            f"None of the requested consensus statistics columns were found or are numeric. Available columns: {list(data_df_clean.columns)}",
        )
        return None

    self.logger.debug(
        f"Creating distribution plots for {len(numeric_columns)} specific consensus columns: {numeric_columns}",
    )

    # Select only the numeric columns for plotting
    data_df_clean = data_df_clean.select(numeric_columns)

    # Check if all numeric columns are empty
    all_columns_empty = True
    for col in numeric_columns:
        # Check if column has any non-null, finite values
        non_null_count = (
            data_df_clean[col]
            .filter(
                data_df_clean[col].is_not_null()
                & (
                    data_df_clean[col].is_finite()
                    if data_df_clean[col].dtype in [pl.Float32, pl.Float64]
                    else pl.lit(True)
                ),
            )
            .len()
        )

        if non_null_count > 0:
            all_columns_empty = False
            break

    if all_columns_empty:
        self.logger.error("All numeric columns contain only NaN/infinite values.")
        return None

    # Calculate grid dimensions
    n_plots = len(numeric_columns)
    n_rows = (n_plots + n_cols - 1) // n_cols  # Ceiling division

    # Auto-calculate height if not provided
    if height is None:
        plot_height = 210  # Reduced from 300 (30% smaller)
        height = plot_height * n_rows + 56  # Reduced from 80 (30% smaller)
    else:
        plot_height = (height - 56) // n_rows  # Reduced padding (30% smaller)

    plot_width = (width - 56) // n_cols  # Reduced padding (30% smaller)

    # Create plots grid
    plots = []
    current_row = []

    for i, col in enumerate(numeric_columns):
        # Check if this column should use log scale for y-axis
        y_axis_type = "log" if col in ["number_samples", "number_ms2"] else "linear"

        # Create histogram for this column
        p = figure(
            width=plot_width,
            height=plot_height,
            title=col,
            toolbar_location="above",
            tools="pan,wheel_zoom,box_zoom,reset,save",
            y_axis_type=y_axis_type,
        )

        # Set white background
        p.background_fill_color = "white"
        p.border_fill_color = "white"

        # Calculate histogram using Polars
        # Get valid (non-null, finite) values for this column
        if data_df_clean[col].dtype in [pl.Float32, pl.Float64]:
            valid_values = data_df_clean.filter(
                data_df_clean[col].is_not_null() & data_df_clean[col].is_finite(),
            )[col]
        else:
            valid_values = data_df_clean.filter(data_df_clean[col].is_not_null())[col]

        if valid_values.len() == 0:
            self.logger.warning(f"No valid values for column {col}")
            continue

        # Convert to numpy for histogram calculation
        values_array = valid_values.to_numpy()
        hist, edges = np.histogram(values_array, bins=bins)

        # Handle log y-axis: replace zero counts with small positive values
        if y_axis_type == "log":
            # Replace zero counts with a small value (1e-1) to make them visible on log scale
            hist_log_safe = np.where(hist == 0, 0.1, hist)
            bottom_val = 0.1  # Use small positive value for bottom on log scale
        else:
            hist_log_safe = hist
            bottom_val = 0

        # Create histogram bars
        p.quad(
            top=hist_log_safe,
            bottom=bottom_val,
            left=edges[:-1],
            right=edges[1:],
            fill_color="steelblue",
            line_color="white",
            alpha=alpha,
        )

        # Style the plot
        p.title.text_font_size = "10pt"  # Reduced from 12pt
        p.xaxis.axis_label = ""  # Remove x-axis title
        p.grid.grid_line_alpha = 0.3  # Show y-axis grid with transparency
        p.grid.grid_line_color = "gray"
        p.grid.grid_line_dash = [6, 4]  # Dashed grid lines
        p.xgrid.visible = False  # Hide x-axis grid
        p.outline_line_color = None  # Remove gray border around plot area

        # Remove y-axis label but keep y-axis visible
        p.yaxis.axis_label = ""

        current_row.append(p)

        # If we've filled a row or reached the end, add the row to plots
        if len(current_row) == n_cols or i == n_plots - 1:
            # Fill remaining spots in the last row with None if needed
            while len(current_row) < n_cols and i == n_plots - 1:
                current_row.append(None)
            plots.append(current_row)
            current_row = []

    # Create grid layout with white background
    grid = gridplot(plots, toolbar_location="above", merge_tools=True)

    # The background should be white by default in Bokeh
    # Individual plots already have white backgrounds set above

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(
            grid,
            filename,
            abs_filename,
            self.logger,
            "Consensus Stats Plot",
        )
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(grid)
    return grid


def plot_samples_pca(
    self,
    filename=None,
    width=500,
    height=450,
    alpha=0.8,
    markersize=6,
    n_components=2,
    colorby=None,
    title="PCA of Consensus Matrix",
):
    """
    Plot PCA (Principal Component Analysis) of the consensus matrix using Bokeh.

    Parameters:
        filename (str, optional): Output filename for saving the plot
        width (int): Plot width (default: 800)
        height (int): Plot height (default: 600)
        alpha (float): Point transparency (default: 0.8)
        markersize (int): Size of points (default: 8)
        n_components (int): Number of PCA components to compute (default: 2)
        color_by (str, optional): Column from samples_df to color points by
        title (str): Plot title (default: "PCA of Consensus Matrix")
    """
    from bokeh.models import ColorBar, ColumnDataSource, HoverTool, LinearColorMapper
    from bokeh.palettes import Category20, viridis
    from bokeh.plotting import figure
    from bokeh.transform import factor_cmap
    import numpy as np
    import pandas as pd
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    # Check if consensus matrix and samples_df exist
    try:
        consensus_matrix = self.get_consensus_matrix()
        samples_df = self.samples_df
    except Exception as e:
        self.logger.error(f"Error getting consensus matrix or samples_df: {e}")
        return None

    if consensus_matrix is None or consensus_matrix.shape[0] == 0:
        self.logger.error(
            "No consensus matrix available. Run merge/find_consensus first.",
        )
        return None

    if samples_df is None or samples_df.is_empty():
        self.logger.error("No samples dataframe available.")
        return None

    self.logger.debug(
        f"Performing PCA on consensus matrix with shape: {consensus_matrix.shape}",
    )

    # Extract only the sample columns (exclude consensus_id column)
    sample_cols = [col for col in consensus_matrix.columns if col != "consensus_id"]

    # Convert consensus matrix to numpy, excluding the consensus_id column
    if hasattr(consensus_matrix, "select"):
        # Polars DataFrame
        matrix_data = consensus_matrix.select(sample_cols).to_numpy()
    else:
        # Pandas DataFrame or other - drop consensus_id column
        matrix_sample_data = consensus_matrix.drop(
            columns=["consensus_id"],
            errors="ignore",
        )
        if hasattr(matrix_sample_data, "values"):
            matrix_data = matrix_sample_data.values
        elif hasattr(matrix_sample_data, "to_numpy"):
            matrix_data = matrix_sample_data.to_numpy()
        else:
            matrix_data = np.array(matrix_sample_data)

    # Transpose matrix so samples are rows and features are columns
    matrix_data = matrix_data.T

    # Handle missing values by replacing with 0
    matrix_data = np.nan_to_num(matrix_data, nan=0.0, posinf=0.0, neginf=0.0)

    # Standardize the data
    scaler = StandardScaler()
    matrix_scaled = scaler.fit_transform(matrix_data)

    # Perform PCA
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(matrix_scaled)

    # Get explained variance ratios
    explained_var = pca.explained_variance_ratio_

    self.logger.debug(f"PCA explained variance ratios: {explained_var}")

    # Convert samples_df to pandas for easier manipulation
    samples_pd = samples_df.to_pandas()

    # Create dataframe with PCA results and sample information
    pca_df = pd.DataFrame(
        {
            "PC1": pca_result[:, 0],
            "PC2": pca_result[:, 1] if n_components > 1 else np.zeros(len(pca_result)),
        },
    )

    # Add sample information to PCA dataframe
    if len(samples_pd) == len(pca_df):
        for col in samples_pd.columns:
            pca_df[col] = samples_pd[col].values
    else:
        self.logger.warning(
            f"Sample count mismatch: samples_df has {len(samples_pd)} rows, "
            f"but consensus matrix has {len(pca_df)} samples",
        )

    # Prepare color mapping
    color_mapper = None

    if colorby and colorby in pca_df.columns:
        unique_values = pca_df[colorby].unique()

        # Handle categorical vs numeric coloring
        if pca_df[colorby].dtype in ["object", "string", "category"]:
            # Categorical coloring
            if len(unique_values) <= 20:
                palette = Category20[min(20, max(3, len(unique_values)))]
            else:
                palette = viridis(min(256, len(unique_values)))
            color_mapper = factor_cmap(colorby, palette, unique_values)
        else:
            # Numeric coloring
            palette = viridis(256)
            color_mapper = LinearColorMapper(
                palette=palette,
                low=pca_df[colorby].min(),
                high=pca_df[colorby].max(),
            )

    # Create Bokeh plot
    p = figure(
        width=width,
        height=height,
        title=f"{title} (PC1: {explained_var[0]:.1%}, PC2: {explained_var[1]:.1%})",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )

    p.grid.visible = False
    p.xaxis.axis_label = f"PC1 ({explained_var[0]:.1%} variance)"
    p.yaxis.axis_label = f"PC2 ({explained_var[1]:.1%} variance)"

    # Create data source
    source = ColumnDataSource(pca_df)

    # Create scatter plot
    if color_mapper:
        if isinstance(color_mapper, LinearColorMapper):
            scatter = p.scatter(
                "PC1",
                "PC2",
                size=markersize,
                alpha=alpha,
                color={"field": colorby, "transform": color_mapper},
                source=source,
            )
            # Add colorbar for numeric coloring
            color_bar = ColorBar(color_mapper=color_mapper, width=8, location=(0, 0))
            p.add_layout(color_bar, "right")
        else:
            scatter = p.scatter(
                "PC1",
                "PC2",
                size=markersize,
                alpha=alpha,
                color=color_mapper,
                source=source,
                legend_field=colorby,
            )
    # If no color_by provided, use sample_color column from samples_df
    elif "sample_id" in pca_df.columns or "sample_name" in pca_df.columns:
        # Choose the identifier to map colors by
        id_col = "sample_id" if "sample_id" in pca_df.columns else "sample_name"

        # Get colors from samples_df based on the identifier
        if id_col == "sample_id":
            sample_colors = (
                self.samples_df.filter(
                    pl.col("sample_id").is_in(pca_df[id_col].unique()),
                )
                .select(["sample_id", "sample_color"])
                .to_dict(as_series=False)
            )
            color_map = dict(
                zip(
                    sample_colors["sample_id"],
                    sample_colors["sample_color"],
                    strict=False,
                ),
            )
        else:  # sample_name
            sample_colors = (
                self.samples_df.filter(
                    pl.col("sample_name").is_in(pca_df[id_col].unique()),
                )
                .select(["sample_name", "sample_color"])
                .to_dict(as_series=False)
            )
            color_map = dict(
                zip(
                    sample_colors["sample_name"],
                    sample_colors["sample_color"],
                    strict=False,
                ),
            )

        # Map colors into dataframe
        pca_df["color"] = [
            color_map.get(x, "#1f77b4") for x in pca_df[id_col]
        ]  # fallback to blue
        # Update the ColumnDataSource with new color column
        source = ColumnDataSource(pca_df)
        scatter = p.scatter(
            "PC1",
            "PC2",
            size=markersize,
            alpha=alpha,
            color="color",
            source=source,
        )
    else:
        scatter = p.scatter(
            "PC1",
            "PC2",
            size=markersize,
            alpha=alpha,
            color="blue",
            source=source,
        )

    # Create comprehensive hover tooltips with all sample information
    tooltip_list = []

    # Columns to exclude from tooltips (file paths and internal/plot fields)
    excluded_cols = {
        "file_source",
        "file_path",
        "sample_path",
        "sample_id",
        "PC1",
        "PC2",
        "ms1",
        "ms2",
        "size",
    }

    # Add all sample dataframe columns to tooltips, skipping excluded ones
    for col in samples_pd.columns:
        if col in excluded_cols:
            continue
        if col in pca_df.columns:
            if col == "sample_color":
                # Display sample_color as a colored swatch
                tooltip_list.append(("color", "$color[swatch]:sample_color"))
            elif pca_df[col].dtype in ["float64", "float32"]:
                tooltip_list.append((col, f"@{col}{{0.00}}"))
            else:
                tooltip_list.append((col, f"@{col}"))

    hover = HoverTool(
        tooltips=tooltip_list,
        renderers=[scatter],
    )
    p.add_tools(hover)

    # Add legend if using categorical coloring
    if color_mapper and not isinstance(color_mapper, LinearColorMapper) and colorby:
        # Only set legend properties if legends exist (avoid Bokeh warning when none created)
        if getattr(p, "legend", None) and len(p.legend) > 0:
            p.legend.location = "top_left"
            p.legend.click_policy = "hide"

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "PCA Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)
    return p


def plot_samples_umap(
    self,
    filename=None,
    width=500,
    height=450,
    alpha=0.8,
    markersize=6,
    n_components=2,
    colorby=None,
    title="UMAP of Consensus Matrix",
    n_neighbors=15,
    min_dist=0.1,
    metric="euclidean",
    random_state=42,
):
    """
    Plot UMAP (Uniform Manifold Approximation and Projection) of the consensus matrix using Bokeh.

    Parameters:
        filename (str, optional): Output filename for saving the plot
        width (int): Plot width (default: 500)
        height (int): Plot height (default: 450)
        alpha (float): Point transparency (default: 0.8)
        markersize (int): Size of points (default: 6)
        n_components (int): Number of UMAP components to compute (default: 2)
        colorby (str, optional): Column from samples_df to color points by
        title (str): Plot title (default: "UMAP of Consensus Matrix")
        n_neighbors (int): Number of neighbors for UMAP (default: 15)
        min_dist (float): Minimum distance for UMAP (default: 0.1)
        metric (str): Distance metric for UMAP (default: "euclidean")
        random_state (int or None): Random state for reproducibility (default: 42).
            - Use an integer (e.g., 42) for reproducible results (slower, single-threaded)
            - Use None for faster computation with multiple cores (non-reproducible)

    Note:
        Setting random_state forces single-threaded computation but ensures reproducible results.
        Set random_state=None to enable parallel processing for faster computation.
    """
    try:
        import umap
    except ImportError:
        self.logger.error(
            "UMAP not available. Please install umap-learn: pip install umap-learn",
        )
        return None

    from bokeh.models import ColorBar, ColumnDataSource, HoverTool, LinearColorMapper
    from bokeh.palettes import Category20, viridis
    from bokeh.plotting import figure
    from bokeh.transform import factor_cmap
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import StandardScaler

    # Check if consensus matrix and samples_df exist
    try:
        consensus_matrix = self.get_consensus_matrix()
        samples_df = self.samples_df
    except Exception as e:
        self.logger.error(f"Error getting consensus matrix or samples_df: {e}")
        return None

    if consensus_matrix is None or consensus_matrix.shape[0] == 0:
        self.logger.error(
            "No consensus matrix available. Run merge/find_consensus first.",
        )
        return None

    if samples_df is None or samples_df.is_empty():
        self.logger.error("No samples dataframe available.")
        return None

    self.logger.debug(
        f"Performing UMAP on consensus matrix with shape: {consensus_matrix.shape}",
    )

    # Extract only the sample columns (exclude consensus_id column)
    sample_cols = [col for col in consensus_matrix.columns if col != "consensus_id"]

    # Convert consensus matrix to numpy, excluding the consensus_id column
    if hasattr(consensus_matrix, "select"):
        # Polars DataFrame
        matrix_data = consensus_matrix.select(sample_cols).to_numpy()
    else:
        # Pandas DataFrame or other - drop consensus_id column
        matrix_sample_data = consensus_matrix.drop(
            columns=["consensus_id"],
            errors="ignore",
        )
        if hasattr(matrix_sample_data, "values"):
            matrix_data = matrix_sample_data.values
        elif hasattr(matrix_sample_data, "to_numpy"):
            matrix_data = matrix_sample_data.to_numpy()
        else:
            matrix_data = np.array(matrix_sample_data)

    # Transpose matrix so samples are rows and features are columns
    matrix_data = matrix_data.T

    # Handle missing values by replacing with 0
    matrix_data = np.nan_to_num(matrix_data, nan=0.0, posinf=0.0, neginf=0.0)

    # Standardize the data
    scaler = StandardScaler()
    matrix_scaled = scaler.fit_transform(matrix_data)

    # Perform UMAP
    reducer = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric=metric,
        random_state=random_state,
        n_jobs=1,
    )
    umap_result = reducer.fit_transform(matrix_scaled)

    self.logger.debug(f"UMAP completed with shape: {umap_result.shape}")

    # Convert samples_df to pandas for easier manipulation
    samples_pd = samples_df.to_pandas()

    # Create dataframe with UMAP results and sample information
    umap_df = pd.DataFrame(
        {
            "UMAP1": umap_result[:, 0],
            "UMAP2": umap_result[:, 1]
            if n_components > 1
            else np.zeros(len(umap_result)),
        },
    )

    # Add sample information to UMAP dataframe
    if len(samples_pd) == len(umap_df):
        for col in samples_pd.columns:
            umap_df[col] = samples_pd[col].values
    else:
        self.logger.warning(
            f"Sample count mismatch: samples_df has {len(samples_pd)} rows, "
            f"but consensus matrix has {len(umap_df)} samples",
        )

    # Prepare color mapping
    color_mapper = None

    if colorby and colorby in umap_df.columns:
        unique_values = umap_df[colorby].unique()

        # Handle categorical vs numeric coloring
        if umap_df[colorby].dtype in ["object", "string", "category"]:
            # Categorical coloring
            if len(unique_values) <= 20:
                palette = Category20[min(20, max(3, len(unique_values)))]
            else:
                palette = viridis(min(256, len(unique_values)))
            color_mapper = factor_cmap(colorby, palette, unique_values)
        else:
            # Numeric coloring
            palette = viridis(256)
            color_mapper = LinearColorMapper(
                palette=palette,
                low=umap_df[colorby].min(),
                high=umap_df[colorby].max(),
            )

    # Create Bokeh plot
    p = figure(
        width=width,
        height=height,
        title=f"{title}",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )

    p.grid.visible = False
    p.xaxis.axis_label = "UMAP1"
    p.yaxis.axis_label = "UMAP2"

    # Create data source
    source = ColumnDataSource(umap_df)

    # Create scatter plot
    if color_mapper:
        if isinstance(color_mapper, LinearColorMapper):
            scatter = p.scatter(
                "UMAP1",
                "UMAP2",
                size=markersize,
                alpha=alpha,
                color={"field": colorby, "transform": color_mapper},
                source=source,
            )
            # Add colorbar for numeric coloring
            color_bar = ColorBar(color_mapper=color_mapper, width=8, location=(0, 0))
            p.add_layout(color_bar, "right")
        else:
            scatter = p.scatter(
                "UMAP1",
                "UMAP2",
                size=markersize,
                alpha=alpha,
                color=color_mapper,
                source=source,
                legend_field=colorby,
            )
    # If no color_by provided, use sample_color column from samples_df
    elif "sample_id" in umap_df.columns or "sample_name" in umap_df.columns:
        # Choose the identifier to map colors by
        id_col = "sample_id" if "sample_id" in umap_df.columns else "sample_name"

        # Get colors from samples_df based on the identifier
        if id_col == "sample_id":
            sample_colors = (
                self.samples_df.filter(
                    pl.col("sample_id").is_in(umap_df[id_col].unique()),
                )
                .select(["sample_id", "sample_color"])
                .to_dict(as_series=False)
            )
            color_map = dict(
                zip(
                    sample_colors["sample_id"],
                    sample_colors["sample_color"],
                    strict=False,
                ),
            )
        else:  # sample_name
            sample_colors = (
                self.samples_df.filter(
                    pl.col("sample_name").is_in(umap_df[id_col].unique()),
                )
                .select(["sample_name", "sample_color"])
                .to_dict(as_series=False)
            )
            color_map = dict(
                zip(
                    sample_colors["sample_name"],
                    sample_colors["sample_color"],
                    strict=False,
                ),
            )

        # Map colors into dataframe
        umap_df["color"] = [
            color_map.get(x, "#1f77b4") for x in umap_df[id_col]
        ]  # fallback to blue
        # Update the ColumnDataSource with new color column
        source = ColumnDataSource(umap_df)
        scatter = p.scatter(
            "UMAP1",
            "UMAP2",
            size=markersize,
            alpha=alpha,
            color="color",
            source=source,
        )
    else:
        scatter = p.scatter(
            "UMAP1",
            "UMAP2",
            size=markersize,
            alpha=alpha,
            color="blue",
            source=source,
        )

    # Create comprehensive hover tooltips with all sample information
    tooltip_list = []

    # Columns to exclude from tooltips (file paths and internal/plot fields)
    excluded_cols = {
        "file_source",
        "file_path",
        "sample_path",
        "sample_id",
        "UMAP1",
        "UMAP2",
        "ms1",
        "ms2",
        "size",
    }

    # Add all sample dataframe columns to tooltips, skipping excluded ones
    for col in samples_pd.columns:
        if col in excluded_cols:
            continue
        if col in umap_df.columns:
            if col == "sample_color":
                # Display sample_color as a colored swatch
                tooltip_list.append(("color", "$color[swatch]:sample_color"))
            elif umap_df[col].dtype in ["float64", "float32"]:
                tooltip_list.append((col, f"@{col}{{0.00}}"))
            else:
                tooltip_list.append((col, f"@{col}"))

    hover = HoverTool(
        tooltips=tooltip_list,
        renderers=[scatter],
    )
    p.add_tools(hover)

    # Add legend if using categorical coloring
    if color_mapper and not isinstance(color_mapper, LinearColorMapper) and colorby:
        # Only set legend properties if legends exist (avoid Bokeh warning when none created)
        if getattr(p, "legend", None) and len(p.legend) > 0:
            p.legend.location = "top_left"
            p.legend.click_policy = "hide"

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "UMAP Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)
    return p


def plot_tic(
    self,
    samples=100,
    title: str | None = None,
    filename: str | None = None,
    width: int = 1000,
    height: int = 300,
    original: bool = False,
):
    """
    Plot Total Ion Chromatograms (TIC) for selected samples overlaid using Bokeh.

    Parameters and behavior mirror `plot_bpc` but use per-sample TICs (get_tic).
    """
    # Local imports to avoid heavy top-level deps / circular imports
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.plotting import figure

    from masster.study.helpers import get_tic

    sample_ids = self._get_sample_ids(samples)
    if not sample_ids:
        self.logger.error("No valid sample_ids provided for TIC plotting.")
        return None

    # Get sample colors from samples_df
    sample_colors = (
        self.samples_df.filter(pl.col("sample_id").is_in(sample_ids))
        .select(["sample_id", "sample_color"])
        .to_dict(as_series=False)
    )
    color_map = dict(
        zip(sample_colors["sample_id"], sample_colors["sample_color"], strict=False),
    )

    plot_title = title or "Total Ion Chromatograms"

    # Get rt_unit from the first chromatogram, default to "s" if not available
    rt_unit = "s"
    for uid in sample_ids:
        try:
            first_chrom = get_tic(self, sample=uid, label=None)
            if hasattr(first_chrom, "rt_unit"):
                rt_unit = first_chrom.rt_unit
                break
        except Exception:
            continue

    p = figure(
        width=width,
        height=height,
        title=plot_title,
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    p.xaxis.axis_label = f"Retention Time ({rt_unit})"
    p.yaxis.axis_label = "Intensity"

    renderers = []

    # Build sample name mapping once
    samples_info = None
    if hasattr(self, "samples_df") and self.samples_df is not None:
        try:
            samples_info = self.samples_df.to_pandas()
        except Exception:
            samples_info = None

    for uid in sample_ids:
        try:
            chrom = get_tic(self, sample=uid, label=None)
        except Exception as e:
            self.logger.debug(f"Skipping sample {uid} for TIC: {e}")
            continue

        # extract arrays
        try:
            chrom_dict = (
                chrom.to_dict()
                if hasattr(chrom, "to_dict")
                else {"rt": chrom.rt, "inty": chrom.inty}
            )
            rt = chrom_dict.get("rt")
            inty = chrom_dict.get("inty")
        except Exception:
            try:
                rt = chrom.rt
                inty = chrom.inty
            except Exception as e:
                self.logger.debug(f"Invalid chromatogram for sample {uid}: {e}")
                continue

        if rt is None or inty is None:
            continue

        import numpy as _np

        rt = _np.asarray(rt)
        inty = _np.asarray(inty)
        if rt.size == 0 or inty.size == 0:
            continue

        # Sort by rt
        idx = _np.argsort(rt)
        rt = rt[idx]
        inty = inty[idx]

        sample_name = str(uid)
        if samples_info is not None:
            try:
                row = samples_info[samples_info["sample_id"] == uid]
                if not row.empty:
                    sample_name = row.iloc[0].get("sample_name", sample_name)
            except Exception:
                pass

        color = color_map.get(uid, "#000000")

        data = {
            "rt": rt,
            "inty": inty,
            "sample": [sample_name] * len(rt),
            "sample_color": [color] * len(rt),
        }
        src = ColumnDataSource(data)

        r_line = p.line(
            "rt",
            "inty",
            source=src,
            line_width=1,
            color=color,
            legend_label=str(sample_name),
        )
        p.scatter("rt", "inty", source=src, size=2, color=color, alpha=0.6)
        renderers.append(r_line)

    if not renderers:
        self.logger.warning("No TIC curves to plot for the selected samples.")
        return None

    hover = HoverTool(
        tooltips=[
            ("sample", "@sample"),
            ("sample_color", "$color[swatch]:sample_color"),
            ("rt", "@rt{0.00}"),
            ("inty", "@inty{0.00e0}"),
        ],
        renderers=renderers,
    )
    p.add_tools(hover)

    # Only set legend properties if a legend was actually created to avoid Bokeh warnings
    if getattr(p, "legend", None) and len(p.legend) > 0:
        p.legend.visible = False

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "TIC Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)

    return p


def plot_heatmap(
    self,
    filename=None,
    width=800,
    height=600,
    cmap="viridis",
    title="Consensus Matrix Heatmap",
    quant="chrom_area",
    samples=None,
):
    """
    Plot a heatmap of the consensus matrix data.

    Samples are ordered from left to right, features are ordered by m/z from top to bottom.
    Values are log10 transformed for better visualization.

    Parameters:
        filename (str, optional): Path to save the plot
        width (int): Plot width in pixels (default: 800)
        height (int): Plot height in pixels (default: 600)
        cmap (str): Colormap name (default: "viridis")
        title (str): Plot title (default: "Consensus Matrix Heatmap")
        quant (str): Quantification method column name (default: "chrom_area")
        samples: Sample identifier(s) to include. Can be:
                - None: include all samples (default)
                - int: single sample_id
                - str: single sample_name
                - list: multiple sample_ids or sample_names
    """
    from bokeh.models import BasicTicker, ColorBar, LinearColorMapper
    from bokeh.plotting import figure
    from bokeh.transform import transform
    import numpy as np
    import pandas as pd

    # Get consensus matrix
    matrix_df = self.get_consensus_matrix(quant=quant, samples=samples)

    if matrix_df is None or matrix_df.is_empty():
        self.logger.error("No consensus matrix available for heatmap.")
        return None

    # Get m/z values for each consensus_id to sort by
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.error("No consensus_df available for sorting features by m/z.")
        return None

    # Join with consensus_df to get m/z values
    matrix_with_mz = matrix_df.join(
        self.consensus_df.select(["consensus_id", "mz"]),
        on="consensus_id",
        how="left",
    )

    # Sort by m/z (ascending - lowest m/z at top)
    matrix_with_mz = matrix_with_mz.sort("mz")

    # Remove the m/z column after sorting
    matrix_sorted = matrix_with_mz.drop("mz")

    # Extract consensus_id and sample columns
    consensus_ids = matrix_sorted["consensus_id"].to_list()
    sample_cols = [col for col in matrix_sorted.columns if col != "consensus_id"]

    # Convert to pandas for easier heatmap processing
    matrix_pd = matrix_sorted.select(sample_cols).to_pandas()

    # Apply log10 transformation (add 1 to avoid log(0))
    matrix_log = np.log10(matrix_pd.values + 1)

    # Prepare data for Bokeh heatmap
    # Create a list of (sample, feature, value) tuples
    heatmap_data = []
    for i, feature_idx in enumerate(range(len(consensus_ids))):
        for j, sample in enumerate(sample_cols):
            value = matrix_log[feature_idx, j]
            heatmap_data.append(
                {
                    "sample": sample,
                    "feature": str(consensus_ids[feature_idx]),
                    "feature_idx": str(i),  # Use string index for y-axis position
                    "value": value,
                },
            )

    # Convert to DataFrame for Bokeh ColumnDataSource
    heatmap_df = pd.DataFrame(heatmap_data)

    from bokeh.models import ColumnDataSource

    source = ColumnDataSource(heatmap_df)

    # Handle colormap using cmap.Colormap
    try:
        # Get colormap palette using cmap
        if isinstance(cmap, str):
            colormap = Colormap(cmap)
            # Generate 256 colors and convert to hex
            import matplotlib.colors as mcolors

            colors = colormap(np.linspace(0, 1, 256))
            palette = [mcolors.rgb2hex(color) for color in colors]
        else:
            colormap = cmap
            # Try to use to_bokeh() method first
            try:
                palette = colormap.to_bokeh()
                # Ensure we got a color palette, not another mapper
                if not isinstance(palette, (list, tuple)):
                    # Fall back to generating colors manually
                    import matplotlib.colors as mcolors

                    colors = colormap(np.linspace(0, 1, 256))
                    palette = [mcolors.rgb2hex(color) for color in colors]
            except AttributeError:
                # Fall back to generating colors manually
                import matplotlib.colors as mcolors

                colors = colormap(np.linspace(0, 1, 256))
                palette = [mcolors.rgb2hex(color) for color in colors]
    except (AttributeError, ValueError, TypeError) as e:
        # Fallback to viridis if cmap interpretation fails
        self.logger.warning(
            f"Could not interpret colormap '{cmap}': {e}, falling back to viridis",
        )
        from bokeh.palettes import viridis

        palette = viridis(256)

    # Create color mapper
    color_mapper = LinearColorMapper(
        palette=palette,
        low=heatmap_df["value"].min(),
        high=heatmap_df["value"].max(),
    )

    # Create figure with categorical ranges for both axes
    p = figure(
        width=width,
        height=height,
        title=title,
        x_range=sample_cols,
        y_range=[str(i) for i in range(len(consensus_ids))],
        toolbar_location="above",
        tools="pan,wheel_zoom,box_zoom,reset,save,hover",
        tooltips=[
            ("Sample", "@sample"),
            ("Feature UID", "@feature"),
            ("log10(Value+1)", "@value{0.00}"),
        ],
    )

    # Draw rectangles for heatmap
    p.rect(
        x="sample",
        y="feature_idx",
        width=1,
        height=1,
        source=source,
        fill_color=transform("value", color_mapper),
        line_color=None,
    )

    # Add colorbar
    color_bar = ColorBar(
        color_mapper=color_mapper,
        width=8,
        location=(0, 0),
        title=f"log10({quant}+1)",
        ticker=BasicTicker(desired_num_ticks=8),
    )
    p.add_layout(color_bar, "right")

    # Style the plot
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.grid.grid_line_color = None
    p.xaxis.major_label_text_font_size = "0pt"  # Hide x-axis tick labels
    p.yaxis.major_label_text_font_size = "0pt"  # Hide y-axis tick labels
    p.yaxis.axis_label = "Features (sorted by m/z)"
    p.xaxis.axis_label = "Samples"

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "Heatmap Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)

    return p


def plot_ms2(
    self,
    features=None,
    width=800,
    height=150,
    normalize=False,
    logy=False,
    show_title=True,
):
    """
    Plot MS2 spectra for selected consensus features in a stacked form.

    Parameters:
        features: Feature selection using same format as consensus_select():
            - None: all consensus features with MS2 spectra
            - int: single consensus UID
            - list: list of consensus UIDs
            - tuple: range of consensus UIDs (min, max)
            - DataFrame: with consensus_id or consensus_id column
        width: Plot width in pixels (default: 800)
        height: Height per spectrum in pixels (default: 150)
        normalize: Normalize each spectrum to 100% (default: False)
        logy: Use log10 scale for y-axis (default: False)
        show_title: Show title with feature information (default: True)

    Returns:
        holoviews Layout object with stacked spectra
    """
    from bokeh.models import HoverTool
    import holoviews as hv
    import pandas as pd

    # Get consensus UIDs using the helper method
    consensus_ids = self._get_consensus_ids(features=features, verbose=False)

    if not consensus_ids:
        self.logger.warning("No consensus features selected.")
        return None

    # Filter consensus_df for selected UIDs with non-null ms2_specs
    if self.consensus_df is None:
        self.logger.warning("No consensus_df found.")
        return None

    feats = self.consensus_df.filter(
        pl.col("consensus_id").is_in(consensus_ids) & pl.col("ms2_specs").is_not_null(),
    )

    if feats.is_empty():
        self.logger.warning("No consensus features with MS2 spectra found.")
        return None

    self.logger.debug(
        f"Found {len(feats)} consensus features with MS2 spectra to plot.",
    )

    # Convert to list of dicts using Polars to preserve Spectrum objects
    feats_list = feats.to_dicts()
    self.logger.debug(f"Processing {len(feats_list)} consensus features...")

    plots = []
    for idx, row in enumerate(feats_list):
        consensus_id = row["consensus_id"]
        consensus_id = row.get("consensus_id", consensus_id)
        mz = row["mz"]
        rt = row["rt"]

        self.logger.debug(
            f"Processing consensus {idx + 1}/{len(feats_list)}: UID={consensus_id}, ID={consensus_id}",
        )

        # Get MS2 spectrum
        ms2_specs = row["ms2_specs"]
        if ms2_specs is None or (isinstance(ms2_specs, list) and len(ms2_specs) == 0):
            self.logger.warning(
                f"Consensus {consensus_id} has null or empty ms2_specs, skipping.",
            )
            continue

        # Use first spectrum if multiple are available
        spectrum = ms2_specs[0] if isinstance(ms2_specs, list) else ms2_specs

        # Get energy from spectrum
        energy = getattr(spectrum, "energy", "N/A")

        # Build title
        title = f"MS2 spectrum for m/z {mz:.4f}, rt {rt:.2f}, e {energy}, uid {consensus_id}"

        # Extract m/z and intensity
        if not (hasattr(spectrum, "mz") and hasattr(spectrum, "inty")):
            self.logger.warning(
                f"Consensus {consensus_id} spectrum missing mz or inty attributes, skipping.",
            )
            continue

        spec_mz = np.array(spectrum.mz)
        spec_inty = np.array(spectrum.inty)

        if len(spec_mz) == 0:
            self.logger.info(f"Consensus {consensus_id} has empty spectrum, skipping.")
            continue

        self.logger.debug(
            f"Consensus {consensus_id}: spectrum has {len(spec_mz)} peaks",
        )

        # Normalize if requested
        if normalize and spec_inty.max() > 0:
            spec_inty = (spec_inty / spec_inty.max()) * 100

        # Apply log10 if requested
        if logy:
            # Add small epsilon to avoid log(0)
            spec_inty = np.log10(spec_inty + 1)

        # Create DataFrame for proper hover tooltips
        spec_data = pd.DataFrame({"mz": spec_mz, "intensity": spec_inty})

        # Create stem plot
        plot_opts = {
            "width": width,
            "height": height,
            "color": "steelblue",
            "line_width": 2,
            "xlabel": "m/z",
            "ylabel": "Intensity (%)"
            if normalize
            else ("log10(Intensity)" if logy else "Intensity"),
            "title": title if show_title else "",
            "show_grid": True,
            "toolbar": "above",
            "default_tools": ["pan", "wheel_zoom", "box_zoom", "reset"],
        }

        # Only add ylim if normalizing
        if normalize:
            plot_opts["ylim"] = (0, 105)

        stems = hv.Spikes(spec_data, kdims=["mz"], vdims=["intensity"]).opts(
            **plot_opts,
        )

        # Add hover tool
        hover = HoverTool(
            tooltips=[("m/z", "@mz{0.0000}"), ("Intensity", "@intensity{0.0f}")],
        )
        stems = stems.opts(tools=[hover])

        self.logger.debug(f"Created plot for consensus {consensus_id}")
        plots.append(stems)

    if not plots:
        self.logger.warning("No spectra could be plotted.")
        return None

    self.logger.debug(f"Created {len(plots)} spectrum plots.")

    # Stack plots vertically
    if len(plots) == 1:
        return plots[0]
    layout = plots[0]
    for plot in plots[1:]:
        layout = layout + plot
    layout = layout.cols(1)
    # Unlink y-axis if not normalizing
    if not normalize:
        layout = layout.opts(shared_axes=False)
    return layout


def plot_volcano(
    self,
    samples1=None,
    samples2=None,
    diff_id=None,
    quant="chrom_area",
    test_type="welch",
    fdr_type="bh",
    yaxis="fdr",
    log2fc_min=None,
    pvalue_max=None,
    fdr_max=None,
    qvalue_max=None,
    colorby=None,
    cmap="viridis",
    alpha=0.7,
    markersize=8,
    sizeby=None,
    width=700,
    height=500,
    filename=None,
    legend="bottom_right",
    show_none=True,
    significance_line=0.05,
    fc_lines=1.0,
):
    """
    Create a volcano plot from differential analysis results.

    A volcano plot shows log2 fold-change on the x-axis and -log10(p-value/FDR/q-value)
    on the y-axis. Points above the significance threshold and beyond fold-change
    cutoffs are considered significant.

    Parameters:
        samples1: First group of samples (legacy mode). Can be:
                  - pl.DataFrame: from samples_select()
                  - list of sample_ids (int) or sample_names (str)
                  - int: N randomly selected samples
                  Not used if diff_id is specified.
        samples2: Second group of samples (legacy mode, same format as samples1)
                  Not used if diff_id is specified.
        diff_id (str, optional): Comparison label registered with diff_add(). If specified,
                                retrieves comparison from diff_df instead of using samples1/samples2.
        quant (str): Quantification column to use (default: "chrom_area")
        test_type (str): Statistical test to use (default: "welch")
                    - "welch": Welch's t-test (unequal variances assumed)
                    - "t": Student's t-test (equal variances assumed)
        fdr_type (str): FDR correction method (default: "bh")
                   - "bh": Benjamini-Hochberg (controls FDR)
                   - "by": Benjamini-Yekutieli (controls FDR under dependence)
        yaxis (str): Column to use for y-axis: "pvalue", "fdr", or "qvalue" (default: "fdr")
        log2fc_min (float, optional): Minimum absolute log2 fold-change to include
        pvalue_max (float, optional): Maximum p-value to include
        fdr_max (float, optional): Maximum FDR to include
        qvalue_max (float, optional): Maximum q-value to include
        colorby (str, optional): Column name to use for color mapping. If None, colors by significance.
        cmap (str): Color map name (default: "viridis")
        alpha (float): Transparency level (default: 0.7)
        markersize (int): Base marker size (default: 8)
        sizeby (str, optional): Column name to use for size mapping
        width (int): Plot width in pixels (default: 700)
        height (int): Plot height in pixels (default: 500)
        filename (str, optional): Path to save the plot
        legend (str, optional): Legend position for categorical data. Options: 'top_right', 'top_left',
                               'bottom_right', 'bottom_left', 'right', 'left', 'top', 'bottom'.
                               If None, legend is hidden. (default: "bottom_right")
        show_none (bool): Whether to display points with None values for colorby column (default: True)
        significance_line (float, optional): Y-axis threshold for significance line (default: 0.05)
        fc_lines (float, optional): Absolute log2 fold-change threshold for vertical lines (default: 1.0)

    Returns:
        Bokeh figure object

    Example:
        >>> # Using registered comparison (recommended)
        >>> study.diff_add([('treatment_vs_ctrl', treatment, control)])
        >>> study.plot_volcano(diff_id='treatment_vs_ctrl')
        >>>
        >>> # Legacy mode with direct sample groups
        >>> study.plot_volcano(
        ...     samples1=study.samples_select(sample_group=['control']),
        ...     samples2=study.samples_select(sample_group=['treatment'])
        ... )
        >>> # Colored by identification class
        >>> study.plot_volcano(
        ...     diff_id='treatment_vs_ctrl',
        ...     colorby='id_top_class',
        ...     significance_line=0.01
        ... )
    """
    from bokeh.models import (
        BasicTicker,
        ColumnDataSource,
        HoverTool,
        LinearColorMapper,
        Span,
    )
    from bokeh.palettes import Category20, viridis
    import bokeh.plotting as bp

    try:
        from bokeh.models import ColorBar
    except ImportError:
        from bokeh.models.annotations import ColorBar

    # Validate yaxis parameter
    if yaxis not in ["pvalue", "fdr", "qvalue"]:
        self.logger.warning(f"Unknown yaxis '{yaxis}', using 'fdr'")
        yaxis = "fdr"

    # Run differential analysis
    if diff_id is not None:
        # Use diff_df mode with registered comparison
        diff_df = self.get_diff(
            diff_ids=[diff_id],
            quant=quant,
            test_type=test_type,
            fdr_type=fdr_type,
            log2fc_min=log2fc_min,
            pvalue_max=pvalue_max,
            fdr_max=fdr_max,
            qvalue_max=qvalue_max,
        )
    elif samples1 is not None and samples2 is not None:
        # Legacy mode with direct sample groups
        diff_df = self.get_diff(
            samples1=samples1,
            samples2=samples2,
            quant=quant,
            test_type=test_type,
            fdr_type=fdr_type,
            log2fc_min=log2fc_min,
            pvalue_max=pvalue_max,
            fdr_max=fdr_max,
            qvalue_max=qvalue_max,
        )
    else:
        self.logger.error(
            "Either diff_id or both samples1 and samples2 must be provided",
        )
        return None

    if diff_df is None or diff_df.is_empty():
        self.logger.error("No data returned from differential analysis")
        return None

    # Calculate -log10(yaxis value) for plotting
    data = diff_df.with_columns([(-pl.col(yaxis).log(base=10)).alias("neg_log10_y")])

    # Handle infinite values (from log10(0))
    data = data.with_columns(
        [
            pl.when(pl.col("neg_log10_y").is_infinite())
            .then(pl.lit(None))
            .otherwise(pl.col("neg_log10_y"))
            .alias("neg_log10_y"),
        ],
    )

    # Default colorby: significance based on thresholds
    if colorby is None:
        # Create significance categories
        sig_threshold = significance_line if significance_line else 0.05
        fc_threshold = fc_lines if fc_lines else 1.0

        data = data.with_columns(
            [
                pl.when(
                    (pl.col(yaxis) <= sig_threshold)
                    & (pl.col("log2fc") >= fc_threshold),
                )
                .then(pl.lit("Up"))
                .when(
                    (pl.col(yaxis) <= sig_threshold)
                    & (pl.col("log2fc") <= -fc_threshold),
                )
                .then(pl.lit("Down"))
                .when(pl.col(yaxis) <= sig_threshold)
                .then(pl.lit("Significant"))
                .otherwise(pl.lit("Not significant"))
                .alias("_significance"),
            ],
        )
        colorby = "_significance"
        # Custom palette for significance categories
        sig_palette = {
            "Up": "#e74c3c",
            "Down": "#3498db",
            "Significant": "#9b59b6",
            "Not significant": "#95a5a6",
        }
    else:
        sig_palette = None

    # Handle sizeby
    if sizeby is not None and sizeby in data.columns:
        if sizeby in ["mean1", "mean2", "inty_mean"]:
            # Use log10 scaling for intensity-like values
            data = data.with_columns(
                [
                    pl.when(
                        (pl.col(sizeby).is_not_null())
                        & (pl.col(sizeby).is_finite())
                        & (pl.col(sizeby) > 0),
                    )
                    .then((pl.col(sizeby).log10() * markersize / 12).pow(1.5))
                    .otherwise(markersize)
                    .alias("markersize"),
                ],
            )
        else:
            max_size = data[sizeby].max()
            if max_size and max_size > 0:
                data = data.with_columns(
                    [
                        (
                            pl.col(sizeby) / max_size * markersize * 2 + markersize / 2
                        ).alias("markersize"),
                    ],
                )
            else:
                data = data.with_columns([pl.lit(markersize).alias("markersize")])
    else:
        data = data.with_columns([pl.lit(markersize).alias("markersize")])

    # Filter out None values for colorby column if show_none=False
    if not show_none and colorby in data.columns:
        data = data.filter(pl.col(colorby).is_not_null())

    # Filter out rows with NaN in critical columns for plotting
    data = data.filter(
        pl.col("log2fc").is_not_null()
        & pl.col("log2fc").is_finite()
        & pl.col("neg_log10_y").is_not_null(),
    )

    if data.is_empty():
        self.logger.error("No valid data points to plot after filtering")
        return None

    # Convert to pandas for Bokeh
    data_pd = data.to_pandas()
    source = ColumnDataSource(data_pd)

    # Handle colormap
    try:
        if isinstance(cmap, str):
            colormap = Colormap(cmap)
            import matplotlib.colors as mcolors

            colors = colormap(np.linspace(0, 1, 256))
            palette = [mcolors.rgb2hex(color) for color in colors]
        else:
            colormap = cmap
            try:
                palette = colormap.to_bokeh()
                if not isinstance(palette, (list, tuple)):
                    import matplotlib.colors as mcolors

                    colors = colormap(np.linspace(0, 1, 256))
                    palette = [mcolors.rgb2hex(color) for color in colors]
            except AttributeError:
                import matplotlib.colors as mcolors

                colors = colormap(np.linspace(0, 1, 256))
                palette = [mcolors.rgb2hex(color) for color in colors]
    except (AttributeError, ValueError, TypeError) as e:
        self.logger.warning(
            f"Could not interpret colormap '{cmap}': {e}, falling back to viridis",
        )
        palette = viridis(256)

    # Check if colorby column contains categorical data
    colorby_values = data[colorby].to_list()
    is_categorical = data_pd[colorby].dtype in ["object", "string", "category"] or (
        isinstance(colorby_values[0], str) if colorby_values else False
    )

    # Create figure
    yaxis_label = f"-log10({yaxis})"
    p = bp.figure(
        width=width,
        height=height,
        title=f"Volcano Plot (test={test_type}, {yaxis} correction={fdr_type})",
    )
    p.xaxis.axis_label = "log2 Fold Change"
    p.yaxis.axis_label = yaxis_label

    if is_categorical:
        # Categorical coloring
        unique_values = [v for v in data_pd[colorby].unique() if v is not None]

        # Use significance palette if available, otherwise use cmap
        if sig_palette:
            categorical_palette = [sig_palette.get(v, "#95a5a6") for v in unique_values]
        elif len(palette) >= len(unique_values):
            indices = np.linspace(0, len(palette) - 1, len(unique_values)).astype(int)
            categorical_palette = [palette[i] for i in indices]
        elif len(unique_values) <= 20:
            categorical_palette = Category20[min(20, max(3, len(unique_values)))]
        else:
            categorical_palette = viridis(min(256, len(unique_values)))

        # Handle None values with gray color first (background)
        all_unique_values = list(data_pd[colorby].unique())
        has_none_values = None in all_unique_values

        if has_none_values and show_none:
            none_data = data.filter(pl.col(colorby).is_null())
            none_data_pd = none_data.to_pandas()
            none_source = ColumnDataSource(none_data_pd)
            p.scatter(
                x="log2fc",
                y="neg_log10_y",
                size="markersize",
                fill_color="lightgray",
                line_color=None,
                alpha=alpha,
                source=none_source,
                legend_label="None",
                muted_alpha=0.0,
            )

        # Create separate renderer for each category
        for i, category in enumerate(unique_values):
            category_data = data.filter(pl.col(colorby) == category)
            category_data_pd = category_data.to_pandas()
            category_source = ColumnDataSource(category_data_pd)

            color = categorical_palette[i % len(categorical_palette)]

            p.scatter(
                x="log2fc",
                y="neg_log10_y",
                size="markersize",
                fill_color=color,
                line_color=None,
                alpha=alpha,
                source=category_source,
                legend_label=str(category),
                muted_alpha=0.0,
            )

        scatter_renderer = None
    else:
        # Numeric coloring
        color_mapper = LinearColorMapper(
            palette=palette,
            low=data[colorby].min(),
            high=data[colorby].max(),
        )
        scatter_renderer = p.scatter(
            x="log2fc",
            y="neg_log10_y",
            size="markersize",
            fill_color={"field": colorby, "transform": color_mapper},
            line_color=None,
            alpha=alpha,
            source=source,
        )

    # Add significance threshold line (horizontal)
    if significance_line is not None and significance_line > 0:
        sig_y = -np.log10(significance_line)
        hline = Span(
            location=sig_y,
            dimension="width",
            line_color="red",
            line_dash="dashed",
            line_width=1,
            line_alpha=0.6,
        )
        p.add_layout(hline)

    # Add fold-change threshold lines (vertical)
    if fc_lines is not None and fc_lines > 0:
        vline_pos = Span(
            location=fc_lines,
            dimension="height",
            line_color="gray",
            line_dash="dashed",
            line_width=1,
            line_alpha=0.6,
        )
        vline_neg = Span(
            location=-fc_lines,
            dimension="height",
            line_color="gray",
            line_dash="dashed",
            line_width=1,
            line_alpha=0.6,
        )
        p.add_layout(vline_pos)
        p.add_layout(vline_neg)

    # Add hover tool
    tooltips = [
        ("log2FC", "@log2fc{0.00}"),
        (yaxis, f"@{yaxis}{{0.0000}}"),
        ("mean1", "@mean1{0.0}"),
        ("mean2", "@mean2{0.0}"),
    ]

    # Add ID columns if present
    id_cols = ["id_top_name", "id_top_class", "id_top_adduct", "id_top_score"]
    for col in id_cols:
        if col in data.columns and data.filter(pl.col(col).is_not_null()).height > 0:
            if col == "id_top_score":
                tooltips.append((col, f"@{col}{{0.0}}"))
            else:
                tooltips.append((col, f"@{col}"))

    # Add consensus info if present
    if "consensus_id" in data.columns:
        tooltips.insert(0, ("consensus_id", "@consensus_id"))
    if "rt" in data.columns:
        tooltips.append(("rt", "@rt{0.0}"))
    if "mz" in data.columns:
        tooltips.append(("mz", "@mz{0.0000}"))

    hover = HoverTool(tooltips=tooltips)
    if not is_categorical and scatter_renderer:
        hover.renderers = [scatter_renderer]
    p.add_tools(hover)

    # Add colorbar for numeric data
    if not is_categorical:
        color_bar = ColorBar(
            color_mapper=color_mapper,
            label_standoff=12,
            location=(0, 0),
            title=colorby,
            ticker=BasicTicker(desired_num_ticks=8),
        )
        p.add_layout(color_bar, "right")
    # Configure legend for categorical data
    elif legend is not None:
        legend_position_map = {
            "top_right": "top_right",
            "top_left": "top_left",
            "bottom_right": "bottom_right",
            "bottom_left": "bottom_left",
            "right": "right",
            "left": "left",
            "top": "top",
            "bottom": "bottom",
        }
        bokeh_legend_pos = legend_position_map.get(legend, "bottom_right")
        p.legend.location = bokeh_legend_pos
        p.legend.click_policy = "hide"
    else:
        p.legend.visible = False

    # Save or show plot
    if filename is not None:
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)
        abs_filename = os.path.abspath(filename)
        _isolated_save_plot(p, filename, abs_filename, self.logger, "Volcano Plot")
    else:
        _isolated_show_notebook(p)

    return p


def plot_features_stats(
    self,
    filename=None,
):
    """
    Generates vertically stacked density plots for selected feature metrics.
    The distributions are created separately for features that have been mapped to a consensus feature
    (linked) and features that have not been mapped (orphan).
    Metrics include mz, rt, log10(inty), chrom_coherence, chrom_prominence, and chrom_prominence_scaled.
    The plots help to visualize the distribution differences between features that are linked to
    consensus features and those that are not.

    Parameters:
        filename (str, optional): The output filename. If the filename ends with ".html",
                                    the plot is saved as an interactive HTML file; otherwise,
                                    if provided, the plot is saved as a PNG image. If not provided,
                                    the interactive plot is displayed.

    Returns:
        None
    """
    import numpy as np

    # Check if we have the required data
    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found. Load features first.")
        return None

    if self.consensus_mapping_df is None or self.consensus_mapping_df.is_empty():
        self.logger.error(
            "No consensus_mapping_df found. Run merge() first to create consensus features.",
        )
        return None

    # Work on a copy of features_df
    feats = self.features_df.clone()
    # Convert to pandas for operations that require pandas functionality
    if hasattr(feats, "to_pandas"):
        feats = feats.to_pandas()

    # Get feature UIDs that are mapped to consensus features
    mapped_feature_ids = set(self.consensus_mapping_df["feature_id"].to_list())

    # Separate features based on whether they are mapped to consensus features
    feats["is_mapped"] = feats["feature_id"].isin(mapped_feature_ids)
    feats_mapped = feats[feats["is_mapped"]]
    feats_orphan = feats[~feats["is_mapped"]]

    self.logger.info(
        f"Found {len(feats_mapped)} features mapped to consensus, "
        f"{len(feats_orphan)} orphan features",
    )

    # Apply log10 transformation to intensity (handling non-positive values)
    feats["inty"] = np.where(feats["inty"] <= 0, np.nan, np.log10(feats["inty"]))

    # Apply log10 transformation to quality if present (handling non-positive values)
    if "quality" in feats.columns:
        feats["quality"] = np.where(
            feats["quality"] <= 0,
            np.nan,
            np.log10(feats["quality"]),
        )

    # Apply log10 transformation to chromatographic metrics if present
    if "chrom_prominence" in feats.columns:
        feats["chrom_prominence"] = np.where(
            feats["chrom_prominence"] <= 0,
            np.nan,
            np.log10(feats["chrom_prominence"]),
        )
    if "chrom_prominence_scaled" in feats.columns:
        feats["chrom_prominence_scaled"] = np.where(
            feats["chrom_prominence_scaled"] <= 0,
            np.nan,
            np.log10(feats["chrom_prominence_scaled"]),
        )
    if "chrom_height_scaled" in feats.columns:
        feats["chrom_height_scaled"] = np.where(
            feats["chrom_height_scaled"] <= 0,
            np.nan,
            np.log10(feats["chrom_height_scaled"]),
        )

    # Update the separated dataframes
    feats_mapped = feats[feats["is_mapped"]]
    feats_orphan = feats[~feats["is_mapped"]]

    # Define the specific metrics to plot
    cols_to_plot = [
        "mz",
        "rt",
        "inty",  # Already log10 transformed above
        "rt_delta",
    ]

    # Add optional columns if they exist
    optional_cols = [
        "quality",  # Already log10 transformed above
        "chrom_coherence",
        "chrom_prominence",  # Already log10 transformed above
        "chrom_prominence_scaled",  # Already log10 transformed above
        "chrom_height_scaled",  # Already log10 transformed above
    ]
    for col in optional_cols:
        if col in feats.columns:
            cols_to_plot.append(col)

    density_plots = []
    # Create overlaid distribution plots for each metric
    for col in cols_to_plot:
        # Extract non-null values from both groups
        data_mapped = feats_mapped[col].dropna().values
        data_orphan = feats_orphan[col].dropna().values

        # Create distribution elements - Green for MAPPED, Red for ORPHAN
        dist_mapped = hv.Distribution(data_mapped, label="Mapped to consensus").opts(
            fill_color="green",
            fill_alpha=0.1,
            line_color="green",
            line_width=3,
            line_alpha=1.0,
            muted_alpha=0.0,
        )
        dist_orphan = hv.Distribution(data_orphan, label="Orphan").opts(
            fill_color="red",
            fill_alpha=0.1,
            line_color="red",
            line_width=3,
            line_alpha=1.0,
            muted_alpha=0.0,
        )

        # Overlay the distributions with a legend and hover tool enabled
        title = col
        xlabel = col
        if col == "inty":
            title = "log10(inty)"
            xlabel = "log10(inty)"
        elif col == "quality":
            title = "log10(quality)"
            xlabel = "log10(quality)"
        elif col == "chrom_prominence":
            title = "log10(chrom_prominence)"
            xlabel = "log10(chrom_prominence)"
        elif col == "chrom_prominence_scaled":
            title = "log10(chrom_prominence_scaled)"
            xlabel = "log10(chrom_prominence_scaled)"
        elif col == "chrom_height_scaled":
            title = "log10(chrom_height_scaled)"
            xlabel = "log10(chrom_height_scaled)"

        overlay = (dist_mapped * dist_orphan).opts(
            title=title,
            xlabel=xlabel,
            show_legend=True,
            tools=["hover"],
            legend_position="right",
            legend_offset=(10, 0),
            width=800,
            height=250,
        )
        density_plots.append(overlay)

    # Arrange the plots in a vertical layout (1 column)
    layout = hv.Layout(density_plots).cols(1).opts(shared_axes=False)

    # Handle output
    if filename is not None:
        import os

        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)
        abs_filename = os.path.abspath(filename)

        # Save using Panel for HoloViews layouts
        _isolated_save_panel_plot(
            panel.Column(layout, align="start"),
            filename,
            abs_filename,
            self.logger,
            "Features Stats Plot",
        )
    else:
        # Return the layout directly for notebook display, wrapped in panel for alignment
        return panel.Column(layout, align="start")
