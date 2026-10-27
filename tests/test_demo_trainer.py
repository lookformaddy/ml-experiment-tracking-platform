import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from examples.demo_trainer import synthetic_dataset, train
def test_deterministic():
    d1, d2 = synthetic_dataset(), synthetic_dataset()
    assert d1 == d2 and len(d1) == 200
    assert train(d1, 0.1, 50) == train(d2, 0.1, 50)
def test_training_improves_over_baseline():
    data = synthetic_dataset()
    assert train(data, 0.1, 50) < sum(y ** 2 for _, y in data) / len(data)
