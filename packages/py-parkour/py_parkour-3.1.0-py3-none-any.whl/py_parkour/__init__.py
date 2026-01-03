"""
Py-Parkour: The Hybrid Scraper Framework
Version: 3.0.0

A lightweight automation utility for modern web scraping:
- Cookie consent bypassing
- Auto-pagination
- Verification gate handling
- Hybrid scraping (browser + API)
- Stealth and fingerprint synchronization
"""

from typing import AsyncGenerator, Any, Dict, List, Optional

# Core components
from .core.driver import ParkourDriver
from .core.fingerprint import BrowserFingerprint, FingerprintGallery
from .core.stealth import StealthInjector
from .core.context_pool import ContextPool, PooledContext

# Gadgets
from .gadgets.crusher import Crusher
from .gadgets.compass import Compass
from .gadgets.disguises import Disguises
from .gadgets.shadow import Shadow
from .gadgets.radar import Radar
from .gadgets.ghost_cursor import GhostCursor
from .gadgets.spatial import SpatialCompass
from .gadgets.chaos_typer import ChaosTyper
from .gadgets.solicitor import Solicitor, TwoCaptchaSolver
from .gadgets.turnstile_solver import TurnstileSolver

__version__ = "3.0.0"

__all__ = [
    # Main API
    "ParkourBot",
    
    # Core
    "ParkourDriver",
    "BrowserFingerprint",
    "FingerprintGallery",
    "StealthInjector",
    "ContextPool",
    "PooledContext",
    
    # Gadgets
    "Crusher",
    "Compass",
    "Disguises",
    "Shadow",
    "Radar",
    "GhostCursor",
    "SpatialCompass",
    "ChaosTyper",
    "Solicitor",
    "TwoCaptchaSolver",
    "TurnstileSolver",
]


