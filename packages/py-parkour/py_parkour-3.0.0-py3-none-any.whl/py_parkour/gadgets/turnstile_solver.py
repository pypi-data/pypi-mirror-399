"""
Turnstile Auto-Solver for Py-Parkour.
Built-in Cloudflare Turnstile solver using micro-interaction patterns.
No external API needed - uses behavioral patterns to pass validation.
"""

import asyncio
import random
from typing import Optional, Dict, Any
from playwright.async_api import Page, Frame, ElementHandle

from .ghost_cursor import GhostCursor


class TurnstileSolver:
    """
    Built-in Cloudflare Turnstile solver using micro-interactions.
    
    Unlike external API solvers (2Captcha, etc.), this attempts to solve
    Turnstile naturally by simulating human behavior patterns.
    
    Success rate depends on:
    - Stealth evasions being properly injected
    - Natural mouse movement patterns
    - Browser fingerprint consistency
    
    Usage:
        solver = TurnstileSolver(page)
        success = await solver.solve()
    """
    
    # Turnstile selectors
    TURNSTILE_CONTAINER_SELECTORS = [
        ".cf-turnstile",
        "[data-turnstile]",
        "div[id^='cf-turnstile']",
        "iframe[src*='challenges.cloudflare.com/turnstile']",
    ]
    
    TURNSTILE_IFRAME_PATTERNS = [
        "challenges.cloudflare.com/turnstile",
        "challenges.cloudflare.com/cdn-cgi/challenge-platform",
    ]
    
    def __init__(self, page: Page, ghost: Optional[GhostCursor] = None):
        """
        Initialize the Turnstile solver.
        
        Args:
            page: Playwright Page instance
            ghost: Optional GhostCursor for human-like movement (creates one if not provided)
        """
        self.page = page
        self.ghost = ghost or GhostCursor(page)
        
        # Behavior timing (randomized for each attempt)
        self.pre_click_delay = (0.5, 2.0)  # Seconds before clicking
        self.post_click_delay = (0.3, 1.0)  # Seconds after clicking
        self.idle_movement_duration = (1.0, 3.0)  # Idle movement duration
    
    async def detect_turnstile(self) -> Optional[str]:
        """
        Detect Turnstile on the page and in all iframes.
        
        Returns:
            Selector or 'iframe' string if found, None otherwise
        """
        # 1. Check main page selectors
        for selector in self.TURNSTILE_CONTAINER_SELECTORS:
            try:
                element = self.page.locator(selector).first
                if await element.count() > 0:
                    return selector
            except Exception:
                continue
        
        # 2. Check all frames for Turnstile URLs
        for frame in self.page.frames:
            try:
                frame_url = frame.url
                for pattern in self.TURNSTILE_IFRAME_PATTERNS:
                    if pattern in frame_url:
                        # Find the iframe element in the parent page to get a selector
                        return f"iframe[src*='{pattern}']"
            except Exception:
                continue
                
        return None
    
    async def _find_turnstile_frame(self) -> Optional[Frame]:
        """Find the Turnstile iframe."""
        for frame in self.page.frames:
            frame_url = frame.url
            for pattern in self.TURNSTILE_IFRAME_PATTERNS:
                if pattern in frame_url:
                    return frame
        return None
    
    async def _find_checkbox(self, frame: Frame) -> Optional[ElementHandle]:
        """Find the checkbox element within the Turnstile frame."""
        checkbox_selectors = [
            "input[type='checkbox']",
            ".checkbox",
            "[role='checkbox']",
            "#turnstile-wrapper input",
            "label",
            "div.ctp-checkbox-container",
            "#challenge-stage",
        ]
        
        for selector in checkbox_selectors:
            try:
                element = await frame.query_selector(selector)
                if element:
                    is_visible = await element.is_visible()
                    print(f"TurnstileSolver: Found potential checkbox with selector: {selector} (visible: {is_visible})")
                    return element
            except Exception:
                continue
        return None
    
    async def _simulate_human_presence(self):
        """
        Simulate human browsing behavior before interacting with Turnstile.
        This helps establish a "human" pattern in the page.
        """
        # Random scroll
        scroll_amount = random.randint(50, 200)
        scroll_direction = random.choice([1, -1])
        await self.page.evaluate(f"window.scrollBy(0, {scroll_amount * scroll_direction})")
        
        # Small wait
        await asyncio.sleep(random.uniform(0.3, 0.8))
        
        # Scroll back
        await self.page.evaluate(f"window.scrollBy(0, {-scroll_amount * scroll_direction // 2})")
        
        # Move mouse randomly
        viewport = self.page.viewport_size or {"width": 1920, "height": 1080}
        random_x = random.randint(100, viewport["width"] - 100)
        random_y = random.randint(100, viewport["height"] - 100)
        
        await self.ghost.move_to(x=random_x, y=random_y, steps=15)
        
        # Random pause
        await asyncio.sleep(random.uniform(*self.idle_movement_duration))
    
    async def _get_element_center(self, element: ElementHandle) -> tuple:
        """Get the center coordinates of an element."""
        box = await element.bounding_box()
        if box:
            center_x = box["x"] + box["width"] / 2
            center_y = box["y"] + box["height"] / 2
            return center_x, center_y
        return None, None
    
    async def solve(self, timeout: int = 30, simulate_human: bool = True) -> bool:
        """
        Attempt to solve Turnstile using micro-interactions.
        
        Args:
            timeout: Maximum seconds to wait for solution
            simulate_human: Whether to simulate human presence before solving
            
        Returns:
            True if solved successfully, False otherwise
        """
        print("TurnstileSolver: Attempting to solve Turnstile...")
        
        # 1. Find Turnstile
        container_selector = await self.detect_turnstile()
        if not container_selector:
            print("TurnstileSolver: No Turnstile detected on page")
            return False
        
        print(f"TurnstileSolver: Found Turnstile container: {container_selector}")
        
        # 2. Wait for Turnstile to load (lenient)
        try:
            # Check if it's already solved first
            if await self.is_solved():
                print("TurnstileSolver: Challenge already solved")
                return True
                
            # Wait for selector with shorter timeout and continue anyway
            await self.page.wait_for_selector(container_selector, state="attached", timeout=5000)
            print(f"TurnstileSolver: Container {container_selector} attached")
        except Exception as e:
            print(f"TurnstileSolver: Container wait timed out, continuing: {e}")
        
        # 3. Simulate human presence
        if simulate_human:
            await self._simulate_human_presence()
        
        # 4. Find the Turnstile frame
        frame = await self._find_turnstile_frame()
        if not frame:
            # Maybe it's not in an iframe (embedded mode)
            print("TurnstileSolver: No iframe found, trying direct interaction...")
            return await self._solve_embedded(container_selector, timeout)
        
        print(f"TurnstileSolver: Found Turnstile frame: {frame.url}")
        
        # 5. Wait for frame to be ready
        await asyncio.sleep(random.uniform(1.0, 2.0))
        
        # 6. Find checkbox in frame
        checkbox = await self._find_checkbox(frame)
        if not checkbox:
            print("TurnstileSolver: Could not find checkbox in Turnstile frame")
            return await self._solve_by_container_click(container_selector, timeout)
        
        # 7. Pre-click delay (human hesitation)
        await asyncio.sleep(random.uniform(*self.pre_click_delay))
        
        # 8. Move to checkbox and click
        center_x, center_y = await self._get_element_center(checkbox)
        if center_x and center_y:
            # Add some randomness to click position
            click_x = center_x + random.randint(-3, 3)
            click_y = center_y + random.randint(-3, 3)
            
            await self.ghost.move_to(x=click_x, y=click_y, steps=20)
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Use force=True in case it's "not visible" but attached
            await checkbox.click(force=True)
        else:
            await checkbox.click(force=True)
        
        # 9. Post-click delay
        await asyncio.sleep(random.uniform(*self.post_click_delay))
        
        # 10. Wait for verification
        return await self._wait_for_success(timeout)
    
    async def _solve_embedded(self, container_selector: str, timeout: int) -> bool:
        """Solve embedded (non-iframe) Turnstile."""
        try:
            container = self.page.locator(container_selector).first
            
            # Move to container and click
            box = await container.bounding_box()
            if box:
                center_x = box["x"] + box["width"] / 2 + random.randint(-5, 5)
                center_y = box["y"] + box["height"] / 2 + random.randint(-5, 5)
                
                await self.ghost.move_to(x=center_x, y=center_y, steps=20)
                await asyncio.sleep(random.uniform(0.2, 0.5))
                await container.click()
                
                return await self._wait_for_success(timeout)
        except Exception as e:
            print(f"TurnstileSolver: Embedded solve failed: {e}")
        
        return False
    
    async def _solve_by_container_click(self, container_selector: str, timeout: int) -> bool:
        """Fallback: Click the container directly."""
        print("TurnstileSolver: Trying container click fallback...")
        return await self._solve_embedded(container_selector, timeout)
    
    async def _wait_for_success(self, timeout: int) -> bool:
        """Wait for Turnstile to be solved."""
        success_indicators = [
            "[data-turnstile-response]",
            "input[name='cf-turnstile-response'][value]",
            ".cf-turnstile[data-success='true']",
        ]
        
        end_time = asyncio.get_event_loop().time() + timeout
        
        while asyncio.get_event_loop().time() < end_time:
            # Check for success indicators
            for selector in success_indicators:
                try:
                    element = self.page.locator(selector).first
                    if await element.count() > 0:
                        # Check if response token exists
                        if "response" in selector.lower():
                            value = await element.get_attribute("value")
                            if value and len(value) > 10:
                                print("TurnstileSolver: ✅ Turnstile solved!")
                                return True
                        else:
                            print("TurnstileSolver: ✅ Turnstile solved!")
                            return True
                except Exception:
                    continue
            
            # Check for hidden input with token
            try:
                token = await self.page.evaluate("""
                    () => {
                        const input = document.querySelector('input[name="cf-turnstile-response"]');
                        return input ? input.value : null;
                    }
                """)
                if token and len(token) > 10:
                    print("TurnstileSolver: ✅ Turnstile solved (via token)!")
                    return True
            except Exception:
                pass
            
            await asyncio.sleep(0.5)
        
        print("TurnstileSolver: ❌ Timeout waiting for Turnstile solution")
        return False
    
    async def get_token(self) -> Optional[str]:
        """
        Get the Turnstile response token after solving.
        
        Returns:
            Token string if available, None otherwise
        """
        try:
            token = await self.page.evaluate("""
                () => {
                    const input = document.querySelector('input[name="cf-turnstile-response"]');
                    return input ? input.value : null;
                }
            """)
            return token if token else None
        except Exception:
            return None
    
    async def is_present(self) -> bool:
        """Check if Turnstile is present on the page."""
        return await self.detect_turnstile() is not None
    
    async def is_solved(self) -> bool:
        """Check if Turnstile is already solved."""
        token = await self.get_token()
        return token is not None and len(token) > 10
