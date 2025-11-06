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
    Tree,
)
from federated_api.services.tree_service import TreeService
from federated_api.services.validation_service import ValidationService

# We expose a combined router that includes both public and protected sub-routers
router = APIRouter()
authed = APIRouter(prefix="/api/v1/trees", tags=["trees"], dependencies=[Depends(require_api_key)])
public = APIRouter(prefix="/api/v1/trees", tags=["trees"])

service = TreeService()
validation_service = ValidationService()


def _convert_legacy_tree(legacy: Dict[str, Any]) -> Dict[str, Any]:
    """Convert legacy tree format (dict of nodes) to API format (list of nodes)."""
    # legacy['nodes'] is a dict keyed by node_id with rich metadata
    nodes_dict = legacy.get("nodes", {})
    nodes = []
    for node_id, data in nodes_dict.items():
        node_payload: Dict[str, Any] = {"id": node_id}
        node_payload.update(data)
        nodes.append(node_payload)

    # legacy['edges'] is a list with parent/child; convert to source/target
    edges = []
    for e in legacy.get("edges", []):
        edge_data = e.get("data") or {}
        edges.append({
            "source": e.get("parent"),
            "target": e.get("child"),
            **edge_data
        })

    meta = legacy.get("metadata", {})
    return {"nodes": nodes, "edges": edges, "meta": meta}


# -------------------------
# Protected (API-key required)
# -------------------------

@authed.post("/clone", response_model=CloneResponse)
async def clone_tree(payload: CloneRequest) -> CloneResponse:
    result = service.clone(payload.architecture, payload.constraints)
    return CloneResponse(**result)


@authed.post("/{tree_id}/expand", response_model=ExpandResponse)
async def expand_tree(tree_id: str, payload: ExpandRequest) -> ExpandResponse:
    if not tree_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tree_id required")
    new_nodes = service.expand(tree_id, payload.architecture)
    return ExpandResponse(new_nodes=new_nodes)


@authed.get("/{tree_id}", response_model=Tree)
async def get_tree(tree_id: str) -> Tree:
    tree = tree_repository.get(tree_id)
    if not tree:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tree not found")
    return Tree(**tree)


@authed.put("/{tree_id}/sync")
async def sync_tree(tree_id: str, payload: Dict[str, Any]) -> Dict[str, str]:
    # Stub: accept and return status
    return {"status": "synced"}


@authed.post("/import", response_model=Dict[str, str])
async def import_legacy_tree(payload: Dict[str, Any]) -> Dict[str, str]:
    """Import a tree in legacy format (dict of nodes) and convert to API format."""
    try:
        converted = _convert_legacy_tree(payload)
        # Validate the converted tree (checks for duplicate nodes, invalid edges, etc.)
        validation_service.validate_tree(converted)
        # Update metadata
        service._update_metadata(converted)
        tree_id = tree_repository.create(converted)
        return {"tree_id": tree_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# -------------------------
# Public (no auth required)
# -------------------------

@public.get("/sample", response_model=Tree)
async def sample_tree() -> Tree:
    """Return a sample tree in the legacy format, converted to API format."""
    legacy = {
      "nodes": {
        "node_quantize_int8_cnn": {
          "architecture": {"family": "CNN", "variant": "ResNet"},
          "compression_config": {"type": "quantization", "bits": 8, "method": "int8_weight_only"},
          "performance": {
            "accuracy_retention": 0.98,
            "compression_ratio": 4.0,
            "latency_speedup": 2.0,
            "memory_gb": 2.5,
            "latency_ms": 12.5
          },
          "validation": {"sample_count": 15, "confidence": 0.85, "validators": 3, "source": "validated"},
          "source": {
            "origin": "federated",
            "paper_refs": ["Post-Training Quantization for Neural Networks"],
            "status": "validated",
            "paper_score": 0.9
          },
          "visit_count": 0,
          "q_value": 0.5,
          "local_updated": "2024-01-15T10:00:00"
        },
        "node_quantize_prune_cnn": {
          "architecture": {"family": "CNN", "variant": "ResNet"},
          "compression_config": {
            "type": "quantization",
            "bits": 8,
            "method": "int8_weight_only",
            "pruning": {"type": "structured", "ratio": 0.3}
          },
          "performance": {
            "accuracy_retention": 0.95,
            "compression_ratio": 5.5,
            "latency_speedup": 2.8,
            "memory_gb": 1.8,
            "latency_ms": 10.0
          },
          "validation": {"sample_count": 12, "confidence": 0.78, "validators": 2, "source": "validated"},
          "source": {
            "origin": "federated",
            "paper_refs": ["Structured Pruning and Quantization for Efficient Inference"],
            "status": "validated",
            "paper_score": 0.85
          },
          "visit_count": 0,
          "q_value": 0.5,
          "local_updated": "2024-01-15T10:00:00"
        },
        "node_quantize_prune_fuse_cnn": {
          "architecture": {"family": "CNN", "variant": "ResNet"},
          "compression_config": {
            "type": "quantization",
            "bits": 8,
            "method": "int8_weight_only",
            "pruning": {"type": "structured", "ratio": 0.3},
            "fusion": {"types": ["conv_bn_relu", "linear_gelu"]}
          },
          "performance": {
            "accuracy_retention": 0.94,
            "compression_ratio": 6.2,
            "latency_speedup": 3.5,
            "memory_gb": 1.6,
            "latency_ms": 8.5
          },
          "validation": {"sample_count": 20, "confidence": 0.92, "validators": 5, "source": "validated"},
          "source": {
            "origin": "federated",
            "paper_refs": ["Efficient CNN Inference via Layer Fusion and Quantization"],
            "status": "validated",
            "paper_score": 0.95
          },
          "visit_count": 0,
          "q_value": 0.5,
          "local_updated": "2024-01-15T10:00:00"
        },
        "node_quantize_vit": {
          "architecture": {"family": "ViT", "variant": "VisionTransformer"},
          "compression_config": {
            "type": "quantization",
            "bits": 8,
            "method": "int8_weight_only",
            "token_merge": {"ratio": 0.3, "r": 16}
          },
          "performance": {
            "accuracy_retention": 0.96,
            "compression_ratio": 4.5,
            "latency_speedup": 2.2,
            "memory_gb": 3.2,
            "latency_ms": 15.0
          },
          "validation": {"sample_count": 8, "confidence": 0.70, "validators": 1, "source": "validated"},
          "source": {
            "origin": "federated",
            "paper_refs": ["Token Merging for Vision Transformers"],
            "status": "experimental",
            "paper_score": 0.80
          },
          "visit_count": 0,
          "q_value": 0.5,
          "local_updated": "2024-01-15T10:00:00"
        }
      },
      "edges": [
        {
          "parent": "node_quantize_int8_cnn",
          "child": "node_quantize_prune_cnn",
          "data": {"weights": {"success_probability": 0.82, "sample_count": 12, "confidence": 0.78}}
        },
        {
          "parent": "node_quantize_prune_cnn",
          "child": "node_quantize_prune_fuse_cnn",
          "data": {"weights": {"success_probability": 0.88, "sample_count": 20, "confidence": 0.92}}
        }
      ],
      "metadata": {"node_count": 4, "edge_count": 2, "saved_at": "2024-01-15T10:00:00"}
    }

    converted = _convert_legacy_tree(legacy)
    return Tree(**converted)


# Combine routers so main.py can keep including `router`
router.include_router(public)
router.include_router(authed)

