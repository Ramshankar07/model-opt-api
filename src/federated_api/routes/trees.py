from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status

from federated_api.auth import require_api_key
from federated_api.database import tree_repository
from federated_api.models import (
    CloneRequest,
    CloneResponse,
    ExpandRequest,
    ExpandResponse,
    OptimizationTaxonomy,
)
from federated_api.services.tree_service import TreeService
from federated_api.services.validation_service import ValidationService

# We expose a combined router that includes both public and protected sub-routers
router = APIRouter()
authed = APIRouter(prefix="/api/v1/trees", tags=["trees"], dependencies=[Depends(require_api_key)])
public = APIRouter(prefix="/api/v1/trees", tags=["trees"])

service = TreeService()
validation_service = ValidationService()


# -------------------------
# Protected (API-key required)
# -------------------------

@authed.post("/clone", response_model=CloneResponse)
async def clone_tree(payload: CloneRequest) -> CloneResponse:
    result = service.clone(payload.architecture, payload.constraints)
    return CloneResponse(
        tree_id=result["tree_id"],
        taxonomy=OptimizationTaxonomy(data=result["taxonomy"])
    )


@authed.post("/{tree_id}/expand", response_model=ExpandResponse)
async def expand_tree(tree_id: str, payload: ExpandRequest) -> ExpandResponse:
    if not tree_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tree_id required")
    result = service.expand(tree_id, payload.architecture, payload.path)
    return ExpandResponse(**result)


@authed.get("/{tree_id}", response_model=OptimizationTaxonomy)
async def get_tree(tree_id: str) -> OptimizationTaxonomy:
    taxonomy = tree_repository.get(tree_id)
    if not taxonomy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tree not found")
    return OptimizationTaxonomy(data=taxonomy)


@authed.get("/{tree_id}/taxonomy")
async def get_taxonomy(tree_id: str) -> Dict[str, Any]:
    """Get full taxonomy structure."""
    try:
        taxonomy = service.get_taxonomy(tree_id)
        return taxonomy
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@authed.get("/{tree_id}/model_family/{family}")
async def get_model_family(tree_id: str, family: str) -> Dict[str, Any]:
    """Get a specific model family."""
    try:
        family_data = service.get_model_family(tree_id, family)
        if family_data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Model family '{family}' not found")
        return family_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@authed.get("/{tree_id}/path/{path:path}")
async def get_path(tree_id: str, path: str) -> Any:
    """Get data at a specific path (e.g., 'model_family/subcategory/specific_model')."""
    try:
        data = service.get_path(tree_id, path)
        if data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Path '{path}' not found")
        return data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@authed.get("/{tree_id}/methods/{path:path}")
async def get_optimization_methods(tree_id: str, path: str) -> Dict[str, Any]:
    """Get all optimization methods for a specific model path."""
    try:
        methods = service.get_optimization_methods(tree_id, path)
        if methods is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Path '{path}' not found or has no methods")
        return {"methods": methods, "count": len(methods)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@authed.put("/{tree_id}/sync")
async def sync_tree(tree_id: str, payload: Dict[str, Any]) -> Dict[str, str]:
    # Stub: accept and return status
    return {"status": "synced"}


@authed.post("/import")
async def import_taxonomy(payload: Dict[str, Any]) -> Dict[str, str]:
    """Import a taxonomy structure."""
    try:
        taxonomy = payload.get("taxonomy", payload)  # Allow direct taxonomy or wrapped
        # Validate the taxonomy structure
        validation_service.validate_schema_structure(taxonomy)
        tree_id = tree_repository.create(taxonomy)
        return {"tree_id": tree_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -------------------------
# Public (no auth required)
# -------------------------

@public.get("/sample", response_model=OptimizationTaxonomy)
async def sample_tree() -> OptimizationTaxonomy:
    """Return a sample empty taxonomy structure."""
    sample = {}
    return OptimizationTaxonomy(data=sample)


# Combine routers so main.py can keep including `router`
router.include_router(public)
router.include_router(authed)
