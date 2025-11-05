from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from federated_api.models import CloneRequest, CloneResponse, ExpandRequest, ExpandResponse, Tree
from federated_api.auth import require_api_key
from federated_api.services.tree_service import TreeService

router = APIRouter(prefix="/api/v1/trees", tags=["trees"], dependencies=[Depends(require_api_key)])
service = TreeService()


@router.post("/clone", response_model=CloneResponse)
async def clone_tree(payload: CloneRequest) -> CloneResponse:
    result = service.clone(payload.architecture, payload.constraints)
    return CloneResponse(**result)


@router.post("/{tree_id}/expand", response_model=ExpandResponse)
async def expand_tree(tree_id: str, payload: ExpandRequest) -> ExpandResponse:
    if not tree_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tree_id required")
    new_nodes = service.expand(tree_id, payload.architecture)
    return ExpandResponse(new_nodes=new_nodes)


@router.get("/{tree_id}", response_model=Tree)
async def get_tree(tree_id: str) -> Tree:
    from federated_api.database import tree_repository

    tree = tree_repository.get(tree_id)
    if not tree:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tree not found")
    return Tree(**tree)


@router.put("/{tree_id}/sync")
async def sync_tree(tree_id: str, payload: dict) -> dict:
    # Stub: accept and return status
    return {"status": "synced"}

