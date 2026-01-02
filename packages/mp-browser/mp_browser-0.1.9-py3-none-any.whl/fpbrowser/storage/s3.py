import json
from pathlib import Path
from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError
from .local import LocalStorage
class S3Storage:
    def __init__(self, s3_config: Dict[str, Any]):
        self.config = s3_config
        self.client = boto3.client(
            's3',
            endpoint_url=s3_config.get("endpoint"),
            aws_access_key_id=s3_config.get("access_key"),
            aws_secret_access_key=s3_config.get("secret_key"),
        )
        self.bucket = s3_config.get("bucket")
        self.prefix = s3_config.get("prefix", "").strip("/")
    def _get_key(self, path: str) -> str:
        if self.prefix:
            return f"{self.prefix}/{path}"
        return path
    def upload_profile(
        self,
        profile_name: str,
        profile_dir: Path,
        include_session: bool = False
    ) -> None:
        config_file = profile_dir / "profile.json"
        if config_file.exists():
            key = self._get_key(f"profiles/{profile_name}/profile.json")
            self.client.upload_file(
                str(config_file),
                self.bucket,
                key
            )
        if include_session:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                tmp_path = Path(tmp.name)
            try:
                LocalStorage.pack_session_data(profile_dir, tmp_path)
                key = self._get_key(f"profiles/{profile_name}/session.zip")
                self.client.upload_file(
                    str(tmp_path),
                    self.bucket,
                    key
                )
            finally:
                tmp_path.unlink(missing_ok=True)
    def download_profile(
        self,
        profile_name: str,
        profile_dir: Path,
        include_session: bool = False
    ) -> None:
        profile_dir.mkdir(parents=True, exist_ok=True)
        config_file = profile_dir / "profile.json"
        key = self._get_key(f"profiles/{profile_name}/profile.json")
        try:
            self.client.download_file(
                self.bucket,
                key,
                str(config_file)
            )
        except ClientError as e:
            raise ValueError(f"Profile '{profile_name}' not found in cloud") from e
        if include_session:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                tmp_path = Path(tmp.name)
            try:
                key = self._get_key(f"profiles/{profile_name}/session.zip")
                self.client.download_file(
                    self.bucket,
                    key,
                    str(tmp_path)
                )
                LocalStorage.unpack_session_data(tmp_path, profile_dir)
            except ClientError:
                print("  ⚠️  No session data found in cloud")
            finally:
                tmp_path.unlink(missing_ok=True)
    def list_profiles(self) -> List[Dict[str, Any]]:
        prefix = self._get_key("profiles/")
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                Delimiter='/'
            )
            profiles = []
            for common_prefix in response.get('CommonPrefixes', []):
                profile_prefix = common_prefix['Prefix']
                profile_name = profile_prefix.rstrip('/').split('/')[-1]
                profiles.append({
                    "name": profile_name,
                    "path": profile_prefix
                })
            return profiles
        except ClientError as e:
            print(f"❌ Failed to list profiles: {e}")
            return []