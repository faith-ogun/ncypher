"""FLAGSHIP EXTENSION: do the cohort's OPC-regulatory somatic non-coding variants that
land inside the DIPG super-enhancer addiction (the BET/CDK7 target, Nagaraja 2017 Table
S4) preferentially carry the functional / constrained signal?

Design (honest, accessibility-matched): the universe is the 10,869 variants already in
Corces c15 OPC peaks. We split them by membership in the DIPG super-enhancer set and
compare IN-SE vs OUT-SE on convergence, chromatin impact and constraint. Both arms are
OPC-accessible, so accessibility is controlled; the contrast is SE membership only.

Caveats stated up front: SE regions are gene-dense and may have a different local somatic
mutation RATE, but rate cancels in a WITHIN-observed-variant proportion (%converged among
in-SE vs out-SE) and phyloP is a genomic property independent of the mutations. Enrichment
is not selection. Low DMG non-coding burden caps power. This is hypothesis generation.

Inputs: Table S4 xlsx (local), hg19->hg38 chain (local), data/dmg/sweep_result.tsv.
Run: PYTHONPATH=src .venv/bin/python scripts/k27m_se_analysis.py
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from pyliftover import LiftOver
from scipy.stats import fisher_exact, mannwhitneyu

ENH = Path("data/dmg/enhancers")
S4 = ("articles/Transcriptional Dependencies in Diffuse Intrinsic Pontine Glioma/"
      "NIHMS863827-supplement-2.xlsx")
CHAIN = ENH / "hg19ToHg38.over.chain.gz"
SWEEP = Path("data/dmg/sweep_result.tsv")


def build_se_hg38() -> pd.DataFrame:
    lo = LiftOver(str(CHAIN))
    xl = pd.ExcelFile(S4)
    rows, dropped = [], 0
    for sh in xl.sheet_names:  # one sheet per DIPG line
        df = xl.parse(sh, header=1)
        df = df[df["isSuper"] == 1]
        for _, r in df.iterrows():
            c = str(r["Chr"]); s = int(r["Start"]); e = int(r["End"])
            ls = lo.convert_coordinate(c, s); le = lo.convert_coordinate(c, e)
            if ls and le and ls[0][0] == c and le[0][0] == c:
                a, b = sorted((ls[0][1], le[0][1]))
                if b - a > 0:
                    rows.append((c, a, b, sh))
                else:
                    dropped += 1
            else:
                dropped += 1
    se = pd.DataFrame(rows, columns=["chrom", "start", "end", "line"])
    print(f"super-enhancers lifted hg19->hg38: {len(se)} (dropped {dropped} unmappable), "
          f"{se.line.nunique()} lines, {se.chrom.nunique()} chroms")
    return se


def merged_union(se: pd.DataFrame) -> dict:
    """Per-chrom merged non-overlapping intervals (union across all lines)."""
    out = {}
    for c, g in se.groupby("chrom"):
        iv = sorted(zip(g.start, g.end))
        merged = []
        for s, e in iv:
            if merged and s <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append((s, e))
        arr = np.array(merged)
        out[c] = (arr[:, 0], arr[:, 1])
    return out


def in_se(chrom: str, pos: int, union: dict) -> bool:
    if chrom not in union:
        return False
    starts, ends = union[chrom]
    i = np.searchsorted(starts, pos, side="right") - 1
    return i >= 0 and pos <= ends[i]


def main():
    se = build_se_hg38()
    union = merged_union(se)
    total_bp = sum(int((e - s).sum()) for s, e in union.values())
    print(f"union SE footprint: {total_bp/1e6:.1f} Mb over {sum(len(s) for s,_ in union.values())} merged intervals")
    ENH.mkdir(exist_ok=True)
    se.sort_values(["chrom", "start"]).to_csv(ENH / "dipg_superenhancers.hg38.bed",
        sep="\t", header=False, index=False)

    sw = pd.read_csv(SWEEP, sep="\t")
    parts = sw["key"].str.split("-", n=3, expand=True)
    sw["chrom"] = parts[0]; sw["pos"] = parts[1].astype(int)
    sw["in_se"] = [in_se(c, p, union) for c, p in zip(sw.chrom, sw.pos)]

    n_in, n_out = int(sw.in_se.sum()), int((~sw.in_se).sum())
    print(f"\nOPC-regulatory variants: {len(sw)} total, {n_in} in DIPG SEs, {n_out} outside")

    def flag(col):
        return sw[col].fillna(0).astype(bool) if col in sw else pd.Series(False, index=sw.index)

    print("\n--- IN-SE vs OUT-SE (both are OPC-accessible; SE membership is the only contrast) ---")
    for col, name in [("converged_2ax", "converged (2-axis)"),
                      ("high_impact", "chromatin high-impact"),
                      ("constrained", "phyloP-constrained")]:
        f = flag(col)
        a = int(f[sw.in_se].sum()); b = n_in - a
        c = int(f[~sw.in_se].sum()); d = n_out - c
        pin = a / n_in if n_in else 0; pout = c / n_out if n_out else 0
        _, p = fisher_exact([[a, b], [c, d]], alternative="greater")
        print(f"  {name:22s}: in-SE {a}/{n_in} ({100*pin:.1f}%)  vs  out {c}/{n_out} "
              f"({100*pout:.1f}%)  fold {pin/pout if pout else float('nan'):.2f}  Fisher p={p:.3g}")

    # constraint + chromatin magnitude (phyloP is a genomic property; mutation rate irrelevant)
    for col, name in [("phylop", "phyloP"), ("abs_logfc", "|log2FC| chromatin")]:
        if col in sw:
            xi = sw.loc[sw.in_se, col].dropna(); xo = sw.loc[~sw.in_se, col].dropna()
            _, p = mannwhitneyu(xi, xo, alternative="greater")
            print(f"  {name:22s}: in-SE median {xi.median():.3f}  vs out {xo.median():.3f}  MWU p={p:.3g}")

    # the honest shortlist: converged variants that fall in the K27M SE addiction
    conv_in = sw[sw.in_se & flag("converged_2ax")].sort_values("phylop", ascending=False)
    print(f"\nConverged variants inside DIPG super-enhancers: {len(conv_in)}")
    cols = [c for c in ["key", "gene", "logfc", "phylop", "confidence"] if c in sw]
    if len(conv_in):
        print(conv_in[cols].head(20).to_string(index=False))
    conv_in[cols + ["chrom", "pos"]].to_csv(ENH / "converged_in_dipg_se.tsv", sep="\t", index=False)

    # --- CONFOUND CONTROL: is the constraint signal just gene-dense neighbourhood? ---
    if "cls" in sw.columns and "constrained" in sw.columns:
        print("\n--- CONFOUND CONTROL: constraint within variant class ---")
        ct = pd.crosstab(sw["cls"], sw["in_se"], normalize="columns").round(3)
        print("variant-class fraction (False=out-SE, True=in-SE):\n" + ct.to_string())
        con = sw["constrained"].fillna(0).astype(bool)
        print("constrained fraction, in-SE vs out-SE, WITHIN each class:")
        for cl in sw["cls"].dropna().unique():
            gi = (sw["cls"] == cl) & sw.in_se
            go = (sw["cls"] == cl) & ~sw.in_se
            ni, no = int(gi.sum()), int(go.sum())
            if ni >= 20 and no >= 20:
                a, c = int(con[gi].sum()), int(con[go].sum())
                _, p = fisher_exact([[a, ni - a], [c, no - c]], alternative="greater")
                print(f"  {str(cl):10s}: in-SE {100*a/ni:4.1f}% vs out {100*c/no:4.1f}%  "
                      f"(n={ni}/{no})  Fisher p={p:.3g}")
        # class-matched permutation: draw out-SE variants matching the in-SE class mix
        rng = np.random.default_rng(0)
        in_cls = sw.loc[sw.in_se, "cls"].value_counts()
        out = sw[~sw.in_se]
        in_med = float(sw.loc[sw.in_se, "phylop"].median())
        null = []
        for _ in range(1000):
            draws = []
            for cl, k in in_cls.items():
                pool = out[out["cls"] == cl]
                if len(pool):
                    draws.append(pool.sample(min(k, len(pool)), replace=False,
                                             random_state=int(rng.integers(1e9))))
            null.append(pd.concat(draws)["phylop"].median())
        null = np.array(null)
        pval = float((null >= in_med).mean())
        print(f"\nclass-matched phyloP median: in-SE {in_med:.3f}  vs class-matched null "
              f"{np.median(null):.3f} [{np.percentile(null,2.5):.3f}, {np.percentile(null,97.5):.3f}]"
              f"  p={pval:.3g}  ({'survives' if pval < 0.05 else 'does NOT survive'} class control)")

    print(f"\nwrote {ENH/'dipg_superenhancers.hg38.bed'} and {ENH/'converged_in_dipg_se.tsv'}")


if __name__ == "__main__":
    main()
