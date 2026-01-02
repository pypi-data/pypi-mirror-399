import json
import os
import subprocess
import time
import signal
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import shutil
from ..utils import Config, get_config, get_random_port
from .profile import Profile, ProfileManager
from .zero_profile import ZeroProfileManager
class Browser:
    def __init__(
        self,
        profile_name: str,
        profile_dir: Path,
        orbita_path: str,
        port: int,
        process: subprocess.Popen,
        config: Config
    ):
        self.profile_name = profile_name
        self.profile_dir = profile_dir
        self.orbita_path = orbita_path
        self.port = port
        self.process = process
        self.config = config
    @property
    def debugger_url(self) -> str:
        return f"ws://127.0.0.1:{self.port}"
    @property
    def is_running(self) -> bool:
        return self.process.poll() is None
    def stop(self) -> None:
        if self.is_running:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            print(f"✅ Browser stopped (profile: {self.profile_name})")
    def wait(self) -> None:
        self.process.wait()
    @staticmethod
    def start(
        profile: Optional[str] = None,
        mode: str = "temp",
        auto_download: bool = False,
        auto_create: bool = False,
        os: Optional[str] = None,
        language: Optional[str] = None,
        timezone: Optional[str] = None,
        proxy: Optional[Union[str, Dict]] = None,
        use_proxy: Optional[Union[bool, str]] = None,
        browser_path: Optional[str] = None,
        headless: bool = False,
        extensions: Optional[List[str]] = None,
        args: Optional[List[str]] = None,
        port: Optional[int] = None,
        user_data_dir: Optional[str] = None,
        **kwargs
    ) -> "Browser":
        config = get_config()
        manager = ProfileManager(config)
        if not profile or mode == "temp":
            profile_obj = manager.create_temp()
            profile_obj.save(config.profiles_dir)
            profile_name = profile_obj.name
        else:
            profile_name = profile
            profile_obj = manager.get(profile_name)
            if not profile_obj and auto_download:
                print(f"📥 Profile '{profile_name}' not found locally, downloading from cloud...")
                try:
                    manager.download(profile_name, include_session=True, force=False)
                    profile_obj = manager.get(profile_name)
                except Exception as e:
                    print(f"⚠️  Failed to download: {e}")
            if not profile_obj and auto_create:
                print(f"🔨 Creating new profile '{profile_name}'...")
                profile_obj = Profile.create(
                    name=profile_name,
                    os=os,
                    language=language,
                    timezone=timezone,
                    proxy=_parse_proxy(proxy) if proxy else None,
                    **kwargs
                )
                profile_obj.save(config.profiles_dir)
            if not profile_obj:
                raise ValueError(f"Profile '{profile_name}' not found. Use --init to create.")
        profile_dir = config.profiles_dir / profile_name
        profile_dir.mkdir(parents=True, exist_ok=True)
        profile_json_file = profile_dir / "profile.json"
        with open(profile_json_file, 'w', encoding='utf-8') as f:
            json.dump(profile_obj.config, f, indent=2)
        if browser_path:
            if browser_path.lower() == 'chromium':
                executable_path = _get_chromium_path(config.orbita_path)
                if not executable_path:
                    raise ValueError(
                        "Chromium not found. Install with:\n"
                        "  fpbrowser install --chromium"
                    )
            else:
                executable_path = browser_path
                if not Path(executable_path).exists():
                    raise ValueError(f"Browser not found: {executable_path}")
            print(f"🌐 Using Chromium mode (no fingerprint injection)")
        else:
            zero_profile_manager = ZeroProfileManager(
                config.zero_profile_dir.parent,
                config.s3_config
            )
            zero_profile_path = zero_profile_manager.ensure_zero_profile()
            _prepare_profile(profile_dir, zero_profile_path, profile_obj.config)
            executable_path = config.orbita_path
            _switch_preferences(profile_dir, use_chromium=False)
        if browser_path:
            _switch_preferences(profile_dir, use_chromium=True)
        if not port:
            port = get_random_port()
        runtime_proxy = None
        if use_proxy is True:
            runtime_proxy = profile_obj.config.get("proxy")
        elif use_proxy and isinstance(use_proxy, str):
            runtime_proxy = _parse_proxy(use_proxy)
        launch_args = _build_launch_args(
            profile_dir=user_data_dir or profile_dir,
            profile_name=profile_name,
            port=port,
            proxy=runtime_proxy,
            headless=headless,
            extensions=extensions,
            extra_args=args
        )
        process = subprocess.Popen(
            [executable_path] + launch_args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        max_attempts = 10
        for i in range(max_attempts):
            time.sleep(0.5)
            if process.poll() is not None:
                raise RuntimeError(f"Browser process exited with code {process.returncode}")
            try:
                import requests
                response = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=1)
                if response.status_code == 200:
                    break
            except:
                pass
        else:
            if process.poll() is not None:
                raise RuntimeError("Browser failed to start")
        print(f"✅ Browser started (profile: {profile_name}, port: {port})")
        return Browser(
            profile_name=profile_name,
            profile_dir=profile_dir,
            orbita_path=executable_path,
            port=port,
            process=process,
            config=config
        )
    @staticmethod
    def list_running() -> List[Dict[str, Any]]:
        return []
    @staticmethod
    def stop_all() -> None:
        pass
