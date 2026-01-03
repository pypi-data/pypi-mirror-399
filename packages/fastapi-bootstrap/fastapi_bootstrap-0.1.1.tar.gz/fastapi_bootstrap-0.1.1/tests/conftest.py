"""Pytest configuration and fixtures."""

import os

import pytest


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["LOG_LEVEL"] = "ERROR"  # Reduce log noise in tests
    os.environ["LOG_JSON"] = "false"
    yield
    # Cleanup if needed
