# NCypher DMG therapy-axis mapping

How NCypher routes a promoted non-coding regulatory finding to a real, published DMG
therapeutic axis. This is a **hypothesis-routing** map, not a treatment recommendation.
NCypher does not predict drug response (guardrail 4); every nomination below carries the
blood-brain-barrier (BBB) delivery caveat, because CNS exposure is the binding constraint
for these classes. British English, no em dashes. All citations are PubMed-verified;
sources are `docs/research/dmg-therapeutics.md` and `docs/plan/the-finding.md`.

The routing rule (from the target gene): if the target is an undruggable transcription
factor, nominate the **actionable node one step away**. Every node below is an
independently published DMG programme, so NCypher routes to real vulnerabilities, it does
not invent them.

---

## Why DMG is the right disease for a regulatory-variant tool

H3 K27M collapses H3K27me3 and redistributes H3K27ac, so the disease is defined by
**chromatin state, enhancer activity and transcriptional addiction**, not by a tidy set
of coding drivers. The coding landscape (H3, ACVR1, PDGFRA, TP53) is largely solved and
largely undruggable; the **non-coding regulatory layer is where the dependencies live**.
That is the white space a ChromBPNet-plus-constraint convergence engine can occupy. The
one approved drug (dordaviprone / ONC201, FDA accelerated approval Aug 2025) gives ~20 to
22% ORR in recurrent disease; median survival remains ~11 months. The honest impact frame
is **prioritisation and triage, not cure**.

---

## The three axes NCypher routes to

### Axis A - super-enhancer / transcriptional-addiction (BET/BRD4, CDK7, HDAC)

- **Route from:** OPC / glioma-stem core-circuit genes - **SOX2** (and SOX2-OT), OLIG2,
  SOX10, POU3F2, SALL2. These are neurodevelopmental master TFs, essential for glioma
  propagation and sufficient to reprogram the stem-like state (Suva et al., Cell 2014,
  PMID 24726434); H3 K27M DMG is dominated by the OPC-like stem state (Filbin et al.,
  Science 2018, PMID 29674595).
- **Druggable node one step away:** BET (BRD4) inhibition, CDK7 inhibition, synergistic
  with HDAC inhibition (panobinostat). DIPG carries a distinctive super-enhancer landscape
  and is addicted to the machinery that fires it (Nagaraja et al., Cancer Cell 2017,
  PMID 28434841; Piunti et al., Nat Med 2017, PMID 28263307; Grasso et al., Nat Med 2015,
  PMID 25939062).
- **Best mechanistic fit** for a regulatory-activity model: a variant that creates or
  strengthens a TF motif inside a DMG super-enhancer near an oncogene is directly a
  BET/CDK7-actionable lesion. **Lead with this axis.**
- **Confidence:** High for the axis biology; Medium that a given variant marks a
  drug-responsive tumour. **BBB caveat:** brain-penetrant BET/CDK7 chemotypes or
  convection-enhanced / intra-CSF delivery are the realistic routes.

### Axis B - neuron-to-glioma activity-regulated (NLGN3, BDNF/TrkB, AMPA-R)

- **Route from:** synaptic / neuronal-activity genes - **SYN3, FARP1, DISC1, DOCK4,
  LRRC4C, KCNMA1**. This is the most Gladstone-resonant and the hottest new DMG biology.
- **Druggable nodes one step away:** AMPA-receptor antagonism (perampanel); gap-junction
  blockade (meclofenamate); ADAM10 inhibition (blocks NLGN3 shedding); TrkB blockade.
  Neuronal activity drives glioma growth via secreted NLGN3 (Venkatesh et al., Cell 2015,
  PMID 25913192; Nature 2017, PMID 28959975), glioma cells form bona fide AMPA-mediated
  synapses (Venkataramani et al., Nature 2019, PMID 31534219), and BDNF-TrkB potentiates
  them (Taylor et al., Nature 2023, PMID 37914930). KCNMA1 (a BK K+ channel) is on-point:
  Nagaraja 2017 names potassium-channel function as a DIPG viability mechanism.
- **Confidence:** High for the programme (in-vivo genetic dependency: paediatric glioma
  xenografts fail to grow in Nlgn3-knockout mice). Low to Medium that any single host gene
  is cell-autonomously essential (the axis is largely microenvironmental / electrical).
  This axis routes therapy through the **programme**, not necessarily the host gene.

### Axis C - imipridone response / resistance (ONC201, PPARGC1A)

- **Route from:** regulatory variants that tune the imipridone-resistance transcriptional
  programme, or the DRD2 / mitochondrial gene neighbourhood.
- **Clinical anchor:** dordaviprone (ONC201) is the only approved DMG drug (ClpP agonist +
  DRD2/3 antagonist; Arrillaga-Romany et al., JCO 2024, PMID 38335473). Resistance runs
  through **PPARGC1A / mitochondrial biogenesis**, itself a gene-regulatory programme, so
  the resistance axis is a non-coding transcriptional read (Okada et al., Neuro-Oncology
  2026, PMID 42178382).
- **Confidence:** Medium for the biology; connecting a regulatory finding to standard-of-care
  response makes a nomination clinically legible, but response prediction is out of scope.

### Axis D (special case) - tumour-suppressor lost

- **Route from:** a tumour-suppressor gene silenced by an accessibility-**loss** variant,
  e.g. **NPAS3** (validated glioma tumour suppressor; Moreira et al., Am J Pathol 2011,
  PMID 21703424; and a paediatric-medulloblastoma tumour-suppressor master regulator,
  Michaelsen et al., Sci Rep 2025).
- **There is no direct restore drug.** Nominate the **EZH2 / EZHIP axis or reader/eraser
  reactivation** (H3 K27M silencing is epigenetic; residual PRC2 is a dependency, Mohammad
  et al., Nat Med 2017, PMID 28263309), or use the variant as a **prognostic /
  stratification** marker.
- **Confidence:** Low for therapy, Medium for biomarker. Do not nominate a restore therapy
  as if it exists.

---

## The mapping table (target class to node)

| If the target gene is ... | Nominate (node one step away) | Axis | Therapy confidence |
|---|---|---|---|
| OPC/stem core circuit (SOX2, OLIG2, SOX10, POU3F2, SALL2) | BET/BRD4, CDK7, +HDAC | A | High axis / Medium variant |
| synaptic / activity (SYN3, FARP1, DISC1, DOCK4, LRRC4C, KCNMA1) | AMPA-R antagonist (perampanel), gap-junction blocker (meclofenamate), ADAM10i, TrkB blockade | B | High programme / Low-Med gene |
| imipridone-resistance / mitochondrial (PPARGC1A neighbourhood) | ONC201 combination, PPARGC1A-directed | C | Medium |
| tumour suppressor lost (NPAS3) | EZH2/EZHIP reactivation, or biomarker only | D | Low therapy / Med biomarker |

**Every row carries the same closing guardrail:** this is a mechanism-anchored hypothesis
to validate, paired with a delivery story (CAR-T ICV, imipridones, CED payloads are the
classes already crossing or bypassing the BBB), not a prediction that the drug will work.
NCypher does not predict drug response.
