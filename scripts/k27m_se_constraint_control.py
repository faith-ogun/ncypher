"""TIGHTEN the DIPG super-enhancer constraint result: is the phyloP elevation in
SE-resident OPC variants robust to the two confounds a reviewer will raise, gene
proximity (variant class) AND GC content? Plus a bootstrap CI on the effect size, and
an honest genic-vs-intergenic decomposition.

Controls:
 1. class x GC-decile matched permutation (1,000x): draw out-SE variants matching the
    in-SE joint (class, GC-bin) distribution; compare in-SE median phyloP to that null.
 2. bootstrap CI (1,000x) on the in-SE minus out-SE median-phyloP difference.
 3. genic (intron/UTR) vs intergenic (IGR) breakdown, reported honestly.

Inputs (all local): data/dmg/enhancers/dipg_superenhancers.hg38.bed, data/dmg/sweep_result.tsv,
data/genome/hg38.analysisSet.fa. Run: PYTHONPATH=src .venv/bin/python scripts/k27m_se_constraint_control.py
"""
from __future__ import annotations
from pathlib import Path
import numpy as np, pandas as pd
from pyfaidx import Fasta

ENH = Path("data/dmg/enhancers")
FASTA = "data/genome/hg38.analysisSet.fa"


def union_from_bed(bed):
    se = pd.read_csv(bed, sep="\t", header=None, names=["chrom", "start", "end", "line"])
    out = {}
    for c, g in se.groupby("chrom"):
        iv = sorted(zip(g.start, g.end)); merged = []
        for s, e in iv:
            if merged and s <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append((s, e))
        arr = np.array(merged); out[c] = (arr[:, 0], arr[:, 1])
    return out


def in_se(chrom, pos, union):
    if chrom not in union: return False
    s, e = union[chrom]; i = np.searchsorted(s, pos, side="right") - 1
    return i >= 0 and pos <= e[i]


def gc_frac(fa, chrom, pos, half=50):
    try:
        seq = fa[chrom][pos - 1 - half: pos - 1 + half].seq.upper()
    except Exception:
        return np.nan
    n = sum(seq.count(b) for b in "ACGT")
    return (seq.count("G") + seq.count("C")) / n if n else np.nan


def main():
    union = union_from_bed(ENH / "dipg_superenhancers.hg38.bed")
    sw = pd.read_csv("data/dmg/sweep_result.tsv", sep="\t")
    parts = sw["key"].str.split("-", n=3, expand=True)
    sw["chrom"] = parts[0]; sw["pos"] = parts[1].astype(int)
    sw["in_se"] = [in_se(c, p, union) for c, p in zip(sw.chrom, sw.pos)]

    fa = Fasta(FASTA, sequence_always_upper=True)
    sw["gc"] = [gc_frac(fa, c, p) for c, p in zip(sw.chrom, sw.pos)]
    sw = sw.dropna(subset=["gc", "phylop", "cls"]).copy()
    sw["gcbin"] = pd.qcut(sw.gc, 10, labels=False, duplicates="drop")

    ins, out = sw[sw.in_se], sw[~sw.in_se]
    in_med = float(ins.phylop.median())
    print(f"n in-SE={len(ins)}  out-SE={len(out)}  in-SE median phyloP={in_med:.3f}  out={out.phylop.median():.3f}")

    # 1. class x GC matched permutation
    key = ["cls", "gcbin"]
    in_counts = ins.groupby(key).size()
    rng = np.random.default_rng(0); null = []
    for _ in range(1000):
        draws = []
        for (cl, gb), k in in_counts.items():
            pool = out[(out.cls == cl) & (out.gcbin == gb)]
            if len(pool):
                draws.append(pool.sample(min(k, len(pool)), replace=False,
                                         random_state=int(rng.integers(1e9))))
        null.append(pd.concat(draws).phylop.median())
    null = np.array(null); p = float((null >= in_med).mean())
    print(f"\n[1] class x GC matched permutation: in-SE {in_med:.3f} vs null "
          f"{np.median(null):.3f} [{np.percentile(null,2.5):.3f}, {np.percentile(null,97.5):.3f}]"
          f"  p={p:.3g}  ({'SURVIVES' if p<0.05 else 'does NOT survive'} class+GC control)")

    # 2. bootstrap CI on the median difference
    rng2 = np.random.default_rng(1); diffs = []
    ip, op = ins.phylop.values, out.phylop.values
    for _ in range(1000):
        diffs.append(np.median(rng2.choice(ip, len(ip))) - np.median(rng2.choice(op, len(op))))
    diffs = np.array(diffs)
    print(f"[2] bootstrap median-phyloP difference (in-SE minus out-SE): "
          f"{np.median(diffs):+.3f}  95% CI [{np.percentile(diffs,2.5):+.3f}, {np.percentile(diffs,97.5):+.3f}]"
          f"  ({'excludes 0' if np.percentile(diffs,2.5)>0 else 'includes 0'})")

    # 3. genic vs intergenic
    print("[3] honest decomposition (constrained fraction, in-SE vs out-SE):")
    con = sw["constrained"].fillna(0).astype(bool)
    for label, mask in [("genic (intron+UTR)", sw.cls.isin(["Intron", "5'UTR", "3'UTR"])),
                        ("intergenic (IGR)", sw.cls == "IGR")]:
        gi, go = mask & sw.in_se, mask & ~sw.in_se
        ni, no = int(gi.sum()), int(go.sum())
        if ni and no:
            pi, po = con[gi].mean(), con[go].mean()
            print(f"    {label:20s}: in-SE {100*pi:.1f}% vs out {100*po:.1f}%  (n={ni}/{no})")

    with open(ENH / "constraint_control_result.txt", "w") as fh:
        fh.write(f"class+GC matched perm p={p:.3g}; bootstrap median diff "
                 f"{np.median(diffs):+.3f} [{np.percentile(diffs,2.5):+.3f},{np.percentile(diffs,97.5):+.3f}]\n")
    print(f"\nwrote {ENH/'constraint_control_result.txt'}")


if __name__ == "__main__":
    main()
