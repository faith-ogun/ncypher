"""Axis 3: evolutionary constraint (Zoonomia phyloP).

Zoonomia phyloP (``cactus241way``) is a per-base, genome-wide measure of
purifying selection across 241 placental mammals, and it is Pollard's own
resource. Positive scores mean slower-than-neutral evolution (conservation);
negative means acceleration (e.g. HARs). A base is "constrained" at phyloP
>= 2.27 (5% FDR), which flags ~3.26% of the genome.

We use it two ways, from a single data source (docs/research/08):
  1. as a per-variant feature (the phyloP at the variant base), and
  2. as an independent validation axis: NCypher's high-impact non-coding calls
     should land in constrained bases; low-impact ones should not. The model
     never saw this label, so it is an orthogonal evolutionary check.

The 9 GB bigWig is queried remotely over HTTP range requests by default, so no
download is needed. Pass a local path if you have mirrored the file.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

import numpy as np

from nc_score.variants import Variant

# UCSC goldenPath. bigWig supports HTTP range requests, so pyBigWig streams the
# few bytes it needs per query rather than pulling the whole 9 GB file.
PHYLOP_URL = (
    "http://hgdownload.soe.ucsc.edu/goldenPath/hg38/cactus241way/"
    "cactus241way.phyloP.bw"
)

# Constrained-base threshold from Christmas/Sullivan et al., Science 2023
# (PMC10259825): phyloP >= 2.27 at 5% FDR.
CONSTRAINT_THRESHOLD = 2.27


@dataclass(frozen=True)
class PhyloPHit:
    """The constraint readout for one variant."""

    variant: Variant
    phylop: Optional[float]  # None if the base is not covered by the track
    constrained: bool

    @property
    def available(self) -> bool:
        return self.phylop is not None


class PhyloP:
    """A thin, cached accessor over the Zoonomia phyloP bigWig.

    Open once and reuse; the first query pays the remote-open overhead, later
    point lookups are cheap. Safe to keep alive for the life of the MCP server.
    """

    def __init__(self, source: str = PHYLOP_URL, threshold: float = CONSTRAINT_THRESHOLD):
        self.source = source
        self.threshold = threshold
        self._bw = None

    @property
    def bw(self):
        if self._bw is None:
            import pyBigWig  # imported lazily so the package loads without it

            bw = pyBigWig.open(self.source)
            if not bw.isBigWig():
                raise ValueError(f"{self.source} is not a bigWig")
            self._bw = bw
        return self._bw

    def score(self, chrom: str, pos: int) -> Optional[float]:
        """phyloP at a single 1-based position. None if not covered or NaN."""
        vals = self.bw.values(chrom, pos - 1, pos)  # bigWig is 0-based, half-open
        if not vals:
            return None
        v = vals[0]
        return None if v is None or np.isnan(v) else float(v)

    def score_window(self, chrom: str, start0: int, end0: int) -> np.ndarray:
        """phyloP across a 0-based half-open window; NaN where uncovered.

        Used to draw the constraint sparkline under a saliency logo so the
        broken base can be read against local conservation.
        """
        vals = self.bw.values(chrom, start0, end0)
        return np.array([np.nan if v is None else v for v in vals], dtype=float)

    def hit(self, variant: Variant) -> PhyloPHit:
        s = self.score(variant.chrom, variant.pos)
        return PhyloPHit(
            variant=variant,
            phylop=s,
            constrained=(s is not None and s >= self.threshold),
        )

    def hits(self, variants: Iterable[Variant]) -> list[PhyloPHit]:
        return [self.hit(v) for v in variants]

    def close(self):
        if self._bw is not None:
            self._bw.close()
            self._bw = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def constraint_enrichment(
    impact: Sequence[float],
    phylop: Sequence[float],
    n_bins: int = 5,
    threshold: float = CONSTRAINT_THRESHOLD,
) -> list[dict]:
    """The validation axis: bin variants by NCypher's predicted impact and
    report mean phyloP and the fraction of constrained bases per bin.

    A working model shows a monotonic rise in constraint from the low-impact to
    the high-impact bin, using a label it never trained on. Returns one dict per
    bin (ordered low to high impact); rows with a missing phyloP are dropped.
    """
    imp = np.asarray(impact, dtype=float)
    php = np.asarray(phylop, dtype=float)
    ok = ~(np.isnan(imp) | np.isnan(php))
    imp, php = imp[ok], php[ok]
    if imp.size == 0:
        return []

    # Rank-based binning is robust to the skew of impact scores; quantile edges
    # keep bins balanced even when most variants are near-neutral.
    order = np.argsort(imp)
    bins = np.array_split(order, min(n_bins, imp.size))
    rows = []
    for i, idx in enumerate(bins):
        if idx.size == 0:
            continue
        b_php = php[idx]
        rows.append(
            {
                "bin": i,
                "impact_low": float(imp[idx].min()),
                "impact_high": float(imp[idx].max()),
                "n": int(idx.size),
                "mean_phylop": float(np.mean(b_php)),
                "frac_constrained": float(np.mean(b_php >= threshold)),
            }
        )
    return rows
