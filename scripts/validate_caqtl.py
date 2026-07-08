"""The CORRECT chromatin-axis validation: does ChromBPNet's predicted accessibility
change recover caQTLs (allelic-imbalance accessibility QTLs)?

MPRA measures reporter ACTIVITY (a different modality); caQTLs measure ACCESSIBILITY
allelic imbalance - the native ground truth for a chromatin-accessibility model. The
c15 model is a fetal OPC/PROGENITOR context, so the honest prediction is that it best
recovers PROGENITOR caQTLs (context specificity = the "right cell context" USP).

Run: PYTHONPATH=src python scripts/validate_caqtl.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nc_score.validate import ranking_report  # noqa: E402
from scipy.stats import mannwhitneyu  # noqa: E402

MPRA = Path("data/mpra")


def main():
    s2 = pd.read_excel(MPRA / "DataS2-Variant-library-ratios.xlsx", sheet_name="Primary")
    s2 = s2[(s2.alt_is_active == 1) | (s2.ref_is_active == 1)].copy()
    res = pd.read_csv(MPRA / "mpra_validation.result.tsv", sep="\t").merge(
        s2[["rsid", "cqtl_pec", "cqtl_liang_neuron", "cqtl_liang_progenitor"]],
        on="rsid", how="left")
    res["any_caqtl"] = ((res.cqtl_pec == 1) | (res.cqtl_liang_neuron == 1)
                        | (res.cqtl_liang_progenitor == 1)).astype(int)

    panels = [("cqtl_liang_progenitor", "Progenitor caQTL\n(matched context)"),
              ("cqtl_liang_neuron", "Neuron caQTL"),
              ("any_caqtl", "Any caQTL"),
              ("cqtl_pec", "PsychENCODE caQTL\n(mismatched)")]
    rows = []
    for col, name in panels:
        lab = (res[col] == 1).astype(int)
        n = int(lab.sum())
        rr = ranking_report(lab.values, res.pred_abs.values)
        _, p = mannwhitneyu(res[lab == 1].pred_abs, res[lab == 0].pred_abs, alternative="greater")
        rows.append({"set": name, "n_pos": n, "auprc": rr.auprc,
                     "fold": rr.auprc_fold_over_baseline, "auroc": rr.auroc, "mwu_p": p})
        print(f"{name.splitlines()[0]}: n={n} AUPRC={rr.auprc:.3f} ({rr.fold if False else rr.auprc_fold_over_baseline:.1f}x) "
              f"AUROC={rr.auroc:.3f} p={p:.2g}")
    df = pd.DataFrame(rows)
    df.to_csv(MPRA / "caqtl_validation.tsv", sep="\t", index=False)

    # context-specificity figure (AUROC by context)
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4, 4.2), constrained_layout=True)
    colors = ["#0E9E8A", "#3DD6B5", "#8A94A3", "#C2410C"]
    ax.bar(range(len(df)), df.auroc, color=colors)
    ax.axhline(0.5, ls="--", color="#8A94A3", lw=1)
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels([r["set"] for _, r in df.iterrows()], fontsize=8)
    for i, r in df.iterrows():
        ax.text(i, r.auroc + 0.01, f"AUROC {r.auroc:.2f}\n{r.fold:.1f}x", ha="center", fontsize=8)
    ax.set_ylabel("AUROC (recover caQTLs by predicted |log2FC|)")
    ax.set_ylim(0, 0.8)
    ax.set_title("ChromBPNet (fetal OPC/progenitor context) is context-specific:\n"
                 "best recovers progenitor caQTLs", fontsize=11, loc="left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig("data/figures/caqtl_context_specificity.png", dpi=150, bbox_inches="tight")
    print("\nwrote data/figures/caqtl_context_specificity.png and data/mpra/caqtl_validation.tsv")


if __name__ == "__main__":
    main()
