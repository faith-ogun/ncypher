"""Analyse the DMG discovery sweep: calibrate, add constraint, converge, rank.

Run after the Modal scoring of the functional candidate set completes:
    PYTHONPATH=src python scripts/analyze_sweep.py

Inputs (all under data/dmg/):
  functional_sweep.variant_scores.tsv  - ChromBPNet scores for OPC-peak variants
  background_scores.variant_scores.tsv - 800 random variants, for calibration
  functional_candidates.tsv            - gene / classification / recurrence annotation

Output: data/dmg/sweep_result.tsv + a printed shortlist.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nc_score.scoring import load_scores  # noqa: E402
from nc_score.constraint import PhyloP, CONSTRAINT_THRESHOLD  # noqa: E402
from nc_score.converge import converge  # noqa: E402
from nc_score.variants import Variant  # noqa: E402
from nc_score.cohort import DMG_GENES  # noqa: E402

DMG = Path("data/dmg")


def main():
    # 1. calibrate the high-impact threshold on the background distribution
    bg = load_scores(DMG / "background_scores.variant_scores.tsv")
    bg_abs = np.array([s.abs_logfc for s in bg])
    thr95, thr99 = np.percentile(bg_abs, [95, 99])
    print(f"calibration: background |log2FC| n={len(bg)} "
          f"median={np.median(bg_abs):.3f} p95={thr95:.3f} p99={thr99:.3f}")
    hi = float(thr99)  # high impact = above the 99th percentile of background

    # 2. load the sweep + annotation
    scores = load_scores(DMG / "functional_sweep.variant_scores.tsv",
                         context="trevino_2021.c15")
    ann = pd.read_csv(DMG / "functional_candidates.tsv", sep="\t")
    ann["key"] = ann["chrom"] + "-" + ann["pos"].astype(str) + "-" + ann["ref"] + "-" + ann["alt"]
    annm = ann.set_index("key")
    print(f"sweep scores: {len(scores):,}")

    # 3a. phyloP with an INCREMENTAL, RESUMABLE cache (10,869 remote lookups; the
    #     environment suspends often, so we flush progress and resume).
    cache_path = DMG / "phylop_cache.tsv"
    cache = {}
    if cache_path.exists():
        for ln in cache_path.read_text().splitlines():
            k, v = ln.split("\t")
            cache[k] = float(v) if v != "nan" else float("nan")
    need = [s for s in scores if f"{s.chrom}-{s.pos}-{s.ref}-{s.alt}" not in cache]
    print(f"phyloP cache: {len(cache):,} cached, {len(need):,} to fetch")
    if need:
        with PhyloP() as php, open(cache_path, "a") as cf:
            for j, s in enumerate(need):
                k = f"{s.chrom}-{s.pos}-{s.ref}-{s.alt}"
                v = php.score(s.chrom, s.pos)
                cache[k] = v if v is not None else float("nan")
                cf.write(f"{k}\t{cache[k]}\n")
                if j % 500 == 0:
                    cf.flush()
                    print(f"  phyloP {j:,}/{len(need):,}")
    import numpy as _np

    # 3b. convergence for every scored variant (all local now)
    rows = []
    if True:
        for s in scores:
            key = f"{s.chrom}-{s.pos}-{s.ref}-{s.alt}"
            a = annm.loc[key] if key in annm.index else None
            pv = cache.get(key, float("nan"))
            from nc_score.constraint import PhyloPHit, CONSTRAINT_THRESHOLD as _CT
            hit = PhyloPHit(Variant(s.chrom, s.pos, s.ref, s.alt),
                            phylop=(None if _np.isnan(pv) else pv),
                            constrained=(not _np.isnan(pv) and pv >= _CT))
            call = converge(s, hit, chromatin_hi=hi)
            rows.append(dict(
                key=key, gene=(a["gene"] if a is not None else "?"),
                cls=(a["classification"] if a is not None else "?"),
                n_patients=int(a["n_patients"]) if a is not None else 1,
                logfc=s.logfc, abs_logfc=s.abs_logfc, jsd=s.jsd,
                phylop=hit.phylop, constrained=hit.constrained,
                high_impact=(s.abs_logfc >= hi), promote=call.promote,
                confidence=call.confidence,
                impact_pctile=float((bg_abs < s.abs_logfc).mean()),
            ))
    df = pd.DataFrame(rows)

    # 4. the discovery signal: high chromatin impact AND constrained (2/2 axes)
    df["converged_2ax"] = df["high_impact"] & df["constrained"]
    df = df.sort_values(["converged_2ax", "abs_logfc"], ascending=[False, False]).reset_index(drop=True)
    df.to_csv(DMG / "sweep_result.tsv", sep="\t", index=False)

    print(f"\nhigh-impact (>= p99 background): {df['high_impact'].sum():,}")
    print(f"constrained (phyloP >= {CONSTRAINT_THRESHOLD}): {df['constrained'].sum():,}")
    print(f"CONVERGED (high-impact AND constrained): {df['converged_2ax'].sum():,}")
    print(f"recurrent among converged: {df[df.converged_2ax]['n_patients'].gt(1).sum()}")

    print("\n=== TOP CONVERGED CANDIDATES (chromatin + constraint agree) ===")
    top = df[df.converged_2ax].head(20)
    cols = ["key", "gene", "cls", "n_patients", "logfc", "jsd", "phylop", "impact_pctile"]
    print(top[cols].to_string(index=False) if len(top) else "  (none converged - report honestly)")

    dmg_hits = df[df.gene.isin(DMG_GENES) & df.high_impact]
    print(f"\n=== high-impact variants in DMG genes: {len(dmg_hits)} ===")
    if len(dmg_hits):
        print(dmg_hits[cols].head(15).to_string(index=False))
    print("\nwrote", DMG / "sweep_result.tsv")


if __name__ == "__main__":
    main()
