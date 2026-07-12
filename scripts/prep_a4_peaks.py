#!/usr/bin/env python3
"""Stage the A4 tfmodisco input: the top-N c15 fetal-OPC accessible peaks as
fixed 2114 bp windows centred on each summit, for genome-wide contribution
scoring on Modal (the tfmodisco rediscovery step).

Reads data/dmg/c15_peaks.bed.gz (ENCODE narrowPeak, 10 columns:
chrom start end name score strand signalValue pValue qValue peakOffset), takes
the top N by signalValue, centres a 2114 bp window on the summit (start +
peakOffset), drops windows that run off a chromosome end (chrom sizes from the
local hg38 .fai), and writes data/dmg/enhancers/a4_c15_peaks_subset.bed.

2114 bp is the ChromBPNet input length. If the deposited model's config says
otherwise (1000 / other), pass --window to match before the Modal contribs run.
"""
import argparse
import gzip
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PEAKS = ROOT / "data/dmg/c15_peaks.bed.gz"
FAI = ROOT / "data/genome/hg38.analysisSet.fa.fai"
OUT = ROOT / "data/dmg/enhancers/a4_c15_peaks_subset.bed"


def chrom_sizes() -> dict:
    sizes = {}
    with FAI.open() as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                sizes[parts[0]] = int(parts[1])
    return sizes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=30000, help="top N peaks by signalValue")
    ap.add_argument("--window", type=int, default=2114, help="window length (ChromBPNet input)")
    args = ap.parse_args()
    half = args.window // 2

    sizes = chrom_sizes()

    rows = []
    with gzip.open(PEAKS, "rt") as fh:
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < 10:
                continue
            chrom = f[0]
            start = int(f[1])
            try:
                signal = float(f[6])
            except ValueError:
                signal = 0.0
            off = int(f[9])
            summit = start + off if off >= 0 else (start + int(f[2])) // 2
            rows.append((signal, chrom, summit, f[3] or f"peak{len(rows)}"))

    rows.sort(key=lambda r: r[0], reverse=True)

    kept = []
    dropped_edge = 0
    dropped_chrom = 0
    for signal, chrom, summit, name in rows:
        if chrom not in sizes:
            dropped_chrom += 1
            continue
        ws = summit - half
        we = summit + half
        if ws < 0 or we > sizes[chrom]:
            dropped_edge += 1
            continue
        kept.append((chrom, ws, we, name))
        if len(kept) >= args.top:
            break

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as fh:
        for chrom, ws, we, name in kept:
            fh.write(f"{chrom}\t{ws}\t{we}\t{name}\n")

    print(
        f"wrote {OUT} : {len(kept)} windows of {args.window} bp "
        f"(top {args.top} by signalValue; dropped {dropped_edge} edge, {dropped_chrom} off-contig)"
    )


if __name__ == "__main__":
    main()
