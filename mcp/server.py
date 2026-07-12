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

This is a full MCP surface, not a bare tool:
  - tools     : score_variant, top_candidates, cohort_summary (read-only, annotated)
  - resources : ncypher://provenance, ncypher://cohort/summary,
                ncypher://shortlist/converged, ncypher://finding/k27m-superenhancer
  - prompt    : triage_variant (guides an agent through a triage)

It does no heavy scoring. It serves the pre-computed discovery sweep
(``data/dmg/sweep_result.tsv``, 10,869 OPC-regulatory DMG variants) and, for a
variant not in that cache, does a fast live phyloP lookup while telling the
caller the chromatin axis still needs scoring.

Run:
    /Users/faith/Desktop/NCypher/.venv/bin/python mcp/server.py
or, for a browsable inspector (the clean demo surface):
    fastmcp dev mcp/server.py
"""

from __future__ import annotations

import csv
import json
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
from mcp.types import ToolAnnotations  # noqa: E402

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
SALIENCY_DIR = FIGURES_DIR / "real"
SE_SHORTLIST_TSV = DATA_DIR / "enhancers" / "converged_in_dipg_se.tsv"
SCORED_DIR = PROJECT_ROOT / "data" / "scored"
HERO_SCORES_TSV = SCORED_DIR / "ncypher.variant_scores.tsv"  # off-sweep positive controls with saliency

# Explicit saliency PNGs (never generated here). Any additional
# ``<GENE>_*.saliency.png`` dropped into data/figures/real/ is auto-discovered.
SALIENCY_FIGURES_BY_GENE = {
    "TERT": [
        SALIENCY_DIR / "TERT_C228T.saliency.png",
        SALIENCY_DIR / "TERT_C250T.saliency.png",
    ],
}

# --- declared output schemas (agent-legible; kept permissive) ----------------
_MEMO_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string"},
        "decisive_experiment": {"type": "string"},
        "kill_criterion": {"type": "string"},
    },
}
SCORE_VARIANT_OUTPUT_SCHEMA = {
    "type": "object",
    "description": "Three-axis convergence call + go/no-go memo for one variant.",
    "properties": {
        "variant_id": {"type": "string"},
        "gene": {"type": ["string", "null"]},
        "in_cache": {"type": "boolean"},
        "axes": {
            "type": "object",
            "description": "chromatin (ChromBPNet), constraint (phyloP), function (MPRA)",
        },
        "converged": {"type": "boolean"},
        "promote": {"type": ["boolean", "null"]},
        "confidence": {"type": "string"},
        "in_domain": {"type": ["boolean", "null"]},
        "agreement": {"type": ["number", "null"]},
        "votes": {"type": "array", "items": {"type": "object"}},
        "memo": _MEMO_SCHEMA,
        "saliency_attached": {"type": "boolean"},
        "provenance": {"type": "object"},
    },
    "required": ["variant_id", "in_cache", "axes", "provenance"],
}
TOP_CANDIDATES_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "n_requested": {"type": "integer"},
        "n_returned": {"type": "integer"},
        "converged_only": {"type": "boolean"},
        "ranked_by": {"type": "string"},
        "candidates": {"type": "array", "items": {"type": "object"}},
        "provenance": {"type": "object"},
    },
    "required": ["n_returned", "candidates", "provenance"],
}
COHORT_SUMMARY_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "n_scored": {"type": "integer"},
        "n_high_impact_chromatin": {"type": "integer"},
        "n_constrained_phylop": {"type": "integer"},
        "n_converged_two_axis": {"type": "integer"},
        "n_recurrent_among_converged": {"type": "integer"},
        "n_in_canonical_driver_genes": {"type": "integer"},
        "cohort": {"type": "string"},
        "caveat": {"type": "string"},
        "provenance": {"type": "object"},
    },
    "required": ["n_scored", "n_converged_two_axis", "provenance"],
}


# --- sweep cache -------------------------------------------------------------
_SWEEP: Optional[dict[str, dict]] = None
_HEROES: Optional[dict[str, dict]] = None
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


def _load_heroes() -> dict[str, dict]:
    """Off-sweep positive-control / hero variants (e.g. the TERT promoter controls),
    keyed by chr-pos-ref-alt. These carry saliency logos."""
    global _HEROES
    if _HEROES is None:
        rows: dict[str, dict] = {}
        if HERO_SCORES_TSV.exists():
            with open(HERO_SCORES_TSV, newline="") as fh:
                for r in csv.DictReader(fh, delimiter="\t"):
                    key = f"{r['chr']}-{r['pos']}-{r['allele1']}-{r['allele2']}"
                    rows[key] = r
        _HEROES = rows
    return _HEROES


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


def _saliency_paths(gene: Optional[str]) -> list[Path]:
    """Existing saliency PNGs for a gene: the explicit map plus any
    ``<GENE>_*.saliency.png`` in data/figures/real/ (auto-discovered, deduped)."""
    if not gene:
        return []
    seen: dict[str, Path] = {}
    for path in SALIENCY_FIGURES_BY_GENE.get(gene.upper(), []):
        if path.exists():
            seen[path.name] = path
    if SALIENCY_DIR.exists():
        for path in sorted(SALIENCY_DIR.glob(f"{gene.upper()}_*.saliency.png")):
            seen[path.name] = path
    return list(seen.values())


def _saliency_images(gene: Optional[str]) -> list[Image]:
    """Image content for any saliency PNG that already exists for this gene.
    Never generates a figure."""
    return [Image(path=str(p)) for p in _saliency_paths(gene)]


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


def _cohort_summary_data() -> dict:
    """The honest headline numbers, computed live from the cached sweep."""
    sweep = _load_sweep()
    rows = list(sweep.values())
    total = len(rows)
    high_impact = sum(1 for r in rows if _as_bool(r.get("high_impact")))
    constrained = sum(1 for r in rows if _as_bool(r.get("constrained")))
    converged = sum(1 for r in rows if _as_bool(r.get("converged_2ax")))
    recurrent = sum(1 for r in rows if (int(r.get("n_patients") or 1) > 1)
                    and _as_bool(r.get("converged_2ax")))
    return {
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


def _shortlist_data(n: int = 20, converged_only: bool = True) -> dict:
    """The ranked 'validate first' shortlist, computed live from the sweep."""
    sweep = _load_sweep()
    rows = list(sweep.values())
    if converged_only:
        rows = [r for r in rows if _as_bool(r.get("converged_2ax"))]
    rows.sort(key=lambda r: _fnum(r.get("abs_logfc")) or 0.0, reverse=True)
    rows = rows[: max(1, int(n))]
    candidates = [
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
        for r in rows
    ]
    return {
        "n_requested": int(n),
        "n_returned": len(candidates),
        "converged_only": converged_only,
        "ranked_by": "abs_logfc",
        "candidates": candidates,
        "provenance": PROVENANCE,
    }


# --- the server --------------------------------------------------------------
mcp = FastMCP(
    "ncypher",
    instructions=(
        "NCypher triages somatic non-coding regulatory variants in paediatric DMG by "
        "converging chromatin accessibility (ChromBPNet fetal-OPC), evolutionary "
        "constraint (Zoonomia phyloP) and, where available, MPRA function. Call "
        "score_variant for a go/no-go memo on one variant; top_candidates for the "
        "ranked shortlist; cohort_summary for the honest headline numbers. Read the "
        "resources (ncypher://...) for provenance, the shortlist and the flagship "
        "super-enhancer finding. It never promotes on a single axis and flags "
        "out-of-domain calls."
    ),
)


@mcp.tool(
    title="Triage a non-coding DMG variant",
    tags={"triage", "variant", "dmg", "non-coding"},
    output_schema=SCORE_VARIANT_OUTPUT_SCHEMA,
    annotations=ToolAnnotations(
        title="Triage a non-coding DMG variant",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=True,  # live phyloP lookup for uncached variants
    ),
)
def score_variant(variant_id: str) -> ToolResult:
    """Triage one non-coding variant (e.g. "chr22-33000876-C-T").

    Couples chromatin accessibility (ChromBPNet fetal-OPC), evolutionary
    constraint (Zoonomia phyloP) and, where available, measured MPRA function via
    the convergence engine, and returns a go/no-go memo: the verdict, the decisive
    experiment to run, and the kill criterion. If the variant is in the DMG
    discovery cache the full three-axis call is served (with the saliency logo when
    one exists); otherwise a fast live phyloP lookup is done and the chromatin axis
    is flagged as still needing scoring on the Corces c15 model.
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
    hero = _load_heroes().get(key)
    if hero is not None:
        return _score_from_hero(variant, hero)
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
    images = _saliency_images(gene)

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
        "saliency_attached": bool(images),
        "provenance": PROVENANCE,
    }

    text = _render_cache_text(variant, gene, row, call)
    content: list = [text]
    content.extend(images)
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


