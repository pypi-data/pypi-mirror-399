"""Chromium installer (Playwright-compatible paths)."""

import os
import platform
import zipfile
import tarfile
from pathlib import Path
from typing import Optional
import urllib.request
import shutil


class ChromiumInstaller:
    """Install Chromium browser (v141)."""
    
    def __init__(self):
        """Initialize installer."""
        self.system = platform.system()
        self.machine = platform.machine().lower()
        
        # Load config
        from .config import get_config
        self.config = get_config()
        
        # Get download info from config
        self.version = self.config.get("browser.version", "141")
        self.base_url = self.config.get("browser.chromium_url", "https://storage.googleapis.com/chromium-browser-snapshots")
        self.revision = self.config.get("browser.chromium_revision", "1509326")
    
    def install(self) -> bool:
        """Install Chromium browser (v141).
        
        Returns:
            True if successful
        """
        # Determine platform
        platform_name = self._get_platform_name()
        if not platform_name:
            print(f"❌ Unsupported platform: {self.system} {self.machine}")
            return False
        
        # Build download URL
        archive_name = self._get_archive_name()
        download_url = f"{self.base_url}/{platform_name}/{self.revision}/{archive_name}"
        
        # Determine install path
        install_dir = self._get_install_dir(self.revision)
        if install_dir.exists():
            print(f"✅ Chromium {self.version} (r{self.revision}) already installed")
            return True
        
        print(f"📥 Downloading Chromium {self.version} (r{self.revision})...")
        print(f"   URL: {download_url}")
        
        # Download
        try:
            archive_path = self._download(download_url, install_dir.parent)
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
        
        # Extract
        print(f"📦 Extracting...")
        try:
            self._extract(archive_path, install_dir)
        except Exception as e:
            print(f"❌ Extract failed: {e}")
            return False
        finally:
            # Clean up archive
            if archive_path.exists():
                archive_path.unlink()
        
        # Set permissions (Unix)
        if self.system in ["Darwin", "Linux"]:
            self._set_permissions(install_dir)
        
        print(f"✅ Installed to: {install_dir}")
        return True
    
    def _get_platform_name(self) -> Optional[str]:
        """Get Chromium platform name.
        
        Returns:
            Platform name for CDN or None
        """
        if self.system == "Linux":
            return "Linux_x64"
        elif self.system == "Darwin":
            # Check ARM (M1/M2) or Intel
            if self.machine in ["arm64", "aarch64"]:
                return "Mac_Arm"
            else:
                return "Mac"
        elif self.system == "Windows":
            return "Win_x64"
        return None
    
    def _get_archive_name(self) -> str:
        """Get archive filename."""
        if self.system == "Linux":
            return "chrome-linux.zip"
        elif self.system == "Darwin":
            return "chrome-mac.zip"
        elif self.system == "Windows":
            return "chrome-win.zip"
        return "chrome.zip"
    
    def _get_install_dir(self, revision: str) -> Path:
        """Get installation directory (Playwright standard)."""
        if self.system == "Darwin":
            base = Path.home() / "Library" / "Caches" / "ms-playwright"
        elif self.system == "Linux":
            base = Path.home() / ".cache" / "ms-playwright"
        elif self.system == "Windows":
            base = Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"
        else:
            base = Path.home() / ".cache" / "ms-playwright"
        
        return base / f"chromium-{revision}"
    
    def _download(self, url: str, dest_dir: Path) -> Path:
        """Download file with progress.
        
        Args:
            url: Download URL
            dest_dir: Destination directory
            
        Returns:
            Path to downloaded file
        """
        dest_dir.mkdir(parents=True, exist_ok=True)
        archive_path = dest_dir / "chromium.zip"
        
        def reporthook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, downloaded * 100 / total_size)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="")
        
        urllib.request.urlretrieve(url, archive_path, reporthook)
        print()  # Newline after progress
        
        return archive_path
    
    def _extract(self, archive_path: Path, dest_dir: Path):
        """Extract archive.
        
        Args:
            archive_path: Archive file path
            dest_dir: Destination directory
        """
        dest_dir.parent.mkdir(parents=True, exist_ok=True)
        
        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(dest_dir.parent)
        elif archive_path.suffix in [".tar", ".gz", ".bz2"]:
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(dest_dir.parent)
        
        # Chromium extracts to chrome-linux, chrome-mac, etc.
        # Rename to chromium-{revision}
        if self.system == "Linux":
            extracted = dest_dir.parent / "chrome-linux"
        elif self.system == "Darwin":
            extracted = dest_dir.parent / "chrome-mac"
        elif self.system == "Windows":
            extracted = dest_dir.parent / "chrome-win"
        else:
            return
        
        if extracted.exists() and not dest_dir.exists():
            extracted.rename(dest_dir)
    
    def _set_permissions(self, install_dir: Path):
        """Set executable permissions (Unix).
        
        Args:
            install_dir: Installation directory
        """
        if self.system == "Darwin":
            executable = install_dir / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
        elif self.system == "Linux":
            executable = install_dir / "chrome"
        else:
            return
        
        if executable.exists():
            os.chmod(executable, 0o755)
