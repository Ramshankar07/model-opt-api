from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from federated_api.database import tree_repository
from federated_api.services.validation_service import ValidationService
from federated_api.services.migration_service import migrate_taxonomy_to_ideal_schema


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

    def add_relationship(
        self,
        tree_id: str,
        relationship_data: Dict[str, Any]
    ) -> str:
        """Add a relationship between methods with weights."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        
        # Validate relationship data
        self.validation_service.validate_relationship(relationship_data, taxonomy)
        
        # Generate ID if not provided
        if 'id' not in relationship_data:
            relationship_data['id'] = tree_repository.new_id()
        
        # Store relationships at top level (in taxonomy root)
        if 'relationships' not in taxonomy:
            taxonomy['relationships'] = []
        
        if not isinstance(taxonomy['relationships'], list):
            taxonomy['relationships'] = []
        
        taxonomy['relationships'].append(relationship_data)
        
        # Validate the updated structure
        self.validation_service.validate_schema_structure(taxonomy)
        tree_repository.upsert(tree_id, taxonomy)
        
        return relationship_data['id']

    def get_relationships(self, tree_id: str, path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all relationships, optionally filtered by path."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        
        relationships = taxonomy.get('relationships', [])
        if not isinstance(relationships, list):
            return []
        
        # If path is provided, filter relationships that involve this path
        if path:
            filtered = []
            for rel in relationships:
                methods = rel.get('methods', [])
                if any(path in method_path or method_path.startswith(path) for method_path in methods):
                    filtered.append(rel)
            return filtered
        
        return relationships

    def get_relationship(self, tree_id: str, relationship_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific relationship by ID."""
        relationships = self.get_relationships(tree_id)
        for rel in relationships:
            if rel.get('id') == relationship_id:
                return rel
        return None

    def update_relationship(
        self,
        tree_id: str,
        relationship_id: str,
        updates: Dict[str, Any]
    ) -> None:
        """Update an existing relationship."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        
        relationships = taxonomy.get('relationships', [])
        if not isinstance(relationships, list):
            raise ValueError("No relationships found")
        
        # Find and update the relationship
        found = False
        for i, rel in enumerate(relationships):
            if rel.get('id') == relationship_id:
                # Don't allow updating the ID
                updates.pop('id', None)
                relationships[i].update(updates)
                # Validate the updated relationship
                self.validation_service.validate_relationship(relationships[i], taxonomy)
                found = True
                break
        
        if not found:
            raise ValueError(f"Relationship not found: {relationship_id}")
        
        # Validate the entire structure
        self.validation_service.validate_schema_structure(taxonomy)
        tree_repository.upsert(tree_id, taxonomy)

    def remove_relationship(self, tree_id: str, relationship_id: str) -> bool:
        """Remove a relationship."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        
        relationships = taxonomy.get('relationships', [])
        if not isinstance(relationships, list):
            return False
        
        # Find and remove the relationship
        original_count = len(relationships)
        taxonomy['relationships'] = [rel for rel in relationships if rel.get('id') != relationship_id]
        
        if len(taxonomy['relationships']) < original_count:
            # Validate the updated structure
            self.validation_service.validate_schema_structure(taxonomy)
            tree_repository.upsert(tree_id, taxonomy)
            return True
        
        return False

    def load_from_file(self, tree_id: str, file_path: str) -> Dict[str, Any]:
        """Load taxonomy from a JSON file and update the tree.
        
        Args:
            tree_id: The ID of the tree to update
            file_path: Path to the JSON file (relative to project root or absolute)
            
        Returns:
            Dictionary with success status and tree_id
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file contains invalid JSON or validation fails
        """
        # Resolve file path (handle both relative and absolute paths)
        if not os.path.isabs(file_path):
            # If relative, assume it's relative to project root (where run_local.py is)
            # Get the project root by going up from src/federated_api/services
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            file_path = os.path.join(project_root, file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Load JSON file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                taxonomy = json.load(f)
        except json.JSONDecodeError as e:
            # Re-raise with more context
            raise ValueError(f"Invalid JSON in file {file_path}: {e.msg} at line {e.lineno}, column {e.colno}")
        
        # Normalize category names: "weight_quantization" -> "quantization"
        # This handles legacy naming in base_tree.json
        taxonomy = self._normalize_category_names(taxonomy)
        
        # Auto-migrate taxonomy to ideal schema structure
        # This ensures all nodes have techniques, performance, validation, architecture, and paper fields
        taxonomy = migrate_taxonomy_to_ideal_schema(taxonomy)
        
        # Validate the taxonomy structure
        self.validation_service.validate_schema_structure(taxonomy)
        
        # Replace the entire tree (upsert will overwrite if tree_id exists)
        tree_repository.upsert(tree_id, taxonomy)
        
        return {"status": "success", "tree_id": tree_id}

    def _normalize_category_names(self, taxonomy: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize category names and structure in optimization_methods.
        
        Converts:
        1. "weight_quantization" -> "quantization" to match the expected schema
        2. Flat category structure (category -> methods) to nested structure (category -> subcategory -> methods)
        
        This handles legacy naming conventions in base_tree.json.
        """
        if not isinstance(taxonomy, dict):
            return taxonomy
        
        # Recursively process the taxonomy structure
        normalized = {}
        for key, value in taxonomy.items():
            if key == "relationships":
                # Preserve relationships as-is
                normalized[key] = value
            elif isinstance(value, dict):
                # Check if this is a model with optimization_methods
                if "optimization_methods" in value:
                    # Normalize the optimization_methods structure
                    opt_methods = value["optimization_methods"]
                    if isinstance(opt_methods, dict):
                        normalized_opt_methods = {}
                        for category_name, category_data in opt_methods.items():
                            # Rename weight_quantization to quantization
                            if category_name == "weight_quantization":
                                category_name = "quantization"
                            
                            # Check if category_data has "methods" directly (flat structure)
                            if isinstance(category_data, dict) and "methods" in category_data:
                                # Check if methods is a list (could be strings or objects)
                                methods = category_data.get("methods", [])
                                if isinstance(methods, list) and len(methods) > 0:
                                    # If first method is a string, this is the flat structure
                                    # Wrap it in a default subcategory
                                    if isinstance(methods[0], str):
                                        # Create a default subcategory name based on category
                                        subcategory_name = "default"
                                        if category_name == "quantization":
                                            subcategory_name = "weight_only"
                                        elif category_name == "fusion":
                                            subcategory_name = "layer_fusion"
                                        elif category_name == "pruning":
                                            subcategory_name = "structured"
                                        elif category_name == "structural":
                                            subcategory_name = "topology"
                                        
                                        # Wrap the category data in a subcategory
                                        normalized_opt_methods[category_name] = {
                                            subcategory_name: category_data
                                        }
                                    else:
                                        # Methods are already objects, but structure might still be flat
                                        # Wrap in default subcategory
                                        subcategory_name = "default"
                                        normalized_opt_methods[category_name] = {
                                            subcategory_name: category_data
                                        }
                                else:
                                    # Empty methods or not a list, wrap in default subcategory
                                    normalized_opt_methods[category_name] = {
                                        "default": category_data
                                    }
                            else:
                                # Already has subcategories, just rename if needed
                                normalized_opt_methods[category_name] = category_data
                        
                        # Update the optimization_methods with normalized structure
                        value["optimization_methods"] = normalized_opt_methods
                    
                    # Recursively process the rest of the model data
                    normalized[key] = {k: self._normalize_category_names(v) if isinstance(v, dict) else v 
                                      for k, v in value.items()}
                else:
                    # Recursively process nested dictionaries
                    normalized[key] = self._normalize_category_names(value)
            else:
                normalized[key] = value
        
        return normalized
