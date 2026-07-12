#!/usr/bin/env python3
"""Build the NCypher DMG non-coding regulatory map (deliverable B1).

Assembles every scored somatic non-coding variant in the OpenPedCan H3 K27M DMG
cohort into one documented, downloadable, agent-queryable table: the chromatin
score, the evolutionary-constraint axis, the two-axis convergence verdict, the
model-native mechanism (motif), and every Claude Science hardening annotation
(A3 context-specificity, A9/A9b target gene, A5 AlphaGenome cross-check).

Spine: data/dmg/sweep_result.tsv (10,869 scored variants). All annotation tables
are LEFT-joined by the variant key (chrN-pos-ref-alt), so annotation columns are
populated only where that analysis covered the variant (documented per column in
the data dictionary). Nothing is invented; every column traces to a source file.

Outputs (regulatory_map/):
  ncypher_dmg_regulatory_map.tsv            full map, 10,869 rows
  ncypher_dmg_regulatory_map.parquet        same, columnar (if pyarrow present)
  ncypher_dmg_regulatory_map.converged.tsv  the 164-converged shortlist (rich)
  manifest.json                             row counts, sources + md5, thresholds

Rebuilding requires the local data/ + results/ (fetched, not committed), same as
the rest of the pipeline; the built release is committed so it is directly usable.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "regulatory_map"
OUT.mkdir(exist_ok=True)

# Calibrated thresholds (from the Phase-5 sweep; see data dictionary).
CHROMATIN_HI = 0.162   # |log2FC| p99 of an 800-variant cohort background
CONSTRAINT = 2.27      # phyloP, 5% FDR

SOURCES: dict[str, Path] = {
    "sweep": ROOT / "data/dmg/sweep_result.tsv",
    "motif": ROOT / "data/dmg/motif_convergence.converged.tsv",
    "a3": ROOT / "results/a3/a3_context_matrix.tsv",
    "a9": ROOT / "results/a9/a9_target_gene_table.tsv",
    "a9b": ROOT / "results/a9b/a9b_hic_target_table.tsv",
    "a5": ROOT / "results/a5/a5_comparison_table.tsv",
}


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def derive_direction(row) -> str:
    if not row["high_impact"]:
        return "flat"
    return "gain" if row["chromatin_log2fc"] > 0 else "loss"


def derive_verdict(row) -> str:
    # Faithful to the dashboard convention: a GO needs two axes agreeing in the
    # matched context; one impactful axis is a HOLD; neither is a NO-GO.
    if row["converged"]:
        return "GO"
    if row["high_impact"] or row["constrained"]:
        return "HOLD"
    return "NO-GO"


def main() -> None:
    for name, p in SOURCES.items():
        if not p.exists():
            raise SystemExit(f"missing source '{name}': {p}")

    # ---- spine: every scored variant ---------------------------------------
    s = pd.read_csv(SOURCES["sweep"], sep="\t")
    m = pd.DataFrame()
    m["variant_id"] = s["key"]
    m["chrom"] = s["key"].str.split("-").str[0]
    m["pos"] = s["key"].str.split("-").str[1].astype(int)
    m["ref"] = s["key"].str.split("-").str[2]
    m["alt"] = s["key"].str.split("-").str[3]
    m["host_gene"] = s["gene"]
    m["variant_class"] = s["cls"]
    m["n_patients"] = s["n_patients"]
    # axis 2 — chromatin accessibility (fetal-OPC ChromBPNet, c15)
    m["chromatin_log2fc"] = s["logfc"].round(4)
    m["chromatin_abs_log2fc"] = s["abs_logfc"].round(4)
    m["chromatin_jsd"] = s["jsd"].round(4)
    m["chromatin_high_impact"] = s["high_impact"].astype(bool)
    m["chromatin_impact_pctile"] = s["impact_pctile"].round(4)
    # axis 3 — evolutionary constraint (Zoonomia phyloP, 241 mammals)
    m["phylop"] = s["phylop"].round(3)
    m["constrained"] = s["constrained"].astype(bool)
    # convergence
    m["converged"] = s["converged_2ax"].astype(bool)
    m["confidence"] = s["confidence"]
    # keep aligned helper cols for the derivations, then drop
    m["high_impact"] = m["chromatin_high_impact"]
    m["direction"] = m.apply(derive_direction, axis=1)
    m["verdict"] = m.apply(derive_verdict, axis=1)
    m = m.drop(columns=["high_impact"])

    n_total = len(m)

    # ---- mechanism: model-native motif (converged set) ---------------------
    mot = pd.read_csv(SOURCES["motif"], sep="\t")
    mot = mot.rename(columns={
        "key": "variant_id", "top_tf": "motif_top_tf",
        "delta": "motif_pwm_delta", "is_opc_tf": "motif_is_opc_lineage_tf",
    })[["variant_id", "motif_top_tf", "motif_pwm_delta", "motif_is_opc_lineage_tf"]]
    mot["motif_pwm_delta"] = mot["motif_pwm_delta"].round(3)
    m = m.merge(mot, on="variant_id", how="left")

    # ---- A3: multi-context cell-type specificity ---------------------------
    a3 = pd.read_csv(SOURCES["a3"], sep="\t").rename(columns={
        "label": "a3_context_label",
        "prog_max_abs": "a3_progenitor_max_abs_log2fc",
        "control_abs": "a3_heart_control_abs_log2fc",
    })[["key", "a3_context_label", "a3_progenitor_max_abs_log2fc", "a3_heart_control_abs_log2fc"]]
    a3 = a3.rename(columns={"key": "variant_id"})
    m = m.merge(a3, on="variant_id", how="left")

    # ---- A9: ABC target-gene linking ---------------------------------------
    a9 = pd.read_csv(SOURCES["a9"], sep="\t").rename(columns={
        "key": "variant_id", "in_se": "in_dipg_super_enhancer",
        "final_gene": "a9_target_gene", "final_basis": "a9_target_basis",
        "confidence": "a9_target_confidence", "orthogonal_eqtl": "a9_eqtl_supported",
        "nearestTSS_gene": "a9_nearest_tss_gene",
    })[["variant_id", "in_dipg_super_enhancer", "a9_target_gene", "a9_target_basis",
        "a9_target_confidence", "a9_eqtl_supported", "a9_nearest_tss_gene"]]
    a9["in_dipg_super_enhancer"] = a9["in_dipg_super_enhancer"].astype(bool)
    m = m.merge(a9, on="variant_id", how="left")

    # ---- A9b: matched fetal Hi-C target ------------------------------------
    a9b = pd.read_csv(SOURCES["a9b"], sep="\t").rename(columns={
        "key": "variant_id", "hic_top_gene": "a9b_hic_target_gene",
        "hic_top_obsexp": "a9b_hic_obs_over_exp", "tier": "a9b_hic_tier",
    })[["variant_id", "a9b_hic_target_gene", "a9b_hic_obs_over_exp", "a9b_hic_tier"]]
    a9b["a9b_hic_obs_over_exp"] = a9b["a9b_hic_obs_over_exp"].round(3)
    m = m.merge(a9b, on="variant_id", how="left")

    # ---- A5: AlphaGenome orthogonal cross-check ----------------------------
    a5 = pd.read_csv(SOURCES["a5"], sep="\t").rename(columns={
        "variant_id": "variant_id", "ag_direction": "a5_alphagenome_direction",
        "dir_agree": "a5_direction_agrees", "agreement_class": "a5_agreement_class",
    })[["variant_id", "a5_alphagenome_direction", "a5_direction_agrees", "a5_agreement_class"]]
    a5["a5_direction_agrees"] = a5["a5_direction_agrees"].astype("boolean")
    m = m.merge(a5, on="variant_id", how="left")

    # ---- tidy: stable sort (converged first, then by impact) ---------------
    m = m.sort_values(
        by=["converged", "chromatin_abs_log2fc"], ascending=[False, False]
    ).reset_index(drop=True)

    # ---- coverage report ----------------------------------------------------
    cov = {
        "total_scored": n_total,
        "converged": int(m["converged"].sum()),
        "in_super_enhancer": int((m["in_dipg_super_enhancer"] == True).sum()),
        "with_motif_call": int(m["motif_top_tf"].notna().sum()),
        "with_a3_context_label": int(m["a3_context_label"].notna().sum()),
        "with_a9_target_gene": int(m["a9_target_gene"].notna().sum()),
        "with_a9b_hic_target": int(m["a9b_hic_target_gene"].notna().sum()),
        "with_a5_alphagenome": int(m["a5_alphagenome_direction"].notna().sum()),
        "verdict_GO": int((m["verdict"] == "GO").sum()),
        "verdict_HOLD": int((m["verdict"] == "HOLD").sum()),
        "verdict_NOGO": int((m["verdict"] == "NO-GO").sum()),
    }

    # ---- write outputs ------------------------------------------------------
    full_tsv = OUT / "ncypher_dmg_regulatory_map.tsv"
    m.to_csv(full_tsv, sep="\t", index=False)

    conv = m[m["converged"]].copy()
    conv_tsv = OUT / "ncypher_dmg_regulatory_map.converged.tsv"
    conv.to_csv(conv_tsv, sep="\t", index=False)

    parquet_ok = False
    try:
        import pyarrow  # noqa: F401
        m.to_parquet(OUT / "ncypher_dmg_regulatory_map.parquet", index=False)
        parquet_ok = True
    except Exception as e:  # pragma: no cover
        print(f"[parquet skipped: {e}]")

    manifest = {
        "name": "NCypher DMG non-coding regulatory map",
        "version": "1.0.0",
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "description": (
            "Every scored somatic non-coding SNV in the OpenPedCan H3 K27M DMG "
            "cohort, with chromatin score, evolutionary constraint, two-axis "
            "convergence verdict, model-native motif, and Claude Science hardening "
            "annotations (A3 context-specificity, A9/A9b target gene, A5 cross-check)."
        ),
        "genome": "GRCh38",
        "model": "developing-brain ChromBPNet, fetal-OPC (Trevino 2021 cluster c15)",
        "thresholds": {"chromatin_high_impact_abs_log2fc": CHROMATIN_HI,
                       "constraint_phylop": CONSTRAINT},
        "n_columns": m.shape[1],
        "coverage": cov,
        "columns": list(m.columns),
        "sources": {k: {"path": str(v.relative_to(ROOT)), "md5": md5(v),
                        "rows": int(sum(1 for _ in v.open()) - 1)}
                    for k, v in SOURCES.items()},
        "files": {
            "full_tsv": full_tsv.name,
            "converged_tsv": conv_tsv.name,
            "parquet": "ncypher_dmg_regulatory_map.parquet" if parquet_ok else None,
        },
        "provenance_note": (
            "Annotation columns are populated only where that analysis covered the "
            "variant (LEFT join by variant_id); nulls are 'not assessed', not "
            "'assessed negative'. See data_dictionary.md."
        ),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))

    print(f"wrote {full_tsv.name} ({n_total} rows, {m.shape[1]} cols)")
    print(f"wrote {conv_tsv.name} ({len(conv)} converged rows)")
    print(f"parquet: {'yes' if parquet_ok else 'no'}")
    print("coverage:", json.dumps(cov, indent=2))


if __name__ == "__main__":
    main()
