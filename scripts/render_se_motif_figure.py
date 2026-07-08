"""Render the honest motif-readout figure for the DIPG super-enhancer-resident variants,
from REAL DeepSHAP (data/dmg/enhancers/se31.shap.npz, 29 mappable of 31). Shows what the
fetal-OPC model reads at the 4 hits with the strongest local contribution collapse. Honest:
only 4/29 reach >=50% collapse, and they are generic regulatory motifs, not OPC-master TFs.

Run: PYTHONPATH=src .venv/bin/python scripts/render_se_motif_figure.py
"""
from __future__ import annotations
import sys; sys.path.insert(0, "src")
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from nc_score import viz

viz.BASE_COLORS = {"A": "#2E9E43", "C": "#2F6FE0", "G": "#C67F12", "T": "#DA4A42"}  # theme palette

z = np.load("data/dmg/enhancers/se31.shap.npz", allow_pickle=True)
ids = [str(x) for x in z["variant_ids"]]
rc, ac, rs, asq = z["ref_contrib"], z["alt_contrib"], z["ref_seq"], z["alt_seq"]
L = int(z["input_len"]); c = L // 2
B = np.array(list("ACGT"))
dec = lambda r: "".join(B[np.clip(r, 0, 3)])

meta = pd.read_csv("data/dmg/enhancers/converged_in_dipg_se.tsv", sep="\t")
mm = {r.gene: (float(r.phylop), float(r.logfc)) for r in meta.itertuples()}

feat = [("NPAS3", 79), ("LINC01117", 78), ("IER2", 62), ("COL1A1", 62)]
flank = 11
fig, axes = plt.subplots(2, 4, figsize=(19, 6.4), sharex=True)
for j, (g, col) in enumerate(feat):
    i = ids.index(g); ph, lf = mm[g]
    viz._draw_logo(axes[0, j], dec(rs[i]), rc[i], c, flank, "", highlight=True)
    viz._draw_logo(axes[1, j], dec(asq[i]), ac[i], c, flank, "", highlight=True)
    axes[0, j].set_title(f"{g}  |  phyloP {ph:.1f}  |  {col}% collapse",
                         fontsize=9.5, loc="center", fontweight="bold", pad=8)
    axes[0, j].text(0.02, 0.86, "reference", transform=axes[0, j].transAxes, fontsize=8, color="#54606F")
    axes[1, j].text(0.02, 0.86, "alternate", transform=axes[1, j].transAxes, fontsize=8, color="#54606F")
    if j > 0:
        axes[0, j].set_ylabel(""); axes[1, j].set_ylabel("")
    axes[1, j].set_xlabel("position relative to variant (bp)", fontsize=8)

fig.suptitle("What the fetal-OPC model reads at DIPG super-enhancer-resident variants",
             fontsize=14, fontweight="bold")
cap = ("Real DeepSHAP over all 31 super-enhancer-resident converged variants (29 mappable). "
       "Honest coverage: only 4/29 show >=50% local contribution collapse (shown), 6/29 >=30%; "
       "these are generic regulatory motifs (GC-box, AP-1-like), NOT OPC-master TFs. Motif "
       "disruption is weak in super-enhancers, which is coherent with the null chromatin axis "
       "there: the super-enhancer signal is evolutionary CONSTRAINT, not somatic disruption. The "
       "clean OPC-lineage grammar (NFIA / SOX10 / OLIG2) the model learned is genome-wide. NPAS3 "
       "is a validated glioma tumour suppressor.")
fig.text(0.5, -0.02, cap, ha="center", va="top", fontsize=8.5, wrap=True, color="#0E1420")
fig.savefig("data/figures/se_motif_readout.png", dpi=170, bbox_inches="tight", facecolor="white")
print("wrote data/figures/se_motif_readout.png  (4 SE-resident readouts, real DeepSHAP)")
