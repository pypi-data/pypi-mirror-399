"""
Stealth Injection for Py-Parkour.
Injects evasion scripts to avoid bot detection.
"""

from typing import Optional, List, Dict
from playwright.async_api import Page, BrowserContext

from .fingerprint import BrowserFingerprint


class StealthInjector:
    """
    Injects stealth scripts to evade bot detection.
    
    Covers common detection vectors:
    - navigator.webdriver
    - chrome.runtime
    - permissions API
    - plugins/mimeTypes
    - WebGL fingerprint
    - And more...
    """
    
    EVASION_WEBDRIVER = """
        // Remove webdriver flag
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });

        // Delete from prototype
        if (Object.getPrototypeOf(navigator).hasOwnProperty('webdriver')) {
            delete Object.getPrototypeOf(navigator).webdriver;
        }

        // Mock chrome driver strings
        window.cdc_adoQbhC0nS7alvltBdfm6X_Array = undefined;
        window.cdc_adoQbhC0nS7alvltBdfm6X_Promise = undefined;
        window.cdc_adoQbhC0nS7alvltBdfm6X_Symbol = undefined;
    """
    
    EVASION_CHROME_RUNTIME = """
        // Add chrome.runtime
        window.chrome = window.chrome || {};
        window.chrome.runtime = window.chrome.runtime || {};
        
        // Mock chrome.runtime.connect
        window.chrome.runtime.connect = function() {
            return { onMessage: { addListener: function() {} } };
        };
    """
    
    EVASION_PERMISSIONS = """
        // Fix permissions API
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """
    
    EVASION_PLUGINS = """
        // Mock plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => {
                const plugins = [
                    { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                    { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
                    { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' },
                ];
                plugins.length = 3;
                plugins.item = (index) => plugins[index];
                plugins.namedItem = (name) => plugins.find(p => p.name === name);
                plugins.refresh = () => {};
                return plugins;
            },
        });
    """
    
    EVASION_LANGUAGES = """
        // Ensure languages array
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
    """
    
    EVASION_HARDWARE_CONCURRENCY = """
        // Set realistic hardware concurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8,
        });
    """
    
    EVASION_DEVICE_MEMORY = """
        // Set realistic device memory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8,
        });
    """
    
    EVASION_IFRAME_CONTENT_WINDOW = """
        // Fix iframe detection
        try {
            const originalContentWindow = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow');
            Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                get: function() {
                    const iframe = originalContentWindow.get.call(this);
                    return iframe;
                }
            });
        } catch (e) {}
    """
    
    EVASION_CONSOLE_DEBUG = """
        // Prevent console.debug detection
        const originalDebug = console.debug;
        console.debug = function() {
            return originalDebug.apply(console, arguments);
        };
    """
    
    EVASION_BROKEN_IMAGE = """
        // Fix broken image dimensions used for detection
        ['height', 'width'].forEach(property => {
            const originalDescriptor = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, property);
            Object.defineProperty(HTMLImageElement.prototype, property, {
                ...originalDescriptor,
                get: function() {
                    if (this.complete && this.naturalHeight === 0) {
                        return 0;
                    }
                    return originalDescriptor.get.call(this);
                },
            });
        });
    """

    EVASION_SERVICE_WORKER = """
        // Mock ServiceWorker
        if (!('serviceWorker' in navigator)) {
            Object.defineProperty(navigator, 'serviceWorker', {
                get: () => ({
                    register: () => Promise.resolve({}),
                    getRegistration: () => Promise.resolve(null),
                    getRegistrations: () => Promise.resolve([]),
                    ready: new Promise(() => {}),
                    addEventListener: () => {},
                    removeEventListener: () => {},
                })
            });
        }
    """

    EVASION_WEBGL_EXTENSIONS = """
        // Add realistic WebGL extensions
        try {
            const getExtension = WebGLRenderingContext.prototype.getExtension;
            WebGLRenderingContext.prototype.getExtension = function(name) {
                if (name === 'WEBGL_debug_renderer_info') {
                    return {
                        UNMASKED_VENDOR_WEBGL: 0x9245,
                        UNMASKED_RENDERER_WEBGL: 0x9246,
                    };
                }
                return getExtension.apply(this, arguments);
            };
        } catch (e) {}
    """

    EVASION_INTL = """
        // Mock Intl properties
        try {
            const originalDateTimeFormat = Intl.DateTimeFormat;
            Intl.DateTimeFormat = function() {
                const formatter = new originalDateTimeFormat(...arguments);
                const originalResolvedOptions = formatter.resolvedOptions;
                formatter.resolvedOptions = function() {
                    const options = originalResolvedOptions.apply(this, arguments);
                    options.timeZone = 'UTC'; // Or match fingerprint
                    return options;
                };
                return formatter;
            };
        } catch (e) {}
    """

    # All evasions combined
    ALL_EVASIONS = [
        EVASION_WEBDRIVER,
        EVASION_CHROME_RUNTIME,
        EVASION_PERMISSIONS,
        EVASION_PLUGINS,
        EVASION_LANGUAGES,
        EVASION_HARDWARE_CONCURRENCY,
        EVASION_DEVICE_MEMORY,
        EVASION_IFRAME_CONTENT_WINDOW,
        EVASION_CONSOLE_DEBUG,
        EVASION_BROKEN_IMAGE,
        EVASION_SERVICE_WORKER,
        EVASION_WEBGL_EXTENSIONS,
        EVASION_INTL,
    ]
    
    @classmethod
    def get_all_scripts(cls) -> List[str]:
        """Get all evasion scripts as a list."""
        return cls.ALL_EVASIONS.copy()
    
    @classmethod
    def get_combined_script(cls) -> str:
        """Get all evasion scripts combined into one."""
        return "\n".join([
            "// Py-Parkour Stealth Evasions",
            "(function() {",
            "\n".join(cls.ALL_EVASIONS),
            "})();",
        ])
    
    @classmethod
    async def inject_all(cls, page: Page):
        """Inject all evasion scripts into a page."""
        script = cls.get_combined_script()
        await page.add_init_script(script)
    
    @classmethod
    async def inject_into_context(cls, context: BrowserContext):
        """
        Inject evasion scripts into a browser context.
        Scripts will be injected into all pages (existing and new).
        """
        script = cls.get_combined_script()
        await context.add_init_script(script)
    
    @classmethod
    def get_fingerprint_script(cls, fingerprint: BrowserFingerprint) -> str:
        """
        Generate a script to inject custom fingerprint values.
        
        Args:
            fingerprint: The fingerprint to inject
            
        Returns:
            JavaScript code to inject the fingerprint
        """
        return f"""
            // Py-Parkour Custom Fingerprint
            (function() {{
                // Platform
                Object.defineProperty(navigator, 'platform', {{
                    get: () => '{fingerprint.platform}',
                }});
                
                // Hardware
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {fingerprint.hardware_concurrency},
                }});
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: () => {fingerprint.device_memory},
                }});
                
                // Languages
                Object.defineProperty(navigator, 'languages', {{
                    get: () => {fingerprint.languages},
                }});
                Object.defineProperty(navigator, 'language', {{
                    get: () => '{fingerprint.languages[0] if fingerprint.languages else "en-US"}',
                }});
                
                // Screen
                Object.defineProperty(screen, 'width', {{
                    get: () => {fingerprint.screen_width},
                }});
                Object.defineProperty(screen, 'height', {{
                    get: () => {fingerprint.screen_height},
                }});
                Object.defineProperty(screen, 'colorDepth', {{
                    get: () => {fingerprint.color_depth},
                }});
                Object.defineProperty(window, 'devicePixelRatio', {{
                    get: () => {fingerprint.pixel_ratio},
                }});
                
                // WebGL
                const getParameterProxy = new Proxy(WebGLRenderingContext.prototype.getParameter, {{
                    apply: function(target, thisArg, args) {{
                        const param = args[0];
                        // UNMASKED_VENDOR_WEBGL
                        if (param === 37445) {{
                            return '{fingerprint.webgl_vendor}';
                        }}
                        // UNMASKED_RENDERER_WEBGL
                        if (param === 37446) {{
                            return '{fingerprint.webgl_renderer}';
                        }}
                        return Reflect.apply(target, thisArg, args);
                    }}
                }});
                WebGLRenderingContext.prototype.getParameter = getParameterProxy;
                
                // WebGL2
                try {{
                    const getParameter2Proxy = new Proxy(WebGL2RenderingContext.prototype.getParameter, {{
                        apply: function(target, thisArg, args) {{
                            const param = args[0];
                            if (param === 37445) {{
                                return '{fingerprint.webgl_vendor}';
                            }}
                            if (param === 37446) {{
                                return '{fingerprint.webgl_renderer}';
                            }}
                            return Reflect.apply(target, thisArg, args);
                        }}
                    }});
                    WebGL2RenderingContext.prototype.getParameter = getParameter2Proxy;
                }} catch (e) {{}}
            }})();
        """
    
    @classmethod
    async def inject_fingerprint(cls, page: Page, fingerprint: BrowserFingerprint):
        """Inject custom fingerprint values into a page."""
        script = cls.get_fingerprint_script(fingerprint)
        await page.add_init_script(script)
    
    @classmethod
    async def inject_full_stealth(cls, page: Page, fingerprint: Optional[BrowserFingerprint] = None):
        """
        Inject both evasion scripts and optional fingerprint.
        
        Args:
            page: Playwright page to inject into
            fingerprint: Optional custom fingerprint
        """
        await cls.inject_all(page)
        if fingerprint:
            await cls.inject_fingerprint(page, fingerprint)
