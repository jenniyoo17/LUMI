"""GET/PUT /permissions — manage existing per-source permissions."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import PermissionToggle, PermissionUpdateResponse
from app.permissions.service import get_all_permissions, set_permission

router = APIRouter()


@router.get("/permissions", response_model=dict[str, bool])
def list_permissions() -> dict[str, bool]:
    return {state.source: state.permission for state in get_all_permissions()}


@router.put("/permissions/{source}", response_model=PermissionUpdateResponse)
def update_permission(source: str, payload: PermissionToggle) -> PermissionUpdateResponse:
    try:
        state = set_permission(source, payload.enabled)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PermissionUpdateResponse(source=state.source, enabled=state.permission)