"""Bootstrap confidence intervals for the caQTL validation, so the headline
progenitor AUROC 0.69 / 7.5x is not a single point, and so context-specificity
(progenitor > mismatched PsychENCODE) is tested directly, not asserted.

Method: 1,000 nonparametric bootstrap resamples of the scored variant pool. Per
context we recompute AUROC and AUPRC-fold-over-base-rate on each resample and take
the 2.5 / 97.5 percentiles. We also resample the WHOLE pool once per iteration and
compute (AUROC_progenitor - AUROC_mismatched) on the same resample, giving a CI on
the context-specificity gap; if that CI excludes 0 the "right cell context" claim is
statistically supported, not just descriptive.

Run: PYTHONPATH=src python scripts/bootstrap_caqtl.py
Honest notes: positives are rare (progenitor n=45), so CIs are wide by construction;
resamples with <1 positive or <1 negative for a given label are skipped and counted.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score

MPRA = Path("data/mpra")
N_BOOT = 1000
SEED = 0


def auroc(lab: np.ndarray, score: np.ndarray) -> float:
    return roc_auc_score(lab, score)


def auprc_fold(lab: np.ndarray, score: np.ndarray) -> float:
    base = lab.mean()
    if base == 0:
        return np.nan
    return average_precision_score(lab, score) / base


def load() -> pd.DataFrame:
    s2 = pd.read_excel(MPRA / "DataS2-Variant-library-ratios.xlsx", sheet_name="Primary")
    s2 = s2[(s2.alt_is_active == 1) | (s2.ref_is_active == 1)].copy()
    res = pd.read_csv(MPRA / "mpra_validation.result.tsv", sep="\t").merge(
        s2[["rsid", "cqtl_pec", "cqtl_liang_neuron", "cqtl_liang_progenitor"]],
        on="rsid", how="left")
    res["any_caqtl"] = ((res.cqtl_pec == 1) | (res.cqtl_liang_neuron == 1)
                        | (res.cqtl_liang_progenitor == 1)).astype(int)
    return res


def main():
    res = load()
    score = res.pred_abs.values.astype(float)
    panels = [("cqtl_liang_progenitor", "progenitor (matched)"),
              ("cqtl_liang_neuron", "neuron"),
              ("any_caqtl", "any"),
              ("cqtl_pec", "PsychENCODE (mismatched)")]
    labels = {col: (res[col] == 1).astype(int).values for col, _ in panels}

    rng = np.random.default_rng(SEED)
    n = len(res)
    idx_boot = [rng.integers(0, n, n) for _ in range(N_BOOT)]

    rows = []
    for col, name in panels:
        lab = labels[col]
        pt_auroc = auroc(lab, score)
        pt_fold = auprc_fold(lab, score)
        au, fo = [], []
        for idx in idx_boot:
            l, s = lab[idx], score[idx]
            if l.sum() < 1 or (1 - l).sum() < 1:
                continue
            au.append(auroc(l, s))
            fo.append(auprc_fold(l, s))
        au, fo = np.array(au), np.array(fo)
        rows.append({
            "context": name, "n_pos": int(lab.sum()),
            "auroc": round(pt_auroc, 3),
            "auroc_lo": round(np.percentile(au, 2.5), 3),
            "auroc_hi": round(np.percentile(au, 97.5), 3),
            "auprc_fold": round(pt_fold, 1),
            "fold_lo": round(np.percentile(fo, 2.5), 1),
            "fold_hi": round(np.percentile(fo, 97.5), 1),
            "n_valid_boot": len(au),
        })
        print(f"{name:26s} n={int(lab.sum()):3d}  AUROC {pt_auroc:.3f} "
              f"[{np.percentile(au,2.5):.3f}, {np.percentile(au,97.5):.3f}]  "
              f"AUPRC {pt_fold:.1f}x [{np.percentile(fo,2.5):.1f}, {np.percentile(fo,97.5):.1f}]")

    # Context-specificity gap: progenitor AUROC minus mismatched AUROC, same resample
    prog, mis = labels["cqtl_liang_progenitor"], labels["cqtl_pec"]
    gaps = []
    for idx in idx_boot:
        s = score[idx]
        lp, lm = prog[idx], mis[idx]
        if lp.sum() < 1 or (1 - lp).sum() < 1 or lm.sum() < 1 or (1 - lm).sum() < 1:
            continue
        gaps.append(auroc(lp, s) - auroc(lm, s))
    gaps = np.array(gaps)
    gap_pt = auroc(prog, score) - auroc(mis, score)
    lo, hi = np.percentile(gaps, 2.5), np.percentile(gaps, 97.5)
    frac_pos = float((gaps > 0).mean())
    print("\ncontext-specificity gap (progenitor AUROC - mismatched AUROC):")
    print(f"  point {gap_pt:+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]  "
          f"P(gap>0)={frac_pos:.3f}  ({'excludes 0' if lo > 0 else 'includes 0'})")

    df = pd.DataFrame(rows)
    df.to_csv(MPRA / "caqtl_bootstrap_ci.tsv", sep="\t", index=False)
    with open(MPRA / "caqtl_bootstrap_gap.txt", "w") as fh:
        fh.write(f"progenitor-minus-mismatched AUROC gap: point {gap_pt:+.3f}, "
                 f"95% CI [{lo:+.3f}, {hi:+.3f}], P(gap>0)={frac_pos:.3f}, "
                 f"n_boot={N_BOOT}, seed={SEED}\n")
    print(f"\nwrote {MPRA/'caqtl_bootstrap_ci.tsv'} and caqtl_bootstrap_gap.txt")


if __name__ == "__main__":
    main()
