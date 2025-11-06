from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Node(BaseModel):
    id: str
    label: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Edge(BaseModel):
    source: str
    target: str
    relation: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class Tree(BaseModel):
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID. Returns None if not found."""
        return next((n for n in self.nodes if n.id == node_id), None)

    def has_node(self, node_id: str) -> bool:
        """Check if a node with the given ID exists."""
        return any(n.id == node_id for n in self.nodes)

    def get_edges_for_node(self, node_id: str) -> List[Edge]:
        """Get all edges connected to a node (as source or target)."""
        return [e for e in self.edges if e.source == node_id or e.target == node_id]

    def get_children(self, node_id: str) -> List[str]:
        """Get child node IDs (nodes that this node points to)."""
        return [e.target for e in self.edges if e.source == node_id]

    def get_parents(self, node_id: str) -> List[str]:
        """Get parent node IDs (nodes that point to this node)."""
        return [e.source for e in self.edges if e.target == node_id]


class CloneRequest(BaseModel):
    architecture: str
    constraints: Dict[str, Any] = Field(default_factory=dict)


class CloneResponse(BaseModel):
    tree_id: str
    tree: Tree


class ExpandRequest(BaseModel):
    architecture: str


class ExpandResponse(BaseModel):
    new_nodes: List[Node] = Field(default_factory=list)


class SyncRequest(BaseModel):
    local_tree: Tree
    changes: Dict[str, Any] = Field(default_factory=dict)


class MergeRequest(BaseModel):
    local_tree: Tree
    changes: Dict[str, Any] = Field(default_factory=dict)


class Conflict(BaseModel):
    id: str
    path: str
    description: str
    local: Any | None = None
    remote: Any | None = None


class ConflictListResponse(BaseModel):
    conflicts: List[Conflict] = Field(default_factory=list)


class ResolveConflictRequest(BaseModel):
    resolution: Dict[str, Any] = Field(default_factory=dict)

