"""
Context Pool for Py-Parkour.
Maintains multiple browser contexts for reuse, enabling 10x faster challenge solving.
"""

import asyncio
from typing import Optional, Set, List, Dict, Any
from playwright.async_api import Browser, BrowserContext, Page

from .fingerprint import BrowserFingerprint


class ContextPool:
    """
    Maintains a pool of browser contexts for efficient reuse.
    
    Benefits:
    - 10x faster challenge solving (no context creation overhead)
    - Reduced memory churn
    - Pre-warmed contexts ready for immediate use
    
    Usage:
        pool = ContextPool(browser, pool_size=5)
        await pool.warm_up()
        
        context = await pool.acquire()
        try:
            page = await context.new_page()
            # ... do work ...
        finally:
            await pool.release(context)
    """
    
    def __init__(
        self, 
        browser: Browser, 
        pool_size: int = 5,
        fingerprint: Optional[BrowserFingerprint] = None,
        stealth_scripts: Optional[List[str]] = None
    ):
        """
        Initialize the context pool.
        
        Args:
            browser: Playwright Browser instance
            pool_size: Maximum number of contexts to maintain
            fingerprint: Optional fingerprint to apply to all contexts
            stealth_scripts: Optional list of JS scripts to inject on page creation
        """
        self.browser = browser
        self.pool_size = pool_size
        self.fingerprint = fingerprint
        self.stealth_scripts = stealth_scripts or []
        
        self._available: List[BrowserContext] = []
        self._in_use: Set[BrowserContext] = set()
        self._lock = asyncio.Lock()
        
        # Stats
        self._created = 0
        self._reused = 0
    
    @property
    def stats(self) -> Dict[str, int]:
        """Get pool statistics."""
        return {
            "pool_size": self.pool_size,
            "available": len(self._available),
            "in_use": len(self._in_use),
            "total_created": self._created,
            "total_reused": self._reused,
            "reuse_rate": self._reused / max(1, self._reused + self._created),
        }
    
    async def _create_context(self) -> BrowserContext:
        """Create a new browser context with fingerprint and stealth scripts."""
        # Get context options from fingerprint or use defaults
        if self.fingerprint:
            context_options = self.fingerprint.to_context_options()
        else:
            context_options = {}
        
        context = await self.browser.new_context(**context_options)
        
        # Inject stealth scripts on every new page
        if self.stealth_scripts:
            async def inject_stealth(page: Page):
                for script in self.stealth_scripts:
                    await page.add_init_script(script)
            
            context.on("page", lambda page: asyncio.create_task(inject_stealth(page)))
        
        self._created += 1
        return context
    
    async def warm_up(self, count: Optional[int] = None):
        """
        Pre-create contexts for immediate availability.
        
        Args:
            count: Number of contexts to create (defaults to pool_size)
        """
        count = count or self.pool_size
        count = min(count, self.pool_size - len(self._available))
        
        if count <= 0:
            return
        
        async with self._lock:
            tasks = [self._create_context() for _ in range(count)]
            contexts = await asyncio.gather(*tasks)
            self._available.extend(contexts)
        
        print(f"ContextPool: Warmed up {count} contexts (total available: {len(self._available)})")
    
    async def acquire(self) -> BrowserContext:
        """
        Get a context from the pool or create a new one.
        
        Returns:
            BrowserContext ready for use
        """
        async with self._lock:
            if self._available:
                context = self._available.pop()
                self._in_use.add(context)
                self._reused += 1
                return context
            
            # No available contexts, create new one
            context = await self._create_context()
            self._in_use.add(context)
            return context
    
    async def release(self, context: BrowserContext, clean: bool = True):
        """
        Return a context to the pool for reuse.
        
        Args:
            context: The context to release
            clean: Whether to clean the context (clear cookies, close pages)
        """
        async with self._lock:
            if context not in self._in_use:
                return
            
            self._in_use.discard(context)
            
            # Clean the context for reuse
            if clean:
                try:
                    # Close all pages
                    for page in context.pages:
                        await page.close()
                    
                    # Clear cookies
                    await context.clear_cookies()
                except Exception:
                    # Context might be corrupted, don't reuse
                    try:
                        await context.close()
                    except Exception:
                        pass
                    return
            
            # Return to pool if not at capacity
            if len(self._available) < self.pool_size:
                self._available.append(context)
            else:
                # Pool full, close the context
                try:
                    await context.close()
                except Exception:
                    pass
    
    async def acquire_with_page(self) -> tuple:
        """
        Acquire a context and create a new page in one call.
        
        Returns:
            Tuple of (BrowserContext, Page)
        """
        context = await self.acquire()
        page = await context.new_page()
        return context, page
    
    async def close_all(self):
        """Close all contexts in the pool."""
        async with self._lock:
            # Close available contexts
            for context in self._available:
                try:
                    await context.close()
                except Exception:
                    pass
            self._available.clear()
            
            # Close in-use contexts
            for context in list(self._in_use):
                try:
                    await context.close()
                except Exception:
                    pass
            self._in_use.clear()
        
        print(f"ContextPool: Closed all contexts. Stats: {self.stats}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.warm_up()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_all()


class PooledContext:
    """
    Context manager for acquiring and auto-releasing pooled contexts.
    
    Usage:
        async with PooledContext(pool) as (context, page):
            await page.goto("https://example.com")
            # Context automatically released when done
    """
    
    def __init__(self, pool: ContextPool, with_page: bool = True):
        self.pool = pool
        self.with_page = with_page
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        if self.with_page:
            self.context, self.page = await self.pool.acquire_with_page()
            return self.context, self.page
        else:
            self.context = await self.pool.acquire()
            return self.context
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.pool.release(self.context)
