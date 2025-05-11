"""
Custom exceptions for the tinyagent_deepsearch library.
"""

class TinyAgentDeepSearchError(Exception):
    """Base exception class for tinyagent_deepsearch errors."""
    pass

class MissingAPIKeyError(TinyAgentDeepSearchError):
    """Raised when a required API key is not found in environment variables."""
    def __init__(self, key_name: str):
        self.key_name = key_name
        super().__init__(
            f"Required API key '{key_name}' not found in environment variables. "
            f"Please set the {key_name} environment variable."
        )

class ConfigurationError(TinyAgentDeepSearchError):
    """Raised for general configuration issues."""
    pass