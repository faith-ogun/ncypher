"""Local side of the saliency wow.

The heavy DeepSHAP contribution scoring runs on Modal (``shap_tsv`` in
``modal/score_variants.py``) and returns a compact ``.npz``. This module loads
that file and renders the ref-vs-alt contribution logo via :mod:`nc_score.viz`,
zoomed to the window around the variant so the motif change is legible.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from nc_score.viz import ref_alt_logo, save_logo

_ACGT = np.array(list("ACGT"))


def _decode(seq_idx: np.ndarray) -> str:
    return "".join(_ACGT[seq_idx.astype(int)])


@dataclass
class SaliencyTrack:
    """Per-variant DeepSHAP contribution track for both alleles."""

    variant_id: str
    ref_seq: str
    alt_seq: str
    ref_contrib: np.ndarray
    alt_contrib: np.ndarray
    center: int  # index of the variant base within the full-length track

    def logo(self, flank: int = 12, suptitle: Optional[str] = None):
        return ref_alt_logo(
            self.ref_seq, self.ref_contrib, self.alt_seq, self.alt_contrib,
            center_idx=self.center, flank=flank,
            suptitle=suptitle or f"{self.variant_id} — ChromBPNet DeepSHAP",
            ref_label="reference allele", alt_label="alternate allele",
        )


class SaliencyBundle:
    """All saliency tracks returned by one ``shap_tsv`` call."""

    def __init__(self, npz_path: Path):
        d = np.load(npz_path, allow_pickle=True)
        self.variant_ids = [str(v) for v in d["variant_ids"]]
        self._ref_c = d["ref_contrib"]
        self._alt_c = d["alt_contrib"]
        self._ref_s = d["ref_seq"]
        self._alt_s = d["alt_seq"]
        self.input_len = int(d["input_len"][0])
        self.center = self.input_len // 2  # ChromBPNet centres input on the variant

    def __len__(self):
        return len(self.variant_ids)

    def track(self, variant_id: str) -> SaliencyTrack:
        i = self.variant_ids.index(variant_id)
        return SaliencyTrack(
            variant_id=variant_id,
            ref_seq=_decode(self._ref_s[i]),
            alt_seq=_decode(self._alt_s[i]),
            ref_contrib=self._ref_c[i].astype(float),
            alt_contrib=self._alt_c[i].astype(float),
            center=self.center,
        )

    def render_all(self, out_dir: Path, flank: int = 12) -> list[Path]:
        out_dir = Path(out_dir)
        paths = []
        for vid in self.variant_ids:
            fig = self.track(vid).logo(flank=flank)
            paths.append(save_logo(fig, out_dir / f"{vid}.saliency.png"))
        return paths
