from ml_experiment_tracking.models import RunStatus
from ml_experiment_tracking.promotion import PromotionGate, evaluate_promotion
from ml_experiment_tracking.store import TrackingStore
def test_all_gates_pass(tmp_path):
    s = TrackingStore(tmp_path); r = s.create_run("r1", "e", "r1")
    r.log_metric("mse", 0.3); r.log_metric("accuracy", 0.9)
    res = evaluate_promotion(r, [PromotionGate("mse", "mse", 0.5, False), PromotionGate("acc", "accuracy", 0.85)])
    assert res.promoted and res.failed_gates() == []
def test_missing_metric_blocks_promotion(tmp_path):
    s = TrackingStore(tmp_path); r = s.create_run("r1", "e", "r1"); r.log_metric("mse", 0.3)
    res = evaluate_promotion(r, [PromotionGate("acc", "accuracy", 0.85)])
    assert not res.promoted and res.failed_gates() == ["acc"]
def test_failing_gate_reported(tmp_path):
    s = TrackingStore(tmp_path); r = s.create_run("r1", "e", "r1"); r.log_metric("mse", 0.9)
    res = evaluate_promotion(r, [PromotionGate("mse", "mse", 0.5, False)])
    assert not res.promoted
