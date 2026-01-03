class EncryptionError(Exception):
    """Custom exception for encryption errors."""
    pass


class DecryptionError(Exception):
    """Custom exception for decryption errors."""
    pass


class AuthenticationError(Exception):
    """Authentication or authorization failed."""
    pass


class ChannelError(Exception):
    """Channel subscription or operation failed."""
    pass


class NotConnectedError(RuntimeError):
    """Operation requires an active connection."""
    pass


class ValidationError(Exception):
    """Data validation failed (config, KeyPair, JWT, etc.)."""
    pass


class APIError(Exception):
    """Server API request failed."""
    pass