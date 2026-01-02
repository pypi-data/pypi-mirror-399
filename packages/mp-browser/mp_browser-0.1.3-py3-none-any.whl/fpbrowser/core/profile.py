import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from ..utils import Config, get_config, detect_os
from .fingerprint import FingerprintGenerator
from .zero_profile import ZeroProfileManager
class Profile:
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
    @staticmethod
    def create(
        name: str,
        os: Optional[str] = None,
        language: Optional[str] = None,
        timezone: Optional[str] = None,
        proxy: Optional[Dict[str, Any]] = None,
        fingerprint: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "Profile":
        if not os:
            os = detect_os()
        if not language:
            language = "en-US"
        if fingerprint:
            fingerprint_config = fingerprint
        else:
            fingerprint_config = FingerprintGenerator.generate(
                os=os,
                language=language,
                timezone=timezone,
                **kwargs
            )
        config = {
            "profile_id": str(uuid.uuid4()),
            "name": name,
            "fingerprint": fingerprint_config,
            "navigator": fingerprint_config["navigator"],
            "webgl": fingerprint_config["webgl"],
            "canvas": fingerprint_config["canvas"],
            "clientRects": fingerprint_config["clientRects"],
            "audioContext": fingerprint_config["audioContext"],
            "webRTC": fingerprint_config["webRTC"],
            "timezone": fingerprint_config["timezone"],
            "geolocation": fingerprint_config["geolocation"],
            "mediaDevices": fingerprint_config["mediaDevices"],
            "storage": fingerprint_config["storage"],
            "plugins": fingerprint_config["plugins"],
            "proxy": proxy or {"mode": "none"},
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
        }
        return Profile(name, config)
    def save(self, profiles_dir: Path) -> None:
        profile_dir = profiles_dir / self.name
        profile_dir.mkdir(parents=True, exist_ok=True)
        config_file = profile_dir / "profile.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    def to_dict(self) -> Dict[str, Any]:
        return self.config.copy()
    @staticmethod
    def from_dict(name: str, data: Dict[str, Any]) -> "Profile":
        return Profile(name, data)
    @staticmethod
    def load(name: str, profiles_dir: Path) -> Optional["Profile"]:
        config_file = profiles_dir / name / "profile.json"
        if not config_file.exists():
            return None
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if "profile_id" not in config:
            config["profile_id"] = str(uuid.uuid4())
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        return Profile(name, config)
class ProfileManager:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or get_config()
        self.profiles_dir = self.config.profiles_dir
        self.zero_profile_manager = ZeroProfileManager(
            self.config.zero_profile_dir.parent,
            self.config.s3_config
        )
    def list(self, include_temp: bool = False) -> List[Profile]:
        profiles = []
        if not self.profiles_dir.exists():
            return profiles
        for profile_dir in self.profiles_dir.iterdir():
            if not profile_dir.is_dir():
                continue
            if not include_temp and profile_dir.name.startswith("temp-"):
                continue
            profile = Profile.load(profile_dir.name, self.profiles_dir)
            if profile:
                profiles.append(profile)
        return profiles
    def get(self, name: str) -> Optional[Profile]:
        return Profile.load(name, self.profiles_dir)
    def exists(self, name: str) -> bool:
        return (self.profiles_dir / name / "profile.json").exists()
    def delete(self, name: str) -> None:
        profile_dir = self.profiles_dir / name
        if profile_dir.exists():
            import shutil
            shutil.rmtree(profile_dir)
    def create_temp(self) -> Profile:
        temp_name = f"temp-{uuid.uuid4().hex[:8]}"
        return Profile.create(name=temp_name)
    def upload(
        self,
        name: str,
        include_session: bool = True,
        force: bool = False
    ) -> None:
        from ..storage.s3 import S3Storage
        if not self.config.s3_enabled:
            raise RuntimeError("S3 is not enabled")
        profile = self.get(name)
        if not profile:
            raise ValueError(f"Profile '{name}' not found")
        storage = S3Storage(self.config.s3_config)
        profile_dir = self.profiles_dir / name
        storage.upload_profile(name, profile_dir, include_session)
        print(f"✅ Uploaded profile '{name}' to cloud")
    def download(
        self,
        name: str,
        include_session: bool = True,
        force: bool = False
    ) -> None:
        from ..storage.s3 import S3Storage
        if not self.config.s3_enabled:
            raise RuntimeError("S3 is not enabled")
        if self.exists(name) and not force:
            raise ValueError(f"Profile '{name}' already exists locally. Use force=True to overwrite.")
        storage = S3Storage(self.config.s3_config)
        profile_dir = self.profiles_dir / name
        profile_dir.mkdir(parents=True, exist_ok=True)
        storage.download_profile(name, profile_dir, include_session)
        print(f"✅ Downloaded profile '{name}' from cloud")
    def list_remote(self) -> List[Dict[str, Any]]:
        from ..storage.s3 import S3Storage
        if not self.config.s3_enabled:
            raise RuntimeError("S3 is not enabled")
        storage = S3Storage(self.config.s3_config)
        return storage.list_profiles()
    def export(self, name: str, output_path: str) -> None:
        profile = self.get(name)
        if not profile:
            raise ValueError(f"Profile '{name}' not found")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(profile.to_dict(), f, indent=2)
        print(f"✅ Exported profile '{name}' to {output_path}")
    def import_from(self, input_path: str, name: Optional[str] = None) -> None:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        profile_name = name or data.get("name", "imported-profile")
        profile = Profile.from_dict(profile_name, data)
        profile.save(self.profiles_dir)
        print(f"✅ Imported profile '{profile_name}'")
    def cleanup_temp(self, older_than_days: int = 7) -> int:
        count = 0
        cutoff_time = datetime.utcnow().timestamp() - (older_than_days * 86400)
        for profile_dir in self.profiles_dir.iterdir():
            if not profile_dir.is_dir():
                continue
            if not profile_dir.name.startswith("temp-"):
                continue
            mtime = profile_dir.stat().st_mtime
            if mtime < cutoff_time:
                import shutil
                shutil.rmtree(profile_dir)
                count += 1
                print(f"  Deleted {profile_dir.name}")
        return count