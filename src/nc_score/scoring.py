"""Axis 2 result model: the ChromBPNet chromatin-accessibility effect.

The heavy scoring runs on Modal (``modal/score_variants.py``) via the kundajelab
variant-scorer and writes a ``*.variant_scores.tsv``. This module parses that
TSV into structured :class:`ChromatinScore` records that the convergence engine
and the MCP tool consume, so nothing downstream has to know the TSV column
layout.

Effect metrics (allele2/alt vs allele1/ref), per the ChromBPNet preprint:
  - ``logfc``       log2 fold-change of predicted total accessibility (effect size)
  - ``jsd``         Jensen-Shannon distance between base-resolution profiles
                    (profile-shape change, i.e. footprint disruption)
  - ``active_allele_quantile`` percentile of the stronger allele vs all peaks
  - ``ies``/``ips`` integrative effect size / prioritisation score (products)
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# TSV column -> attribute. variant-scorer names vary slightly by version, so we
# resolve by a set of aliases.
_ALIASES = {
    "logfc": ["logfc", "log2fc"],
    "abs_logfc": ["abs_logfc"],
    "jsd": ["jsd"],
    "active_allele_quantile": ["active_allele_quantile", "max_percentile"],
    "ies": ["abs_logfc_x_jsd"],
    "ips": ["logfc_x_jsd_x_active_allele_quantile", "abs_logfc_x_jsd_x_active_allele_quantile"],
}


@dataclass
class ChromatinScore:
    variant_id: str
    chrom: str
    pos: int
    ref: str
    alt: str
    logfc: float
    abs_logfc: float
    jsd: float
    active_allele_quantile: Optional[float] = None
    ies: Optional[float] = None
    ips: Optional[float] = None
    context: Optional[str] = None  # e.g. trevino_2021.c15

    @property
    def direction(self) -> str:
        """Does the alt allele open or close chromatin?"""
        if self.logfc > 0:
            return "gain"
        if self.logfc < 0:
            return "loss"
        return "none"


def _pick(row: dict, names: list[str]) -> Optional[str]:
    for n in names:
        if n in row and row[n] not in (None, "", "NA", "nan"):
            return row[n]
    return None


def _fnum(row: dict, key: str) -> Optional[float]:
    raw = _pick(row, _ALIASES[key])
    if raw is None:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def load_scores(path: Path, context: Optional[str] = None) -> list[ChromatinScore]:
    """Parse a variant-scorer ``*.variant_scores.tsv`` into ChromatinScore rows."""
    out: list[ChromatinScore] = []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            chrom = _pick(row, ["chr", "chrom", "#chr"])
            pos = _pick(row, ["pos", "position"])
            logfc = _fnum(row, "logfc")
            if chrom is None or pos is None or logfc is None:
                continue
            abs_logfc = _fnum(row, "abs_logfc")
            out.append(
                ChromatinScore(
                    variant_id=_pick(row, ["variant_id", "rsid", "snp"]) or f"{chrom}-{pos}",
                    chrom=chrom if chrom.startswith("chr") else f"chr{chrom}",
                    pos=int(float(pos)),
                    ref=_pick(row, ["allele1", "ref"]) or "N",
                    alt=_pick(row, ["allele2", "alt"]) or "N",
                    logfc=logfc,
                    abs_logfc=abs_logfc if abs_logfc is not None else abs(logfc),
                    jsd=_fnum(row, "jsd") or 0.0,
                    active_allele_quantile=_fnum(row, "active_allele_quantile"),
                    ies=_fnum(row, "ies"),
                    ips=_fnum(row, "ips"),
                    context=context,
                )
            )
    return out
