"""
Sentrial Python SDK

Performance monitoring for AI agents. Track success rates, costs, and KPIs.
"""

from .client import SentrialClient
from .types import EventType

__version__ = "0.2.0"
__all__ = ["SentrialClient", "EventType"]

# Optional LangChain integration (only available if langchain is installed)
try:
    from .langchain import SentrialCallbackHandler
    __all__.extend(["SentrialCallbackHandler"])
except ImportError:
    # LangChain not installed, skip
    pass
