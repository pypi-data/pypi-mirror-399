"""S3 指纹库操作模块"""

import json
import tempfile
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import boto3
from botocore.exceptions import ClientError


class S3ProfileLibrary:
    """S3 指纹库管理"""
    
    def __init__(self, bucket: str, prefix: str = "fingerprint-library"):
        """初始化
        
        Args:
            bucket: S3 bucket 名称
            prefix: S3 前缀（文件夹）
        """
        self.bucket = bucket
        self.prefix = prefix
        self.s3_client = boto3.client('s3')
        self._manifest_cache = None
    
    def get_manifest(self, force_refresh: bool = False) -> Dict[str, Any]:
        """获取 manifest
        
        Args:
            force_refresh: 强制刷新缓存
            
        Returns:
            Manifest 数据
        """
        if self._manifest_cache and not force_refresh:
            return self._manifest_cache
        
        manifest_key = f"{self.prefix}/manifest.json"
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket,
                Key=manifest_key
            )
            manifest = json.loads(response['Body'].read())
            self._manifest_cache = manifest
            return manifest
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return {'total': 0, 'profiles': {}}
            raise
    
    def list_profiles(
        self,
        os_filter: Optional[str] = None,
        lang_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """列出所有 profiles
        
        Args:
            os_filter: 过滤 OS（windows/mac/lin）
            lang_filter: 过滤语言（en-US, en-GB 等）
            
        Returns:
            Profile 列表
        """
        manifest = self.get_manifest()
        profiles = manifest.get('profiles', {})
        
        result = []
        for filename, metadata in profiles.items():
            # 过滤
            if os_filter and metadata.get('os') != os_filter:
                continue
            if lang_filter and metadata.get('language') != lang_filter:
                continue
            
            # 提取编号
            try:
                index = int(filename.replace('profile-', '').replace('.zip', ''))
            except:
                index = -1
            
            result.append({
                'index': index,
                'filename': filename,
                **metadata
            })
        
        # 按编号排序
        result.sort(key=lambda x: x['index'])
        return result
    
    def get_profile_metadata(self, index: int) -> Optional[Dict[str, Any]]:
        """获取指定 profile 的元数据
        
        Args:
            index: Profile 编号
            
        Returns:
            元数据或 None
        """
        filename = f"profile-{index:03d}.zip"
        manifest = self.get_manifest()
        return manifest.get('profiles', {}).get(filename)
    
    def download_profile(self, index: int, output_dir: Path) -> Optional[Path]:
        """下载 profile 到本地
        
        Args:
            index: Profile 编号
            output_dir: 输出目录
            
        Returns:
            下载的 ZIP 文件路径，失败返回 None
        """
        filename = f"profile-{index:03d}.zip"
        s3_key = f"{self.prefix}/{filename}"
        local_path = output_dir / filename
        
        try:
            self.s3_client.download_file(
                self.bucket,
                s3_key,
                str(local_path)
            )
            return local_path
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise
    
    def extract_and_rename(
        self,
        zip_path: Path,
        target_dir: Path,
        new_name: str
    ) -> None:
        """解压 profile 并重命名
        
        Args:
            zip_path: ZIP 文件路径
            target_dir: 目标目录（profiles 目录）
            new_name: 新名字（用户指定的 profile name）
        """
        profile_dir = target_dir / new_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        # 解压
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(profile_dir)
        
        # 读取并更新 profile.json 中的 name
        profile_json = profile_dir / 'profile.json'
        if profile_json.exists():
            with open(profile_json, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config['name'] = new_name
            # profile_id 保持官方的（UUID）
            
            with open(profile_json, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        else:
            # 如果没有 profile.json，创建一个基础的
            # 从 Preferences 中提取信息
            prefs_file = profile_dir / 'Default' / 'Preferences'
            if prefs_file.exists():
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                
                gologin = prefs.get('gologin', {})
                
                # 构建 profile.json
                config = {
                    'profile_id': gologin.get('profile_id', ''),
                    'name': new_name,
                    'navigator': {
                        'userAgent': gologin.get('userAgent', ''),
                        'platform': gologin.get('navigator', {}).get('platform', ''),
                        'language': gologin.get('langHeader', 'en-US'),
                        'hardwareConcurrency': gologin.get('hardwareConcurrency', 8),
                        'deviceMemory': gologin.get('deviceMemory', 8192) // 1024,  # MB -> GB
                    },
                    'webgl': {
                        'vendor': gologin.get('webGl', {}).get('vendor', ''),
                        'renderer': gologin.get('webGl', {}).get('renderer', ''),
                        'mode': 'noise',
                        'noise': gologin.get('webglNoiseValue', 10),
                    },
                    'canvas': {
                        'mode': gologin.get('canvasMode', 'off'),
                        'noise': gologin.get('canvasNoise', 0),
                    },
                    'audioContext': {
                        'mode': 'noise' if gologin.get('audioContext', {}).get('enable') else 'off',
                        'noise': gologin.get('audioContext', {}).get('noiseValue', 0),
                    },
                    'clientRects': {
                        'mode': 'noise',
                        'noise': gologin.get('getClientRectsNoice', 0),
                    },
                    'webRTC': gologin.get('webRTC', {}),
                    'timezone': gologin.get('timezone', {}),
                    'geolocation': gologin.get('geolocation', {}),
                    'mediaDevices': gologin.get('media_devices', {}),
                    'storage': gologin.get('storage', {}),
                    'plugins': gologin.get('plugins', {}),
                    'proxy': {'mode': 'none'},
                    'metadata': {
                        'imported_from': 's3_library',
                        'original_profile_id': gologin.get('profile_id', ''),
                    }
                }
                
                with open(profile_json, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
    
    def import_profile(
        self,
        index: int,
        profiles_dir: Path,
        new_name: str
    ) -> bool:
        """从 S3 导入 profile
        
        Args:
            index: Profile 编号
            profiles_dir: fpbrowser profiles 目录
            new_name: 新的 profile 名字
            
        Returns:
            是否成功
        """
        # 下载到临时目录
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # 下载
            zip_path = self.download_profile(index, tmpdir_path)
            if not zip_path:
                return False
            
            # 解压并重命名
            self.extract_and_rename(zip_path, profiles_dir, new_name)
        
        return True
    
    def get_random_index(
        self,
        os_filter: Optional[str] = None,
        lang_filter: Optional[str] = None
    ) -> Optional[int]:
        """随机选择一个 profile 编号
        
        Args:
            os_filter: 过滤 OS
            lang_filter: 过滤语言
            
        Returns:
            随机编号或 None
        """
        profiles = self.list_profiles(os_filter=os_filter, lang_filter=lang_filter)
        if not profiles:
            return None
        
        import random
        return random.choice(profiles)['index']
    
    def check_library_exists(self) -> bool:
        """检查指纹库是否存在
        
        Returns:
            是否存在
        """
        try:
            manifest = self.get_manifest()
            return manifest.get('total', 0) > 0
        except:
            return False
