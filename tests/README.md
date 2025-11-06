# Federated API Tests

## Production API Tests

Tests for the deployed Federated API at: `https://model-opt-api-production-06d6.up.railway.app`

### Quick Test (Simple)

Run the simple smoke tests:

```bash
# No auth required for basic tests
python tests/test_production_api_simple.py

# With API key for full tests
export FEDERATED_API_KEY=your-api-key
python tests/test_production_api_simple.py
```

### Full Test Suite (Pytest)

Run comprehensive tests with pytest:

```bash
# Install pytest if needed
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/test_production_api.py -v

# Run with API key
FEDERATED_API_KEY=your-api-key pytest tests/test_production_api.py -v

# Run specific test class
pytest tests/test_production_api.py::TestPublicEndpoints -v
pytest tests/test_production_api.py::TestValidationAndIntegrity -v

# Run with output
pytest tests/test_production_api.py -v -s
```

### Test Coverage

The test suite covers:

1. **Public Endpoints** (no auth required)
   - Health check
   - Sample tree retrieval

2. **Tree Operations** (auth required)
   - Clone tree
   - Get tree
   - Get non-existent tree (error handling)

3. **Legacy Tree Import**
   - Import legacy format (dict of nodes)
   - Verify conversion to API format
   - Verify tree structure

4. **Node Operations** (auth required)
   - Add node
   - Update node
   - Delete node

5. **Tree Expansion** (auth required)
   - Expand tree with new nodes

6. **Sync Operations** (auth required)
   - Sync local changes

7. **Merge Operations** (auth required)
   - Merge changes
   - Get conflicts

8. **Validation and Integrity** (auth required)
   - Duplicate node ID prevention
   - Orphaned edge cleanup verification
   - Metadata consistency checks
   - Invalid edge validation
   - Tree validation on import

9. **Error Handling**
   - Invalid tree IDs
   - Invalid payloads
   - Validation errors (400 status codes)

### Environment Variables

```bash
# Required for protected endpoints
export FEDERATED_API_KEY=your-secret-api-key

# Optional: override production URL
export FEDERATED_API_URL=https://model-opt-api-production-06d6.up.railway.app
```

### Expected Output

```
============================================================
Testing Federated API Production Deployment
URL: https://model-opt-api-production-06d6.up.railway.app
============================================================

✅ Health check passed
✅ Sample tree retrieved: 4 nodes, 2 edges
✅ Tree cloned: abc123...
✅ Tree retrieved: abc123...
✅ Legacy tree imported and verified: xyz789...
✅ Duplicate node ID prevented
✅ Orphaned edges cleaned up on node deletion
✅ Metadata consistency maintained
✅ Invalid edge validation working
✅ Tree validation on import working
...
```

### Troubleshooting

**401 Unauthorized:**
- Set `FEDERATED_API_KEY` environment variable
- Check that the API key is correct

**Connection errors:**
- Verify the production URL is accessible
- Check network connectivity
- Verify Railway deployment is running

**Test failures:**
- Check that the API is running
- Verify endpoint paths match the API
- Check for API changes/updates

