"""Tests for the device identity store."""

import json

import pytest

from debian.device.identity import DeviceIdentity, DeviceIdentityStore


@pytest.fixture
def store(tmp_path) -> DeviceIdentityStore:
    return DeviceIdentityStore(config_dir=str(tmp_path / "config"))


def test_generate_identity() -> None:
    identity = DeviceIdentity.generate()
    assert identity.device_type == "server"
    assert identity.platform == "debian"
    assert identity.device_id.startswith("debian-")


def test_save_and_load(store: DeviceIdentityStore) -> None:
    identity = DeviceIdentity.generate()
    store.save(identity)
    loaded = store.load()
    assert loaded is not None
    assert loaded.device_id == identity.device_id


def test_get_or_create_creates(store: DeviceIdentityStore) -> None:
    identity = store.get_or_create()
    loaded = store.load()
    assert loaded is not None
    assert loaded.device_id == identity.device_id


def test_get_or_create_returns_existing(store: DeviceIdentityStore) -> None:
    original = store.get_or_create()
    cached = store.get_or_create()
    assert cached.device_id == original.device_id


def test_load_nonexistent_returns_none(store: DeviceIdentityStore) -> None:
    assert store.load() is None
