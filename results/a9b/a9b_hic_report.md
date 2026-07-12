# A9b - matched Hi-C ABC upgrade for the 164 converged variants

**Question.** A9's ABC fell back to a distance power-law because no Hi-C was available, so it merely reproduced nearest-gene. Swap in a real, cell-type-matched contact map (Won 2016 fetal germinal-zone Hi-C) and re-run. Two decisive tests: (1) does anything genuinely reassign now that contact is independent of distance, and (2) does the NPAS3 long-range (854 kb) enhancer-to-promoter loop appear that the power-law could not see?

**One-line verdict.** Matched Hi-C changes the top gene at 54 of 164 variants (33%), so contact is now genuinely independent of distance. But the change is a warning, not a win: of the 54, only 18 change because of a real contact loop (obs/exp >= 2), and **none of those 18 has independent brain-eQTL support**. They skew distal (500-900 kb) into strong contact domains (the top switch is to HOXD8, a Polycomb self-interacting cluster), which is the classic ABC structural-hub artefact. The one unambiguous positive is **NPAS3: the 854 kb loop is real** (obs/exp 5.6, 99.8th percentile), promoting NPAS3 from a power-law also-ran to co-top ABC. The trustworthy target calls remain the ones where distance, matched contact, and eQTL all agree (8 triangulated links), and there Hi-C confirms distance rather than overriding it.

---

## Inputs and provenance (confirmed unless marked inferred)

- **Variants + activity:** reused A9's staged inputs - `data/dmg/enhancers/a9_input.tsv` (164 converged SNVs) and `data/dmg/c15_peaks.bed.gz` (Corces fetal-OPC c15 ATAC, signalValue = activity). GENCODE v44 gene-level TSS (hg38) as in A9.
- **Contact (new): Won et al. 2016, Nature 538:523-527 (GEO GSE77565), the germinal-zone (GZ) genome-wide Hi-C contact matrix, 10 kb, hg19.** Confirmed from GSM metadata that **GZ = the FBP-labelled files** (GSM2054567-69, "layers: Germinal zone"), not FBD; FBD = the cortical-plate/neuron zone. File `GSE77565_FBP_IC-heatmap-chr-10k.hdf5.gz` (5,197,906,391 bytes). The HDF5 stores per-chromosome intra-chromosomal ICE-normalised matrices keyed by mirnylib index tuples ("(0, 0)" = chr1 ... "(22, 22)" = chrX); bin dimensions matched hg19 chromosome lengths exactly, confirming the mapping.
- **Genome build:** Hi-C is hg19; variants/peaks are hg38. Reconciled by lifting the query coordinates (element midpoints, candidate TSS, nearby peaks) hg38 -> hg19 with the UCSC `hg38ToHg19.over.chain`, then reading the hg19 matrix - not by remapping ~300k matrix bins.
- **Orthogonal support:** GTEx v8 brain cis-eQTL (13 tissues), reused from A9; a gene is eQTL-supported if it has a brain eQTL lead SNP within 10 kb of the element midpoint.
- **Compute:** the download + gunzip + liftOver + ABC ran as a Modal CPU job (8 CPU, 48 GB, image `im-kLsUKZ2SWsIlPm5uEcZwZ5` with h5py/numpy/pyliftover); final job `68223ead-f3ed-436e-87b2-d39ac1238eeb`, 425 s wall, exit 0, all 164 variants scored.

## Method

For each variant: element = enclosing c15 peak (activity = its signalValue); candidate genes = GENCODE TSS within 1 Mb; Contact(e,g) = the GZ Hi-C contact between the element's 10 kb bin and the candidate TSS bin; ABC(e,g) = Activity(e) x Contact(e,g) / sum over c15 peaks within 1 Mb of g's TSS. Standard ABC contact handling was applied and is load-bearing here: (a) **diagonal fix** - for bin separation <= 1 the self/adjacent contact is unreliable, so the separation-2 contact stands in; (b) a per-chromosome **pseudocount** (median contact at the 1 Mb window edge) added to every contact so a masked bin does not zero a proximal gene; (c) an **observed/expected** ratio per element-gene pair (contact divided by the chromosome-wide mean at that bin separation) to separate a real loop from generic domain proximity.

## Headline numbers (reviewer-verified: recomputed on an independent code path off the raw Modal files + the A9 artifact table, all matched)

