"""CLI: python -m ml_experiment_tracking --help (stdlib only)."""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml_experiment_tracking.store import TrackingStore
def main():
    p = argparse.ArgumentParser(); p.add_argument("--store", default="./.tracking-store"); p.add_argument("--list", action="store_true")
    a = p.parse_args(); s = TrackingStore(a.store)
    print(f"{len(s.list_runs())} run(s) in {a.store}")
if __name__ == "__main__": main()
