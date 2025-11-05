from fastapi import APIRouter, Depends
from typing import Dict, Any
from federated_api.auth import require_api_key
from federated_api.services.merge_service import MergeService

router = APIRouter(prefix="/api/v1/trees", tags=["merge"], dependencies=[Depends(require_api_key)])
service = MergeService()


@router.post("/{tree_id}/merge")
async def merge_changes(tree_id: str, payload: Dict[str, Any]) -> dict:
    local_tree = payload.get("local_tree", {})
    changes = payload.get("changes", {})
    return service.merge_changes(tree_id, local_tree, changes)


@router.get("/{tree_id}/conflicts")
async def get_conflicts(tree_id: str) -> dict:
    return {"conflicts": service.get_conflicts(tree_id)}


@router.post("/{tree_id}/conflicts/{conflict_id}/resolve")
async def resolve_conflict(tree_id: str, conflict_id: str, resolution: Dict[str, Any]) -> dict:
    return service.resolve_conflict(tree_id, conflict_id, resolution)

