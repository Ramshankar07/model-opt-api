"""
Integration tests for the deployed Federated API on Railway.
Run with: pytest tests/test_production_api.py -v
"""
import pytest
import httpx
import os
from typing import Dict, Any

# Production API URL
PRODUCTION_URL = "https://model-opt-api-production-06d6.up.railway.app"

# API key (set via environment variable or pytest command line)
API_KEY = os.getenv("FEDERATED_API_KEY", "test-key-placeholder")


@pytest.fixture
async def client():
    """Create an async HTTP client for testing."""
    headers = {"Content-Type": "application/json"}
    if API_KEY and API_KEY != "test-key-placeholder":
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    async with httpx.AsyncClient(
        base_url=PRODUCTION_URL,
        headers=headers,
        timeout=30.0
    ) as client:
        yield client


@pytest.fixture
async def public_client():
    """Create a client without auth for public endpoints."""
    async with httpx.AsyncClient(
        base_url=PRODUCTION_URL,
        headers={"Content-Type": "application/json"},
        timeout=30.0
    ) as client:
        yield client


@pytest.mark.asyncio
class TestPublicEndpoints:
    """Test endpoints that don't require authentication."""
    
    async def test_health_check(self, public_client):
        """Test health check endpoint."""
        response = await public_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("[OK] Health check passed")
    
    async def test_get_sample_tree(self, public_client):
        """Test getting sample tree (public endpoint)."""
        response = await public_client.get("/api/v1/trees/sample")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], dict)
        print(f"[OK] Sample tree retrieved: Empty taxonomy structure")


@pytest.mark.asyncio
class TestTreeOperations:
    """Test tree CRUD operations."""
    
    async def test_clone_tree(self, client):
        """Test cloning a tree."""
        payload = {
            "architecture": "transformer",
            "constraints": {
                "depth": 12,
                "max_memory_gb": 8.0
            }
        }
        response = await client.post("/api/v1/trees/clone", json=payload)
        
        # May return 401 if API key is required and not set
        if response.status_code == 401:
            pytest.skip("API key authentication required - set FEDERATED_API_KEY env var")
        
        assert response.status_code == 200
        data = response.json()
        assert "tree_id" in data
        assert "taxonomy" in data
        assert isinstance(data["taxonomy"], dict)
        print(f"[OK] Tree cloned: {data['tree_id']}")
        return data["tree_id"]
    
    async def test_get_tree(self, client):
        """Test getting a tree by ID."""
        # First clone a tree
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Now get it
        response = await client.get(f"/api/v1/trees/{tree_id}")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], dict)
        print(f"[OK] Tree retrieved: {tree_id}")
    
    async def test_get_nonexistent_tree(self, client):
        """Test getting a non-existent tree."""
        response = await client.get("/api/v1/trees/nonexistent-tree-id-12345")
        assert response.status_code == 404
        print("[OK] Non-existent tree correctly returns 404")
    
    async def test_get_taxonomy(self, client):
        """Test getting full taxonomy."""
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        response = await client.get(f"/api/v1/trees/{tree_id}/taxonomy")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        print(f"[OK] Taxonomy retrieved: {tree_id}")
    
    async def test_get_path(self, client):
        """Test getting data at a specific path."""
        # First import a taxonomy with data
        taxonomy = {
            "CNN": {
                "Classification": {
                    "ResNet": {
                        "optimization_methods": {},
                        "model_characteristics": {},
                        "calibration_free_status": {}
                    }
                }
            }
        }
        
        import_response = await client.post(
            "/api/v1/trees/import",
            json={"taxonomy": taxonomy}
        )
        
        if import_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = import_response.json()["tree_id"]
        
        # Get path
        response = await client.get(f"/api/v1/trees/{tree_id}/path/CNN/Classification/ResNet")
        assert response.status_code == 200
        data = response.json()
        assert "optimization_methods" in data
        print(f"[OK] Path data retrieved")


