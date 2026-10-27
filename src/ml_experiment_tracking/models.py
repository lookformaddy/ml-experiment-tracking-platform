"""Typed domain models. All state is JSON-serialisable so the store stays portable."""
from __future__ import annotations
import hashlib, json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

class RunStatus(str, Enum):
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

def sha256_json(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()

@dataclass
class Artifact:
    name: str
    content_hash: str
    version: int = 1
    size_bytes: int = 0
    uri: str = ""
    def to_dict(self): return asdict(self)

@dataclass
class Run:
    id: str
    experiment_id: str
    name: str
    status: RunStatus = RunStatus.RUNNING
    params: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)
    artifacts: list[Artifact] = field(default_factory=list)
    dataset_version: str = ""
    model_version: str = ""
    reproducibility: dict[str, str] = field(default_factory=dict)
    def log_metric(self, name: str, value: float) -> None:
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("metric must be finite")
        self.metrics[name] = float(value)
    def log_param(self, name: str, value: Any) -> None: self.params[name] = value
    def add_artifact(self, artifact: Artifact) -> None: self.artifacts.append(artifact)
    def snapshot_manifest(self) -> dict[str, str]:
        """Reproducibility manifest: hashes of code/config/data, not the data itself."""
        return {
            "config_hash": sha256_json(self.params),
            "dataset_hash": sha256_text(self.dataset_version),
            "artifact_hash": sha256_json([a.to_dict() for a in self.artifacts]),
        }
    def to_dict(self):
        d = asdict(self); d["status"] = self.status.value; return d

@dataclass
class Experiment:
    id: str
    name: str
    description: str = ""
    def to_dict(self): return asdict(self)
