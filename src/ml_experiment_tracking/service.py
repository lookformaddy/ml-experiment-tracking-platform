"""Optional FastAPI service. Importing this module without FastAPI installed
raises a clear error; the stdlib core and CLI/demo never require it."""
from __future__ import annotations
try:
    from fastapi import FastAPI, HTTPException
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("FastAPI is not installed; install the api extra to run the service") from exc
from .store import TrackingStore
def create_app(store: TrackingStore) -> FastAPI:
    app = FastAPI(title="ML Experiment Tracking")
    @app.get("/runs/{run_id}")
    def get_run(run_id: str):
        try: return store.get_run(run_id).to_dict()
        except FileNotFoundError: raise HTTPException(404, "run not found")
    @app.get("/runs")
    def list_runs(experiment_id: str | None = None):
        return [r.to_dict() for r in store.list_runs(experiment_id)]
    @app.get("/runs/best/{metric}")
    def best(metric: str, higher_is_better: bool = True):
        run = store.best_run(metric, higher_is_better); return run.to_dict() if run else {}
    return app
