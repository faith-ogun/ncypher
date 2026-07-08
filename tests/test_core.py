"""Offline unit tests for NCypher's local core (no network, no reference).

Run: PYTHONPATH=src python -m pytest tests/test_core.py -q
"""

import numpy as np
import pytest

from nc_score.constraint import CONSTRAINT_THRESHOLD, constraint_enrichment
from nc_score.genome import one_hot
from nc_score.variants import Variant


def test_variant_parse_and_normalise():
    v = Variant.parse("7-5530601-a-g", label="x")
    assert v.chrom == "chr7" and v.pos == 5530601
    assert v.ref == "A" and v.alt == "G"  # upper-cased
    assert v.pos0 == 5530600 and v.is_snv
    assert v.id == "chr7-5530601-A-G"


def test_variant_window_centres_on_base():
    v = Variant("chr1", 1000, "A", "T")
    chrom, start, end = v.window(2114)
    assert chrom == "chr1"
    assert end - start == 2114
    assert start <= v.pos0 < end
    assert v.pos0 - start == 2114 // 2  # variant sits on the centre base


def test_variant_rejects_bad_input():
    with pytest.raises(ValueError):
        Variant("chr1", 0, "A", "T")  # 1-based, pos>=1
    with pytest.raises(ValueError):
        Variant("chr1", 10, "A", "Z")  # non-ACGT
    with pytest.raises(ValueError):
        Variant.parse("not-a-variant")


def test_one_hot_encoding():
    oh = one_hot("ACGTN")
    assert oh.shape == (5, 4)
    assert np.array_equal(oh[0], [1, 0, 0, 0])  # A
    assert np.array_equal(oh[3], [0, 0, 0, 1])  # T
    assert np.array_equal(oh[4], [0, 0, 0, 0])  # N -> all zero


def test_constraint_enrichment_is_monotonic():
    # phyloP built to rise with impact: bins should show increasing constraint.
    rng = np.random.default_rng(0)
    impact = rng.random(500)
    phylop = -1 + 5 * impact + rng.normal(0, 0.4, 500)
    rows = constraint_enrichment(impact, phylop, n_bins=5)
    assert len(rows) == 5
    means = [r["mean_phylop"] for r in rows]
    fracs = [r["frac_constrained"] for r in rows]
    assert means == sorted(means)          # monotonic mean phyloP
    assert fracs[-1] > fracs[0]            # more constrained in the top bin
    assert 0.0 <= fracs[0] <= fracs[-1] <= 1.0


def test_constraint_enrichment_handles_nans():
    impact = [0.1, 0.5, np.nan, 0.9]
    phylop = [0.0, np.nan, 2.0, 3.0]
    rows = constraint_enrichment(impact, phylop, n_bins=2)
    # only the two rows with both values present survive
    assert sum(r["n"] for r in rows) == 2


def test_constraint_threshold_value():
    assert CONSTRAINT_THRESHOLD == 2.27


# --- convergence engine ------------------------------------------------------
from nc_score.constraint import PhyloPHit  # noqa: E402
from nc_score.converge import MPRAEvidence, converge  # noqa: E402
from nc_score.scoring import ChromatinScore  # noqa: E402


def _chrom(logfc=1.2, jsd=0.09, ctx="trevino_2021.c15", aaq=0.9):
    return ChromatinScore("v", "chr5", 1295113, "G", "A", logfc=logfc,
                          abs_logfc=abs(logfc), jsd=jsd, active_allele_quantile=aaq,
                          context=ctx)


def test_converge_promotes_when_axes_agree_in_domain():
    call = converge(
        _chrom(),
        PhyloPHit(Variant("chr5", 1295113, "G", "A"), phylop=3.1, constrained=True),
        MPRAEvidence(measured_log2fc=1.0, is_dav=True),
    )
    assert call.promote and call.in_domain
    assert call.confidence == "high"
    assert call.agreement == 1.0
    assert call.memo["verdict"].startswith("GO")


def test_converge_flags_out_of_domain():
    call = converge(_chrom(ctx="breast_x"))
    assert not call.promote
    assert call.confidence == "out-of-domain"
    assert "NO-GO" in call.memo["verdict"]


def test_converge_holds_on_disagreement():
    # in-domain, high chromatin, but unconstrained and no MPRA -> should not promote
    call = converge(
        _chrom(),
        PhyloPHit(Variant("chr5", 1295113, "G", "A"), phylop=0.1, constrained=False),
    )
    assert not call.promote
    assert call.memo["verdict"].startswith("HOLD")


def test_converge_counts_only_available_axes():
    call = converge(_chrom())  # chromatin only
    assert call.n_available == 1
    assert not call.promote  # needs >= 2 axes to promote


# --- validation harness ------------------------------------------------------
from nc_score.validate import (  # noqa: E402
    ranking_report, recovery_vs_motifbreakr, threshold_for_recovery, correlate_effects,
)


def test_ranking_report_separates_positives():
    rng = np.random.default_rng(1)
    labels = np.array([1] * 50 + [0] * 950)
    rng.shuffle(labels)
    # scores strongly separate the classes -> high AUPRC well above base rate
    scores = labels * 1.0 + rng.normal(0, 0.2, labels.size)
    rr = ranking_report(labels, scores)
    assert rr.n_positive == 50
    assert 0.04 < rr.positive_rate < 0.06
    assert rr.auprc > 0.5
    assert rr.auprc_fold_over_baseline > 5


def test_recovery_beats_motifbreakr_when_scores_high():
    dav = np.array([0.8] * 100 + [0.1] * 64)  # 100/164 clear a 0.5 threshold
    rec = recovery_vs_motifbreakr(dav, threshold=0.5)
    assert rec.ncypher_recovered == 100
    assert rec.ncypher_frac > rec.motifbreakr_frac
    assert "covers more" in rec.summary().lower()


def test_threshold_for_recovery_targets_fraction():
    dav = np.linspace(0.0, 1.0, 164)
    thr = threshold_for_recovery(dav, 0.5)  # threshold recovering ~half
    frac = (np.abs(dav) >= thr).mean()
    assert 0.45 <= frac <= 0.55


def test_correlate_effects_direction():
    pred = np.array([1.0, -1.0, 0.5, -0.5, 2.0])
    meas = np.array([0.8, -0.9, 0.4, -0.3, 1.5])
    cc = correlate_effects(pred, meas)
    assert cc.pearson_r > 0.9
    assert cc.direction_concordance == 1.0
