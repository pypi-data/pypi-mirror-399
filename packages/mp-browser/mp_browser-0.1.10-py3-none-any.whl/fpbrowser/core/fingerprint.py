import random
import re
from typing import Dict, Any, Optional
class FingerprintGenerator:
    UA_TEMPLATES = {
        "windows": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
        ],
        "macos_intel": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
        ],
        "macos_arm": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
        ],
        "linux": [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36",
        ],
    }
    WEBGL_VENDORS = {
        "windows": [
            {"vendor": "Google Inc. (Intel)", "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)", "type": "intel"},
            {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0)", "type": "nvidia"},
            {"vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD, AMD Radeon RX 580 Series Direct3D11 vs_5_0 ps_5_0)", "type": "amd"},
        ],
        "macos_intel": [
            {"vendor": "Intel Inc.", "renderer": "Intel(R) Iris(TM) Plus Graphics 655", "type": "intel"},
            {"vendor": "Intel Inc.", "renderer": "Intel(R) UHD Graphics 630", "type": "intel"},
        ],
        "macos_arm": [
            {"vendor": "Apple Inc.", "renderer": "Apple M1", "type": "apple"},
            {"vendor": "Apple Inc.", "renderer": "Apple M2", "type": "apple"},
        ],
        "linux": [
            {"vendor": "Intel Open Source Technology Center", "renderer": "Mesa DRI Intel(R) UHD Graphics 630 (CFL GT2)", "type": "intel"},
            {"vendor": "X.Org", "renderer": "AMD Radeon RX 580 Series (POLARIS10, DRM 3.42.0, 5.15.0-56-generic, LLVM 12.0.0)", "type": "amd"},
        ],
    }
    @classmethod
    def generate(
        cls,
        os: str,
        language: str = "en-US",
        timezone: Optional[str] = None,
        orbita_version: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        if not orbita_version:
            from ..utils.helpers import detect_orbita_version
            orbita_version = detect_orbita_version()
        os_variant = os
        if os == "macos":
            os_variant = random.choice(["macos_intel", "macos_arm"])
        ua_template = random.choice(cls.UA_TEMPLATES.get(os_variant, cls.UA_TEMPLATES["windows"]))
        user_agent = ua_template.format(version=orbita_version)
        platform_map = {
            "windows": "Win32",
            "macos_intel": "MacIntel",
            "macos_arm": "MacIntel",
            "linux": "Linux x86_64"
        }
        platform = platform_map.get(os_variant, "Win32")
        resolutions = ["1920x1080", "1366x768", "1536x864", "1440x900", "2560x1440"]
        resolution = random.choice(resolutions)
        screen_width, screen_height = map(int, resolution.split('x'))
        if os_variant == "macos_arm":
            hardware_concurrency = random.choice([8, 10])
            device_memory = random.choice([8, 16])
        elif os_variant == "macos_intel":
            hardware_concurrency = random.choice([4, 8])
            device_memory = random.choice([8, 16])
        else:
            hardware_concurrency = random.choice([4, 8, 12, 16])
            device_memory = random.choice([4, 8, 16])
        webgl = random.choice(cls.WEBGL_VENDORS.get(os_variant, cls.WEBGL_VENDORS["windows"]))
        if not timezone:
            timezone = cls._infer_timezone(language)
        canvas_noise = random.randint(5, 15)
        webgl_noise = random.randint(5, 15)
        return {
            "navigator": {
                "userAgent": user_agent,
                "platform": platform,
                "language": language,
                "hardwareConcurrency": hardware_concurrency,
                "deviceMemory": device_memory,
                "maxTouchPoints": 0 if os != "windows" else random.choice([0, 10]),
                "doNotTrack": False,
                "resolution": resolution,
            },
            "webgl": {
                "vendor": webgl["vendor"],
                "renderer": webgl["renderer"],
                "mode": "noise",
                "noise": webgl_noise,
            },
            "canvas": {
                "mode": "noise",
                "noise": canvas_noise,
            },
            "clientRects": {
                "mode": "noise",
                "noise": random.randint(3, 8),
            },
            "audioContext": {
                "mode": "noise",
                "noise": random.randint(5, 15),
            },
            "webRTC": {
                "mode": "disabled",
            },
            "timezone": {
                "id": timezone,
            },
            "geolocation": {
                "mode": "prompt",
                "latitude": 0,
                "longitude": 0,
                "accuracy": 10,
            },
            "mediaDevices": {
                "enableMasking": True,
                "uid": "",
                "audioInputs": 1,
                "audioOutputs": 1,
                "videoInputs": 1,
            },
            "storage": {
                "local": True,
            },
            "plugins": {
                "enableVulnerable": True,
                "enableFlash": False,
            },
        }
    @staticmethod
    def _infer_timezone(language: str) -> str:
        timezone_map = {
            "en-US": "America/New_York",
            "en-GB": "Europe/London",
            "zh-CN": "Asia/Shanghai",
            "ja-JP": "Asia/Tokyo",
            "de-DE": "Europe/Berlin",
            "fr-FR": "Europe/Paris",
        }
        return timezone_map.get(language, "America/New_York")
    @staticmethod
    def validate(fingerprint: Dict[str, Any]) -> bool:
        required_keys = ["navigator", "webgl", "canvas", "timezone"]
        for key in required_keys:
            if key not in fingerprint:
                return False
        user_agent = fingerprint.get("navigator", {}).get("userAgent", "")
        platform = fingerprint.get("navigator", {}).get("platform", "")
        if "Windows" in user_agent and platform != "Win32":
            return False
        if "Macintosh" in user_agent and platform != "MacIntel":
            return False
        if "Linux" in user_agent and "Linux" not in platform:
            return False
        return True