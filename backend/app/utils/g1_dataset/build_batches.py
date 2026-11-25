"""Build G1 raw batches from specs and report distributions.

Run from Edumentor-ai/backend:
    python -m app.utils.g1_dataset.build_batches            # all specs/batch_XX.py
    python -m app.utils.g1_dataset.build_batches 3 4        # only batches 3 and 4

For each specs/batch_XX.py (a module exposing SAMPLES: list[Spec]):
  - sample IDs: G1_{1000 + (batch-1)*50 + i}  (batch 1 -> G1_001001 ...)
  - expands specs (dsl.build), validates every sample (validate.check_sample)
  - writes datajson/LLM_dataset/g1/raw/batch_XX.json
    and datajson/LLM_dataset/g1/manifest/manifest_batch_XX.json
A batch with any invalid sample is NOT written. Prints totals across all built batches:
distributions, per-field fill rate (target ~60% for background fields), query length and
how many kinds of information each query carries.
"""
from __future__ import annotations

import importlib
import json
import sys
from collections import Counter
from pathlib import Path

from app.utils.g1_dataset.dsl import UNKNOWN_ORDER, build
from app.utils.g1_dataset.validate import check_sample

SPECS = Path(__file__).resolve().parent / "specs"
G1 = Path(__file__).resolve().parents[4] / "datajson" / "LLM_dataset" / "g1"
OUT = G1 / "raw"
MAN = G1 / "manifest"
BATCH_SIZE = 50


def build_batch(n: int) -> tuple[list[dict], list[dict], list[str]]:
    mod = importlib.import_module(f"app.utils.g1_dataset.specs.batch_{n:02d}")
    samples, manifest, errors = [], [], []
    if len(mod.SAMPLES) != BATCH_SIZE:
        errors.append(f"batch {n}: {len(mod.SAMPLES)} samples, expected {BATCH_SIZE}")
    for i, spec in enumerate(mod.SAMPLES, 1):
        sid = f"G1_{1000 + (n - 1) * BATCH_SIZE + i:06d}"
        try:
            sample, row = build(spec, sid)
        except Exception as exc:  # spec mistakes
            errors.append(f"{sid}: build error {exc!r}")
            continue
        for e in check_sample(sample):
            errors.append(f"{sid}: {e}  | q={spec.q[:70]!r}")
        samples.append(sample)
        manifest.append(row)
    return samples, manifest, errors


def report() -> None:
    rows, samples = [], []
    for p in sorted(MAN.glob("manifest_batch_*.json")):
        rows += json.loads(p.read_text(encoding="utf-8"))
    for p in sorted(OUT.glob("batch_*.json")):
        samples += json.loads(p.read_text(encoding="utf-8"))
    total = len(samples)
    if not total:
        return

    def show(name, counter):
        print(f"  {name}: " + ", ".join(f"{k} {v} ({100 * v / total:.0f}%)" for k, v in counter.most_common()))

    print(f"\nTOTAL {total} samples")
    for key in ("persona", "lang", "input_pattern", "status", "goal_type"):
        show(key, Counter(r[key] for r in rows))
    show("scenario", Counter(s["metadata"]["scenario_type"] for s in samples))
    show("difficulty", Counter(s["metadata"]["difficulty"] for s in samples))

    unknown = Counter(f for s in samples for f in s["expected_output"]["unknown_fields"])
    print("  filled: " + ", ".join(f"{f} {100 * (total - unknown[f]) / total:.0f}%" for f in UNKNOWN_ORDER))
    words = [len(s["input"]["original_query"].split()) for s in samples]
    print(f"  query words: avg {sum(words) / total:.0f}, median {sorted(words)[total // 2]}, "
          f"<12 words {100 * sum(w < 12 for w in words) / total:.0f}%")
    if all("query_facts" in r for r in rows):
        facts = Counter(min(r["query_facts"], 5) for r in rows)
        print("  facts in query: " + ", ".join(
            f"{'5+' if k == 5 else k} {100 * v / total:.0f}%" for k, v in sorted(facts.items())))

    queries = Counter(" ".join(s["input"]["original_query"].lower().split()) for s in samples)
    dupes = [q for q, c in queries.items() if c > 1]
    print(f"  duplicate queries: {len(dupes)}" + (f" e.g. {dupes[:3]}" if dupes else ""))


def main(args: list[str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    MAN.mkdir(parents=True, exist_ok=True)
    batches = [int(a) for a in args] or sorted(int(p.stem.split("_")[1]) for p in SPECS.glob("batch_*.py"))
    failed = False
    for n in batches:
        samples, manifest, errors = build_batch(n)
        if errors:
            failed = True
            print(f"batch {n:02d}: {len(errors)} error(s), not written")
            for e in errors:
                print("   -", e)
            continue
        (OUT / f"batch_{n:02d}.json").write_text(json.dumps(samples, indent=2, ensure_ascii=False), encoding="utf-8")
        (MAN / f"manifest_batch_{n:02d}.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"batch {n:02d}: {len(samples)} samples written")
    report()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
