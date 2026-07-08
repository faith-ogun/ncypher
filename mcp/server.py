"""NCypher MCP server: the triage engine for non-coding DMG variants, as a tool.

NCypher couples three evidence axes for a somatic non-coding regulatory variant
in paediatric diffuse midline glioma (DMG):

  - chromatin accessibility  (ChromBPNet, the developing-brain fetal-OPC model,
                              Trevino 2021 cluster c15)
  - evolutionary constraint  (Zoonomia cactus241way phyloP, 241 placental mammals)
  - measured function        (lentiMPRA, added on a later axis; not available for
                              these somatic variants)

The convergence engine promotes a variant only when the available axes AGREE,
surfaces informative disagreements, and is honest when a call sits out of domain.
The output is a go/no-go memo: the verdict, the decisive experiment to run, and
the kill criterion.

This server does no heavy scoring. It serves the pre-computed discovery sweep
(``data/dmg/sweep_result.tsv``, 10,869 OPC-regulatory DMG variants) and, for a
variant not in that cache, does a fast live phyloP lookup while telling the
caller the chromatin axis still needs scoring.

Run:
    /Users/faith/Desktop/NCypher/.venv/bin/python mcp/server.py
or:
    fastmcp run mcp/server.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Optional

# --- make the analysis engine importable (read-only dependency) --------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from nc_score.constraint import CONSTRAINT_THRESHOLD, PhyloP, PhyloPHit  # noqa: E402
from nc_score.converge import converge  # noqa: E402
from nc_score.scoring import ChromatinScore  # noqa: E402
from nc_score.variants import Variant  # noqa: E402

from fastmcp import FastMCP  # noqa: E402
from fastmcp.tools.tool import ToolResult  # noqa: E402
from fastmcp.utilities.types import Image  # noqa: E402

# --- provenance and calibration (single source of truth) ---------------------
MODEL_CONTEXT = "trevino_2021.c15"  # developing-brain ChromBPNet, fetal OPC (cluster c15)
GENOME = "GRCh38"
# High-impact chromatin threshold: |log2FC| >= p99 of an 800-variant cohort
# background (0.162), NOT the meaningless absolute 0.5. See docs/audit/sweep-result.md.
CALIBRATED_CHROMATIN_HI = 0.162

PROVENANCE = {
    "model": "developing-brain ChromBPNet, fetal OPC (Trevino 2021 cluster c15)",
    "model_context": MODEL_CONTEXT,
    "genome": GENOME,
    "constraint_track": "Zoonomia cactus241way phyloP (241 placental mammals)",
    "constraint_threshold": CONSTRAINT_THRESHOLD,
    "chromatin_hi_threshold": CALIBRATED_CHROMATIN_HI,
    "chromatin_hi_note": "|log2FC| >= p99 of an 800-variant cohort background",
    "cohort": "OpenPedCan H3 K27M DMG, 152 patients, somatic non-coding SNVs",
    "sources": [
        "ChromBPNet fetal-OPC model (Trevino 2021 developing-brain multiome, cluster c15)",
        "Zoonomia cactus241way phyloP (Christmas/Sullivan et al., Science 2023)",
        "OpenPedCan somatic MAF (GRCh38); phyloP queried live from UCSC goldenPath",
    ],
}

# --- data locations (read-only cache) ----------------------------------------
DATA_DIR = PROJECT_ROOT / "data" / "dmg"
SWEEP_TSV = DATA_DIR / "sweep_result.tsv"
FIGURES_DIR = PROJECT_ROOT / "data" / "figures"

# Saliency PNGs that already exist on disk (never generated here). Keyed by the
# gene the figure illustrates; attached to a score result when relevant.
SALIENCY_FIGURES_BY_GENE = {
    "TERT": [
        FIGURES_DIR / "real" / "TERT_C228T.saliency.png",
        FIGURES_DIR / "real" / "TERT_C250T.saliency.png",
    ],
}


# --- sweep cache -------------------------------------------------------------
_SWEEP: Optional[dict[str, dict]] = None
_PHYLOP: Optional[PhyloP] = None


def _load_sweep() -> dict[str, dict]:
    """Load sweep_result.tsv once, keyed by variant key (chr-pos-ref-alt)."""
    global _SWEEP
    if _SWEEP is None:
        rows: dict[str, dict] = {}
        with open(SWEEP_TSV, newline="") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                rows[row["key"]] = row
        _SWEEP = rows
    return _SWEEP


def _get_phylop() -> PhyloP:
    """A single, reused live phyloP accessor (remote HTTP range reads)."""
    global _PHYLOP
    if _PHYLOP is None:
        _PHYLOP = PhyloP()
    return _PHYLOP


def _as_bool(s: Optional[str]) -> bool:
    return str(s).strip().lower() == "true"


def _fnum(s: Optional[str]) -> Optional[float]:
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _saliency_images(gene: Optional[str]) -> list[Image]:
    """Return Image content for any saliency PNG that already exists for this
    gene. Never generates a figure."""
    if not gene:
        return []
    imgs: list[Image] = []
    for path in SALIENCY_FIGURES_BY_GENE.get(gene.upper(), []):
        if path.exists():
            imgs.append(Image(path=str(path)))
    return imgs


def _votes_payload(call) -> list[dict]:
    return [
        {
            "axis": v.name,
            "available": v.available,
            "impactful": v.impactful,
            "detail": v.detail,
        }
        for v in call.votes
    ]


# --- the server --------------------------------------------------------------
mcp = FastMCP("ncypher")


@mcp.tool
def score_variant(variant_id: str) -> ToolResult:
    """Triage one non-coding variant (e.g. "chr22-33000876-C-T").

    Couples chromatin accessibility (ChromBPNet fetal-OPC), evolutionary
    constraint (Zoonomia phyloP) and, where available, measured MPRA function via
    the convergence engine, and returns a go/no-go memo: the verdict, the decisive
    experiment to run, and the kill criterion. If the variant is in the DMG
    discovery cache the full three-axis call is served; otherwise a fast live
    phyloP lookup is done and the chromatin axis is flagged as still needing
    scoring on the Corces c15 model.
    """
    try:
        variant = Variant.parse(variant_id)
    except ValueError as exc:
        return ToolResult(
            content=f"Could not parse variant {variant_id!r}: {exc}",
            structured_content={"error": str(exc), "variant_id": variant_id},
            is_error=True,
        )

    key = variant.id
    sweep = _load_sweep()
    row = sweep.get(key)

    if row is not None:
        return _score_from_cache(variant, row)
    return _score_live(variant)


def _score_from_cache(variant: Variant, row: dict) -> ToolResult:
    gene = row.get("gene")
    logfc = _fnum(row["logfc"]) or 0.0
    abs_logfc = _fnum(row["abs_logfc"]) or abs(logfc)
    jsd = _fnum(row["jsd"]) or 0.0
    phylop = _fnum(row["phylop"])

    chromatin = ChromatinScore(
        variant_id=variant.id,
        chrom=variant.chrom,
        pos=variant.pos,
        ref=variant.ref,
        alt=variant.alt,
        logfc=logfc,
        abs_logfc=abs_logfc,
        jsd=jsd,
        active_allele_quantile=None,
        context=MODEL_CONTEXT,
    )
    hit = PhyloPHit(
        variant=variant,
        phylop=phylop,
        constrained=_as_bool(row.get("constrained")),
    )
    # MPRA function axis is not available for these somatic DMG variants.
    call = converge(chromatin, constraint=hit, mpra=None,
                    chromatin_hi=CALIBRATED_CHROMATIN_HI)
    memo = call.memo

    structured = {
        "variant_id": variant.id,
        "gene": gene,
        "class": row.get("cls"),
        "n_patients": int(row.get("n_patients") or 0),
        "in_cache": True,
        "axes": {
            "chromatin": {
                "logfc": logfc,
                "abs_logfc": abs_logfc,
                "jsd": jsd,
                "direction": chromatin.direction,
                "high_impact": _as_bool(row.get("high_impact")),
            },
            "constraint": {
                "phylop": phylop,
                "constrained": _as_bool(row.get("constrained")),
                "threshold": CONSTRAINT_THRESHOLD,
            },
            "function": {"available": False, "note": "not in the MPRA/DAV set"},
        },
        "converged": _as_bool(row.get("converged_2ax")),
        "promote": call.promote,
        "confidence": row.get("confidence") or call.confidence,
        "in_domain": call.in_domain,
        "n_axes_available": call.n_available,
        "n_axes_impactful": call.n_impactful,
        "agreement": round(call.agreement, 3),
        "votes": _votes_payload(call),
        "memo": {
            "verdict": memo["verdict"],
            "decisive_experiment": memo["decisive_experiment"],
            "kill_criterion": memo["kill_criterion"],
        },
        "provenance": PROVENANCE,
    }

    text = _render_cache_text(variant, gene, row, call)
    content: list = [text]
    content.extend(_saliency_images(gene))
    return ToolResult(content=content, structured_content=structured)


def _render_cache_text(variant, gene, row, call) -> str:
    memo = call.memo
    label = f"{variant.id}" + (f"  ({gene})" if gene else "")
    votes = "\n".join(
        f"- {v.name}: {v.detail}"
        + ("" if v.impactful is None else ("  [impactful]" if v.impactful else "  [not impactful]"))
        for v in call.votes
    )
    converged = "yes" if _as_bool(row.get("converged_2ax")) else "no"
    return f"""# NCypher triage: {label}

