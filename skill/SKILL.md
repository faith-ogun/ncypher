---
name: ncypher-triage
description: >-
  Run NCypher's non-coding regulatory-variant triage procedure for paediatric diffuse
  midline glioma (DMG) in the developing-brain / fetal-OPC context. Use when asked to
  triage, score, prioritise, explain, or decide GO / HOLD / NO-GO on a somatic non-coding
  variant (chr-pos-ref-alt) or a cohort of them, or to produce a "which variants to
  validate first" shortlist or a go/no-go memo. Orchestrates the NCypher MCP tools
  (score_variant, top_candidates, cohort_summary) across three orthogonal axes (chromatin
  accessibility via ChromBPNet fetal-OPC, evolutionary constraint via Zoonomia phyloP, and
  measured function via lentiMPRA where available), applies a structurally-independent
  falsification (skeptic) check that tries to refute the call, reports the disrupted motif
  and which axis drives the verdict, and returns a memo with a calibrated confidence tier
  and an explicit honesty guardrail on every claim.
---

# NCypher triage: which non-coding variant to validate next, and why

NCypher is a **triage tool**, not a predictor. It tells a researcher which non-coding
variant to test next and why, by coupling three orthogonal evidence axes into one call
and being honest when a call is out of domain. This skill encodes NCypher's decision
**procedure** so you can run it end to end on a single variant or a whole cohort, in
Claude Code or Claude Science, and return a defensible go/no-go memo.

The novelty is the **convergence engine**, not the score. Anyone can run a pretrained
model and get a number; NCypher promotes a variant only when the axes agree, surfaces the
informative disagreements, shows the mechanism, and refuses to over-claim. Follow the
seven steps below in order. Do not skip the skeptic step.

Read `references/thresholds.md` for the calibrated numbers and axis definitions,
`references/guardrails.md` for the "Do NOT say" registry, and `references/therapy-map.md`
for the DMG therapy routing. Load them when a step tells you to.

## When to use this skill

Use it when the user asks to triage / score / prioritise a non-coding variant or cohort
in a DMG or developing-brain context, wants the "validate first" shortlist, or wants the
mechanism behind a regulatory variant with an honest confidence.

Do not use it for coding variants, for a disease context outside developing brain (score
it, but the honest output is an out-of-domain NO-GO), or as a general variant-effect
predictor that competes with AlphaGenome or Enformer (it is not; see guardrail 1).

## What NCypher is, and is not (state this in the output)

- **Is:** the coupling layer that joins a chromatin-accessibility score, evolutionary
  constraint, and (where available) measured reporter function, in the correct fetal-OPC
  context, callable by an agent, returning a mechanism and an honesty flag.
- **Is not:** a bigger or better general predictor; a recurrent-driver caller; a drug-response
  predictor. The DMG converged hits are private, single-patient, hypothesis-generating
  candidates, not validated drivers.

## The tools this skill orchestrates (NCypher MCP server)

If the NCypher MCP server is connected, call these. If it is not, the same numbers are in
`data/dmg/sweep_result.tsv` and the reference files, and `example_run.md` shows worked
output you can reason over without a live server.

| Tool | Call | Returns |
|---|---|---|
| `score_variant` | `score_variant(variant_id="chr14-33788719-A-G")` | Full triage for one variant: the three axes, the convergence verdict, and a go/no-go memo (verdict, decisive experiment, kill criterion), plus provenance. A cache hit gives the complete two-axis call; a miss does a live phyloP lookup and flags the chromatin axis as still needing scoring on the c15 model. |
| `top_candidates` | `top_candidates(n=20, converged_only=True)` | The ranked "which to validate first" shortlist, as a table plus structured rows. |
| `cohort_summary` | `cohort_summary()` | The honest headline numbers from the sweep and the caveat, computed live from the cache. |

For a cohort, start with `cohort_summary` for the landscape, then `top_candidates` for the
shortlist, then `score_variant` on each candidate for the memo.

---

## The triage procedure (run in order)

### 1. Intake

