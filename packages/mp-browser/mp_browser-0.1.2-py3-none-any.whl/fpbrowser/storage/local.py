"""Local storage for session data."""

import zipfile
import shutil
import tempfile
from pathlib import Path
from typing import Optional


class LocalStorage:
    """Local session data storage (pack/unpack)."""
    
    @staticmethod
    def pack_session_data(profile_dir: Path, output_path: Path) -> bool:
        """Pack session data to ZIP.
        
        Includes: Cookies, Login Data, Session/Local Storage
        Based on original session_data_sync.py
        
        Args:
            profile_dir: Profile directory
            output_path: Output ZIP path
            
        Returns:
            True if successful
        """
        default_dir = profile_dir / "Default"
        if not default_dir.exists():
            return False
        
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Cookies
                _add_file_to_zip(zipf, default_dir / "Cookies", "Cookies")
                _add_file_to_zip(zipf, default_dir / "Cookies-journal", "Cookies-journal")
                
                # Login Data (important for Google sessions)
                _add_file_to_zip(zipf, default_dir / "Login Data", "Login Data")
                _add_file_to_zip(zipf, default_dir / "Login Data For Account", "Login Data For Account")
                _add_file_to_zip(zipf, default_dir / "Login Data-journal", "Login Data-journal")
                _add_file_to_zip(zipf, default_dir / "Login Data For Account-journal", "Login Data For Account-journal")
                
                # Storage
                _add_dir_to_zip(zipf, default_dir / "Session Storage", "Session Storage")
                _add_dir_to_zip(zipf, default_dir / "Local Storage", "Local Storage")
            
            return True
        
        except Exception as e:
            print(f"❌ Failed to pack session data: {e}")
            return False
    
    @staticmethod
    def unpack_session_data(zip_path: Path, profile_dir: Path) -> bool:
        """Unpack session data from ZIP.
        
        Args:
            zip_path: ZIP file path
            profile_dir: Profile directory
            
        Returns:
            True if successful
        """
        default_dir = profile_dir / "Default"
        default_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Remove existing files to avoid conflicts
            files_to_remove = [
                "Cookies", "Cookies-journal",
                "Login Data", "Login Data For Account",
                "Login Data-journal", "Login Data For Account-journal",
            ]
            for filename in files_to_remove:
                file_path = default_dir / filename
                if file_path.exists():
                    try:
                        file_path.unlink()
                    except:
                        # Try rename if unlink fails
                        file_path.rename(file_path.with_suffix('.bak'))
            
            # Extract
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(default_dir)
            
            return True
        
        except Exception as e:
            print(f"❌ Failed to unpack session data: {e}")
            return False


def _add_file_to_zip(zipf: zipfile.ZipFile, file_path: Path, arcname: str) -> None:
    """Add file to ZIP (with SQLite lock handling).
    
    Args:
        zipf: ZipFile object
        file_path: File to add
        arcname: Archive name
    """
    if not file_path.exists():
        return
    
    try:
        # Try to copy to temp first (avoid SQLite lock)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            shutil.copy2(file_path, tmp_path)
            zipf.write(tmp_path, arcname)
            tmp_path.unlink()
        except:
            # Fallback: direct write
            try:
                zipf.write(file_path, arcname)
            except Exception as e:
                print(f"  ⚠️  Failed to add {arcname}: {e}")
    
    except Exception as e:
        print(f"  ⚠️  Failed to process {arcname}: {e}")


def _add_dir_to_zip(zipf: zipfile.ZipFile, dir_path: Path, arcname: str) -> None:
    """Add directory to ZIP.
    
    Args:
        zipf: ZipFile object
        dir_path: Directory to add
        arcname: Archive name
    """
    if not dir_path.exists():
        return
    
    for item in dir_path.rglob('*'):
        if item.is_file():
            relative_path = item.relative_to(dir_path.parent)
            zipf.write(item, relative_path)
