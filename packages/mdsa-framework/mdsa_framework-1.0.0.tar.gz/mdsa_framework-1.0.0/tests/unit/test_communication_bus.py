"""
Unit tests for Communication Bus module.

Tests message publishing, subscriptions, and message history.
"""

import unittest
import time
from mdsa.core.communication_bus import MessageBus, Message, MessageType


class TestMessageType(unittest.TestCase):
    """Test suite for MessageType enum."""

    def test_message_types_exist(self):
        """Test all expected message types exist."""
        expected_types = [
            'QUERY', 'RESPONSE', 'TOOL_CALL', 'TOOL_RESULT',
            'STATE_CHANGE', 'METRIC', 'ERROR', 'LOG'
        ]

        for msg_type in expected_types:
            self.assertTrue(hasattr(MessageType, msg_type))


class TestMessage(unittest.TestCase):
    """Test suite for Message dataclass."""

    def test_message_creation(self):
        """Test creating a message."""
        msg = Message(
            type=MessageType.LOG,
            channel="test",
            sender="test_sender",
            payload={"key": "value"}
        )

        self.assertEqual(msg.type, MessageType.LOG)
        self.assertEqual(msg.channel, "test")
        self.assertEqual(msg.sender, "test_sender")
        self.assertEqual(msg.payload, {"key": "value"})
        self.assertIsNotNone(msg.id)
        self.assertIsInstance(msg.timestamp, float)

    def test_message_with_correlation_id(self):
        """Test message with correlation ID."""
        msg = Message(
            type=MessageType.QUERY,
            channel="test",
            sender="sender",
            payload={},
            correlation_id="req-123"
        )

        self.assertEqual(msg.correlation_id, "req-123")

    def test_message_with_metadata(self):
        """Test message with metadata."""
        metadata = {"extra": "data"}
        msg = Message(
            type=MessageType.RESPONSE,
            channel="test",
            sender="sender",
            payload={},
            metadata=metadata
        )

        self.assertEqual(msg.metadata, metadata)

    def test_message_id_unique(self):
        """Test each message has unique ID."""
        msg1 = Message(type=MessageType.LOG, channel="test", sender="s", payload={})
        msg2 = Message(type=MessageType.LOG, channel="test", sender="s", payload={})

        self.assertNotEqual(msg1.id, msg2.id)

    def test_message_repr(self):
        """Test message string representation."""
        msg = Message(
            type=MessageType.LOG,
            channel="events",
            sender="orchestrator",
            payload={}
        )

        repr_str = repr(msg)
        self.assertIn("Message", repr_str)
        self.assertIn("log", repr_str)
        self.assertIn("events", repr_str)


