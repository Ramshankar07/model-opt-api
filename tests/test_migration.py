"""Tests for migration service."""

import pytest
from federated_api.services.migration_service import (
    extract_techniques_from_method_name,
    migrate_node_to_ideal_schema,
    migrate_taxonomy_to_ideal_schema,
)


class TestTechniqueExtraction:
    """Test technique extraction from method names."""
    
    def test_exact_match(self):
        """Test exact matching in TECHNIQUE_MAPPING."""
        techniques = extract_techniques_from_method_name("Conv-BN Fusion")
        assert "fuse_layers" in techniques
    
    def test_keyword_fallback(self):
        """Test keyword-based fallback inference."""
        techniques = extract_techniques_from_method_name("Some Random Fusion Method")
        assert "fuse_layers" in techniques
    
    def test_quantization_keywords(self):
        """Test quantization keyword detection."""
        techniques = extract_techniques_from_method_name("INT8 Quantization")
        assert "quantize_int8" in techniques
    
    def test_pruning_keywords(self):
        """Test pruning keyword detection."""
        techniques = extract_techniques_from_method_name("Channel Pruning Method")
        assert "prune_magnitude" in techniques
        assert "structured" in techniques
    
    def test_empty_string(self):
        """Test empty string handling."""
        techniques = extract_techniques_from_method_name("")
        assert techniques == []
    
    def test_none_input(self):
        """Test None input handling."""
        techniques = extract_techniques_from_method_name(None)
        assert techniques == []


class TestNodeMigration:
    """Test node migration to ideal schema."""
    
    def test_migrate_old_format_node(self):
        """Test migrating a node from old format to ideal schema."""
        old_node = {
            "name": "Conv-BN Fusion",
            "method_name": "Conv-BN Fusion",
            "compression_ratio": "1.25×",
            "speedup": "1.25×",
            "confidence": 0.7,
            "architecture": "ResNet",
            "architecture_family": "CNN",
            "effectiveness": "high",
            "accuracy_impact": "zero"
        }
        
        migrated = migrate_node_to_ideal_schema(old_node, "test_node")
        
        # Check techniques
        assert "techniques" in migrated
        assert len(migrated["techniques"]) > 0
        
        # Check performance dict
        assert "performance" in migrated
        assert isinstance(migrated["performance"], dict)
        assert "latency_speedup" in migrated["performance"]
        assert "compression_ratio" in migrated["performance"]
        assert "accuracy_retention" in migrated["performance"]
        
        # Check validation dict
        assert "validation" in migrated
        assert isinstance(migrated["validation"], dict)
        assert "confidence" in migrated["validation"]
        assert migrated["validation"]["confidence"] == 0.7
        
        # Check architecture dict
        assert "architecture" in migrated
        assert isinstance(migrated["architecture"], dict)
        assert migrated["architecture"]["family"] == "CNN"
        assert migrated["architecture"]["variant"] == "ResNet"
        
        # Check paper dict
        assert "paper" in migrated
        assert isinstance(migrated["paper"], dict)
        
        # Check backward compatibility
        assert "architecture_family" in migrated
    
    def test_migrate_already_ideal_node(self):
        """Test that already-ideal nodes remain unchanged (idempotent)."""
        ideal_node = {
            "name": "Test Method",
            "techniques": ["fuse_layers"],
            "performance": {
                "latency_speedup": 2.0,
                "compression_ratio": 2.0,
                "accuracy_retention": 0.98
            },
            "validation": {
                "confidence": 0.8,
                "sample_count": 50,
                "validators": 5
            },
            "architecture": {
                "family": "CNN",
                "variant": "ResNet"
            },
            "paper": {
                "title": "Test Paper",
                "authors": ["Author1"],
                "venue": "ICML",
                "year": 2024
            }
        }
        
        migrated = migrate_node_to_ideal_schema(ideal_node, "test_node")
        
        # Should preserve all fields
        assert migrated["techniques"] == ideal_node["techniques"]
        assert migrated["performance"] == ideal_node["performance"]
        assert migrated["validation"] == ideal_node["validation"]
        assert migrated["architecture"] == ideal_node["architecture"]
        assert migrated["paper"] == ideal_node["paper"]
    
    def test_migrate_node_with_string_methods(self):
        """Test migrating taxonomy with string methods (legacy format)."""
        taxonomy = {
            "cnn_based_models": {
                "classification": {
                    "resnet": {
                        "optimization_methods": {
                            "fusion": {
                                "methods": ["Conv-BN Fusion", "Conv-ReLU Fusion"]
                            }
                        }
                    }
                }
            }
        }
        
        migrated = migrate_taxonomy_to_ideal_schema(taxonomy)
        
        # Check that string methods were converted to objects
        methods = migrated["cnn_based_models"]["classification"]["resnet"]["optimization_methods"]["fusion"]["methods"]
        assert len(methods) == 2
        assert isinstance(methods[0], dict)
        assert "name" in methods[0]
        assert "techniques" in methods[0]
        assert "performance" in methods[0]
        assert "validation" in methods[0]
        assert "architecture" in methods[0]
        assert "paper" in methods[0]