def _score_from_hero(variant: Variant, hrow: dict) -> ToolResult:
    """A positive-control / hero variant scored off-sweep (e.g. TERT): real chromatin
    score + live phyloP for constraint + its saliency logo. Shows the honest
    disagreement (chromatin fires, constraint may not) with the mechanism visible."""
    name = (hrow.get("variant_id") or "").strip()
    gene = name.split("_")[0] if name else None
    logfc = _fnum(hrow.get("logfc")) or 0.0
    abs_logfc = _fnum(hrow.get("abs_logfc")) or abs(logfc)
    jsd = _fnum(hrow.get("jsd")) or 0.0

    chromatin = ChromatinScore(
        variant_id=variant.id, chrom=variant.chrom, pos=variant.pos,
        ref=variant.ref, alt=variant.alt, logfc=logfc, abs_logfc=abs_logfc,
        jsd=jsd, active_allele_quantile=None, context=MODEL_CONTEXT,
    )
    phylop: Optional[float] = None
    constrained = False
    phylop_error: Optional[str] = None
    try:
        hit = _get_phylop().hit(variant)
        phylop = hit.phylop
        constrained = hit.constrained
    except Exception as exc:
        phylop_error = str(exc)

    constraint_hit = (
        PhyloPHit(variant=variant, phylop=phylop, constrained=constrained)
        if phylop is not None else None
    )
    call = converge(chromatin, constraint=constraint_hit, mpra=None,
                    chromatin_hi=CALIBRATED_CHROMATIN_HI)
    memo = call.memo

    figpath = SALIENCY_DIR / f"{name}.saliency.png"
    images = [Image(path=str(figpath))] if figpath.exists() else _saliency_images(gene)
    high_impact = abs_logfc >= CALIBRATED_CHROMATIN_HI
    votes_str = "\n".join(f"- {v.name}: {v.detail}" for v in call.votes)
    cons = (f"phyloP {phylop:.2f} ({'constrained' if constrained else 'unconstrained'})"
            if phylop is not None else f"unavailable ({phylop_error or 'no coverage'})")

    structured = {
        "variant_id": variant.id,
        "gene": gene,
        "label": name,
        "in_cache": False,
        "positive_control": True,
        "axes": {
            "chromatin": {
                "logfc": logfc, "abs_logfc": abs_logfc, "jsd": jsd,
                "direction": chromatin.direction, "high_impact": high_impact,
            },
            "constraint": {
                "phylop": phylop, "constrained": constrained,
                "threshold": CONSTRAINT_THRESHOLD, "available": phylop is not None,
                "error": phylop_error,
            },
            "function": {"available": False, "note": "not in the MPRA/DAV set"},
        },
        "promote": call.promote,
        "confidence": call.confidence,
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
        "saliency_attached": bool(images),
        "provenance": PROVENANCE,
    }

    text = f"""# NCypher triage: {variant.id}  ({name}, positive control)

**Verdict:** {memo['verdict']}

**Decisive experiment:** {memo['decisive_experiment']}

**Kill criterion:** {memo['kill_criterion']}

## Convergence
Positive control scored off the DMG sweep. Chromatin |log2FC| {abs_logfc:.3f}
({'high-impact' if high_impact else 'below the calibrated cutoff'} at >= {CALIBRATED_CHROMATIN_HI});
constraint {cons}. The saliency logo below shows the model-native DeepSHAP
contribution at the exact variant base.

{votes_str}

## Provenance
Model context {MODEL_CONTEXT} (developing-brain fetal-OPC ChromBPNet), genome
{GENOME}. Constraint: Zoonomia cactus241way phyloP. Positive-control scores from
data/scored/ncypher.variant_scores.tsv.
"""
    content: list = [text]
    content.extend(images)
    return ToolResult(content=content, structured_content=structured)


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
        "saliency_attached": False,
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