@pytest.mark.asyncio
class TestTaxonomyImport:
    """Test importing taxonomy structures."""
    
    async def test_import_taxonomy(self, client):
        """Test importing a taxonomy structure."""
        taxonomy = {
            "CNN": {
                "Classification Models": {
                    "ResNet": {
                        "optimization_methods": {
                            "quantization": {
                                "weight_only": {
                                    "methods": [
                                        {
                                            "name": "int8_weight_only",
                                            "paper_title": "Post-Training Quantization",
                                            "paper_link": "https://arxiv.org/abs/1234.5678",
                                            "venue": "ICML",
                                            "year": 2024,
                                            "authors": "Author et al.",
                                            "bit_widths": ["W8", "W4"],
                                            "granularity": "per_layer",
                                            "effectiveness": "high",
                                            "compression_ratio": "4×",
                                            "speedup": "2×",
                                            "accuracy_impact": "minimal",
                                            "notes": "Test method"
                                        }
                                    ]
                                }
                            }
                        },
                        "model_characteristics": {
                            "architecture_type": "cnn"
                        },
                        "calibration_free_status": {
                            "available_methods": "abundant"
                        }
                    }
                }
            }
        }
        
        response = await client.post("/api/v1/trees/import", json={"taxonomy": taxonomy})
        
        if response.status_code == 401:
            pytest.skip("API key authentication required")
        
        assert response.status_code == 200
        data = response.json()
        assert "tree_id" in data
        tree_id = data["tree_id"]
        
        # Verify the taxonomy was imported correctly
        get_response = await client.get(f"/api/v1/trees/{tree_id}")
        assert get_response.status_code == 200
        imported_taxonomy = get_response.json()
        assert "data" in imported_taxonomy
        assert "CNN" in imported_taxonomy["data"]
        print(f"[OK] Taxonomy imported and verified: {tree_id}")


