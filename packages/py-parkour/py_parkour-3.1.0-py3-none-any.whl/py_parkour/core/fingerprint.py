"""
Fingerprint Sync API for Py-Parkour.
Matches browser fingerprint with TLS layer (e.g., TLS-Chameleon profiles).
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import random


@dataclass
class BrowserFingerprint:
    """
    Browser fingerprint configuration for stealth.
    Designed to sync with TLS-Chameleon profiles.
    """
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    locale: str = "en-US"
    timezone: str = "America/New_York"
    platform: str = "Win32"
    
    # WebGL fingerprint
    webgl_vendor: str = "Google Inc. (Intel)"
    webgl_renderer: str = "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)"
    
    # Hardware
    device_memory: int = 8  # GB
    hardware_concurrency: int = 8  # CPU cores
    
    # Screen
    screen_width: int = 1920
    screen_height: int = 1080
    color_depth: int = 24
    pixel_ratio: float = 1.0
    
    # Languages
    languages: List[str] = field(default_factory=lambda: ["en-US", "en"])
    
    # Extra TLS sync data
    ja3_hash: Optional[str] = None
    
    def to_context_options(self) -> Dict[str, Any]:
        """Convert to Playwright browser context options."""
        return {
            "user_agent": self.user_agent,
            "viewport": self.viewport,
            "locale": self.locale,
            "timezone_id": self.timezone,
            "device_scale_factor": self.pixel_ratio,
            "color_scheme": "light",
            "extra_http_headers": {
                "Accept-Language": ",".join(self.languages),
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Export fingerprint as dictionary."""
        return {
            "user_agent": self.user_agent,
            "viewport": self.viewport,
            "locale": self.locale,
            "timezone": self.timezone,
            "platform": self.platform,
            "webgl_vendor": self.webgl_vendor,
            "webgl_renderer": self.webgl_renderer,
            "device_memory": self.device_memory,
            "hardware_concurrency": self.hardware_concurrency,
            "screen": {
                "width": self.screen_width,
                "height": self.screen_height,
                "color_depth": self.color_depth,
                "pixel_ratio": self.pixel_ratio,
            },
            "languages": self.languages,
            "ja3_hash": self.ja3_hash,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrowserFingerprint":
        """Create fingerprint from dictionary."""
        screen = data.get("screen", {})
        return cls(
            user_agent=data.get("user_agent", cls.user_agent),
            viewport=data.get("viewport", {"width": 1920, "height": 1080}),
            locale=data.get("locale", "en-US"),
            timezone=data.get("timezone", "America/New_York"),
            platform=data.get("platform", "Win32"),
            webgl_vendor=data.get("webgl_vendor", cls.webgl_vendor),
            webgl_renderer=data.get("webgl_renderer", cls.webgl_renderer),
            device_memory=data.get("device_memory", 8),
            hardware_concurrency=data.get("hardware_concurrency", 8),
            screen_width=screen.get("width", 1920),
            screen_height=screen.get("height", 1080),
            color_depth=screen.get("color_depth", 24),
            pixel_ratio=screen.get("pixel_ratio", 1.0),
            languages=data.get("languages", ["en-US", "en"]),
            ja3_hash=data.get("ja3_hash"),
        )


class FingerprintGallery:
    """
    Pre-built browser fingerprint profiles.
    Designed to match TLS-Chameleon profile names.
    """
    
    # Chrome profiles
    CHROME_120_WIN11 = BrowserFingerprint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        platform="Win32",
        timezone="America/New_York",
        webgl_vendor="Google Inc. (NVIDIA)",
        webgl_renderer="ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    )
    
    CHROME_120_WIN10 = BrowserFingerprint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        platform="Win32",
        timezone="America/Chicago",
        device_memory=16,
        hardware_concurrency=12,
    )
    
    CHROME_120_MACOS = BrowserFingerprint(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        platform="MacIntel",
        timezone="America/Los_Angeles",
        webgl_vendor="Google Inc. (Apple)",
        webgl_renderer="ANGLE (Apple, Apple M1 Pro, OpenGL 4.1)",
        device_memory=16,
        hardware_concurrency=10,
    )
    
    CHROME_121_WIN11 = BrowserFingerprint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        platform="Win32",
        timezone="America/New_York",
    )
    
    # Firefox profiles
    FIREFOX_121_WIN11 = BrowserFingerprint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        platform="Win32",
        timezone="Europe/London",
        webgl_vendor="Mozilla",
        webgl_renderer="Mozilla",
    )
    
    FIREFOX_121_LINUX = BrowserFingerprint(
        user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        platform="Linux x86_64",
        timezone="Europe/Berlin",
        webgl_vendor="Mozilla",
        webgl_renderer="Mozilla",
    )
    
    # Safari profiles
    SAFARI_17_MACOS = BrowserFingerprint(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        platform="MacIntel",
        timezone="America/Los_Angeles",
        webgl_vendor="Apple Inc.",
        webgl_renderer="Apple GPU",
        device_memory=16,
    )
    
    SAFARI_17_IOS = BrowserFingerprint(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        platform="iPhone",
        timezone="America/New_York",
        viewport={"width": 390, "height": 844},
        screen_width=390,
        screen_height=844,
        pixel_ratio=3.0,
        device_memory=4,
        hardware_concurrency=6,
    )
    
    # Edge profiles
    EDGE_120_WIN11 = BrowserFingerprint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        platform="Win32",
        timezone="America/New_York",
    )
    
    # Profile mapping for TLS-Chameleon sync
    PROFILE_MAP = {
        "chrome_120_win11": CHROME_120_WIN11,
        "chrome_120_win10": CHROME_120_WIN10,
        "chrome_120_macos": CHROME_120_MACOS,
        "chrome_121_win11": CHROME_121_WIN11,
        "firefox_121_win11": FIREFOX_121_WIN11,
        "firefox_121_linux": FIREFOX_121_LINUX,
        "safari_17_macos": SAFARI_17_MACOS,
        "safari_17_ios": SAFARI_17_IOS,
        "edge_120_win11": EDGE_120_WIN11,
    }
    
    @classmethod
    def get(cls, profile_name: str) -> BrowserFingerprint:
        """
        Get a fingerprint profile by name.
        
        Args:
            profile_name: Profile name matching TLS-Chameleon (e.g., 'chrome_120_win11')
            
        Returns:
            BrowserFingerprint instance
        """
        if profile_name not in cls.PROFILE_MAP:
            available = ", ".join(cls.PROFILE_MAP.keys())
            raise ValueError(f"Unknown profile '{profile_name}'. Available: {available}")
        return cls.PROFILE_MAP[profile_name]
    
    @classmethod
    def from_tls_profile(cls, tls_profile: str) -> BrowserFingerprint:
        """
        Create fingerprint matching a TLS-Chameleon profile.
        Alias for get() with TLS-Chameleon naming convention.
        """
        return cls.get(tls_profile)
    
    @classmethod
    def list_profiles(cls) -> List[str]:
        """List all available profile names."""
        return list(cls.PROFILE_MAP.keys())
    
    @classmethod
    def randomize(cls, fingerprint: BrowserFingerprint, variation: float = 0.1) -> BrowserFingerprint:
        """
        Add slight randomization to a fingerprint to avoid pattern detection.
        
        Args:
            fingerprint: Base fingerprint to randomize
            variation: Amount of variation (0.0-1.0)
            
        Returns:
            New randomized BrowserFingerprint
        """
        # Randomize viewport slightly
        width_var = int(fingerprint.viewport["width"] * variation * random.uniform(-1, 1))
        height_var = int(fingerprint.viewport["height"] * variation * random.uniform(-1, 1))
        
        # Randomize screen size to match
        new_viewport = {
            "width": fingerprint.viewport["width"] + width_var,
            "height": fingerprint.viewport["height"] + height_var,
        }
        
        # Pick random timezone from same region
        timezones = {
            "America": ["America/New_York", "America/Chicago", "America/Los_Angeles", "America/Denver"],
            "Europe": ["Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Amsterdam"],
            "Asia": ["Asia/Tokyo", "Asia/Singapore", "Asia/Seoul", "Asia/Shanghai"],
        }
        
        current_region = fingerprint.timezone.split("/")[0]
        if current_region in timezones:
            new_timezone = random.choice(timezones[current_region])
        else:
            new_timezone = fingerprint.timezone
        
        return BrowserFingerprint(
            user_agent=fingerprint.user_agent,
            viewport=new_viewport,
            locale=fingerprint.locale,
            timezone=new_timezone,
            platform=fingerprint.platform,
            webgl_vendor=fingerprint.webgl_vendor,
            webgl_renderer=fingerprint.webgl_renderer,
            device_memory=fingerprint.device_memory,
            hardware_concurrency=fingerprint.hardware_concurrency,
            screen_width=new_viewport["width"],
            screen_height=new_viewport["height"],
            color_depth=fingerprint.color_depth,
            pixel_ratio=fingerprint.pixel_ratio,
            languages=fingerprint.languages,
            ja3_hash=fingerprint.ja3_hash,
        )
