# A2: hardening the K27M super-enhancer constraint finding against distance-to-TSS and replication-timing

**Question.** The flagship finding says H3K27M super-enhancers sit on more evolutionarily
constrained OPC sequence (in-SE median phyloP 0.283 vs out-SE 0.185, MWU p=2.6e-3, one-sided).
Its skeptic flagged two uncontrolled confounds: constrained sequence tends to sit near TSS and
in early-replicating regions. A2 asks whether the in-SE constraint premium survives matching and
regressing on distance-to-TSS and replication timing.

**Verdict: SURVIVES.**

---

## Headline numbers (all independently re-verified from `a2_features.tsv.gz`)

| quantity | value | test / detail |
|---|---|---|
| naive in-SE median phyloP | **0.283** | n=1,946 |
| naive out-SE median phyloP | **0.185** | n=8,907 (16 NaN-phyloP dropped, all out-SE) |
| naive MWU p (two-sided) | **5.2e-3** | one-sided (greater) = 2.61e-3, matches canonical 2.6e-3 |
| matched permutation p | **0.0010** | 1000 draws, seed 0; floor for 1000 draws |
| observed in-SE median (matched strata) | **0.281** | |
| matched-null median | **0.154** | 95% [0.114, 0.192] |
| OLS in_se coef (mean shift) | **0.140** | p=0.016 (HC3); bootstrap 95% CI [0.025, 0.249] |
| median-regression in_se coef | **0.087** | p=2.4e-3; bootstrap 95% CI [0.021, 0.156] |

Naive raw median difference 0.096; confound-adjusted median shift 0.087. The two confounds
jointly explain <10% of the effect.

## Method

1. **Input.** `data/dmg/enhancers/a2_input.tsv` (10,869 OPC-regulatory somatic SNVs, labelled
   in_se 1,946 / out 8,923, with phyloP, coords, class). Confirmed row/label counts match the brief.
2. **Distance to nearest TSS.** GENCODE v44 (hg38) comprehensive GTF; 252,835 transcripts ->
   219,270 unique TSS (start for +, end for -). Per-variant nearest-TSS distance (hg38 native,
   0 missing).
3. **Replication timing.** ENCODE/UW Repli-seq wavelet-smoothed WaveSignal, SK-N-SH (neural), hg19.
   Variant positions lifted hg38 -> hg19 (UCSC hg38ToHg19 chain), then queried against WaveSignal.
   41/10,869 missing (0.4%; 31 liftover failures). Higher WaveSignal = earlier replication.
4. **Naive difference** reproduced exactly (0.283 vs 0.185).
5. **Control (a) matched permutation.** Strata = distance-to-TSS decile x rep-timing decile x
   variant class. Out-SE controls drawn to match the in-SE stratum distribution, 1000 draws, seed 0.
   99.2% of in-SE matchable; empirical p = 0.0010.
6. **Control (b) regression.** `phylop ~ in_se + log_dist_tss + rep_timing + C(cls)`, both OLS
   (HC3 robust SE, mean estimand) and median (quantile q=0.5) regression. The median regression is
   the estimand that matches the finding's median claim. Bootstrap 95% CIs, 2000 resamples, seed 0.

## Confound QC (why it survives)

A variable can only confound if it associates with both in_se and phyloP.

- **Distance-to-TSS:** barely differs in vs out-SE (median 5,317 vs 5,416 bp, MWU p=0.10);
  near-zero correlation with phyloP (Spearman rho=-0.020). Weak confound at most.
- **Replication timing:** in-SE is strongly earlier-replicating (65.1 vs 57.7, MWU p=6e-133) -
  a real exposure difference - but essentially zero correlation with phyloP (rho=0.002, p=0.86).
  It predicts SE membership, not constraint, so it cannot mediate the phyloP premium.

## Falsification (skeptic step)

**Strongest argument against:** the matched null could be a sparse-control artefact. Because in-SE
variants concentrate in early-replicating deciles where out-SE controls are scarce, the matched null
might be built by resampling a handful of atypical controls with replacement, inflating variance and
making the observed median look artificially extreme.

**Guard / test:** restricting the permutation to the 193 strata with >=5 distinct out-SE controls
(min pool 5, still covering 96.4% of in-SE) leaves the result unchanged: observed 0.281 vs null 0.154
[0.114, 0.198], p=0.0010. This guard permutation is stored under `guard_ge5_permutation` in
`reviewer_check.json`. The result does not depend on thin pools. **Argument refuted.**

Note on the figure: panel (a) plots the **full** naive comparison (n=1,946 in / 8,907 out;
medians 0.283 / 0.185). Panels (b) and both regressions use the **complete-case** subset (n=10,818;
in 1,944 / out 8,874), which drops 51 variants missing a confound feature (41 rep-timing, plus 10
where dropping the 16 NaN-phyloP overlaps). On complete-case the naive medians are 0.281 / 0.186 -
the 0.002 shift from the dropped rows does not affect any test or the verdict.

## Honest caveats

- The effect is **modest** (+0.087 confound-adjusted median phyloP). Enrichment is not selection;
  this is a confound-controlled, hypothesis-generating observation, not a somatic-driver claim.
- The replication-timing track is a **cross-cell-type proxy**: ENCODE has no fetal-OPC/NPC Repli-seq,
  so SK-N-SH (neuroblastoma, neural-crest lineage, and coincidentally one of the lentiMPRA cell lines)
  stands in. Replication timing is broadly conserved across cell types, so this is an acceptable proxy,
  but it is a proxy and stated as such.
- The naive p=2.6e-3 canonical figure is the one-sided MWU; the two-sided is 5.2e-3. Reported both.

## Provenance

- **Input:** `data/dmg/enhancers/a2_input.tsv` (repo commit a943c3d).
- **GENCODE:** `https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gtf.gz`
- **Repli-seq:** `https://hgdownload.soe.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeUwRepliSeq/wgEncodeUwRepliSeqSknshWaveSignalRep1.bigWig`
  (ENCODE experiment context: SK-N-SH Repli-seq, John Stamatoyannopoulos lab, UW).
- **Liftover chain:** `https://hgdownload.soe.ucsc.edu/goldenPath/hg38/liftOver/hg38ToHg19.over.chain.gz`
- **Env:** python 3.13.14; pandas 3.0.3, numpy 2.5.1, scipy 1.18.0, statsmodels 0.14.6,
  matplotlib 3.11.0, pyBigWig 0.3.25, pyliftover 0.4.1. Seeds: permutation & bootstrap seed 0.
- **MCP grounding:** NCypher `cohort_summary` (10,869 scored, 753 chromatin high-impact, 1,583
  constrained, 164 converged, 0 recurrent, 0 canonical drivers); `score_variant` on three genuine
  SE-resident converged hits (LINC01117 phyloP 8.82 log2FC-0.26; POLR2F 8.70 / -0.70; NOL4L 7.02 / -0.19).
- **Outputs:** `a2_features.tsv.gz` (per-variant features), `a2_results.json`, `reviewer_check.json`,
  `a2_phylop_se_confound.png`, `tss_hg38_gencode_v44.tsv.gz`.

## Confirmed vs inferred

- **Confirmed (computed here):** all naive/permutation/regression numbers, confound QC, the guard.
- **Inferred / proxy:** SK-N-SH replication timing as a stand-in for fetal-OPC timing.