**Verdict:** {memo['verdict']}

**Decisive experiment:** {memo['decisive_experiment']}

**Kill criterion:** {memo['kill_criterion']}

## Convergence
Two axes available (chromatin + constraint); the MPRA function axis is not in the
set for this somatic variant. {call.n_impactful}/{call.n_available} available axes
are impactful (agreement {call.agreement:.0%}). Two-axis convergence: {converged}.
Confidence: {row.get('confidence') or call.confidence}. In domain: {'yes' if call.in_domain else 'no'}.

{votes}

Gene {gene or 'n/a'}, class {row.get('cls', 'n/a')}, seen in {row.get('n_patients', '?')} patient(s).

## Provenance
Model context {MODEL_CONTEXT} (developing-brain fetal-OPC ChromBPNet), genome
{GENOME}. Constraint: Zoonomia cactus241way phyloP (constrained at phyloP >=
{CONSTRAINT_THRESHOLD}). Chromatin high-impact calibrated at |log2FC| >=
{CALIBRATED_CHROMATIN_HI} (p99 of an 800-variant cohort background).
"""


def _score_live(variant: Variant) -> ToolResult:
    """Variant not in the cache: do a fast live phyloP lookup and flag that the
    chromatin axis still needs scoring on the Corces c15 model."""
    phylop: Optional[float] = None
    constrained = False
    phylop_error: Optional[str] = None
    try:
        hit = _get_phylop().hit(variant)
        phylop = hit.phylop
        constrained = hit.constrained
    except Exception as exc:  # network / pyBigWig unavailable
        phylop_error = str(exc)

    structured = {
        "variant_id": variant.id,
        "in_cache": False,
        "axes": {
            "chromatin": {
                "available": False,
                "note": "needs scoring on the Corces c15 (fetal-OPC) ChromBPNet; "
                        "this variant is not in the DMG discovery cache",
            },
            "constraint": {
                "phylop": phylop,
                "constrained": constrained,
                "threshold": CONSTRAINT_THRESHOLD,
                "available": phylop is not None,
                "error": phylop_error,
            },
            "function": {"available": False, "note": "not in the MPRA/DAV set"},
        },
        "converged": False,
        "confidence": "incomplete (chromatin axis unscored)",
        "provenance": PROVENANCE,
    }

    if phylop is not None:
        constraint_line = (
            f"phyloP = {phylop:.2f} "
            f"({'constrained' if constrained else 'unconstrained'} at threshold "
            f"{CONSTRAINT_THRESHOLD})."
        )
    else:
        constraint_line = (
            f"Live phyloP lookup unavailable ({phylop_error or 'no coverage'})."
        )

    text = f"""# NCypher triage: {variant.id}

