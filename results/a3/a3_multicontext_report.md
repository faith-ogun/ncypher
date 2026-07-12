---
title: "A3 result: is the converged DMG set OPC-context-specific?"
type: result
status: current
last-reviewed: 2026-07-11
source: "Claude Science + Modal run A3 (2026-07-11). Off-context ChromBPNet scoring on Modal via modal/score_variants.py::score_to_volume (Python 3.11 image, TF-CPU 2.15.1). Contexts: trevino_2021 c15/c10/c11/c9 (Corces/Marderstein deposition syn64713927) + non-neural control domcke_2020.fetal_heart.Cardiomyocytes (syn64715850). c15 baseline reused from data/dmg/sweep_result.tsv and independently re-scored for validation. Constraint (phyloP) and cutoff from the Phase-5 sweep."
tags: [type/result, status/current, topic/dmg, topic/chromatin, topic/context-specificity, topic/honesty, topic/modal, project/ncypher]
---

# A3 result: multi-context cell-type specificity of the 164 converged DMG hits

> [!verdict] Partly specific, and honestly so. SURVIVES as a neural-vs-non-neural claim; WEAKENED as an OPC-exclusive one.
> The 164 converged somatic non-coding hits carry a chromatin effect that is strongly biased to
> the developing-brain contexts and goes quiet in a non-neural (fetal-heart cardiomyocyte) control,
> but it is a developing-brain-progenitor signal shared across OPC and radial-glia/IPC lineages, not
> a c15-private one. This is the variant-level echo of the validated caQTL context-specificity
> ([[validation-result]]), not a new causation claim. Reviewer re-derived every headline number from
> the raw per-context tables.

## What was done
Re-scored the 164 converged variants (`data/dmg/enhancers/a3_input.scorer.tsv`) through four
off-context ChromBPNet models on Modal and joined the matched fetal-OPC (c15) baseline:

- **matched:** c15 (fetal-OPC, `trevino_2021.c15`) - reused from `sweep_result.tsv`, and independently
  re-scored on the same Modal image as a check.
- **other developing-brain progenitors (unselected):** c10 oligo-IPC, c11 early radial glia, c9 late radial glia.
- **non-neural control:** `domcke_2020.fetal_heart.Cardiomyocytes` (syn64715850). Chosen because the
  domcke_2020 study deposited both fetal_brain and fetal_heart contexts through the same pipeline, so it
  is the cleanest same-deposition off-lineage control.

Baseline reuse validated: the Modal re-score of c15 reproduces the stored sweep c15 logfc to a
**max absolute difference of 1.1e-6** (Pearson r > 0.99999999999), so the off-context columns are on
the same footing as the matched column.

## The numbers (n = 164; cutoff |log2FC| >= 0.162, the calibrated p99)

| context | median \|log2FC\| | fires (>= 0.162) |
|---|---|---|
| c15 OPC (matched, **selected on**) | 0.261 | 100% (by construction) |
| c11 early RG | 0.272 | 68.3% |
| c9 late RG | 0.230 | 61.0% |
| c10 oligo-IPC | 0.252 | 67.1% |
| **fetal-heart control** | **0.092** | **34.1%** |

**Primary test (avoids the c15 selection circularity).** c15 fires in 100% *by construction* (the 164
were selected as chromatin-high-impact on c15), so a c15-vs-control contrast would be circular. The
defensible headline is the **unselected** progenitor contexts vs control:

> progenitor_max(c10/c11/c9) - control, median paired diff **+0.208, 95% CI [+0.160, +0.248]**
> (excludes 0), one-sided paired Wilcoxon **p = 4.9e-24**, **90.2%** of variants neural > control.

Secondary/descriptive (selection-inflated, do not use as the specificity test): neural_max (incl c15)
- control median +0.266, 95% CI [+0.228, +0.328], p = 3.7e-26, 92.7% neural > control.

For scale, the caQTL context-specificity gap this operationalises was +0.240 [+0.081, +0.394]
(AUROC units, a different metric); the variant-level |log2FC| gap here is of comparable magnitude and
the same sign.

