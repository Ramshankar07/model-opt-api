from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OptimizationMethod(BaseModel):
    """Standardized structure for all optimization methods."""
    name: str
    paper_title: str
    paper_link: str
    venue: str
    year: int
    authors: str
    effectiveness: str  # 'high' | 'medium' | 'low'
    accuracy_impact: str  # 'zero' | 'minimal' | 'moderate'
    
    # Optional fields
    bit_widths: List[str] = Field(default_factory=list)
    granularity: Optional[str] = None
    compression_ratio: Optional[str] = None
    speedup: Optional[str] = None
    notes: str = Field(default="")


class OptimizationMethods(BaseModel):
    """Container for optimization methods by category and subcategory."""
    quantization: Dict[str, Dict[str, List[OptimizationMethod]]] = Field(default_factory=dict)
    fusion: Dict[str, Dict[str, List[OptimizationMethod]]] = Field(default_factory=dict)
    pruning: Dict[str, Dict[str, List[OptimizationMethod]]] = Field(default_factory=dict)
    structural: Dict[str, Dict[str, List[OptimizationMethod]]] = Field(default_factory=dict)


class ModelCharacteristics(BaseModel):
    """Characteristics of a specific model."""
    architecture_type: Optional[str] = None  # 'cnn' | 'transformer' | 'hybrid' | 'multimodal'
    key_components: List[str] = Field(default_factory=list)
    has_batch_norm: Optional[bool] = None
    has_layer_norm: Optional[bool] = None
    has_attention: Optional[bool] = None
    has_skip_connections: Optional[bool] = None
    optimization_challenges: List[str] = Field(default_factory=list)


class CalibrationFreeStatus(BaseModel):
    """Status information about calibration-free methods availability."""
    available_methods: Optional[str] = None  # 'abundant' | 'moderate' | 'minimal'
    research_gap: Optional[bool] = None
    recommended_approach: Optional[str] = None


class SpecificModel(BaseModel):
    """Represents a specific model with its optimization methods and characteristics."""
    optimization_methods: Dict[str, Any] = Field(default_factory=dict)
    model_characteristics: Dict[str, Any] = Field(default_factory=dict)
    calibration_free_status: Dict[str, Any] = Field(default_factory=dict)


class OptimizationTaxonomy(BaseModel):
    """Main taxonomy structure matching CALIBRATION_FREE_SCHEMA."""
    data: Dict[str, Any] = Field(default_factory=dict)  # model_family -> subcategory -> specific_model
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def get_path(self, path: str) -> Optional[Any]:
        """Get data at a specific path (e.g., 'model_family/subcategory/specific_model')."""
        parts = path.split('/')
        current = self.data
        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current

    def set_path(self, path: str, value: Any) -> None:
        """Set data at a specific path."""
        parts = path.split('/')
        current = self.data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value


class CloneRequest(BaseModel):
    architecture: str
    constraints: Dict[str, Any] = Field(default_factory=dict)


class CloneResponse(BaseModel):
    tree_id: str
    taxonomy: OptimizationTaxonomy


class ExpandRequest(BaseModel):
    architecture: str
    path: Optional[str] = None  # Optional path to expand


class ExpandResponse(BaseModel):
    expanded: bool
    path: Optional[str] = None


class SyncRequest(BaseModel):
    local_taxonomy: OptimizationTaxonomy
    changes: Dict[str, Any] = Field(default_factory=dict)


class MergeRequest(BaseModel):
    local_taxonomy: OptimizationTaxonomy
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
