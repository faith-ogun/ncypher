# A5: AlphaGenome as an independent second opinion on NCypher's chromatin calls

**Task:** for the 31 super-enhancer-resident converged hits plus 7 hero variants (38 total), does AlphaGenome corroborate NCypher's chromatin call, and where it disagrees, is that informative?

**One-line verdict:** On the axis both models measure the same way (direction of accessibility change), AlphaGenome corroborates NCypher on **82% of variants (31/38, binomial p=5.8e-5)** and this **survives**. On magnitude, the two are **weakly and non-significantly correlated** (Spearman rho=0.23, p=0.16), and any single binary "both impactful" concordance number is **threshold-hostage** (92% at the AlphaGenome background median falling to 13% at p99) and should not be quoted alone. This is a generic second opinion, **not** validation: AlphaGenome is not DMG- or OPC-specific and NCypher is not shown to beat it or be validated by it.

## Provenance
- Test variants: `data/dmg/enhancers/a5_input.tsv` (31 se-hit + 7 hero = 38; the brief's "8 heroes" counts NPAS3, which sits in the SE-resident set here, so 7 distinct hero rows).
- NCypher call: live NCypher MCP `score_variant` per variant (not the staged column). Chromatin-impactful defined at NCypher's own calibrated cutoff |log2FC| >= 0.162 (p99 of an 800-variant background); this reproduces NCypher's own `[impactful]` tag on all 31 se-hits (0 mismatches).
- AlphaGenome: SDK 0.7.0, endpoint gdmscience.googleapis.com, `score_variant` on a 100 kb interval, ATAC+DNASE recommended CenterMaskScorers (DIFF_LOG2_SUM, width 501). Restricted to 14 CNS/neural biosamples (brain, cortex, cerebellum, astrocyte, neural progenitor, neuronal stem cell, glutamatergic neuron, motor neuron, neural crest; vascular/endothelial/pericyte excluded).
- Impactful on the AlphaGenome scale = neural max|log2FC| >= p95 (0.556) of 200 class-matched OPC-regulatory background variants from `data/dmg/sweep_result.tsv` (seed 20260709), 0 API errors.

## Headline numbers (both, together)
| Metric | Value | Reading |
|---|---|---|
| Direction (gain/loss) agreement | 31/38 = 82% (p=5.8e-5) | robust; survives; stable across effect size (83% for |log2FC|>=0.4, 81% below) |
| Binary p95-impactful concordance | 14/38 = 36.8% | threshold-hostage, do not headline alone |
| Magnitude correlation (Spearman) | rho=0.23, p=0.16 | weak, not significant |
| NCypher-impactful also >= AG background median | 35/36 | NCypher hits are real signal on AG, just modest |
| NCypher-impactful also >= AG p90 / p95 | 22/36 / 13/36 | most clear background outliers, few clear AG p95 outliers |

**Threshold sensitivity of binary concordance** (why it cannot be the headline): median 92.1%, p75 76.3%, p90 60.5%, p95 36.8%, p99 13.2%.

## Where they agree (corroboration)
- **4 of the 5 strongest NCypher variants** agree on both direction and are AlphaGenome-impactful: SYN3 (NC loss 1.24 / AG loss 3.21, p100), POLR2F (0.70 / 1.05, p99), GDPD5 (0.91 / 0.72, p96), FARP1 (1.16 / 0.67, p96). These are the cleanest corroborations.
- Among the 31 SE-resident hits, 10 are AG-impactful at p95 and 22 clear AG p90; the SE set is modest-effect by construction (median NCypher |log2FC| ~0.25), so most sit above AG background but below its strict p95, which is expected, not a discovery.

## Where they disagree (informative, honestly owned)
1. **NPAS3, NCypher's lead candidate, is the single most damaging disagreement.** NCypher: strong loss (|log2FC| 0.71, phyloP 4.68, GO). AlphaGenome: neural max 0.20 at background p70 (sub-p90), and the opposite sign (gain). AlphaGenome essentially sees little accessibility effect here rather than a confident opposite one, but on its generic neural tracks it does not corroborate the OPC-specific loss that anchors NCypher's shortlist. This is the honest headline caveat, not a footnote: the lead variant is the one AlphaGenome least supports.
2. **TERT is an NCypher false-negative that AlphaGenome catches.** The TERT C228T positive control reads weak on NCypher's live call (|log2FC| 0.10, below the 0.162 cutoff, HOLD) but is clearly AlphaGenome-impactful (neural gain 1.06, p99). The brief expected TERT impactful in both; it is impactful only in AlphaGenome. This is a point against NCypher's chromatin axis on a canonical regulatory variant, and belongs in the verdict, not buried.
3. Six further direction disagreements (LINC01905, PTPRJ, RXRA, ENST00000652518, PKNOX2, SNX1) all have NCypher |log2FC| <= 0.22, i.e. sitting on the 0.162 cutoff where the sign is noisy; these are low-confidence for both models.

## Structural caveats (own these)
- **Construction circularity:** the 31 SE-resident hits are pre-selected to exceed NCypher's own threshold, so "NCypher-impactful variants that fall below AlphaGenome's independent p95" is a structural consequence of comparing a selected set against an unselected threshold, not evidence about either model's accuracy.
- **Modality/context:** AlphaGenome has no OPC track; the closest CNS tracks are embryonic neural progenitor and neuronal stem cell. Disagreement where the OPC/DMG context matters is expected and is exactly why this is a second opinion, not a verdict.
- AlphaGenome measures predicted accessibility change like NCypher's ChromBPNet (same modality), so this is a fair chromatin-axis cross-check; it says nothing about NCypher's constraint (phyloP) or convergence axes.

## Skeptic check (falsification)
- **Strongest argument against the positive read:** "82% direction agreement is a low bar (50% chance baseline) on individually weak, noisy effects, and the favourable metric is being promoted while the unfavourable ones (rho ns, binary threshold-hostage) are buried." **Guard:** both metrics are reported together above; direction agreement is significant vs chance (p=5.8e-5), stable across effect size, and driven by the strong variants agreeing (4/5 top). The binary and correlation weaknesses are stated as first-class results, and the two disagreements against NCypher (NPAS3, TERT) are named in the verdict. The claim is narrowed to "direction corroboration survives", not "AlphaGenome validates NCypher".
- **All-tracks vs neural-only:** re-running with all 472 tracks (background p95 1.06) gives the same 36.8% binary concordance; the neural restriction does not manufacture the result.
- **Reviewer verification:** headline numbers were re-derived from the saved `a5_comparison_table.tsv` alone (not in-memory objects) and reproduce exactly (36.8% binary, 81.6% direction); an independent model reviewer flagged metric-promotion, NPAS3 weight, and construction circularity, all now incorporated.

## Verdict
- Claim "AlphaGenome corroborates NCypher's chromatin direction": **SURVIVES** (82%, p=5.8e-5).
- Claim "AlphaGenome corroborates NCypher's chromatin magnitude / binary impact call": **DOES NOT SURVIVE as a robust number** (threshold-hostage; rho ns).
- Net: a supportive but partial second opinion. It agrees on which way the accessibility moves for most variants and strongly on the biggest-effect heroes, disagrees on the lead candidate (NPAS3) and on TERT (an NCypher miss), and cannot be read as validation. AlphaGenome is a cross-check, not ground truth.
