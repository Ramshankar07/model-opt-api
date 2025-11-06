from __future__ import annotations

from typing import Dict, Any, Set


class ValidationService:
    def validate_tree(self, tree: Dict[str, Any]) -> None:
        """Comprehensive tree validation."""
        if "nodes" not in tree or "edges" not in tree:
            raise ValueError("Invalid tree format: missing 'nodes' or 'edges'")
        
        nodes = tree.get("nodes", [])
        edges = tree.get("edges", [])
        
        # Collect all node IDs
        node_ids: Set[str] = set()
        for node in nodes:
            node_id = node.get("id")
            if not node_id:
                raise ValueError("Invalid node: missing 'id' field")
            if node_id in node_ids:
                raise ValueError(f"Duplicate node ID found: {node_id}")
            node_ids.add(node_id)
        
        # Validate all edges reference existing nodes
        for edge in edges:
            self.validate_edge(edge, node_ids)
    
    def validate_node(self, node: Dict[str, Any], existing_node_ids: Set[str] = None) -> None:
        """Validate a single node."""
        if not isinstance(node, dict):
            raise ValueError("Node must be a dictionary")
        
        node_id = node.get("id")
        if not node_id:
            raise ValueError("Node must have an 'id' field")
        
        if existing_node_ids is not None and node_id in existing_node_ids:
            raise ValueError(f"Duplicate node ID: {node_id}")
    
    def validate_edge(self, edge: Dict[str, Any], node_ids: Set[str]) -> None:
        """Validate a single edge."""
        if not isinstance(edge, dict):
            raise ValueError("Edge must be a dictionary")
        
        source = edge.get("source")
        target = edge.get("target")
        
        if not source:
            raise ValueError("Edge must have a 'source' field")
        if not target:
            raise ValueError("Edge must have a 'target' field")
        
        if source not in node_ids:
            raise ValueError(f"Edge references non-existent source node: {source}")
        if target not in node_ids:
            raise ValueError(f"Edge references non-existent target node: {target}")
        
        # Prevent self-loops (edge from node to itself)
        if source == target:
            raise ValueError(f"Edge cannot have source and target as the same node: {source}")
    
    def validate_edge_for_tree(self, edge: Dict[str, Any], tree: Dict[str, Any]) -> None:
        """Validate an edge against a specific tree's node IDs."""
        node_ids = {node.get("id") for node in tree.get("nodes", []) if node.get("id")}
        self.validate_edge(edge, node_ids)

