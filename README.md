# Federated API (Stub v1)

In-memory FastAPI service for federated tree operations. Uses simple repositories that can be swapped for MongoDB/Redis later.

## Quickstart

```bash
pip install -r requirements.txt
uvicorn federated_api.main:app --reload
```

Then open `http://localhost:8000/docs`.

## Environment

- `FEDERATED_API_KEY` (optional): when set, API requires `Authorization: Bearer <key>`.

## Notes

- Current implementation uses in-memory storage and stubbed services.
- Persistence backends can be added later by replacing repositories in `federated_api.database`.

## Examples

```bash
# Health
curl -s http://localhost:8000/health

# Clone (no auth)
curl -s -X POST http://localhost:8000/api/v1/trees/clone \
  -H 'content-type: application/json' \
  -d '{"architecture":"transformer","constraints":{"depth":12}}'

# With API key
export FEDERATED_API_KEY=devkey
curl -s -X POST http://localhost:8000/api/v1/trees/clone \
  -H 'authorization: Bearer devkey' \
  -H 'content-type: application/json' \
  -d '{"architecture":"transformer","constraints":{}}'
```

