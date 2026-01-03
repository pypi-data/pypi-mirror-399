"""
Communication Bus Module

Event-driven message bus for inter-component communication in MDSA.
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages that can be sent through the bus."""
    QUERY = "query"
    RESPONSE = "response"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    STATE_CHANGE = "state_change"
    METRIC = "metric"
    ERROR = "error"
    LOG = "log"


@dataclass
class Message:
    """
    Message object for the communication bus.

    Attributes:
        id: Unique message identifier
        type: Message type
        channel: Channel name
        sender: Sender identifier
        payload: Message payload
        timestamp: Message creation time
        correlation_id: ID for tracking related messages
        metadata: Additional metadata
    """
    type: MessageType
    channel: str
    sender: str
    payload: Any
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"<Message id={self.id[:8]}... type={self.type.value} "
            f"channel={self.channel} sender={self.sender}>"
        )


class MessageBus:
    """
    Event-driven message bus with pub/sub pattern.

    Supports:
    - Subscribe to channels
    - Publish messages to channels
    - Message history
    - Message filtering
    - Async message delivery

    Example:
        >>> bus = MessageBus()
        >>> bus.subscribe("events", lambda msg: print(msg.payload))
        >>> bus.publish("events", "sender", {"data": "test"}, MessageType.LOG)
    """

    def __init__(self, max_history: int = 1000):
        """
        Initialize message bus.

        Args:
            max_history: Maximum number of messages to keep in history
        """
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_history: List[Message] = []
        self.max_history = max_history
        self._message_count = 0

        logger.debug("MessageBus initialized")

    def subscribe(self, channel: str, callback: Callable[[Message], None]) -> str:
        """
        Subscribe to a channel.

        Args:
            channel: Channel name
            callback: Function to call when message received (signature: callback(message))

        Returns:
            str: Subscription ID (for unsubscribing)

        Example:
            >>> def handler(msg):
            ...     print(f"Received: {msg.payload}")
            >>> sub_id = bus.subscribe("events", handler)
        """
        # Create subscription ID
        sub_id = f"{channel}_{id(callback)}"

        # Add subscriber
        self.subscribers[channel].append(callback)

        logger.debug(f"Subscribed to channel '{channel}' (sub_id: {sub_id})")
        return sub_id

    def unsubscribe(self, channel: str, callback: Callable):
        """
        Unsubscribe from a channel.

        Args:
            channel: Channel name
            callback: Callback function to remove
        """
        if channel in self.subscribers and callback in self.subscribers[channel]:
            self.subscribers[channel].remove(callback)
            logger.debug(f"Unsubscribed from channel '{channel}'")

    def publish(
        self,
        channel: str,
        sender: str,
        payload: Any,
        message_type: MessageType = MessageType.LOG,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Message:
        """
        Publish message to a channel.

        Args:
            channel: Channel name
            sender: Sender identifier
            payload: Message payload
            message_type: Type of message
            correlation_id: Optional correlation ID
            metadata: Optional metadata

        Returns:
            Message: Published message object

        Example:
            >>> msg = bus.publish("events", "orchestrator", {"status": "ok"})
        """
        # Create message
        message = Message(
            type=message_type,
            channel=channel,
            sender=sender,
            payload=payload,
            correlation_id=correlation_id,
            metadata=metadata or {}
        )

        # Add to history
        self._add_to_history(message)

        # Deliver to subscribers
        self._deliver_message(channel, message)

        self._message_count += 1
        logger.debug(f"Published message to '{channel}': {message.id[:8]}...")

        return message

    def _deliver_message(self, channel: str, message: Message):
        """
        Deliver message to all subscribers.

        Args:
            channel: Channel name
            message: Message to deliver
        """
        if channel not in self.subscribers:
            logger.debug(f"No subscribers for channel '{channel}'")
            return

        # Call all subscribers
        for callback in self.subscribers[channel]:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"Error in subscriber callback for '{channel}': {e}")

    def _add_to_history(self, message: Message):
        """
        Add message to history.

        Args:
            message: Message to add
        """
        self.message_history.append(message)

        # Trim history if too long
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]

    def get_history(
        self,
        channel: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        sender: Optional[str] = None,
        limit: int = 100
    ) -> List[Message]:
        """
        Get message history with optional filtering.

        Args:
            channel: Filter by channel
            message_type: Filter by message type
            sender: Filter by sender
            limit: Maximum number of messages to return

        Returns:
            list: List of messages

        Example:
            >>> recent = bus.get_history(channel="events", limit=10)
        """
        filtered = self.message_history

        if channel:
            filtered = [m for m in filtered if m.channel == channel]

        if message_type:
            filtered = [m for m in filtered if m.type == message_type]

        if sender:
            filtered = [m for m in filtered if m.sender == sender]

        # Return most recent up to limit
        return filtered[-limit:]

    def get_correlated_messages(self, correlation_id: str) -> List[Message]:
        """
        Get all messages with matching correlation ID.

        Args:
            correlation_id: Correlation ID to search for

        Returns:
            list: List of correlated messages

        Example:
            >>> correlated = bus.get_correlated_messages("req-123")
        """
        return [
            m for m in self.message_history
            if m.correlation_id == correlation_id
        ]

    def clear_history(self):
        """Clear message history."""
        self.message_history.clear()
        logger.info("Message history cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get message bus statistics.

        Returns:
            dict: Statistics (channels, subscribers, message_count, etc.)
        """
        return {
            'total_messages': self._message_count,
            'history_size': len(self.message_history),
            'channels': list(self.subscribers.keys()),
            'subscriber_counts': {
                ch: len(subs) for ch, subs in self.subscribers.items()
            },
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<MessageBus channels={len(self.subscribers)} "
            f"history={len(self.message_history)} "
            f"messages={self._message_count}>"
        )


if __name__ == "__main__":
    # Demo usage
    print("=== MessageBus Demo ===\n")

    bus = MessageBus()

    # Subscribe to channel
    def event_handler(msg: Message):
        print(f"[Handler] Received: {msg.payload} from {msg.sender}")

    bus.subscribe("events", event_handler)
    print("Subscribed to 'events' channel\n")

    # Publish messages
    print("--- Publishing Messages ---")
    bus.publish("events", "sender1", {"action": "started"}, MessageType.LOG)
    bus.publish("events", "sender2", {"action": "processing"}, MessageType.LOG)
    bus.publish("events", "sender1", {"action": "completed"}, MessageType.LOG)

    # Correlation
    print("\n--- Correlation Demo ---")
    corr_id = "request-123"
    bus.publish("events", "orchestrator", {"step": 1}, MessageType.QUERY, correlation_id=corr_id)
    bus.publish("events", "domain", {"step": 2}, MessageType.RESPONSE, correlation_id=corr_id)
    bus.publish("events", "validator", {"step": 3}, MessageType.LOG, correlation_id=corr_id)

    correlated = bus.get_correlated_messages(corr_id)
    print(f"Found {len(correlated)} correlated messages for '{corr_id}'")

    # History
    print("\n--- Message History ---")
    history = bus.get_history(limit=5)
    for msg in history:
        print(f"  {msg.timestamp:.2f} [{msg.type.value}] {msg.sender}: {msg.payload}")

    # Stats
    print("\n--- Statistics ---")
    stats = bus.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