@pytest.mark.asyncio
class TestMethodOperations:
    """Test optimization method CRUD operations."""
    
    async def test_add_method(self, client):
        """Test adding an optimization method."""
        # First create a tree and set up a path
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # First, we need to create the path structure
        taxonomy = {
            "CNN": {
                "Classification": {
                    "ResNet": {
                        "optimization_methods": {
                            "quantization": {
                                "weight_only": {
                                    "methods": []
                                }
                            }
                        },
                        "model_characteristics": {},
                        "calibration_free_status": {}
                    }
                }
            }
        }
        
        # Import the structure
        await client.post(f"/api/v1/trees/import", json={"taxonomy": taxonomy})
        # Actually, let's use the tree_id we just created
        # We'll need to manually set up the structure or use a different approach
        
        # For now, let's test with a simpler approach - add method to existing path
        method_data = {
            "path": "CNN/Classification/ResNet",
            "category": "quantization",
            "subcategory": "weight_only",
            "name": "test_method",
            "paper_title": "Test Paper",
            "paper_link": "https://arxiv.org/abs/1234.5678",
            "venue": "ICML",
            "year": 2024,
            "authors": "Author et al.",
            "effectiveness": "high",
            "accuracy_impact": "minimal",
            "bit_widths": ["W8"],
            "notes": "Test"
        }
        
        # First import the base structure
        await client.post("/api/v1/trees/import", json={"taxonomy": taxonomy})
        # Get the new tree_id
        import_response = await client.post("/api/v1/trees/import", json={"taxonomy": taxonomy})
        tree_id = import_response.json()["tree_id"]
        
        response = await client.post(
            f"/api/v1/trees/{tree_id}/methods",
            json=method_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "added"
        print(f"[OK] Method added to tree: {tree_id}")
    
    async def test_update_method(self, client):
        """Test updating an optimization method."""
        # Create taxonomy with a method
        taxonomy = {
            "CNN": {
                "Classification": {
                    "ResNet": {
                        "optimization_methods": {
                            "quantization": {
                                "weight_only": {
                                    "methods": [
                                        {
                                            "name": "test_method",
                                            "paper_title": "Test Paper",
                                            "paper_link": "https://arxiv.org/abs/1234.5678",
                                            "venue": "ICML",
                                            "year": 2024,
                                            "authors": "Author et al.",
                                            "effectiveness": "high",
                                            "accuracy_impact": "minimal"
                                        }
                                    ]
                                }
                            }
                        },
                        "model_characteristics": {},
                        "calibration_free_status": {}
                    }
                }
            }
        }
        
        import_response = await client.post("/api/v1/trees/import", json={"taxonomy": taxonomy})
        
        if import_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = import_response.json()["tree_id"]
        
        # Update the method
        updates = {"effectiveness": "medium", "notes": "Updated"}
        response = await client.put(
            f"/api/v1/trees/{tree_id}/methods/CNN/Classification/ResNet/quantization/weight_only/0",
            json=updates
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        print(f"[OK] Method updated")
    
    async def test_delete_method(self, client):
        """Test deleting an optimization method."""
        # Create taxonomy with a method
        taxonomy = {
            "CNN": {
                "Classification": {
                    "ResNet": {
                        "optimization_methods": {
                            "quantization": {
                                "weight_only": {
                                    "methods": [
                                        {
                                            "name": "deletable_method",
                                            "paper_title": "Test Paper",
                                            "paper_link": "https://arxiv.org/abs/1234.5678",
                                            "venue": "ICML",
                                            "year": 2024,
                                            "authors": "Author et al.",
                                            "effectiveness": "high",
                                            "accuracy_impact": "minimal"
                                        }
                                    ]
                                }
                            }
                        },
                        "model_characteristics": {},
                        "calibration_free_status": {}
                    }
                }
            }
        }
        
        import_response = await client.post("/api/v1/trees/import", json={"taxonomy": taxonomy})
        
        if import_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = import_response.json()["tree_id"]
        
        # Delete the method
        response = await client.delete(
            f"/api/v1/trees/{tree_id}/methods/CNN/Classification/ResNet/quantization/weight_only/0"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "removed"
        print(f"[OK] Method deleted")


@pytest.mark.asyncio
class TestTreeExpansion:
    """Test tree expansion operations."""
    
    async def test_expand_tree(self, client):
        """Test expanding a tree."""
        # Create a tree first
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "transformer", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Expand the tree
        response = await client.post(
            f"/api/v1/trees/{tree_id}/expand",
            json={"architecture": "transformer"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "expanded" in data
        print(f"[OK] Tree expanded: {tree_id}")


@pytest.mark.asyncio
class TestSyncOperations:
    """Test sync operations."""
    
    async def test_sync_tree(self, client):
        """Test syncing local changes."""
        # Create a tree
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Sync changes
        sync_payload = {
            "local_taxonomy": {"data": {}},
            "changes": {}
        }
        
        response = await client.put(
            f"/api/v1/trees/{tree_id}/sync",
            json=sync_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "synced"
        print(f"[OK] Tree synced: {tree_id}")


@pytest.mark.asyncio
class TestMergeOperations:
    """Test merge operations."""
    
    async def test_merge_changes(self, client):
        """Test merging changes."""
        # Create a tree
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Merge changes
        merge_payload = {
            "local_taxonomy": {"data": {}},
            "changes": {}
        }
        
        response = await client.post(
            f"/api/v1/trees/{tree_id}/merge",
            json=merge_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print(f"[OK] Changes merged: {tree_id}")
    
    async def test_get_conflicts(self, client):
        """Test getting conflicts."""
        # Create a tree
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Get conflicts
        response = await client.get(f"/api/v1/trees/{tree_id}/conflicts")
        assert response.status_code == 200
        data = response.json()
        assert "conflicts" in data
        assert isinstance(data["conflicts"], list)
        print(f"[OK] Conflicts retrieved: {len(data['conflicts'])} conflicts")


@pytest.mark.asyncio
class TestRelationshipOperations:
    """Test relationship/weight operations for backward compatibility."""
    
    async def test_add_relationship(self, client):
        """Test adding a relationship with weights."""
        # Create a tree
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Add a relationship with weights
        relationship_data = {
            "methods": ["method1", "method2"],
            "weights": {
                "success_probability": 0.85,
                "sample_count": 15,
                "confidence": 0.80
            },
            "relationship_type": "compatibility"
        }
        
        response = await client.post(
            f"/api/v1/trees/{tree_id}/relationships",
            json=relationship_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "added"
        assert "relationship_id" in data
        print(f"[OK] Relationship added: {data['relationship_id']}")
        return tree_id, data["relationship_id"]
    
    async def test_get_relationships(self, client):
        """Test getting all relationships."""
        # Create tree and add relationship
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Add a relationship
        relationship_data = {
            "methods": ["method1", "method2"],
            "weights": {
                "success_probability": 0.85,
                "confidence": 0.80
            }
        }
        await client.post(
            f"/api/v1/trees/{tree_id}/relationships",
            json=relationship_data
        )
        
        # Get all relationships
        response = await client.get(f"/api/v1/trees/{tree_id}/relationships")
        assert response.status_code == 200
        data = response.json()
        assert "relationships" in data
        assert data["count"] >= 1
        assert len(data["relationships"]) >= 1
        print(f"[OK] Retrieved {data['count']} relationships")
    
    async def test_get_relationship_by_id(self, client):
        """Test getting a specific relationship by ID."""
        # Create tree and add relationship
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Add a relationship
        relationship_data = {
            "methods": ["method1", "method2"],
            "weights": {
                "success_probability": 0.85,
                "confidence": 0.80
            }
        }
        add_response = await client.post(
            f"/api/v1/trees/{tree_id}/relationships",
            json=relationship_data
        )
        relationship_id = add_response.json()["relationship_id"]
        
        # Get the relationship
        response = await client.get(f"/api/v1/trees/{tree_id}/relationships/id/{relationship_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == relationship_id
        assert "weights" in data
        assert data["weights"]["success_probability"] == 0.85
        print(f"[OK] Retrieved relationship: {relationship_id}")
    
    async def test_update_relationship(self, client):
        """Test updating a relationship."""
        # Create tree and add relationship
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Add a relationship
        relationship_data = {
            "methods": ["method1", "method2"],
            "weights": {
                "success_probability": 0.85,
                "confidence": 0.80
            }
        }
        add_response = await client.post(
            f"/api/v1/trees/{tree_id}/relationships",
            json=relationship_data
        )
        relationship_id = add_response.json()["relationship_id"]
        
        # Update the relationship
        updates = {
            "weights": {
                "success_probability": 0.90,
                "confidence": 0.85
            }
        }
        response = await client.put(
            f"/api/v1/trees/{tree_id}/relationships/{relationship_id}",
            json=updates
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        print(f"[OK] Relationship updated: {relationship_id}")
    
    async def test_delete_relationship(self, client):
        """Test deleting a relationship."""
        # Create tree and add relationship
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Add a relationship
        relationship_data = {
            "methods": ["method1", "method2"],
            "weights": {
                "success_probability": 0.85,
                "confidence": 0.80
            }
        }
        add_response = await client.post(
            f"/api/v1/trees/{tree_id}/relationships",
            json=relationship_data
        )
        relationship_id = add_response.json()["relationship_id"]
        
        # Delete the relationship
        response = await client.delete(f"/api/v1/trees/{tree_id}/relationships/{relationship_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "removed"
        print(f"[OK] Relationship deleted: {relationship_id}")
    
    async def test_import_legacy_with_weights(self, client):
        """Test importing legacy format with edge weights."""
        legacy_tree = {
            "nodes": {
                "node1": {"test": True},
                "node2": {"test": True}
            },
            "edges": [
                {
                    "parent": "node1",
                    "child": "node2",
                    "data": {
                        "weights": {
                            "success_probability": 0.82,
                            "sample_count": 12,
                            "confidence": 0.78
                        }
                    }
                }
            ]
        }
        
        response = await client.post("/api/v1/trees/import", json=legacy_tree)
        
        if response.status_code == 401:
            pytest.skip("API key authentication required")
        
        assert response.status_code == 200
        data = response.json()
        assert "tree_id" in data
        assert data.get("converted_from_legacy") == True
        
        # Verify relationships were created
        tree_id = data["tree_id"]
        rel_response = await client.get(f"/api/v1/trees/{tree_id}/relationships")
        assert rel_response.status_code == 200
        rel_data = rel_response.json()
        assert rel_data["count"] >= 1
        
        # Verify weights were preserved
        relationship = rel_data["relationships"][0]
        assert "weights" in relationship
        assert relationship["weights"]["success_probability"] == 0.82
        assert relationship["weights"]["confidence"] == 0.78
        print(f"[OK] Legacy import with weights: {tree_id}")
    
    async def test_export_to_legacy_format(self, client):
        """Test exporting taxonomy to legacy format with weights preserved."""
        # Create tree and add relationship
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Add a relationship with weights
        relationship_data = {
            "methods": ["method1", "method2"],
            "weights": {
                "success_probability": 0.85,
                "sample_count": 15,
                "confidence": 0.80
            }
        }
        await client.post(
            f"/api/v1/trees/{tree_id}/relationships",
            json=relationship_data
        )
        
        # Export as legacy format
        response = await client.get(f"/api/v1/trees/{tree_id}/export?format=legacy")
        assert response.status_code == 200
        data = response.json()
        assert "edges" in data
        assert len(data["edges"]) >= 1
        
        # Verify weights are in edges
        edge = data["edges"][0]
        assert "data" in edge
        assert "weights" in edge["data"]
        assert edge["data"]["weights"]["success_probability"] == 0.85
        print(f"[OK] Export to legacy format: weights preserved")
    
    async def test_get_all_weights(self, client):
        """Test getting all weights from a taxonomy."""
        # Create tree and add relationships
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Add multiple relationships with weights
        for i in range(2):
            relationship_data = {
                "methods": [f"method{i*2+1}", f"method{i*2+2}"],
                "weights": {
                    "success_probability": 0.8 + i * 0.05,
                    "confidence": 0.75 + i * 0.05
                }
            }
            await client.post(
                f"/api/v1/trees/{tree_id}/relationships",
                json=relationship_data
            )
        
        # Get all weights
        response = await client.get(f"/api/v1/trees/{tree_id}/weights")
        assert response.status_code == 200
        data = response.json()
        assert "weights" in data
        assert data["count"] >= 2
        assert len(data["weights"]) >= 2
        print(f"[OK] Retrieved {data['count']} weight entries")


@pytest.mark.asyncio
class TestValidationAndIntegrity:
    """Test validation and data integrity features."""
    
    async def test_invalid_taxonomy_validation(self, client):
        """Test that invalid taxonomy structures are rejected."""
        # Try to import an invalid taxonomy (missing required fields in method)
        invalid_taxonomy = {
            "CNN": {
                "Classification": {
                    "ResNet": {
                        "optimization_methods": {
                            "quantization": {
                                "weight_only": {
                                    "methods": [
                                        {
                                            "name": "invalid_method"
                                            # Missing required fields
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }
        }
        
        response = await client.post("/api/v1/trees/import", json={"taxonomy": invalid_taxonomy})
        
        if response.status_code == 401:
            pytest.skip("API key authentication required")
        
        assert response.status_code == 400
        assert "required" in response.json()["detail"].lower() or "missing" in response.json()["detail"].lower()
        print("[OK] Invalid taxonomy validation working")
    
    async def test_path_validation(self, client):
        """Test path validation."""
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Try to get an invalid path
        response = await client.get(f"/api/v1/trees/{tree_id}/path/invalid")
        assert response.status_code == 400
        print("[OK] Path validation working")
    
    async def test_method_validation(self, client):
        """Test that method validation catches issues."""
        taxonomy = {
            "CNN": {
                "Classification": {
                    "ResNet": {
                        "optimization_methods": {
                            "quantization": {
                                "weight_only": {
                                    "methods": []
                                }
                            }
                        },
                        "model_characteristics": {},
                        "calibration_free_status": {}
                    }
                }
            }
        }
        
        import_response = await client.post("/api/v1/trees/import", json={"taxonomy": taxonomy})
        
        if import_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = import_response.json()["tree_id"]
        
        # Try to add a method with missing required fields
        invalid_method = {
            "path": "CNN/Classification/ResNet",
            "category": "quantization",
            "subcategory": "weight_only",
            "name": "test"
            # Missing required fields
        }
        
        response = await client.post(f"/api/v1/trees/{tree_id}/methods", json=invalid_method)
        assert response.status_code == 400
        print("[OK] Method validation working")
    
    async def test_relationship_validation(self, client):
        """Test that relationship validation catches issues."""
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Try to add relationship with invalid weights
        invalid_relationship = {
            "methods": ["method1", "method2"],
            "weights": {
                "success_probability": 1.5  # Invalid: > 1.0
            }
        }
        
        response = await client.post(f"/api/v1/trees/{tree_id}/relationships", json=invalid_relationship)
        assert response.status_code == 400
        print("[OK] Relationship validation working")
    
    async def test_relationship_requires_two_methods(self, client):
        """Test that relationships require at least 2 methods."""
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Try to add relationship with only one method
        invalid_relationship = {
            "methods": ["method1"],  # Only one method
            "weights": {
                "success_probability": 0.85
            }
        }
        
        response = await client.post(f"/api/v1/trees/{tree_id}/relationships", json=invalid_relationship)
        assert response.status_code == 400
        print("[OK] Relationship requires at least 2 methods")


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling."""
    
    async def test_invalid_tree_id(self, client):
        """Test operations with invalid tree ID."""
        response = await client.get("/api/v1/trees/invalid-id-12345")
        assert response.status_code == 404
    
    async def test_invalid_payload(self, client):
        """Test with invalid payload."""
        response = await client.post(
            "/api/v1/trees/clone",
            json={"invalid": "payload"}
        )
        # Should return 400 or 422 for validation error
        assert response.status_code in [400, 422, 401]


def run_all_tests():
    """Run all tests with verbose output."""
    import asyncio
    
    async def run():
        print("=" * 60)
        print("Testing Federated API Production Deployment")
        print(f"URL: {PRODUCTION_URL}")
        print("=" * 60)
        print()
        
        # Run tests
        pytest.main([__file__, "-v", "-s", "--tb=short"])
    
    asyncio.run(run())


if __name__ == "__main__":
    run_all_tests()
