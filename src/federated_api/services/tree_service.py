from __future__ import annotations

from typing import Any, Dict, List, Optional

from federated_api.database import tree_repository
from federated_api.services.validation_service import ValidationService


class TreeService:
    def __init__(self):
        self.validation_service = ValidationService()

    @staticmethod
    def _update_metadata(tree: Dict[str, Any]) -> None:
        """Update metadata fields (node_count, edge_count) to match actual counts."""
        tree.setdefault("meta", {})
        tree["meta"]["node_count"] = len(tree.get("nodes", []))
        tree["meta"]["edge_count"] = len(tree.get("edges", []))

    @staticmethod
    def _get_node_index(tree: Dict[str, Any], node_id: str) -> int:
        """Get the index of a node by ID. Returns -1 if not found."""
        for i, node in enumerate(tree.get("nodes", [])):
            if node.get("id") == node_id:
                return i
        return -1

    @staticmethod
    def _get_node_by_id(tree: Dict[str, Any], node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID. Returns None if not found."""
        index = TreeService._get_node_index(tree, node_id)
        if index >= 0:
            return tree.get("nodes", [])[index]
        return None

    @staticmethod
    def cleanup_orphaned_edges(tree: Dict[str, Any]) -> int:
        """Remove edges that reference non-existent nodes. Returns number of edges removed."""
        node_ids = {node.get("id") for node in tree.get("nodes", []) if node.get("id")}
        edges = tree.get("edges", [])
        original_count = len(edges)
        
        tree["edges"] = [
            e for e in edges
            if e.get("source") in node_ids and e.get("target") in node_ids
        ]
        
        removed_count = original_count - len(tree["edges"])
        return removed_count

    def clone(self, architecture: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        tree = {
            "nodes": [],
            "edges": [],
            "meta": {"architecture": architecture, "constraints": constraints},
        }
        # Validate the tree (even though it's empty, ensures structure is correct)
        self.validation_service.validate_tree(tree)
        self._update_metadata(tree)
        tree_id = tree_repository.create(tree)
        tree = tree_repository.get(tree_id) or {"nodes": [], "edges": [], "meta": {}}
        return {"tree_id": tree_id, "tree": tree}

    def expand(self, tree_id: str, architecture: str) -> List[Dict[str, Any]]:
        # Stub expansion: return empty list for now
        return []

    def add_node_to_tree(self, tree_id: str, node_data: Dict[str, Any]) -> None:
        """Add a node to a tree with validation."""
        tree = tree_repository.get(tree_id)
        if tree is None:
            raise ValueError(f"Tree not found: {tree_id}")
        
        # Get existing node IDs for uniqueness check
        existing_node_ids = {n.get("id") for n in tree.get("nodes", []) if n.get("id")}
        self.validation_service.validate_node(node_data, existing_node_ids)
        
        tree.setdefault("nodes", []).append(node_data)
        self._update_metadata(tree)
        tree_repository.upsert(tree_id, tree)

    def remove_node_from_tree(self, tree_id: str, node_id: str) -> bool:
        """Remove a node from a tree and clean up its edges. Returns True if removed."""
        tree = tree_repository.get(tree_id)
        if tree is None:
            raise ValueError(f"Tree not found: {tree_id}")
        
        before = len(tree.get("nodes", []))
        tree["nodes"] = [n for n in tree.get("nodes", []) if n.get("id") != node_id]
        after = len(tree.get("nodes", []))
        
        if before == after:
            return False
        
        # Remove all edges referencing the deleted node
        tree["edges"] = [
            e for e in tree.get("edges", [])
            if e.get("source") != node_id and e.get("target") != node_id
        ]
        
        self._update_metadata(tree)
        tree_repository.upsert(tree_id, tree)
        return True

    def add_edge_to_tree(self, tree_id: str, edge_data: Dict[str, Any]) -> None:
        """Add an edge to a tree with validation."""
        tree = tree_repository.get(tree_id)
        if tree is None:
            raise ValueError(f"Tree not found: {tree_id}")
        
        self.validation_service.validate_edge_for_tree(edge_data, tree)
        tree.setdefault("edges", []).append(edge_data)
        self._update_metadata(tree)
        tree_repository.upsert(tree_id, tree)

    def remove_edge_from_tree(self, tree_id: str, source: str, target: str) -> bool:
        """Remove an edge from a tree. Returns True if removed."""
        tree = tree_repository.get(tree_id)
        if tree is None:
            raise ValueError(f"Tree not found: {tree_id}")
        
        edges = tree.get("edges", [])
        original_count = len(edges)
        tree["edges"] = [
            e for e in edges
            if not (e.get("source") == source and e.get("target") == target)
        ]
        
        removed = len(edges) != len(tree["edges"])
        if removed:
            self._update_metadata(tree)
            tree_repository.upsert(tree_id, tree)
        return removed

