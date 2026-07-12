# A9 — ABC target-gene linking for the 164 converged variants

**Question.** NCypher reports the host / nearest gene for each converged variant. Does an Activity-by-Contact (ABC) pass, using matched fetal-OPC accessibility as the activity term, reassign any of these to a different, better-supported target gene, and does it resolve the flagship shortlist (LINC01117, NPAS3, COL1A1, IER2)?

**One-line verdict.** Power-law ABC with matched c15 activity reproduces the distance call almost everywhere, so it does **not** out-resolve nearest-gene. Its value here is corroboration, not reassignment: at 9 loci (of 164), the matched-activity ABC top gene, the nearest-TSS gene, and an independent brain eQTL all agree on a target that is **not** the intron-host gene NCypher currently reports. LINC01117 is the one flagship that reassigns cleanly (to LINC01116); NPAS3, COL1A1 and IER2 keep their host-gene default.

---

## Inputs and provenance (all confirmed unless marked inferred)

- **Variants:** `data/dmg/enhancers/a9_input.tsv` — 164 two-axis-converged somatic SNVs (staged by `scripts/prep_a9_input.py` from `data/dmg/sweep_result.tsv`; the same 164 the MCP `cohort_summary` reports).
- **Activity:** `data/dmg/c15_peaks.bed.gz` — 115,662 Corces fetal-OPC (cluster c15) ATAC narrowPeak, hg38. Activity term = column 7 `signalValue` of the enclosing peak. **ATAC-only** (no H3K27ac track fetched; stated per method).
- **TSS / candidate genes:** GENCODE v44 (hg38) gene models, fetched fresh from EBI (`gencode.v44.annotation.gtf.gz`), gene-level TSS extracted (62,700 genes; candidate universe restricted to 38,912 protein_coding + lncRNA). *Note: the repo's staged `tss_hg38_gencode_v44.tsv.gz` carries coordinates only, no gene names, so it cannot label ABC targets; the GTF was re-fetched for gene names and biotypes.*
- **Contact:** distance power-law, `Contact = max(|d|, 5 kb)^-0.87` (gamma 0.87, Fulco 2019 / Nasser 2021; zero download). **No Hi-C prior used** — the ENCODE average-Hi-C file `ENCFF134PUN` is a 58 GB GRCh38 contact-domains BED, not a usable 5 kb interaction matrix, and impractical in this sandbox; the brief marks it optional. A gamma sensitivity sweep stands in for the contact-prior robustness check (below).
- **Orthogonal support:** GTEx v8 single-tissue cis-eQTLs, 13 brain tissues, queried live from the GTEx v2 API for 184 candidate genes (67 have ≥1 brain eQTL). A gene is "eQTL-supported" for an element if it has a brain eQTL whose lead SNP lies within 10 kb of the element midpoint.
- **MCP grounding:** NCypher `cohort_summary` (10,869 scored; 164 converged; 0 recurrent, 0 canonical-driver) and `score_variant` on the four flagship variants (all GO, chromatin loss + constrained).

## Method

For each variant: (1) the enclosing c15 peak is the element, its signalValue the activity; (2) candidate genes = all protein_coding/lncRNA TSS within 1 Mb of the element midpoint (median 23 candidates); (3) `ABC(e,g) = Activity(e)·Contact(e,g) / Σ_elements Activity·Contact` over all c15 peaks within 1 Mb of g's TSS; (4) rank candidates, compare the top to nearest-gene; (5) HIGH confidence only where the ABC-top gene also carries a proximal brain eQTL.

## Headline numbers (reviewer-verified — recomputed from an independent code path off the raw files, all matched)

| Quantity | Value |
|---|---|
| Converged variants linked | 164 |
| All have an enclosing c15 peak | 164 / 164 |
| ABC-top == matched nearest-TSS gene | **139 / 164 (85%)** |
| ABC-top == input host/nearest-gene label | 40 / 164 (24%) |
| input host-gene == matched nearest-TSS | 43 / 164 |
| ABC-top gene stable across gamma 0.70 / 0.87 / 1.00 | 155 / 164 (95%) |
| HIGH-confidence links (proximal brain eQTL for ABC-top) | 21 |
| — of which unambiguous, differ from host, not near-tie | **9** |
| — of which near-ties (top:2nd ratio < 1.25) | 8 |

The 24% vs 85% gap is the key artefact to read correctly: **power-law ABC tracks distance** (Contact is a function of distance, so ABC ≈ activity-weighted nearest-TSS), and it agrees with the nearest **TSS** 85% of the time. The low 24% agreement with the *input* label is mostly because NCypher's `nearest_gene` is a gene-body/intron **host** assignment (only 43/164 input labels are even the nearest TSS), not because ABC discovered anything distal.

