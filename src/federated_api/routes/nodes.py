from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from typing import Dict, Any
from federated_api.auth import require_api_key

router = APIRouter(prefix="/api/v1/trees", tags=["nodes"], dependencies=[Depends(require_api_key)])


@router.post("/{tree_id}/nodes")
async def add_node(tree_id: str, node_data: Dict[str, Any]) -> dict:
    from federated_api.database import tree_repository

    tree = tree_repository.get(tree_id)
    if tree is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tree not found")
    tree.setdefault("nodes", []).append(node_data)
    tree_repository.upsert(tree_id, tree)
    return {"status": "added"}


@router.put("/{tree_id}/nodes/{node_id}")
async def update_node(tree_id: str, node_id: str, updates: Dict[str, Any]) -> dict:
    from federated_api.database import tree_repository

    tree = tree_repository.get(tree_id)
    if tree is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tree not found")
    for n in tree.get("nodes", []):
        if n.get("id") == node_id:
            n.update(updates)
            tree_repository.upsert(tree_id, tree)
            return {"status": "updated"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")


@router.delete("/{tree_id}/nodes/{node_id}")
async def prune_node(tree_id: str, node_id: str) -> dict:
    from federated_api.database import tree_repository

    tree = tree_repository.get(tree_id)
    if tree is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tree not found")
    before = len(tree.get("nodes", []))
    tree["nodes"] = [n for n in tree.get("nodes", []) if n.get("id") != node_id]
    after = len(tree.get("nodes", []))
    if before == after:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    tree_repository.upsert(tree_id, tree)
    return {"status": "pruned"}

