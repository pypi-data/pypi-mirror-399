"""Orbita browser installer."""

import os
import platform
import tarfile
import zipfile
import shutil
from pathlib import Path
from typing import Optional
import urllib.request


class OrbitaInstaller:
    """Install Orbita browser from GoLogin (v141)."""
    
    def __init__(self):
        """Initialize installer."""
        self.system = platform.system()
        self.machine = platform.machine().lower()
        
        # Load config
        from .config import get_config
        self.config = get_config()
        
        # Get download URLs from config
        self.version = self.config.get("browser.version", "141")
        self.urls = self.config.get("browser.orbita_urls", {})
    
    def install(self) -> bool:
        """Install Orbita browser (v141 fixed).
        
        Returns:
            True if successful
        """
        install_dir = self._get_install_dir()
        
        # Check if already installed
        executable = self._get_executable_path(install_dir)
        if executable and Path(executable).exists():
            print(f"✅ Orbita already installed at: {install_dir}")
            return True
        
        print(f"📥 Downloading Orbita browser (v{self.version})...")
        
        # Determine platform
        platform_key = self._get_platform_key()
        if not platform_key:
            print(f"❌ Unsupported platform: {self.system} {self.machine}")
            return False
        
        # Download
        try:
            archive_path = self._download_orbita(platform_key, install_dir.parent)
        except Exception as e:
            print(f"❌ Download failed: {e}")
            print(f"\n💡 Manual installation:")
            print(f"   1. Download Orbita from: https://gologin.com/download")
            print(f"   2. Extract to: {install_dir}")
            return False
        
        # Extract
        print(f"📦 Extracting...")
        try:
            self._extract(archive_path, install_dir)
        except Exception as e:
            print(f"❌ Extract failed: {e}")
            return False
        finally:
            # Clean up
            if archive_path and archive_path.exists():
                archive_path.unlink()
        
        # Set permissions
        if self.system in ["Darwin", "Linux"]:
            self._set_permissions(install_dir)
        
        print(f"✅ Orbita installed to: {install_dir}")
        return True
    
    def _get_platform_key(self) -> Optional[str]:
        """Get platform key for downloads."""
        if self.system == "Linux":
            return "linux"
        elif self.system == "Darwin":
            if self.machine in ["arm64", "aarch64"]:
                return "darwin-arm"
            return "darwin"
        elif self.system == "Windows":
            return "windows"
        return None
    
    def _get_install_dir(self) -> Path:
        """Get installation directory."""
        if self.system == "Darwin":
            # macOS: ~/orbita-browser/
            return Path.home() / "orbita-browser"
        elif self.system == "Linux":
            # Linux: ~/orbita-browser/
            return Path.home() / "orbita-browser"
        elif self.system == "Windows":
            # Windows: ~/orbita-browser/
            return Path.home() / "orbita-browser"
        return Path.home() / "orbita-browser"
    
    def _get_executable_path(self, install_dir: Path) -> Optional[str]:
        """Get executable path within install directory."""
        if self.system == "Darwin":
            candidates = [
                install_dir / "Orbita.app" / "Contents" / "MacOS" / "Orbita",
                install_dir / "chrome",
            ]
        elif self.system == "Linux":
            candidates = [
                install_dir / "chrome",
                install_dir / "orbita",
            ]
        elif self.system == "Windows":
            candidates = [
                install_dir / "chrome.exe",
                install_dir / "orbita.exe",
            ]
        else:
            return None
        
        for path in candidates:
            if path.exists():
                return str(path)
        return None
    
    def _download_orbita(self, platform_key: str, dest_dir: Path) -> Path:
        """Download Orbita from GoLogin official source.
        
        Args:
            platform_key: Platform identifier
            dest_dir: Destination directory
            
        Returns:
            Path to downloaded archive
        """
        url = self.urls.get(platform_key)
        if not url:
            raise ValueError(f"No URL for platform: {platform_key}")
        
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Archive name
        if self.system == "Windows":
            archive_name = "orbita.zip"
        else:
            archive_name = "orbita.tar.gz"
        
        archive_path = dest_dir / archive_name
        
        print(f"   URL: {url}")
        
        def reporthook(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                percent = min(100, downloaded * 100 / total_size)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="")
        
        urllib.request.urlretrieve(url, archive_path, reporthook)
        print()  # Newline
        return archive_path
    
    def _extract(self, archive_path: Path, dest_dir: Path):
        """Extract Orbita archive.
        
        Args:
            archive_path: Archive file
            dest_dir: Destination directory
        """
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract to temporary directory first
        temp_extract = dest_dir.parent / f"{dest_dir.name}_temp"
        temp_extract.mkdir(parents=True, exist_ok=True)
        
        try:
            if archive_path.suffix == ".zip":
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_extract)
            elif ".tar" in archive_path.name:
                with tarfile.open(archive_path, 'r:*') as tar:
                    tar.extractall(temp_extract)
            
            # Check if archive created a nested directory with same name
            extracted_items = list(temp_extract.iterdir())
            if len(extracted_items) == 1 and extracted_items[0].is_dir():
                nested_dir = extracted_items[0]
                # If nested dir has same name as dest_dir, move its contents up
                if nested_dir.name == dest_dir.name or nested_dir.name in ["orbita-browser", "Orbita-browser"]:
                    # Move contents from nested dir to dest_dir
                    for item in nested_dir.iterdir():
                        shutil.move(str(item), str(dest_dir))
                    shutil.rmtree(temp_extract)
                else:
                    # Move the single directory to dest_dir
                    shutil.move(str(nested_dir), str(dest_dir))
                    shutil.rmtree(temp_extract)
            else:
                # Multiple items or single file - move all to dest_dir
                for item in extracted_items:
                    shutil.move(str(item), str(dest_dir))
                shutil.rmtree(temp_extract)
        except Exception as e:
            # Cleanup temp directory on error
            if temp_extract.exists():
                shutil.rmtree(temp_extract)
            raise e
    
    def _set_permissions(self, install_dir: Path):
        """Set executable permissions."""
        executable = self._get_executable_path(install_dir)
        if executable:
            os.chmod(executable, 0o755)
