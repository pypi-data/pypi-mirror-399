"""
ParkourDriver - Enhanced Browser Driver for Py-Parkour.
Wrapper around Playwright with fingerprint, stealth, and context pool support.
"""

import asyncio
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from .fingerprint import BrowserFingerprint, FingerprintGallery
from .stealth import StealthInjector
from .context_pool import ContextPool


class ParkourDriver:
    """
    Enhanced wrapper around Playwright to manage browser lifecycle.
    
    Features:
    - Fingerprint synchronization with TLS layer
    - Stealth script injection
    - Context pooling for faster operations
    - Flexible browser configuration
    """
    
    def __init__(
        self, 
        headless: bool = True,
        fingerprint: Optional[BrowserFingerprint] = None,
        stealth: bool = True,
        pool_size: int = 0
    ):
        """
        Initialize the driver.
        
        Args:
            headless: Run browser in headless mode
            fingerprint: Browser fingerprint to use (or None for default)
            stealth: Enable stealth evasion scripts
            pool_size: Context pool size (0 = no pooling)
        """
        self.headless = headless
        self.fingerprint = fingerprint
        self.stealth = stealth
        self.pool_size = pool_size
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.pool: Optional[ContextPool] = None
    
    async def start(self):
        """Start the Playwright engine and browser."""
        self.playwright = await async_playwright().start()
        
        # Browser launch arguments for stealth
        launch_args = []
        if self.stealth:
            launch_args.extend([
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ])
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=launch_args if launch_args else None
        )
        
        # Create context with fingerprint
        context_options = {}
        if self.fingerprint:
            context_options = self.fingerprint.to_context_options()
        
        self.context = await self.browser.new_context(**context_options)
        
        # Inject stealth scripts into context
        if self.stealth:
            await StealthInjector.inject_into_context(self.context)
            if self.fingerprint:
                # Will inject fingerprint on each new page
                self.context.on("page", lambda p: asyncio.create_task(
                    StealthInjector.inject_fingerprint(p, self.fingerprint)
                ))
        
        self.page = await self.context.new_page()
        
        # Initialize context pool if enabled
        if self.pool_size > 0:
            stealth_scripts = StealthInjector.get_all_scripts() if self.stealth else None
            self.pool = ContextPool(
                self.browser,
                pool_size=self.pool_size,
                fingerprint=self.fingerprint,
                stealth_scripts=stealth_scripts
            )
            await self.pool.warm_up()
    
    async def stop(self):
        """Stop the browser and Playwright engine."""
        if self.pool:
            await self.pool.close_all()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def goto(self, url: str):
        """Navigate to the specified URL."""
        if not self.page:
            raise RuntimeError("Driver not started. Call await driver.start() first.")
        await self.page.goto(url)
    
    async def get_content(self) -> str:
        """Return the current page content."""
        if not self.page:
            raise RuntimeError("Driver not started.")
        return await self.page.content()
    
    async def new_page(self) -> Page:
        """Create a new page in the current context."""
        if not self.context:
            raise RuntimeError("Driver not started.")
        page = await self.context.new_page()
        if self.stealth and self.fingerprint:
            await StealthInjector.inject_fingerprint(page, self.fingerprint)
        return page
    
    async def get_pooled_context(self) -> BrowserContext:
        """Get a context from the pool (if pooling is enabled)."""
        if not self.pool:
            raise RuntimeError("Context pooling not enabled. Set pool_size > 0.")
        return await self.pool.acquire()
    
    async def release_pooled_context(self, context: BrowserContext):
        """Release a pooled context back to the pool."""
        if self.pool:
            await self.pool.release(context)
    
    def set_fingerprint(self, fingerprint: BrowserFingerprint):
        """
        Set fingerprint for future contexts.
        Note: Does not affect already-created contexts.
        """
        self.fingerprint = fingerprint
    
    @classmethod
    def with_profile(cls, profile_name: str, headless: bool = True, stealth: bool = True) -> "ParkourDriver":
        """
        Create driver with a pre-built fingerprint profile.
        
        Args:
            profile_name: Profile name from FingerprintGallery (e.g., 'chrome_120_win11')
            headless: Run in headless mode
            stealth: Enable stealth evasions
            
        Returns:
            Configured ParkourDriver instance
        """
        fingerprint = FingerprintGallery.get(profile_name)
        return cls(headless=headless, fingerprint=fingerprint, stealth=stealth)