class TestMessageBus(unittest.TestCase):
    """Test suite for MessageBus class."""

    def setUp(self):
        """Set up test fixtures."""
        self.bus = MessageBus()

    def test_initialization(self):
        """Test MessageBus initialization."""
        self.assertIsNotNone(self.bus)
        self.assertEqual(len(self.bus.message_history), 0)

    def test_subscribe_to_channel(self):
        """Test subscribing to a channel."""
        callback_called = []

        def handler(msg):
            callback_called.append(msg)

        sub_id = self.bus.subscribe("events", handler)
        self.assertIsNotNone(sub_id)
        self.assertIn("events", sub_id)

    def test_publish_message(self):
        """Test publishing a message."""
        msg = self.bus.publish(
            "events",
            "test_sender",
            {"action": "test"},
            MessageType.LOG
        )

        self.assertIsInstance(msg, Message)
        self.assertEqual(msg.channel, "events")
        self.assertEqual(msg.sender, "test_sender")
        self.assertEqual(msg.payload, {"action": "test"})

    def test_message_delivery_to_subscriber(self):
        """Test message is delivered to subscribers."""
        received_messages = []

        def handler(msg):
            received_messages.append(msg)

        self.bus.subscribe("events", handler)
        self.bus.publish("events", "sender", {"data": "test"}, MessageType.LOG)

        self.assertEqual(len(received_messages), 1)
        self.assertEqual(received_messages[0].payload, {"data": "test"})

    def test_multiple_subscribers(self):
        """Test multiple subscribers receive messages."""
        received1 = []
        received2 = []

        def handler1(msg):
            received1.append(msg)

        def handler2(msg):
            received2.append(msg)

        self.bus.subscribe("events", handler1)
        self.bus.subscribe("events", handler2)
        self.bus.publish("events", "sender", {"data": "test"}, MessageType.LOG)

        self.assertEqual(len(received1), 1)
        self.assertEqual(len(received2), 1)

    def test_channel_isolation(self):
        """Test messages on different channels are isolated."""
        received_events = []
        received_metrics = []

        def events_handler(msg):
            received_events.append(msg)

        def metrics_handler(msg):
            received_metrics.append(msg)

        self.bus.subscribe("events", events_handler)
        self.bus.subscribe("metrics", metrics_handler)

        self.bus.publish("events", "s", {}, MessageType.LOG)
        self.bus.publish("metrics", "s", {}, MessageType.METRIC)

        self.assertEqual(len(received_events), 1)
        self.assertEqual(len(received_metrics), 1)

    def test_unsubscribe(self):
        """Test unsubscribing from channel."""
        received = []

        def handler(msg):
            received.append(msg)

        self.bus.subscribe("events", handler)
        self.bus.publish("events", "s", {}, MessageType.LOG)
        self.assertEqual(len(received), 1)

        self.bus.unsubscribe("events", handler)
        self.bus.publish("events", "s", {}, MessageType.LOG)
        self.assertEqual(len(received), 1)  # Still 1, not 2

    def test_message_history(self):
        """Test message history tracking."""
        self.bus.publish("events", "s1", {"msg": 1}, MessageType.LOG)
        self.bus.publish("events", "s2", {"msg": 2}, MessageType.LOG)

        history = self.bus.get_history()
        self.assertEqual(len(history), 2)

    def test_history_limit(self):
        """Test history respects max_history limit."""
        bus = MessageBus(max_history=5)

        for i in range(10):
            bus.publish("events", "s", {"msg": i}, MessageType.LOG)

        history = bus.get_history()
        self.assertEqual(len(history), 5)

    def test_filter_history_by_channel(self):
        """Test filtering history by channel."""
        self.bus.publish("events", "s", {}, MessageType.LOG)
        self.bus.publish("metrics", "s", {}, MessageType.METRIC)
        self.bus.publish("events", "s", {}, MessageType.LOG)

        events_history = self.bus.get_history(channel="events")
        self.assertEqual(len(events_history), 2)

    def test_filter_history_by_message_type(self):
        """Test filtering history by message type."""
        self.bus.publish("events", "s", {}, MessageType.LOG)
        self.bus.publish("events", "s", {}, MessageType.ERROR)
        self.bus.publish("events", "s", {}, MessageType.LOG)

        error_history = self.bus.get_history(message_type=MessageType.ERROR)
        self.assertEqual(len(error_history), 1)

    def test_filter_history_by_sender(self):
        """Test filtering history by sender."""
        self.bus.publish("events", "sender1", {}, MessageType.LOG)
        self.bus.publish("events", "sender2", {}, MessageType.LOG)
        self.bus.publish("events", "sender1", {}, MessageType.LOG)

        sender1_history = self.bus.get_history(sender="sender1")
        self.assertEqual(len(sender1_history), 2)

    def test_history_limit_parameter(self):
        """Test history limit parameter."""
        for i in range(20):
            self.bus.publish("events", "s", {"i": i}, MessageType.LOG)

        recent = self.bus.get_history(limit=5)
        self.assertEqual(len(recent), 5)

    def test_correlated_messages(self):
        """Test getting correlated messages."""
        corr_id = "req-123"

        self.bus.publish("events", "s1", {}, MessageType.QUERY, correlation_id=corr_id)
        self.bus.publish("events", "s2", {}, MessageType.LOG)
        self.bus.publish("events", "s3", {}, MessageType.RESPONSE, correlation_id=corr_id)

        correlated = self.bus.get_correlated_messages(corr_id)
        self.assertEqual(len(correlated), 2)

    def test_clear_history(self):
        """Test clearing message history."""
        self.bus.publish("events", "s", {}, MessageType.LOG)
        self.bus.publish("events", "s", {}, MessageType.LOG)

        self.bus.clear_history()
        history = self.bus.get_history()
        self.assertEqual(len(history), 0)

    def test_get_stats(self):
        """Test getting message bus statistics."""
        self.bus.subscribe("events", lambda msg: None)
        self.bus.subscribe("metrics", lambda msg: None)
        self.bus.publish("events", "s", {}, MessageType.LOG)

        stats = self.bus.get_stats()
        self.assertEqual(stats['total_messages'], 1)
        self.assertEqual(len(stats['channels']), 2)
        self.assertIn('events', stats['channels'])

    def test_subscriber_error_handling(self):
        """Test errors in subscriber callbacks don't break bus."""
        received_by_good = []

        def bad_handler(msg):
            raise ValueError("Handler error")

        def good_handler(msg):
            received_by_good.append(msg)

        self.bus.subscribe("events", bad_handler)
        self.bus.subscribe("events", good_handler)

        # Should not raise, good handler should still receive
        self.bus.publish("events", "s", {}, MessageType.LOG)
        self.assertEqual(len(received_by_good), 1)

    def test_publish_with_metadata(self):
        """Test publishing message with metadata."""
        metadata = {"request_id": "123", "user": "test"}
        msg = self.bus.publish(
            "events",
            "sender",
            {},
            MessageType.LOG,
            metadata=metadata
        )

        self.assertEqual(msg.metadata, metadata)

    def test_repr(self):
        """Test string representation."""
        repr_str = repr(self.bus)
        self.assertIn("MessageBus", repr_str)


class TestMessageBusEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_publish_to_channel_with_no_subscribers(self):
        """Test publishing to channel with no subscribers."""
        bus = MessageBus()
        # Should not raise
        msg = bus.publish("empty", "s", {}, MessageType.LOG)
        self.assertIsNotNone(msg)

    def test_unsubscribe_nonexistent_callback(self):
        """Test unsubscribing non-existent callback."""
        bus = MessageBus()

        def handler(msg):
            pass

        # Should not raise
        bus.unsubscribe("events", handler)

    def test_multiple_channels_same_callback(self):
        """Test same callback on multiple channels."""
        bus = MessageBus()
        received = []

        def handler(msg):
            received.append(msg)

        bus.subscribe("events", handler)
        bus.subscribe("metrics", handler)

        bus.publish("events", "s", {}, MessageType.LOG)
        bus.publish("metrics", "s", {}, MessageType.METRIC)

        self.assertEqual(len(received), 2)


if __name__ == '__main__':
    unittest.main()
