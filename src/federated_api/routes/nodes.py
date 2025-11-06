from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from typing import Dict, Any
from federated_api.auth import require_api_key
from federated_api.services.tree_service import TreeService

router = APIRouter(prefix="/api/v1/trees", tags=["nodes"], dependencies=[Depends(require_api_key)])
tree_service = TreeService()


@router.post("/{tree_id}/nodes")
async def add_node(tree_id: str, node_data: Dict[str, Any]) -> dict:
    try:
        tree_service.add_node_to_tree(tree_id, node_data)
        return {"status": "added"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{tree_id}/nodes/{node_id}")
async def update_node(tree_id: str, node_id: str, updates: Dict[str, Any]) -> dict:
    from federated_api.database import tree_repository
    from federated_api.services.validation_service import ValidationService

    tree = tree_repository.get(tree_id)
    if tree is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tree not found")
    
    # Find the node to update using service helper
    node_index = tree_service._get_node_index(tree, node_id)
    if node_index == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    
    # If updating the ID, check for uniqueness
    if "id" in updates and updates["id"] != node_id:
        existing_node_ids = {
            n.get("id") for i, n in enumerate(tree.get("nodes", []))
            if i != node_index and n.get("id")
        }
        validation_service = ValidationService()
        try:
            validation_service.validate_node({"id": updates["id"]}, existing_node_ids)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    # Update the node
    tree["nodes"][node_index].update(updates)
    tree_service._update_metadata(tree)
    tree_repository.upsert(tree_id, tree)
    return {"status": "updated"}


@router.delete("/{tree_id}/nodes/{node_id}")
async def prune_node(tree_id: str, node_id: str) -> dict:
    try:
        removed = tree_service.remove_node_from_tree(tree_id, node_id)
        if not removed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
        return {"status": "pruned"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

