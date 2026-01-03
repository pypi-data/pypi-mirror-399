"""
GhostCursor - Enhanced Human-Like Mouse Movement for Py-Parkour.
Simulates realistic mouse movements with Bezier curves, overshoot correction,
variable speed, and idle micro-movements.
"""

import asyncio
import random
import math
from typing import Optional, Tuple, List
from playwright.async_api import Page


class GhostCursor:
    """
    Simulates human-like mouse movements using Bezier curves.
    
    Features:
    - Position tracking across movements
    - Overshoot and correction (like real humans)
    - Variable speed (faster in middle, slower near target)
    - Idle micro-movements (subtle jitter while "thinking")
    - Natural hesitation before actions
    
    Anti-detection benefits:
    - Avoids instant cursor teleportation
    - Creates realistic movement patterns
    - Varies timing and path on each movement
    """
    
    def __init__(self, page: Page):
        self.page = page
        
        # Track current position
        self.current_x: float = 0.0
        self.current_y: float = 0.0
        self._position_initialized: bool = False
        
        # Movement configuration
        self.default_steps: int = 25
        self.overshoot_probability: float = 0.3  # 30% chance to overshoot
        self.overshoot_amount: float = 0.15  # Overshoot by 15% of distance
    
    async def _initialize_position(self):
        """Initialize cursor position to a random starting point."""
        if not self._position_initialized:
            viewport = self.page.viewport_size or {"width": 1920, "height": 1080}
            # Start from a random position (simulates user already on page)
            self.current_x = random.uniform(100, viewport["width"] - 100)
            self.current_y = random.uniform(100, viewport["height"] - 100)
            await self.page.mouse.move(self.current_x, self.current_y)
            self._position_initialized = True
    
    def _calculate_bezier_point(
        self, 
        t: float, 
        p0: Tuple[float, float], 
        p1: Tuple[float, float], 
        p2: Tuple[float, float], 
        p3: Tuple[float, float]
    ) -> Tuple[float, float]:
        """Calculate a point on a cubic Bezier curve."""
        # B(t) = (1-t)^3 * P0 + 3(1-t)^2 * t * P1 + 3(1-t) * t^2 * P2 + t^3 * P3
        px = ((1-t)**3 * p0[0]) + (3 * (1-t)**2 * t * p1[0]) + (3 * (1-t) * t**2 * p2[0]) + (t**3 * p3[0])
        py = ((1-t)**3 * p0[1]) + (3 * (1-t)**2 * t * p1[1]) + (3 * (1-t) * t**2 * p2[1]) + (t**3 * p3[1])
        return (px, py)
    
    def _generate_control_points(
        self, 
        start: Tuple[float, float], 
        end: Tuple[float, float]
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Generate random control points for natural curve."""
        distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        
        # Scale deviation based on distance
        deviation = min(distance * 0.3, 150)
        
        # Control point 1 (closer to start)
        cp1_x = start[0] + (random.uniform(0.2, 0.4) * (end[0] - start[0])) + random.uniform(-deviation, deviation)
        cp1_y = start[1] + (random.uniform(0.2, 0.4) * (end[1] - start[1])) + random.uniform(-deviation, deviation)
        
        # Control point 2 (closer to end)
        cp2_x = start[0] + (random.uniform(0.6, 0.8) * (end[0] - start[0])) + random.uniform(-deviation, deviation)
        cp2_y = start[1] + (random.uniform(0.6, 0.8) * (end[1] - start[1])) + random.uniform(-deviation, deviation)
        
        return ((cp1_x, cp1_y), (cp2_x, cp2_y))
    
    def _calculate_variable_delay(self, t: float) -> float:
        """
        Calculate delay for each step with variable speed.
        Slower at start and end, faster in the middle (like real mouse movement).
        """
        # Use a sine curve for natural acceleration/deceleration
        # sin(π*t) is 0 at t=0 and t=1, peaks at t=0.5
        speed_factor = 0.5 + 0.5 * math.sin(math.pi * t)
        
        # Base delay range
        min_delay = 0.003
        max_delay = 0.025
        
        # Invert speed factor for delay (faster = less delay)
        delay = min_delay + (max_delay - min_delay) * (1 - speed_factor)
        
        # Add some randomness
        return delay * random.uniform(0.8, 1.2)
    
    async def _execute_movement(self, path: List[Tuple[float, float]], variable_speed: bool = True):
        """Execute the movement along the path."""
        # The number of steps is len(path) - 1 if path includes start and end points
        # and represents 'steps' segments.
        total_steps = len(path) - 1 
        
        for i, point_tuple in enumerate(path):
            current_x, current_y = point_tuple
            
            # Add micro-jitter during movement
            if random.random() < 0.1: # 10% chance to add jitter
                current_x += random.uniform(-1, 1)
                current_y += random.uniform(-1, 1)
            
            await self.page.mouse.move(current_x, current_y)
            self.current_x, self.current_y = current_x, current_y
            
            # Variable speed: slower at the beginning and end
            if variable_speed and total_steps > 0:
                progress = i / total_steps # progress from 0 to 1
                if progress < 0.2 or progress > 0.8:
                    delay = random.uniform(0.01, 0.03) # Slower at ends
                else:
                    delay = random.uniform(0.005, 0.015) # Faster in middle
                await asyncio.sleep(delay)
            else:
                await asyncio.sleep(random.uniform(0.005, 0.02)) # Default delay if not variable speed
    
    async def move_to(
        self, 
        selector: str = None, 
        x: float = None, 
        y: float = None, 
        steps: int = None,
        overshoot: bool = None,
        variable_speed: bool = True
    ):
        """
        Move the mouse to a target element or coordinate using human-like path.
        
        Args:
            selector: CSS selector of target element
            x: Target X coordinate (used if no selector)
            y: Target Y coordinate (used if no selector)
            steps: Number of movement steps (default: 25)
            overshoot: Whether to overshoot and correct (None = random)
            variable_speed: Use variable speed (slower at ends)
        """
        await self._initialize_position()
        
        steps = steps or self.default_steps
        target_x = x
        target_y = y
        
        # Get target from selector
        if selector:
            try:
                box = await self.page.locator(selector).first.bounding_box()
                if box:
                    # Target center with small random offset
                    target_x = box['x'] + (box['width'] / 2) + random.uniform(-3, 3)
                    target_y = box['y'] + (box['height'] / 2) + random.uniform(-3, 3)
            except Exception:
                return
        
        if target_x is None or target_y is None:
            return
        
        start = (self.current_x, self.current_y)
        end = (target_x, target_y)
        
        # Determine if we should overshoot
        should_overshoot = overshoot if overshoot is not None else (random.random() < self.overshoot_probability)
        
        if should_overshoot:
            # Calculate overshoot point
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            overshoot_end = (
                end[0] + dx * self.overshoot_amount * random.uniform(0.8, 1.2),
                end[1] + dy * self.overshoot_amount * random.uniform(0.8, 1.2)
            )
            
            # Move to overshoot point first
            cp1, cp2 = self._generate_control_points(start, overshoot_end)
            path = [self._calculate_bezier_point(i / steps, start, cp1, cp2, overshoot_end) for i in range(steps + 1)]
            await self._execute_movement(path, variable_speed)
            
            # Small pause (simulating recognition of overshoot)
            await asyncio.sleep(random.uniform(0.05, 0.15))
            
            # Correct to actual target
            correction_steps = max(5, steps // 4)
            cp1, cp2 = self._generate_control_points((self.current_x, self.current_y), end)
            path = [self._calculate_bezier_point(i / correction_steps, (self.current_x, self.current_y), cp1, cp2, end) for i in range(correction_steps + 1)]
            await self._execute_movement(path, variable_speed)
        else:
            # Direct movement
            cp1, cp2 = self._generate_control_points(start, end)
            path = [self._calculate_bezier_point(i / steps, start, cp1, cp2, end) for i in range(steps + 1)]
            await self._execute_movement(path, variable_speed)
    
    async def click(self, selector: str, hesitate: bool = True):
        """
        Move to element and click it naturally.
        
        Args:
            selector: CSS selector of element to click
            hesitate: Whether to pause briefly before clicking
        """
        await self.move_to(selector)
        
        if hesitate:
            # Small hesitation before clicking (human reaction time)
            await asyncio.sleep(random.uniform(0.1, 0.3))
        
        await self.page.click(selector)
    
    async def double_click(self, selector: str):
        """Move to element and double-click it naturally."""
        await self.move_to(selector)
        await asyncio.sleep(random.uniform(0.05, 0.15))
        await self.page.dblclick(selector)
    
    async def right_click(self, selector: str):
        """Move to element and right-click it naturally."""
        await self.move_to(selector)
        await asyncio.sleep(random.uniform(0.1, 0.25))
        await self.page.click(selector, button="right")
    
    async def idle_movement(self, duration: float = 1.0, intensity: float = 1.0):
        """
        Subtle micro-movements simulating an idle user.
        
        Args:
            duration: How long to idle (seconds)
            intensity: Movement intensity (0.5 = subtle, 2.0 = more noticeable)
        """
        await self._initialize_position()
        
        end_time = asyncio.get_event_loop().time() + duration
        
        while asyncio.get_event_loop().time() < end_time:
            # Small random movement
            dx = random.uniform(-5, 5) * intensity
            dy = random.uniform(-5, 5) * intensity
            
            new_x = self.current_x + dx
            new_y = self.current_y + dy
            
            await self.page.mouse.move(new_x, new_y)
            self.current_x, self.current_y = new_x, new_y
            
            # Variable wait between micro-movements
            await asyncio.sleep(random.uniform(0.1, 0.4))
    
    async def scroll_to(self, selector: str):
        """Move to element area and scroll it into view."""
        await self._initialize_position()
        
        try:
            element = self.page.locator(selector).first
            box = await element.bounding_box()
            
            if box:
                # Move near the element first
                await self.move_to(x=box['x'] + random.uniform(0, box['width']),
                                   y=box['y'] + random.uniform(-50, 50))
                
                # Scroll to make element visible
                await element.scroll_into_view_if_needed()
                await asyncio.sleep(random.uniform(0.2, 0.5))
        except Exception:
            pass
    
    async def hover(self, selector: str, duration: float = 0.5):
        """
        Move to element and hover for a duration.
        
        Args:
            selector: CSS selector of element to hover
            duration: How long to hover (seconds)
        """
        await self.move_to(selector)
        await self.idle_movement(duration=duration, intensity=0.3)
    
    def reset_position(self):
        """Reset tracked position (call if page navigates)."""
        self._position_initialized = False
        self.current_x = 0.0
        self.current_y = 0.0
