import pytest
try: from ml_experiment_tracking.service import create_app
except RuntimeError: pytest.skip("FastAPI not installed", allow_module_level=True)
def test_service_lists_runs(tmp_path):
    from fastapi.testclient import TestClient
    from ml_experiment_tracking.store import TrackingStore
    s = TrackingStore(tmp_path); s.create_run("r1", "e", "r1")
    assert TestClient(create_app(s)).get("/runs").json()[0]["id"] == "r1"
