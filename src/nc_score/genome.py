"""Local hg38 access: pull the sequence window around a variant and one-hot
encode it.

Used for (a) building the ref/alt sequences that the saliency renderer draws
under the logo, and (b) any local sequence checks. The heavy ChromBPNet forward
pass runs on Modal via the variant-scorer; this module is the light local side.

ChromBPNet's standard input length is 2114 bp centred on the position of
interest. We keep that as the default so local windows line up with what the
model saw.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

from nc_score.variants import Variant

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FASTA = REPO_ROOT / "data" / "genome" / "hg38.analysisSet.fa"

CHROMBPNET_INPUT_LEN = 2114

# Fixed base order for one-hot encoding, shared with the model.
BASES = "ACGT"
_BASE_IDX = {b: i for i, b in enumerate(BASES)}


def one_hot(seq: str) -> np.ndarray:
    """One-hot encode a DNA string to shape ``(len(seq), 4)`` in ACGT order.
    Any non-ACGT base (N, lower-case ambiguity) maps to an all-zero column."""
    arr = np.zeros((len(seq), 4), dtype=np.float32)
    for i, b in enumerate(seq.upper()):
        j = _BASE_IDX.get(b)
        if j is not None:
            arr[i, j] = 1.0
    return arr


class Genome:
    """Thin wrapper over a pyfaidx FASTA with edge-safe window extraction."""

    def __init__(self, fasta: Path = DEFAULT_FASTA):
        self.fasta_path = Path(fasta)
        self._fa = None

    @property
    def fa(self):
        if self._fa is None:
            from pyfaidx import Fasta

            if not self.fasta_path.exists():
                raise FileNotFoundError(
                    f"reference not found at {self.fasta_path}; download the hg38 "
                    "analysis set (see docs/data/sources.md) and decompress it"
                )
            self._fa = Fasta(str(self.fasta_path), sequence_always_upper=True)
        return self._fa

    def get_seq(self, chrom: str, start0: int, end0: int) -> str:
        """Sequence over a 0-based half-open interval. Out-of-bounds flanks are
        padded with N so the returned string is always ``end0 - start0`` long."""
        contig = self.fa[chrom]
        n = len(contig)
        left_pad = max(0, -start0)
        right_pad = max(0, end0 - n)
        s = str(contig[max(0, start0):min(n, end0)])
        return "N" * left_pad + s + "N" * right_pad

    def ref_base(self, chrom: str, pos: int) -> str:
        """The reference base at a 1-based position."""
        return self.get_seq(chrom, pos - 1, pos)

    def variant_sequences(
        self, variant: Variant, input_len: int = CHROMBPNET_INPUT_LEN
    ) -> tuple[str, str]:
        """Return ``(ref_seq, alt_seq)`` of length ``input_len`` centred on the
        variant, with the alt allele substituted at the centre base. SNVs only.
        Raises if the reference does not match ``variant.ref`` (a coordinate or
        build error we would rather catch loudly)."""
        if not variant.is_snv:
            raise NotImplementedError("variant_sequences currently supports SNVs only")
        chrom, start0, end0 = variant.window(input_len)
        ref_seq = self.get_seq(chrom, start0, end0)
        centre = variant.pos0 - start0
        observed = ref_seq[centre]
        if observed != variant.ref:
            raise ValueError(
                f"reference mismatch for {variant.id}: genome has {observed!r} at "
                f"the centre base, variant.ref is {variant.ref!r} (check build/coords)"
            )
        alt_seq = ref_seq[:centre] + variant.alt + ref_seq[centre + 1:]
        return ref_seq, alt_seq

    def variant_onehot(
        self, variant: Variant, input_len: int = CHROMBPNET_INPUT_LEN
    ) -> tuple[np.ndarray, np.ndarray]:
        """One-hot ``(ref, alt)`` arrays of shape ``(input_len, 4)``."""
        ref_seq, alt_seq = self.variant_sequences(variant, input_len)
        return one_hot(ref_seq), one_hot(alt_seq)

    def close(self):
        if self._fa is not None:
            self._fa.close()
            self._fa = None
