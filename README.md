# Federated API (Stub v1)

In-memory FastAPI service for federated tree operations. Uses simple repositories that can be swapped for MongoDB/Redis later.

## Tree Structure

The API uses a graph-based tree structure with nodes and edges:

### Data Models

**Node:**
- `id` (required): Unique identifier for the node
- `label` (optional): Human-readable label
- `data` (dict): Flexible data container for node-specific information
- `created_at` (optional): Timestamp when node was created
- `updated_at` (optional): Timestamp when node was last updated

**Edge:**
- `source` (required): ID of the source node
- `target` (required): ID of the target node
- `relation` (optional): Relationship type between nodes
- `data` (dict): Edge-specific data (e.g., weights, probabilities)

**Tree:**
- `nodes`: List of Node objects
- `edges`: List of Edge objects
- `meta`: Metadata dictionary (includes `node_count`, `edge_count`, etc.)
- `created_at` (optional): Timestamp when tree was created
- `updated_at` (optional): Timestamp when tree was last updated

### Data Integrity & Validation

The API enforces several data integrity rules:

1. **Node Uniqueness**: Each node must have a unique ID within a tree
2. **Edge Validation**: All edges must reference existing nodes (source and target)
3. **Orphaned Edge Cleanup**: When a node is deleted, all edges referencing it are automatically removed
4. **Metadata Consistency**: `meta.node_count` and `meta.edge_count` are automatically maintained
5. **Self-Loop Prevention**: Edges cannot have the same source and target node

### Tree Helper Methods

The `Tree` model provides convenient helper methods:

- `get_node(node_id)`: Get a node by ID (returns `None` if not found)
- `has_node(node_id)`: Check if a node exists
- `get_edges_for_node(node_id)`: Get all edges connected to a node
- `get_children(node_id)`: Get child node IDs (nodes this node points to)
- `get_parents(node_id)`: Get parent node IDs (nodes that point to this node)

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

## API Features

### Validation

All tree operations are validated to ensure data integrity:
- Duplicate node IDs are rejected
- Invalid edge references are caught
- Missing required fields are detected
- Tree structure is validated on import

### Service Methods

The `TreeService` provides centralized operations:
- `add_node_to_tree()`: Add node with validation
- `remove_node_from_tree()`: Remove node and cleanup edges
- `add_edge_to_tree()`: Add edge with validation
- `remove_edge_from_tree()`: Remove edge
- `cleanup_orphaned_edges()`: Remove edges referencing non-existent nodes

### Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors, duplicate IDs, invalid edges)
- `404`: Not Found (tree or node not found)
- `401`: Unauthorized (missing or invalid API key)
- `422`: Unprocessable Entity (schema validation errors)

## Notes

- Current implementation uses in-memory storage and stubbed services.
- Persistence backends can be added later by replacing repositories in `federated_api.database`.
- All tree operations automatically maintain metadata consistency.
- Node deletion automatically cleans up related edges to prevent orphaned references.

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

# Add node to tree (requires auth)
curl -X POST https://model-opt-api-production-06d6.up.railway.app/api/v1/trees/{tree_id}/nodes \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"id":"node1","label":"Test Node","data":{"test":true}}'

# Update node (requires auth)
curl -X PUT https://model-opt-api-production-06d6.up.railway.app/api/v1/trees/{tree_id}/nodes/node1 \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"data":{"updated":true}}'

# Delete node (requires auth) - automatically cleans up edges
curl -X DELETE https://model-opt-api-production-06d6.up.railway.app/api/v1/trees/{tree_id}/nodes/node1 \
  -H "Authorization: Bearer your-api-key"
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

## Usage Examples

### Working with Trees

```python
# Example: Creating a tree and adding nodes
import httpx

# Clone a tree
response = httpx.post(
    "http://localhost:8000/api/v1/trees/clone",
    json={"architecture": "transformer", "constraints": {"depth": 12}},
    headers={"Authorization": "Bearer your-api-key"}
)
tree_id = response.json()["tree_id"]

# Add nodes
node1 = {"id": "node1", "label": "Base Model", "data": {"type": "baseline"}}
node2 = {"id": "node2", "label": "Optimized", "data": {"type": "optimized"}}

httpx.post(f"http://localhost:8000/api/v1/trees/{tree_id}/nodes", json=node1)
httpx.post(f"http://localhost:8000/api/v1/trees/{tree_id}/nodes", json=node2)

# Try to add duplicate (will fail with 400)
duplicate = {"id": "node1", "label": "Duplicate"}
response = httpx.post(f"http://localhost:8000/api/v1/trees/{tree_id}/nodes", json=duplicate)
# Response: 400 Bad Request - "Duplicate node ID: node1"

# Delete node (edges are automatically cleaned up)
httpx.delete(f"http://localhost:8000/api/v1/trees/{tree_id}/nodes/node1")

# Get tree and use helper methods (if using Pydantic Tree model)
tree_data = httpx.get(f"http://localhost:8000/api/v1/trees/{tree_id}").json()
from federated_api.models import Tree
tree = Tree(**tree_data)

# Use helper methods
node = tree.get_node("node2")
children = tree.get_children("node2")
parents = tree.get_parents("node2")
edges = tree.get_edges_for_node("node2")
```

### Importing Legacy Trees

```python
# Legacy format (dict of nodes)
legacy_tree = {
    "nodes": {
        "node_1": {
            "architecture": {"family": "CNN", "variant": "ResNet"},
            "compression_config": {"type": "quantization", "bits": 8}
        },
        "node_2": {
            "architecture": {"family": "CNN", "variant": "ResNet"},
            "compression_config": {"type": "quantization", "bits": 8, "pruning": {"ratio": 0.3}}
        }
    },
    "edges": [
        {
            "parent": "node_1",
            "child": "node_2",
            "data": {"weights": {"success_probability": 0.82}}
        }
    ],
    "metadata": {"node_count": 2, "edge_count": 1}
}

# Import will validate and convert to API format
response = httpx.post(
    "http://localhost:8000/api/v1/trees/import",
    json=legacy_tree,
    headers={"Authorization": "Bearer your-api-key"}
)
tree_id = response.json()["tree_id"]
```

