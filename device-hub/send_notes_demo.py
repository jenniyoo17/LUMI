"""Produce the Phase 4 demo note and send it to the local Lumi backend."""

from __future__ import annotations

import argparse
import json

from adapters.notes_adapter import NotesAdapter
from lumi_client import send_notes_to_lumi
from permissions.permission_manager import PermissionManager


class DemoNotesProvider:
    def get_data(self) -> dict[str, object]:
        return {"text": "My DBMS exam is tomorrow morning.", "is_mock": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend-url", default="http://127.0.0.1:8000")
    parser.add_argument("--disable-device-notes", action="store_true")
    args = parser.parse_args()

    permissions = PermissionManager()
    if args.disable_device_notes:
        permissions.disable("notes")
    else:
        permissions.enable("notes")

    standard_data = NotesAdapter(permissions, DemoNotesProvider()).fetch()
    print(json.dumps(standard_data.to_dict(), indent=2))
    if not standard_data.permission:
        print("Device Hub permission is disabled; no data was sent.")
        return

    print(json.dumps(send_notes_to_lumi(standard_data, args.backend_url), indent=2))


if __name__ == "__main__":
    main()