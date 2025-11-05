from fastapi.testclient import TestClient
from federated_api.main import create_app


def test_health():
    app = create_app()
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