| Quantity | Value |
|---|---|
| Variants scored with GZ Hi-C | 164 / 164 |
| Hi-C ABC top == A9 power-law top | 110 / 164 (67%) |
| Hi-C ABC top == nearest-TSS gene | 103 / 164 (63%) |
| (for contrast) power-law top == nearest-TSS | 139 / 164 (85%) |
| Hi-C ABC top == input host gene | 40 / 164 (24%) |
| **Target changed vs power-law** | **54 / 164 (33%)** |
| - of which loop-driven (Hi-C top obs/exp >= 2) | 18 |
| - loop-driven **and** brain-eQTL supported | **0** |
| Triangulated links (Hi-C == power-law top, eQTL-supported, non-host) | 8 |
| A9 power-law HIGH links surviving as Hi-C top | 6 / 9 |

The reading: power-law ABC agreed with nearest-TSS 85% of the time (it is a distance function); matched Hi-C drops that to 63% and disagrees with the power-law itself at 33% of variants. That 33% is the genuine independence-from-distance the brief asked for. But independence is only useful if the new calls are better supported, and they are not: the loop-driven switches have zero eQTL support and sit in contact domains, not at specific regulatory loops.

## The NPAS3 loop (the one clean positive)

Reviewer-checked directly from `npas3_loop_probe.json`:

- Element bin (hg19 chr14:34,257,657, bin 3425) to NPAS3 promoter bin (hg19 chr14:33,403,602, bin 3340): **85-bin separation = 850 kb**.
- Contact = 13.56, versus a distance-matched background mean of 2.42 (n = 2,575 bin-pairs at the same separation): **obs/exp = 5.6, the 99.8th percentile** of same-distance contacts on chr14.
- This is the long-range enhancer-to-promoter loop the power-law structurally could not test (it penalised the 854 kb distance to near-zero). Matched contact promotes NPAS3 to **co-top ABC** (ABC 0.0207, tied with its promoter bin-mate ENSG00000289111 which shares the identical bin), just behind a proximal lncRNA ENSG00000287777 (105 kb, ABC 0.0212) whose contact is **exactly at expectation (obs/exp 0.96)** - i.e. proximity, no loop.

So Hi-C does not make NPAS3 the single ABC winner, but it does something the power-law could not: it shows the NPAS3-intron element physically contacts the NPAS3 promoter far above chance, while the gene that edges it on raw ABC has no loop at all. On loop strength, NPAS3 is the call. NPAS3 has no proximal brain eQTL (adult bulk brain, cell-type-mismatched), so this stays a fetal-progenitor-specific hypothesis, consistent with A9.

## The flagship shortlist, re-checked

| Variant | Host | Power-law top | Hi-C top (obs/exp) | Reading |
|---|---|---|---|---|
| chr14-33788719-A-G | NPAS3 | ENSG..87777 (105 kb) | ENSG..87777 (0.96), **NPAS3 co-top, loop obs/exp 5.6** | **NPAS3 loop confirmed**; keep NPAS3 as the target on loop strength |
| chr2-176638323-C-A | LINC01117 | LINC01116 (306 bp) | HOXD8 (13.6) | **Hi-C cannot resolve this**; see below |
| chr17-50200666-C-T | COL1A1 | COL1A1 (764 bp) | TMEM92-AS1 (4.1) | switch is 87 kb away, no eQTL, thin margin (1.06x); COL1A1 park stands |
| chr19-13151895-C-G | IER2 | STX10 (1.5 kb) | STX10 (same bin) | still a bidirectional-promoter tie IER2/STX10; unchanged |

**LINC01117 -> LINC01116 (the A9 flagship reassignment): Hi-C cannot adjudicate it.** LINC01116's promoter is 306 bp from the element - the *same 10 kb Hi-C bin* - so its obs/exp is undefined and 10 kb Hi-C has no power to confirm or deny a same-bin link. The Hi-C top instead goes to HOXD8 (508 kb, obs/exp 13.6), but HOXD8 is inside the HOXD Polycomb cluster, a domain that self-interacts strongly for reasons unrelated to enhancer activity - a textbook ABC false positive. So the honest position is: the A9 call (LINC01116, backed by 10 same-element brain eQTLs across 5 tissues, best p=2e-20) stands on distance + activity + eQTL; Hi-C at this resolution neither strengthens nor overturns it, and its raw top gene here is an artefact.

