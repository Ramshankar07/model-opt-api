"""
Simple smoke tests for production API - quick verification.
Run with: python tests/test_production_api_simple.py
"""
import asyncio
import httpx
import os

PRODUCTION_URL = "https://model-opt-api-production-06d6.up.railway.app"
API_KEY = os.getenv("FEDERATED_API_KEY")


async def test_health():
    """Test health endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PRODUCTION_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("[OK] Health check: OK")


async def test_sample_tree():
    """Test sample tree endpoint."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PRODUCTION_URL}/api/v1/trees/sample")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], dict)
        print(f"[OK] Sample tree: Empty taxonomy structure")


async def test_clone_tree():
    """Test clone tree endpoint."""
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PRODUCTION_URL}/api/v1/trees/clone",
            json={"architecture": "transformer", "constraints": {"depth": 12}},
            headers=headers
        )
        
        if response.status_code == 401:
            print("[SKIP] Clone tree: Requires API key (set FEDERATED_API_KEY env var)")
            return
        
        assert response.status_code == 200
        data = response.json()
        assert "tree_id" in data
        assert "taxonomy" in data
        print(f"[OK] Clone tree: Created tree {data['tree_id']}")
        return data["tree_id"]


async def test_import_taxonomy():
    """Test importing taxonomy structure."""
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    # Create a simple taxonomy structure
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
                                        "paper_title": "Post-Training Quantization for Neural Networks",
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
                        "architecture_type": "cnn",
                        "key_components": ["conv", "bn", "relu"]
                    },
                    "calibration_free_status": {
                        "available_methods": "abundant",
                        "research_gap": False
                    }
                }
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PRODUCTION_URL}/api/v1/trees/import",
            json={"taxonomy": taxonomy},
            headers=headers
        )
        
        if response.status_code == 401:
            print("[SKIP] Import taxonomy: Requires API key")
            return
        
        assert response.status_code == 200
        data = response.json()
        assert "tree_id" in data
        print(f"[OK] Import taxonomy: Imported as {data['tree_id']}")


async def main():
    """Run all simple tests."""
    print("=" * 60)
    print("Simple Production API Tests")
    print(f"URL: {PRODUCTION_URL}")
    if API_KEY:
        print(f"API Key: {'*' * (len(API_KEY) - 4)}{API_KEY[-4:]}")
    else:
        print("API Key: Not set (some tests will be skipped)")
    print("=" * 60)
    print()
    
    try:
        await test_health()
        await test_sample_tree()
        await test_clone_tree()
        await test_import_taxonomy()
        print()
        print("=" * 60)
        print("[OK] All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
