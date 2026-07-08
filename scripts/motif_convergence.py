"""Motif-convergence test (H1): do the converged non-coding hits disrupt the SAME
transcription-factor motif classes - specifically OPC master-TFs?

Position-level recurrence can't answer this (the hits are private). The right test:
for each variant, ask which TF motif its allele change most disrupts (PWM match delta,
ref vs alt), classify it, and test whether the CONVERGED hits are enriched for OPC-
lineage TF motifs (OLIG2 / SOX10 / SOX2 / ASCL1 / NEUROD / NFIA / POU3F2) versus a
matched background of non-converged OPC-peak variants.

PWMs from JASPAR (cached locally). Uses the local hg38 (no Modal). Honest either way:
enrichment = a real finding; no enrichment = a real negative we report.

Run: PYTHONPATH=src python scripts/motif_convergence.py
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nc_score.genome import Genome  # noqa: E402

DMG = Path("data/dmg")
PWM_CACHE = DMG / "jaspar_pwms.json"

# OPC / neural master-TF panel + controls (JASPAR matrix IDs).
TF_PANEL = {
    "OLIG2": "MA0678.1", "SOX10": "MA0442.2", "SOX2": "MA0143.4",
    "ASCL1": "MA1100.2", "NEUROD1": "MA1109.1", "NFIA": "MA0670.1",
    "POU3F2": "MA0787.1",
    # controls (non-OPC)
    "CTCF": "MA0139.1", "GABPA_ETS": "MA0062.2", "SPI1_ETS": "MA0080.5",
}
OPC_TFS = {"OLIG2", "SOX10", "SOX2", "ASCL1", "NEUROD1", "NFIA", "POU3F2"}
FLANK = 20  # bp each side of the variant to scan


def fetch_pwms() -> dict:
    if PWM_CACHE.exists():
        return json.loads(PWM_CACHE.read_text())
    pwms = {}
    for tf, mid in TF_PANEL.items():
        url = f"https://jaspar.genereg.net/api/v1/matrix/{mid}/?format=json"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        pfm = r.json()["pfm"]  # {A:[...],C:[...],G:[...],T:[...]}
        pwms[tf] = {b: pfm[b] for b in "ACGT"}
        print(f"  fetched {tf} ({mid}) len={len(pfm['A'])}")
    PWM_CACHE.write_text(json.dumps(pwms))
    return pwms


def log_odds(pwm: dict) -> np.ndarray:
    """(L,4) log-odds matrix vs uniform background, with a pseudocount."""
    m = np.array([pwm[b] for b in "ACGT"], dtype=float).T  # (L,4)
    m = m + 0.25
    m = m / m.sum(axis=1, keepdims=True)
    return np.log2(m / 0.25)


_IDX = {b: i for i, b in enumerate("ACGT")}


def best_match(seq: str, lo: np.ndarray) -> float:
    """Max PWM log-odds score over both strands of seq."""
    L = lo.shape[0]
    arr = np.array([_IDX.get(b, -1) for b in seq])
    rc = np.array([_IDX.get({"A": "T", "C": "G", "G": "C", "T": "A"}.get(b, "N"), -1)
                   for b in reversed(seq)])
    best = -1e9
    for a in (arr, rc):
        for i in range(len(a) - L + 1):
            w = a[i:i + L]
            if (w < 0).any():
                continue
            best = max(best, lo[np.arange(L), w].sum())
    return best


def classify(variants: pd.DataFrame, genome: Genome, los: dict) -> pd.DataFrame:
    rows = []
    for r in variants.itertuples():
        chrom, pos, ref, alt = r.chrom, int(r.pos), r.ref, r.alt
        ref_seq = genome.get_seq(chrom, pos - 1 - FLANK, pos + FLANK)
        c = FLANK
        if ref_seq[c] != ref:  # coordinate/build sanity; skip if mismatch
            continue
        alt_seq = ref_seq[:c] + alt + ref_seq[c + 1:]
        deltas = {tf: best_match(alt_seq, lo) - best_match(ref_seq, lo) for tf, lo in los.items()}
        top_tf = max(deltas, key=lambda t: abs(deltas[t]))
        rows.append({"key": r.key, "gene": getattr(r, "gene", ""), "top_tf": top_tf,
                     "delta": deltas[top_tf], "abs_delta": abs(deltas[top_tf]),
                     "is_opc_tf": top_tf in OPC_TFS})
    return pd.DataFrame(rows)


def main():
    print("fetching JASPAR PWMs...")
    los = {tf: log_odds(p) for tf, p in fetch_pwms().items()}
    g = Genome()
    d = pd.read_csv(DMG / "sweep_result.tsv", sep="\t")
    for col in ["chrom", "pos", "ref", "alt"]:
        if col not in d.columns:
            parts = d["key"].str.split("-", expand=True)
            d["chrom"], d["pos"], d["ref"], d["alt"] = parts[0], parts[1].astype(int), parts[2], parts[3]
            break

    converged = d[d.converged_2ax].copy()
    # matched background: non-converged variants (still OPC-peak), same size x5
    bg = d[~d.converged_2ax].sample(n=min(len(converged) * 5, (~d.converged_2ax).sum()),
                                    random_state=7).copy()

    print(f"classifying converged (n={len(converged)}) and background (n={len(bg)})...")
    cc = classify(converged, g, los)
    bb = classify(bg, g, los)

    # require a real motif effect (|delta| >= 3 bits) to count as "affects a motif"
    THR = 3.0
    cc_hit = cc[cc.abs_delta >= THR]
    bb_hit = bb[bb.abs_delta >= THR]
    c_opc = cc_hit.is_opc_tf.mean() if len(cc_hit) else float("nan")
    b_opc = bb_hit.is_opc_tf.mean() if len(bb_hit) else float("nan")

    print("\n=== TF class of the most-disrupted motif (converged hits) ===")
    print(cc["top_tf"].value_counts().to_string())
    print(f"\nconverged: {len(cc_hit)}/{len(cc)} disrupt a motif (|delta|>={THR}); "
          f"OPC-TF fraction = {c_opc:.2f}")
    print(f"background: {len(bb_hit)}/{len(bb)} disrupt a motif; OPC-TF fraction = {b_opc:.2f}")
    if not np.isnan(c_opc) and not np.isnan(b_opc):
        from scipy.stats import fisher_exact
        table = [[cc_hit.is_opc_tf.sum(), (~cc_hit.is_opc_tf).sum()],
                 [bb_hit.is_opc_tf.sum(), (~bb_hit.is_opc_tf).sum()]]
        odds, p = fisher_exact(table)
        print(f"\nOPC-TF enrichment converged vs background: OR={odds:.2f}, Fisher p={p:.4g}")
        print("verdict:", "OPC-motif convergence" if (odds > 1 and p < 0.05)
              else "no significant OPC-motif convergence (honest negative)")

    cc.to_csv(DMG / "motif_convergence.converged.tsv", sep="\t", index=False)
    print("\nwrote data/dmg/motif_convergence.converged.tsv")


if __name__ == "__main__":
    main()
