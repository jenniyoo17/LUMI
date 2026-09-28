# Lumi

Lumi is a privacy-first personal AI companion hackathon project. The repository contains three cooperating parts:

- `backend/`: FastAPI API, SQLite storage, permissions, personal Memory, temporary Notes/Calendar context retrieval, Groq chat, and persistent chat history.
- `device-hub/`: standalone Python source adapters and permission checks. Current providers are local mock data; no real calendar, wearable, health, camera, or microphone service is connected.
- `frontend/`: React + TypeScript + Vite app. Chat, Memory, and Data Control use the backend by default; mock mode remains available.

This guide is written for running Lumi locally on Windows/PowerShell. The component READMEs contain more details: [Frontend](frontend/README.md) and [Device Hub](device-hub/README.md).

## Requirements

- Python 3.11 or newer
- Node.js and npm
- A Groq API key for live LLM responses

The backend uses local SQLite. Its default database path is `backend/lumi.db`; no database server is required. Do not commit `.env` or a database containing personal data.

## 1. Set Up the Backend

Open a PowerShell terminal at the repository root:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.venvs" | Out-Null
py -m venv "$env:USERPROFILE\.venvs\lumi-backend"
& "$env:USERPROFILE\.venvs\lumi-backend\Scripts\Activate.ps1"
Set-Location backend
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run this once in that terminal, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& "$env:USERPROFILE\.venvs\lumi-backend\Scripts\Activate.ps1"
```

Create `backend/.env` with your own key. Keep the real key private; this file is ignored by Git.

```dotenv
GROQ_API_KEY=your_groq_api_key_here
# Optional model override; the application has a default.
GROQ_MODEL=qwen/qwen3.8-27b
```

Start FastAPI from `backend/` with the virtual environment active:

```powershell
uvicorn app.main:app --reload
```

The API is at `http://127.0.0.1:8000`. Swagger is at `http://127.0.0.1:8000/docs` and health check is `GET /health`. The SQLite database and tables initialize automatically at startup.

## 2. Enable a Backend Source

Device Hub and backend permissions are separate and both must be enabled. Enable a backend source through the existing permission API:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/permissions/notes -Method Put -ContentType 'application/json' -Body '{"enabled":true}'
```

For the Calendar demo, enable Calendar separately:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/permissions/calendar -Method Put -ContentType 'application/json' -Body '{"enabled":true}'
```

Inspect current backend permissions with:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/permissions
```

## 3. Send Device Hub Data

Use a second PowerShell terminal. The Device Hub uses Python's standard library and the packages in this repository; it does not require a separate package installation.

Send its deterministic Notes demo:

```powershell
cd device-hub
python send_notes_demo.py
```

The demo enables the Device Hub Notes permission, produces a `StandardData` object, and posts it to the running backend `/data` endpoint. `--disable-device-notes` demonstrates the Device Hub-side permission gate; denied data is not sent.

For Calendar, enable both Device Hub and backend Calendar permissions. From `device-hub/`, run:

```powershell
python -c "from permissions.permission_manager import PermissionManager; from adapters.calendar_adapter import CalendarAdapter; from lumi_client import send_data_to_lumi; p=PermissionManager(); p.enable('calendar'); print(send_data_to_lumi(CalendarAdapter(p).fetch()))"
```

The bridge currently sends only Notes and Calendar. Chat can retrieve relevant Notes or Calendar context; other source adapters are mock-only and do not yet provide chat context.

## 4. Run the Frontend

In another terminal at the repository root:

```powershell
cd frontend
npm ci
$env:VITE_API_URL = 'http://localhost:8000'
npm run dev
```

Open the Vite URL printed in the terminal, normally `http://localhost:5173`. Leave `VITE_USE_MOCK_API` unset for the real service. To run with the local mock service instead:

```powershell
$env:VITE_USE_MOCK_API = 'true'
npm run dev
```

Vite environment variables are read when the dev server starts, so restart it after changing them. The frontend authentication is demo-only and is not backend authentication. The seeded demo login is `demo@lumi.app` / `lumi1234`.

## 5. Try a Chat Request

After enabling a backend permission and sending a matching Device Hub item, ask Lumi through the frontend, or call the API directly:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/chat -Method Post -ContentType 'application/json' -Body '{"message":"When is my DBMS exam?"}'
```

Successful chats are stored in chat history, separately from Memory. Relevant authorized source data is passed as temporary context; it is not automatically copied into Memory. Existing history can be viewed with `GET /chat/history` and cleared with `DELETE /chat/history`.

## API Overview

- `GET /health` - backend health check.
- `POST /data` - ingest a Device Hub `StandardData.to_dict()` payload.
- `GET /permissions`, `PUT /permissions/{source}` - read or update backend permissions.
- `GET /memory`, `POST /memory`, `DELETE /memory/{id}`, `DELETE /memory` - explicit personal Memory operations.
- `POST /chat`, `GET /chat/history`, `DELETE /chat/history` - chat and separate conversation history.

Use Swagger at `/docs` for request/response examples. Backend permission changes do not synchronize the independent Device Hub `PermissionManager` automatically.

## Run Tests and Build

Backend tests, from `backend/` with its environment active:

```powershell
python -m pytest tests -q
```

Device Hub tests, from `device-hub/`:

```powershell
python -m unittest discover -s tests -v
```

Frontend TypeScript and production build, from `frontend/`:

```powershell
npm run build
```

## Extending the Project

Keep source access behind the existing permission checks. For a new Device Hub source, add its schema value, provider, adapter, and tests without changing the shared `StandardData` envelope. Backend ingestion already accepts the standard envelope for supported backend source names; context retrieval currently implements Notes and Calendar only. Add explicit retrieval behavior and tests before allowing another source into chat context. Keep temporary context, explicit Memory, and chat history separate.
