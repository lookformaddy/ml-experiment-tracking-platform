"""Promotion gates: a run may be promoted only if every gate passes.

Gates are explicit, auditable predicates (not hidden thresholds): a gate
records its name, the metric checked, the threshold and the observed value.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from .models import Run

@dataclass
class PromotionGate:
    name: str
    metric: str
    threshold: float
    higher_is_better: bool = True
    def check(self, run: Run) -> tuple[bool, str]:
        if self.metric not in run.metrics:
            return False, f"metric {self.metric!r} missing"
        value = run.metrics[self.metric]
        ok = value >= self.threshold if self.higher_is_better else value <= self.threshold
        return ok, f"{self.metric}={value} vs threshold {self.threshold} -> {'pass' if ok else 'fail'}"

@dataclass
class PromotionResult:
    run_id: str
    promoted: bool
    gate_results: list[tuple[str, bool, str]]
    def failed_gates(self) -> list[str]: return [n for n, ok, _ in self.gate_results if not ok]

def evaluate_promotion(run: Run, gates: list[PromotionGate]) -> PromotionResult:
    results = [(g.name, *g.check(run)) for g in gates]
    return PromotionResult(run.id, all(ok for _, ok, _ in results), results)