def _get_chromium_path(orbita_path: str) -> Optional[str]:
    import platform
    system = platform.system()
    if system == "Darwin":
        playwright_cache = Path.home() / "Library" / "Caches" / "ms-playwright"
    elif system == "Linux":
        playwright_cache = Path.home() / ".cache" / "ms-playwright"
    elif system == "Windows":
        playwright_cache = Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright"
    else:
        playwright_cache = None
    if playwright_cache and playwright_cache.exists():
        chromium_dirs = sorted(
            [d for d in playwright_cache.glob("chromium-*") if d.is_dir()],
            key=lambda d: int(d.name.split('-')[1]) if '-' in d.name and d.name.split('-')[1].isdigit() else 0,
            reverse=True
        )
        for chromium_dir in chromium_dirs:
            if system == "Darwin":
                exe = chromium_dir / "chrome-mac" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
            elif system == "Linux":
                exe = chromium_dir / "chrome-linux" / "chrome"
            elif system == "Windows":
                exe = chromium_dir / "chrome-win" / "chrome.exe"
            else:
                continue
            if exe.exists():
                return str(exe)
    if system == "Darwin":
        our_install = Path.home() / "orbita-browser" / "chrome"
    elif system == "Linux":
        our_install = Path.home() / "orbita-browser" / "chrome"
    elif system == "Windows":
        our_install = Path.home() / "orbita-browser" / "chrome.exe"
    else:
        our_install = None
    if our_install and our_install.exists():
        return str(our_install)
    return None
def _parse_proxy(proxy: Union[str, Dict]) -> Dict[str, Any]:
    if isinstance(proxy, dict):
        return proxy
    if "://" in proxy:
        mode, rest = proxy.split("://", 1)
        if ":" in rest:
            host, port_str = rest.rsplit(":", 1)
            return {
                "mode": mode,
                "host": host,
                "port": int(port_str),
                "username": "",
                "password": ""
            }
    return {"mode": "none"}
def _prepare_profile(
    profile_dir: Path,
    zero_profile_path: Path,
    profile_config: Dict[str, Any]
) -> None:
    default_dir = profile_dir / "Default"
    default_dir.mkdir(parents=True, exist_ok=True)
    zero_default = zero_profile_path / "Default"
    if zero_default.exists():
        print(f"   Copying files from zero profile...")
        for item in zero_default.iterdir():
            dest = default_dir / item.name
            if item.is_file():
                if not dest.exists():
                    shutil.copy2(item, dest)
                    print(f"   Copied {item.name} from zero profile")
            elif item.is_dir() and item.name == "Network":
                if not dest.exists():
                    shutil.copytree(item, dest)
                    print(f"   Copied Network directory from zero profile")
    preferences_file = default_dir / "Preferences"
    if preferences_file.exists():
        with open(preferences_file, 'r', encoding='utf-8') as f:
            preferences = json.load(f)
        print(f"   Loaded Preferences from zero profile")
    else:
        preferences = _generate_preferences_base(profile_config)
        print(f"   Generated new Preferences")
    _update_preferences_fingerprint(preferences, profile_config)
    with open(preferences_file, 'w', encoding='utf-8') as f:
        json.dump(preferences, f, indent=2)
    lang = profile_config.get("navigator", {}).get("language", "en-US")
    lang_list = [l.strip() for l in lang.split(',')]
    orbita_config = {
        "intl": {
            "accept_languages": lang,
            "selected_languages": lang,
            "app_locale": lang_list[0] if lang_list else "en-US",
            "forced_languages": [lang_list[0]] if lang_list else ["en-US"]
        }
    }
    orbita_config_file = profile_dir / "orbita.config"
    with open(orbita_config_file, 'w', encoding='utf-8') as f:
        json.dump(orbita_config, f, indent="\t")
    print(f"   Generated orbita.config")
    print(f"✅ Profile prepared at {profile_dir}")
def _generate_preferences_base(profile_config: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "profile": {
            "name": profile_config.get("name", "Person 1"),
            "exit_type": "Normal",
            "exited_cleanly": True
        },
        "browser": {
            "check_default_browser": False,
            "show_home_button": True
        },
        "download": {
            "prompt_for_download": False
        },
        "safebrowsing": {
            "enabled": False
        },
        "extensions": {
            "settings": {}
        }
    }
