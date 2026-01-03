"""
Shadow Gadget - Enhanced Session Transfer for Py-Parkour.
"Breaks in with the Browser, Steals the Soul for the API."

Features:
- Transfer browser session to aiohttp/requests
- Export cookies, localStorage, sessionStorage
- Direct cloudscraper integration
- Session state serialization
"""

from typing import Optional, Dict, Any, List
from playwright.async_api import Page
import aiohttp
import asyncio
import json


class Shadow:
    """
    The Shadow Gadget: Session Transfer.
    
    Enables seamless handoff from browser to HTTP client:
    1. Login/authenticate using browser
    2. Export session state
    3. Continue with fast HTTP requests
    
    Usage:
        # After browser authentication
        session_data = await bot.shadow.export_session()
        
        # Use with requests
        import requests
        s = requests.Session()
        for name, value in session_data['cookies'].items():
            s.cookies.set(name, value)
        
        # Or create aiohttp session directly
        async with await bot.shadow.create_session() as session:
            response = await session.get(url)
    """
    
    def __init__(self, page: Page):
        self.page = page
    
    async def get_cookies(self) -> Dict[str, str]:
        """
        Get all cookies from the current browser context.
        
        Returns:
            Dictionary of cookie name -> value
        """
        if not self.page:
            raise RuntimeError("Shadow needs a running browser page.")
        
        cookies = await self.page.context.cookies()
        return {cookie['name']: cookie['value'] for cookie in cookies}
    
    async def get_cookies_detailed(self) -> List[Dict[str, Any]]:
        """
        Get all cookies with full details (domain, path, expires, etc.)
        
        Returns:
            List of cookie dictionaries with all attributes
        """
        if not self.page:
            raise RuntimeError("Shadow needs a running browser page.")
        
        return await self.page.context.cookies()
    
    async def get_local_storage(self) -> Dict[str, str]:
        """
        Get all localStorage items from the current page.
        
        Returns:
            Dictionary of localStorage key -> value
        """
        if not self.page:
            raise RuntimeError("Shadow needs a running browser page.")
        
        try:
            storage = await self.page.evaluate("""
                () => {
                    const items = {};
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        items[key] = localStorage.getItem(key);
                    }
                    return items;
                }
            """)
            return storage or {}
        except Exception:
            return {}
    
    async def get_session_storage(self) -> Dict[str, str]:
        """
        Get all sessionStorage items from the current page.
        
        Returns:
            Dictionary of sessionStorage key -> value
        """
        if not self.page:
            raise RuntimeError("Shadow needs a running browser page.")
        
        try:
            storage = await self.page.evaluate("""
                () => {
                    const items = {};
                    for (let i = 0; i < sessionStorage.length; i++) {
                        const key = sessionStorage.key(i);
                        items[key] = sessionStorage.getItem(key);
                    }
                    return items;
                }
            """)
            return storage or {}
        except Exception:
            return {}
    
    async def get_user_agent(self) -> str:
        """Get the browser's User-Agent."""
        if not self.page:
            raise RuntimeError("Shadow needs a running browser page.")
        
        return await self.page.evaluate("navigator.userAgent")
    
    async def export_session(self) -> Dict[str, Any]:
        """
        Export full session state for cloudscraper/requests integration.
        
        Returns:
            Dictionary containing:
            - cookies: Dict of cookie name -> value
            - cookies_detailed: List of full cookie objects
            - user_agent: Browser User-Agent string
            - local_storage: Dict of localStorage items
            - session_storage: Dict of sessionStorage items
            - headers: Recommended headers for requests
            - url: Current page URL
        """
        if not self.page:
            raise RuntimeError("Shadow needs a running browser page.")
        
        # Gather all session data
        cookies = await self.get_cookies()
        cookies_detailed = await self.get_cookies_detailed()
        user_agent = await self.get_user_agent()
        local_storage = await self.get_local_storage()
        session_storage = await self.get_session_storage()
        
        # Build recommended headers
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
        
        return {
            "cookies": cookies,
            "cookies_detailed": cookies_detailed,
            "user_agent": user_agent,
            "local_storage": local_storage,
            "session_storage": session_storage,
            "headers": headers,
            "url": self.page.url,
        }
    
    async def create_session(self, include_all_headers: bool = True) -> aiohttp.ClientSession:
        """
        Create an aiohttp ClientSession with session state transferred.
        
        Args:
            include_all_headers: Include full browser headers (recommended)
            
        Returns:
            aiohttp.ClientSession ready for use
        """
        if not self.page:
            raise RuntimeError("Shadow needs a running browser page.")
        
        session_data = await self.export_session()
        
        headers = session_data["headers"] if include_all_headers else {
            "User-Agent": session_data["user_agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        session = aiohttp.ClientSession(
            headers=headers,
            cookies=session_data["cookies"]
        )
        
        return session
    
    async def to_requests_session(self):
        """
        Create configuration for a requests.Session.
        
        Returns:
            Dictionary with cookies and headers for requests
            
        Usage:
            config = await bot.shadow.to_requests_session()
            import requests
            s = requests.Session()
            s.headers.update(config['headers'])
            for name, value in config['cookies'].items():
                s.cookies.set(name, value)
        """
        session_data = await self.export_session()
        return {
            "cookies": session_data["cookies"],
            "headers": session_data["headers"],
        }
    
    async def import_to_cloudscraper(self, scraper) -> None:
        """
        Import session state directly into a cloudscraper session.
        
        Args:
            scraper: A cloudscraper session object
            
        Usage:
            import cloudscraper
            scraper = cloudscraper.create_scraper()
            await bot.shadow.import_to_cloudscraper(scraper)
            # scraper now has browser cookies and headers
        """
        session_data = await self.export_session()
        
        # Update headers
        scraper.headers.update(session_data["headers"])
        
        # Add cookies
        for cookie in session_data["cookies_detailed"]:
            scraper.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain", ""),
                path=cookie.get("path", "/"),
            )
    
    async def save_session(self, filepath: str) -> None:
        """
        Save session state to a JSON file.
        
        Args:
            filepath: Path to save session file
        """
        session_data = await self.export_session()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"Shadow: Session saved to {filepath}")
    
    @staticmethod
    def load_session(filepath: str) -> Dict[str, Any]:
        """
        Load session state from a JSON file.
        
        Args:
            filepath: Path to session file
            
        Returns:
            Session data dictionary
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def inject_cookies(self, cookies: Dict[str, str], domain: str = None) -> None:
        """
        Inject cookies into the browser context.
        
        Args:
            cookies: Dictionary of cookie name -> value
            domain: Cookie domain (defaults to current page domain)
        """
        if not self.page:
            raise RuntimeError("Shadow needs a running browser page.")
        
        if not domain:
            from urllib.parse import urlparse
            domain = urlparse(self.page.url).netloc
        
        cookie_list = [
            {"name": name, "value": value, "domain": domain, "path": "/"}
            for name, value in cookies.items()
        ]
        
        await self.page.context.add_cookies(cookie_list)
    
    async def inject_local_storage(self, items: Dict[str, str]) -> None:
        """
        Inject items into localStorage.
        
        Args:
            items: Dictionary of key -> value to set
        """
        if not self.page:
            raise RuntimeError("Shadow needs a running browser page.")
        
        for key, value in items.items():
            await self.page.evaluate(f"localStorage.setItem('{key}', '{value}')")
    
    async def inject_session_storage(self, items: Dict[str, str]) -> None:
        """
        Inject items into sessionStorage.
        
        Args:
            items: Dictionary of key -> value to set
        """
        if not self.page:
            raise RuntimeError("Shadow needs a running browser page.")
        
        for key, value in items.items():
            await self.page.evaluate(f"sessionStorage.setItem('{key}', '{value}')")
    
    async def clear_session(self) -> None:
        """Clear all cookies, localStorage, and sessionStorage."""
        if not self.page:
            raise RuntimeError("Shadow needs a running browser page.")
        
        await self.page.context.clear_cookies()
        await self.page.evaluate("localStorage.clear()")
        await self.page.evaluate("sessionStorage.clear()")
        
        print("Shadow: Session cleared")

