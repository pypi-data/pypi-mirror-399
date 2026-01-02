"""fpbrowser - Lightweight fingerprint browser SDK."""

__version__ = "0.1.0"

from .core import Browser, Profile, ProfileManager
from .utils import Config, get_config

__all__ = [
    "Browser",
    "Profile",
    "ProfileManager",
    "Config",
    "get_config",
    "__version__",
]
