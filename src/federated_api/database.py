from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import uuid4


class TreeRepository:
    """In-memory repository for taxonomy structures. Each taxonomy is a dict following CALIBRATION_FREE_SCHEMA.

    This interface is kept minimal and is intended to be swapped with a
    persistent backend (e.g., MongoDB) in a future iteration without changing
    the services/routes using it.
    """

    def __init__(self) -> None:
        self._trees: Dict[str, Dict[str, Any]] = {}

    def new_id(self) -> str:
        return uuid4().hex

    def upsert(self, tree_id: str, tree: Dict[str, Any]) -> None:
        self._trees[tree_id] = tree

    def create(self, tree: Optional[Dict[str, Any]] = None) -> str:
        tree_id = self.new_id()
        self._trees[tree_id] = tree or {}
        return tree_id

    def get(self, tree_id: str) -> Optional[Dict[str, Any]]:
        return self._trees.get(tree_id)

    def delete(self, tree_id: str) -> bool:
        return self._trees.pop(tree_id, None) is not None

    def exists(self, tree_id: str) -> bool:
        return tree_id in self._trees


# Singleton-ish in-memory store for the app instance
tree_repository = TreeRepository()


# Future backends (skeletons)
class MongoTreeRepository:
    """Placeholder for a MongoDB-backed implementation."""

    def __init__(self, uri: str):
        self.uri = uri

    # Define the same methods as TreeRepository in the future
    # def upsert(...): ...
    # def create(...): ...
    # def get(...): ...
    # def delete(...): ...
    # def exists(...): ...


class RedisCache:
    """Placeholder for a Redis cache helper."""

    def __init__(self, uri: str):
        self.uri = uri

