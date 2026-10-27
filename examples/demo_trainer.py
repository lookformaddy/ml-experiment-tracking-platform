"""Deterministic from-scratch toy trainer demo (synthetic data only).

A tiny closed-form-style trainer: for a fixed synthetic dataset, sweeping
learning-rate / epochs produces deterministic metrics, logged as runs.
No ML framework, no randomness (seeded generator), no external data.
Run: PYTHONPATH=src python -m examples.demo_trainer
"""
import random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ml_experiment_tracking.models import RunStatus
from ml_experiment_tracking.promotion import PromotionGate, evaluate_promotion
from ml_experiment_tracking.store import TrackingStore

def synthetic_dataset(n: int = 200, seed: int = 42) -> list[tuple[float, float]]:
    rng = random.Random(seed); return [(rng.uniform(-1, 1), 2 * rng.uniform(-1, 1) + 0.5) for _ in range(n)]

def train(data, lr: float, epochs: int) -> float:
    """Toy linear fit: deterministic gradient steps on y ~ w*x + b, returns MSE."""
    w = b = 0.0
    for _ in range(epochs):
        gw = sum(-2 * x * (y - (w * x + b)) for x, y in data) / len(data)
        gb = sum(-2 * (y - (w * x + b)) for x, y in data) / len(data)
        w -= lr * gw; b -= lr * gb
    return sum((y - (w * x + b)) ** 2 for x, y in data) / len(data)

def main() -> None:
    store = TrackingStore(Path(__file__).resolve().parents[1] / ".tracking-store")
    store.create_experiment("toy-regression", "Toy regression sweep", "Synthetic-data demo")
    data = synthetic_dataset()
    for i, (lr, epochs) in enumerate([(0.1, 50), (0.05, 100), (0.2, 30)]):
        run = store.create_run(f"demo-{i}", "toy-regression", f"lr={lr} epochs={epochs}",
                               dataset_version="synthetic-v1", model_version=f"toy-v{i}")
        run.log_param("lr", lr); run.log_param("epochs", epochs)
        run.log_metric("mse", train(data, lr, epochs)); run.status = RunStatus.FINISHED
        store.log_artifact(run, "model.json", f'{{"lr": {lr}, "epochs": {epochs}}}'.encode())
        store.save_run(run)
    best = store.best_run("mse", higher_is_better=False, experiment_id="toy-regression")
    print(f"best run: {best.id} mse={best.metrics['mse']:.4f}")
    result = evaluate_promotion(best, [PromotionGate("mse-gate", "mse", 1.4, higher_is_better=False)])
    print(f"promotion: promoted={result.promoted} gates={result.gate_results}")
    print(f"lineage: {store.lineage(best.id)}")
if __name__ == "__main__": main()
