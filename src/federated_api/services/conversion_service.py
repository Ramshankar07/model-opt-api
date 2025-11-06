from __future__ import annotations

from typing import Any, Dict, List, Optional


class ConversionService:
    """Service for converting between schema format and legacy graph format."""
    
    @staticmethod
    def schema_to_legacy(taxonomy: Dict[str, Any]) -> Dict[str, Any]:
        """Convert schema format to legacy graph format, preserving relationships as edges with weights."""
        legacy = {
            "nodes": {},
            "edges": [],
            "metadata": {}
        }
        
        # Extract relationships and convert to edges
        relationships = taxonomy.get("relationships", [])
        for rel in relationships:
            if isinstance(rel, dict):
                methods = rel.get("methods", [])
                weights = rel.get("weights", {})
                
                # Create edges from relationships
                # For relationships with 2 methods, create a single edge
                if len(methods) >= 2:
                    edge = {
                        "parent": methods[0],
                        "child": methods[1],
                        "data": {
                            "weights": weights
                        }
                    }
                    # Add relationship metadata
                    if rel.get("relationship_type"):
                        edge["data"]["relationship_type"] = rel["relationship_type"]
                    if rel.get("metadata"):
                        edge["data"]["metadata"] = rel["metadata"]
                    
                    legacy["edges"].append(edge)
                
                # For relationships with more than 2 methods, create multiple edges
                # (chain them together)
                for i in range(len(methods) - 1):
                    edge = {
                        "parent": methods[i],
                        "child": methods[i + 1],
                        "data": {
                            "weights": weights.copy() if weights else {}
                        }
                    }
                    legacy["edges"].append(edge)
        
        # Count metadata
        legacy["metadata"] = {
            "node_count": len(legacy["nodes"]),
            "edge_count": len(legacy["edges"])
        }
        
        return legacy
    
    @staticmethod
    def legacy_to_schema(legacy: Dict[str, Any]) -> Dict[str, Any]:
        """Convert legacy graph format to schema format, preserving edge weights as relationships."""
        taxonomy = {}
        relationships = []
        
        # Extract edges and convert to relationships
        edges = legacy.get("edges", [])
        for edge in edges:
            source = edge.get("parent") or edge.get("source")
            target = edge.get("child") or edge.get("target")
            edge_data = edge.get("data", {})
            weights = edge_data.get("weights", {})
            
            if source and target:
                relationship = {
                    "methods": [source, target],
                    "weights": weights,
                    "relationship_type": edge_data.get("relationship_type", "legacy_edge"),
                    "metadata": edge_data.get("metadata", {})
                }
                relationships.append(relationship)
        
        # Add relationships to taxonomy
        if relationships:
            taxonomy["relationships"] = relationships
        
        return taxonomy
    
    @staticmethod
    def extract_weights_from_taxonomy(taxonomy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all weight data from a taxonomy structure."""
        weights_list = []
        
        # Extract from top-level relationships
        relationships = taxonomy.get("relationships", [])
        for rel in relationships:
            if isinstance(rel, dict) and "weights" in rel:
                weights_list.append({
                    "source": "relationships",
                    "relationship_id": rel.get("id"),
                    "methods": rel.get("methods", []),
                    "weights": rel["weights"]
                })
        
        # Extract from model-level relationships
        # Navigate through model_family -> subcategory -> specific_model
        for model_family, subcategories in taxonomy.items():
            if model_family == "relationships" or not isinstance(subcategories, dict):
                continue
            
            for subcategory, models in subcategories.items():
                if not isinstance(models, dict):
                    continue
                
                for specific_model, model_data in models.items():
                    if not isinstance(model_data, dict):
                        continue
                    
                    model_rels = model_data.get("relationships", {})
                    if isinstance(model_rels, dict):
                        method_combinations = model_rels.get("method_combinations", [])
                        for combo in method_combinations:
                            if isinstance(combo, dict) and "weights" in combo:
                                weights_list.append({
                                    "source": "model_relationships",
                                    "path": f"{model_family}/{subcategory}/{specific_model}",
                                    "methods": combo.get("methods", []),
                                    "weights": combo["weights"]
                                })
        
        return weights_list

