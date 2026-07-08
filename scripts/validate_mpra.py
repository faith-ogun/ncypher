"""Axis-1 validation: does NCypher's chromatin prediction recover the measured
functional variants (the 164 DAVs) in the Pollard developing-cortex MPRA?

Two honest claims:
  1. Ranking - AUPRC of predicted |log2FC| at recovering the 164 DAVs among the
     ~8,029 active variants (positive rate ~2%; AUPRC, not AUROC).
  2. Effect-size - correlation of predicted allelic log2FC vs measured MPRA logFC.
Plus the honest motifbreakR framing: it annotates a motif for only 34/164 (21%) of
the DAVs (mechanism coverage), whereas NCypher ranks + predicts function.

Run after Modal scoring of mpra_validation.scorer.tsv:
  PYTHONPATH=src python scripts/validate_mpra.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nc_score.scoring import load_scores  # noqa: E402
from nc_score.validate import ranking_report, correlate_effects, plot_pr_curve  # noqa: E402

MPRA = Path("data/mpra")


def main():
    ann = pd.read_csv(MPRA / "mpra_validation.annot.tsv", sep="\t")
    scores = load_scores(MPRA / "mpra_scores.variant_scores.tsv", context="trevino_2021.c15")
    sdf = pd.DataFrame([{
        "key": f"{s.chrom}-{s.pos}-{s.ref}-{s.alt}",
        "pred_logfc": s.logfc, "pred_abs": s.abs_logfc, "pred_jsd": s.jsd,
    } for s in scores])
    m = ann.merge(sdf, on="key", how="inner")
    print(f"scored + annotated variants: {len(m)} ({int(m['is_dav'].sum())} DAVs)")

    # 1. AUPRC (predicted |log2FC| ranks the DAVs)
    rr = ranking_report(m["is_dav"].values, m["pred_abs"].values)
    print("\n=== RANKING (recover the 164 DAVs) ===")
    print(" ", rr.summary())
    # also a combined score: |log2FC| * JSD (the integrative effect size)
    ies = (m["pred_abs"] * m["pred_jsd"]).values
    rr2 = ranking_report(m["is_dav"].values, ies)
    print("  IES (|log2FC|*JSD) AUPRC=%.3f (%.1fx base rate)" % (rr2.auprc, rr2.auprc_fold_over_baseline))

    # 2. effect-size correlation on the DAVs (measured logFC vs predicted)
    dav = m[m["is_dav"] == 1]
    cc = correlate_effects(dav["pred_logfc"].values, dav["logFC"].values)
    print("\n=== EFFECT SIZE (on the 164 DAVs) ===")
    print(" ", cc.summary())
    cc_all = correlate_effects(m["pred_logfc"].values, m["logFC"].values)
    print("  across all active variants:", cc_all.summary())

    # 3. motifbreakR honest framing
    n_dav = int(m["is_dav"].sum())
    mb = int((dav["motifbreakr"].notna()).sum())
    print("\n=== vs motifbreakR (honest) ===")
    print(f"  motifbreakR annotates a motif for {mb}/{n_dav} DAVs "
          f"({mb/n_dav:.0%}) = mechanism coverage, NOT recall.")
    print(f"  NCypher ranks all {len(m)} by predicted function (AUPRC {rr.auprc:.3f}) "
          f"and explains the mechanism via saliency - a different, stronger claim.")

    fig = plot_pr_curve(rr, title=f"NCypher recovers {n_dav} MPRA DAVs (developing cortex)",
                        motifbreakr_recall=mb / n_dav)
    fig.savefig("data/figures/mpra_pr_curve.png", dpi=150, bbox_inches="tight")
    m.to_csv(MPRA / "mpra_validation.result.tsv", sep="\t", index=False)
    print("\nwrote data/figures/mpra_pr_curve.png and data/mpra/mpra_validation.result.tsv")


if __name__ == "__main__":
    main()
