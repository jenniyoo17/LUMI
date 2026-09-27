"""Central configuration, loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load a .env file if present (local dev convenience). Does nothing in
# environments where the vars are already set (e.g. CI, containers).
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database file. Overridable for tests (see tests/conftest use of
# an in-memory or temp-file DB).
DATABASE_PATH = os.getenv("LUMI_DATABASE_PATH", str(BASE_DIR / "lumi.db"))

# Memory importance threshold: candidate memories scoring below this are
# discarded rather than stored (see app/memory).
MEMORY_IMPORTANCE_THRESHOLD = float(os.getenv("LUMI_MEMORY_IMPORTANCE_THRESHOLD", "0.35"))

# MVP has no real auth. Every memory/data row is scoped to this single
# demo user so the schema is already multi-user-shaped without building
# actual auth (explicitly out of scope for this backend right now).
DEMO_USER_ID = "demo-user"

# Sources the backend currently understands. Matches device-hub's
# implemented adapters plus "messages" from the original data contract.
# camera / microphone / location are intentionally NOT included yet —
# there are no corresponding device-hub adapters to produce that data.
SUPPORTED_SOURCES = frozenset({"notes", "calendar", "health", "device", "messages"})
