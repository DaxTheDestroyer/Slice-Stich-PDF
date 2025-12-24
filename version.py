"""
Application version configuration.
This is the single source of truth for version information.
"""

__version__ = "4.0.0"
__app_name__ = "Slice & Stich PDF"
__author__ = "Dax Sapien"

def get_version_tuple():
    """Returns version as tuple of integers (major, minor, patch)"""
    parts = __version__.split('.')
    return tuple(int(p) for p in parts[:3])

def get_version_string():
    """Returns formatted version string for display"""
    return f"v{__version__}"
