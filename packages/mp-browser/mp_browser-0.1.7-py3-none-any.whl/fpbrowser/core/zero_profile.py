"""Zero Profile management (base template for profiles)."""

import zipfile
from pathlib import Path
from typing import Optional
import requests


class ZeroProfileManager:
    """Manage Zero Profile (base template)."""
    
    ZERO_PROFILE_S3_KEY = "zero_profile.zip"
    
    def __init__(self, cache_dir: Path, s3_config: dict):
        """Initialize Zero Profile manager.
        
        Args:
            cache_dir: Cache directory path
            s3_config: S3 configuration
        """
        self.cache_dir = Path(cache_dir)
        self.s3_config = s3_config
        self.zero_profile_path = self.cache_dir / "zero_profile"
    
    def ensure_zero_profile(self) -> Path:
        """Ensure Zero Profile exists (download if needed).
        
        Returns:
            Zero Profile directory path
        """
        # Check if already exists
        if self._is_valid():
            return self.zero_profile_path
        
        # Download from S3
        print("📥 Zero Profile not found, downloading from cloud...")
        self.download_from_s3()
        
        if self._is_valid():
            print("✅ Zero Profile ready")
            return self.zero_profile_path
        else:
            raise RuntimeError("Failed to setup Zero Profile")
    
    def _is_valid(self) -> bool:
        """Check if Zero Profile is valid.
        
        Returns:
            True if valid
        """
        required_files = [
            self.zero_profile_path / "Default" / "Preferences",
        ]
        return all(f.exists() for f in required_files)
    
    def download_from_s3(self) -> None:
        """Download Zero Profile from S3."""
        if not self.s3_config.get("enabled"):
            raise RuntimeError("S3 is not enabled in config")
        
        # Build S3 URL
        url_base = self.s3_config.get("url_base", "")
        prefix = self.s3_config.get("prefix", "")
        url = f"{url_base}{prefix}{self.ZERO_PROFILE_S3_KEY}"
        
        # Download
        zip_path = self.cache_dir / "zero_profile.zip"
        try:
            print(f"  Downloading from: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            print(f"  Downloaded {len(response.content)} bytes")
            
            # Check zip file structure
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                print(f"  Zip contains {len(file_list)} files")
                
                # Check if zip has zero_profile/ prefix or starts with Default/
                has_zero_profile_prefix = any(f.startswith('zero_profile/') for f in file_list)
                has_default = any(f.startswith('Default/') or f == 'Default' for f in file_list)
                
                if has_zero_profile_prefix:
                    # Zip has zero_profile/ prefix, extract directly
                    print("  Extracting (has zero_profile/ prefix)...")
                    zip_ref.extractall(self.cache_dir)
                elif has_default:
                    # Zip starts with Default/, extract to zero_profile/
                    print("  Extracting (has Default/ prefix)...")
                    zip_ref.extractall(self.zero_profile_path)
                else:
                    # Unknown structure
                    print(f"  Warning: Unexpected zip structure. First files: {file_list[:5]}")
                    # Try extracting to zero_profile anyway
                    zip_ref.extractall(self.zero_profile_path)
            
            # Cleanup
            zip_path.unlink()
            print("  ✅ Extraction complete")
            
        except Exception as e:
            print(f"  ❌ Download/extract failed: {e}")
            raise RuntimeError(f"Failed to download Zero Profile: {e}")
    
    def update(self) -> None:
        """Update Zero Profile from S3 (force re-download)."""
        # Remove existing
        if self.zero_profile_path.exists():
            import shutil
            shutil.rmtree(self.zero_profile_path)
        
        # Re-download
        self.download_from_s3()