Accept either a single variant as `chr-pos-ref-alt` on GRCh38 (e.g. `chr14-33788719-A-G`),
or a cohort (a list of such ids, or a request to use the cached DMG sweep). Normalise to
that form. If the build is unstated, assume GRCh38 and say so. If given an rsID or a gene
name only, ask for coordinates or resolve them explicitly and state how.

### 2. Score (call the MCP)

Call `score_variant` for each variant. Pull the three axes from the result:

- **chromatin** - `log2FC` (signed; + = accessibility gain, - = loss), `jsd`, and the
  high-impact flag;
- **constraint** - `phyloP` and the constrained flag (threshold 2.27);
- **function** - present only if the variant is in the MPRA/DAV set; otherwise marked not
  available (expected for somatic DMG variants).

If the variant is not in the cache, the chromatin axis comes back **unscored**: report
that honestly and do not issue a verdict until it is scored on the c15 model. Never invent
a chromatin number.

### 3. Converge

Apply the convergence logic (full definition in `references/thresholds.md`):

- **GO (promote)** when the context is in domain, the chromatin axis is high-impact, at
  least two axes are available, and agreement is `>= 2/3`.
- **HOLD** when in domain but the axes do not converge. This is an **informative
  disagreement**, not a green light: name which axis dissents and why. Surface
  disagreements as first-class output, not a footnote.
- **NO-GO** when out of domain (score not trustworthy) or the chromatin axis is not
  impactful.

Record `n_axes_available`, `n_axes_impactful`, and `agreement`. NCypher never promotes on
a single axis.

### 4. Mechanism

Report **what breaks and which axis drives the call**:

- From the DeepSHAP / contribution track (in `data/figures/mining/hero_candidates.tsv` for
  the top hits), state the **percent collapse of local model contribution at the variant
  base**, and name the disrupted TF motif **only when the PWM disruption is clean** (e.g.
  SYN3 cleanly breaks NFIA). When the motif call is noisy, report the contribution collapse
  without asserting a specific TF (guardrail 6).
- Say which axis is doing the work. For the DMG shortlist the neurodevelopmental focus is
  **constraint-driven** (phyloP 2.62x, p = 4.8e-13), not chromatin-driven (chromatin alone
  1.13x, p = 0.363 after length control). Attribute each number to its axis (guardrail 8).

### 5. Skeptic step (structurally-independent falsification) - DO NOT SKIP

This is the part that makes NCypher honest rather than confident. Before promoting, run a
**separate falsification pass that tries to refute the call**, ideally in a fresh context
or by a reviewer subagent so the reviewer is not the same reasoning that produced the GO
(the LUMEN pattern: the reviewer is not the model checking itself). Explicitly test each
of these, and state what you find:

1. **Brain-expression / GC / length confounder.** These are intronic variants in a
   brain-tumour cohort scored in a brain chromatin model, so they are biased toward
   brain-expressed genes. Is the signal just that bias? Check: the chromatin axis alone is
   **not** neurodevelopmentally enriched after gene-length control (p = 0.363), so a
   chromatin-only call earns no neural credit. Does the call survive against a
   length-matched, brain-expression-matched background?
2. **Is the effect within noise?** Is `|log2FC|` genuinely above the calibrated p99
   (0.162), or is it hugging the threshold? How close to the boundary is `phyloP` vs 2.27?
   A hit that clears both by a wide margin (e.g. SYN3, |log2FC| 1.24, phyloP 8.58) is
   robust; a marginal one is not.
3. **Is constraint doing all the work?** (Liang 2026 critique.) phyloP-constrained bases
   sit near conserved neurodevelopmental genes anyway. Does the chromatin axis add signal
   beyond conservation, or is this a conservation-only call dressed up as convergence?
4. **Is the enhancer-to-gene link weak?** The host gene of an intron is often not the
   regulated gene. Without Activity-by-Contact + Hi-C, the target assignment is a
   hypothesis. Flag the SOX2-OT to SOX2 chain (394 kb) as needing Hi-C.
5. **Is this a mapping / recurrence artefact?** Naive recurrence in this cohort returns
   mapping artefacts (the audit caught DHPS, ABCA1, PDE4DIP). If the claim leans on
   recurrence, is it gene-level and externally supported, or a single suspicious element?

