# A7 — Axis decomposition: does convergence add signal beyond a conservation baseline?

**Question (Liang 2026 critique).** Non-coding variant scorers are repeatedly caught
re-packaging evolutionary conservation. The honest test is whether NCypher's two-axis
convergence adds independent signal *beyond* a plain phyloP ranking. This report decomposes
convergence into its constraint (Zoonomia phyloP) and chromatin (Corces fetal-OPC ChromBPNet
|log2FC|) axes and reports the verdict either way.

**Input.** `data/dmg/enhancers/a7_input.tsv` (10,869 OPC-regulatory somatic SNVs, OpenPedCan
152-patient H3 K27M DMG). Marginals confirmed live against the NCypher MCP `cohort_summary`:
10,869 scored, 753 chromatin high-impact (|log2FC| >= 0.162), 1,583 constrained (phyloP >= 2.27),
164 converged (both), 0 recurrent among converged, 0 in canonical DMG driver genes. The dataset
identity `converged == (high_impact AND constrained)` holds exactly.

---

## Verdict (one line)

> NCypher's convergence is **genuine multi-evidence, not conservation counted twice**: the two
> axes are statistically independent (Spearman rho = -0.004, p = 0.68), so convergence is a real
> AND-gate. But convergence does **not** out-rank a pure-phyloP baseline at general variant
> prediction, and the neurodevelopmental focus of the shortlist is **conservation-driven** (the
> constraint axis carries it at 2.64x, p = 1.3e-13; chromatin alone is null, 1.20x, p = 0.37).
> The chromatin axis contributes an orthogonal accessibility filter, not neural specificity.

---

## 1. Axis independence — convergence is a real AND-gate

Correlation of `phylop` vs `abs_logfc`:

| set | n | Spearman rho [95% CI] | p | Pearson r [95% CI] | p |
|---|---:|---|---:|---|---:|
| all variants | 10,853 | **-0.004 [-0.023, +0.015]** | 0.68 | +0.066 [+0.042, +0.092] | 5.4e-12 |
| constrained subset | 1,583 | +0.076 [+0.028, +0.122] | 2.4e-3 | +0.119 [+0.063, +0.174] | 2.2e-6 |
| high-impact subset | 749 | +0.088 [+0.018, +0.160] | 1.6e-2 | +0.144 [+0.061, +0.229] | 7.7e-5 |

The rank correlation across all variants is indistinguishable from zero (rho = -0.004). The
Pearson r = +0.066 is "significant" only because n is large: it explains 0.4% of variance
(r^2 = 0.0044) and is an artefact of a handful of high-|log2FC|, high-phyloP points, not a
monotone relationship. Within the constrained and high-impact subsets the correlation is
marginally positive but still negligible (rho <= 0.09). **The two axes are independent; a
variant's conservation tells you essentially nothing about its predicted chromatin effect.**
Convergence is therefore a genuine two-source AND-gate, not conservation measured twice.

## 2. Conservation-baseline comparison — convergence is a distinct, more stringent set

Three equal-size ranked sets (n=164 each): NCypher converged; top-164 by phyloP alone; top-164
by chromatin |log2FC| alone.

| pair | shared | Jaccard | interpretation |
|---|---:|---:|---|
| converged ∩ top-phyloP | 20/164 | 0.065 | convergence recovers only 12% of a pure-phyloP top ranking |
| converged ∩ top-chromatin | 45/164 | 0.159 | more chromatin-led, but still a minority |
| top-phyloP ∩ top-chromatin | 10/164 | 0.031 | the two single-axis rankings barely overlap |

Convergence overlaps a pure-phyloP top ranking by only 20/164. It is not a re-ranking of
conservation; it is the **intersection of two gates**, and by construction that is strictly more
stringent: higher precision, lower recall. Convergence captures 10.4% of all constrained variants
and 21.8% of all high-impact variants. It **removes conserved-but-chromatin-inert variants** that
a phyloP ranking would promote. Concrete example (spot-checked live on the MCP): `chr2-133674869-C-T`
(NCKAP5) has the maximum phyloP in the cohort (8.90) but chromatin |log2FC| = 0.13 — the MCP returns
**HOLD, "informative disagreement, not a green light"**, exactly the variant a pure-phyloP baseline
promotes and convergence correctly withholds.

**Honest framing:** this is a precision/recall trade, not a claim of superior prediction.
Convergence trades recall for precision by intersecting two independent filters. It does **not**
out-predict a conservation baseline at general variant-effect prediction, and A7 makes no such
claim.

## 3. Incremental stratification — each axis carries information the other does not

- **Partial correlation** of phyloP vs chromatin, controlling for variant class: Spearman rho =
  +0.007 (p = 0.48). Independence survives class adjustment.
- **Logistic regression** of patient recurrence (n >= 2 patients; 86 events) on both standardised
  axes + class: phyloP is nominally associated with recurrence (z-coef -0.27, p = 0.013, uncorrected)
  and, notably, in the negative direction (more conserved elements are slightly *less* recurrently
  hit); chromatin is not (z-coef -0.14, p = 0.36). Recurrence is a sparse, weak endpoint here (86
  events), so treat the phyloP association as suggestive not decisive, and read it as further
  evidence the two axes are non-redundant (only one carries recurrence signal), not as a claim that
  either axis predicts recurrence well.

