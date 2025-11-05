from __future__ import annotations

from typing import Any, Dict, List


class MergeService:
    def merge_changes(self, tree_id: str, local_tree: Dict[str, Any], changes: Dict[str, Any]) -> Dict[str, Any]:
        # Stub merge: accept changes without conflict handling for now
        return {"status": "merged", "conflicts": []}

    def get_conflicts(self, tree_id: str) -> List[Dict[str, Any]]:
        # Stub: no conflicts
        return []

    def resolve_conflict(self, tree_id: str, conflict_id: str, resolution: Dict[str, Any]) -> Dict[str, Any]:
        # Stub: pretend the conflict is resolved
        return {"status": "resolved", "conflict_id": conflict_id}

