# NCypher triage: two worked examples on the real cached data

Both examples below are run on the **real** DMG discovery sweep
(`data/dmg/sweep_result.tsv`) and the mining tables (`data/figures/mining/`), so they are
demonstrable without live Modal or a GPU. The axis numbers and the memo text are the
actual output of `score_variant` (verified against `mcp/server.py`); the skeptic,
therapy, and honesty layers are what this skill adds on top. British English, no em dashes.

To reproduce the raw tool output:

```bash
cd /Users/faith/Desktop/NCypher
.venv/bin/python - <<'PY'
import sys; sys.path.insert(0, "mcp"); import server
# FastMCP wraps the tool in some versions; .fn is the callable, else the function itself.
fn = getattr(server.score_variant, "fn", server.score_variant)
r = fn(variant_id="chr14-33788719-A-G")
print(r.structured_content["memo"]["verdict"])
PY
```

---

## Example 1 - NPAS3 (the lead "validate first" candidate)

**Variant:** `chr14-33788719-A-G`  ·  gene *NPAS3* (intron)  ·  DMG patient PT_DS0HZCSD

### 1. Intake
Single somatic non-coding SNV, GRCh38, `chr14-33788719-A-G`. In the cached DMG sweep, so
the full two-axis call is available.

### 2. Score (from `score_variant`)
- **chromatin:** log2FC **-0.710** (accessibility **loss**), JSD 0.116, high-impact **yes**
  (|log2FC| 0.710 is far above the calibrated p99 of 0.162).
- **constraint:** phyloP **4.68**, constrained **yes** (threshold 2.27).
- **function:** not available (not in the MPRA/DAV set).

### 3. Converge
2 axes available, 2 impactful, agreement **1.0**, in domain (`trevino_2021.c15`).
Verdict from the engine: **GO (promote = true)**.

Real memo text returned by the tool:
> GO: validate chr14-33788719-A-G first. Evidence converges (log2FC=-0.71, JSD=0.116
> (loss)  phyloP=4.68 (constrained @ 2.27)); predicted chromatin loss.

### 4. Mechanism
Model-native DeepSHAP shows an **80% collapse of local contribution** at the variant base
(`hero_candidates.tsv`: `deepshap_collapse = 0.802`). The accessibility **loss** is
consistent with silencing of a tumour-suppressor enhancer. The crude PWM top-motif call
for this base is noisy (CTCF-like, low information), so **do not assert a specific TF here**
(guardrail 6): report the contribution collapse, not a clean motif. Driver of the call:
both axes fire, and NPAS3 sits in the **constraint-driven** neurodevelopmental programme.

### 5. Skeptic step (tried to refute it)
- **Brain-expression / length confounder?** NPAS3 is one of the 6 canonical neural genes
  in the converged set, and it earns that credit through the **constraint** axis, not
  chromatin alone (chromatin-only neural enrichment is n.s., p = 0.363). The converged
  neural enrichment (2.62x, p = 0.029) is suggestive, not decisive, and is reported as such.
- **Within noise?** No. |log2FC| 0.710 clears the p99 (0.162) by ~4.4x; phyloP 4.68 clears
  2.27 comfortably. Robust on magnitude.
- **Constraint doing all the work?** No: the chromatin axis adds a real loss-of-accessibility
  signal plus the 80% contribution collapse; this is not a conservation-only call.
- **Enhancer-to-gene link weak?** NPAS3 is a ~0.84 Mb locus; the host gene is the likely
  target but Activity-by-Contact + Hi-C is needed to confirm this element regulates NPAS3
  rather than a neighbour. Link confidence: **Medium**.
- **Mapping / recurrence artefact?** The NPAS3 signal is **gene-level** recurrence (3
  distinct high-impact variants, 3 different enhancers, 3 patients: `chr14-33788719-A-G`
  converged, plus `chr14-33057410-A-G` and `chr14-33282787-C-A` high-impact), and it is
  **externally validated**: NPAS3 is a tumour suppressor in glioma (Moreira et al., Am J
  Pathol 2011, PMID 21703424) and a paediatric-medulloblastoma tumour-suppressor master
  regulator (Michaelsen et al., Sci Rep 2025). **But** the per-gene binomial p = 0.014
  does not survive Bonferroni across ~6,800 genes, and only 1 of the 3 is fully converged.
  So: elevate as a biologically-motivated lead, **not** a genome-wide driver.

**What would kill it:** base-edit `chr14-33788719` in an OPC-like DMG line; if NPAS3
expression and local accessibility do not move beyond noise, and CRISPRi of the element
does not lower NPAS3 either, the call is dead.

**Survives** as the strongest single lead to validate first, at **MEDIUM** confidence.

### 6. Go/no-go memo
- **Verdict:** GO, validate first. Confidence **MEDIUM** (two-axis; function axis absent).
- **Decisive experiment:** base-edit the A>G base at chr14:33788719 in SU-DIPG-XIII or
  HSJD-DIPG-007, in parallel with CRISPRi of the element; read NPAS3 mRNA, local ATAC
  accessibility, and the OPC-differentiation phenotype.
- **Kill criterion:** no change in NPAS3 beyond noise after both the base edit and CRISPRi.
- **Therapy angle (Axis D, tumour-suppressor lost):** NPAS3 cannot be directly restored;
  nominate the **EZH2 / EZHIP reactivation** axis (H3 K27M silencing is epigenetic; residual
  PRC2 is a dependency, Mohammad et al., Nat Med 2017, PMID 28263309) or use the variant as
  a **prognostic / stratification** biomarker. Therapy confidence Low, biomarker Medium.
  NCypher does not predict drug response; CNS delivery (BBB) is the binding constraint.

