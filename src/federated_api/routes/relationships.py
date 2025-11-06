from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from typing import Dict, Any, List, Optional
from federated_api.auth import require_api_key
from federated_api.services.tree_service import TreeService

router = APIRouter(prefix="/api/v1/trees", tags=["relationships"], dependencies=[Depends(require_api_key)])
tree_service = TreeService()


@router.post("/{tree_id}/relationships")
async def add_relationship(
    tree_id: str,
    relationship_data: Dict[str, Any]
) -> dict:
    """Add a relationship between methods with weights."""
    try:
        relationship_id = tree_service.add_relationship(tree_id, relationship_data)
        return {"status": "added", "relationship_id": relationship_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{tree_id}/relationships")
async def get_relationships(
    tree_id: str,
    path: Optional[str] = None
) -> Dict[str, Any]:
    """Get all relationships, optionally filtered by path."""
    try:
        relationships = tree_service.get_relationships(tree_id, path)
        return {"relationships": relationships, "count": len(relationships)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{tree_id}/relationships/{path:path}")
async def get_relationships_for_path(
    tree_id: str,
    path: str
) -> Dict[str, Any]:
    """Get all relationships for a specific path."""
    try:
        relationships = tree_service.get_relationships(tree_id, path)
        return {"relationships": relationships, "count": len(relationships), "path": path}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{tree_id}/relationships/id/{relationship_id}")
async def get_relationship(
    tree_id: str,
    relationship_id: str
) -> Dict[str, Any]:
    """Get a specific relationship by ID."""
    try:
        relationship = tree_service.get_relationship(tree_id, relationship_id)
        if relationship is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
        return relationship
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{tree_id}/relationships/{relationship_id}")
async def update_relationship(
    tree_id: str,
    relationship_id: str,
    updates: Dict[str, Any]
) -> dict:
    """Update an existing relationship."""
    try:
        tree_service.update_relationship(tree_id, relationship_id, updates)
        return {"status": "updated", "relationship_id": relationship_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{tree_id}/relationships/{relationship_id}")
async def remove_relationship(
    tree_id: str,
    relationship_id: str
) -> dict:
    """Remove a relationship."""
    try:
        removed = tree_service.remove_relationship(tree_id, relationship_id)
        if not removed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relationship not found")
        return {"status": "removed", "relationship_id": relationship_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