**State what would kill the call**, then only promote if it survives. If it does not
survive, downgrade GO to HOLD and say which check failed.

### 6. Go/no-go memo

Assemble the memo (this mirrors the shape the MCP already returns, extended with the
therapy angle). Four parts:

- **Verdict:** GO / HOLD / NO-GO, one line, with the converging evidence in parentheses.
- **Validate first / the decisive experiment:** the specific wet-lab test. For a promoted
  DMG variant this is: **base-edit the exact variant base in an OPC-like DMG line**
  (SU-DIPG-XIII or HSJD-DIPG-007), in parallel with CRISPRi of the element, and read
  chromatin accessibility, the target gene, and the OPC-stemness / phenotype.
- **Kill criterion:** the explicit result that ends the chain. For example: if base-editing
  the single base does not move the target gene beyond noise AND CRISPRi of the element
  does not either, the score was a shortcut and the chain is dead; report it.
- **Therapeutic angle (with the guardrail):** route the target gene to a real DMG axis via
  `references/therapy-map.md` (OPC/SOX2 to BET/CDK7/HDAC; synaptic to the Monje AMPA-R /
  gap-junction / ADAM10 / TrkB axis; tumour-suppressor-lost to EZH2/EZHIP or biomarker
  only). Always close with: **NCypher does not predict drug response**, this is a
  mechanism-anchored hypothesis to validate, and CNS delivery (BBB) is the binding
  constraint.

### 7. Honesty (attach to every claim)

Give each claim a **confidence tier** (HIGH / MEDIUM / LOW / OUT-OF-DOMAIN, defined in
`references/thresholds.md`) and check it against `references/guardrails.md` before saying
it. In particular: a two-axis converged DMG hit is **MEDIUM**, not HIGH (the function axis
is absent and the accessibility percentile is modest); reaching HIGH needs the third axis
or a top-percentile element. Do not inflate the tier. End with a short "what this is not"
line drawn from the guardrails.

---

## Cohort mode (the scale fan-out)

For a cohort, do not triage one variant and rhetorically ask "why stop at one patient".
Actually fan out:

1. `cohort_summary` for the landscape (how many scored, high-impact, constrained,
   converged, and the honest caveat: 0 recurrent, 0 in canonical drivers).
2. `top_candidates(n, converged_only=True)` for the ranked shortlist.
3. `score_variant` on the top candidates in parallel; collect the memos.
4. Report the **programme-level** convergence, not a fake recurrent locus: the shortlist
   concentrates in the neurodevelopmental / OPC-stem programme (constraint-driven), led by
   NPAS3. Attribute the enrichment to the constraint axis and quote the strong number
   (p = 4.8e-13) as the robust one and the convergence number (p = 0.029) as suggestive.

## Output template

```
NCypher triage - <variant or cohort>

Verdict: <GO | HOLD | NO-GO>   (confidence: <tier>)
Axes:    chromatin log2FC <x> (<gain/loss>, high-impact <y/n>) | phyloP <p> (constrained <y/n>) | function <available? / n.a.>
Converge: <n_impactful>/<n_available> agree; in-domain <y/n>
Mechanism: <N% contribution collapse at the variant base; motif <TF or "no clean PWM">>; driven by the <constraint/chromatin> axis
Skeptic:  <which falsification checks it survived; what would kill it>
Memo:
  - Validate first: <decisive base-edit + CRISPRi experiment in an OPC-like DMG line>
  - Kill criterion: <the explicit negative result>
  - Therapy angle: <axis via therapy-map> (NCypher does not predict drug response; BBB caveat)
What this is not: <one line from guardrails>
```

## Provenance to cite

Model context `trevino_2021.c15` (developing-brain fetal-OPC ChromBPNet), GRCh38.
Constraint: Zoonomia `cactus241way` phyloP (constrained at phyloP >= 2.27). Chromatin
high-impact calibrated at |log2FC| >= 0.162 (p99 of an 800-variant cohort background).
Cohort: OpenPedCan H3 K27M DMG, 152 patients. Full write-ups: `docs/audit/sweep-result.md`,
`docs/audit/validation-result.md`, `docs/plan/the-finding.md`,
`docs/plan/data-mining-findings.md`.
