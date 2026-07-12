"""Stage the A2 input: every OPC-regulatory somatic variant labelled in-SE / out-SE,
with coords + phyloP + class, so Claude Science can load ONE clean file and run the
element-level phyloP + distance-to-TSS + replication-timing rigour on the flagship finding.

Run: PYTHONPATH=src .venv/bin/python scripts/prep_a2_input.py
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ENH = Path("data/dmg/enhancers")
SWEEP = Path("data/dmg/sweep_result.tsv")
BED = ENH / "dipg_superenhancers.hg38.bed"
OUT = ENH / "a2_input.tsv"


def main() -> None:
    if not BED.exists():
        raise SystemExit(
            f"Missing {BED}. Run `PYTHONPATH=src .venv/bin/python scripts/k27m_se_analysis.py` first "
            "(it lifts the Nagaraja super-enhancers and writes the bed)."
        )
    sw = pd.read_csv(SWEEP, sep="\t")
    parts = sw["key"].str.split("-", n=3, expand=True)
    sw["chrom"] = parts[0]
    sw["pos"] = parts[1].astype(int)
    sw["ref"] = parts[2]
    sw["alt"] = parts[3]

    # merged super-enhancer union per chromosome
    se = pd.read_csv(BED, sep="\t", header=None, names=["chrom", "start", "end", "line"])
    union: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for c, g in se.groupby("chrom"):
        merged: list[list[int]] = []
        for s, e in sorted(zip(g.start, g.end)):
            if merged and s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        arr = np.array(merged)
        union[c] = (arr[:, 0], arr[:, 1])

    def in_se(c: str, p: int) -> bool:
        if c not in union:
            return False
        starts, ends = union[c]
        i = int(np.searchsorted(starts, p, side="right")) - 1
        return i >= 0 and p <= ends[i]

    sw["in_se"] = [in_se(c, p) for c, p in zip(sw.chrom, sw.pos)]

    cols = ["chrom", "pos", "ref", "alt", "gene", "cls", "phylop", "constrained",
            "converged_2ax", "in_se", "abs_logfc", "high_impact"]
    sw[cols].to_csv(OUT, sep="\t", index=False)
    n_in = int(sw.in_se.sum())
    print(f"wrote {OUT}")
    print(f"  {len(sw)} variants total | {n_in} in-SE | {len(sw) - n_in} out-SE")
    print(f"  phyloP median: in-SE {sw.loc[sw.in_se,'phylop'].median():.3f}  "
          f"vs out {sw.loc[~sw.in_se,'phylop'].median():.3f}")


if __name__ == "__main__":
    main()
