"""File-backed run registry with search, ranking, lineage and artifact versioning.

Design: one JSON document per run under <store>/runs/<run_id>.json, plus
experiment index. No database dependency; the storage layer is swappable
(see docs/architecture.md). All writes are atomic (temp file + rename).
"""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, Callable, Iterable
from .models import Artifact, Experiment, Run, RunStatus, sha256_text

class TrackingStore:
    def __init__(self, root: str | Path):
        self.root = Path(root); (self.root / "runs").mkdir(parents=True, exist_ok=True)
        (self.root / "artifacts").mkdir(parents=True, exist_ok=True)
    # -- experiments -------------------------------------------------
    def create_experiment(self, exp_id: str, name: str, description: str = "") -> Experiment:
        exp = Experiment(exp_id, name, description)
        self._write_json(self.root / f"experiment-{exp_id}.json", exp.to_dict()); return exp
    # -- runs --------------------------------------------------------
    def create_run(self, run_id: str, experiment_id: str, name: str, **kw: Any) -> Run:
        run = Run(id=run_id, experiment_id=experiment_id, name=name, **kw)
        self._save(run); return run
    def get_run(self, run_id: str) -> Run:
        return self._load(self.root / "runs" / f"{run_id}.json")
    def save_run(self, run: Run) -> None: self._save(run)
    def list_runs(self, experiment_id: str | None = None) -> list[Run]:
        runs = [self._load(p) for p in sorted((self.root / "runs").glob("*.json"))]
        return [r for r in runs if experiment_id is None or r.experiment_id == experiment_id]
    def search(self, metric: str | None = None, min_value: float | None = None,
               max_value: float | None = None, param: tuple[str, Any] | None = None,
               tag: tuple[str, str] | None = None, experiment_id: str | None = None) -> list[Run]:
        out = []
        for r in self.list_runs(experiment_id):
            if metric is not None and metric not in r.metrics: continue
            if metric is not None and min_value is not None and r.metrics[metric] < min_value: continue
            if metric is not None and max_value is not None and r.metrics[metric] > max_value: continue
            if param is not None and r.params.get(param[0]) != param[1]: continue
            if tag is not None and r.tags.get(tag[0]) != tag[1]: continue
            out.append(r)
        return out
    def rank(self, metric: str, higher_is_better: bool = True, experiment_id: str | None = None) -> list[Run]:
        runs = [r for r in self.list_runs(experiment_id) if metric in r.metrics]
        return sorted(runs, key=lambda r: r.metrics[metric], reverse=higher_is_better)
    def best_run(self, metric: str, higher_is_better: bool = True, experiment_id: str | None = None) -> Run | None:
        ranked = self.rank(metric, higher_is_better, experiment_id); return ranked[0] if ranked else None
    # -- artifacts ---------------------------------------------------
    def log_artifact(self, run: Run, name: str, content: bytes) -> Artifact:
        digest = sha256_text(content.decode(errors="replace")) if False else __import__("hashlib").sha256(content).hexdigest()
        version = 1 + sum(1 for a in run.artifacts if a.name == name)
        path = self.root / "artifacts" / f"{run.id}-{name}-v{version}"
        path.write_bytes(content)
        art = Artifact(name=name, content_hash=digest, version=version, size_bytes=len(content), uri=str(path))
        run.add_artifact(art); self._save(run); return art
    def lineage(self, run_id: str) -> dict[str, str]:
        r = self.get_run(run_id)
        return {"run_id": r.id, "experiment_id": r.experiment_id, "dataset_version": r.dataset_version,
                "model_version": r.model_version, "artifacts": ",".join(f"{a.name}@v{a.version}" for a in r.artifacts),
                **r.snapshot_manifest()}
    # -- io ----------------------------------------------------------
    def _save(self, run: Run) -> None: self._write_json(self.root / "runs" / f"{run.id}.json", run.to_dict())
    @staticmethod
    def _write_json(path: Path, payload: dict) -> None:
        tmp = path.with_suffix(".tmp"); tmp.write_text(json.dumps(payload, indent=2, sort_keys=True)); os.replace(tmp, path)
    @staticmethod
    def _load(path: Path) -> Run:
        d = json.loads(path.read_text())
        d["status"] = RunStatus(d["status"])
        d["artifacts"] = [Artifact(**a) for a in d.get("artifacts", [])]
        return Run(**d)
