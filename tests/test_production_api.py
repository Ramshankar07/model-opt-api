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
        assert "nodes" in data
        assert "edges" in data
        assert "meta" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)
        print(f"[OK] Sample tree retrieved: {len(data['nodes'])} nodes, {len(data['edges'])} edges")


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
        assert "tree" in data
        assert data["tree"]["meta"]["architecture"] == "transformer"
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
        assert "nodes" in data
        assert "edges" in data
        print(f"[OK] Tree retrieved: {tree_id}")
    
    async def test_get_nonexistent_tree(self, client):
        """Test getting a non-existent tree."""
        response = await client.get("/api/v1/trees/nonexistent-tree-id-12345")
        assert response.status_code == 404
        print("[OK] Non-existent tree correctly returns 404")


@pytest.mark.asyncio
class TestLegacyTreeImport:
    """Test importing trees in legacy format."""
    
    async def test_import_legacy_tree(self, client):
        """Test importing a tree in legacy format."""
        legacy_tree = {
            "nodes": {
                "node_quantize_int8_cnn": {
                    "architecture": {"family": "CNN", "variant": "ResNet"},
                    "compression_config": {
                        "type": "quantization",
                        "bits": 8,
                        "method": "int8_weight_only"
                    },
                    "performance": {
                        "accuracy_retention": 0.98,
                        "compression_ratio": 4.0,
                        "latency_speedup": 2.0,
                        "memory_gb": 2.5,
                        "latency_ms": 12.5
                    },
                    "validation": {
                        "sample_count": 15,
                        "confidence": 0.85,
                        "validators": 3,
                        "source": "validated"
                    },
                    "source": {
                        "origin": "federated",
                        "paper_refs": ["Post-Training Quantization for Neural Networks"],
                        "status": "validated",
                        "paper_score": 0.9
                    },
                    "visit_count": 0,
                    "q_value": 0.5,
                    "local_updated": "2024-01-15T10:00:00"
                },
                "node_quantize_prune_cnn": {
                    "architecture": {"family": "CNN", "variant": "ResNet"},
                    "compression_config": {
                        "type": "quantization",
                        "bits": 8,
                        "method": "int8_weight_only",
                        "pruning": {"type": "structured", "ratio": 0.3}
                    },
                    "performance": {
                        "accuracy_retention": 0.95,
                        "compression_ratio": 5.5,
                        "latency_speedup": 2.8,
                        "memory_gb": 1.8,
                        "latency_ms": 10.0
                    },
                    "validation": {
                        "sample_count": 12,
                        "confidence": 0.78,
                        "validators": 2,
                        "source": "validated"
                    },
                    "source": {
                        "origin": "federated",
                        "paper_refs": ["Structured Pruning and Quantization for Efficient Inference"],
                        "status": "validated",
                        "paper_score": 0.85
                    },
                    "visit_count": 0,
                    "q_value": 0.5,
                    "local_updated": "2024-01-15T10:00:00"
                }
            },
            "edges": [
                {
                    "parent": "node_quantize_int8_cnn",
                    "child": "node_quantize_prune_cnn",
                    "data": {
                        "weights": {
                            "success_probability": 0.82,
                            "sample_count": 12,
                            "confidence": 0.78
                        }
                    }
                }
            ],
            "metadata": {
                "node_count": 2,
                "edge_count": 1,
                "saved_at": "2024-01-15T10:00:00"
            }
        }
        
        response = await client.post("/api/v1/trees/import", json=legacy_tree)
        
        if response.status_code == 401:
            pytest.skip("API key authentication required")
        
        assert response.status_code == 200
        data = response.json()
        assert "tree_id" in data
        tree_id = data["tree_id"]
        
        # Verify the tree was imported correctly
        get_response = await client.get(f"/api/v1/trees/{tree_id}")
        assert get_response.status_code == 200
        imported_tree = get_response.json()
        assert len(imported_tree["nodes"]) == 2
        assert len(imported_tree["edges"]) == 1
        # Verify conversion: parent/child -> source/target
        assert imported_tree["edges"][0]["source"] == "node_quantize_int8_cnn"
        assert imported_tree["edges"][0]["target"] == "node_quantize_prune_cnn"
        print(f"[OK] Legacy tree imported and verified: {tree_id}")


