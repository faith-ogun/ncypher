# NCypher DMG regulatory map — agent-queryability & scientific audit

**Reviewer run**, 2026-07-12. Every number below was read from the granted files or returned live by the NCypher MCP; provenance is cited inline. British English, honest verdict either way.

## 1. Load the map two ways and confirm they agree

**(a) MCP resource `ncypher://regulatory-map` — NOT reachable through the connector as wired.**
The `ncypher` connector bridge (`host.mcp`) surfaces only the three *tools* it registers: `score_variant`, `top_candidates`, `cohort_summary`. Every attempt to read a resource (`resources/read`, `read_resource`, `ncypher://regulatory-map`, `regulatory-map`) returned `unknown method … Known server tools: score_variant, top_candidates, cohort_summary`. The resource *is* defined in `mcp/server.py:819` (`@mcp.resource("ncypher://regulatory-map")`), so the server declares it, but the Claude Science connector layer exposes tools only, not MCP resources/prompts. **This is a real gap: an agent in this project cannot read the map via the resource URI.**

Workaround used for the audit: the resource function is a deterministic read of `manifest.json` + `ncypher_dmg_regulatory_map.converged.tsv`, so I reproduced its exact payload from those files. It returns `schema` (37 cols), `coverage`, and the 164-row `converged_shortlist` — identical to what the function would emit.

**(b) Full table `ncypher_dmg_regulatory_map.parquet` (and `.tsv`).** Both load, agree on row count and columns.

| check | value | source |
|---|---|---|
| rows (parquet) | **10,869** | parquet |
| rows (tsv) | 10,869 (== parquet, same 37 cols) | tsv |
| `converged == True` | **164** | parquet |
| resource `converged_shortlist` rows | 164 (== parquet converged) | converged.tsv via resource fn |
| verdict split | **164 GO / 2,008 HOLD / 8,697 NO-GO** | parquet `verdict` |
| in DIPG super-enhancer | 31 | parquet |
| source sweep md5 | `64cf28713f…` == manifest | data/dmg/sweep_result.tsv |

`cohort_summary` (live MCP) independently reports 10,869 scored, 753 chromatin high-impact, 1,583 constrained, 164 converged. HOLD is internally consistent: (753−164)+(1,583−164) = 2,008; NO-GO = 10,869−164−2,008 = 8,697. **All step-1 counts confirmed.**

## 2. A real triage question answered purely from the map

Shortlist = `verdict == "GO"` AND `a3_context_label == "OPC-specific"` AND `a9_eqtl_supported == True`, ranked by `chromatin_abs_log2fc`. **7 variants** (the full set, not a top-10 — the filter is that selective).

| variant_id | host_gene | chromatin_log2fc | phylop | motif_top_tf | a9_target_gene |
|---|---|---:|---:|---|---|
| chr6-105474324-C-G | LOC105377921 | −0.429 | 3.50 | NEUROD1 | PREP |
| chr1-178871299-T-G | RALGPS2 | −0.378 | 2.30 | CTCF | ANGPTL1 |
| chr1-110300824-C-T | RBM15-AS1 | −0.378 | 5.91 | OLIG2 | RBM15-AS1 |
| chr17-56129764-G-A | ANKFN1 | −0.267 | 6.97 | OLIG2 | ANKFN1 |
| chr14-96614717-A-G | ENSR00001202083 | −0.248 | 6.31 | POU3F2 | ENSG00000258702 |
| chr3-43273596-C-G | Unknown | +0.211 | 4.04 | NFIA | SNRK |
| chr5-54543565-G-T | SNX18 | −0.206 | 4.94 | NEUROD1 | SNX18 |

**Cross-check, top row `chr6-105474324-C-G` via `score_variant`:**

| axis | map | MCP `score_variant` | match |
|---|---|---|---|
| chromatin log2FC | −0.4294 | −0.43 | ✓ |
| JSD | 0.098 | 0.098 | ✓ |
| phyloP | 3.50 | 3.50 | ✓ |
| verdict | GO | GO | ✓ |

Axes match exactly. **Caveat on independence:** `score_variant` serves from the same DMG discovery cache (`sweep_result.tsv`) that feeds the map's chromatin/constraint columns, so this confirms the LEFT-join did not corrupt values — it is a *consistency* check, not an independent re-derivation of the axes.

The query itself was clean: three equality filters + one sort, straight off the parquet. The one snag an agent will hit is dtype — after a TSV round-trip `a9_eqtl_supported` is the string `"True"`, not a Python bool, so a naive `== True` silently returns nothing. The parquet preserves bool; the TSV does not.

## 3. Scientific audit of schema and caveats

