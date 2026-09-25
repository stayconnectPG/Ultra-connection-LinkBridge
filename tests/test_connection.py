"""Tests for the connection manager and message envelope."""

import json
from datetime import datetime

import pytest

from debian.connection.manager import (
    ConnectionManager,
    ConnectionState,
    Message,
    MessageType,
)


@pytest.fixture
def sample_message() -> Message:
    return Message(
        type=MessageType.COMMAND,
        payload={"action": "ping", "value": 42},
    )


def test_message_serialization(sample_message: Message) -> None:
    data = sample_message.model_dump()
    assert data["type"] == "command"
    assert data["payload"]["action"] == "ping"


def test_message_round_trip(sample_message: Message) -> None:
    data = sample_message.model_dump()
    restored = Message.from_dict(data)
    assert restored.type == sample_message.type
    assert restored.payload == sample_message.payload


def test_message_types() -> None:
    assert MessageType.COMMAND.value == "command"
    assert MessageType.RESPONSE.value == "response"
    assert MessageType.EVENT.value == "event"
    assert MessageType.ACK.value == "ack"
    assert MessageType.PING.value == "ping"
    assert MessageType.PONG.value == "pong"


def test_message_from_dict_invalid_type() -> None:
    with pytest.raises(ValueError):
        Message.from_dict({"type": "unknown"})