def _update_preferences_fingerprint(preferences: Dict[str, Any], profile_config: Dict[str, Any]) -> None:
    gologin_config = _convert_to_gologin_format(profile_config)
    preferences["gologin"] = gologin_config
    lang_header = profile_config.get("navigator", {}).get("language", "en-US")
    if "intl" not in preferences:
        preferences["intl"] = {}
    preferences["intl"]["selected_languages"] = lang_header
    if "profile" not in preferences:
        preferences["profile"] = {}
    preferences["profile"]["name"] = profile_config.get("name", "Person 1")
    print(f"   Updated gologin fingerprint config")
def _switch_preferences(profile_dir: Path, use_chromium: bool = False) -> None:
    pref_file = profile_dir / "Default" / "Preferences"
    pref_orbita = profile_dir / "Default" / "Preferences.orbita"
    pref_chromium = profile_dir / "Default" / "Preferences.chromium"
    if not pref_file.exists():
        return
    try:
        with open(pref_file, 'r', encoding='utf-8') as f:
            prefs = json.load(f)
    except Exception as e:
        print(f"⚠️  Failed to read Preferences: {e}")
        return
    has_gologin = 'gologin' in prefs
    if use_chromium:
        if has_gologin:
            print("   Switching to Chromium mode (removing gologin field)...")
            with open(pref_orbita, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2)
            if pref_chromium.exists():
                with open(pref_chromium, 'r', encoding='utf-8') as f:
                    prefs_chromium = json.load(f)
                with open(pref_file, 'w', encoding='utf-8') as f:
                    json.dump(prefs_chromium, f, indent=2)
                print("   Restored Chromium Preferences")
            else:
                del prefs['gologin']
                with open(pref_file, 'w', encoding='utf-8') as f:
                    json.dump(prefs, f, indent=2)
                with open(pref_chromium, 'w', encoding='utf-8') as f:
                    json.dump(prefs, f, indent=2)
                print("   Created Chromium Preferences (removed gologin)")
    else:
        if not has_gologin:
            print("   Switching to Orbita mode (restoring gologin field)...")
            with open(pref_chromium, 'w', encoding='utf-8') as f:
                json.dump(prefs, f, indent=2)
            if pref_orbita.exists():
                with open(pref_orbita, 'r', encoding='utf-8') as f:
                    prefs_orbita = json.load(f)
                with open(pref_file, 'w', encoding='utf-8') as f:
                    json.dump(prefs_orbita, f, indent=2)
                print("   Restored Orbita Preferences")
            else:
                print("   ⚠️  No Orbita backup found, gologin field will be regenerated")
