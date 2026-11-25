"""Write datajson/LLM_dataset/g1/dataset_manifest.json and review_sample_20.json from the raw batches.

Run from Edumentor-ai/backend (after build_batches):
    python -m app.utils.g1_dataset.write_manifest
The review set is stratified (conflicts, clarifications, project goals, inferred skills,
hard Vietnamese, switchers, form-heavy) with a fixed seed so it is reproducible.
"""
from __future__ import annotations

import collections
import json
import random
from pathlib import Path

from app.utils.learner_analyzer.prompt import PROMPT_VERSION

G1 = Path(__file__).resolve().parents[4] / "datajson" / "LLM_dataset" / "g1"


def main() -> None:
    samples, rows = [], []
    for p in sorted((G1 / "raw").glob("batch_*.json")):
        samples += json.loads(p.read_text(encoding="utf-8"))
    for p in sorted((G1 / "manifest").glob("manifest_batch_*.json")):
        rows += json.loads(p.read_text(encoding="utf-8"))
    meta = {r["sample_id"]: r for r in rows}
    count = lambda f: dict(collections.Counter(f(s) for s in samples).most_common())  # noqa: E731
    n_batches = len(list((G1 / "raw").glob("batch_*.json")))
    manifest = {
        "dataset_name": "G1_parser",
        "dataset_version": "0.1-raw",
        "schema": "Edumentor-ai/backend/app/utils/learner_analyzer/schemas.py (G1DatasetSample)",
        "prompt_version": PROMPT_VERSION,
        "created_at": "2026-11-24",
        "total_samples": len(samples),
        "sample_id_range": [samples[0]["sample_id"], samples[-1]["sample_id"]],
        "split_status": "not split yet: train 2,000 / validation 375 / test 375 / OOD 250 are assigned when the full 3,000 exist (plan 2.7)",
        "provenance": {
            "source": "synthetic",
            "generator": "Claude (claude-opus-5-5) writing compact specs; deterministic fields expanded by app/utils/g1_dataset/dsl.py",
            "specs": "Edumentor-ai/backend/app/utils/g1_dataset/specs/batch_XX.py",
            "validation": "app/utils/g1_dataset/validate.py (schema + semantic + no-invention checks)",
            "human_review": "pending (see review_sample_20.json)",
            "batches": [{"batch": b, "sample_ids": [f"G1_{1000 + (b - 1) * 50 + 1:06d}", f"G1_{1000 + b * 50:06d}"]}
                        for b in range(1, n_batches + 1)],
        },
        "distribution": {
            "persona": count(lambda s: meta[s["sample_id"]]["persona"]),
            "language": count(lambda s: meta[s["sample_id"]]["lang"]),
            "input_pattern": count(lambda s: meta[s["sample_id"]]["input_pattern"]),
            "status": count(lambda s: s["expected_output"]["status"]),
            "goal_type": count(lambda s: s["expected_output"]["goal"]["goal_type"]),
            "scenario_type": count(lambda s: s["metadata"]["scenario_type"]),
            "difficulty": count(lambda s: s["metadata"]["difficulty"]),
        },
        "per_sample": rows,
    }
    (G1 / "dataset_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    rnd, chosen = random.Random(42), []

    def pick(pred, n):
        pool = [s for s in samples if pred(s) and s not in chosen]
        chosen.extend(rnd.sample(pool, min(n, len(pool))))

    pick(lambda s: meta[s["sample_id"]]["input_pattern"] == "conflict", 4)
    pick(lambda s: s["expected_output"]["status"] == "needs_clarification", 3)
    pick(lambda s: s["expected_output"]["goal"]["goal_type"] == "project", 2)
    pick(lambda s: any(p["evidence_type"] == "inferred_from_context" for p in s["expected_output"]["skill_profiles"]), 3)
    pick(lambda s: s["metadata"]["difficulty"] == "hard" and meta[s["sample_id"]]["lang"] == "vi", 2)
    pick(lambda s: meta[s["sample_id"]]["persona"] == "switcher", 2)
    pick(lambda s: meta[s["sample_id"]]["input_pattern"] == "mostly_structured", 2)
    pick(lambda s: True, 2)
    review = [{"review": {"lang": meta[s["sample_id"]]["lang"], "persona": meta[s["sample_id"]]["persona"],
                          "input_pattern": meta[s["sample_id"]]["input_pattern"], "verdict": None, "notes": None}, **s}
              for s in sorted(chosen, key=lambda s: s["sample_id"])]
    (G1 / "review_sample_20.json").write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"manifest: {len(samples)} samples; review set: {len(review)} samples")


if __name__ == "__main__":
    main()
