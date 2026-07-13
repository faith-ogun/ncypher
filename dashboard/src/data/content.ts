import type { HeroContent } from "../types";

// Authored narrative for the featured variants. Every claim here is checked
// against skill/references/guardrails.md and docs/plan/the-finding.md.
// Numbers come from the sweep (ncypher.json); this file holds only prose.
// British English, no em dashes.

export const HERO_ORDER = [
  "chr14-33788719-A-G", // NPAS3   GO  (the lead)
  "chr22-33000876-C-T", // SYN3    GO  (strongest signal, real DeepSHAP logo)
  "chr3-181317760-C-T", // SOX2-OT GO  (the star chain, accessibility gain)
  "chr13-98333680-C-G", // FARP1   GO  (real DeepSHAP logo, SOX10)
  "chr11-75445498-C-T", // GDPD5   GO  (real DeepSHAP logo, NFIA)
  "chr5-1295113-G-A", // TERT     positive control (real DeepSHAP logo)
  "chr4-57055909-T-C", // IGFBP7  HOLD (chromatin fires, constraint disagrees)
  "chr9-79651705-C-T", // TLE4    NO-GO (deeply conserved, chromatin silent)
];

export const HEROES: Record<string, HeroContent> = {
  // ---------------------------------------------------------------- NPAS3 --
  "chr14-33788719-A-G": {
    key: "chr14-33788719-A-G",
    label: "NPAS3",
    gene: "NPAS3",
    tagline: "Neurodevelopmental TF, validated glioma tumour suppressor",
    kind: "lead",
    saliencyKind: "collapse",
    mechanism:
      "Accessibility loss inside an NPAS3 intronic OPC enhancer, with an 80% collapse of local model-native DeepSHAP contribution at the variant base (0.299 to 0.059). The crude PWM top call here is noisy, so NCypher reports the contribution collapse and does not assert a specific transcription factor.",
    driverAxis:
      "Constraint (phyloP 4.68) plus a chromatin accessibility loss. The neurodevelopmental focus of the shortlist is carried by the constraint axis, not the chromatin model.",
    skeptic: [
      "Gene-level recurrence (three different enhancers in three patients), not a single recurrent element. The per-gene binomial p = 0.014 does NOT survive Bonferroni across ~6,800 genes.",
      "Only 1 of the 3 NPAS3 variants is fully converged. This is a biologically motivated, externally validated lead, not a genome-wide-significant driver.",
      "External support is for the gene as a tumour suppressor (Moreira 2011; Michaelsen 2025), not for this specific element. Enhancer-to-gene needs Activity-by-Contact plus Hi-C.",
    ],
    memo: {
      validateFirst:
        "Confirm this element is an NPAS3 enhancer: ABC plus fetal-brain Hi-C should place a within-TAD contact between the peak and the NPAS3 promoter; cross-check an NPAS3 eQTL in a paediatric-brain cohort.",
      decisiveExperiment:
        "Base-edit the exact A>G base in an OPC-like DMG line and, in parallel, silence the element with CRISPRi (dCas9-KRAB). Read NPAS3 mRNA and accessibility at the promoter.",
      killCriterion:
        "If base-editing the single predicted base does not lower NPAS3 accessibility or expression AND CRISPRi of the element does not lower NPAS3, the score was a shortcut and the chain is dead. Report it.",
      therapyAngle:
        "Tumour suppressor lost: there is no direct restore drug. Nominate the EZH2 / EZHIP axis (residual PRC2 is a dependency under H3 K27M; Mohammad 2017) or use the variant as a prognostic / stratification biomarker.",
      therapyAxis: "D",
      therapyConfidence: "Low for therapy, Medium for biomarker. Carries the BBB delivery caveat.",
    },
  },

  // ----------------------------------------------------------------- SYN3 --
  "chr22-33000876-C-T": {
    key: "chr22-33000876-C-T",
    label: "SYN3",
    gene: "SYN3",
    tagline: "Strongest effect and deepest constraint in the cohort",
    kind: "converged",
    saliencyImage: "saliency/SYN3_chr22-33000876-C-T.png",
    saliencyKind: "deepshap",
    mechanism:
      "The strongest chromatin effect in the cohort (log2FC -1.24) at the deepest-conserved converged base (phyloP 8.58). A 90% collapse of local DeepSHAP contribution, cleanly breaking an NFIA motif (an OPC-lineage master transcription factor, PWM delta -17.6).",
    motifClaim: "NFIA (OPC-lineage master TF), clean PWM disruption",
    driverAxis: "Both axes fire hard: chromatin loss and deep evolutionary constraint agree.",
    skeptic: [
      "Private, single-patient variant. There is no recurrent non-coding hotspot in DMG, consistent with its enhancer-reprogramming biology.",
      "The regulated gene is not settled: TIMP3 (a methylation-silenced glioma tumour suppressor ~138 kb away) is a coherent alternative to SYN3. ABC / Hi-C is the arbiter. This is exactly the informative disagreement NCypher surfaces.",
    ],
    memo: {
      validateFirst:
        "Run ABC plus fetal-brain / DIPG Hi-C to disambiguate SYN3 versus TIMP3 as the regulated target before any wet-lab spend.",
      decisiveExperiment:
        "Base-edit chr22:33,000,876 (C>T) in an OPC-like DMG line; read the resolved target gene and the neuron-glioma synaptic / electrical phenotype (AMPA-R currents, activity-driven proliferation in neuron co-culture).",
      killCriterion:
        "No change in the ABC-resolved target gene, or no change in activity-dependent proliferation, kills the chain.",
      therapyAngle:
        "Synaptic / neuronal-activity axis: AMPA-receptor antagonism (perampanel) or gap-junction blockade (meclofenamate). Neuron-glioma electrochemical signalling is an in-vivo genetic dependency (Venkatesh 2017, 2019).",
      therapyAxis: "B",
      therapyConfidence:
        "High for the programme, Low to Medium that this single host gene is cell-autonomously essential. Carries the BBB delivery caveat.",
    },
  },

  // --------------------------------------------------------------- SOX2-OT --
  "chr3-181317760-C-T": {
    key: "chr3-181317760-C-T",
    label: "SOX2-OT",
    gene: "SOX2-OT",
    tagline: "The star chain: a regulatory gain on the OPC/glioma-stem core circuit",
    kind: "converged",
    saliencyKind: "gain",
    mechanism:
      "A rare accessibility GAIN (log2FC +0.26, above the calibrated p99 threshold of 0.162) inside the SOX2-OT body, 394 kb from SOX2, the master transcription factor of the OPC-like/glioma-stem state that defines this tumour. A gain that reinforces the core stemness circuit. No single clean PWM call, so reported as a gain of accessibility pending an AlphaGenome cross-check.",
    driverAxis:
      "Chromatin accessibility gain plus constraint (phyloP 3.54). The direction (gain) fits SOX2 up, the biologically coherent reading.",
    skeptic: [
      "Modest effect (+0.26). The enhancer-to-gene link spans 394 kb, at the outer-but-plausible range for ABC; intra-TAD Hi-C is the decisive arbiter.",
      "Even the conservative reading (the element regulates SOX2-OT rather than SOX2 directly) is pro-SOX2, because SOX2-OT is a positive regulator of SOX2 in neural / stem contexts. But that is a prior, not proof.",
    ],
    memo: {
      validateFirst:
        "Is the element a SOX2 enhancer? Confirm the OPC peak overlaps active marks, and that ABC plus fetal-brain / DIPG Hi-C place a within-TAD contact to the SOX2 promoter. Cross-check a SOX2 eQTL.",
      decisiveExperiment:
        "Install the exact patient allele at chr3:181,317,760 by CRISPR base editing, and in parallel CRISPRi-silence the element. Read accessibility at the element and the SOX2 promoter, SOX2 mRNA/protein, the OPC-stemness signature, and proliferation.",
      killCriterion:
        "If base-editing does not move SOX2 AND CRISPRi of the element does not lower SOX2, the score was a shortcut. Second kill: if Hi-C shows no element-to-SOX2 contact, re-route the memo to the true ABC target first.",
      therapyAngle:
        "OPC/stem core circuit: nominate the transcriptional dependency one step from the undruggable TF, BET (BRD4) or CDK7 inhibition synergistic with HDAC inhibition, all validated in DIPG (Nagaraja 2017). Clinical-stage.",
      therapyAxis: "A",
      therapyConfidence:
        "High for the axis biology, Medium that this variant marks a drug-responsive tumour. Carries the BBB delivery caveat.",
    },
  },

  // ---------------------------------------------------------------- FARP1 --
  "chr13-98333680-C-G": {
    key: "chr13-98333680-C-G",
    label: "FARP1",
    gene: "FARP1",
    tagline: "Deep constraint, clean OPC-master-TF collapse",
    kind: "converged",
    saliencyImage: "saliency/FARP1_chr13-98333680-C-G.png",
    saliencyKind: "deepshap",
    mechanism:
      "Accessibility loss at the deepest-conserved base among the hero set (phyloP 8.64), with an 84% collapse of local DeepSHAP contribution cleanly breaking a SOX10 motif, an OPC-lineage master transcription factor.",
    motifClaim: "SOX10 (OPC-lineage master TF), clean PWM disruption",
    driverAxis: "Both axes fire: chromatin loss and deep constraint agree.",
    skeptic: [
      "Private, single-patient variant; no recurrent hotspot.",
      "FARP1 (dendrite and synapse morphogenesis) is the host gene, but ABC should confirm FARP1 versus neighbours (for example STK24) as the regulated target.",
    ],
    memo: {
      validateFirst:
        "ABC / Hi-C to confirm FARP1 (versus STK24) as the regulated target.",
      decisiveExperiment:
        "Base-edit chr13:98,333,680 in an OPC-like DMG line; read the target gene and the synaptic phenotype.",
      killCriterion:
        "No change in the ABC-resolved target gene, or no change in activity-dependent proliferation, kills the chain.",
      therapyAngle:
        "Synaptic / neuronal-activity axis: AMPA-receptor antagonism (perampanel) or gap-junction blockade (meclofenamate).",
      therapyAxis: "B",
      therapyConfidence:
        "High for the programme, Low to Medium for the single host gene. Carries the BBB delivery caveat.",
    },
  },

  // ---------------------------------------------------------------- GDPD5 --
  "chr11-75445498-C-T": {
    key: "chr11-75445498-C-T",
    label: "GDPD5",
    gene: "GDPD5",
    tagline: "Oligodendrocyte-lineage locus, strongest contribution collapse",
    kind: "converged",
    saliencyImage: "saliency/GDPD5_chr11-75445498-C-T.png",
    saliencyKind: "deepshap",
    mechanism:
      "Accessibility loss with a 91% collapse of local DeepSHAP contribution, cleanly breaking an NFIA motif (an OPC-lineage master transcription factor). GDPD5 has oligodendrocyte / myelin and neurite-outgrowth relevance.",
    motifClaim: "NFIA (OPC-lineage master TF), clean PWM disruption",
    driverAxis:
      "Chromatin loss (strong) plus constraint (phyloP 2.80, just over the 2.27 threshold).",
    skeptic: [
      "Private, single-patient variant; no recurrent hotspot.",
      "Constraint here is modest (phyloP 2.80, near the threshold); the chromatin and mechanism signals carry this call more than the constraint does.",
    ],
    memo: {
      validateFirst: "ABC / Hi-C to confirm GDPD5 as the regulated target.",
      decisiveExperiment:
        "Base-edit chr11:75,445,498 in an OPC-like DMG line; read GDPD5 and the OL-differentiation phenotype.",
      killCriterion:
        "No change in the ABC-resolved target gene kills the chain.",
      therapyAngle:
        "OL-lineage / differentiation programme; route through the OPC core-circuit transcriptional dependency (BET/CDK7/HDAC) if ABC resolves to a core-circuit gene.",
      therapyAxis: "A",
      therapyConfidence: "Medium for the axis. Carries the BBB delivery caveat.",
    },
  },

  // ----------------------------------------------------------------- TERT --
  "chr5-1295113-G-A": {
    key: "chr5-1295113-G-A",
    label: "TERT",
    gene: "TERT (C228T)",
    tagline: "Positive control: the canonical non-coding oncogenic variant",
    kind: "control",
    saliencyImage: "saliency/TERT_C228T.png",
    saliencyKind: "deepshap",
    mechanism:
      "The textbook TERT promoter mutation. The alternate-allele saliency shows a de-novo GGAA ETS (GABPA) motif created at the variant, exactly the TERT-reactivation mechanism, recovered by the OPC model from sequence alone. This is a sanity check that the model reads real TF grammar, not a GC shortcut.",
    motifClaim: "de-novo ETS / GABPA (GGAA) motif created by the alt allele",
    driverAxis:
      "Chromatin: the model correctly fires on a known-functional positive control and recovers its mechanism.",
    skeptic: [
      "The magnitude is modest in the OPC context (log2FC +0.10), which is honest: TERT reactivation is not principally an OPC-accessibility event. The point of this control is the recovered mechanism, not the score size.",
      "This is a positive control for calibration, not a DMG somatic hit. It is shown to demonstrate the model recognises a validated non-coding driver mechanism.",
    ],
    holdNote:
      "Positive control. Not a DMG cohort variant. It confirms the engine recovers a canonical non-coding oncogenic mechanism (ETS-motif creation) from sequence, which is the credibility check behind every DMG call.",
  },

  // ---------------------------------------------------------------- IGFBP7 --
  "chr4-57055909-T-C": {
    key: "chr4-57055909-T-C",
    label: "IGFBP7",
    gene: "IGFBP7",
    tagline: "Informative disagreement: chromatin fires, constraint does not",
    kind: "hold",
    saliencyKind: "none",
    mechanism:
      "A strong predicted accessibility loss (log2FC -1.10, well past the high-impact threshold), but at an evolutionarily unconstrained base (phyloP -0.36, slightly accelerated). The chromatin model likes it; evolution does not.",
    driverAxis:
      "One axis only. Agreement is 1 of 2 available axes (50%), below the 66% bar for a GO.",
    skeptic: [
      "NCypher does not promote on a single axis. This is surfaced as a HOLD, an informative disagreement, not hidden.",
      "Resolve the constraint axis before bench time: is this a human-specific / accelerated regulatory change, or a chromatin-model shortcut (GC / mappability)? Score the third axis (MPRA / CRISPRi) to break the tie.",
    ],
    holdNote:
      "HOLD. The chromatin axis fires hard but the constraint axis disagrees. This is the honest output a responsible tool gives: resolve the disagreeing axis (score function, or check for a model shortcut) before committing bench time. A confident single-axis GO here would be exactly the overclaim the guardrails forbid.",
  },

  // ----------------------------------------------------------------- TLE4 --
  "chr9-79651705-C-T": {
    key: "chr9-79651705-C-T",
    label: "TLE4",
    gene: "TLE4",
    tagline: "Deeply conserved, but the chromatin model is silent",
    kind: "nogo",
    saliencyKind: "none",
    mechanism:
      "A deeply conserved base (phyloP 8.90, among the most constrained in the genome) where the OPC chromatin model predicts essentially no accessibility change (log2FC +0.003). Evolution flags it; chromatin does not.",
    driverAxis:
      "Chromatin is not impactful. Constraint alone cannot promote a variant.",
    skeptic: [
      "A single axis is never enough. Deep conservation without a chromatin effect in the matched context is not a functional regulatory call here.",
      "This is the mirror image of the HOLD case, and it is a NO-GO because the chromatin axis (the one that must fire for a regulatory-activity call) is flat.",
    ],
    holdNote:
      "NO-GO. Constraint is deep, but the chromatin axis is flat, so NCypher does not promote it. Reaching a GO would require the chromatin model to fire in the matched OPC context. Equally, scoring any variant in a mismatched context (breast, non-OPC brain) is out-of-domain and NO-GO by default.",
  },
};

