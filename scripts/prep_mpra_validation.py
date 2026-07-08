"""Prepare the Pollard MPRA validation set: resolve ref/alt alleles for the active
variants (rsids -> Ensembl GRCh38), verify against hg38, write the scorer TSV.

The Science 2024 Data S2 gives rsid + chrom + pos + measured logFC + adj.P.Val +
motifbreakR annotation, but no ref/alt. We need alleles to score through ChromBPNet.
Ensembl allele lookups are cached incrementally (data/mpra/allele_cache.json) so the
run resumes if interrupted.

Run: PYTHONPATH=src python scripts/prep_mpra_validation.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from nc_score.genome import Genome  # noqa: E402
from nc_score.variants import Variant  # noqa: E402
from nc_score.data import write_scorer_tsv  # noqa: E402

MPRA = Path("data/mpra")
CACHE = MPRA / "allele_cache.json"
ENSEMBL = "https://rest.ensembl.org/variation/homo_sapiens"


def load_active() -> pd.DataFrame:
    df = pd.read_excel(MPRA / "DataS2-Variant-library-ratios.xlsx", sheet_name="Primary")
    active = df[(df["alt_is_active"] == 1) | (df["ref_is_active"] == 1)].copy()
    active["is_dav"] = (active["adj.P.Val"] < 0.10).astype(int)
    active["chrom"] = active["variant_chrom"].astype(str)
    active["pos"] = active["variant_pos"].astype(int)
    return active[["rsid", "chrom", "pos", "logFC", "adj.P.Val", "is_dav",
                   "qtl_motifbreakr_effect"]].reset_index(drop=True)


def fetch_alleles(rsids: list[str]) -> dict:
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    todo = [r for r in rsids if r not in cache and isinstance(r, str) and r.startswith("rs")]
    print(f"allele cache: {len(cache)} cached, {len(todo)} to fetch")
    for i in range(0, len(todo), 190):
        batch = todo[i:i + 190]
        try:
            r = requests.post(ENSEMBL, headers={"Content-Type": "application/json",
                                                "Accept": "application/json"},
                              data=json.dumps({"ids": batch}), timeout=60)
            if r.status_code == 200:
                data = r.json()
                for rs, info in data.items():
                    alleles = None
                    for m in info.get("mappings", []):
                        if m.get("assembly_name") == "GRCh38":
                            alleles = m.get("allele_string")
                            chrom = "chr" + str(m.get("seq_region_name"))
                            pos = int(m.get("start"))
                            break
                    if alleles and "/" in alleles:
                        parts = alleles.split("/")
                        cache[rs] = {"chrom": chrom, "pos": pos, "ref": parts[0], "alt": parts[1]}
                # mark unresolved so we don't retry forever
                for rs in batch:
                    cache.setdefault(rs, None)
                CACHE.write_text(json.dumps(cache))
                print(f"  fetched {i + len(batch)}/{len(todo)}")
            else:
                print(f"  batch {i} HTTP {r.status_code}; retrying later")
                time.sleep(2)
        except Exception as e:
            print(f"  batch {i} error {e}; continuing")
            CACHE.write_text(json.dumps(cache))
    return cache


def main():
    active = load_active()
    print(f"active variants: {len(active)} ({active['is_dav'].sum()} DAVs)")
    cache = fetch_alleles(active["rsid"].tolist())

    g = Genome()
    rows = []
    for r in active.itertuples():
        info = cache.get(r.rsid)
        if not info or info.get("ref") is None:
            continue
        ref, alt = info["ref"], info["alt"]
        if len(ref) != 1 or len(alt) != 1 or ref not in "ACGT" or alt not in "ACGT":
            continue  # SNVs only
        chrom, pos = info["chrom"], info["pos"]
        gref = g.ref_base(chrom, pos)
        # keep only where the genome matches ref (or the alt-swapped case)
        if gref == ref:
            R, A = ref, alt
        elif gref == alt:
            R, A = alt, ref  # table/dbSNP strand; use genome ref
        else:
            continue
        rows.append({"chrom": chrom, "pos": pos, "ref": R, "alt": A,
                     "rsid": r.rsid, "logFC": r.logFC, "is_dav": r.is_dav,
                     "motifbreakr": r.qtl_motifbreakr_effect})
    out = pd.DataFrame(rows)
    print(f"resolved SNVs with genome-matching ref: {len(out)} ({out['is_dav'].sum()} DAVs)")

    vs = [Variant(x.chrom, int(x.pos), x.ref, x.alt, label=f"{x.chrom}-{x.pos}-{x.ref}-{x.alt}")
          for x in out.itertuples()]
    write_scorer_tsv(vs, MPRA / "mpra_validation.scorer.tsv")
    out["key"] = out["chrom"] + "-" + out["pos"].astype(str) + "-" + out["ref"] + "-" + out["alt"]
    out.to_csv(MPRA / "mpra_validation.annot.tsv", sep="\t", index=False)
    print("wrote", MPRA / "mpra_validation.scorer.tsv", "and .annot.tsv")


if __name__ == "__main__":
    main()
