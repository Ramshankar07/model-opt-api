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

