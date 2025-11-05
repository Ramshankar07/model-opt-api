from __future__ import annotations

from typing import Dict, Any


class ValidationService:
    def validate_tree(self, tree: Dict[str, Any]) -> None:
        # Minimal stub validation
        if "nodes" not in tree or "edges" not in tree:
            raise ValueError("Invalid tree format: missing 'nodes' or 'edges'")

