#!/usr/bin/env python3
"""Render the A8 pitfalls x status grid in NCypher branding (electric blue on white).

A rebrand of the Claude-Science-generated a8_pitfalls_status.png (kept as the
provenance original at results/a8/a8_pitfalls_status.claude-science-original.png).
Same content and status assignments; NCypher palette + white background.

Status colours (CVD-safe: blue vs amber vs grey, no red/green):
  controlled           -> electric blue #0600f9, solid, white text
  partly controlled    -> amber #eab308, solid, ink text
  planned / Modal-gated -> OUTLINED (white fill, amber border+text) = honestly "not done yet"
  n/a (we do not train) -> muted grey #7c8496, solid, white text
"""
import textwrap
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

INK = "#0e0f23"
ACCENT = "#0600f9"   # electric blue
AMBER = "#eab308"
GREY = "#7c8496"
MUTED = "#3d4152"

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Helvetica Neue", "Arial", "DejaVu Sans"],
    "figure.dpi": 200,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

# status codes: 0 n/a, 1 controlled, 2 partly, 3 planned/Modal-gated
rows = [
    ("1. Distributional shift\n(train vs deploy)",      [("matched OPC context + caQTL context-specificity", 1)]),
    ("2. Data-point dependency\n(proximity leakage)",   [("no split of ours (pretrained); caQTL not random-split", 0),
                                                          ("functional-first, 0 recurrent", 1),
                                                          ("mappability guard", 3)]),
    ("3. Confounding",                                  [("A2 dist-TSS + rep-timing; GC-decile; A7 rho=-0.004", 1)]),
    ("4. Leaky preprocessing\n/ calibration",           [("p99=0.162 background; GC control", 1)]),
    ("5. Class imbalance\n/ wrong metric",              [("AUPRC primary + honest MPRA negative", 1),
                                                          ("reverse-complement consistency", 3)]),
    ("6. Over-interpreting\nattributions",              [("saliency-as-mechanism + caveat", 2),
                                                          ("tfmodisco rediscovery figure (A4)", 3)]),
]

# (facecolor, edgecolor, textcolor)
STYLE = {
    0: (GREY, GREY, "white"),
    1: (ACCENT, ACCENT, "white"),
    2: (AMBER, AMBER, INK),
    3: ("white", AMBER, AMBER),   # outlined = planned / not done
}
NAME = {1: "controlled", 2: "partly controlled", 3: "planned / Modal-gated", 0: "n/a (we do not train)"}

fig, ax = plt.subplots(figsize=(9.4, 5.7))
n = len(rows)
ax.set_ylim(0, n)
ax.invert_yaxis()

for i, (pf, comps) in enumerate(rows):
    y = i + 0.5
    ax.text(-0.15, y, pf, ha="right", va="center", fontsize=8.5, color=INK, linespacing=1.15, fontweight="bold")
    x = 0.15
    for lbl, st in comps:
        w = 3.05
        fc, ec, tc = STYLE[st]
        ax.add_patch(FancyBboxPatch((x, y - 0.34), w, 0.68,
                     boxstyle="round,pad=0.02,rounding_size=0.08",
                     facecolor=fc, edgecolor=ec, linewidth=1.6))
        txt = "\n".join(textwrap.wrap(lbl, 30))
        ax.text(x + w / 2, y, txt, ha="center", va="center", fontsize=6.4,
                color=tc, linespacing=1.08, fontweight="medium")
        x += w + 0.12

ax.set_xlim(-3.2, 9.7)
ax.axis("off")
ax.set_title("NCypher against the six ML-in-genomics pitfalls\n(Whalen, Schreiber, Noble & Pollard, Nat Rev Genet 2022)",
             fontsize=10, loc="left", pad=14, color=INK, fontweight="bold")

handles = [Patch(facecolor=STYLE[k][0], edgecolor=STYLE[k][1], label=NAME[k]) for k in [1, 2, 3, 0]]
ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.35, -0.10),
          ncol=4, frameon=False, fontsize=7.4, handlelength=1.1, columnspacing=1.2)

fig.tight_layout()
fig.savefig("data/figures/a8_pitfalls_status.png", dpi=300, bbox_inches="tight", facecolor="white")
print("wrote data/figures/a8_pitfalls_status.png (NCypher-branded)")
