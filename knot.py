"""
Knot - API Management Layer
Manages API connections and secrets securely, linking Dedalus endpoints with Claude API
and external event sources. Frontend and AI agents don't need to hardcode URLs or API keys.
"""
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class Knot:
    """API connection and secrets management."""
    
    # Dedalus Events API configuration
    DEDALUS_BASE_URL = os.getenv("DEDALUS_BASE_URL", "http://localhost:8000")
    DEDALUS_API_KEY = os.getenv("DEDALUS_API_KEY", None)  # Optional for now
    
    # Claude API configuration
    CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY", os.getenv("CLAUDE_API_KEY", None))
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    
    # Eventbrite API configuration
    EVENTBRITE_API_KEY = os.getenv("EVENTBRITE_API_KEY", None)
    EVENTBRITE_BASE_URL = "https://www.eventbriteapi.com/v3"
    
    # External event sources (if any)
    EXTERNAL_EVENTS_API_KEY = os.getenv("EXTERNAL_EVENTS_API_KEY", None)
    EXTERNAL_EVENTS_BASE_URL = os.getenv("EXTERNAL_EVENTS_BASE_URL", None)
    
    @classmethod
    def get_dedalus_url(cls, endpoint: str = "") -> str:
        """Get full Dedalus API URL for an endpoint."""
        base = cls.DEDALUS_BASE_URL.rstrip('/')
        endpoint = endpoint.lstrip('/')
        return f"{base}/{endpoint}" if endpoint else base
    
    @classmethod
    def get_claude_config(cls) -> Dict:
        """Get Claude API configuration."""
        if not cls.CLAUDE_API_KEY:
            raise ValueError("Claude API key not found. Set ANTHROPIC_API_KEY or CLAUDE_API_KEY in environment.")
        
        return {
            "api_key": cls.CLAUDE_API_KEY,
            "model": cls.CLAUDE_MODEL
        }
    
    @classmethod
    def get_eventbrite_config(cls) -> Optional[Dict]:
        """Get Eventbrite API configuration if available."""
        if not cls.EVENTBRITE_API_KEY:
            return None
        
        return {
            "api_key": cls.EVENTBRITE_API_KEY,
            "base_url": cls.EVENTBRITE_BASE_URL
        }
    
    @classmethod
    def get_external_events_config(cls) -> Optional[Dict]:
        """Get external events API configuration if available."""
        if not cls.EXTERNAL_EVENTS_API_KEY or not cls.EXTERNAL_EVENTS_BASE_URL:
            return None
        
        return {
            "api_key": cls.EXTERNAL_EVENTS_API_KEY,
            "base_url": cls.EXTERNAL_EVENTS_BASE_URL
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate that required configurations are present."""
        return {
            "dedalus": bool(cls.DEDALUS_BASE_URL),
            "claude": bool(cls.CLAUDE_API_KEY),
            "external_events": bool(cls.EXTERNAL_EVENTS_API_KEY and cls.EXTERNAL_EVENTS_BASE_URL)
        }


