# NCypher DMG non-coding regulatory map

**A downloadable, agent-queryable map of every scored somatic non-coding variant in
paediatric H3 K27M diffuse midline glioma (DMG), with its regulatory score, the
mechanism, the two-axis convergence verdict, and every orthogonal hardening check.**

This is the resource leg of NCypher: not a leaderboard, but a reproducible,
mechanism-explained shortlist of which non-coding variants to validate next, and why.

## Files

| file | what it is |
|---|---|
| `ncypher_dmg_regulatory_map.tsv` | The full map — **10,869** scored variants × 37 columns. |
| `ncypher_dmg_regulatory_map.parquet` | Same, columnar (fast for agents / dataframes). |
| `ncypher_dmg_regulatory_map.converged.tsv` | The **164** two-axis-converged hits — the useful shortlist, fully annotated. |
| `data_dictionary.md` | Every column defined, with source analysis, coverage, and caveats. **Read this first.** |
| `manifest.json` | Version, row counts, source files + md5, thresholds, coverage. |

## Quickstart

```python
import pandas as pd
m = pd.read_parquet("ncypher_dmg_regulatory_map.parquet")   # preferred: preserves dtypes

# The validation shortlist: two-axis GO, OPC-context-specific, strongest first.
go = m[(m.verdict == "GO") & (m.a3_context_label == "OPC-specific")]
go.sort_values("chromatin_abs_log2fc", ascending=False)[
    ["host_gene", "chromatin_log2fc", "phylop", "motif_top_tf",
     "a9_target_gene", "a9_eqtl_supported"]
].head(10)
```

**Use the Parquet for programmatic queries.** It preserves real booleans/numbers, so
`m[m.a9_eqtl_supported]` works. In the TSV, booleans are the strings `"True"`/`"False"`,
so a naive `== True` filter silently returns nothing (compare to `"True"`, or load the Parquet).

**For agents:** the map is also served through the MCP tool **`get_regulatory_map`** (manifest +
schema + the 164 converged rows, already typed) and the resource **`ncypher://regulatory-map`**.
Use the tool on hosts that surface tools but not MCP resources.

## How to read it (one paragraph)

Each row is one variant. Two axes carry the call: **chromatin** (`chromatin_log2fc`,
high-impact at |log2FC| ≥ 0.162, fetal-OPC ChromBPNet) and **constraint**
(`phylop`, constrained at ≥ 2.27, Zoonomia). A variant is `converged` (verdict
**GO**) only when both fire — 164 of 10,869. For those, the map adds the model-native
**mechanism** (`motif_*`), the **cell-type specificity** (`a3_context_label`), the
**target gene** (`a9_*`, `a9b_*`), and an **independent second opinion**
(`a5_*`). Nulls mean "not assessed at this tier", never "assessed negative".

## The honesty rules baked in (so you can trust it)

- Confidence is highest where axes and orthogonal evidence **agree**; disagreements
  are surfaced (e.g. NPAS3 is a top nomination, *not* cross-confirmed by AlphaGenome).
- "OPC-specific" means **neural, not cardiomyocyte** — a developing-brain-progenitor
  signal, not OPC-exclusive (see A3 caveat in the dictionary).
- Target genes are mostly the nearest-TSS default (143/164); only 21 are HIGH-confidence
  reassignments. The NPAS3 Hi-C loop is confirmed by a *targeted* probe (obs/exp 5.6),
  even though its ABC-top gene reads AMBIGUOUS — read the dictionary's NPAS3 caveat.
- These are **hypotheses to validate**, not proven drivers, and NCypher does not claim
  to out-predict general variant-effect models.

## Provenance / rebuild

Built by [`scripts/build_regulatory_map.py`](../scripts/build_regulatory_map.py) — a
deterministic LEFT-join of the scored sweep with the Claude Science hardening tables
(A3/A5/A9/A9b) and the motif calls, keyed by `variant_id`. Rebuilding needs the local
`data/` + `results/` (fetched, not committed). Cohort: OpenPedCan (open). Model:
developing-brain ChromBPNet (fetal-OPC c15). Licence: Apache-2.0.
