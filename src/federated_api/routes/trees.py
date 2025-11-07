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
from federated_api.services.conversion_service import ConversionService

# We expose a combined router that includes both public and protected sub-routers
router = APIRouter()
authed = APIRouter(prefix="/api/v1/trees", tags=["trees"], dependencies=[Depends(require_api_key)])
public = APIRouter(prefix="/api/v1/trees", tags=["trees"])

service = TreeService()
validation_service = ValidationService()
conversion_service = ConversionService()


# -------------------------
# Protected (API-key required)
# -------------------------

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
    
    # Extract relationships if present (don't modify original)
    relationships = taxonomy.get("relationships", [])
    taxonomy_data = {k: v for k, v in taxonomy.items() if k != "relationships"}
    
    return OptimizationTaxonomy(
        data=taxonomy_data,
        relationships=relationships
    )


@authed.put("/{tree_id}")
async def update_tree_from_file(tree_id: str) -> Dict[str, Any]:
    """Update a tree by loading data from backups/base_tree.json.
    
    This endpoint replaces the entire tree data for the specified tree_id
    with the contents of backups/base_tree.json. The file is validated
    before updating.
    """
    try:
        # Load from base_tree.json (relative to project root)
        file_path = "backups/base_tree.json"
        result = service.load_from_file(tree_id, file_path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {str(e)}"
        )
    except ValueError as e:
        # Catches both JSON decode errors (converted to ValueError) and validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


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


def _convert_legacy_to_schema(legacy: Dict[str, Any]) -> Dict[str, Any]:
    """Convert legacy graph format (nodes/edges) to schema format with relationships."""
    return conversion_service.legacy_to_schema(legacy)


@authed.post("/import")
async def import_taxonomy(payload: Dict[str, Any]) -> Dict[str, str]:
    """Import a taxonomy structure. Supports both new schema format and legacy graph format with edge weights."""
    try:
        # Check if it's legacy format and convert
        if "nodes" in payload and "edges" in payload:
            # Legacy format - convert edges with weights to relationships
            taxonomy = _convert_legacy_to_schema(payload)
            # Note: This creates a minimal taxonomy with just relationships
            # In production, you'd want a more sophisticated conversion
        else:
            taxonomy = payload.get("taxonomy", payload)  # Allow direct taxonomy or wrapped
        
        # Validate the taxonomy structure (relationships are optional)
        validation_service.validate_schema_structure(taxonomy)
        tree_id = tree_repository.create(taxonomy)
        return {"tree_id": tree_id, "converted_from_legacy": "nodes" in payload and "edges" in payload}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@authed.get("/{tree_id}/export")
async def export_taxonomy(
    tree_id: str,
    format: str = "schema"  # "schema" or "legacy"
) -> Dict[str, Any]:
    """Export taxonomy structure. Can export as schema format or legacy graph format (preserving weights)."""
    try:
        taxonomy = service.get_taxonomy(tree_id)
        
        if format == "legacy":
            # Convert to legacy format, preserving relationships as edges with weights
            legacy = conversion_service.schema_to_legacy(taxonomy)
            return legacy
        else:
            # Return schema format
            return taxonomy
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@authed.get("/{tree_id}/weights")
async def get_all_weights(tree_id: str) -> Dict[str, Any]:
    """Get all weight data from a taxonomy structure."""
    try:
        taxonomy = service.get_taxonomy(tree_id)
        weights_list = conversion_service.extract_weights_from_taxonomy(taxonomy)
        return {"weights": weights_list, "count": len(weights_list)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# -------------------------
# Public (no auth required)
# -------------------------

@public.post("/clone", response_model=CloneResponse)
async def clone_tree(payload: CloneRequest) -> CloneResponse:
    """Create a new empty taxonomy structure. No API key required."""
    result = service.clone(payload.architecture, payload.constraints)
    return CloneResponse(
        tree_id=result["tree_id"],
        taxonomy=OptimizationTaxonomy(data=result["taxonomy"])
    )


@public.get("/sample", response_model=OptimizationTaxonomy)
async def sample_tree() -> OptimizationTaxonomy:
    """Return a sample empty taxonomy structure."""
    sample = {}
    return OptimizationTaxonomy(data=sample)


# Combine routers so main.py can keep including `router`
router.include_router(public)
router.include_router(authed)
