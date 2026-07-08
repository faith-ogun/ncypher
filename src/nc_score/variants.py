"""The variant model shared across NCypher's axes.

A single, permissive representation of an SNV on hg38, plus parsing for the
compact string forms an agent is likely to pass to the MCP tool
(``chr7-5530601-A-G`` or ``chr7:5530601:A:G``).

Coordinates are 1-based throughout NCypher's public surface (the convention of
VCF, the UCSC browser, and the ChromBPNet variant-scorer TSV). We only drop to
0-based at the boundary of tools that demand it (pyBigWig, pyfaidx), and we do
that conversion explicitly at the call site so it is never ambiguous.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

_BASES = set("ACGT")

# chr7-5530601-A-G  /  chr7:5530601:A:G  /  7_5530601_A_G  (case-insensitive alleles)
_VARIANT_RE = re.compile(
    r"^(?P<chrom>chr[0-9XYM]+|[0-9XYM]+)"
    r"[-:_](?P<pos>\d+)"
    r"[-:_](?P<ref>[ACGTacgt]+)"
    r"[-:_](?P<alt>[ACGTacgt]+)$"
)


@dataclass(frozen=True)
class Variant:
    """An SNV (or short indel) on hg38, 1-based.

    ``chrom`` is normalised to UCSC style (``chr7``). ``ref``/``alt`` are
    upper-cased. ``label`` is a free-text tag (gene, cohort id, hero name) that
    rides along for reporting and never affects scoring.
    """

    chrom: str
    pos: int
    ref: str
    alt: str
    label: Optional[str] = None
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        chrom = self.chrom if self.chrom.startswith("chr") else f"chr{self.chrom}"
        object.__setattr__(self, "chrom", chrom)
        object.__setattr__(self, "ref", self.ref.upper())
        object.__setattr__(self, "alt", self.alt.upper())
        if self.pos < 1:
            raise ValueError(f"pos must be 1-based (>=1), got {self.pos}")
        if not set(self.ref) <= _BASES or not set(self.alt) <= _BASES:
            raise ValueError(f"ref/alt must be A/C/G/T, got {self.ref}>{self.alt}")

    @property
    def is_snv(self) -> bool:
        return len(self.ref) == 1 and len(self.alt) == 1

    @property
    def pos0(self) -> int:
        """0-based position of the variant (for pyBigWig / pyfaidx slicing)."""
        return self.pos - 1

    @property
    def id(self) -> str:
        return f"{self.chrom}-{self.pos}-{self.ref}-{self.alt}"

    def window(self, size: int) -> tuple[str, int, int]:
        """A 0-based, half-open ``(chrom, start, end)`` window of ``size`` bp
        centred on the variant. Used to pull the model input sequence and the
        constraint track around the base. ``size`` should be odd so the variant
        sits on the centre base.
        """
        half = size // 2
        start = self.pos0 - half
        return self.chrom, start, start + size

    def __str__(self) -> str:
        return self.id if self.label is None else f"{self.id} ({self.label})"

    @classmethod
    def parse(cls, s: str, label: Optional[str] = None) -> "Variant":
        """Parse ``chr7-5530601-A-G`` (also ``:``/``_`` separated)."""
        m = _VARIANT_RE.match(s.strip())
        if not m:
            raise ValueError(
                f"could not parse variant {s!r}; expected chrom-pos-ref-alt "
                "e.g. chr7-5530601-A-G"
            )
        return cls(
            chrom=m["chrom"],
            pos=int(m["pos"]),
            ref=m["ref"],
            alt=m["alt"],
            label=label,
        )