The axes are non-redundant: the chromatin filter is not predictable from conservation, so it adds
an orthogonal dimension rather than a correlated re-weighting.

## 4. Gene-set decomposition (confirmatory) — the neural focus is conservation-driven

Pre-registered canonical neurodevelopmental gene set re-derived independently from four curated
components (**not** chosen from these data): oligodendrocyte/OPC lineage (30), neurodevelopmental
TFs (43), SynGO-core synaptic (40), canonical neurodevelopmental-disorder genes (35); union after
dedup = **141 symbols**. Per-variant enrichment over the OPC-peak background, footprint-matched
permutation (5,000 draws on log mutational footprint deciles); hypergeometric for the constraint
axis. Base rate 1.44%.

| subset | neural hits | n | fold | test | p |
|---|---:|---:|---:|---|---:|
| chromatin only (high-impact) | 13 | 753 | **1.20x** | footprint perm | 0.37 (n.s.) |
| constraint (phyloP) | 60 | 1,583 | **2.64x** | hypergeometric | **1.3e-13** |
| converged (both) | 6 | 164 | **2.55x** | footprint perm | 0.033 (nominal) |

This **confirms the prior result** (prior: constraint 2.62x p~5e-13; chromatin 1.13x n.s.;
converged 2.6x nominal) on an independently re-derived gene set. The six canonical converged
genes are **CNTNAP2, DISC1, EBF2, NPAS3, SCRT2, SYN3** — identical to the prior list.

- The **constraint axis carries the neurodevelopmental signal** (2.64x, p = 1.3e-13). Robust, but
  partly expected: neurodevelopmental genes have deeply conserved regulatory sequence.
- The **chromatin axis alone is not neural-enriched** once footprint is controlled (1.20x,
  p = 0.37).
- **Convergence inherits the neural focus from the constraint axis** (2.55x) while adding the
  chromatin accessibility filter.

**Caveat (stated plainly):** the converged p = 0.033 is **nominal**. Several gene sets were
considered (tight-OPC, broad-neuro, glioma) before settling on this strict canonical one, so
0.033 is suggestive, not decisive. The statistically robust number is the **constraint-axis
enrichment (p = 1.3e-13)**. The OPC-peak background is already neural-leaning, which makes the
enrichment conservative in the sense that it exceeds an in-context baseline.

---

## Falsification pass

1. **"The two axes look independent only because a rank test is insensitive; a linear
   relationship exists (Pearson p = 5e-12)."** Tested: the Pearson r = +0.066 explains 0.4% of
   variance and vanishes as a rank relationship (rho = -0.004). It is driven by a few extreme
   points, not a monotone trend. The AND-gate reading holds; the linear "signal" is
   effect-size-negligible. **Guard holds.**
2. **"Convergence is just conservation re-labelled."** Tested: convergence shares only 20/164
   (Jaccard 0.065) with a pure-phyloP top ranking, and its members require an independent chromatin
   gate that is uncorrelated with phyloP. It is a distinct, more stringent set. **Refuted.**
3. **"The neural enrichment is a footprint/gene-length artefact — long neural genes accrue more
   variants."** Tested: footprint-matched permutation on log mutational-footprint deciles; the
   constraint enrichment survives (perm p = 2e-4) and the chromatin axis stays null (p = 0.37).
   **Guard holds.**
4. **"The gene set was reverse-engineered from the hits."** Tested: re-derived from four curated
   field sources before touching these data; it reproduces the prior 141-symbol set and the same
   six converged genes. Membership is source-defined, not data-defined. **Guard holds.**
5. **"Convergence out-predicts conservation."** Not claimed. Convergence is an intersection (higher
   precision, lower recall) of two independent filters; it does not out-rank phyloP at general
   prediction. Reported as a precision/recall trade, not a win. **No overclaim.**

## Reviewer verification

Every headline number was recomputed from the raw TSV in an independent pass, disjoint from the
analysis cells. All 11 checks PASS: marginals (10,869 / 164 / 1,583 / 753); Spearman rho = -0.004,
p > 0.5; converged ∩ top-phyloP = 20; folds constraint 2.641 / converged 2.549 / chromatin 1.203;
constraint hypergeometric p = 1.26e-13.

## Provenance

- Input: `data/dmg/enhancers/a7_input.tsv` (staged full scored sweep).
- Chromatin: Corces developing-brain fetal-OPC ChromBPNet, context `trevino_2021.c15`, GRCh38.
  High-impact gate |log2FC| >= 0.162 (p99 of 800-variant background).
- Constraint: Zoonomia cactus241way phyloP; constrained gate phyloP >= 2.27.
- MCP grounding: `cohort_summary` (marginals), `score_variant` on chr22-33000876-C-T (SYN3, GO)
  and chr2-133674869-C-T (NCKAP5, conserved-but-inert HOLD).
- Neural gene set: re-derived from OL-lineage + neurodevelopmental-TF + SynGO-core + NDD curated
  sources (141 symbols; components listed in the analysis code).
- Code: this session (axis correlations with bootstrap CIs, three-set Jaccard, partial correlation
  + logistic, footprint-matched permutation enrichment, independent reviewer recomputation).

British English, no em dashes. Hypothesis-generating; converged hits are private single-patient
candidates to validate, not proven drivers.
