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

