"""Shared test fixtures.

LUMI_DATABASE_PATH must be set BEFORE app.config is imported anywhere,
since it's read once at module import time. That's why this file points
it at a temp file as its very first action.
"""

from __future__ import annotations

import os
import tempfile

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ["LUMI_DATABASE_PATH"] = _db_path

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.models.database import reset_db  # noqa: E402


@pytest.fixture()
def client():
    """A TestClient with a freshly wiped database for every test function."""

    with TestClient(app) as test_client:
        reset_db()
        yield test_client
