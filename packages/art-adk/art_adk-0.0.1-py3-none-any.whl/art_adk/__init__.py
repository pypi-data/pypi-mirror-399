"""
ART ADK - Python SDK for ART WebSocket platform

Provides both synchronous and asynchronous interfaces for real-time communication.

Basic Usage:
    Synchronous:
        from art_adk import Adk
        
        with Adk(config) as client:
            client.connect()
            sub = client.subscribe("channel")
            sub.push("event", {"data": "test"})
    
    Asynchronous:
        from art_adk import AsyncAdk
        import asyncio
        
        async def main():
            client = AsyncAdk(config)
            await client.connect()
            sub = await client.subscribe("channel")
            await sub.push("event", {"data": "test"})
        
        asyncio.run(main())
"""
import logging

def enable_sdk_logging(level=logging.INFO):
    """
    Enable logging for the SDK.
    
    Args:
        level: Logging level (logging.DEBUG, logging.INFO, logging.WARNING, etc.)
        
    Example:
        >>> import your_sdk_name
        >>> your_sdk_name.enable_sdk_logging(logging.DEBUG)
    """
    sdk_logger = logging.getLogger(__name__.split('.')[0])
    sdk_logger.setLevel(level)
    
    # Add console handler if none exists
    if not sdk_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        sdk_logger.addHandler(handler)
        sdk_logger.propagate = False
        
        
# Version information
__version__ = "0.0.1"
from .async_adk import AsyncAdk
from .sync_adk import Adk
from .sync_wrapper import SyncWrapper
from .exceptions import EncryptionError, AuthenticationError, ChannelError, NotConnectedError, ValidationError, APIError
from .cryptobox import CryptoBox

# Define public API
__all__ = [
    "Adk",          
    "AsyncAdk",          
    "CryptoBox",         
    "EncryptionError",   
    "AuthenticationError", 
    "ChannelError",       
    "NotConnectedError",  
    "ValidationError",   
    "APIError",           
    "__version__",
    "enable_sdk_logging",
]


__author__ = "Aiotrix"
__license__ = "MIT"
__description__ = "Python SDK for ART WebSocket platform with sync/async support"