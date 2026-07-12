# NCypher DMG non-coding regulatory map — data dictionary

Version 1.0.0 · genome GRCh38 · one row per scored somatic non-coding SNV.

This is the machine-readable companion to the map. Every column is defined below
with its source analysis and its coverage (how many of the 10,869 rows carry a
non-null value). **A null is "not assessed", never "assessed negative"** — the
richer annotations only cover the 164 two-axis-converged hits (or smaller sets),
by design.

> **Working with the files (types matter).** Prefer the **Parquet** for
> programmatic queries: it preserves real dtypes, so `df[df.a9_eqtl_supported]`
> and `df.converged == True` work directly. In the **TSV**, booleans round-trip as
> the strings `"True"` / `"False"`, so a naive `== True` filter silently returns
> nothing — compare to `"True"` or load the Parquet. Agents can also pull the map
> through the MCP **tool** `get_regulatory_map` (or the `ncypher://regulatory-map`
> resource), which returns the 164 converged rows already typed.

## Grain and coverage

- **10,869 rows** — every somatic non-coding SNV in the OpenPedCan H3 K27M DMG
  cohort (152 patients) that lands in a fetal-OPC (c15) regulatory element.
- **164 converged** — pass both the chromatin and constraint axes; these carry the
  full annotation set (motif, A3 context, A9/A9b target, A5 where run).
- **31** of the converged sit inside a DIPG super-enhancer (the flagship finding).

## The three axes (the core score)

| column | type | source | definition |
|---|---|---|---|
| `variant_id` | str | sweep | `chrN-pos-ref-alt` (GRCh38). Primary key. |
| `chrom` `pos` `ref` `alt` | str/int | sweep | Parsed coordinates. |
| `host_gene` | str | sweep | Gene whose intron/body the variant falls in. **Provisional**: only 43/164 are the nearest TSS (see `a9_*`). |
| `variant_class` | str | sweep | Intron / promoter / UTR / intergenic. |
| `n_patients` | int | sweep | Patients carrying this exact SNV (cohort is private/sparse: mostly 1). |
| `chromatin_log2fc` | float | sweep | **Axis 2.** Predicted alt-vs-ref accessibility change, fetal-OPC ChromBPNet (c15). +gain / −loss. |
| `chromatin_abs_log2fc` | float | sweep | \|log2FC\|. |
| `chromatin_jsd` | float | sweep | Jensen-Shannon divergence of the predicted profiles (shape change). |
| `chromatin_high_impact` | bool | sweep | \|log2FC\| ≥ **0.162** (p99 of an 800-variant cohort background). |
| `chromatin_impact_pctile` | float | sweep | Percentile of \|log2FC\| within the cohort. |
| `phylop` | float | sweep | **Axis 3.** Zoonomia phyloP (241 mammals). Higher = more constrained. |
| `constrained` | bool | sweep | phyloP ≥ **2.27** (5% FDR). |

> Axis 1 (measured MPRA/reporter function) is deliberately **not** a column: it is
> orthogonal (reporter activity ≠ chromatin accessibility) and the cohort's somatic
> variants are not in the MPRA DAV set. See the model card for why.

## Convergence and verdict

| column | type | source | definition |
|---|---|---|---|
| `converged` | bool | sweep | Two-axis convergence: `chromatin_high_impact AND constrained`. The 164. |
| `confidence` | str | sweep | Calibrated tier (low/medium/high) for converged hits. |
| `direction` | str | derived | gain / loss (if high-impact) else flat. |
| `verdict` | str | derived | **GO** if converged; **HOLD** if exactly one axis is impactful; **NO-GO** otherwise. Counts: 164 / 2,008 / 8,697. Mirrors the dashboard convention: a GO needs two axes agreeing in the matched context. |

## Mechanism (model-native motif) — converged set (164)

| column | type | source | definition |
|---|---|---|---|
| `motif_top_tf` | str | `motif_convergence.converged.tsv` | Top PWM-disrupted TF at the variant. **Caveat:** a crude PWM top call, noisy for some hits (e.g. NPAS3 returns CTCF; the reliable signal there is the DeepSHAP contribution collapse, not this label). |
| `motif_pwm_delta` | float | motif | PWM score change (negative = motif broken). |
| `motif_is_opc_lineage_tf` | bool | motif | Whether `motif_top_tf` is an OPC-lineage master TF (SOX10, NFIA, OLIG2, …). |

> The de-novo motif grammar the model learned genome-wide (SOX / OLIG2 / ETS,
> not a GC shortcut) is the **A4** result; it is model-level, not per-variant, so it
> lives in `results/a4/` and the model card, not as a column here.

## A3 — multi-context cell-type specificity — converged set (164)

| column | type | source | definition |
|---|---|---|---|
| `a3_context_label` | str | `a3_context_matrix.tsv` | **OPC-specific** (80) / **broad** (56) / **weak** (28). "OPC-specific" = fires in developing-brain progenitors but not the non-neural fetal-heart control; it means **neural-not-cardiomyocyte, not OPC-not-other-progenitor** (the signal is progenitor-broad within neural lineages). |
| `a3_progenitor_max_abs_log2fc` | float | A3 | Max \|log2FC\| across the unselected progenitor contexts (c10/c11/c9). |
| `a3_heart_control_abs_log2fc` | float | A3 | \|log2FC\| in the non-neural fetal-heart control. |

## Super-enhancer membership

