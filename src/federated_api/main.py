from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title="Federated API (Stub v1)")

    # CORS (dev-friendly defaults)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers (endpoints are still stubs)
    from federated_api.routes.trees import router as trees_router
    from federated_api.routes.nodes import router as nodes_router
    from federated_api.routes.merge import router as merge_router
    from federated_api.routes.relationships import router as relationships_router
    app.include_router(trees_router)
    app.include_router(nodes_router)
    app.include_router(merge_router)
    app.include_router(relationships_router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.on_event("startup")
    async def load_default_tree():
        """Load the default tree from base_tree.json on startup."""
        try:
            from federated_api.services.tree_service import TreeService
            import os
            
            service = TreeService()
            tree_id = "default"
            
            # Try multiple possible paths for the file (prefer v2, fallback to v1)
            possible_paths = [
                "backups/base_tree_v2.json",  # Updated taxonomy (v2)
                "backups/base_tree.json",  # Original taxonomy (fallback)
                os.path.join(os.path.dirname(__file__), "..", "..", "backups", "base_tree_v2.json"),  # From src/federated_api
                os.path.join(os.path.dirname(__file__), "..", "..", "backups", "base_tree.json"),  # From src/federated_api
                "/app/backups/base_tree_v2.json",  # Docker container path (v2)
                "/app/backups/base_tree.json",  # Docker container path (fallback)
            ]
            
            file_path = None
            for path in possible_paths:
                # Resolve relative paths
                if not os.path.isabs(path):
                    # Try relative to current file location
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    resolved = os.path.join(current_dir, "..", "..", path)
                    resolved = os.path.normpath(resolved)
                else:
                    resolved = path
                
                if os.path.exists(resolved):
                    file_path = path
                    break
            
            if file_path:
                try:
                    service.load_from_file(tree_id, file_path)
                    print(f"[STARTUP] ✅ Loaded default tree from {file_path}")
                except Exception as e:
                    print(f"[STARTUP] ⚠️  Failed to load default tree: {e}")
            else:
                print(f"[STARTUP] ⚠️  base_tree.json not found in any expected location")
                print(f"[STARTUP]    Tried paths: {possible_paths}")
        except Exception as e:
            # Don't fail startup if tree loading fails
            print(f"[STARTUP] ⚠️  Error during default tree loading: {e}")

    return app


app = create_app()

