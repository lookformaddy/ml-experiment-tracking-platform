import pytest
from ml_experiment_tracking.models import RunStatus
from ml_experiment_tracking.store import TrackingStore

@pytest.fixture
def store(tmp_path): return TrackingStore(tmp_path)

def _run(store, rid, mse, lr=0.1):
    r = store.create_run(rid, "exp1", rid, dataset_version="synthetic-v1", model_version="m1")
    r.log_param("lr", lr); r.log_metric("mse", mse); r.status = RunStatus.FINISHED; store.save_run(r); return r

def test_create_and_get_roundtrip(store):
    r = _run(store, "r1", 0.5); got = store.get_run("r1")
    assert got.metrics["mse"] == 0.5 and got.params["lr"] == 0.1 and got.status == RunStatus.FINISHED
def test_search_by_metric_and_param(store):
    _run(store, "r1", 0.5); _run(store, "r2", 0.9, lr=0.2)
    assert [r.id for r in store.search(metric="mse", max_value=0.6)] == ["r1"]
    assert [r.id for r in store.search(param=("lr", 0.2))] == ["r2"]
def test_rank_and_best(store):
    _run(store, "r1", 0.5); _run(store, "r2", 0.2); _run(store, "r3", 0.8)
    assert [r.id for r in store.rank("mse", higher_is_better=False)] == ["r2", "r1", "r3"]
    assert store.best_run("mse", higher_is_better=False).id == "r2"
    assert store.best_run("missing") is None
def test_artifact_versioning_and_hash(store):
    r = _run(store, "r1", 0.5)
    a1 = store.log_artifact(r, "model.bin", b"v1"); a2 = store.log_artifact(r, "model.bin", b"v2")
    assert (a1.version, a2.version) == (1, 2) and a1.content_hash != a2.content_hash
def test_reproducibility_manifest_changes_with_config(store):
    r1, r2 = _run(store, "r1", 0.5), _run(store, "r2", 0.5, lr=0.2)
    assert r1.snapshot_manifest()["config_hash"] != r2.snapshot_manifest()["config_hash"]
def test_lineage_contains_dataset_and_model(store):
    r = _run(store, "r1", 0.5); lin = store.lineage("r1")
    assert lin["dataset_version"] == "synthetic-v1" and lin["model_version"] == "m1"
def test_nonfinite_metric_rejected(store):
    r = store.create_run("r1", "exp1", "r1")
    with pytest.raises(ValueError): r.log_metric("mse", float("inf"))
def test_missing_run_raises(store):
    with pytest.raises(FileNotFoundError): store.get_run("nope")
