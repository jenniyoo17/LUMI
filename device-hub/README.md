# LUMI Data + Device Hub

The Data + Device Hub is an independent, privacy-first Python module for
collecting personal data from replaceable source adapters. It produces one
standard response shape so a later LUMI module can consume notes, calendar,
health, and generic device data without knowing how each source is implemented.

This MVP uses local mock providers. It does **not** connect to a real calendar,
health service, wearable, Bluetooth device, or other personal data account.
Health and device values are fictional mock data only and are labeled with
`"is_mock": true`.

## Supported sources

| Source | MVP provider | Example data |
| --- | --- | --- |
| `notes` | `MockNotesProvider` | A fictional study note |
| `calendar` | `MockCalendarProvider` | A fictional DBMS exam event |
| `health` | `MockHealthProvider` | Fictional heart rate, steps, and sleep |
| `device` | `MockDeviceProvider` | Fictional smartwatch status |

## Permission model

`PermissionManager` is the single source of truth for access:

```python
from permissions.permission_manager import PermissionManager

permissions = PermissionManager()
permissions.enable("notes")
permissions.disable("health")
permissions.is_enabled("notes")       # True
permissions.check_permission("health") # False
permissions.get_permissions()
```

Permissions are independent and default to disabled. Every adapter checks the
manager before calling its provider. When a source is disabled, the provider
is not called and the adapter returns a safe standardized result with
`permission: false` and an empty `data` object. This prevents unauthorized
source values from being returned or sent downstream.

## Standard data format

Every adapter returns a `StandardData` dataclass with this logical structure:

```json
{
  "source": "notes",
  "timestamp": "2026-09-26T12:30:00+00:00",
  "permission": true,
  "data": {
    "text": "Normalization is an important DBMS topic.",
    "is_mock": true
  }
}
```

`source` is one of `notes`, `calendar`, `health`, or `device`.
`timestamp` must be timezone-aware and serializes as ISO-8601.
`permission` is a boolean. `data` is a mapping and is source-specific.

Disabled example:

```json
{
  "source": "health",
  "timestamp": "2026-09-26T12:30:00+00:00",
  "permission": false,
  "data": {}
}
```

## Folder structure

```text
device-hub/
├── adapters/       # Shared adapter base and source adapters
├── mocks/          # Clearly fictional local providers
├── permissions/    # Central privacy permission manager
├── schemas/        # StandardData validation and serialization
├── tests/          # unittest coverage
├── run_demo.py     # Small standalone demo
└── README.md
```

## Run the tests

From the repository root:

```bash
cd device-hub
python -m unittest discover -s tests -v
```

Run the demo:

```bash
cd device-hub
python run_demo.py
```

## Add a new data source

1. Add the source name to `DataSource` in `schemas/data_schema.py`.
2. Add a clearly fictional or real provider implementing `get_data()`.
3. Add a source adapter extending `BaseAdapter`.
4. Add the adapter and provider exports to their package `__init__.py` files.
5. Add permission and schema tests, especially a test proving disabled access
   never calls the provider.
6. Document whether the provider is mock or real and update this README.

The adapter's standard output does not change when a provider changes.

## Replace a mock with a future real adapter

Each adapter accepts an optional provider object. A future integration can
implement the same `get_data() -> Mapping[str, Any]` contract and be passed to
the existing adapter, for example:

```python
real_notes = NotesAdapter(permissions, provider=RealNotesProvider())
```

The permission check and `StandardData` output remain unchanged. Future
integrations must still honor the explicit permission state and must not claim
that mock values came from a real device.