"""The convergence engine: NCypher's actual novelty.

Everyone in the Researcher track can run the Corces model and get a score; that
is the commodity baseline. NCypher's edge is to promote a variant only when the
evidence axes AGREE, surface the informative DISAGREEMENTS, and be honest about
out-of-domain calls. Three axes:

  - chromatin  (axis 2): ChromBPNet predicted accessibility effect
  - function   (axis 1): measured lentiMPRA allelic activity (Pollard 164 DAVs)
  - constraint (axis 3): Zoonomia phyloP evolutionary conservation

Output is a go/no-go memo (mirrors the PKU demo): validate X first, the decisive
experiment, and the kill criterion. That turns a scorer into a decision tool and
answers Pollard's "validation is the bottleneck" directly.

The chromatin high-impact threshold is calibrated per run (the ``chromatin_hi``
argument; e.g. the 99th percentile of a cohort background, 0.162 for the DMG sweep)
rather than the provisional 0.5 default, and the go/no-go memo quotes that same
calibrated value so a HOLD kill-criterion can never contradict the engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from nc_score.constraint import CONSTRAINT_THRESHOLD, PhyloPHit
from nc_score.scoring import ChromatinScore

# --- calibration knobs (PROVISIONAL; calibrate on the 164 DAVs, Day 2) -------
CHROMATIN_LOGFC_HI = 0.5      # |log2FC| above which the chromatin effect is "high"
CHROMATIN_JSD_HI = 0.05       # JSD above which profile shape is meaningfully changed
MPRA_LOG2FC_HI = 0.5          # measured allelic effect magnitude counted as active
IN_DOMAIN_CONTEXTS = {        # Trevino developing-brain contexts matched to DMG
    "trevino_2021.c15", "trevino_2021.c10", "trevino_2021.c11", "trevino_2021.c9",
}


@dataclass
class MPRAEvidence:
    """Axis 1: measured lentiMPRA allelic effect (only for variants in the set)."""

    measured_log2fc: float
    is_dav: bool  # differential-activity variant at 10% FDR


@dataclass
class AxisVote:
    name: str
    available: bool
    impactful: Optional[bool]     # None when not available
    detail: str


@dataclass
class NCypherCall:
    """The full triage verdict for one variant."""

    variant_id: str
    chrom: str
    pos: int
    ref: str
    alt: str
    context: Optional[str]

    votes: list[AxisVote]
    n_available: int
    n_impactful: int
    agreement: float              # n_impactful / n_available
    direction: str                # gain / loss / none (chromatin)
    promote: bool
    confidence: str               # high / medium / low / out-of-domain
    in_domain: bool

    memo: dict = field(default_factory=dict)
    axis_values: dict = field(default_factory=dict)


def _chromatin_vote(score: ChromatinScore, hi_threshold: float = CHROMATIN_LOGFC_HI) -> AxisVote:
    hi = score.abs_logfc >= hi_threshold or (score.jsd or 0) >= CHROMATIN_JSD_HI
    return AxisVote(
        name="chromatin",
        available=True,
        impactful=hi,
        detail=f"log2FC={score.logfc:+.2f}, JSD={score.jsd:.3f} ({score.direction})",
    )


def _constraint_vote(hit: Optional[PhyloPHit]) -> AxisVote:
    if hit is None or not hit.available:
        return AxisVote("constraint", False, None, "phyloP unavailable")
    return AxisVote(
        name="constraint",
        available=True,
        impactful=hit.constrained,
        detail=f"phyloP={hit.phylop:.2f} "
               f"({'constrained' if hit.constrained else 'unconstrained'} @ {CONSTRAINT_THRESHOLD})",
    )


def _function_vote(mpra: Optional[MPRAEvidence]) -> AxisVote:
    if mpra is None:
        return AxisVote("function", False, None, "not in the MPRA/DAV set")
    hi = mpra.is_dav or abs(mpra.measured_log2fc) >= MPRA_LOG2FC_HI
    return AxisVote(
        name="function",
        available=True,
        impactful=hi,
        detail=f"measured log2FC={mpra.measured_log2fc:+.2f}"
               f"{', DAV' if mpra.is_dav else ''}",
    )


def _confidence(in_domain: bool, n_available: int, agreement: float,
                active_quantile: Optional[float]) -> str:
    if not in_domain:
        return "out-of-domain"
    if n_available >= 2 and agreement >= 0.66 and (active_quantile or 0) >= 0.5:
        return "high"
    if agreement >= 0.5:
        return "medium"
    return "low"


def _memo(variant_id: str, promote: bool, direction: str, votes: list[AxisVote],
          confidence: str, context: Optional[str],
          chromatin_hi: float = CHROMATIN_LOGFC_HI) -> dict:
    """The go/no-go memo: decisive experiment + kill criterion."""
    line = "  ".join(v.detail for v in votes if v.available)
    if confidence == "out-of-domain":
        verdict = (f"NO-GO (out of domain): {variant_id} sits outside the "
                   "developing-brain contexts the model was trained on; the score is "
                   "not trustworthy here. Do not prioritise on this call.")
        experiment = "Re-score in a matched cell-type model before spending bench time."
        kill = "N/A - out-of-domain, deprioritise by default."
    elif promote:
        verdict = (f"GO: validate {variant_id} first. Evidence converges "
                   f"({line}); predicted chromatin {direction}.")
        experiment = ("Ref/alt reporter assay (lentiMPRA) or CRISPRi of this element in "
                      "an OPC-like line; confirm the allelic direction and the disrupted motif.")
        kill = (f"Deprioritise if measured allelic |log2FC| < {MPRA_LOG2FC_HI}, or if the "
                "axes fall below 2/3 agreement on re-test.")
    else:
        verdict = (f"HOLD: {variant_id} does not yet converge ({line}). "
                   "Informative disagreement, not a green light.")
        experiment = "Resolve the disagreeing axis (e.g. measure MPRA activity) before committing."
        kill = f"Drop if chromatin |log2FC| stays < {chromatin_hi:.3f} and constraint is absent."
    return {"context": context, "verdict": verdict,
            "decisive_experiment": experiment, "kill_criterion": kill}


def converge(
    chromatin: ChromatinScore,
    constraint: Optional[PhyloPHit] = None,
    mpra: Optional[MPRAEvidence] = None,
    chromatin_hi: float = CHROMATIN_LOGFC_HI,
) -> NCypherCall:
    """Combine the axes into a single triage verdict for one variant.

    ``chromatin_hi`` is the |log2FC| above which the chromatin effect counts as
    high impact. Pass a value calibrated to the model's dynamic range (e.g. the
    99th percentile of a cohort background) rather than the provisional default.
    """
    votes = [
        _chromatin_vote(chromatin, chromatin_hi),
        _function_vote(mpra),
        _constraint_vote(constraint),
    ]
    available = [v for v in votes if v.available]
    impactful = [v for v in available if v.impactful]
    n_available = len(available)
    n_impactful = len(impactful)
    agreement = n_impactful / n_available if n_available else 0.0

    in_domain = chromatin.context in IN_DOMAIN_CONTEXTS if chromatin.context else False
    # promote: chromatin must be impactful AND the axes must agree (>=2/3 of those
    # available), and the call must be in domain.
    chromatin_impactful = votes[0].impactful
    promote = bool(in_domain and chromatin_impactful and n_available >= 2 and agreement >= 0.66)
    confidence = _confidence(in_domain, n_available, agreement, chromatin.active_allele_quantile)

    return NCypherCall(
        variant_id=chromatin.variant_id,
        chrom=chromatin.chrom, pos=chromatin.pos, ref=chromatin.ref, alt=chromatin.alt,
        context=chromatin.context,
        votes=votes, n_available=n_available, n_impactful=n_impactful,
        agreement=agreement, direction=chromatin.direction,
        promote=promote, confidence=confidence, in_domain=in_domain,
        memo=_memo(chromatin.variant_id, promote, chromatin.direction, votes, confidence,
                   chromatin.context, chromatin_hi=chromatin_hi),
        axis_values={
            "logfc": chromatin.logfc, "jsd": chromatin.jsd,
            "active_allele_quantile": chromatin.active_allele_quantile,
            "phylop": constraint.phylop if constraint and constraint.available else None,
            "mpra_log2fc": mpra.measured_log2fc if mpra else None,
        },
    )
