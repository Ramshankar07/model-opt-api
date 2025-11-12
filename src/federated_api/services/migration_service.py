from __future__ import annotations

import re
import warnings
from typing import Any, Dict, List, Optional

# Technique mapping table with explicit mappings, patterns, and fallback logic
TECHNIQUE_MAPPING: Dict[str, List[str]] = {
    # Explicit mappings for common methods
    "Conv-BN Fusion": ["fuse_layers"],
    "Conv-ReLU Fusion": ["fuse_layers"],
    "Graph Fusion (Conv+BN+ReLU)": ["fuse_layers"],
    "Residual Connection Fusion": ["fuse_layers"],
    "Layer Fusion": ["fuse_layers"],
    "Depthwise-Pointwise Fusion": ["fuse_layers"],
    "Inverted Residual Fusion": ["fuse_layers"],
    "Sequential Layer Fusion": ["fuse_layers"],
    "LayerNorm Fusion": ["fuse_layers"],
    "QKV Projection Fusion": ["fuse_layers"],
    "MLP Fusion": ["fuse_layers"],
    "Window Partition Fusion": ["fuse_layers"],
    "Patch Merging Fusion": ["fuse_layers"],
    "Encoder-Decoder Fusion": ["fuse_layers"],
    "Multi-scale Feature Fusion": ["fuse_layers"],
    "Skip Connection Fusion": ["fuse_layers"],
    "Upsampling Layer Fusion": ["fuse_layers"],
    "ASPP Module Fusion": ["fuse_layers"],
    "Decoder Fusion": ["fuse_layers"],
    "Skip Layer Fusion": ["fuse_layers"],
    "Multi-Modal Feature Fusion": ["fuse_layers"],
    "Conv-BN Fusion (Backbone)": ["fuse_layers"],
    "Conv-BN Fusion (Neck)": ["fuse_layers"],
    "Feature Fusion Layer Optimization": ["fuse_layers"],
    "Path Aggregation Fusion": ["fuse_layers"],
    "Conv-BN Fusion (Encoder/Decoder)": ["fuse_layers"],
    "Skip Connection Fusion": ["fuse_layers"],
    "Upsampling Fusion": ["fuse_layers"],
    "Conv-BN Fusion (Vision Encoder)": ["fuse_layers"],
    "Projection Layer Fusion": ["fuse_layers"],
    "Conv-BN Fusion (CNN Blocks)": ["fuse_layers"],
    "MBConv Fusion": ["fuse_layers"],
    "Stage Transition Fusion": ["fuse_layers"],
    "Conv-BN Fusion (MobileNet Blocks)": ["fuse_layers"],
    "Transformer-Conv Transition Fusion": ["fuse_layers"],
    "Convolutional Projection Fusion": ["fuse_layers"],
    "Hierarchical Stage Fusion": ["fuse_layers"],
    "Stem Fusion": ["fuse_layers"],
    "Layer Scale Fusion": ["fuse_layers"],
    "Inverted Bottleneck Fusion": ["fuse_layers"],
    
    # Quantization methods
    "AdpQ (Adaptive LASSO)": ["quantize_int8", "weight_only"],
    "VLCQ (Variable-Length Coding)": ["quantize_int8", "weight_only"],
    "Hardware-Friendly PTQ": ["quantize_int8", "weight_only"],
    "Per-Channel Weight Quantization": ["quantize_int8", "weight_only", "per_channel"],
    "Weight Clustering (K-means)": ["quantize_int8", "weight_only"],
    "Codebook Quantization": ["quantize_int8", "weight_only"],
    "Per-Layer Weight Quantization": ["quantize_int8", "weight_only", "per_layer"],
    "Depthwise Conv Quantization": ["quantize_int8", "weight_only"],
    "Pointwise Conv Quantization": ["quantize_int8", "weight_only"],
    "Inverted Residual Quantization": ["quantize_int8", "weight_only"],
    "Weight-Only Quantization": ["quantize_int8", "weight_only"],
    "INT8 Weight-Only": ["quantize_int8", "weight_only"],
    "BoA (Attention-aware Hessian)": ["quantize_int8", "attention_aware"],
    "aespa (Attention-wise Reconstruction)": ["quantize_int8", "attention_aware"],
    "PTQ4ViT": ["quantize_int8", "attention_aware"],
    "APHQ-ViT": ["quantize_int8", "attention_aware"],
    "P4Q (Prompt for Quantization)": ["quantize_int8", "multimodal"],
    "Q-VLM": ["quantize_int8", "multimodal"],
    "Quantized Prompt": ["quantize_int8", "multimodal"],
    "QADS (Per-channel Scaling)": ["quantize_int8", "per_channel"],
    "Q-HyViT": ["quantize_int8", "hybrid"],
    "HyQ": ["quantize_int8", "hybrid"],
    "EfficientQuant": ["quantize_int8", "hybrid"],
    "M2-ViT": ["quantize_int8", "hybrid"],
    "Mix-QViT": ["quantize_int8", "hybrid"],
    "Hardware-Aware Quantization (HAQ)": ["quantize_int8", "hardware_aware"],
    
    # Pruning methods
    "Channel Pruning (L1-norm)": ["prune_magnitude", "structured"],
    "Channel Pruning (BN Scale)": ["prune_magnitude", "structured"],
    "Filter Pruning (Weight Magnitude)": ["prune_magnitude", "structured"],
    "Structured Pruning (Layer-wise)": ["prune_magnitude", "structured"],
    "Filter Pruning (Weight Magnitude)": ["prune_magnitude", "structured"],
    "Structured Layer Pruning": ["prune_magnitude", "structured"],
    "Channel Pruning (Depthwise)": ["prune_magnitude", "structured"],
    "Width Multiplier Adjustment": ["prune_magnitude", "structured"],
    "Channel Pruning (L1-norm)": ["prune_magnitude", "structured"],
    "Channel Pruning (Group-wise)": ["prune_magnitude", "structured"],
    "Backbone Layer Pruning": ["prune_magnitude", "structured"],
    "Attention Head Pruning": ["prune_magnitude", "structured"],
    "MLP Dimension Pruning": ["prune_magnitude", "structured"],
    "Layer Pruning (Depth Reduction)": ["prune_magnitude", "structured"],
    "Window Attention Head Pruning": ["prune_magnitude", "structured"],
    "Stage Pruning": ["prune_magnitude", "structured"],
    "ASPP Branch Pruning": ["prune_magnitude", "structured"],
    "Skip Layer Pruning": ["prune_magnitude", "structured"],
    "Vision Encoder Pruning": ["prune_magnitude", "structured"],
    "Text Encoder Pruning": ["prune_magnitude", "structured"],
    "Channel Pruning (CNN Blocks)": ["prune_magnitude", "structured"],
    "Attention Head Pruning (Transformer Blocks)": ["prune_magnitude", "structured"],
    "Block Pruning (Weight-Based)": ["prune_magnitude", "structured"],
    "Block Pruning": ["prune_magnitude", "structured"],
    "Channel Pruning": ["prune_magnitude", "structured"],
    "Path Pruning": ["prune_magnitude", "structured"],
    
    # Structural optimizations
    "Tailor (Skip Connection Optimization)": ["skip_connection_optimization"],
    "Bottleneck Restructuring": ["topology_optimization"],
    "Bottleneck Optimization": ["topology_optimization"],
    "QSI-NMS": ["nms_acceleration"],
    "eQSI-NMS": ["nms_acceleration"],
    "Detection Head Optimization": ["nms_acceleration"],
    "NMS Acceleration": ["nms_acceleration"],
    "Skip Connection Optimization (Tailor)": ["skip_connection_optimization"],
    "UNet++ Redesigned Skip Connections": ["skip_connection_optimization"],
    "Patch Merging": ["topology_optimization"],
    "Token Dimension Reduction": ["topology_optimization"],
    "Distillation Token Removal": ["topology_optimization"],
    "Reconstruction Head Removal": ["topology_optimization"],
    "Block Pruning (Weight-Based)": ["prune_magnitude", "structured"],
    "Stage Pruning": ["prune_magnitude", "structured"],
}