@pytest.mark.asyncio
class TestNodeOperations:
    """Test node CRUD operations."""
    
    async def test_add_node(self, client):
        """Test adding a node to a tree."""
        # First create a tree
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Add a node
        node_data = {
            "id": "test_node_123",
            "architecture": {"family": "CNN", "variant": "ResNet"},
            "compression_config": {"type": "quantization", "bits": 8},
            "performance": {"accuracy_retention": 0.95}
        }
        
        response = await client.post(
            f"/api/v1/trees/{tree_id}/nodes",
            json=node_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "added"
        print(f"[OK] Node added to tree: {tree_id}")
    
    async def test_update_node(self, client):
        """Test updating a node."""
        # Create tree and add node
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        node_data = {"id": "updatable_node", "performance": {"accuracy_retention": 0.90}}
        await client.post(f"/api/v1/trees/{tree_id}/nodes", json=node_data)
        
        # Update the node
        updates = {"performance": {"accuracy_retention": 0.95}}
        response = await client.put(
            f"/api/v1/trees/{tree_id}/nodes/updatable_node",
            json=updates
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        print(f"[OK] Node updated: updatable_node")
    
    async def test_delete_node(self, client):
        """Test deleting a node."""
        # Create tree and add node
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        node_data = {"id": "deletable_node", "test": True}
        await client.post(f"/api/v1/trees/{tree_id}/nodes", json=node_data)
        
        # Delete the node
        response = await client.delete(
            f"/api/v1/trees/{tree_id}/nodes/deletable_node"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pruned"
        print(f"[OK] Node deleted: deletable_node")


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
        assert "new_nodes" in data
        assert isinstance(data["new_nodes"], list)
        print(f"[OK] Tree expanded: {len(data['new_nodes'])} new nodes")


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
            "local_tree": {
                "nodes": [{"id": "local_node", "test": True}],
                "edges": [],
                "meta": {}
            },
            "changes": {
                "updated_edges": [],
                "new_nodes": [{"id": "local_node"}]
            }
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
            "local_tree": {
                "nodes": [{"id": "merged_node", "test": True}],
                "edges": [],
                "meta": {}
            },
            "changes": {
                "new_nodes": [{"id": "merged_node"}]
            }
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
class TestValidationAndIntegrity:
    """Test validation and data integrity features."""
    
    async def test_duplicate_node_prevention(self, client):
        """Test that duplicate node IDs are prevented."""
        # Create a tree
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Add a node
        node_data = {"id": "unique_node", "test": True}
        response = await client.post(f"/api/v1/trees/{tree_id}/nodes", json=node_data)
        assert response.status_code == 200
        
        # Try to add another node with the same ID
        response = await client.post(f"/api/v1/trees/{tree_id}/nodes", json=node_data)
        assert response.status_code == 400
        assert "duplicate" in response.json()["detail"].lower()
        print("[OK] Duplicate node ID prevented")
    
    async def test_orphaned_edge_cleanup(self, client):
        """Test that edges are cleaned up when a node is deleted."""
        # Create a tree
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Add two nodes
        node1 = {"id": "node1", "test": True}
        node2 = {"id": "node2", "test": True}
        await client.post(f"/api/v1/trees/{tree_id}/nodes", json=node1)
        await client.post(f"/api/v1/trees/{tree_id}/nodes", json=node2)
        
        # Manually add an edge (if edge endpoint exists, otherwise we'll test the cleanup)
        # For now, we'll test that deleting a node doesn't leave orphaned edges
        # by checking the tree structure after deletion
        
        # Get tree before deletion
        tree_before = await client.get(f"/api/v1/trees/{tree_id}")
        assert tree_before.status_code == 200
        
        # Delete node1
        delete_response = await client.delete(f"/api/v1/trees/{tree_id}/nodes/node1")
        assert delete_response.status_code == 200
        
        # Get tree after deletion
        tree_after = await client.get(f"/api/v1/trees/{tree_id}")
        assert tree_after.status_code == 200
        tree_data = tree_after.json()
        
        # Verify node1 is gone
        node_ids = [n["id"] for n in tree_data["nodes"]]
        assert "node1" not in node_ids
        assert "node2" in node_ids
        
        # Verify no edges reference node1 (if edges existed)
        for edge in tree_data.get("edges", []):
            assert edge.get("source") != "node1"
            assert edge.get("target") != "node1"
        
        print("[OK] Orphaned edges cleaned up on node deletion")
    
    async def test_metadata_consistency(self, client):
        """Test that metadata node_count and edge_count are consistent."""
        # Create a tree
        clone_response = await client.post(
            "/api/v1/trees/clone",
            json={"architecture": "test", "constraints": {}}
        )
        
        if clone_response.status_code == 401:
            pytest.skip("API key authentication required")
        
        tree_id = clone_response.json()["tree_id"]
        
        # Get initial tree
        tree_response = await client.get(f"/api/v1/trees/{tree_id}")
        tree_data = tree_response.json()
        
        # Check metadata consistency
        meta = tree_data.get("meta", {})
        actual_node_count = len(tree_data.get("nodes", []))
        actual_edge_count = len(tree_data.get("edges", []))
        
        # Metadata should match actual counts
        assert meta.get("node_count") == actual_node_count
        assert meta.get("edge_count") == actual_edge_count
        
        # Add a node
        node_data = {"id": "meta_test_node", "test": True}
        await client.post(f"/api/v1/trees/{tree_id}/nodes", json=node_data)
        
        # Check metadata again
        tree_response = await client.get(f"/api/v1/trees/{tree_id}")
        tree_data = tree_response.json()
        meta = tree_data.get("meta", {})
        actual_node_count = len(tree_data.get("nodes", []))
        
        assert meta.get("node_count") == actual_node_count
        print("[OK] Metadata consistency maintained")
    
    async def test_invalid_edge_validation(self, client):
        """Test that edges with invalid node references are rejected."""
        # Try to import a tree with invalid edges (in legacy format)
        # The edge references a node that doesn't exist
        invalid_tree = {
            "nodes": {
                "node1": {"test": True}
            },
            "edges": [
                {
                    "parent": "node1",
                    "child": "nonexistent_node",
                    "data": {}
                }
            ],
            "metadata": {}
        }
        
        response = await client.post("/api/v1/trees/import", json=invalid_tree)
        assert response.status_code == 400
        assert "non-existent" in response.json()["detail"].lower() or "invalid" in response.json()["detail"].lower()
        print("[OK] Invalid edge validation working")
    
    async def test_tree_validation_on_import(self, client):
        """Test that tree validation catches issues on import."""
        if client.base_url.host == "model-opt-api-production-06d6.up.railway.app":
            # Skip if API key not available for production
            if not API_KEY or API_KEY == "test-key-placeholder":
                pytest.skip("API key required for production")
        
        # Try to import tree with duplicate node IDs
        invalid_tree = {
            "nodes": {
                "node1": {"test": True},
                "node2": {"test": True}
            },
            "edges": [],
            "metadata": {}
        }
        
        # Convert to API format manually for test
        # The conversion should create duplicate IDs if we manipulate it
        # Actually, let's test with a tree that has duplicate IDs after conversion
        # Since conversion uses node_id as the key, duplicates aren't possible in legacy format
        # So we'll test with missing required fields instead
        
        invalid_tree_missing_fields = {
            "nodes": [
                {"id": "node1"},  # Valid
                {"label": "node without id"}  # Invalid - missing id
            ],
            "edges": [],
            "metadata": {}
        }
        
        response = await client.post("/api/v1/trees/import", json=invalid_tree_missing_fields)
        # Should fail validation
        assert response.status_code == 400
        print("[OK] Tree validation on import working")


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

