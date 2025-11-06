from __future__ import annotations

from typing import Any, Dict, List, Optional
from federated_api.schema import CALIBRATION_FREE_SCHEMA


class ValidationService:
    def validate_schema_structure(self, taxonomy: Dict[str, Any]) -> None:
        """Validate that taxonomy matches CALIBRATION_FREE_SCHEMA structure."""
        if not isinstance(taxonomy, dict):
            raise ValueError("Taxonomy must be a dictionary")
        
        # Validate top-level structure (model_family -> subcategory -> specific_model)
        for model_family, subcategories in taxonomy.items():
            if not isinstance(subcategories, dict):
                raise ValueError(f"Subcategories for '{model_family}' must be a dictionary")
            
            for subcategory, models in subcategories.items():
                if not isinstance(models, dict):
                    raise ValueError(f"Models for '{model_family}/{subcategory}' must be a dictionary")
                
                for specific_model, model_data in models.items():
                    if not isinstance(model_data, dict):
                        raise ValueError(f"Model data for '{model_family}/{subcategory}/{specific_model}' must be a dictionary")
                    
                    # Validate required top-level keys
                    required_keys = ['optimization_methods']
                    for key in required_keys:
                        if key not in model_data:
                            raise ValueError(f"Missing required key '{key}' in '{model_family}/{subcategory}/{specific_model}'")
                    
                    # Validate optimization_methods structure
                    opt_methods = model_data.get('optimization_methods', {})
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
                            
                            # Validate each method
                            for i, method in enumerate(methods):
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
        """Validate that a method follows the standardized structure."""
        if not isinstance(method, dict):
            raise ValueError(f"Method must be a dictionary{(' at ' + context) if context else ''}")
        
        # Required fields
        required_fields = [
            'name', 'paper_title', 'paper_link', 'venue', 
            'year', 'authors', 'effectiveness', 'accuracy_impact'
        ]
        
        for field in required_fields:
            if field not in method:
                raise ValueError(f"Method missing required field '{field}'{(' at ' + context) if context else ''}")
        
        # Validate field types
        if not isinstance(method['name'], str) or not method['name'].strip():
            raise ValueError(f"Method 'name' must be a non-empty string{(' at ' + context) if context else ''}")
        
        if not isinstance(method['paper_title'], str) or not method['paper_title'].strip():
            raise ValueError(f"Method 'paper_title' must be a non-empty string{(' at ' + context) if context else ''}")
        
        if not isinstance(method['paper_link'], str) or not method['paper_link'].strip():
            raise ValueError(f"Method 'paper_link' must be a non-empty string{(' at ' + context) if context else ''}")
        
        if not isinstance(method['venue'], str) or not method['venue'].strip():
            raise ValueError(f"Method 'venue' must be a non-empty string{(' at ' + context) if context else ''}")
        
        if not isinstance(method['year'], int) or method['year'] < 1900 or method['year'] > 2100:
            raise ValueError(f"Method 'year' must be an integer between 1900 and 2100{(' at ' + context) if context else ''}")
        
        if not isinstance(method['authors'], str) or not method['authors'].strip():
            raise ValueError(f"Method 'authors' must be a non-empty string{(' at ' + context) if context else ''}")
        
        valid_effectiveness = ['high', 'medium', 'low']
        if method['effectiveness'] not in valid_effectiveness:
            raise ValueError(f"Method 'effectiveness' must be one of {valid_effectiveness}{(' at ' + context) if context else ''}")
        
        valid_accuracy_impact = ['zero', 'minimal', 'moderate']
        if method['accuracy_impact'] not in valid_accuracy_impact:
            raise ValueError(f"Method 'accuracy_impact' must be one of {valid_accuracy_impact}{(' at ' + context) if context else ''}")
        
        # Optional fields validation
        if 'bit_widths' in method:
            if not isinstance(method['bit_widths'], list):
                raise ValueError(f"Method 'bit_widths' must be a list{(' at ' + context) if context else ''}")
        
        if 'granularity' in method and method['granularity'] is not None:
            if not isinstance(method['granularity'], str):
                raise ValueError(f"Method 'granularity' must be a string or None{(' at ' + context) if context else ''}")
        
        if 'compression_ratio' in method and method['compression_ratio'] is not None:
            if not isinstance(method['compression_ratio'], str):
                raise ValueError(f"Method 'compression_ratio' must be a string or None{(' at ' + context) if context else ''}")
        
        if 'speedup' in method and method['speedup'] is not None:
            if not isinstance(method['speedup'], str):
                raise ValueError(f"Method 'speedup' must be a string or None{(' at ' + context) if context else ''}")
        
        if 'notes' in method:
            if not isinstance(method['notes'], str):
                raise ValueError(f"Method 'notes' must be a string{(' at ' + context) if context else ''}")

    def validate_method_data(self, method_data: Dict[str, Any]) -> None:
        """Validate method data matches standardized structure."""
        self.validate_optimization_method(method_data)
