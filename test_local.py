"""Quick local test of the API"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from federated_api.main import app
from fastapi.testclient import TestClient

# Create client with auth headers
client = TestClient(app, headers={"Authorization": "Bearer test-key"})

def test_health():
    response = client.get("/health")
    print(f"Health: {response.status_code} - {response.json()}")

def test_sample():
    response = client.get("/api/v1/trees/sample")
    print(f"Sample: {response.status_code}")
    print(f"Response: {response.json()}")

def test_clone():
    response = client.post("/api/v1/trees/clone", json={"architecture": "test", "constraints": {}})
    print(f"Clone: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        tree_id = data.get("tree_id")
        # Immediately try to get it
        print(f"Immediately getting tree {tree_id}...")
        get_response = client.get(f"/api/v1/trees/{tree_id}")
        print(f"Immediate get: {get_response.status_code} - {get_response.json()}")
        return tree_id
    else:
        print(f"Error: {response.json()}")
    return None

def test_get_tree(tree_id):
    if not tree_id:
        return
    print(f"Getting tree with ID: {tree_id}")
    response = client.get(f"/api/v1/trees/{tree_id}")
    print(f"Get tree: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.json()}")
    
    # Also test getting the taxonomy directly
    response2 = client.get(f"/api/v1/trees/{tree_id}/taxonomy")
    print(f"Get taxonomy: {response2.status_code}")
    if response2.status_code == 200:
        print(f"Taxonomy: {response2.json()}")

def test_import():
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
    response = client.post("/api/v1/trees/import", json={"taxonomy": taxonomy})
    print(f"Import: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Tree ID: {data.get('tree_id')}")
        return data.get("tree_id")
    else:
        print(f"Error: {response.json()}")
    return None

if __name__ == "__main__":
    print("Testing local API...")
    print("=" * 60)
    test_health()
    print("-" * 60)
    test_sample()
    print("-" * 60)
    tree_id = test_clone()
    print("-" * 60)
    if tree_id:
        test_get_tree(tree_id)
    print("-" * 60)
    import_id = test_import()
    print("=" * 60)

