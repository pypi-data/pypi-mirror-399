"""Storage module

Provides comprehensive memory management features, including:
- Short-term memory for conversation events
- Long-term memory for persistent knowledge storage
- Token management tools
"""

# Short-term memory exports
# Long-term memory exports
from .long_term_memory import (
    BaseLongTermMemory,
    MemoryEntity,
    MemoryQuery,
    TDAILongTermMemory,
)
from .memory import (
    BaseMemory,
    IMemoryEvent,
    InMemoryMemory,
    ListOptions,
    Message,
    MessageRole,
    TDAIMemory,
)

__all__ = [
    # Short-term memory
    "BaseMemory",
    "IMemoryEvent",
    "ListOptions",
    "Message",
    "MessageRole",
    "InMemoryMemory",
    "TDAIMemory",
    # Long-term memory
    "BaseLongTermMemory",
    "MemoryEntity",
    "MemoryQuery",
    "TDAILongTermMemory",
]

# Declare this as a namespace package to allow other cloudbase_agent subpackages to coexist
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
