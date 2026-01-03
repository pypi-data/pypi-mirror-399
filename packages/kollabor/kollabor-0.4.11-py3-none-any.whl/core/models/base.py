"""Shared data models for Kollabor CLI."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class ConversationMessage:
    """A single message in the conversation.
    
    Attributes:
        role: Role of the message sender (user, assistant, system, tool).
        content: The message content.
        timestamp: When the message was created.
        metadata: Additional metadata.
        thinking: Optional thinking process information.
    """
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    thinking: Optional[str] = None