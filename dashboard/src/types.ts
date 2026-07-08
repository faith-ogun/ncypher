// Types for the bundled data (ncypher.json) and the authored content (content.ts).

export type Verdict = "GO" | "HOLD" | "NO-GO";
export type Direction = "gain" | "loss" | "flat";

export interface SweepRow {
  key: string;
  gene: string | null;
  cls: string | null;
  n_patients: number;
  logfc: number | null;
  abs_logfc: number;
  jsd: number;
  phylop: number | null;
  constrained: boolean;
  high_impact: boolean;
  converged: boolean;
  confidence: string | null;
  impact_pctile: number | null;
  direction: Direction;
  verdict: Verdict;
  deepshap_collapse?: number | null;
  top_tf?: string | null;
  pwm_delta?: number | null;
  is_opc_tf?: boolean;
  gene_n_hi_pat?: number | null;
}

export interface Provenance {
  model: string;
  model_context: string;
  genome: string;
  constraint_track: string;
  constraint_threshold: number;
  chromatin_hi_threshold: number;
  chromatin_hi_note: string;
  cohort: string;
  sources: string[];
}

export interface Cohort {
  n_scored: number;
  n_high_impact: number;
  n_constrained: number;
  n_converged: number;
  n_recurrent_converged: number;
  n_driver_genes: number;
  n_patients: number;
  converged_loss: number;
  converged_gain: number;
  class_breakdown: Record<string, number>;
  median_phylop: number;
  median_abs_logfc: number;
}

export interface AxisDecompRow {
  axis: string;
  subset: string;
  neural: number;
  fraction: number;
  fold: number;
  p: number;
  sig: "strong" | "nominal" | "ns";
  test: string;
}

export interface Npas3Variant {
  key: string;
  patient: string;
  peak: string;
  logfc: number;
  phylop: number;
  flag: string;
}

export interface Npas3 {
  key: string;
  gene: string;
  n_patients: number;
  n_enhancers: number;
  n_functional_variants: number;
  n_high_impact: number;
  binomial_p: number;
  expected_hi: number;
  deepshap_collapse: number;
  deepshap_ref: number;
  deepshap_alt: number;
  variants: Npas3Variant[];
}

export interface Finding {
  axisDecomposition: AxisDecompRow[];
  baseRate: number;
  convergedGenes: string[];
  npas3: Npas3;
}

export interface CaqtlRow {
  set: string;
  n_pos: number;
  auprc: number;
  fold: number;
  auroc: number;
  mwu_p: number;
}

export interface Validation {
  caqtl: CaqtlRow[];
  mpra: {
    n_davs: number;
    fdr: string;
    auprc: number;
    auprc_vs_base: number;
    auroc: number;
    pearson_r: number;
    frac_zero_in_c15: number;
  };
  motifbreakr: { caught: number; total: number; pct: number };
}

export interface NCypherData {
  meta: { generated: string; note: string };
  provenance: Provenance;
  thresholds: {
    chromatin_hi: number;
    chromatin_hi_note: string;
    constraint: number;
    constraint_note: string;
    model_context: string;
    genome: string;
  };
  cohort: Cohort;
  sweep: Record<string, SweepRow>;
  finding: Finding;
  validation: Validation;
}

// ---- Authored content (content.ts) ----------------------------------------

export type TherapyAxis = "A" | "B" | "C" | "D" | null;

export interface HeroContent {
  key: string;
  label: string; // short chip label, e.g. "NPAS3"
  gene: string;
  tagline: string; // one-line role
  kind: "lead" | "converged" | "control" | "hold" | "nogo";
  saliencyImage?: string; // path under /saliency, real DeepSHAP PNG
  saliencyKind: "deepshap" | "collapse" | "gain" | "none";
  mechanism: string; // paragraph, honesty-checked
  motifClaim?: string; // named TF only when PWM is clean
  driverAxis: string; // which axis drives the call
  skeptic: string[]; // falsification lines
  memo?: {
    validateFirst: string;
    decisiveExperiment: string;
    killCriterion: string;
    therapyAngle: string;
    therapyAxis: TherapyAxis;
    therapyConfidence: string;
  };
  holdNote?: string; // for HOLD / NO-GO explanation instead of a GO memo
}
