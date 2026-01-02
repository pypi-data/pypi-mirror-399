"""Configuration management."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import shutil

from .helpers import detect_orbita_path, detect_os


class Config:
    """Configuration manager."""
    
    DEFAULT_CONFIG_DIR = Path.home() / ".fpbrowser"
    DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration.
        
        Args:
            config_path: Custom config file path, defaults to ~/.fpbrowser/config.json
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_FILE
        self.config_dir = self.config_path.parent
        self._data: Dict[str, Any] = {}
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create config
        if not self.config_path.exists():
            self._create_default_config()
        
        self._load()
    
    def _create_default_config(self) -> None:
        """Create default configuration file."""
        # Copy default config from package data
        default_config_path = Path(__file__).parent.parent / "data" / "default_config.json"
        
        if default_config_path.exists():
            shutil.copy2(default_config_path, self.config_path)
            print(f"✅ Created default config at {self.config_path}")
        else:
            # Fallback: create minimal config
            self._data = {
                "version": "0.1.0",
                "orbita_path": "auto",
                "browser": {
                    "version": "141",
                    "orbita_urls": {
                        "linux": "https://orbita-browser-linux.gologin.com/orbita-browser-latest.tar.gz",
                        "darwin": "https://orbita-browser-mac.gologin.com/orbita-browser-latest.tar.gz",
                        "darwin-arm": "https://orbita-browser-mac-arm.gologin.com/orbita-browser-latest.tar.gz",
                        "windows": "https://orbita-browser-win.gologin.com/orbita-browser-latest.zip"
                    },
                    "chromium_url": "https://storage.googleapis.com/chromium-browser-snapshots",
                    "chromium_revision": "1509326"
                },
                "s3": {"enabled": False},
                "defaults": {
                    "os": "auto",
                    "language": "en-US",
                    "timezone": "auto",
                    "headless": False
                },
                "cleanup": {"temp_profile_days": 7}
            }
            self._save()
            print(f"⚠️  Created minimal config at {self.config_path}")
    
    def _load(self) -> None:
        """Load configuration from file."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._data = json.load(f)
    
    def _save(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., "s3.bucket")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        # Handle "auto" values
        if value == "auto":
            if key == "orbita_path":
                return detect_orbita_path()
            elif key == "defaults.os":
                return detect_os()
            elif key == "defaults.timezone":
                # TODO: detect timezone based on language
                return "America/New_York"
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        data = self._data
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        # Set value
        data[keys[-1]] = value
        self._save()
    
    def reset(self) -> None:
        """Reset configuration to default."""
        self.config_path.unlink(missing_ok=True)
        self._create_default_config()
        self._load()
    
    @property
    def profiles_dir(self) -> Path:
        """Get profiles directory."""
        path = self.config_dir / "profiles"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def zero_profile_dir(self) -> Path:
        """Get zero profile directory."""
        path = self.config_dir / "zero_profile"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def logs_dir(self) -> Path:
        """Get logs directory."""
        path = self.config_dir / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def s3_config(self) -> Dict[str, Any]:
        """Get S3 configuration."""
        return self.get("s3", {})
    
    @property
    def s3_enabled(self) -> bool:
        """Check if S3 is enabled."""
        return self.get("s3.enabled", False)
    
    @property
    def orbita_path(self) -> Optional[str]:
        """Get Orbita browser path."""
        path = self.get("orbita_path")
        if not path:
            raise RuntimeError(
                "Orbita browser not found. Please set orbita_path in config:\n"
                "  fpbrowser config set orbita_path /path/to/orbita"
            )
        return path
    
    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return self._data.copy()


# Global config instance
_config: Optional[Config] = None


def get_config(config_path: Optional[Path] = None) -> Config:
    """Get global configuration instance.
    
    Args:
        config_path: Custom config file path
        
    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
