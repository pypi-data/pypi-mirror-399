"""Helper functions."""

import platform
import socket
import random
from pathlib import Path
from typing import Optional


def detect_os() -> str:
    """Detect current operating system.
    
    Returns:
        "windows" | "macos" | "linux"
    """
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system in ["linux", "windows"]:
        return system
    else:
        return "linux"  # fallback


def detect_orbita_path() -> Optional[str]:
    """Auto-detect Orbita browser path.
    
    Returns:
        Path to Orbita executable or None if not found
    """
    system = platform.system().lower()
    
    # macOS
    if system == "darwin":
        paths = [
            "/Applications/Orbita-Browser.app/Contents/MacOS/Orbita",
            "/Applications/Orbita.app/Contents/MacOS/Orbita",
        ]
        for path in paths:
            if Path(path).exists():
                return path
    
    # Linux
    elif system == "linux":
        paths = [
            "/home/runner/orbita-browser/chrome",
            "/home/runner/orbita-browser/orbita",
            "/opt/orbita-browser/chrome",
            "/opt/orbita-browser/orbita",
            Path.home() / "orbita-browser" / "chrome",
            Path.home() / "orbita-browser" / "orbita",
        ]
        for path in paths:
            path_obj = Path(path) if isinstance(path, str) else path
            if path_obj.exists():
                return str(path_obj)
    
    # Windows
    elif system == "windows":
        paths = [
            Path.home() / "orbita-browser" / "chrome.exe",  # User home directory
            r"C:\Program Files\Orbita-Browser\Orbita.exe",
            r"C:\Program Files (x86)\Orbita-Browser\Orbita.exe",
            Path.home() / "AppData" / "Local" / "Orbita-Browser" / "Orbita.exe",
        ]
        for path in paths:
            path_obj = Path(path) if isinstance(path, str) else path
            if path_obj.exists():
                return str(path_obj)
    
    return None


def is_port_available(port: int) -> bool:
    """Check if a port is available.
    
    Args:
        port: Port number
        
    Returns:
        True if available, False otherwise
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(('127.0.0.1', port))
        return result != 0  # 0 means port is in use
    finally:
        sock.close()


def get_random_port(min_port: int = 10000, max_port: int = 35000) -> int:
    """Get a random available port.
    
    Args:
        min_port: Minimum port number
        max_port: Maximum port number
        
    Returns:
        Available port number
    """
    max_attempts = 100
    for _ in range(max_attempts):
        port = random.randint(min_port, max_port)
        if is_port_available(port):
            return port
    
    raise RuntimeError(f"Could not find available port after {max_attempts} attempts")


def detect_orbita_version(orbita_path: Optional[str] = None) -> str:
    """Detect Orbita browser version.
    
    Args:
        orbita_path: Path to Orbita executable (None = auto-detect)
        
    Returns:
        Chrome version string (e.g., "118.0.0.0")
    """
    import subprocess
    import re
    
    if not orbita_path:
        orbita_path = detect_orbita_path()
    
    if not orbita_path or not Path(orbita_path).exists():
        # Fallback to default version
        return "118.0.0.0"
    
    try:
        # Try to get version from --version flag
        result = subprocess.run(
            [orbita_path, '--version'],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        # Parse version from output
        # Example: "Chromium 118.0.5993.117" or "Chrome/118.0.0.0"
        match = re.search(r'(\d+\.\d+\.\d+\.\d+)', result.stdout + result.stderr)
        if match:
            return match.group(1)
        
        # Try reading from binary (Linux/macOS)
        if platform.system() != "Windows":
            result = subprocess.run(
                ['strings', orbita_path],
                capture_output=True,
                text=True,
                timeout=3
            )
            # Look for Chrome version pattern
            for line in result.stdout.split('\n'):
                if 'Chrome/' in line:
                    match = re.search(r'Chrome/(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        return match.group(1)
    
    except Exception as e:
        pass
    
    # Fallback to default version
    return "118.0.0.0"
