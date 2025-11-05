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
    app.include_router(trees_router)
    app.include_router(nodes_router)
    app.include_router(merge_router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()

