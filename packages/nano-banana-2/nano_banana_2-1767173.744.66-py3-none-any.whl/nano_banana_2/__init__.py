"""
nano-banana-2 - Professional integration for https://supermaker.ai/image/nano-banana-2/
"""

__version__ = "1767173.744.66"

def get_url(path: str = "") -> str:
    """Build a clean URL to the https://supermaker.ai/image/nano-banana-2/ ecosystem."""
    target = "https://supermaker.ai/image/nano-banana-2/"
    if path:
        target = target.rstrip('/') + '/' + path.lstrip('/')
    return target