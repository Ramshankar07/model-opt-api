from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from typing import Dict, Any
from federated_api.auth import require_api_key
from federated_api.services.tree_service import TreeService

router = APIRouter(prefix="/api/v1/trees", tags=["methods"], dependencies=[Depends(require_api_key)])
tree_service = TreeService()


@router.post("/{tree_id}/methods")
async def add_method(
    tree_id: str, 
    method_data: Dict[str, Any]
) -> dict:
    """Add an optimization method to a taxonomy."""
    try:
        # Extract required path information from method_data
        path = method_data.get("path")
        category = method_data.get("category")
        subcategory = method_data.get("subcategory")
        
        if not path:
            raise ValueError("'path' is required (e.g., 'model_family/subcategory/specific_model')")
        if not category:
            raise ValueError("'category' is required (e.g., 'quantization', 'fusion', 'pruning', 'structural')")
        if not subcategory:
            raise ValueError("'subcategory' is required (e.g., 'weight_only', 'layer_fusion', etc.)")
        
        # Extract the actual method data (excluding path/category/subcategory)
        method = {k: v for k, v in method_data.items() if k not in ['path', 'category', 'subcategory']}
        
        tree_service.add_optimization_method(tree_id, path, category, subcategory, method)
        return {"status": "added"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{tree_id}/methods/{path:path}/{category}/{subcategory}/{method_index:int}")
async def update_method(
    tree_id: str, 
    path: str,
    category: str,
    subcategory: str,
    method_index: int,
    updates: Dict[str, Any]
) -> dict:
    """Update an optimization method."""
    try:
        tree_service.update_optimization_method(tree_id, path, category, subcategory, method_index, updates)
        return {"status": "updated"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{tree_id}/methods/{path:path}/{category}/{subcategory}/{method_index:int}")
async def remove_method(
    tree_id: str, 
    path: str,
    category: str,
    subcategory: str,
    method_index: int
) -> dict:
    """Remove an optimization method."""
    try:
        removed = tree_service.remove_optimization_method(tree_id, path, category, subcategory, method_index)
        if not removed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Method not found")
        return {"status": "removed"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