def extract_techniques_from_method_name(method_name: str) -> List[str]:
    """Extract techniques using mapping table with pattern fallback.
    
    Args:
        method_name: The method name to extract techniques from
        
    Returns:
        List of technique identifiers (e.g., ["fuse_layers", "quantize_int8"])
    """
    if not method_name or not isinstance(method_name, str):
        return []
    
    # Try exact match first
    if method_name in TECHNIQUE_MAPPING:
        return TECHNIQUE_MAPPING[method_name].copy()
    
    # Try pattern matching (regex)
    method_lower = method_name.lower()
    for pattern, techniques in TECHNIQUE_MAPPING.items():
        # Simple substring matching for now (can be enhanced with regex)
        pattern_lower = pattern.lower()
        if pattern_lower in method_lower or method_lower in pattern_lower:
            return techniques.copy()
    
    # Fallback: infer from keywords
    techniques = []
    method_lower = method_name.lower()
    
    # Fusion keywords
    if any(kw in method_lower for kw in ['fuse', 'fusion', 'merge', 'combine']):
        techniques.append('fuse_layers')
    
    # Quantization keywords
    if any(kw in method_lower for kw in ['quant', 'int8', 'int4', 'bit', 'precision']):
        techniques.append('quantize_int8')
        if 'weight' in method_lower or 'w' in method_lower:
            techniques.append('weight_only')
        if 'channel' in method_lower or 'per-channel' in method_lower:
            techniques.append('per_channel')
        if 'attention' in method_lower:
            techniques.append('attention_aware')
    
    # Pruning keywords
    if any(kw in method_lower for kw in ['prune', 'sparse', 'remove', 'drop']):
        techniques.append('prune_magnitude')
        if any(kw in method_lower for kw in ['channel', 'filter', 'structured', 'block']):
            techniques.append('structured')
    
    # Structural optimization keywords
    if any(kw in method_lower for kw in ['skip', 'connection', 'tailor']):
        techniques.append('skip_connection_optimization')
    if any(kw in method_lower for kw in ['nms', 'non-maximum', 'suppression']):
        techniques.append('nms_acceleration')
    if any(kw in method_lower for kw in ['topology', 'structure', 'bottleneck', 'restructure']):
        techniques.append('topology_optimization')
    if any(kw in method_lower for kw in ['decompose', 'svd', 'factorization']):
        techniques.append('decompose_svd')
    if any(kw in method_lower for kw in ['token', 'merge', 'merging']):
        techniques.append('token_merging')
    
    return techniques if techniques else []