## The 8 triangulated links (the resource that survives)

Where the power-law top, the Hi-C top, and a brain eQTL all point at the same non-host gene, the target is well-supported from three angles. These 8 are all **proximal** (element-to-TSS 0.1-32 kb) with Hi-C contact at or near expectation (obs/exp ~1 or same-bin), meaning Hi-C confirms the distance call rather than adding a loop:

RALGPS2->ANGPTL1 (123 bp); host ENSR00001202083->ENSG00000258702 (22 kb, 5 tissues); LOC105371268->AKTIP (6 kb, 9 tissues, p=2e-15); ENSR00000288073->ZNF507 (5 kb, 3 tissues); Unknown->SNRK (13 kb); C4orf33->SCLT1 (3 kb); LOC105377921->PREP (20 kb); ENSR00000914768->APLN (32 kb). Six of these were already A9 power-law HIGH links; two (AKTIP, SCLT1) are new because the pseudocount/diagonal handling scored the proximal bins A9's power-law also favoured.

## Falsification (the skeptic check, done)

**Claim under test:** "matched Hi-C reassigns targets that distance could not, so the loop-driven switches are the real ABC edge."

**Strongest argument against:** naive bin-bin Hi-C contact is dominated by TAD/compartment structure, so a high-contact "switch" to a distal gene can be generic domain co-membership (or a Polycomb/structural hub), not a specific regulatory loop - and would have no independent support.

**Test result: the argument holds, and it is why the 18 loop-driven switches are not promoted.** All 18 have zero proximal brain eQTL; the strongest (HOXD8, obs/exp 13.6) is a known Polycomb self-interacting cluster; the switches skew to 500-900 kb where compartment contact dominates; and margins are thin (median ratio ~1.2x over the second gene). The obs/exp filter was added precisely to expose this, and it does. The claim does **not** survive as stated. What survives is narrower and defensible: at one locus (NPAS3) matched contact reveals a specific, distance-matched-significant long-range loop the power-law could not see; and the trustworthy target calls are the triangulated proximal ones, where Hi-C agrees with distance rather than overriding it.

**Second check - is the NPAS3 loop itself a structural artefact?** The obs/exp is computed against distance-matched background (2,575 bin-pairs at the same 85-bin separation across chr14), so it already controls for the generic distance decay. At the 99.8th percentile it is a genuine local contact enrichment, not the compartment floor. It remains cortex-progenitor (not pons/OPC) and bin-level (10 kb), so it is a strong hypothesis, not proof of regulation.

## Honest guardrails observed

- No reassignment percentage is headlined as a win; the 33%-changed figure is reported and then explained as mostly unsupported structural-contact switches.
- GZ is fetal *cortex* progenitors, not pons/OPC-specific - matched-ish, the same cortex->DMG regional caveat flagged elsewhere.
- Fetal Hi-C at 10 kb is bin-level; same-bin links (LINC01116, COL1A1, IER2) are below its resolution and it cannot adjudicate them.
- Contact partly co-varies with activity (ABC state-independence assumption is only approximate).
- Brain eQTL is adult bulk, proximity-biased and cell-type-mismatched, so an eQTL negative (NPAS3, the 18 switches) is a floor, not a verdict.
- Every link is a single-patient, private hypothesis to validate (CRISPRi of the element in an OPC-like line, read out candidate and host gene), not a proven target assignment. This does not out-claim AlphaGenome/Enformer/Malinois/the Pollard CNN-BiLSTM; it is target-gene context for the convergence layer.

## Artefacts
- `a9b_hic_target_table.tsv` - per-variant: host / nearest-TSS / power-law top / Hi-C top gene, distances, Hi-C obs/exp, ratios, eQTL support, and confidence tier (TRIANGULATED / LOOP-ONLY / HOST-CONFIRMED / AMBIGUOUS).
- `a9b_hic_comparison.png` - (A) where the Hi-C top gene agrees (power-law vs nearest-TSS vs host); (B) the NPAS3 locus, obs/exp vs distance, showing the 850 kb loop against the no-loop proximal lncRNA; (C) the 18 loop-driven switches, distance vs obs/exp, coloured by eQTL support (all blue = none supported).
- `a9b_headline_numbers.json`, `npas3_loop_probe.json` - reviewer-checkable numbers.
