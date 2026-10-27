# ML Experiment Tracking Platform
## Enterprise problem
ML teams lose reproducibility when runs, metrics, artifacts, and promotion decisions
live in notebooks and chat threads. This platform is a small, auditable registry:
every run records its parameters, metrics, artifact versions (content-hashed),
dataset/model lineage, and a reproducibility manifest — and promotion to the next
stage requires explicit gates to pass, with the evidence attached.
## Architecture overview
Pure-stdlib core (`src/ml_experiment_tracking/`): typed models, a file-backed run
registry with atomic writes, artifact versioning, search/ranking, and promotion gates.
An optional FastAPI read API (`service.py`) is only loaded when FastAPI is installed.
See `docs/architecture.md` for the component diagram in prose and the scaling path.
## How to run
```
PYTHONPATH=src python -m examples.demo_trainer   # deterministic synthetic-data sweep
PYTHONPATH=src python -m pytest -q               # test suite (or: make test)
PYTHONPATH=src python -m ml_experiment_tracking --store ./.tracking-store --list
```
## Design decisions and trade-offs
- **File-backed JSON over a database**: zero-dependency, portable, inspectable; the
  store interface is the seam for a DB/object-store swap later.
- **Content hashes, not stored datasets**: manifests prove what ran without copying
  (potentially sensitive) data into the registry.
- **Explicit gates over magic thresholds**: every promotion decision lists each gate,
  its threshold, and the observed value, so a failed promotion is auditable.
- **Single-writer assumption**: atomic renames prevent torn files but concurrent
  writers can lose updates — acceptable for this scope, flagged in architecture docs.
- **CI shipped as `docs/github-actions-ci.yml`**, not `.github/workflows/ci.yml`:
  the GitHub integration used to publish this repo rejects workflow paths
  (Workflows permission missing). Move it to `.github/workflows/ci.yml` to activate.
## What it demonstrates
Experiment/run registry, metric & parameter logging, artifact versioning with content
hashes, run comparison and ranking, best-run selection with promotion gates,
reproducibility manifests, search/filter by metric/param, run-to-dataset/model lineage,
and a deterministic from-scratch toy trainer demo — all clean-room, synthetic data only.
