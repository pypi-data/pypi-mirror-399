"""Export defaults for study-level operations."""

from dataclasses import dataclass


@dataclass
class export_mgf_defaults:
    """Default parameters for exporting study results."""

    filename: str = "consensus.mgf"
    selection: str = "best"  # "best" or "all"
    split_energy: bool = True
    merge: bool = False
    mz_start: float | None = None
    mz_end: float | None = None
    rt_start: float | None = None
    rt_end: float | None = None
    centroid: bool = True
    inty_min: float | None = None
    deisotope: bool = True
    verbose: bool = False
    precursor_trim: float = -10
    centroid_algo: str = "lmp"

    def get(self, key: str):
        """Get parameter value by key."""
        return getattr(self, key, None)

    def set(self, key: str, value, validate: bool = True) -> bool:
        """Set parameter value with optional validation."""
        if hasattr(self, key):
            setattr(self, key, value)
            return True
        return False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        from dataclasses import asdict

        return asdict(self)
