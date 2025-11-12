from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OptimizationMethod(BaseModel):
    """Standardized structure for all optimization methods.
    
    Supports both legacy format (for backward compatibility) and ideal format.
    """
    name: str
    paper_title: Optional[str] = None  # Optional for transition period
    paper_link: Optional[str] = None
    venue: Optional[str] = None
    year: Optional[int] = None
    authors: Optional[str] = None
    effectiveness: str = "medium"  # 'high' | 'medium' | 'low'
    accuracy_impact: str = "minimal"  # 'zero' | 'minimal' | 'moderate'
    
    # New ideal schema fields
    techniques: List[str] = Field(default_factory=list)  # Explicit techniques array
    method_name: Optional[str] = None  # Alias for name, for backward compatibility
    
    # Performance structure (consistent dict format)
    performance: Dict[str, Any] = Field(default_factory=lambda: {
        'latency_speedup': 1.0,
        'compression_ratio': 1.0,
        'accuracy_retention': 1.0
    })
    
    # Validation structure (consistent dict format)
    validation: Dict[str, Any] = Field(default_factory=lambda: {
        'confidence': 0.5,
        'sample_count': 0,
        'validators': 0,
        'last_validated': None,
        'validation_method': 'unknown'
    })
    
    # Architecture structure (supports both string and dict for transition)
    architecture: Any = Field(default=None)  # Can be str (legacy) or Dict[str, str] (new)
    architecture_family: Optional[str] = None  # Kept for backward compatibility
    
    # Paper metadata structure
    paper: Dict[str, Any] = Field(default_factory=lambda: {
        'title': '',
        'authors': [],
        'venue': '',
        'year': 0,
        'arxiv_id': '',
        'url': ''
    })
    
    # Legacy optional fields (kept for backward compatibility)
    bit_widths: List[str] = Field(default_factory=list)
    granularity: Optional[str] = None
    compression_ratio: Optional[str] = None  # Legacy, prefer performance.compression_ratio
    speedup: Optional[str] = None  # Legacy, prefer performance.latency_speedup
    confidence: Optional[float] = None  # Legacy, prefer validation.confidence
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


class WeightData(BaseModel):
    """Weight data for relationships (backward compatibility with graph edges)."""
    success_probability: Optional[float] = None
    sample_count: Optional[int] = None
    confidence: Optional[float] = None
    # Allow additional weight fields
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MethodRelationship(BaseModel):
    """Relationship between optimization methods with weights and compatibility metadata."""
    id: str
    methods: List[str]  # List of method paths (e.g., ["quantization/weight_only/methods[0]", ...])
    weights: Dict[str, Any] = Field(default_factory=dict)  # Weight data (success_probability, confidence, etc.)
    relationship_type: Optional[str] = None  # 'compatibility', 'sequence', 'alternative', etc.
    metadata: Dict[str, Any] = Field(default_factory=lambda: {
        'constraints': {
            'order': None,  # Optional ordering constraint
            'min_accuracy_retention': None  # Optional minimum accuracy requirement
        },
        'tested_models': [],  # List of models this relationship was tested on
        'tested_datasets': []  # List of datasets this relationship was tested on
    })


class SpecificModel(BaseModel):
    """Represents a specific model with its optimization methods and characteristics."""
    optimization_methods: Dict[str, Any] = Field(default_factory=dict)
    model_characteristics: Dict[str, Any] = Field(default_factory=dict)
    calibration_free_status: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, Any] = Field(default_factory=dict)  # For backward compatibility with weights


class OptimizationTaxonomy(BaseModel):
    """Main taxonomy structure matching CALIBRATION_FREE_SCHEMA."""
    data: Dict[str, Any] = Field(default_factory=dict)  # model_family -> subcategory -> specific_model
    relationships: List[Dict[str, Any]] = Field(default_factory=list)  # Top-level relationships (optional, as dicts for flexibility)
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
