from __future__ import annotations

__version__ = "0.8.18"


def get_version() -> str:
    """Get the current version of masster.

    Returns:
        str: The version string
    """
    return __version__


def main() -> None:
    """Print the current version."""
    print(f"Current version: {__version__}")


if __name__ == "__main__":
    main()
