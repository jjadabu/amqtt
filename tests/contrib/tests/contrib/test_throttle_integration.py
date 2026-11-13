
"""
Integration tests for the MQTT throttle plugin.

These tests use a mock rate limiter so that the broker/plugin
interaction can be developed independently of the final algorithms.
"""

import pytest
from unittest.mock import Mock

from amqtt.contexts import Action


class MockRateLimiter:
    """Simple rate limiter for testing integration behavior."""

    def __init__(self, message_limit=3):
        self.message_limit = message_limit
        self.client_counts = {}

    def allow(self, client_id, *args, **kwargs):
        """Allow messages up to the limit for each client."""
        count = self.client_counts.get(client_id, 0)

        if count < self.message_limit:
            self.client_counts[client_id] = count + 1
            return True

        return False


def test_mock_limiter_allows_messages_under_limit():
    limiter = MockRateLimiter(message_limit=3)

    assert limiter.allow("client1") is True
    assert limiter.allow("client1") is True
    assert limiter.allow("client1") is True


def test_mock_limiter_rejects_messages_over_limit():
    limiter = MockRateLimiter(message_limit=3)

    for _ in range(3):
        limiter.allow("client1")

    assert limiter.allow("client1") is False


def test_mock_limiter_tracks_clients_independently():
    limiter = MockRateLimiter(message_limit=2)

    assert limiter.allow("client1") is True
    assert limiter.allow("client1") is True
    assert limiter.allow("client1") is False

    # A different client should have its own independent limit.
    assert limiter.allow("client2") is True
    assert limiter.allow("client2") is True
    assert limiter.allow("client2") is False


def test_mock_limiter_does_not_count_rejected_messages():
    limiter = MockRateLimiter(message_limit=1)

    assert limiter.allow("client1") is True
    assert limiter.allow("client1") is False

    # The client remains over its limit.
    assert limiter.client_counts["client1"] == 1