class TestTaxonomyMigration:
    """Test taxonomy-wide migration."""
    
    def test_migrate_empty_taxonomy(self):
        """Test migrating empty taxonomy."""
        taxonomy = {}
        migrated = migrate_taxonomy_to_ideal_schema(taxonomy)
        assert migrated == {}
    
    def test_migrate_taxonomy_preserves_structure(self):
        """Test that migration preserves taxonomy structure."""
        taxonomy = {
            "cnn_based_models": {
                "classification": {
                    "resnet": {
                        "optimization_methods": {
                            "fusion": {
                                "methods": ["Conv-BN Fusion"]
                            }
                        },
                        "model_characteristics": {
                            "architecture_type": "cnn"
                        }
                    }
                }
            }
        }
        
        migrated = migrate_taxonomy_to_ideal_schema(taxonomy)
        
        # Check structure is preserved
        assert "cnn_based_models" in migrated
        assert "classification" in migrated["cnn_based_models"]
        assert "resnet" in migrated["cnn_based_models"]["classification"]
        assert "optimization_methods" in migrated["cnn_based_models"]["classification"]["resnet"]
        assert "model_characteristics" in migrated["cnn_based_models"]["classification"]["resnet"]
        
        # Check methods were migrated
        methods = migrated["cnn_based_models"]["classification"]["resnet"]["optimization_methods"]["fusion"]["methods"]
        assert len(methods) == 1
        assert isinstance(methods[0], dict)
        assert "techniques" in methods[0]
    
    def test_migrate_idempotent(self):
        """Test that migration is idempotent (running twice produces same result)."""
        taxonomy = {
            "test": {
                "optimization_methods": {
                    "fusion": {
                        "methods": ["Conv-BN Fusion"]
                    }
                }
            }
        }
        
        migrated_once = migrate_taxonomy_to_ideal_schema(taxonomy)
        migrated_twice = migrate_taxonomy_to_ideal_schema(migrated_once)
        
        # Should be the same (or at least have same structure)
        assert "test" in migrated_twice
        methods1 = migrated_once["test"]["optimization_methods"]["fusion"]["methods"]
        methods2 = migrated_twice["test"]["optimization_methods"]["fusion"]["methods"]
        assert len(methods1) == len(methods2)
        assert isinstance(methods1[0], dict)
        assert isinstance(methods2[0], dict)


class TestPerformanceMigration:
    """Test performance field migration."""
    
    def test_migrate_performance_from_top_level(self):
        """Test migrating performance from top-level fields."""
        node = {
            "name": "Test",
            "speedup": "2.0×",
            "compression_ratio": "2.0×",
            "accuracy_impact": "minimal"
        }
        
        migrated = migrate_node_to_ideal_schema(node)
        
        assert "performance" in migrated
        perf = migrated["performance"]
        assert perf["latency_speedup"] == 2.0
        assert perf["compression_ratio"] == 2.0
        assert "accuracy_retention" in perf
    
    def test_migrate_performance_preserves_existing(self):
        """Test that existing performance dict is preserved."""
        node = {
            "name": "Test",
            "performance": {
                "latency_speedup": 3.0,
                "compression_ratio": 3.0,
                "accuracy_retention": 0.95
            }
        }
        
        migrated = migrate_node_to_ideal_schema(node)
        
        assert migrated["performance"]["latency_speedup"] == 3.0
        assert migrated["performance"]["compression_ratio"] == 3.0
        assert migrated["performance"]["accuracy_retention"] == 0.95


class TestValidationMigration:
    """Test validation field migration."""
    
    def test_migrate_validation_from_top_level(self):
        """Test migrating validation from top-level confidence."""
        node = {
            "name": "Test",
            "confidence": 0.8
        }
        
        migrated = migrate_node_to_ideal_schema(node)
        
        assert "validation" in migrated
        val = migrated["validation"]
        assert val["confidence"] == 0.8
        assert "sample_count" in val
        assert "validators" in val


class TestArchitectureMigration:
    """Test architecture field migration."""
    
    def test_migrate_architecture_from_string(self):
        """Test migrating architecture from string to dict."""
        node = {
            "name": "Test",
            "architecture": "ResNet",
            "architecture_family": "CNN"
        }
        
        migrated = migrate_node_to_ideal_schema(node)
        
        assert "architecture" in migrated
        assert isinstance(migrated["architecture"], dict)
        assert migrated["architecture"]["family"] == "CNN"
        assert migrated["architecture"]["variant"] == "ResNet"
        assert migrated["architecture_family"] == "CNN"  # Preserved for backward compatibility

