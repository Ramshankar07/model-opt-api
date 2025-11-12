"""
Base schema for calibration-free post-training optimization taxonomy.

This schema defines the structure for storing optimization methods for neural network
models in a truly calibration-free manner (zero-data methods only).

The schema supports multiple optimization categories:
- Quantization (weight-only, attention-specific, component-specific)
- Fusion (layer, block, graph fusion)
- Pruning (structured, unstructured)
- Structural optimizations (topology, algorithm, parameter adjustment)

Each method includes full paper metadata: title, link, venue, year, authors, etc.

IDEAL NODE STRUCTURE:
====================

Every optimization method node should follow this ideal structure:

{
    'name': 'method_name',
    'method_name': 'method_name',  # Alias for backward compatibility
    'techniques': ['fuse_layers', 'quantize_int8'],  # Explicit techniques array
    
    'performance': {  # Consistent performance dict structure
        'latency_speedup': 2.0,
        'compression_ratio': 2.0,
        'accuracy_retention': 0.98,
        'memory_reduction': 1.0  # Optional
    },
    
    'validation': {  # Statistical confidence structure
        'confidence': 0.7,
        'sample_count': 50,
        'validators': 5,
        'last_validated': '2024-01-15T10:30:00Z',
        'validation_method': 'experimental'
    },
    
    'architecture': {  # Consistent architecture dict structure
        'family': 'CNN',
        'variant': 'ResNet'
    },
    'architecture_family': 'CNN',  # Kept for quick lookup/backward compatibility
    
    'paper': {  # Provenance metadata
        'title': 'Layer Fusion for CNN Optimization',
        'authors': ['Author1', 'Author2'],
        'venue': 'ICML',
        'year': 2024,
        'arxiv_id': '2401.12345',
        'url': 'https://arxiv.org/abs/2401.12345'
    },
    
    'effectiveness': 'high',
    'accuracy_impact': 'minimal',
    
    # Legacy fields (kept for backward compatibility)
    'compression_ratio': '2.0×',  # Legacy, prefer performance.compression_ratio
    'speedup': '2.0×',  # Legacy, prefer performance.latency_speedup
    'confidence': 0.7,  # Legacy, prefer validation.confidence
    'bit_widths': ['W8', 'W4'],
    'granularity': 'per_layer',
    'notes': 'additional context'
}

RELATIONSHIP/EDGE STRUCTURE:
============================

Relationships should include enhanced compatibility metadata:

{
    'id': 'rel_123',
    'methods': ['method_path_1', 'method_path_2'],
    'weights': {
        'success_probability': 0.82,
        'sample_count': 12,
        'confidence': 0.78
    },
    'relationship_type': 'compatibility',
    'metadata': {
        'constraints': {
            'order': ['method_path_1', 'method_path_2'],  # Optional ordering
            'min_accuracy_retention': 0.95  # Optional minimum requirement
        },
        'tested_models': ['ResNet-50', 'MobileNet-V2'],
        'tested_datasets': ['ImageNet', 'COCO']
    }
}

MIGRATION:
==========

The system automatically migrates old format nodes to ideal structure on load.
Old format is still accepted during transition period with warnings.

Old format detection:
- Missing 'techniques' field
- Missing or non-dict 'performance' field
- Missing or non-dict 'validation' field
- String 'architecture' instead of dict
- Missing or non-dict 'paper' field
"""