**Column naming:** clear and consistent. Axis columns (`chromatin_*`, `phylop`, `constrained`), verdict logic (`converged`, `verdict`), and the hardening tiers are prefixed by analysis (`a3_/a5_/a9_/a9b_`), which makes provenance legible. `host_gene` is honestly flagged provisional (only 43/164 are nearest-TSS). Minor: `host_gene` vs `a9_nearest_tss_gene` vs `a9_target_gene` is three gene columns; correct, but an agent must read the dictionary to pick the right one.

**Null semantics:** explicitly and correctly documented — "A null is 'not assessed', never 'assessed negative'" appears in the README, the dictionary header, and the manifest `provenance_note`. Verified in the data: NPAS3 has 8 rows in the map but only 1 is converged; the other 7 carry null across every annotation column (motif/A3/A9/A9b), exactly as a LEFT join onto the 164-only annotation tables should behave. Null semantics are sound.

**(a) NPAS3 `a9b_hic_tier` = AMBIGUOUS vs the confirmed loop.** Confirmed in data and dictionary.
- Map row `chr14-33788719-A-G`: `a9b_hic_tier = AMBIGUOUS`, `a9b_hic_target_gene = ENSG00000287777`, `a9b_hic_obs_over_exp = 0.964`. That obs/exp is for the reweighted ABC-*top* gene (the structural-hub artefact), **not** the NPAS3 loop.
- `results/a9b/npas3_loop_probe.json`: element→NPAS3-promoter `obs_over_expected = 5.601`, `percentile_vs_distmatched = 99.81` — the targeted loop is confirmed.
- The dictionary states both, and states the distinction correctly: the column answers "does the ABC-top gene reassign?" (0.964, ambiguous), not "does the specific NPAS3 loop exist?" (5.6, confirmed). Not a refutation of NPAS3 — it is the A9b "structural hubs contaminate ABC-top" finding. **Caveat correct.**

**(b) NPAS3 `motif_top_tf` is the known-noisy PWM call.** Confirmed. Map has `motif_top_tf = CTCF`, `motif_is_opc_lineage_tf = False` for the NPAS3 converged row. The dictionary flags exactly this: "noisy for some hits (e.g. NPAS3 returns CTCF; the reliable signal there is the DeepSHAP contribution collapse, not this label)." **Caveat correct.**

## 4. Verdict

**Is the map agent-queryable? Partly — YES as a table, NO via the advertised resource URI.**

- The parquet/TSV is fully, cleanly agent-queryable: real triage questions resolve in a few dataframe operations, counts are exact and self-consistent, and every axis reconciles with the live MCP `score_variant`. The scientific content is sound: honest null semantics, both NPAS3 caveats present and correct, verdict logic internally consistent, source md5 matches the manifest.
- But the task's step 1(a) — "read the MCP resource `ncypher://regulatory-map`" — **cannot be done through the connector as currently wired.** The connector exposes tools only; the resource (and the `triage_variant` prompt) are declared in the server but invisible to `host.mcp`. An agent told "read `ncypher://regulatory-map`" will fail.

**Fixes to feed back to the build script / server wiring:**
1. **Resource not reachable (highest priority).** Either expose MCP resources through the connector, or add a thin *tool* wrapper — e.g. `get_regulatory_map()` — that returns the same manifest + schema + 164-shortlist payload the resource function produces. Right now `top_candidates`/`cohort_summary`/`score_variant` are the only doors, and none of them hands back the manifest/schema or the download paths.
2. **TSV boolean fidelity.** `a9_eqtl_supported`, `constrained`, `converged`, `chromatin_high_impact`, `motif_is_opc_lineage_tf` round-trip through the TSV as strings `"True"/"False"`. The README quickstart uses the parquet (fine), but any agent handed the TSV and told `== True` gets a silent empty result. Either document "use the parquet for boolean filters" prominently, or write TSV booleans as `1/0`.
3. **Minor wording.** The README says "only 21 are HIGH-confidence reassignments" while the dictionary says `host_gene` "only 43/164 are the nearest TSS" — two different denominators for related claims; a one-line note that these are distinct quantities (target-reassignment count vs host==nearest-TSS count) would prevent an agent conflating them.
4. **Cross-check independence.** Consider stating in the dictionary that `score_variant` and the map share the sweep cache, so re-scoring a map variant is a consistency check, not an orthogonal axis validation — an agent might otherwise present it as independent confirmation.

**Honest bottom line:** the science holds and the table is genuinely queryable; the caveats are present and correct. The one thing that does not work as written is the resource URI itself — the headline access path in the brief. That is a wiring fix, not a data problem.
