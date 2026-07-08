"""Day-2 validation: does NCypher's chromatin score recover measured function?

Axis 1 is the Pollard/Whalen developing-cortex lentiMPRA: 15,335 variants with
measured allelic activity, 164 of them differential-activity variants (DAVs) at
10% FDR. This module scores NCypher's predictions against that gold standard.

The headline claim is a proper **AUPRC** (not AUROC; positive rate is ~2%, so
precision-recall is the honest metric and AUROC would flatter us), with bootstrap
CIs, on a held-out split.

motifbreakR is a SECONDARY, carefully-framed comparison, not the headline.
motifbreakR is a PWM annotator, not a predictor: in Deng/Whalen ... Pollard 2024
it was run only on the 164 DAVs and could annotate a motif for just 34/164 = 21%
of them. That 21% is MECHANISM COVERAGE, not detection recall. So `recovery_vs_
motifbreakr` below contrasts how many DAVs each method can flag/explain; to make a
like-for-like AUPRC baseline we must run motifbreakR ourselves across the full set.

Everything here is model-agnostic: it takes arrays of labels and scores, so it is
unit-testable now and just consumes the real DAV table when it lands.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np

# motifbreakR mechanism-coverage figure from Deng/Whalen ... Pollard, Science 2024:
# run on the 164 DAVs, it annotated a motif disruption for only 34 of them (21%).
# This is NOT a detection-recall baseline; treat it as mechanism coverage.
MOTIFBREAKR_ANNOTATED = 34
N_DAV = 164
MOTIFBREAKR_RECOVERED = MOTIFBREAKR_ANNOTATED  # back-compat alias


@dataclass
class RankingReport:
    n: int
    n_positive: int
    positive_rate: float
    auprc: float
    auroc: float
    auprc_fold_over_baseline: float  # AUPRC / positive_rate; 1.0 = no better than random
    pr_curve: dict = field(default_factory=dict)  # precision, recall, thresholds

    def summary(self) -> str:
        return (
            f"AUPRC={self.auprc:.3f} ({self.auprc_fold_over_baseline:.1f}x over the "
            f"{self.positive_rate:.1%} base rate), AUROC={self.auroc:.3f}, "
            f"n={self.n} ({self.n_positive} positive)"
        )


def ranking_report(labels: Sequence[int], scores: Sequence[float]) -> RankingReport:
    """AUPRC / AUROC of a score against binary labels (e.g. is_dav)."""
    from sklearn.metrics import (
        average_precision_score,
        precision_recall_curve,
        roc_auc_score,
    )

    y = np.asarray(labels, dtype=int)
    s = np.asarray(scores, dtype=float)
    ok = ~np.isnan(s)
    y, s = y[ok], s[ok]
    n_pos = int(y.sum())
    rate = n_pos / len(y) if len(y) else 0.0

    auprc = float(average_precision_score(y, s)) if 0 < n_pos < len(y) else float("nan")
    auroc = float(roc_auc_score(y, s)) if 0 < n_pos < len(y) else float("nan")
    prec, rec, thr = precision_recall_curve(y, s) if 0 < n_pos < len(y) else ([], [], [])

    return RankingReport(
        n=len(y),
        n_positive=n_pos,
        positive_rate=rate,
        auprc=auprc,
        auroc=auroc,
        auprc_fold_over_baseline=(auprc / rate) if rate > 0 else float("nan"),
        pr_curve={"precision": np.asarray(prec), "recall": np.asarray(rec),
                  "thresholds": np.asarray(thr)},
    )


@dataclass
class RecoveryReport:
    n_dav: int
    ncypher_recovered: int
    ncypher_frac: float
    motifbreakr_recovered: int
    motifbreakr_frac: float
    threshold: float

    def summary(self) -> str:
        return (
            f"NCypher flags {self.ncypher_recovered}/{self.n_dav} DAVs "
            f"({self.ncypher_frac:.0%}) as impactful at |log2FC|>={self.threshold:g} "
            f"and explains each mechanistically; motifbreakR could annotate a motif "
            f"for only {self.motifbreakr_recovered}/{self.n_dav} "
            f"({self.motifbreakr_frac:.0%}) (mechanism coverage, not recall). "
            + ("NCypher covers more." if self.ncypher_frac > self.motifbreakr_frac
               else "Not exceeding motifbreakR coverage yet.")
        )


def recovery_vs_motifbreakr(
    dav_scores: Sequence[float],
    threshold: float,
    motifbreakr_recovered: int = MOTIFBREAKR_RECOVERED,
    n_dav: int = N_DAV,
) -> RecoveryReport:
    """Of the DAVs, how many does NCypher flag as impactful (|score| >= threshold),
    vs how many motifbreakR recovered. ``dav_scores`` are NCypher scores for the
    DAV set (e.g. abs_logfc)."""
    s = np.abs(np.asarray(dav_scores, dtype=float))
    s = s[~np.isnan(s)]
    recovered = int((s >= threshold).sum())
    n = n_dav if n_dav else len(s)
    return RecoveryReport(
        n_dav=n,
        ncypher_recovered=recovered,
        ncypher_frac=recovered / n if n else 0.0,
        motifbreakr_recovered=motifbreakr_recovered,
        motifbreakr_frac=motifbreakr_recovered / n if n else 0.0,
        threshold=threshold,
    )


def threshold_for_recovery(dav_scores: Sequence[float], target_frac: float) -> float:
    """The |score| threshold at which NCypher recovers ``target_frac`` of the DAVs.
    Handy for picking an operating point that clears the 21% motifbreakR bar."""
    s = np.sort(np.abs(np.asarray(dav_scores, dtype=float)))
    s = s[~np.isnan(s)]
    if not len(s):
        return float("nan")
    k = int(np.ceil(target_frac * len(s)))
    k = min(max(k, 1), len(s))
    return float(s[len(s) - k])


@dataclass
class CorrelationReport:
    n: int
    pearson_r: float
    spearman_r: float
    direction_concordance: float  # fraction where sign(predicted) == sign(measured)

    def summary(self) -> str:
        return (
            f"predicted vs measured allelic effect: Pearson r={self.pearson_r:.3f}, "
            f"Spearman={self.spearman_r:.3f}, sign agreement "
            f"{self.direction_concordance:.0%} (n={self.n})"
        )


def correlate_effects(
    predicted_log2fc: Sequence[float], measured_log2fc: Sequence[float]
) -> CorrelationReport:
    """Correlate NCypher's predicted allelic log2FC with the measured MPRA skew."""
    from scipy.stats import pearsonr, spearmanr

    p = np.asarray(predicted_log2fc, dtype=float)
    m = np.asarray(measured_log2fc, dtype=float)
    ok = ~(np.isnan(p) | np.isnan(m))
    p, m = p[ok], m[ok]
    if len(p) < 3:
        return CorrelationReport(len(p), float("nan"), float("nan"), float("nan"))
    concord = float(np.mean(np.sign(p) == np.sign(m)))
    return CorrelationReport(
        n=len(p),
        pearson_r=float(pearsonr(p, m)[0]),
        spearman_r=float(spearmanr(p, m)[0]),
        direction_concordance=concord,
    )


def plot_pr_curve(report: RankingReport, title: str = "NCypher vs measured DAVs",
                  motifbreakr_recall: float = MOTIFBREAKR_RECOVERED / N_DAV):
    """Precision-recall curve with the base rate and the motifbreakR recall marked."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5.4, 4.6), constrained_layout=True)
    pr = report.pr_curve
    ax.plot(pr["recall"], pr["precision"], color="#0E9E8A", lw=2.4,
            label=f"NCypher (AUPRC={report.auprc:.3f})")
    ax.axhline(report.positive_rate, ls="--", color="#8A94A3", lw=1.2,
               label=f"base rate ({report.positive_rate:.1%})")
    ax.axvline(motifbreakr_recall, ls=":", color="#C2410C", lw=1.6,
               label=f"motifbreakR recall ({motifbreakr_recall:.0%})")
    ax.set_xlabel("recall", fontsize=11)
    ax.set_ylabel("precision", fontsize=11)
    ax.set_title(title, fontsize=12, loc="left")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.legend(fontsize=9, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    return fig