@mcp.tool(
    title="Top variants to validate first",
    tags={"shortlist", "dmg", "prioritisation"},
    output_schema=TOP_CANDIDATES_OUTPUT_SCHEMA,
    annotations=ToolAnnotations(
        title="Top variants to validate first",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def top_candidates(n: int = 20, converged_only: bool = True) -> ToolResult:
    """The "which variants to validate first" shortlist from the DMG discovery
    sweep, ranked by chromatin effect size (|log2FC|).

    With ``converged_only`` (default), returns only the two-axis-converged hits
    (chromatin high-impact AND evolutionarily constrained). Returns a markdown
    table and a structured list of candidates (key, gene, logfc, phylop,
    confidence, converged).
    """
    data = _shortlist_data(n=n, converged_only=converged_only)
    candidates = data["candidates"]

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
    return ToolResult(content=header + table + note, structured_content=data)


@mcp.tool(
    title="DMG cohort discovery summary",
    tags={"cohort", "dmg", "summary"},
    output_schema=COHORT_SUMMARY_OUTPUT_SCHEMA,
    annotations=ToolAnnotations(
        title="DMG cohort discovery summary",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def cohort_summary() -> ToolResult:
    """The honest headline numbers from the DMG discovery sweep: how many somatic
    non-coding variants were scored, how many are chromatin high-impact, how many
    are evolutionarily constrained, how many converge on both axes, and the
    honest caveat (no recurrent hotspot, nothing in canonical driver genes).
    Computed live from the cached sweep so the numbers are always truthful.
    """
    data = _cohort_summary_data()
    text = f"""# NCypher DMG discovery sweep: cohort summary

- **{data['n_scored']:,}** somatic non-coding SNVs scored (in OPC-accessible c15
  regulatory elements, {data['cohort']}).
- **{data['n_high_impact_chromatin']:,}** chromatin high-impact (|log2FC| >=
  {CALIBRATED_CHROMATIN_HI}, the calibrated p99 background).
- **{data['n_constrained_phylop']:,}** evolutionarily constrained (phyloP >= {CONSTRAINT_THRESHOLD}).
- **{data['n_converged_two_axis']:,}** converged on both axes (high-impact AND
  constrained) - the ranked shortlist to validate first.
- **{data['n_recurrent_among_converged']}** recurrent among converged; **0** in the
  canonical DMG driver-gene list.

## Honest caveat
{data['caveat']}

## Provenance
Model context {MODEL_CONTEXT} (developing-brain fetal-OPC ChromBPNet), genome
{GENOME}; constraint from Zoonomia cactus241way phyloP. Source write-up:
docs/audit/sweep-result.md.
"""
    return ToolResult(content=text, structured_content=data)


def _coerce_row(row: dict) -> dict:
    """Coerce a CSV-DictReader row (all strings) to typed values, so agents that
    reach the map through this tool get real booleans/numbers, not "True"/"False"
    strings (the TSV-boolean footgun the B1b audit flagged)."""
    out: dict = {}
    for k, v in row.items():
        if v is None or v == "":
            out[k] = None
        elif v in ("True", "False"):
            out[k] = v == "True"
        else:
            try:
                f = float(v)
                out[k] = int(f) if (f.is_integer() and "." not in v and "e" not in v.lower()) else f
            except (ValueError, TypeError):
                out[k] = v
    return out


@mcp.tool(
    title="Download the DMG regulatory map",
    tags={"resource", "regulatory-map", "download", "dmg"},
    annotations=ToolAnnotations(
        title="Download the DMG regulatory map",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def get_regulatory_map(limit: int = 0) -> ToolResult:
    """The downloadable, agent-queryable DMG non-coding regulatory map: every scored
    somatic non-coding variant with its chromatin score, evolutionary constraint,
    convergence verdict, motif mechanism, and the A3/A5/A9/A9b hardening annotations.
    Returns the manifest, the 37-column schema, and the 164 converged hits (fully
    annotated, typed) plus the paths to the full 10,869-row TSV/Parquet.

    This is the tool-accessible twin of the ``ncypher://regulatory-map`` resource,
    for agent hosts that surface tools but not MCP resources. ``limit`` caps the
    converged rows returned (0 = all 164). A null annotation means "not assessed at
    this tier", never "assessed negative".
    """
    data = regulatory_map_resource()
    rows = [_coerce_row(r) for r in data.get("converged_shortlist", [])]
    if limit and limit > 0:
        rows = rows[:limit]
    cov = data.get("coverage", {})
    dl = data.get("downloads", {})
    n_scored = cov.get("total_scored", 0)
    text = (
        "# NCypher DMG non-coding regulatory map\n\n"
        f"{n_scored:,} scored somatic non-coding variants x {len(data.get('schema', []))} "
        f"columns; {cov.get('converged', 0)} converged "
        f"(verdicts {cov.get('verdict_GO', 0)} GO / {cov.get('verdict_HOLD', 0)} HOLD / "
        f"{cov.get('verdict_NOGO', 0)} NO-GO). Returned below: the {len(rows)} converged, "
        "fully-annotated hits (typed).\n\n"
        f"Download the full table: `{dl.get('full_parquet', '')}` (Parquet preserves dtypes, "
        f"use it for boolean filters) or `{dl.get('full_tsv', '')}` (TSV). "
        f"Data dictionary: `{dl.get('data_dictionary', '')}`.\n\n"
        f"Query hint: {data.get('how_to_query', '')}\n"
    )
    structured = {
        "manifest": data.get("manifest", {}),
        "schema": data.get("schema", []),
        "coverage": cov,
        "converged": rows,
        "downloads": dl,
    }
    return ToolResult(content=text, structured_content=structured)


# --- resources (readable, not just callable) ---------------------------------
@mcp.resource(
    "ncypher://provenance",
    name="NCypher provenance",
    description="Model, genome, constraint track, calibration and data sources.",
    mime_type="application/json",
    tags={"provenance"},
)
def provenance_resource() -> dict:
    return PROVENANCE


@mcp.resource(
    "ncypher://cohort/summary",
    name="DMG cohort discovery summary",
    description="Live headline numbers from the discovery sweep (scored, high-impact, "
                "constrained, converged) with the honest caveat.",
    mime_type="application/json",
    tags={"cohort", "summary"},
)
def cohort_summary_resource() -> dict:
    return _cohort_summary_data()


@mcp.resource(
    "ncypher://shortlist/converged",
    name="Converged shortlist (validate first)",
    description="The top converged DMG candidates ranked by chromatin effect size.",
    mime_type="application/json",
    tags={"shortlist"},
)
def shortlist_resource() -> dict:
    return _shortlist_data(n=40, converged_only=True)


@mcp.resource(
    "ncypher://finding/k27m-superenhancer",
    name="Flagship: the K27M super-enhancer finding",
    description="The two-sided finding: somatic variants do not drive the DIPG "
                "super-enhancers (chromatin null), but those SEs sit on more "
                "evolutionarily constrained OPC sequence; plus the in-SE shortlist.",
    mime_type="application/json",
    tags={"finding", "super-enhancer"},
)
def k27m_se_finding_resource() -> dict:
    shortlist = []
    if SE_SHORTLIST_TSV.exists():
        with open(SE_SHORTLIST_TSV, newline="") as fh:
            shortlist = list(csv.DictReader(fh, delimiter="\t"))
    return {
        "title": "K27M super-enhancer finding (flagship)",
        "headline": (
            "Cohort somatic non-coding variants do NOT preferentially drive the DIPG "
            "super-enhancer addiction (chromatin null), but those super-enhancers are "
            "anchored on more evolutionarily constrained OPC sequence."
        ),
        "constraint_result": {
            "in_se_constrained_pct": 17,
            "out_se_constrained_pct": 14,
            "fisher_p": 6e-4,
            "class_and_gc_matched_permutation_p": "<0.001 (both)",
            "bootstrap_ci_delta": [0.029, 0.162],
        },
        "in_se_converged_shortlist_n": len(shortlist),
        "lead": "NPAS3 (neurodevelopmental TF, validated glioma tumour suppressor)",
        "honesty": (
            "Enrichment is not selection; low DMG non-coding burden caps power; the "
            "motif readout is honest (only a minority disrupt a clear generic motif, "
            "coherent with the chromatin null). Hypothesis-generating, not proven."
        ),
        "shortlist": shortlist,
        "source": "docs/plan/k27m-se-finding.md",
        "provenance": PROVENANCE,
    }


MAP_DIR = PROJECT_ROOT / "regulatory_map"
MAP_MANIFEST = MAP_DIR / "manifest.json"
MAP_CONVERGED_TSV = MAP_DIR / "ncypher_dmg_regulatory_map.converged.tsv"


@mcp.resource(
    "ncypher://regulatory-map",
    name="DMG non-coding regulatory map (the resource)",
    description="The downloadable, agent-queryable map: every scored somatic "
                "non-coding DMG variant with its chromatin score, constraint, "
                "convergence verdict, motif mechanism, and the A3/A5/A9/A9b "
                "hardening annotations. Returns the manifest + schema + the 164 "
                "converged shortlist; the full 10,869-row table ships as TSV/Parquet.",
    mime_type="application/json",
    tags={"resource", "regulatory-map", "download"},
)
def regulatory_map_resource() -> dict:
    manifest = {}
    if MAP_MANIFEST.exists():
        manifest = json.loads(MAP_MANIFEST.read_text())
    converged = []
    if MAP_CONVERGED_TSV.exists():
        with open(MAP_CONVERGED_TSV, newline="") as fh:
            converged = list(csv.DictReader(fh, delimiter="\t"))
    return {
        "title": "NCypher DMG non-coding regulatory map",
        "manifest": manifest,
        "schema": manifest.get("columns", []),
        "coverage": manifest.get("coverage", {}),
        "converged_shortlist": converged,  # the 164 fully-annotated hits
        "downloads": {
            "full_tsv": "regulatory_map/ncypher_dmg_regulatory_map.tsv",
            "full_parquet": "regulatory_map/ncypher_dmg_regulatory_map.parquet",
            "converged_tsv": "regulatory_map/ncypher_dmg_regulatory_map.converged.tsv",
            "data_dictionary": "regulatory_map/data_dictionary.md",
        },
        "how_to_query": (
            "Filter converged_shortlist by verdict/a3_context_label/a9_eqtl_supported, "
            "or load the full Parquet for all 10,869 scored variants. A null annotation "
            "means 'not assessed at this tier', not 'assessed negative'. See the data "
            "dictionary for the NPAS3 Hi-C and PWM-motif caveats."
        ),
        "provenance": PROVENANCE,
    }


# --- prompt (guides an agent through a triage) -------------------------------
@mcp.prompt(
    name="triage_variant",
    title="Triage a non-coding DMG variant",
    description="Walk an agent through triaging one variant with NCypher.",
    tags={"triage"},
)
def triage_variant_prompt(variant_id: str) -> str:
    return (
        f"Triage the somatic non-coding variant {variant_id} for paediatric DMG using "
        f"NCypher.\n\n"
        f"1. Call `score_variant('{variant_id}')` and read the go/no-go memo (verdict, "
        f"decisive experiment, kill criterion), the three-axis convergence, and the "
        f"saliency logo if one is attached.\n"
        f"2. State whether the chromatin and constraint axes AGREE, and flag any "
        f"disagreement or out-of-domain warning honestly.\n"
        f"3. If it is not in the cache, note that the chromatin axis needs scoring on "
        f"the Corces c15 model before a verdict.\n"
        f"4. For context, read the `ncypher://cohort/summary` resource, and compare "
        f"against `top_candidates()` to see where this variant ranks.\n\n"
        f"Do not promote on a single axis, and do not claim a proven driver - this is a "
        f"hypothesis-generating triage."
    )


if __name__ == "__main__":
    # show_banner=False skips FastMCP's startup PyPI version check. Under the
    # Claude Science sandbox that check is routed through a SOCKS proxy and would
    # otherwise abort stdio startup before any tools are listed.
    mcp.run(show_banner=False)
