"""The DMG discovery cohort: somatic non-coding SNVs from OpenPedCan.

Loads the compact non-coding SNV table extracted from the OpenPedCan consensus
MAF (158 H3 K27M DMG patients, GRCh38), and computes the signals the discovery
sweep needs:

  - **position recurrence**: the same chr:pos:ref:alt seen in >1 patient. Rare for
    non-coding SNVs, but this is how a hotspot (e.g. a TERT-promoter position)
    announces itself.
  - **element / gene recurrence**: many patients with (different) variants in the
    same gene's regulatory region - the softer convergence signal that motif-level
    analysis then sharpens.

The real H1 convergence (variants across patients hitting the same TF-motif class
in K27M-gained OPC enhancers) is computed downstream, once ChromBPNet + DeepSHAP
have told us which motif each variant touches.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from nc_score.variants import Variant

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COHORT = REPO_ROOT / "data" / "dmg" / "dmg_noncoding_snvs.tsv.gz"

# Regulatory-relevant non-coding classes, ordered by how promoter/enhancer-proximal
# they are (used to prioritise when the full set is too big to score).
REGULATORY_PRIORITY = ["5'Flank", "5'UTR", "3'UTR", "3'Flank", "RNA", "Intron", "IGR"]

# DMG-relevant loci whose regulatory variants are the most interpretable priors.
DMG_GENES = {
    "PDGFRA", "MYCN", "MYC", "EGFR", "TERT", "OLIG1", "OLIG2", "SOX10", "SOX2",
    "NKX2-2", "ASCL1", "CSPG4", "ACVR1", "TP53", "PPM1D", "CDKN2A", "ID2",
}


def load_cohort(path: Path = DEFAULT_COHORT) -> pd.DataFrame:
    """Load the compact non-coding SNV table."""
    df = pd.read_csv(path, sep="\t", dtype=str)
    df["pos"] = df["pos"].astype(int)
    # normalise chrom to UCSC style
    df["chrom"] = df["chrom"].apply(lambda c: c if str(c).startswith("chr") else f"chr{c}")
    df["variant_key"] = df["chrom"] + "-" + df["pos"].astype(str) + "-" + df["ref"] + "-" + df["alt"]
    return df


def recurrence_table(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse to unique variants with per-patient recurrence, most recurrent first."""
    g = df.groupby("variant_key")
    out = g.agg(
        chrom=("chrom", "first"),
        pos=("pos", "first"),
        ref=("ref", "first"),
        alt=("alt", "first"),
        classification=("classification", "first"),
        gene=("gene", "first"),
        n_patients=("patient", "nunique"),
        n_samples=("biospecimen", "nunique"),
    ).reset_index()
    return out.sort_values(["n_patients", "gene"], ascending=[False, True]).reset_index(drop=True)


def gene_recurrence(df: pd.DataFrame) -> pd.DataFrame:
    """Per-gene regulatory-variant burden across patients (softer convergence)."""
    g = df.groupby("gene").agg(
        n_variants=("variant_key", "nunique"),
        n_patients=("patient", "nunique"),
    ).reset_index()
    return g.sort_values(["n_patients", "n_variants"], ascending=False).reset_index(drop=True)


def to_variants(rec: pd.DataFrame, limit: Optional[int] = None) -> list[Variant]:
    """Build Variant objects (carrying recurrence + annotation in meta)."""
    out = []
    rows = rec.head(limit) if limit else rec
    for _, r in rows.iterrows():
        out.append(
            Variant(
                chrom=r["chrom"], pos=int(r["pos"]), ref=r["ref"], alt=r["alt"],
                label=r["variant_key"],
                meta={
                    "gene": r.get("gene", ""),
                    "classification": r.get("classification", ""),
                    "n_patients": int(r.get("n_patients", 1)),
                    "n_samples": int(r.get("n_samples", 1)),
                },
            )
        )
    return out


def select_discovery_subset(
    rec: pd.DataFrame, per_bucket: int = 25
) -> pd.DataFrame:
    """Pick an interpretable, tractable first-pass subset:
    (a) every recurrent variant (n_patients > 1),
    (b) variants in DMG-relevant gene regulatory regions,
    (c) a promoter-proximal (5'Flank/UTR) sample.
    Returns the deduplicated union.
    """
    recurrent = rec[rec["n_patients"] > 1]
    dmg = rec[rec["gene"].isin(DMG_GENES)]
    promoter = rec[rec["classification"].isin(["5'Flank", "5'UTR"])].head(per_bucket * 4)
    sub = pd.concat([recurrent, dmg, promoter]).drop_duplicates("variant_key")
    return sub.sort_values(["n_patients"], ascending=False).reset_index(drop=True)
