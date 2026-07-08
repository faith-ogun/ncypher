# NCypher calibrated thresholds and axis definitions

This is the inspectable registry of the numbers the triage procedure uses. Every
threshold here has a provenance line, so a reviewer can audit the decision boundary
rather than trust a prose summary. Single source of truth: these values match
`mcp/server.py`, `src/nc_score/converge.py`, and `src/nc_score/constraint.py`.
British English, no em dashes.

Genome build: GRCh38 throughout. Model context: `trevino_2021.c15` (developing-brain
fetal-OPC ChromBPNet).

---

## The three axes (orthogonal by construction)

NCypher combines three independent lines of evidence. They are orthogonal on purpose:
each measures a different molecular facet, so agreement across them is stringent and
disagreement is informative. No single axis is a universal functional-variant detector,
which is exactly why the tool surfaces all three plus the disagreements rather than
manufacturing one confident number.

### Axis 2 - chromatin accessibility (ChromBPNet)

- **What it measures:** the predicted change in OPC chromatin accessibility when the
  alt allele replaces the ref allele, in the developing-brain fetal-OPC context.
- **Model:** ChromBPNet trained on the Trevino 2021 developing-brain multiome, cluster
  c15 (fetal OPC / progenitor). Pretrained, in-domain, no training by us.
- **Metrics:**
  - `log2FC` - log2 fold-change of predicted total accessibility. Signed:
    **positive = accessibility gain (opening); negative = loss (closing)**.
  - `jsd` - Jensen-Shannon distance between the base-resolution ref and alt profiles;
    a profile-shape change, i.e. footprint / motif disruption.
- **High-impact call:** `|log2FC| >= 0.162` OR `jsd >= 0.05`.
  - `0.162` is the **p99 of an 800-variant cohort background**, not an arbitrary
    absolute 0.5. It is the calibrated dynamic range of this model on this cohort.
    Source: `docs/audit/sweep-result.md`.
- **Validation (the honest, correct one):** on the native ground truth for a chromatin
  model (allelic chromatin-accessibility QTLs, caQTLs), the predicted |log2FC| recovers
  **progenitor caQTLs at AUROC 0.689, 7.5x the base rate (MWU p = 6e-6)** in the matched
  fetal-OPC context, and is **null for a mismatched context** (PsychENCODE caQTL AUROC
  0.449, n.s.). This is the quantitative proof of the "right cell context" claim.
  Source: `docs/audit/validation-result.md`.

### Axis 3 - evolutionary constraint (Zoonomia phyloP)

- **What it measures:** per-base purifying selection across 241 placental mammals. A
  label the model never trained on, so it is an orthogonal evolutionary check.
- **Track:** Zoonomia `cactus241way` phyloP (Christmas, Sullivan et al., Science 2023).
- **Constrained call:** `phyloP >= 2.27` (5% FDR; flags ~3.26% of the genome).
- **Direction:** positive = slower-than-neutral (conserved); negative = accelerated
  (e.g. human accelerated regions).

### Axis 1 - measured function (lentiMPRA)

- **What it measures:** the measured allelic effect on episomal reporter activity in the
  developing-cortex lentiMPRA (Deng, Whalen ... Pollard, Science 2024, adh0559).
- **Impactful call:** the variant is a differential-activity variant (DAV, 10% FDR) OR
  `|measured log2FC| >= 0.5`.
- **Availability (be honest):** this axis is **NOT available for the somatic DMG
  variants** (they are not in the MPRA library). When it is absent, convergence runs on
  the two available axes and the memo says so.
- **Critical honesty note:** the chromatin model does **not** recover the 164 MPRA DAVs
  (AUPRC 0.018, ~= chance), because ChromBPNet predicts **accessibility** and MPRA
  measures **reporter activity** - different molecular modalities. This is expected, not
  a bug. Never claim MPRA recovery or "beat motifbreakR on the DAVs". Source:
  `docs/audit/validation-result.md`.

---

## The convergence logic (from `src/nc_score/converge.py`)

Let `n_available` = number of axes with data, `n_impactful` = number of those that are
impactful, `agreement = n_impactful / n_available`.

- **In domain:** the model context is one of the developing-brain contexts
  `{trevino_2021.c15, c10, c11, c9}`. Outside this set the call is out-of-domain and is
  a NO-GO by default (the score is not trustworthy there).
- **Promote (GO):** `in_domain` AND chromatin is high-impact AND `n_available >= 2` AND
  `agreement >= 0.66`. In words: the chromatin axis must fire, at least two axes must be
  available, and at least two-thirds of the available axes must agree.
- **HOLD:** in domain, but the axes do not yet converge (an informative disagreement,
  not a green light). Resolve the disagreeing axis before committing bench time.
- **NO-GO:** out of domain, or chromatin not impactful.

NCypher never promotes on a single axis.

---

## Confidence tiers (calibrated, and honestly capped)

| Tier | Condition | Meaning |
|---|---|---|
| **HIGH** | in domain, `n_available >= 2`, `agreement >= 0.66`, **and** active-allele accessibility quantile `>= 0.5` | Strong, multi-axis, in a genuinely accessible element |
| **MEDIUM** | in domain, `agreement >= 0.5` | Converges on the available axes, but the third axis is missing or the element accessibility percentile is modest |
| **LOW** | in domain, `agreement < 0.5` | Weak or conflicting |
| **OUT-OF-DOMAIN** | context not in the developing-brain set | Do not prioritise on this call; re-score in a matched model |

**Honest consequence for the DMG cohort:** the two-axis converged hits are reported as
**MEDIUM**, not HIGH, because (a) the measured-function axis is absent for somatic
variants and (b) the accessibility percentile of most hits is below 0.5. Reaching HIGH
requires the third axis (MPRA/CRISPRi) or a top-percentile accessible element. Do not
inflate a two-axis MEDIUM to HIGH.

---

## The cohort the sweep was run on

- **10,869** somatic non-coding SNVs that fall in OPC-accessible c15 regulatory elements
  (functional-first: cohort variants intersected with the 115,662 c15 OPC peaks), from
  **152 H3 K27M DMG patients** (OpenPedCan, GRCh38).
- **753** chromatin high-impact, **1,583** constrained, **164 converged** (both axes).
- Of the converged: 131 accessibility loss, 33 gain; median phyloP 4.60, median
  |log2FC| 0.26; classes Intron 113, IGR 26, 5'UTR 10, RNA 9, 3'UTR 6.
- **0 recurrent** among converged (each private, one patient); **0** in the canonical DMG
  driver-gene list. This is consistent with DMG's non-coding biology being
  enhancer-landscape reprogramming, not a recurrent point hotspot.
- The "164" is a coincidence of the thresholds, unrelated to the 164 MPRA DAVs.

Source: `docs/audit/sweep-result.md`, `data/dmg/sweep_result.tsv`.
