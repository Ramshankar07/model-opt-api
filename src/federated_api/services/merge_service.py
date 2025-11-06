from __future__ import annotations

from typing import Any, Dict, List

from federated_api.database import tree_repository


class MergeService:
    def merge_changes(self, tree_id: str, local_taxonomy: Dict[str, Any], changes: Dict[str, Any]) -> Dict[str, Any]:
        """Merge changes into taxonomy. Stub implementation for now."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        
        # Stub merge: accept changes without conflict handling for now
        return {"status": "merged", "conflicts": []}

    def get_conflicts(self, tree_id: str) -> List[Dict[str, Any]]:
        """Get conflicts for a taxonomy. Stub implementation."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        
        # Stub: no conflicts
        return []

    def resolve_conflict(self, tree_id: str, conflict_id: str, resolution: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a conflict. Stub implementation."""
        taxonomy = tree_repository.get(tree_id)
        if taxonomy is None:
            raise ValueError(f"Taxonomy not found: {tree_id}")
        
        # Stub: pretend the conflict is resolved
        return {"status": "resolved", "conflict_id": conflict_id}
