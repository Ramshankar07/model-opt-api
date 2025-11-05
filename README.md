# Federated API (Stub v1)

In-memory FastAPI service for federated tree operations. Uses simple repositories that can be swapped for MongoDB/Redis later.

## Production Deployment

**Live API:** https://model-opt-api-production-06d6.up.railway.app

**API Docs:** https://model-opt-api-production-06d6.up.railway.app/docs

## Quickstart (Local)

```bash
pip install -r requirements.txt
python run_local.py
```

Then open `http://localhost:8000/docs`.

## Testing Production API

### Quick Test
```bash
python tests/test_production_api_simple.py
```

### Full Test Suite
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/test_production_api.py -v

# With API key for protected endpoints
FEDERATED_API_KEY=your-key pytest tests/test_production_api.py -v
```

See [tests/README.md](tests/README.md) for detailed testing instructions.

## Environment

- `FEDERATED_API_KEY` (optional): when set, API requires `Authorization: Bearer <key>`.

## Notes

- Current implementation uses in-memory storage and stubbed services.
- Persistence backends can be added later by replacing repositories in `federated_api.database`.

## Examples

### Production API

```bash
# Health check (public)
curl https://model-opt-api-production-06d6.up.railway.app/health

# Sample tree (public)
curl https://model-opt-api-production-06d6.up.railway.app/api/v1/trees/sample

# Clone tree (requires auth)
curl -X POST https://model-opt-api-production-06d6.up.railway.app/api/v1/trees/clone \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"architecture":"transformer","constraints":{"depth":12}}'
```

### Local Development

```bash
# Health
curl -s http://localhost:8000/health

# Clone (no auth if FEDERATED_API_KEY not set)
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