### 7. Honesty
NPAS3 is a MEDIUM lead, not a driver. What this is not: not a recurrent non-coding driver
(gene-level, p does not survive Bonferroni), not a validated target, not a restore-therapy
nomination.

---

## Example 2 - SOX2-OT (the star mechanism chain)

**Variant:** `chr3-181317760-C-T`  ·  gene *SOX2-OT* (intron)  ·  a single DMG patient

### 1. Intake
Single somatic non-coding SNV, GRCh38, `chr3-181317760-C-T`. In the cached sweep.

### 2. Score (from `score_variant`)
- **chromatin:** log2FC **+0.26** (accessibility **gain**), JSD 0.067, high-impact **yes**
  (clears the p99 of 0.162; impact percentile 0.999 in the cohort).
- **constraint:** phyloP **3.54**, constrained **yes**.
- **function:** not available.

### 3. Converge
2 axes available, 2 impactful, agreement **1.0**, in domain. Verdict: **GO**.

Real memo text returned by the tool:
> GO: validate chr3-181317760-C-T first. Evidence converges (log2FC=+0.26, JSD=0.067
> (gain)  phyloP=3.54 (constrained @ 2.27)); predicted chromatin gain.

### 4. Mechanism
An accessibility **gain** in an evolutionarily constrained element inside the *SOX2-OT*
body, **394 kb** 5' of *SOX2*, the master TF of the OPC-like / glioma-stem state that
defines this tumour (Suva et al., Cell 2014, PMID 24726434; Filbin et al., Science 2018,
PMID 29674595). A gain fits a variant that **reinforces** the core stemness circuit. This
variant is a small-effect GAIN, so it is not in the top-40 DeepSHAP hero set; running
model-native contribution scoring on it (the accessibility-gain / motif-creation analysis)
is the next step to show a **created** motif at the alt base. Driver: chromatin gain plus
constraint; the mechanistic weight is the target-gene biology, not effect size.

### 5. Skeptic step (tried to refute it)
- **Brain-expression / length confounder?** SOX2-OT is SOX2's antisense lncRNA, not on the
  strict canonical neural gene list, so it does not inflate the neural-enrichment count;
  its relevance is the OPC core circuit, argued from biology, not from the enrichment test.
- **Within noise?** Partly a concern. The chromatin effect is **modest** (+0.26); it clears
  the p99 threshold but is small in absolute terms. phyloP 3.54 clears 2.27 but not deeply.
  Honestly a **Medium**, not a slam-dunk, on magnitude.
- **Constraint doing all the work?** No, the gain is a real chromatin signal, but it is modest.
- **Enhancer-to-gene link weak?** This is the **key** weakness. The element is 394 kb from
  the SOX2 promoter. It is within the same locus / TAD and a canonical long-range
  enhancer-in-lncRNA case, but the 394 kb link **must** be confirmed by fetal-brain / DIPG
  Hi-C. Even the conservative reading (the element regulates SOX2-OT, a positive SOX2
  regulator) is pro-SOX2. Link confidence: **Medium**, pending Hi-C.
- **Mapping / recurrence artefact?** Private, single-patient; not claimed as recurrent. The
  chain rests on the core-circuit biology, not recurrence.

**What would kill it:** (a) base-edit chr3:181317760 in an OPC-like line and CRISPRi the
element; if SOX2 accessibility and mRNA do not move, dead. (b) If Hi-C shows no contact
between the element and SOX2, re-route the memo to the actual Activity-by-Contact target
before any wet-lab spend.

**Survives** as the cleanest single-variant-to-drug logic on the core circuit, at
**MEDIUM** confidence, with the 394 kb link flagged as the thing to confirm first.

### 6. Go/no-go memo
- **Verdict:** GO, validate first. Confidence **MEDIUM**.
- **Decisive experiment:** base-edit the C>T base at chr3:181317760 in an OPC-like DMG line,
  in parallel with CRISPRi of the element; read element and SOX2-promoter accessibility,
  SOX2 mRNA/protein, the core-regulatory-circuit programme, and proliferation / self-renewal.
- **Kill criterion:** base edit does not move SOX2 beyond noise AND CRISPRi of the element
  does not lower SOX2. Second kill: Hi-C shows no element-to-SOX2 contact.
- **Therapy angle (Axis A, OPC/stem core circuit):** a tumour whose stem state is reinforced
  by this circuit is a rational candidate for the circuit's transcriptional dependency:
  **BET (BRD4) or CDK7 inhibition, synergistic with HDAC**, all validated in DIPG (Nagaraja
  et al., Cancer Cell 2017, PMID 28434841). Therapy confidence High for the axis, Medium
  that this variant marks a drug-responsive tumour. NCypher does not predict drug response;
  brain-penetrant BET/CDK7 chemotypes or CED are the realistic delivery routes (BBB caveat).

### 7. Honesty
A MEDIUM star chain: the boldest defensible single-variant story, but the variant effect is
modest and the 394 kb enhancer-to-gene link needs Hi-C. What this is not: not a proven SOX2
enhancer, not a validated target, not a claim that NCypher out-predicts AlphaGenome.

---

## Why these two, together

NPAS3 is the **strongest lead by evidence** (large effect, deep constraint, 80% contribution
collapse, gene-level recurrence, external validation), routing to a biomarker / epigenetic
axis. SOX2-OT is the **cleanest mechanism-to-drug chain** (a gain that reinforces the OPC
core circuit, routing to clinical-stage BET/CDK7), but with a modest effect and a long-range
link to confirm. Presenting both, each with its honest confidence and its kill criterion, is
the NCypher shape: a ranked, mechanism-explained, druggable-linked shortlist of what to
validate first, not a leaderboard number.