def _convert_to_gologin_format(profile_config: Dict[str, Any]) -> Dict[str, Any]:
    import random
    resolution = profile_config.get("navigator", {}).get("resolution", "1920x1080")
    screen_width = int(resolution.split('x')[0])
    screen_height = int(resolution.split('x')[1])
    lang_header = profile_config.get("navigator", {}).get("language", "en-US")
    splitted_langs = lang_header.split(',')[0] if lang_header else "en-US"
    webgl_cfg = profile_config.get("webgl", {})
    canvas_cfg = profile_config.get("canvas", {})
    audio_cfg = profile_config.get("audioContext", {})
    client_rects_cfg = profile_config.get("clientRects", {})
    webgl_noise = float(webgl_cfg.get("noise", random.uniform(10.0, 50.0)))
    canvas_noise = float(canvas_cfg.get("noise", random.uniform(0.1, 0.9)))
    audio_noise = float(audio_cfg.get("noise", random.uniform(1e-9, 1e-7)))
    client_rects_noise = float(client_rects_cfg.get("noise", random.uniform(5.0, 15.0)))
    gologin = {
        "profile_id": profile_config["profile_id"],
        "name": profile_config.get("name", "Person 1"),
        "is_m1": profile_config.get("os") == "mac" and "M" in profile_config.get("osSpec", ""),
        "navigator": {
            "platform": profile_config.get("navigator", {}).get("platform", "Win32"),
            "max_touch_points": profile_config.get("navigator", {}).get("maxTouchPoints", 0),
        },
        "userAgent": profile_config.get("navigator", {}).get("userAgent", ""),
        "screenWidth": screen_width,
        "screenHeight": screen_height,
        "languages": splitted_langs,
        "langHeader": lang_header,
        "hardwareConcurrency": profile_config.get("navigator", {}).get("hardwareConcurrency", 8),
        "deviceMemory": profile_config.get("navigator", {}).get("deviceMemory", 8) * 1024,
        "doNotTrack": profile_config.get("navigator", {}).get("doNotTrack", False),
        "webGl": {
            "vendor": webgl_cfg.get("vendor", "Google Inc. (Intel)"),
            "renderer": webgl_cfg.get("renderer", "ANGLE (Intel, Intel(R) UHD Graphics 630, OpenGL 4.1)"),
            "mode": webgl_cfg.get("mode", "off") == "mask",
        },
        "webGL": {
            "mode": webgl_cfg.get("mode", "off"),
            "noise": webgl_noise,
            "getClientRectsNoise": client_rects_noise,
        },
        "webgl": {
            "metadata": {
                "vendor": webgl_cfg.get("vendor", "Google Inc. (Intel)"),
                "renderer": webgl_cfg.get("renderer", "ANGLE (Intel, Intel(R) UHD Graphics 630, OpenGL 4.1)"),
                "mode": webgl_cfg.get("mode", "off") == "mask",
            }
        },
        "webglParams": profile_config.get("webglParams", {}),
        "webGpu": profile_config.get("webGpu", {}),
        "webgl_noise_enable": webgl_cfg.get("mode") == "noise",
        "webgl_noice_enable": webgl_cfg.get("mode") == "noise",
        "webglNoiceEnable": webgl_cfg.get("mode") == "noise",
        "webgl_noise_value": webgl_noise,
        "webglNoiseValue": webgl_noise,
        "canvas": {
            "mode": canvas_cfg.get("mode", "off"),
        },
        "canvasMode": canvas_cfg.get("mode", "off"),
        "canvasNoise": canvas_noise,
        "audioContext": {
            "enable": audio_cfg.get("mode", "off") != "off",
            "noiseValue": audio_noise,
        },
        "client_rects_noise_enable": client_rects_cfg.get("mode") == "noise",
        "getClientRectsNoice": client_rects_noise,
        "timezone": {
            "id": profile_config.get("timezone", {}).get("id", "America/New_York")
        },
        "geolocation": {
            "mode": profile_config.get("geolocation", {}).get("mode", "prompt"),
            "latitude": float(profile_config.get("geolocation", {}).get("latitude", 0)),
            "longitude": float(profile_config.get("geolocation", {}).get("longitude", 0)),
            "accuracy": float(profile_config.get("geolocation", {}).get("accuracy", 10)),
        },
        "webRTC": profile_config.get("webRTC", {}),
        "media_devices": {
            "enable": True,
            "videoInputs": 1,
            "audioInputs": 1,
            "audioOutputs": 1,
            "uid": "",
        },
        "plugins": {
            "all_enable": True,
            "flash_enable": True,
        },
        "storage": {
            "enable": True,
        },
        "mobile": {
            "enable": profile_config.get("os") == "android",
            "width": screen_width,
            "height": screen_height,
            "device_scale_factor": profile_config.get("devicePixelRatio", 1),
        },
        "proxy": {
            "mode": "fixed_servers",
            "username": "",
            "password": "",
            "server": "",
            "schema": "http",
        },
        "dns": profile_config.get("dns", ""),
        "startupUrl": "",
        "startup_urls": [],
    }
    return gologin
def _build_launch_args(
    profile_dir: Path,
    profile_name: str,
    port: int,
    proxy: Optional[Dict],
    headless: bool,
    extensions: Optional[List[str]],
    extra_args: Optional[List[str]]
) -> List[str]:
    profile_json = profile_dir / "profile.json"
    resolution = "1920x1080"
    if profile_json.exists():
        try:
            with open(profile_json, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
                resolution = profile_data.get("navigator", {}).get("resolution", "1920x1080")
        except:
            pass
    screen_width, screen_height = map(int, resolution.split('x'))
    args = [
        f"--remote-debugging-port={port}",
        "--password-store=basic",
        f"--gologin-profile={profile_name}",
        "--lang=en-US",
        "--webrtc-ip-handling-policy=default_public_interface_only",
        "--disable-features=PrintCompositorLPAC",
        f"--window-size={screen_width},{screen_height}",
        f"--user-data-dir={profile_dir}",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ]
    if headless:
        args.append("--headless=new")
        args.append("--disable-gpu")
    if proxy and proxy.get("mode") != "none":
        mode = proxy.get("mode")
        host = proxy.get("host")
        port_num = proxy.get("port")
        username = proxy.get("username", "")
        password = proxy.get("password", "")
        if mode and host and port_num:
            if username and password:
                proxy_url = f"{mode}://{username}:{password}@{host}:{port_num}"
            else:
                proxy_url = f"{mode}://{host}:{port_num}"
            args.append(f"--proxy-server={proxy_url}")
            args.append(f'--host-resolver-rules=MAP * 0.0.0.0 , EXCLUDE {host}')
    if extensions:
        ext_paths = ",".join(str(Path(e).absolute()) for e in extensions)
        args.append(f"--load-extension={ext_paths}")
    if extra_args:
        args.extend(extra_args)
    return args