## Specificity classification
Note: c15 fires in 100% of the 164 by construction (they were selected as chromatin-high-impact on
c15), so c15 firing is never the deciding factor. The rule as actually implemented turns on the
control and the unselected progenitor contexts:
- **broad 56 (34.1%)** - fires in the non-neural control (context-independent; flagged, not deleted).
- **OPC-specific 80 (48.8%)** - below cutoff in the control AND fires in >= 1 unselected progenitor context (c10/c11/c9).
- **weak 28 (17.1%)** - below cutoff in the control AND fires in none of the unselected progenitor contexts (c10/c11/c9).

## The leads
- **NPAS3** (chr14-33788719-A-G, phyloP 4.68): **OPC-specific**. c15 0.71, fires weakly in two
  progenitor contexts (c10 0.16, c11 0.17), silent in control (**0.013**). The flagship lead behaves
  exactly as the "right context" story predicts.
- **SYN3** (chr22-33000876-C-T, phyloP 8.58): **broad**. Fires huge everywhere including the heart
  control (**0.657**). Its magnitude is ~2-3x larger in neural contexts, but it clears the cutoff
  off-lineage, so it is **not** context-specific and must not be presented as such. Honest catch on a
  top loss.

## Honest limitations (do not overclaim)
1. **"OPC-specific" means neural-not-cardiomyocyte, not OPC-not-other-progenitor.** 68% of the
   OPC-specific hits also fire in >= 1 other progenitor context; the label does not exclude
   radial-glia/IPC sharing. A truly OPC-private tier would need an OPC-vs-other-progenitor contrast,
   which A3 did not run. The signal is developing-brain-progenitor, shared across neural lineages.
2. **One non-neural control tests non-neural specificity, not general accessibility.** A cardiomyocyte
   control is a real off-lineage ChromBPNet, not a scrambled null; some cross-context signal is
   expected because accessibility is partly shared. The test was matched > control, not control at zero.
3. Enrichment / context-firing is not driver selection. These remain private, single-patient
   hypotheses to validate, not proven drivers.

## Verdict (one line)
**Partly specific.** The converged set is a developing-brain-progenitor chromatin signal that is
significantly stronger than a non-neural control (survives), but it is shared across neural progenitor
lineages rather than OPC-exclusive (weakened as an OPC-private claim). NPAS3 is a clean OPC-specific
lead; SYN3 is broad.

> [!skeptic]
> Strongest argument against: the neural-vs-control gap could be a mappability/GC shortcut that happens
> to score lower in one heart model, not developing-brain regulatory biology. Guard: it holds on the
> UNSELECTED progenitor contexts (the variants were not chosen on those), across three independent
> developing-brain models with a tight bootstrap CI excluding 0 and 90% of variants individually
> neural > control; and the control is a real, same-deposition ChromBPNet trained by the same pipeline,
> so a pure artefact would fire there too (34% do - flagged broad). It does not survive as an
> OPC-EXCLUSIVE claim and is not reported as one.

## Provenance
- Off-context scores (raw): `a3_opc/c10/c11/c9/control.variant_scores.tsv` (saved as artifacts).
- Assembled matrix: `a3_context_matrix.tsv` (164 x 5, logfc + |logfc| + label).
- Headline numbers: `a3_headline_numbers.json`. Figure: `a3_context_heatmap.png`.
- Control context: `domcke_2020.fetal_heart.Cardiomyocytes` = syn64715850, registered in
  `modal/score_variants.py` CONTEXTS as `heart_control`.
- Reviewer independently re-derived all headline numbers from the raw per-context tables
  (join 164/164, every number reproduced to 2 s.f.; c15 validation 1.1e-6).

## Related
- [[validation-result|the caQTL context-specificity this operationalises]] · [[k27m-se-finding|the flagship + NPAS3/SYN3 leads]] · [[a7-decomposition-result|A7 axis decomposition]] · [[a3-claude-science-brief|the A3 brief]]
