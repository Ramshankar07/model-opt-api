from __future__ import annotations

from typing import Any, Dict, List, Optional

from federated_api.database import tree_repository
from federated_api.services.validation_service import ValidationService


class TreeService:
    def __init__(self):
        self.validation_service = ValidationService()

    def clone(self, architecture: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new empty taxonomy structure."""
        taxonomy = {}
        # Validate the empty structure (should pass)
        self.validation_service.validate_schema_structure(taxonomy)
        tree_id = tree_repository.create(taxonomy)
        taxonomy = tree_repository.get(tree_id) or {}
        return {"tree_id": tree_id, "taxonomy": taxonomy}

    def expand(self, tree_id: str, architecture: str, path: Optional[str] = None) -> Dict[str, Any]:
        """Expand taxonomy structure. Stub implementation for now."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        return {"expanded": True, "path": path}

    def get_taxonomy(self, tree_id: str) -> Dict[str, Any]:
        """Get full taxonomy structure."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        return taxonomy

    def get_model_family(self, tree_id: str, family_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific model family."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        return taxonomy.get(family_name)

    def get_path(self, tree_id: str, path: str) -> Optional[Any]:
        """Get data at a specific path (e.g., 'model_family/subcategory/specific_model')."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        
        self.validation_service.validate_path(path)
        parts = path.split('/')
        current = taxonomy
        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current

    def get_optimization_methods(self, tree_id: str, path: str) -> Optional[List[Dict[str, Any]]]:
        """Get optimization methods for a specific model path."""
        model_data = self.get_path(tree_id, path)
        if model_data is None or not isinstance(model_data, dict):
            return None
        
        opt_methods = model_data.get('optimization_methods', {})
        if not isinstance(opt_methods, dict):
            return None
        
        # Collect all methods from all categories
        all_methods = []
        for category in ['quantization', 'fusion', 'pruning', 'structural']:
            if category in opt_methods:
                category_data = opt_methods[category]
                if isinstance(category_data, dict):
                    for subcat_name, subcat_data in category_data.items():
                        if isinstance(subcat_data, dict) and 'methods' in subcat_data:
                            methods = subcat_data['methods']
                            if isinstance(methods, list):
                                all_methods.extend(methods)
        
        return all_methods if all_methods else None

    def add_optimization_method(
        self, 
        tree_id: str, 
        path: str, 
        category: str, 
        subcategory: str, 
        method_data: Dict[str, Any]
    ) -> None:
        """Add an optimization method to a specific path."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        
        self.validation_service.validate_path(path)
        self.validation_service.validate_method_data(method_data)
        
        # Navigate to the model
        parts = path.split('/')
        if len(parts) < 3:
            raise ValueError("Path must be at least model_family/subcategory/specific_model")
        
        current = taxonomy
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Ensure optimization_methods structure exists
        if 'optimization_methods' not in current:
            current['optimization_methods'] = {}
        
        opt_methods = current['optimization_methods']
        
        # Ensure category exists
        if category not in opt_methods:
            opt_methods[category] = {}
        
        # Ensure subcategory exists
        if subcategory not in opt_methods[category]:
            opt_methods[category][subcategory] = {'methods': []}
        
        # Add the method
        opt_methods[category][subcategory]['methods'].append(method_data)
        
        # Validate the updated structure
        self.validation_service.validate_schema_structure(taxonomy)
        tree_repository.upsert(tree_id, taxonomy)

    def update_optimization_method(
        self, 
        tree_id: str, 
        path: str, 
        category: str, 
        subcategory: str, 
        method_index: int, 
        updates: Dict[str, Any]
    ) -> None:
        """Update an existing optimization method."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        
        self.validation_service.validate_path(path)
        
        # Navigate to the methods list
        parts = path.split('/')
        current = taxonomy
        for part in parts:
            if part not in current:
                raise ValueError(f"Path not found: {path}")
            current = current[part]
        
        if 'optimization_methods' not in current:
            raise ValueError(f"No optimization_methods found at path: {path}")
        
        opt_methods = current['optimization_methods']
        if category not in opt_methods:
            raise ValueError(f"Category '{category}' not found")
        
        if subcategory not in opt_methods[category]:
            raise ValueError(f"Subcategory '{subcategory}' not found in category '{category}'")
        
        methods = opt_methods[category][subcategory].get('methods', [])
        if not isinstance(methods, list) or method_index < 0 or method_index >= len(methods):
            raise ValueError(f"Invalid method index: {method_index}")
        
        # Update the method
        methods[method_index].update(updates)
        
        # Validate the updated method
        self.validation_service.validate_optimization_method(methods[method_index])
        
        # Validate the entire structure
        self.validation_service.validate_schema_structure(taxonomy)
        tree_repository.upsert(tree_id, taxonomy)

    def remove_optimization_method(
        self, 
        tree_id: str, 
        path: str, 
        category: str, 
        subcategory: str, 
        method_index: int
    ) -> bool:
        """Remove an optimization method."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        
        self.validation_service.validate_path(path)
        
        # Navigate to the methods list
        parts = path.split('/')
        current = taxonomy
        for part in parts:
            if part not in current:
                raise ValueError(f"Path not found: {path}")
            current = current[part]
        
        if 'optimization_methods' not in current:
            return False
        
        opt_methods = current['optimization_methods']
        if category not in opt_methods:
            return False
        
        if subcategory not in opt_methods[category]:
            return False
        
        methods = opt_methods[category][subcategory].get('methods', [])
        if not isinstance(methods, list) or method_index < 0 or method_index >= len(methods):
            return False
        
        # Remove the method
        methods.pop(method_index)
        
        # Validate the updated structure
        self.validation_service.validate_schema_structure(taxonomy)
        tree_repository.upsert(tree_id, taxonomy)
        return True