## The concrete flagship calls

| Variant | Host (NCypher) | ABC top | ratio (top:2nd) | brain eQTL ≤10 kb | Call |
|---|---|---|---|---|---|
| chr2-176638323-C-A | LINC01117 | **LINC01116** | 12.5× | 10 (5 tissues, p=2e-20) | **Reassign → LINC01116 (HIGH)** |
| chr14-33788719-A-G | NPAS3 | novel lncRNA (ENSG…87777) | 1.8× | 0 | Keep NPAS3 (default) |
| chr17-50200666-C-T | COL1A1 | COL1A1 | 1.0× (tie w/ overlapping lncRNA) | 0 | Keep COL1A1 (default) |
| chr19-13151895-C-G | IER2 | STX10 | 1.0× (tie w/ IER2) | 0 | Keep IER2 (default) |

**LINC01117 → LINC01116.** The variant sits inside the LINC01117 gene body (intron), so NCypher labels it LINC01117 — but LINC01117's TSS is 143 kb away, while LINC01116's TSS is 306 bp from the element. ABC prefers LINC01116 by 12.5×, and LINC01116 carries 10 brain cis-eQTLs within 10 kb of the element across 5 tissues (best p=2e-20). Distance, matched activity, and eQTL all agree: **this element most likely regulates LINC01116, not its host LINC01117.** This is the one flagship reassignment, and the strongest HIGH-confidence link in the set.

**NPAS3 is not resolved as its own target by ABC, but the ABC call is not trustworthy here.** NPAS3's TSS is 854 kb from the variant; the top ABC candidate is a nearby novel lncRNA (105 kb away) with no eQTL and a weak 1.8× margin. Power-law ABC penalises the 854 kb NPAS3 distance heavily and has no way to see a long-range intronic-enhancer→NPAS3 loop, which is exactly the regulation a fetal-OPC Hi-C map would test. So ABC does **not** support NPAS3 as the target, but with power-law contact and no OPC Hi-C this is a floor, not a verdict — NPAS3 keeps its host-gene default and the caveat is explicit.

**COL1A1 does not re-target.** ABC-top is COL1A1 itself (the TSS is 764 bp away), effectively tied (1.0×) with an overlapping antisense lncRNA. There is no proximal brain eQTL. ABC gives no reason to move the COL1A1 hit off COL1A1, so the direction-discordance argument in `col1a1-glioma-evidence.md` (a loss-of-accessibility variant on an over-expression oncogene) **stands**: the hit remains parked for the same reason, not revived by re-targeting.

**IER2 is a genuine near-tie with STX10.** The element sits between the head-to-head TSSs of IER2 (1,511 bp) and STX10 (1,539 bp); ABC cannot separate them (1.0×) and neither has a proximal brain eQTL. Honest call: bidirectional-promoter ambiguity, keep IER2 as default and flag STX10 as an equally-likely co-target.

## Falsification (the skeptic check, done)

**Claim under test:** "the 9 HIGH reassignments show matched-activity ABC out-resolving nearest-gene."

**Strongest argument against:** power-law ABC *is* a distance function, so a "reassignment" could just be the input host-label being an intron/gene-body call rather than the nearest TSS, with the eQTL then riding on whatever gene is nearest.

**Test result: the argument holds.** In **9 / 9** HIGH reassignments the ABC-top gene is identical to the matched nearest-TSS gene. So ABC did not beat distance; it agreed with it. The honest framing is therefore **not** "ABC reassigned 9 targets" but "at 9 loci, distance + matched c15 activity + an independent brain eQTL all agree the target is a non-host gene that NCypher's intron-host label misses." That is a resource (well-supported links to validate), not a demonstration that ABC out-resolves nearest-gene — consistent with the method note that power-law + activity does not beat distance without a real contact map.

## Honest guardrails observed

- No reassignment percentage is headlined; the deliverable is the 9 (+ LINC01117 flagship) orthogonally-supported links as a resource.
- ATAC-only activity and power-law-only contact are stated; ABC is not claimed to beat distance.
- Brain eQTL is proximity-biased and cell-type-mismatched (adult bulk brain, not fetal OPC), so an eQTL negative (NPAS3, COL1A1, IER2) is a floor, not a verdict.
- Every link is a single-patient, private hypothesis to validate (CRISPRi of the element in an OPC-like line, read out the candidate and host gene), not a proven target assignment.

## Artefacts
- `a9_target_gene_table.tsv` — per-variant: host / nearest-TSS / ABC-top gene, margin, gamma-stability, eQTL support, confidence tier, final call.
- `a9_target_gene_figure.png` — (a) flagship candidate-gene ABC bars with eQTL/host annotation; (b) the 9 HIGH-confidence reassignments.