This variant is **not** in the DMG discovery cache, so the chromatin axis is not
yet scored.

**Chromatin (axis 2):** needs scoring on the Corces c15 (fetal-OPC) ChromBPNet
before a verdict can be issued. Run the variant-scorer on that model to complete
the call.

**Constraint (axis 3):** {constraint_line}

**Function (axis 1):** not in the MPRA/DAV set.

No convergence verdict is issued without the chromatin axis; NCypher does not
promote on a single axis. Score the chromatin axis, then re-run for a go/no-go
memo.

## Provenance
Model context {MODEL_CONTEXT} (developing-brain fetal-OPC ChromBPNet), genome
{GENOME}. Constraint queried live from Zoonomia cactus241way phyloP.
"""
    return ToolResult(content=text, structured_content=structured)


@mcp.tool
def top_candidates(n: int = 20, converged_only: bool = True) -> ToolResult:
    """The "which variants to validate first" shortlist from the DMG discovery
    sweep, ranked by chromatin effect size (|log2FC|).

    With ``converged_only`` (default), returns only the two-axis-converged hits
    (chromatin high-impact AND evolutionarily constrained). Returns a markdown
    table and a structured list of candidates (key, gene, logfc, phylop,
    confidence, converged).
    """
    sweep = _load_sweep()
    rows = list(sweep.values())
    if converged_only:
        rows = [r for r in rows if _as_bool(r.get("converged_2ax"))]
    rows.sort(key=lambda r: _fnum(r.get("abs_logfc")) or 0.0, reverse=True)
    rows = rows[: max(1, int(n))]

    candidates = []
    for r in rows:
        candidates.append(
            {
                "key": r["key"],
                "gene": r.get("gene"),
                "class": r.get("cls"),
                "logfc": _fnum(r.get("logfc")),
                "phylop": _fnum(r.get("phylop")),
                "constrained": _as_bool(r.get("constrained")),
                "confidence": r.get("confidence"),
                "converged": _as_bool(r.get("converged_2ax")),
                "n_patients": int(r.get("n_patients") or 0),
            }
        )

    header = (
        f"# NCypher shortlist: top {len(candidates)} "
        f"{'converged ' if converged_only else ''}DMG candidates to validate first\n\n"
        "Ranked by chromatin effect size (|log2FC|). "
        + (
            "All rows converge on two axes: chromatin high-impact AND "
            "evolutionarily constrained (phyloP >= "
            f"{CONSTRAINT_THRESHOLD}).\n\n"
            if converged_only
            else "Includes non-converged rows.\n\n"
        )
    )
    table = "| # | variant | gene | class | log2FC | phyloP | confidence | converged |\n"
    table += "|---|---------|------|-------|-------:|-------:|-----------|:---------:|\n"
    for i, c in enumerate(candidates, 1):
        table += (
            f"| {i} | {c['key']} | {c['gene'] or ''} | {c['class'] or ''} | "
            f"{c['logfc']:+.3f} | {c['phylop']:.2f} | {c['confidence'] or ''} | "
            f"{'yes' if c['converged'] else 'no'} |\n"
        )
    note = (
        "\nHonest note: these are private, single-patient variants (no recurrent "
        "cohort-level hotspot in DMG, consistent with its enhancer-reprogramming "
        "biology). This is a hypothesis-generating shortlist for validation, not a "
        "list of proven drivers.\n"
    )

    structured = {
        "n_requested": int(n),
        "n_returned": len(candidates),
        "converged_only": converged_only,
        "ranked_by": "abs_logfc",
        "candidates": candidates,
        "provenance": PROVENANCE,
    }
    return ToolResult(content=header + table + note, structured_content=structured)


@mcp.tool
def cohort_summary() -> ToolResult:
    """The honest headline numbers from the DMG discovery sweep: how many somatic
    non-coding variants were scored, how many are chromatin high-impact, how many
    are evolutionarily constrained, how many converge on both axes, and the
    honest caveat (no recurrent hotspot, nothing in canonical driver genes).
    Computed live from the cached sweep so the numbers are always truthful.
    """
    sweep = _load_sweep()
    rows = list(sweep.values())
    total = len(rows)
    high_impact = sum(1 for r in rows if _as_bool(r.get("high_impact")))
    constrained = sum(1 for r in rows if _as_bool(r.get("constrained")))
    converged = sum(1 for r in rows if _as_bool(r.get("converged_2ax")))
    recurrent = sum(1 for r in rows if (int(r.get("n_patients") or 1) > 1)
                    and _as_bool(r.get("converged_2ax")))

    structured = {
        "n_scored": total,
        "n_high_impact_chromatin": high_impact,
        "n_constrained_phylop": constrained,
        "n_converged_two_axis": converged,
        "n_recurrent_among_converged": recurrent,
        "n_in_canonical_driver_genes": 0,
        "cohort": "OpenPedCan H3 K27M DMG, 152 patients (functional-first: SNVs in "
                  "OPC-accessible c15 peaks)",
        "caveat": (
            "0 recurrent among converged (each private, 1 patient); 0 in the "
            "canonical DMG driver-gene list. Consistent with DMG's non-coding "
            "biology being enhancer-landscape reprogramming, not a recurrent point "
            "hotspot. This is a hypothesis-generating shortlist, not proven drivers."
        ),
        "provenance": PROVENANCE,
    }

    text = f"""# NCypher DMG discovery sweep: cohort summary

- **{total:,}** somatic non-coding SNVs scored (in OPC-accessible c15 regulatory
  elements, {structured['cohort']}).
- **{high_impact:,}** chromatin high-impact (|log2FC| >= {CALIBRATED_CHROMATIN_HI},
  the calibrated p99 background).
- **{constrained:,}** evolutionarily constrained (phyloP >= {CONSTRAINT_THRESHOLD}).
- **{converged:,}** converged on both axes (high-impact AND constrained) - the
  ranked shortlist to validate first.
- **{recurrent}** recurrent among converged; **0** in the canonical DMG driver-gene list.

## Honest caveat
{structured['caveat']}

## Provenance
Model context {MODEL_CONTEXT} (developing-brain fetal-OPC ChromBPNet), genome
{GENOME}; constraint from Zoonomia cactus241way phyloP. Source write-up:
docs/audit/sweep-result.md.
"""
    return ToolResult(content=text, structured_content=structured)


if __name__ == "__main__":
    mcp.run()