CALIBRATION_FREE_SCHEMA = {
    'model_family': {  # Level 1
        'subcategory': {  # Level 2
            'specific_model': {  # Level 3
                'optimization_methods': {  # Level 4
                    'quantization': {
                        'weight_only': {
                            'methods': [
                                {
                                    'name': 'method_name',
                                    'paper_title': 'Full paper title',
                                    'paper_link': 'https://arxiv.org/abs/...',
                                    'venue': 'conference/journal name',
                                    'year': 2024,
                                    'authors': 'First Author et al.',
                                    'bit_widths': ['W8', 'W4', 'W3', 'W2'],
                                    'granularity': 'per_layer/per_channel/per_block',
                                    'effectiveness': 'high/medium/low',
                                    'compression_ratio': 'X×',
                                    'speedup': 'X×',
                                    'accuracy_impact': 'zero/minimal/moderate',
                                    'notes': 'additional context'
                                }
                            ]
                        },
                        'attention_specific': {
                            'methods': [
                                {
                                    'name': 'method_name',
                                    'paper_title': 'Full paper title',
                                    'paper_link': 'https://...',
                                    'venue': 'conference/journal',
                                    'year': 2024,
                                    'applies_to': 'qkv/self_attention/cross_attention',
                                    'effectiveness': 'high/medium/low'
                                }
                            ]
                        },
                        'component_specific': {
                            'methods': [
                                {
                                    'name': 'method_name',
                                    'paper_title': 'Full paper title',
                                    'paper_link': 'https://...',
                                    'venue': 'conference/journal',
                                    'year': 2024,
                                    'target_component': 'component_name',
                                    'effectiveness': 'high/medium/low'
                                }
                            ]
                        }
                    },
                    'fusion': {
                        'layer_fusion': {
                            'methods': [
                                {
                                    'name': 'method_name',
                                    'paper_title': 'Full paper title',
                                    'paper_link': 'https://...',
                                    'venue': 'conference/journal',
                                    'year': 2024,
                                    'fusion_type': 'conv_bn/conv_relu/sequential',
                                    'effectiveness': 'high/medium/low',
                                    'speedup': 'X×',
                                    'accuracy_impact': 'zero/minimal',
                                    'universal': True  # or False
                                }
                            ]
                        },
                        'block_fusion': {
                            'methods': [
                                {
                                    'name': 'method_name',
                                    'paper_title': 'Full paper title',
                                    'paper_link': 'https://...',
                                    'venue': 'conference/journal',
                                    'year': 2024,
                                    'fusion_scope': 'residual/bottleneck/stage',
                                    'effectiveness': 'high/medium/low'
                                }
                            ]
                        },
                        'graph_fusion': {
                            'methods': [
                                {
                                    'name': 'method_name',
                                    'paper_title': 'Full paper title',
                                    'paper_link': 'https://...',
                                    'venue': 'conference/journal',
                                    'year': 2024,
                                    'operations_fused': ['op1', 'op2', 'op3'],
                                    'effectiveness': 'high/medium/low'
                                }
                            ]
                        }
                    },
                    'pruning': {
                        'structured_pruning': {
                            'methods': [
                                {
                                    'name': 'method_name',
                                    'paper_title': 'Full paper title',
                                    'paper_link': 'https://...',
                                    'venue': 'conference/journal',
                                    'year': 2024,
                                    'pruning_granularity': 'channel/filter/layer/head',
                                    'criterion': 'weight_magnitude/bn_scale/importance_score',
                                    'effectiveness': 'high/medium/low',
                                    'validation_needed': True  # or False
                                }
                            ]
                        },
                        'unstructured_pruning': {
                            'methods': [
                                {
                                    'name': 'method_name',
                                    'paper_title': 'Full paper title',
                                    'paper_link': 'https://...',
                                    'venue': 'conference/journal',
                                    'year': 2024,
                                    'sparsity_pattern': 'random/structured_sparse',
                                    'effectiveness': 'high/medium/low'
                                }
                            ]
                        }
                    },
                    'structural': {
                        'topology_optimization': {
                            'methods': [
                                {
                                    'name': 'method_name',
                                    'paper_title': 'Full paper title',
                                    'paper_link': 'https://...',
                                    'venue': 'conference/journal',
                                    'year': 2024,
                                    'optimization_type': 'skip_connection/path/stage',
                                    'effectiveness': 'high/medium/low',
                                    'memory_reduction': 'X%',
                                    'speedup': 'X×'
                                }
                            ]
                        },
                        'algorithm_optimization': {
                            'methods': [
                                {
                                    'name': 'method_name',
                                    'paper_title': 'Full paper title',
                                    'paper_link': 'https://...',
                                    'venue': 'conference/journal',
                                    'year': 2024,
                                    'optimization_scope': 'nms/post_processing/inference',
                                    'effectiveness': 'high/medium/low',
                                    'speedup': 'X×'
                                }
                            ]
                        },
                        'parameter_adjustment': {
                            'methods': [
                                {
                                    'name': 'method_name',
                                    'paper_title': 'Full paper title',
                                    'paper_link': 'https://...',
                                    'venue': 'conference/journal',
                                    'year': 2024,
                                    'adjustable_parameters': ['width/depth/resolution'],
                                    'effectiveness': 'high/medium/low'
                                }
                            ]
                        }
                    }
                },
                'model_characteristics': {
                    'architecture_type': 'cnn/transformer/hybrid/multimodal',
                    'key_components': ['list', 'of', 'components'],
                    'has_batch_norm': True,  # or False
                    'has_layer_norm': True,  # or False
                    'has_attention': True,  # or False
                    'has_skip_connections': True,  # or False
                    'optimization_challenges': ['challenge1', 'challenge2']
                },
                'calibration_free_status': {
                    'available_methods': 'abundant/moderate/minimal',
                    'research_gap': True,  # or False
                    'recommended_approach': 'description'
                },
                'relationships': {  # Optional: For backward compatibility with graph-based weights
                    'method_combinations': [
                        {
                            'id': 'rel_123',
                            'methods': [
                                'quantization/weight_only/methods[0]',
                                'pruning/structured_pruning/methods[0]'
                            ],
                            'weights': {
                                'success_probability': 0.82,
                                'sample_count': 12,
                                'confidence': 0.78
                            },
                            'relationship_type': 'compatibility',  # or 'sequence', 'alternative', etc.
                            'metadata': {}
                        }
                    ]
                }
            }
        }
    }
}

