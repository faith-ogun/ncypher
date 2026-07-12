#!/usr/bin/env python3
"""Stage the A9 ABC-linking input: the 164 converged variants with coordinates,
the current nearest/host-gene call, direction, phyloP, and SE membership.

The A9 Claude Science run assigns each converged enhancer variant to its true
target gene via Activity-by-Contact (matched fetal-OPC activity), and compares
to this nearest-gene baseline. Nearest-gene is a strong baseline; the deliverable
is high-confidence links with orthogonal support, NOT a reassignment percentage.

Reads data/dmg/sweep_result.tsv (key,gene,cls,...,logfc,phylop,...,converged_2ax)
and data/dmg/enhancers/converged_in_dipg_se.tsv (the 31 SE-resident converged).
Writes data/dmg/enhancers/a9_input.tsv.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SWEEP = ROOT / "data/dmg/sweep_result.tsv"
SE = ROOT / "data/dmg/enhancers/converged_in_dipg_se.tsv"
OUT = ROOT / "data/dmg/enhancers/a9_input.tsv"


def is_true(v: str) -> bool:
    return str(v).strip().lower() in {"true", "1", "yes"}


def parse_key(key: str):
    # key format: chr{chrom}-{pos}-{ref}-{alt}
    parts = key.split("-")
    if len(parts) != 4:
        return None
    chrom, pos, ref, alt = parts
    return chrom, pos, ref, alt


def main() -> None:
    se_keys = set()
    with SE.open() as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            se_keys.add(row["key"].strip())

    rows = []
    with SWEEP.open() as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if not is_true(r.get("converged_2ax", "")):
                continue
            p = parse_key(r["key"].strip())
            if p is None:
                continue
            chrom, pos, ref, alt = p
            logfc = float(r["logfc"])
            rows.append(
                {
                    "chrom": chrom,
                    "pos": pos,
                    "ref": ref,
                    "alt": alt,
                    "key": r["key"].strip(),
                    "nearest_gene": r["gene"].strip(),
                    "cls": r["cls"].strip(),
                    "logfc": f"{logfc:.4f}",
                    "direction": "loss" if logfc < 0 else "gain",
                    "phylop": r["phylop"].strip(),
                    "in_se": "1" if r["key"].strip() in se_keys else "0",
                }
            )

    rows.sort(key=lambda x: (x["chrom"], int(x["pos"])))
    cols = ["chrom", "pos", "ref", "alt", "key", "nearest_gene", "cls",
            "logfc", "direction", "phylop", "in_se"]
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t")
        w.writeheader()
        w.writerows(rows)

    n_se = sum(1 for r in rows if r["in_se"] == "1")
    print(f"wrote {OUT} : {len(rows)} converged variants ({n_se} SE-resident)")


if __name__ == "__main__":
    main()
