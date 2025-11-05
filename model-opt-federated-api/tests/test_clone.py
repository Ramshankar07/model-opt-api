from fastapi.testclient import TestClient
from federated_api.main import create_app


def test_clone_tree():
    app = create_app()
    client = TestClient(app)
    payload = {"architecture": "transformer", "constraints": {"depth": 12}}
    r = client.post("/api/v1/trees/clone", json=payload)
    assert r.status_code in (200, 401)  # 401 if env key set
    if r.status_code == 200:
        body = r.json()
        assert "tree_id" in body and "tree" in body

