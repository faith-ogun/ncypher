"""Loading variants into NCypher, and writing them out for the ChromBPNet
variant-scorer.

Three entry points:
  - :func:`load_hero_variants` — the curated demo set (``examples/hero_variants.tsv``).
  - :func:`load_maf` — an OpenPedCan / PCAWG MAF, filtered to non-coding SNVs.
  - :func:`write_scorer_tsv` — emit the ChromBPNet variant-scorer input schema.

The scorer input follows the ``chrombpnet`` schema of kundajelab/variant-scorer:
tab-separated ``chrom  pos  allele1  allele2  variant_id`` with no header,
1-based, allele1 = ref, allele2 = alt.
"""

from __future__ import annotations

import csv
import gzip
from pathlib import Path
from typing import Iterable, Optional

from nc_score.variants import Variant

REPO_ROOT = Path(__file__).resolve().parents[2]
HERO_TSV = REPO_ROOT / "examples" / "hero_variants.tsv"

# MAF Variant_Classification values we treat as non-coding regulatory calls.
# (Coding/splice classes are excluded; NCypher's remit is the non-coding genome.)
NONCODING_CLASSES = {
    "IGR",
    "Intron",
    "5'Flank",
    "3'Flank",
    "5'UTR",
    "3'UTR",
    "RNA",
    "lincRNA",
}


def _open_maybe_gzip(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", newline="")
    return open(path, "rt", newline="")


def load_hero_variants(path: Path = HERO_TSV, include_placeholders: bool = False) -> list[Variant]:
    """The curated hero set. Placeholder rows (ref/alt = N) are skipped unless
    ``include_placeholders`` is set, in which case they are returned with their
    annotations in ``meta`` so the UI can show the intended slot.
    """
    out: list[Variant] = []
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            is_placeholder = row["ref"] == "N" or row["alt"] == "N"
            if is_placeholder and not include_placeholders:
                continue
            meta = {
                k: row[k]
                for k in ("gene", "category", "context", "mechanism", "note")
                if row.get(k)
            }
            meta["placeholder"] = is_placeholder
            ref = row["ref"] if not is_placeholder else "A"
            alt = row["alt"] if not is_placeholder else "T"
            out.append(
                Variant(
                    chrom=row["chrom"],
                    pos=int(row["pos"]),
                    ref=ref,
                    alt=alt,
                    label=row["variant_id"],
                    meta=meta,
                )
            )
    return out


def load_maf(
    path: Path,
    noncoding_only: bool = True,
    snv_only: bool = True,
    limit: Optional[int] = None,
) -> list[Variant]:
    """Load variants from an OpenPedCan / PCAWG MAF.

    MAF column names vary a little between releases, so we resolve them by
    common aliases. Filters to non-coding regulatory classes and SNVs by
    default. ``limit`` caps the number returned (handy for smoke tests).
    """
    chrom_keys = ["Chromosome", "chr", "chrom"]
    pos_keys = ["Start_Position", "Start_position", "start", "pos"]
    ref_keys = ["Reference_Allele", "ref"]
    alt_keys = ["Tumor_Seq_Allele2", "Tumor_Seq_Allele", "alt"]
    cls_keys = ["Variant_Classification", "effect", "Consequence"]
    type_keys = ["Variant_Type", "type"]
    sample_keys = ["Tumor_Sample_Barcode", "sample", "Kids_First_Biospecimen_ID"]

    def pick(row: dict, keys: list[str]) -> Optional[str]:
        for k in keys:
            if k in row and row[k] not in (None, "", "."):
                return row[k]
        return None

    out: list[Variant] = []
    with _open_maybe_gzip(path) as fh:
        # MAF files often carry leading comment lines beginning with '#'.
        reader = csv.DictReader((ln for ln in fh if not ln.startswith("#")), delimiter="\t")
        for row in reader:
            ref = pick(row, ref_keys)
            alt = pick(row, alt_keys)
            chrom = pick(row, chrom_keys)
            pos = pick(row, pos_keys)
            if not (ref and alt and chrom and pos):
                continue
            if snv_only and not (len(ref) == 1 and len(alt) == 1 and ref in "ACGT" and alt in "ACGT"):
                continue
            if noncoding_only:
                cls = pick(row, cls_keys)
                if cls is not None and cls not in NONCODING_CLASSES:
                    continue
            try:
                v = Variant(
                    chrom=chrom,
                    pos=int(pos),
                    ref=ref,
                    alt=alt,
                    label=pick(row, sample_keys),
                    meta={"variant_classification": pick(row, cls_keys) or "",
                          "variant_type": pick(row, type_keys) or ""},
                )
            except ValueError:
                continue
            out.append(v)
            if limit and len(out) >= limit:
                break
    return out


def write_scorer_tsv(variants: Iterable[Variant], path: Path) -> Path:
    """Write the ChromBPNet variant-scorer ``chrombpnet`` schema TSV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        for v in variants:
            w.writerow([v.chrom, v.pos, v.ref, v.alt, v.label or v.id])
    return path
