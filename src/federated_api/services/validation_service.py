from __future__ import annotations

import warnings
from typing import Any, Dict, List, Optional
from federated_api.schema import CALIBRATION_FREE_SCHEMA


class ValidationService:
    def validate_schema_structure(self, taxonomy: Dict[str, Any]) -> None:
        """Validate that taxonomy matches CALIBRATION_FREE_SCHEMA structure."""
        if not isinstance(taxonomy, dict):
            raise ValueError("Taxonomy must be a dictionary")
        
        # Allow empty taxonomy
        if not taxonomy:
            return
        
        # Validate relationships if present (optional top-level field)
        if 'relationships' in taxonomy:
            relationships = taxonomy.get('relationships')
            if not isinstance(relationships, list):
                raise ValueError("'relationships' must be a list")
            for rel in relationships:
                self.validate_relationship(rel, taxonomy, skip_path_check=True)  # Skip path check for flexibility
        
        # Validate top-level structure (model_family -> subcategory -> specific_model)
        # Skip 'relationships' as it's a top-level optional field
        for model_family, subcategories in taxonomy.items():
            if model_family == 'relationships':
                continue  # Skip relationships, already validated above
            if not isinstance(subcategories, dict):
                raise ValueError(f"Subcategories for '{model_family}' must be a dictionary")
            
            for subcategory, models in subcategories.items():
                if not isinstance(models, dict):
                    # Some entries may have lists or other structures (e.g., optimization_effectiveness_summary)
                    # Skip validation for non-dict structures
                    continue
                
                for specific_model, model_data in models.items():
                    if not isinstance(model_data, dict):
                        # Some entries may have lists or other structures
                        # Skip validation for non-dict structures
                        continue
                    
                    # Validate optimization_methods structure if present
                    # (Some entries like cross_architecture_frameworks may have different structures)
                    opt_methods = model_data.get('optimization_methods')
                    if opt_methods is None:
                        # Skip validation if optimization_methods is missing (may be a framework entry)
                        continue
                    
                    if not isinstance(opt_methods, dict):
                        raise ValueError(f"optimization_methods must be a dictionary")
                    
                    # Validate categories
                    valid_categories = ['quantization', 'fusion', 'pruning', 'structural']
                    for category in opt_methods.keys():
                        if category not in valid_categories:
                            raise ValueError(f"Invalid category '{category}'. Must be one of {valid_categories}")
                    
                    # Validate methods in each category
                    for category, subcategories_dict in opt_methods.items():
                        if not isinstance(subcategories_dict, dict):
                            raise ValueError(f"Category '{category}' must contain a dictionary of subcategories")
                        
                        for subcat_name, subcat_data in subcategories_dict.items():
                            if not isinstance(subcat_data, dict):
                                raise ValueError(f"Subcategory '{subcat_name}' in '{category}' must be a dictionary")
                            
                            if 'methods' not in subcat_data:
                                raise ValueError(f"Subcategory '{subcat_name}' in '{category}' must have a 'methods' key")
                            
                            methods = subcat_data['methods']
                            if not isinstance(methods, list):
                                raise ValueError(f"'methods' in '{category}/{subcat_name}' must be a list")
                            
                            # Validate each method (skip if methods are strings, as in base_tree.json)
                            for i, method in enumerate(methods):
                                # If method is a string, skip detailed validation (legacy format)
                                if isinstance(method, str):
                                    continue
                                # Otherwise, validate as a full method object
                                self.validate_optimization_method(method, f"{category}/{subcat_name}/methods[{i}]")

    def validate_path(self, path: str) -> None:
        """Validate path format (model_family/subcategory/specific_model or deeper)."""
        if not path or not isinstance(path, str):
            raise ValueError("Path must be a non-empty string")
        
        parts = path.split('/')
        if len(parts) < 3:
            raise ValueError("Path must have at least 3 parts: model_family/subcategory/specific_model")
        
        # Path parts should not be empty
        for part in parts:
            if not part.strip():
                raise ValueError("Path parts cannot be empty")

    def validate_optimization_method(self, method: Dict[str, Any], context: str = "") -> None:
        """Validate that a method follows the standardized structure.
        
        Supports both old format (for backward compatibility) and new ideal format.
        Logs warnings for old format during transition period.
        """
        if not isinstance(method, dict):
            raise ValueError(f"Method must be a dictionary{(' at ' + context) if context else ''}")
        
        # Detect old format
        is_old_format = (
            'techniques' not in method or
            not method.get('techniques') or
            'performance' not in method or
            not isinstance(method.get('performance'), dict) or
            'validation' not in method or
            not isinstance(method.get('validation'), dict) or
            isinstance(method.get('architecture'), str) or
            'paper' not in method or
            not isinstance(method.get('paper'), dict)
        )
        
        if is_old_format:
            warnings.warn(
                f"Method uses old schema format{(' at ' + context) if context else ''}. "
                "Consider migrating to ideal structure with techniques, performance, validation, architecture, and paper fields.",
                UserWarning,
                stacklevel=2
            )
        
        # Required fields (name is always required, others optional during transition)
        if 'name' not in method:
            raise ValueError(f"Method missing required field 'name'{(' at ' + context) if context else ''}")
        
        if not isinstance(method['name'], str) or not method['name'].strip():
            raise ValueError(f"Method 'name' must be a non-empty string{(' at ' + context) if context else ''}")
        
        # Validate effectiveness if present
        if 'effectiveness' in method:
            valid_effectiveness = ['high', 'medium', 'low']
            if method['effectiveness'] not in valid_effectiveness:
                raise ValueError(f"Method 'effectiveness' must be one of {valid_effectiveness}{(' at ' + context) if context else ''}")
        
        # Validate accuracy_impact if present
        if 'accuracy_impact' in method:
            valid_accuracy_impact = ['zero', 'minimal', 'moderate']
            if method['accuracy_impact'] not in valid_accuracy_impact:
                raise ValueError(f"Method 'accuracy_impact' must be one of {valid_accuracy_impact}{(' at ' + context) if context else ''}")
        
        # Validate new ideal structure fields if present
        if 'techniques' in method:
            if not isinstance(method['techniques'], list):
                raise ValueError(f"Method 'techniques' must be a list{(' at ' + context) if context else ''}")
        
        if 'performance' in method:
            if not isinstance(method['performance'], dict):
                raise ValueError(f"Method 'performance' must be a dictionary{(' at ' + context) if context else ''}")
            # Validate performance fields
            perf = method['performance']
            for key in ['latency_speedup', 'compression_ratio', 'accuracy_retention']:
                if key in perf and not isinstance(perf[key], (int, float)):
                    raise ValueError(f"Method 'performance.{key}' must be a number{(' at ' + context) if context else ''}")
        
        if 'validation' in method:
            if not isinstance(method['validation'], dict):
                raise ValueError(f"Method 'validation' must be a dictionary{(' at ' + context) if context else ''}")
            # Validate validation fields
            val = method['validation']
            if 'confidence' in val and not isinstance(val['confidence'], (int, float)):
                raise ValueError(f"Method 'validation.confidence' must be a number{(' at ' + context) if context else ''}")
            if 'sample_count' in val and not isinstance(val['sample_count'], int):
                raise ValueError(f"Method 'validation.sample_count' must be an integer{(' at ' + context) if context else ''}")
        
        if 'architecture' in method:
            # Architecture can be string (legacy) or dict (new)
            arch = method['architecture']
            if not isinstance(arch, (str, dict)):
                raise ValueError(f"Method 'architecture' must be a string or dictionary{(' at ' + context) if context else ''}")
            if isinstance(arch, dict):
                if 'family' not in arch or 'variant' not in arch:
                    raise ValueError(f"Method 'architecture' dict must have 'family' and 'variant' keys{(' at ' + context) if context else ''}")
        
        if 'paper' in method:
            if not isinstance(method['paper'], dict):
                raise ValueError(f"Method 'paper' must be a dictionary{(' at ' + context) if context else ''}")
        
        # Validate legacy optional fields
        if 'bit_widths' in method:
            if not isinstance(method['bit_widths'], list):
                raise ValueError(f"Method 'bit_widths' must be a list{(' at ' + context) if context else ''}")
        
        if 'granularity' in method and method['granularity'] is not None:
            if not isinstance(method['granularity'], str):
                raise ValueError(f"Method 'granularity' must be a string or None{(' at ' + context) if context else ''}")
        
        if 'compression_ratio' in method and method['compression_ratio'] is not None:
            if not isinstance(method['compression_ratio'], (str, int, float)):
                raise ValueError(f"Method 'compression_ratio' must be a string or number{(' at ' + context) if context else ''}")
        
        if 'speedup' in method and method['speedup'] is not None:
            if not isinstance(method['speedup'], (str, int, float)):
                raise ValueError(f"Method 'speedup' must be a string or number{(' at ' + context) if context else ''}")
        
        if 'notes' in method:
            if not isinstance(method['notes'], str):
                raise ValueError(f"Method 'notes' must be a string{(' at ' + context) if context else ''}")
        
        # Validate paper fields if present (legacy format)
        if 'paper_title' in method and method['paper_title'] is not None:
            if not isinstance(method['paper_title'], str):
                raise ValueError(f"Method 'paper_title' must be a string{(' at ' + context) if context else ''}")
        
        if 'paper_link' in method and method['paper_link'] is not None:
            if not isinstance(method['paper_link'], str):
                raise ValueError(f"Method 'paper_link' must be a string{(' at ' + context) if context else ''}")
        
        if 'venue' in method and method['venue'] is not None:
            if not isinstance(method['venue'], str):
                raise ValueError(f"Method 'venue' must be a string{(' at ' + context) if context else ''}")
        
        if 'year' in method and method['year'] is not None:
            if not isinstance(method['year'], int) or method['year'] < 1900 or method['year'] > 2100:
                raise ValueError(f"Method 'year' must be an integer between 1900 and 2100{(' at ' + context) if context else ''}")
        
        if 'authors' in method and method['authors'] is not None:
            if not isinstance(method['authors'], (str, list)):
                raise ValueError(f"Method 'authors' must be a string or list{(' at ' + context) if context else ''}")

    def validate_method_data(self, method_data: Dict[str, Any]) -> None:
        """Validate method data matches standardized structure."""
        self.validate_optimization_method(method_data)

    def validate_relationship(
        self, 
        relationship: Dict[str, Any], 
        taxonomy: Dict[str, Any],
        skip_path_check: bool = False
    ) -> None:
        """Validate relationship structure and that paths exist."""
        if not isinstance(relationship, dict):
            raise ValueError("Relationship must be a dictionary")
        
        # Required fields
        if 'methods' not in relationship:
            raise ValueError("Relationship must have 'methods' field")
        
        methods = relationship.get('methods', [])
        if not isinstance(methods, list):
            raise ValueError("Relationship 'methods' must be a list")
        
        if len(methods) < 2:
            raise ValueError("Relationship must have at least 2 methods")
        
        # Validate each method path exists (if not skipping)
        if not skip_path_check:
            for method_path in methods:
                if not isinstance(method_path, str):
                    raise ValueError(f"Method path must be a string: {method_path}")
                # Validate path format (basic check)
                if not method_path.strip():
                    raise ValueError("Method path cannot be empty")
        
        # Validate weights structure (optional)
        if 'weights' in relationship:
            weights = relationship['weights']
            if not isinstance(weights, dict):
                raise ValueError("Relationship 'weights' must be a dictionary")
            # Validate common weight fields
            if 'success_probability' in weights:
                prob = weights['success_probability']
                if not isinstance(prob, (int, float)) or prob < 0 or prob > 1:
                    raise ValueError("success_probability must be a number between 0 and 1")
            if 'confidence' in weights:
                conf = weights['confidence']
                if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
                    raise ValueError("confidence must be a number between 0 and 1")
            if 'sample_count' in weights:
                count = weights['sample_count']
                if not isinstance(count, int) or count < 0:
                    raise ValueError("sample_count must be a non-negative integer")
        
        # Validate relationship_type (optional)
        if 'relationship_type' in relationship:
            rel_type = relationship['relationship_type']
            if rel_type is not None and not isinstance(rel_type, str):
                raise ValueError("relationship_type must be a string or None")
        
        # Validate metadata (optional)
        if 'metadata' in relationship:
            if not isinstance(relationship['metadata'], dict):
                raise ValueError("Relationship 'metadata' must be a dictionary")
            
            # Validate enhanced metadata structure if present
            metadata = relationship['metadata']
            if 'constraints' in metadata:
                if not isinstance(metadata['constraints'], dict):
                    raise ValueError("Relationship 'metadata.constraints' must be a dictionary")
                constraints = metadata['constraints']
                if 'order' in constraints and constraints['order'] is not None:
                    if not isinstance(constraints['order'], list):
                        raise ValueError("Relationship 'metadata.constraints.order' must be a list or None")
                if 'min_accuracy_retention' in constraints and constraints['min_accuracy_retention'] is not None:
                    if not isinstance(constraints['min_accuracy_retention'], (int, float)):
                        raise ValueError("Relationship 'metadata.constraints.min_accuracy_retention' must be a number or None")
            
            if 'tested_models' in metadata:
                if not isinstance(metadata['tested_models'], list):
                    raise ValueError("Relationship 'metadata.tested_models' must be a list")
            
            if 'tested_datasets' in metadata:
                if not isinstance(metadata['tested_datasets'], list):
                    raise ValueError("Relationship 'metadata.tested_datasets' must be a list")
