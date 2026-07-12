#!/usr/bin/env python3
"""Stage the A3 multi-context-specificity input: the 164 converged variants in
the ChromBPNet variant-scorer schema, so they can be re-scored across the
off-lineage brain contexts (c10 / c11 / c9) and a non-neural control.

A3 tests whether the chromatin signal behind the converged shortlist is
CONTEXT-SPECIFIC: strongest in the matched fetal-OPC context (c15, already
scored in data/dmg/sweep_result.tsv) and weaker off-lineage / null in a
non-neural control. This mirrors the caQTL context-specificity result at the
variant level.

Reads data/dmg/sweep_result.tsv (the 164 with converged_2ax true) and writes the
scorer TSV `chrom \t pos \t ref \t alt \t key` (NO header) to
data/dmg/enhancers/a3_input.scorer.tsv. c15 is NOT re-run (already banked).
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "data/dmg/sweep_result.tsv"
OUT = ROOT / "data/dmg/enhancers/a3_input.scorer.tsv"


def is_true(v: str) -> bool:
    return str(v).strip().lower() in {"true", "1", "yes"}


def parse_key(key: str):
    parts = key.split("-")
    if len(parts) != 4:
        return None
    return parts  # chrom, pos, ref, alt


def main() -> None:
    rows = []
    with SWEEP.open() as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if not is_true(r.get("converged_2ax", "")):
                continue
            key = r["key"].strip()
            p = parse_key(key)
            if p is None:
                continue
            chrom, pos, ref, alt = p
            rows.append((chrom, int(pos), ref, alt, key))

    rows.sort(key=lambda x: (x[0], x[1]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        for chrom, pos, ref, alt, key in rows:
            w.writerow([chrom, pos, ref, alt, key])

    print(f"wrote {OUT} : {len(rows)} converged variants (scorer schema, no header)")


if __name__ == "__main__":
    main()
