# Architecture
## Components
- `models.py` — typed Run / Experiment / Artifact dataclasses; SHA-256 hashing helpers.
- `store.py` — file-backed registry: one JSON file per run, atomic temp-file+rename writes,
  artifact files under `artifacts/` with content-hash + per-name version counter.
- `promotion.py` — explicit, auditable promotion gates (name, metric, threshold, direction).
- `service.py` — optional FastAPI read API; never imported by the core or the demo.
- `examples/demo_trainer.py` — deterministic toy trainer on synthetic data.
## Data flow
create_run -> log params/metrics -> log_artifact (hash + version) -> save_run -> rank/best -> gates -> lineage.
## Scaling path
Swap `TrackingStore` file I/O for object storage + a relational index; keep the
Run/Artifact model and gate semantics unchanged. Concurrency today is single-writer
(atomic rename prevents torn files but not lost updates — noted as a limitation).
## Security / clean-room
Only hashes of config/data are stored in manifests, never raw datasets; all code and
data here are original/synthetic; no employer code, data, or internal designs.