def _parse_numeric_value(value: Any) -> float:
    """Parse numeric value from string or number.
    
    Handles formats like "2.0×", "1.25×", "4×", etc.
    """
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove common suffixes
        cleaned = value.replace('×', '').replace('x', '').replace('X', '').strip()
        try:
            return float(cleaned)
        except ValueError:
            pass
    
    return 1.0  # Default fallback


def _migrate_performance(node_data: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate performance data to structured dict format."""
    performance = {}
    
    # If performance already exists as a dict, use it (but ensure required fields)
    if 'performance' in node_data and isinstance(node_data['performance'], dict):
        performance = node_data['performance'].copy()
    else:
        # Migrate from top-level fields
        performance = {}
    
    # Extract from top-level fields
    if 'latency_speedup' not in performance:
        speedup = node_data.get('speedup') or node_data.get('latency_speedup')
        performance['latency_speedup'] = _parse_numeric_value(speedup) if speedup else 1.0
    
    if 'compression_ratio' not in performance:
        comp_ratio = node_data.get('compression_ratio')
        performance['compression_ratio'] = _parse_numeric_value(comp_ratio) if comp_ratio else 1.0
    
    if 'accuracy_retention' not in performance:
        # Try to infer from accuracy_impact or accuracy_drop
        accuracy_impact = node_data.get('accuracy_impact', '').lower()
        if accuracy_impact == 'zero':
            performance['accuracy_retention'] = 1.0
        elif accuracy_impact == 'minimal':
            performance['accuracy_retention'] = 0.95  # Default assumption
        elif accuracy_impact == 'moderate':
            performance['accuracy_retention'] = 0.85  # Default assumption
        else:
            # Try accuracy_drop if present
            accuracy_drop = node_data.get('accuracy_drop', 0.0)
            if isinstance(accuracy_drop, (int, float)):
                performance['accuracy_retention'] = 1.0 - float(accuracy_drop)
            else:
                performance['accuracy_retention'] = 1.0  # Default
    
    # Optional: memory_reduction
    if 'memory_reduction' not in performance and 'compression_ratio' in performance:
        # Memory reduction is typically compression_ratio - 1
        performance['memory_reduction'] = max(0.0, performance['compression_ratio'] - 1.0)
    
    return performance


def _migrate_validation(node_data: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate validation data to structured dict format."""
    validation = {}
    
    # If validation already exists as a dict, use it (but ensure required fields)
    if 'validation' in node_data and isinstance(node_data['validation'], dict):
        validation = node_data['validation'].copy()
    else:
        # Migrate from top-level fields
        validation = {}
    
    # Extract confidence from top-level if not in validation dict
    if 'confidence' not in validation:
        validation['confidence'] = node_data.get('confidence', 0.5)
    
    # Set defaults for missing fields
    if 'sample_count' not in validation:
        validation['sample_count'] = node_data.get('sample_count', 0)  # 0 = unknown
    
    if 'validators' not in validation:
        validation['validators'] = node_data.get('validators', 0)
    
    if 'last_validated' not in validation:
        validation['last_validated'] = node_data.get('last_validated')
    
    if 'validation_method' not in validation:
        validation['validation_method'] = node_data.get('validation_method', 'unknown')
    
    return validation


def _migrate_architecture(node_data: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate architecture to structured dict format."""
    arch = node_data.get('architecture')
    
    if isinstance(arch, dict):
        # Already in dict format, ensure it has required fields
        architecture = arch.copy()
        if 'family' not in architecture:
            architecture['family'] = node_data.get('architecture_family', 'Unknown')
        if 'variant' not in architecture:
            architecture['variant'] = architecture.get('name', 'Unknown')
    elif isinstance(arch, str):
        # Convert string to dict
        architecture = {
            'family': node_data.get('architecture_family', 'Unknown'),
            'variant': arch
        }
    else:
        # Default structure
        architecture = {
            'family': node_data.get('architecture_family', 'Unknown'),
            'variant': 'Unknown'
        }
    
    return architecture


def _migrate_paper(node_data: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate paper metadata to structured dict format."""
    paper = {}
    
    # If paper already exists as a dict, use it
    if 'paper' in node_data and isinstance(node_data['paper'], dict):
        paper = node_data['paper'].copy()
    else:
        # Try to extract from source field
        source = node_data.get('source', {})
        if isinstance(source, dict):
            paper_refs = source.get('paper_refs', [])
            if paper_refs and isinstance(paper_refs, list) and len(paper_refs) > 0:
                # Use first paper ref as title
                paper['title'] = paper_refs[0] if isinstance(paper_refs[0], str) else ''
            else:
                paper['title'] = ''
        else:
            paper['title'] = ''
    
    # Ensure all fields exist (use defaults if missing)
    if 'title' not in paper:
        paper['title'] = node_data.get('paper_title', '')
    
    if 'authors' not in paper:
        authors = node_data.get('authors', '')
        if isinstance(authors, str):
            # Try to parse comma-separated authors
            paper['authors'] = [a.strip() for a in authors.split(',') if a.strip()] if authors else []
        elif isinstance(authors, list):
            paper['authors'] = authors
        else:
            paper['authors'] = []
    
    if 'venue' not in paper:
        paper['venue'] = node_data.get('venue', '')
    
    if 'year' not in paper:
        paper['year'] = node_data.get('year', 0)
    
    if 'arxiv_id' not in paper:
        # Try to extract from paper_link
        paper_link = node_data.get('paper_link', '')
        if isinstance(paper_link, str) and 'arxiv.org' in paper_link:
            # Extract arxiv ID from URL
            match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d+\.\d+)', paper_link)
            if match:
                paper['arxiv_id'] = match.group(1)
            else:
                paper['arxiv_id'] = ''
        else:
            paper['arxiv_id'] = ''
    
    if 'url' not in paper:
        paper['url'] = node_data.get('paper_link', '')
    
    return paper


def migrate_node_to_ideal_schema(node_data: Dict[str, Any], node_id: Optional[str] = None) -> Dict[str, Any]:
    """Migrate a single node from old format to ideal schema.
    
    Args:
        node_data: The node data dictionary (may be in old or new format)
        node_id: Optional node identifier for logging
        
    Returns:
        Migrated node data with ideal schema structure
    """
    if not isinstance(node_data, dict):
        return node_data
    
    migrated = node_data.copy()
    
    # Detect old format
    is_old_format = (
        'techniques' not in node_data or
        'performance' not in node_data or
        not isinstance(node_data.get('performance'), dict) or
        'validation' not in node_data or
        not isinstance(node_data.get('validation'), dict) or
        isinstance(node_data.get('architecture'), str) or
        'paper' not in node_data or
        not isinstance(node_data.get('paper'), dict)
    )
    
    if is_old_format:
        context = f"Node {node_id}" if node_id else "Node"
        warnings.warn(
            f"{context} uses old schema format, migrating to ideal structure...",
            UserWarning,
            stacklevel=2
        )
    
    # Migrate techniques
    if 'techniques' not in migrated or not migrated['techniques']:
        method_name = migrated.get('method_name') or migrated.get('name', '')
        techniques = extract_techniques_from_method_name(method_name)
        if techniques:
            migrated['techniques'] = techniques
    
    # Migrate performance
    migrated['performance'] = _migrate_performance(migrated)
    
    # Migrate validation
    migrated['validation'] = _migrate_validation(migrated)
    
    # Migrate architecture
    architecture = _migrate_architecture(migrated)
    migrated['architecture'] = architecture
    # Keep architecture_family for backward compatibility
    if 'architecture_family' not in migrated:
        migrated['architecture_family'] = architecture['family']
    
    # Migrate paper
    migrated['paper'] = _migrate_paper(migrated)
    
    return migrated


def migrate_taxonomy_to_ideal_schema(taxonomy: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively migrate entire taxonomy structure to ideal schema.
    
    Args:
        taxonomy: The taxonomy dictionary (may contain old or new format nodes)
        
    Returns:
        Migrated taxonomy with all nodes in ideal schema format
    """
    if not isinstance(taxonomy, dict):
        return taxonomy
    
    migrated = {}
    
    for key, value in taxonomy.items():
        if key == 'relationships':
            # Preserve relationships as-is (they'll be handled separately if needed)
            migrated[key] = value
        elif isinstance(value, dict):
            # Check if this is a model with optimization_methods
            if 'optimization_methods' in value:
                # This is a model entry - migrate its optimization methods
                migrated_model = value.copy()
                opt_methods = migrated_model.get('optimization_methods', {})
                
                # Extract architecture info from model characteristics for context
                model_characteristics = migrated_model.get('model_characteristics', {})
                architecture_type = model_characteristics.get('architecture_type', 'Unknown')
                # Try to infer architecture family from architecture_type
                architecture_family = architecture_type.upper() if architecture_type else 'Unknown'
                if architecture_type == 'cnn':
                    architecture_family = 'CNN'
                elif architecture_type == 'transformer':
                    architecture_family = 'Transformer'
                elif architecture_type == 'hybrid':
                    architecture_family = 'Hybrid'
                elif architecture_type == 'multimodal':
                    architecture_family = 'Multimodal'
                
                # Get model name from key (e.g., 'resnet', 'vgg')
                model_name = key if key else 'Unknown'
                
                if isinstance(opt_methods, dict):
                    migrated_opt_methods = {}
                    for category, category_data in opt_methods.items():
                        # Normalize category name: weight_quantization -> quantization
                        normalized_category = category
                        if category == 'weight_quantization':
                            normalized_category = 'quantization'
                        
                        if isinstance(category_data, dict):
                            migrated_category = category_data.copy()
                            
                            # Check if this category has subcategories (nested structure)
                            if 'methods' in category_data:
                                # Flat structure: category -> methods (list)
                                methods = category_data.get('methods', [])
                                migrated_methods = []
                                
                                for method in methods:
                                    if isinstance(method, str):
                                        # Legacy string format - convert to object
                                        migrated_method = {
                                            'name': method,
                                            'method_name': method,
                                            'techniques': extract_techniques_from_method_name(method),
                                            'performance': _migrate_performance(category_data),
                                            'validation': _migrate_validation(category_data),
                                            'paper': _migrate_paper(category_data),
                                            'effectiveness': category_data.get('effectiveness', 'medium'),
                                            'accuracy_impact': category_data.get('accuracy_impact', 'minimal'),
                                            # Add architecture from model context
                                            'architecture': {
                                                'family': architecture_family,
                                                'variant': model_name.capitalize()
                                            },
                                            'architecture_family': architecture_family
                                        }
                                        migrated_methods.append(migrated_method)
                                    elif isinstance(method, dict):
                                        # Already an object - migrate it, but add architecture if missing
                                        migrated_method = migrate_node_to_ideal_schema(method)
                                        if not migrated_method.get('architecture') or isinstance(migrated_method.get('architecture'), str):
                                            migrated_method['architecture'] = {
                                                'family': architecture_family,
                                                'variant': model_name.capitalize()
                                            }
                                            migrated_method['architecture_family'] = architecture_family
                                        migrated_methods.append(migrated_method)
                                    else:
                                        migrated_methods.append(method)
                                
                                migrated_category['methods'] = migrated_methods
                            else:
                                # Nested structure: category -> subcategory -> methods
                                for subcat_name, subcat_data in category_data.items():
                                    if isinstance(subcat_data, dict) and 'methods' in subcat_data:
                                        methods = subcat_data.get('methods', [])
                                        migrated_methods = []
                                        
                                        for method in methods:
                                            if isinstance(method, str):
                                                # Legacy string format
                                                migrated_method = {
                                                    'name': method,
                                                    'method_name': method,
                                                    'techniques': extract_techniques_from_method_name(method),
                                                    'performance': _migrate_performance(subcat_data),
                                                    'validation': _migrate_validation(subcat_data),
                                                    'paper': _migrate_paper(subcat_data),
                                                    'effectiveness': subcat_data.get('effectiveness', 'medium'),
                                                    'accuracy_impact': subcat_data.get('accuracy_impact', 'minimal'),
                                                    # Add architecture from model context
                                                    'architecture': {
                                                        'family': architecture_family,
                                                        'variant': model_name.capitalize()
                                                    },
                                                    'architecture_family': architecture_family
                                                }
                                                migrated_methods.append(migrated_method)
                                            elif isinstance(method, dict):
                                                # Already an object - migrate it, but add architecture if missing
                                                migrated_method = migrate_node_to_ideal_schema(method)
                                                if not migrated_method.get('architecture') or isinstance(migrated_method.get('architecture'), str):
                                                    migrated_method['architecture'] = {
                                                        'family': architecture_family,
                                                        'variant': model_name.capitalize()
                                                    }
                                                    migrated_method['architecture_family'] = architecture_family
                                                migrated_methods.append(migrated_method)
                                            else:
                                                migrated_methods.append(method)
                                        
                                        subcat_data['methods'] = migrated_methods
                            
                            migrated_opt_methods[normalized_category] = migrated_category
                        else:
                            migrated_opt_methods[normalized_category] = category_data
                    
                    migrated_model['optimization_methods'] = migrated_opt_methods
                    migrated[key] = migrated_model
                else:
                    migrated[key] = value
            else:
                # Recursively process nested dictionaries
                migrated[key] = migrate_taxonomy_to_ideal_schema(value)
        else:
            # Preserve non-dict values as-is
            migrated[key] = value
    
    return migrated

