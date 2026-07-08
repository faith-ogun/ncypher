# NCypher honesty guardrails

Every NCypher claim carries a confidence tier and a guardrail. This file is the
registry of what the tool may and may not say. It exists because an **agent**, not a
human reading a methods section, is calling NCypher, so the honesty has to be encoded as
data the agent can check, not left to the reader's judgement. British English, no em
dashes.

The rule: **confidently wrong is worse than missing data.** If a claim is not on the
"can say" list at the stated tier, do not make it.

---

## The bright-line "Do NOT say" list

Refuse or rephrase any output that does one of these:

1. **Do NOT claim NCypher beats or out-predicts the strong sequence models.** Not
   AlphaGenome, not Enformer, not Malinois, not the Pollard CNN-BiLSTM. NCypher is the
   **convergence / coupling layer** that joins a chromatin score, evolutionary
   constraint and (where available) measured function into one agent-callable call with
   a mechanism and an honesty flag. It is not a better general variant-effect predictor.
   Saying otherwise is false and a domain judge will catch it.

2. **Do NOT claim the chromatin model recovers the 164 MPRA DAVs, or that it beats
   motifbreakR on the DAVs.** It does not (AUPRC 0.018, ~= chance). ChromBPNet predicts
   accessibility; MPRA measures reporter activity; they are different modalities. The
   correct, validated claim is caQTL recovery (progenitor caQTL AUROC 0.689, 7.5x base
   rate, context-specific).

3. **Do NOT call any DMG variant a genome-wide, recurrent, or validated non-coding
   driver.** The converged hits are **private, single-patient** variants; **0** recur at
   a locus among the converged; **0** fall in canonical DMG driver genes. Even the lead
   gene NPAS3 is a **gene-level** recurrence (three different enhancers in three
   patients) whose per-gene binomial p = 0.014 does **not** survive Bonferroni across
   ~6,800 genes. These are hypothesis-generating candidates to validate, not drivers.

4. **Do NOT claim NCypher predicts drug response, or that a nominated node is a validated
   target.** NCypher triages non-coding regulatory variants and connects them, as
   hypotheses, to established therapeutic axes. It does not predict whether a tumour will
   respond to a drug. State this explicitly whenever a therapy axis is named.

5. **Do NOT promote on a single axis, or on an out-of-domain call.** No GO without at
   least two available axes agreeing (>= 2/3) and an in-domain context. Out-of-domain is
   NO-GO by default.

6. **Do NOT overstate a specific TF motif when the model-native signal is a contribution
   collapse without a clean position weight matrix (PWM) match.** Report "N% collapse of
   local DeepSHAP contribution at the variant base" and name a specific TF **only** when
   the PWM disruption is clean (e.g. SYN3 breaks NFIA cleanly; NPAS3's crude PWM top call
   is noisy, so report its contribution collapse without asserting a specific TF).

7. **Do NOT imply in-house DMG or breast biology at Gladstone.** Gladstone has neither a
   DMG lab nor a breast programme. Bridge to their turf via the **regulatory logic** and
   the neurodevelopmental / activity-regulated enhancer biology, not the disease label.

8. **Do NOT report the neurodevelopmental enrichment as a chromatin-model finding.** The
   neural focus of the shortlist is **constraint-axis-driven** (phyloP 2.62x, p = 4.8e-13);
   the chromatin axis alone is **not** neural-enriched after gene-length control (1.13x,
   p = 0.363). Convergence retains the focus at a modest 2.62x, p = 0.029. Attribute each
   number to its axis.

9. **Do NOT quote the convergence-enrichment p = 0.029 as decisive.** It is nominal and
   several gene sets were tested before the strict canonical one; report it as
   suggestive. The bulletproof number is the constraint-axis p = 4.8e-13.

---

## What NCypher CAN say (with the tier it is licensed at)

- **HIGH confidence:** the engine runs end to end on real data; the chromatin axis is
  validated on caQTLs with clean context-specificity; the axes are genuinely orthogonal;
  the DMG cohort shows no recurrent non-coding point driver (a rigorous, biology-consistent
  negative); NCypher is the first systematic somatic non-coding survey of DMG.

- **MEDIUM confidence:** a specific converged variant is a calibrated, mechanism-explained
  candidate worth validating; the convergence shortlist concentrates in the
  neurodevelopmental programme; NPAS3 is an externally validated glioma tumour suppressor
  hit by three distinct high-impact non-coding variants in three patients.

- **LOW / hypothesis only:** any single enhancer-to-gene assignment for an intronic host
  (needs Activity-by-Contact + Hi-C); any therapy nomination (needs the wet-lab chain and
  carries the blood-brain-barrier delivery caveat); the SOX2-OT to SOX2 chain across
  394 kb (plausible, intra-TAD, but Hi-C is the arbiter).

---

## The honest framing (use this shape)

Lead with the **discovery**, show the **engine** as the evidence, and end with **what
this is not**. For any promoted call, the output must state: the confidence tier, the one
thing that would kill it, and the guardrail on any downstream (therapy) claim. Agreement
across axes is expected; the credible, novel output is often the **informative
disagreement** (chromatin says yes, constraint says no, and the mechanism explains why),
so surface disagreements as first-class, not footnotes.
