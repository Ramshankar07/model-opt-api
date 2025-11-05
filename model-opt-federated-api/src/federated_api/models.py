from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Node(BaseModel):
    id: str
    label: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class Edge(BaseModel):
    source: str
    target: str
    relation: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class Tree(BaseModel):
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)


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

