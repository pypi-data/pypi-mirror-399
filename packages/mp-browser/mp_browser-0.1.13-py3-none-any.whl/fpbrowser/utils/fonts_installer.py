"""Fonts installer for Orbita browser (Linux only)."""

import os
import platform
import tarfile
import tempfile
from pathlib import Path
from urllib.request import urlretrieve

from .config import get_config


class FontsInstaller:
    """Install fonts for Orbita browser.
    
    字体用于防止字体指纹检测，主要用于 Linux Docker/Server 环境。
    Windows/macOS 系统字体丰富，通常不需要。
    """
    
    def __init__(self):
        self.config = get_config()
        self.fonts_url = self.config.config_data.get("browser", {}).get("orbita_urls", {}).get("fonts")
        # ~/.gologin/browser/fonts (官方路径)
        self.fonts_dir = Path.home() / ".gologin" / "browser" / "fonts"
    
    def install(self) -> bool:
        """Install fonts (Linux only).
        
        Returns:
            True if successful
        """
        system = platform.system()
        
        # 非 Linux 系统提示
        if system != "Linux":
            print(f"ℹ️  Fonts installation is for Linux Docker/Server environments.")
            print(f"   {system} has sufficient system fonts, skipping.")
            return True
        
        if not self.fonts_url:
            print("❌ Fonts URL not configured")
            return False
        
        # Check if already installed
        if self.fonts_dir.exists() and any(self.fonts_dir.iterdir()):
            print(f"✅ Fonts already installed at {self.fonts_dir}")
            return True
        
        print(f"📥 Downloading fonts for Linux...")
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
                tmp_path = tmp.name
            
            urlretrieve(self.fonts_url, tmp_path)
            
            self.fonts_dir.mkdir(parents=True, exist_ok=True)
            
            with tarfile.open(tmp_path, 'r:gz') as tar:
                tar.extractall(self.fonts_dir)
            
            print(f"✅ Fonts installed to {self.fonts_dir}")
            return True
        
        except Exception as e:
            print(f"❌ Failed to install fonts: {e}")
            return False
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