class ParkourBot:
    """
    The main unified API for Py-Parkour.
    Combines the Pilot (Driver) and the Gadgets.
    
    Features (v3.0):
    - Pluggable gadgets via constructor
    - Browser fingerprint synchronization with TLS layer
    - Context pooling for faster challenge solving
    - Built-in Turnstile solver
    - Full session export for cloudscraper integration
    
    Example:
        bot = ParkourBot(
            headless=True,
            gadgets=['ghost_cursor', 'turnstile_solver'],
            fingerprint={'user_agent': 'Mozilla/5.0...'}
        )
        await bot.start()
        await bot.solve_turnstile()
        session = await bot.export_session()
    """
    
    # Available gadgets
    AVAILABLE_GADGETS = [
        'crusher', 'compass', 'disguises', 'shadow', 'radar',
        'ghost', 'spatial', 'typer', 'solicitor', 'turnstile'
    ]
    
    def __init__(
        self, 
        headless: bool = True,
        gadgets: List[str] = None,
        fingerprint: Dict[str, Any] = None,
        pool_size: int = 0,
        stealth: bool = True,
        browser: str = "chromium"
    ):
        """
        Initialize ParkourBot with optional configuration.
        
        Args:
            headless: Run browser in headless mode
            gadgets: List of gadgets to enable (default: all)
                     Options: crusher, compass, disguises, shadow, radar,
                              ghost, spatial, typer, solicitor, turnstile
            fingerprint: Browser fingerprint config dict or profile name string
                         e.g., {'user_agent': '...', 'viewport': {...}}
                         or use FingerprintGallery.get('chrome_120_win11')
            pool_size: Number of browser contexts to pool (0 = no pooling)
            stealth: Enable stealth evasion scripts (recommended)
            browser: Browser engine to use ('chromium', 'firefox', 'webkit')
        """
        # Parse fingerprint
        browser_fingerprint = None
        if fingerprint:
            if isinstance(fingerprint, str):
                # Profile name
                browser_fingerprint = FingerprintGallery.get(fingerprint)
            elif isinstance(fingerprint, dict):
                # Dict config
                browser_fingerprint = BrowserFingerprint.from_dict(fingerprint)
            elif isinstance(fingerprint, BrowserFingerprint):
                browser_fingerprint = fingerprint
        
        # Initialize driver
        self.driver = ParkourDriver(
            headless=headless,
            fingerprint=browser_fingerprint,
            stealth=stealth,
            pool_size=pool_size,
            browser_type=browser
        )
        
        # Configuration
        self._enabled_gadgets = set(gadgets) if gadgets else set(self.AVAILABLE_GADGETS)
        self._fingerprint = browser_fingerprint
        self._stealth = stealth
        self._pool_size = pool_size
        self._browser = browser
        
        # Disguises is always available (no browser required)
        self.identity = Disguises()
        
        # These are initialized after browser start
        self.crusher: Optional[Crusher] = None
        self.compass: Optional[Compass] = None
        self.shadow: Optional[Shadow] = None
        self.radar: Optional[Radar] = None
        self.ghost: Optional[GhostCursor] = None
        self.spatial: Optional[SpatialCompass] = None
        self.typer: Optional[ChaosTyper] = None
        self.solicitor: Optional[Solicitor] = None
        self.turnstile: Optional[TurnstileSolver] = None
    
    async def start(self):
        """Start the browser session and initialize gadgets."""
        await self.driver.start()
        
        page = self.driver.page
        
        # Initialize enabled gadgets
        if 'crusher' in self._enabled_gadgets:
            self.crusher = Crusher(page)
        
        if 'compass' in self._enabled_gadgets:
            self.compass = Compass(page)
        
        if 'shadow' in self._enabled_gadgets:
            self.shadow = Shadow(page)
        
        if 'radar' in self._enabled_gadgets:
            self.radar = Radar(page)
            self.radar.start()
        
        if 'ghost' in self._enabled_gadgets:
            self.ghost = GhostCursor(page)
        
        if 'spatial' in self._enabled_gadgets:
            self.spatial = SpatialCompass(page)
        
        if 'typer' in self._enabled_gadgets:
            self.typer = ChaosTyper(page)
        
        if 'solicitor' in self._enabled_gadgets:
            self.solicitor = Solicitor(page)
        
        if 'turnstile' in self._enabled_gadgets:
            self.turnstile = TurnstileSolver(page, self.ghost)
    
    async def close(self):
        """Close the browser session."""
        await self.driver.stop()
    
    async def goto(self, url: str):
        """Navigate to a URL."""
        await self.driver.goto(url)
        
        # Reset ghost cursor position on navigation
        if self.ghost:
            self.ghost.reset_position()
    
    @property
    def current_url(self) -> str:
        """Get current page URL."""
        if self.driver.page:
            return self.driver.page.url
        return ""
    
    @property
    def page(self):
        """Get the current Playwright page."""
        return self.driver.page
    
    # ========================
    # Convenience Methods
    # ========================
    
    async def crush_cookies(self):
        """Clear cookie banners (Crusher gadget)."""
        if not self.crusher:
            raise RuntimeError("Crusher gadget not enabled or bot not started.")
        await self.crusher.clear_path()
    
    async def crawl(self, max_pages: int = 5) -> AsyncGenerator[int, None]:
        """Iterate through pages using the Compass."""
        if not self.compass:
            raise RuntimeError("Compass gadget not enabled or bot not started.")
        async for page_num in self.compass.crawl(max_pages=max_pages):
            yield page_num
    
    async def solve_turnstile(self, url: str = None, timeout: int = 30) -> bool:
        """
        Solve Cloudflare Turnstile challenge.
        
        Args:
            url: URL to navigate to (optional, uses current page if None)
            timeout: Maximum seconds to wait for solution
            
        Returns:
            True if solved successfully
        """
        if not self.turnstile:
            raise RuntimeError("Turnstile gadget not enabled or bot not started.")
        
        if url:
            await self.goto(url)
        
        return await self.turnstile.solve(timeout=timeout)
    
    async def export_session(self) -> Dict[str, Any]:
        """
        Export session state for cloudscraper/requests integration.
        
        Returns:
            Dictionary with cookies, headers, localStorage, etc.
        """
        if not self.shadow:
            raise RuntimeError("Shadow gadget not enabled or bot not started.")
        
        return await self.shadow.export_session()
    
    async def import_to_cloudscraper(self, scraper) -> None:
        """
        Import session directly into a cloudscraper instance.
        
        Args:
            scraper: cloudscraper session object
        """
        if not self.shadow:
            raise RuntimeError("Shadow gadget not enabled or bot not started.")
        
        await self.shadow.import_to_cloudscraper(scraper)
    
    async def auto_setup_identity(self, url: str):
        """
        The 'Magic' Auto-Setup for verification flows.
        1. Generates temporary identity
        2. Fills email/code fields automatically
        """
        if not self.driver.page:
            await self.start()
        
        await self.goto(url)
        
        print("Auto-Setup: Generating identity...")
        id_data = await self.identity.generate_identity()
        print(f"Auto-Setup: Using {id_data.email}")
        
        # Magic Action: Fill email
        try:
            email_input = self.driver.page.locator("input[type='email'], input[name*='email']").first
            if await email_input.count() > 0:
                await email_input.fill(id_data.email)
                print("Auto-Setup: Filled email.")
                
                await email_input.press("Enter")
                print("Auto-Setup: Submitted email form.")
                
                code = await self.identity.wait_for_code()
                if code:
                    code_input = self.driver.page.locator("input[name*='code'], input[name*='otp'], input[id*='code']").first
                    if await code_input.count() > 0:
                        await code_input.fill(code)
                        await code_input.press("Enter")
                        print("Auto-Setup: Submitted verification code.")
                    else:
                        print("Auto-Setup: Could not find code input field.")
            else:
                print("Auto-Setup: Could not find email input field.")
        
        except Exception as e:
            print(f"Auto-Setup failed: {e}")
    
    # ========================
    # Context Pool Methods
    # ========================
    
    async def get_pooled_context(self):
        """Get a context from the pool for parallel operations."""
        if not self.driver.pool:
            raise RuntimeError("Context pooling not enabled. Set pool_size > 0.")
        return await self.driver.pool.acquire()
    
    async def release_pooled_context(self, context):
        """Release a pooled context back to the pool."""
        if self.driver.pool:
            await self.driver.pool.release(context)
    
    def pool_stats(self) -> Dict[str, int]:
        """Get context pool statistics."""
        if self.driver.pool:
            return self.driver.pool.stats
        return {"error": "Pooling not enabled"}
    
    # ========================
    # Factory Methods
    # ========================
    
    @classmethod
    def with_profile(
        cls, 
        profile: str,
        headless: bool = True,
        gadgets: List[str] = None,
        pool_size: int = 0
    ) -> "ParkourBot":
        """
        Create bot with a pre-built fingerprint profile.
        
        Args:
            profile: Profile name (e.g., 'chrome_120_win11', 'firefox_121_linux')
            headless: Run in headless mode
            gadgets: List of gadgets to enable
            pool_size: Context pool size
            
        Returns:
            Configured ParkourBot instance
        """
        fingerprint = FingerprintGallery.get(profile)
        return cls(
            headless=headless,
            gadgets=gadgets,
            fingerprint=fingerprint,
            pool_size=pool_size,
            stealth=True
        )
    
    @classmethod
    def for_cloudscraper(
        cls,
        tls_profile: str = "chrome_120_win11",
        headless: bool = True
    ) -> "ParkourBot":
        """
        Create bot optimized for cloudscraper integration.
        
        Args:
            tls_profile: TLS-Chameleon profile to match
            headless: Run in headless mode
            
        Returns:
            ParkourBot configured for cloudscraper handoff
        """
        return cls.with_profile(
            profile=tls_profile,
            headless=headless,
            gadgets=['ghost', 'turnstile', 'shadow', 'crusher'],
            pool_size=0
        )

