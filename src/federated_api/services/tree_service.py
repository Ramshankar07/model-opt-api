from __future__ import annotations

from typing import Any, Dict, List

from federated_api.database import tree_repository


class TreeService:
    def clone(self, architecture: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        tree_id = tree_repository.create({
            "nodes": [],
            "edges": [],
            "meta": {"architecture": architecture, "constraints": constraints},
        })
        tree = tree_repository.get(tree_id) or {"nodes": [], "edges": [], "meta": {}}
        return {"tree_id": tree_id, "tree": tree}

    def expand(self, tree_id: str, architecture: str) -> List[Dict[str, Any]]:
        # Stub expansion: return empty list for now
        return []