// Therapy axis reference (skill/references/therapy-map.md), shown on The Finding.
export const THERAPY_AXES: {
  id: string;
  name: string;
  routeFrom: string;
  node: string;
  confidence: string;
}[] = [
  {
    id: "A",
    name: "Super-enhancer / transcriptional addiction",
    routeFrom: "OPC / stem core circuit: SOX2, OLIG2, SOX10, POU3F2, SALL2",
    node: "BET (BRD4), CDK7, plus HDAC inhibition",
    confidence: "High axis / Medium variant",
  },
  {
    id: "B",
    name: "Neuron-to-glioma activity-regulated",
    routeFrom: "Synaptic / activity: SYN3, FARP1, DISC1, DOCK4, LRRC4C, KCNMA1",
    node: "AMPA-R antagonist (perampanel), gap-junction blocker (meclofenamate), ADAM10i",
    confidence: "High programme / Low-Med gene",
  },
  {
    id: "D",
    name: "Tumour suppressor lost",
    routeFrom: "Silenced by accessibility loss: NPAS3",
    node: "EZH2 / EZHIP reactivation, or biomarker only",
    confidence: "Low therapy / Med biomarker",
  },
];

// The bright-line "Do NOT say" guardrails (skill/references/guardrails.md).
export const GUARDRAILS: string[] = [
  "NCypher does not out-predict AlphaGenome, Enformer, Malinois or the Pollard CNN-BiLSTM, and does not try to. It is the convergence layer that couples a score with mechanism and an honesty flag.",
  "The chromatin axis is validated against caQTLs (allelic accessibility, AUROC 0.69 in the matched context), not the MPRA reporter assay, which is a different modality we do not conflate.",
  "The converged hits are private, single-patient hypotheses to validate, not recurrent or proven non-coding drivers.",
  "The therapy axes are hypothesis routing, each with a blood-brain-barrier delivery caveat. NCypher does not predict drug response.",
  "No GO on a single axis or an out-of-domain call. A verdict needs two axes agreeing in the right cell context.",
];
