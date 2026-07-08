"""The saliency logo: the demo centre of gravity.

A ref-vs-alt sequence logo where a crisp TF motif visibly collapses at the exact
variant base. Input is a per-base contribution vector (DeepSHAP counts
contributions from the ChromBPNet variant-scorer, or integrated gradients) plus
the sequence; output is a logomaker figure.

This module is deliberately model-agnostic: it renders whatever contribution
scores it is handed, so it can be developed and tested locally while the heavy
attribution runs on Modal. Rendering choices follow Faith's preferences: light
background, legible, colour-blind-safe base colours.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

# Colour-blind-safe base palette (Wong-derived), on a light ground.
BASE_COLORS = {
    "A": "#2ca02c",  # green
    "C": "#1f77b4",  # blue
    "G": "#ff7f0e",  # orange
    "T": "#d62728",  # red
}
_ORDER = "ACGT"


def contrib_matrix(seq: str, contrib: np.ndarray):
    """Build the logomaker input frame: an (L x 4) table where, at each
    position, only the base actually present carries height = its contribution
    score. Requires ``len(seq) == len(contrib)``."""
    import pandas as pd

    seq = seq.upper()
    if len(seq) != len(contrib):
        raise ValueError(f"seq ({len(seq)}) and contrib ({len(contrib)}) length mismatch")
    mat = np.zeros((len(seq), 4), dtype=float)
    idx = {b: i for i, b in enumerate(_ORDER)}
    for i, b in enumerate(seq):
        j = idx.get(b)
        if j is not None:
            mat[i, j] = contrib[i]
    return pd.DataFrame(mat, columns=list(_ORDER))


@dataclass
class LogoPanel:
    seq: str
    contrib: np.ndarray
    title: str


def _draw_logo(ax, seq: str, contrib: np.ndarray, center_idx: int, flank: int,
               title: str, highlight: bool):
    import logomaker

    lo = max(0, center_idx - flank)
    hi = min(len(seq), center_idx + flank + 1)
    sub_seq = seq[lo:hi]
    sub_contrib = np.asarray(contrib[lo:hi], dtype=float)
    df = contrib_matrix(sub_seq, sub_contrib)
    # x axis is relative to the variant base (variant sits at 0), which reads
    # far better than absolute 2114 bp window indices.
    df.index = range(lo - center_idx, hi - center_idx)

    logo = logomaker.Logo(df, ax=ax, color_scheme=BASE_COLORS, shade_below=0.0,
                          fade_below=0.0, flip_below=True)
    logo.style_spines(visible=False)
    logo.style_spines(spines=["left", "bottom"], visible=True)
    ax.set_ylabel("contribution", fontsize=9)
    ax.set_title(title, fontsize=11, loc="left")
    ax.tick_params(labelsize=7)
    ax.set_xlim(-flank - 0.5, flank + 0.5)
    if highlight:
        ax.axvspan(-0.5, 0.5, color="#ffd400", alpha=0.3, zorder=-5)  # box the variant base
    return logo


def ref_alt_logo(
    ref_seq: str,
    ref_contrib: np.ndarray,
    alt_seq: str,
    alt_contrib: np.ndarray,
    center_idx: int,
    flank: int = 12,
    suptitle: Optional[str] = None,
    ref_label: str = "reference",
    alt_label: str = "alternate",
):
    """Stacked ref (top) / alt (bottom) contribution logos over the same window,
    with the variant base highlighted. Returns a matplotlib Figure.

    ``center_idx`` is the index of the variant base within the full sequences
    (both sequences are the same length and aligned)."""
    import matplotlib.pyplot as plt

    fig, (ax_ref, ax_alt) = plt.subplots(
        2, 1, figsize=(max(6, flank * 0.9), 4.2), sharex=True, constrained_layout=True
    )
    _draw_logo(ax_ref, ref_seq, ref_contrib, center_idx, flank, ref_label, highlight=True)
    _draw_logo(ax_alt, alt_seq, alt_contrib, center_idx, flank, alt_label, highlight=True)
    ax_alt.set_xlabel("position (bp)", fontsize=9)
    if suptitle:
        fig.suptitle(suptitle, fontsize=12, fontweight="bold")
    return fig


def save_logo(fig, path, dpi: int = 160):
    from pathlib import Path

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path