| column | type | source | definition |
|---|---|---|---|
| `in_dipg_super_enhancer` | bool | `a9_target_gene_table.tsv` | Inside one of the Nagaraja DIPG super-enhancers (the flagship finding; 31 converged). |

## A9 — ABC target-gene linking — converged set (164)

| column | type | source | definition |
|---|---|---|---|
| `a9_target_gene` | str | `a9_target_gene_table.tsv` | Best-supported regulated gene. **Honest default:** without matched Hi-C, ABC reduces to distance, so 143/164 are `nearest-default` and only 21 are HIGH-confidence reassignments. |
| `a9_target_basis` | str | A9 | How the target was called (nearest-gene default / ABC-reassigned (HIGH) / …). |
| `a9_target_confidence` | str | A9 | HIGH (21) vs nearest-default (143). |
| `a9_eqtl_supported` | bool | A9 | An independent brain eQTL (≤10 kb) supports the link. |
| `a9_nearest_tss_gene` | str | A9 | Nearest TSS gene (the distance baseline). |

> **Two different "nearest-TSS" counts, do not conflate.** `host_gene` is provisional
> because only **43/164** converged variants have a host gene that *is* the nearest TSS
> (an intron/gene-body labelling convention). Separately, of the A9 *target* calls,
> **21/164** are HIGH-confidence ABC reassignments and **143/164** fall back to the
> nearest-gene default. The 43 (host-gene provenance) and the 21 (A9 reassignments) are
> distinct quantities on different denominators.

## A9b — matched fetal Hi-C reassignment probe — converged set (164)

Real Won-2016 fetal germinal-zone Hi-C. This tests whether the ABC-**top** gene
*reassigns* under real 3D contact. It mostly does not (the headline A9b negative:
54/164 tops change, but they skew into structural hubs with no eQTL support).

| column | type | source | definition |
|---|---|---|---|
| `a9b_hic_target_gene` | str (Ensembl ID) | `a9b_hic_target_table.tsv` | Hi-C-reweighted ABC **top** gene. |
| `a9b_hic_obs_over_exp` | float | A9b | Observed/expected contact for that top gene. |
| `a9b_hic_tier` | str | A9b | AMBIGUOUS (105) / HOST-CONFIRMED (33) / LOOP-ONLY (18) / TRIANGULATED (8). |

> **Important NPAS3 caveat.** For the flagship lead NPAS3, `a9b_hic_tier` is
> `AMBIGUOUS` because the reweighted ABC-*top* gene is a structural-hub artefact —
> this is exactly the A9b "structural hubs contaminate ABC-top" finding, **not** a
> refutation of NPAS3. The **targeted** element→NPAS3-promoter loop was separately
> **confirmed at obs/exp 5.6 (99.8th percentile)** — see
> `results/a9b/npas3_loop_probe.json`. The column here answers "does the ABC-top
> gene reassign?", not "does the specific NPAS3 loop exist?".

## A5 — AlphaGenome orthogonal cross-check — 37 variants (31 SE + heroes)

An independent generic model (no fetal-OPC track); a second opinion, **not** ground
truth. Coverage is 37, not the full converged set: only the pre-selected SE-resident
+ hero variants were scored (TERT is a positive control outside the cohort sweep, so
37/38 of the comparison table join here).

| column | type | source | definition |
|---|---|---|---|
| `a5_alphagenome_direction` | str | `a5_comparison_table.tsv` | AlphaGenome's predicted direction (gain/loss). |
| `a5_direction_agrees` | bool | A5 | Agrees with NCypher's chromatin direction (82% overall, survives). |
| `a5_agreement_class` | str | A5 | both impactful (13) / NCypher only (23) / both not (1). Magnitude is threshold-hostage and deliberately not reduced to one number. NPAS3 is "NCypher only" (AlphaGenome, lacking an OPC track, does not see it) → a nomination, not a cross-confirmed hit. |

## Provenance and reproducibility

- Built by `scripts/build_regulatory_map.py` (LEFT joins by `variant_id`; no values
  invented). Source file paths + md5 + row counts are in `manifest.json`.
- **Access:** the built files here, the MCP resource `ncypher://regulatory-map`, and the
  MCP tool `get_regulatory_map` (for hosts that surface tools but not resources) all serve
  the same map.
- **Shared cache, not an orthogonal oracle:** the MCP `score_variant` tool and this map's
  chromatin/constraint columns both read the same discovery sweep, so cross-checking a row
  against `score_variant` is a *consistency* check (the join preserved the values), not an
  independent re-derivation of the axes.
- Thresholds: chromatin high-impact \|log2FC\| ≥ 0.162; constrained phyloP ≥ 2.27.
- Rebuilding needs the local `data/` + `results/` (fetched, not committed — same
  model as the rest of the pipeline). The built release is committed for direct use.
- Licence: Apache-2.0 (repo). Cohort: OpenPedCan (open); model: developing-brain
  ChromBPNet (Marderstein/Kundu 2026, Corces × Kundaje); constraint: Zoonomia.

## What this map is, and is not

- **Is:** a reproducible, mechanism-annotated shortlist of non-coding variants to
  *validate*, with every axis, verdict, and hardening annotation traceable to source.
- **Is not:** a set of proven drivers (they are private single-patient hypotheses),
  a general variant-effect predictor, or a claim to out-predict AlphaGenome/Enformer.
  Confidence is highest where axes and orthogonal evidence agree; disagreements are
  surfaced, not hidden.
