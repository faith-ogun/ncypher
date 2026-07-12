---
title: "NCypher — 3-minute submission demo script (v3)"
type: deliverable
status: draft
version: v3
supersedes: demo-script-ncypher-v2.md
last-reviewed: 2026-07-10
deliverable: demo-video
tags: [type/deliverable, status/draft, deliverable/demo-video, project/ncypher]
---

# NCypher — demo script (v3)

**What changed from v2 (Faith's notes, folded in):**
1. **First person ("I") throughout** the spoken script. It is one person; "we" reads wrong. (In the
   100-200 word written summary we may switch to passive "NCypher is...", TBD.)
2. **No abstract cold open.** Cut "a child's brain tumour, a thousand mutations". Open straight on the
   human + the DMG gravity (Medkit-style), over a proper brain animation, Faith small in a corner.
3. **Impact moved to the START** and **corrected**: DMG is NOT "no targeted therapy" any more. It got its
   FIRST targeted therapy (dordaviprone / Modeyso) in Aug 2025, but that is not a cure. This makes the
   "we still need to know what to test next" motivation stronger.
4. **Facts verified** (see `docs/plan/demo-script-facts.md`). The Pollard "prediction is cheap" line is
   NOT a real quote, so it is presented as OUR framing of her lab's thesis, never in quotation marks.
5. **Name-drops corrected** (see `docs/plan/demo-name-drop-references.md`). Do NOT say "the Corces model":
   ChromBPNet is Kundaje + Montgomery (Stanford); data is Trevino et al. (Cell 2021). The strong, honest
   Gladstone ties are **Pollard** (phyloP + Zoonomia + lentiMPRA) and **Whalen** (lentiMPRA co-first, a
   likely judge). Every axis and dataset gets a **reference card on screen** (paper + year).
6. **Honesty on the footage:** the Claude Science prompts were big staged prompts, not one sentence, so
   the script no longer claims "one sentence in" as fact. The single-sentence hero fan-out is aspirational
   (needs A3/A4 + a purpose-recorded run).
7. **Reference cards + name-drops are shown IN THE VIDEO**, not just spoken, consistent placement
   (bottom of each axis card / a top-right calling card for datasets). `[REF: ...]` marks each.
8. Hardening becomes **six** once A3 + A4 land (hold at four until then). Falsification framing = Popper,
   not attributed to Sukrit Silas. A single Boris Cherny "I write loops" quote is available for the
   harness beat (verified).

> **Length:** do not worry about the 3:00 cap (Faith's call). Better slightly long with the story intact.

---

## THE CUT

### 0:00-~0:12 · Open: who + why DMG matters (the DMG scene + CAM)
`[SCENE: demo/scenes/01-dmg-open.mp4 - the DMG molecular landscape with the survival stats (~11 mo, <10%
at 2y, <1% at 5y) and the dordaviprone line ALL on screen. Faith's real cam composited bottom-right (the
scene's own cam corner is removed for exactly this).]`
`[SHOW, DON'T TELL: the survival figures and the 22% are on screen now, so the VO no longer recites them.
It keeps the framing + one spoken emotional anchor ("uniformly fatal"). Shortened from ~22s to ~12s.]`

> "I'm a computational cancer-genomics researcher, and I usually work on breast cancer. For this I wanted
> to challenge myself with a rare, underserved one, in the spirit of Anthropic's focus on neglected
> diseases: diffuse midline glioma. It is uniformly fatal, and its first targeted therapy arrived only in
> 2025, without curing anyone. So what to test next still matters enormously."
`[NOTE: Faith's PhD is BREAST-CANCER epigenetics (SCARLET); DMG is the hackathon/Onkydra work. Do not
  claim DMG is her field. Say "neglected DISEASES" (Anthropic's framing), never "neglected cancers". The
  survival stats + dordaviprone detail are SHOWN in scene 01, not spoken (show, don't tell). Survival uses
  "make it to" language on screen, never "will not be alive".]`

(facts: `docs/plan/demo-script-facts.md` items 2, 3. DIPG ~11mo median, ~10% at 2y, <1% at 5y;
dordaviprone/Modeyso FDA accelerated approval 6 Aug 2025, 22% ORR, not curative.)

### 0:22-0:42 · The problem (CAM + the tools animation)
`[SCENE: demo/scenes/01c-problem.mp4 (16s) - three siloed tools each giving a partial answer (a score in
K562/HepG2, a motif guess / PWM annotator, phyloP genome-wide), "not coupled" breaks between them, and
two honest flags (none in your tumour's cell type · none coupled). Bottom-right kept CLEAR for Faith's cam.]`
`[REF bottom-LEFT (bottom-right is the cam): Nagaraja et al., Cancer Cell 2017 - DMG depends on
super-enhancer-driven regulatory programmes (the verified "drivers are non-coding" paper; it is Cancer
Cell, NOT Nature Genetics - the script's earlier "e.g. Nature Genetics" was a placeholder).]`

> "In DMG the drivers hide in the non-coding genome, the switches, not the genes. And today you get a
> score from one tool, a motif guess from another, and evolutionary constraint from a third. None of them
> are in your tumour's cell type, and none of them are coupled. And validating even a single non-coding
> variant at the bench is slow and expensive, so the real bottleneck was never prediction, it's deciding
> which handful are worth it. Exactly the pitfall the Pollard lab has spent years warning about."

`[NOTE: never say "rank by gut" - scientists do not; validation effort is the point.]`
`[REF (validation is the bottleneck): Gasperini, Tome & Shendure, "Towards a comprehensive catalogue of
validated and target-linked human enhancers", Nat Rev Genet 2020 (hundreds of thousands nominated, a
handful validated).]`
`[REF (the ML-pitfall framing): Whalen, Schreiber, Noble, Pollard, Nat Rev Genet 2022. OUR framing, NOT a
Pollard quote.]`

### 0:42-0:52 · Name + one line
`[ANIM: NCypher mark]` `[CAP: "Built with Claude: Life Sciences · Researcher track"]`

> "NCypher does three things in one agent call: it tells you which non-coding variant to validate first,
> it shows the exact base and motif that break, and it flags, honestly, when the models disagree. Coupled,
> so you get to the bench sooner."
`[NOTE: three distinct NCypher-unique things (not two), and the coupling is the point - not redundant with
  the problem beat's separate score/motif/constraint tools.]`

### 0:52-1:40 · The spine: how I found NPAS3 (the consensus story)
`[ANIM: the discovery funnel]` `[REF top-right calling-card: the cohort]`

1. `[ANIM: funnel 10,869 -> 164]`
   `[REF card 1: cohort - OpenPedCan v15 / OpenPBTA (Shapiro et al., Cell Genomics 2023), 152 patients]`
   `[REF card 2: why not recurrence - Rheinbay et al., Nature 2020 (PCAWG, 2,658 genomes): recurrence
     alone over-calls artefacts, TERT-dominated after honest background modelling]`
   > "I started with ten thousand eight hundred and sixty-nine somatic non-coding variants across one
   > hundred and fifty-two diffuse-midline-glioma patients. Naive recurrence just finds artefacts, so I
   > ranked by function against a matched background."
2. `[ANIM: three axes light up. Chromatin column carries a "who built it" attribution box (ChromBPNet =
   Kundaje architecture · data = Trevino/Greenleaf, Cell 2021 · weights = Corces lab, Gladstone). Function
   column carries a "used first" box: the 164 developing-cortex DAVs were the first validation benchmark,
   gave an honest negative, and redirected us to caQTLs. No "not measured here" anywhere.]`
   > "The method couples three independent axes. Chromatin accessibility, from the developing brain.
   > Evolutionary constraint, phyloP and Zoonomia. And measured function, a developing-cortex MPRA. The MPRA
   > was actually where I started, and it gave an honest negative that redirected me to caQTLs, the right
   > ground truth. So I promote where chromatin and constraint agree."
   `[NOTE: lab name-drops (Corces, Pollard, Ahituv) are NOT spoken - they are on the axis cards + papers
     on screen (show, don't tell). This keeps the VO ~20 words shorter without losing the Gladstone credit.]`
   `[HONESTY (do not skip): the MPRA negative is a MODALITY mismatch - ChromBPNet predicts chromatin
     ACCESSIBILITY, the MPRA measures reporter ACTIVITY (Pollard trained a SEPARATE model, r~0.82). It is
     NOT evidence that "DMG is epigenetic" - do not say that; Pollard/Whalen built both models and will
     catch it. The finding converges on TWO axes (chromatin + constraint); MPRA/function was the FIRST
     validation benchmark, not a per-variant scoring axis here. Never say "all three converge" for the hits.
     The reusable theme: a negative can be a positive - it pointed us to the right ground truth.]`
   `[REF cards + boxes (on-screen axis columns):
     - chromatin: lab "Ryan Corces lab · Gladstone" / method "developing-brain ChromBPNet" /
       box "ChromBPNet = Kundaje architecture · data = Trevino/Greenleaf (Cell 2021) · weights = Corces lab (the model we ran)"
     - constraint: lab "Katherine Pollard · Gladstone" / "phyloP (2010) + Zoonomia (2023)" (two papers, full)
     - function: lab "Pollard & Ahituv labs" / method "developing-cortex lentiMPRA" /
       box "used first: the 164 DAVs were our first benchmark; an honest negative (reporter activity != accessibility) that redirected us to caQTLs · tag: a negative that sharpened the science"]`
   `[PROD NOTE (Corces, reconciled): Faith runs the pre-trained brain models via the Corces lab Resources
     page and Corces (Gladstone) is a co-author, so "Ryan Corces lab · Gladstone" IS a fair Gladstone
     name-drop for the model resource. Keep the method credit to Kundaje and the data to Trevino alongside
     it. The other strong Gladstone ties are Pollard (constraint + function) and Whalen (MPRA co-first).]`
3. `[ANIM: 164 converged; NPAS3 rises]` `[SCREEN option: a fast montage of Faith scrolling real NPAS3
   literature windows, with a small "crawl" of citations, to show it is a real, credible lead]`
   > "A hundred and sixty-four converged. And one kept rising to the top: NPAS3, a neurodevelopmental
   > tumour suppressor, where a switch inside the gene loses accessibility at the exact conserved base."
4. `[SCREEN: the linked-note graph, fast-forward]` (clip `09_clip_obsidian-graph-view.mov`) + `[ANIM: version log]`
   > "Every step is kept honest in a versioned second brain, a context harness so the work survives long
   > sessions. And when AlphaGenome disagreed on NPAS3, I did not bury it, I downgraded my own lead and said
   > so, and I looked at why. AlphaGenome predicts reference-context tracks, not the patient's tumour cell
   > state, which is likely why it disagreed. The disagreement is signal too."
   `[INSET (Homeward-style pop-up, appears then leaves): "Why AlphaGenome disagreed - it predicts
     reference-context tracks (ENCODE, GTEx, FANTOM), not the tumour cell state." NOTE: not "normal tissue"
     - AlphaGenome's panel includes cancer cell lines (K562, HepG2); the honest point is it has no
     paediatric-DMG / fetal-OPC context.]`
   `[NOTE: no Boris Cherny "loops" attribution - Faith does not write loops; keep "second brain / context
     harness" generic and unattributed.]`

### 1:40-2:25 · How it runs: one workflow, the real surfaces
Narrate the loop. Labels ONLY for non-obvious surfaces (e.g. GitHub Actions), never "this is Claude Science".
1. `[SCREEN: Claude Science, the staged task + the plan]` (clip `27` @00:30)
   > "Here is the real thing running in Claude Science. I hand it a structured brief, it plans the work,
   > and it scores its own confidence before it runs."
   `[HONEST: our prompts are big staged briefs, not one sentence. Do not claim one sentence.]`
2. `[SCREEN COLLAGE: left = MCP Inspector (clip 13); right = the same tool being called in Claude Science]`
   > "Sub-agents call the NCypher tool. One call returns the ranked shortlist, the mechanism, the motif,
   > the exact base, and the saliency picture, not three lines of text."
3. `[SCREEN: the reviewer agent re-deriving the headline number]` (clip `27` @20:00) - hold, no zoom.
   > "Then a second agent re-derives every headline number from the raw files. An agent checking an agent."
4. `[SCREEN: real Modal dashboard]` (clip `22`) + `[SCREEN: GitHub Actions PASS, labelled]` (clip `12`)
   `[REF: Won et al., Nature 2016, fetal-brain Hi-C, for the Modal Hi-C job]`
   > "The heavy scoring and the fetal-brain Hi-C run on Modal. And on every push, GitHub Actions has Claude
   > re-derive the headline number from raw data, so the finding stays reproducible."
5. `[SCREEN: the React dashboard]` (clip `14`)
   > "And if you would rather see it than call it, the finding is laid out on a static, open-source page,
   > the go/no-go memo, the three axes, the mechanism."
   `[HONEST: the dashboard is a STATIC showcase of THIS finding (a github.io site), NOT a live backend that
     re-renders a per-user analysis (github.io cannot). The interactive, variant-agnostic part is the MCP
     tool in Claude Science; the dashboard is the finding presented for humans. Do not imply it auto-renders
     any user's analysis. PROD: keep it current with A2/A8/A9; add the public URL once the repo is public
     and Pages deploys.]`

### 2:25-2:45 · Break my own finding (Claude Science sessions)
`[SCREEN: collage of the hardening sessions, each with its badge. SIX now (A2 confounds · A3 context-
specificity · A4 motif rediscovery · A5 second opinion · A7 conservation · A9b real Hi-C). Hold on the
badges, no zoom.]`

> "A finding is only as strong as the tests that could have broken it. So I tried to break mine six times,
> each its own Claude Science session: confounds, whether the signal is really brain-specific, whether the
> model learned real motifs and not a shortcut, an independent second opinion, whether the axes are truly
> independent, and real fetal-brain Hi-C. It survived, and where a test only partly held, I reported it
> honestly and softened my own lead."
`[NOTE: the falsifiability idea is Popper's; do not attribute the aphorism to Sukrit Silas.]`

### 2:45-3:05+ · Scale + close
`[SCREEN/ANIM: the cohort fan-out]`
`[PROD: clarify what is parallel. If we run a real sub-agent sprawl (one agent per patient/variant), show
it; if not yet, say "triage the whole cohort" and mark the per-patient sprawl as the aspirational hero.]`

> "One variant is a demo. The same engine triages the whole cohort. In a rare disease where samples are
> scarce, every extra validated lead counts. I built one of the things Claude Science is for: a research
> partner that ranks what to test next, shows the mechanism, and tells you when it is wrong."
`[NOTE: "one of the things" - Claude Science is a horizontal production platform, not only a research
  partner; do not say "the thing". "decode the non-coding" may appear as an on-screen VISUAL but is never
  spoken.]`
`[ANIM: logo card - github.com/faith-ogun/ncypher · Apache-2.0 (no "decode the non-coding" catchphrase;
  no "I did not build an app"; no "industry skips" claim - dordaviprone launched Aug 2025; no Anthropic
  neglected-disease reference).]`

---

## Judging criteria (where each lands)
- **Demo 30%** -> 1:40-2:25 the workflow on real surfaces.
- **Claude Use 25%** -> plan + confidence, sub-agent calls, the MCP, the reviewer re-deriving, the CI gate,
  and the hardening as separate Claude Science sessions.
- **Impact 25%** -> the DMG open (survival + dordaviprone-but-not-a-cure) + the cohort scale (a rare,
  small-sample disease where every validated lead counts).
- **Depth 20%** -> the consensus spine to NPAS3, the version log, the six-way (soon) hardening, honest
  name-drops with citations on screen.

## Reference cards to show on screen (from `demo-name-drop-references.md`)
- Cohort: **OpenPedCan v15 / OpenPBTA (Shapiro et al., Cell Genomics 2023)** - 152 patients.
- Chromatin: **ChromBPNet (Marderstein, Kundu et al., Nat Genet 2026)**; data **Trevino et al., Cell 2021**.
- Constraint: **phyloP (Pollard et al., Genome Res 2010)**; **Zoonomia (Science 2023)**.
- Function: **lentiMPRA (Deng, Whalen ... Pollard, Science 2024)**.
- Hi-C: **Won et al., Nature 2016** (GSE77565).
- DMG driver-in-non-coding: pick the on-screen paper Faith supplies (Nature Genetics DMG paper).
Faith will provide the paper screenshots; tell her which, she drops them into `video/public/refs/`.

## Assets Faith still supplies (reel cannot fabricate these well)
- Her **cam** (open + close). The **brain/DMG animation** brief (I build the Remotion motion).
- **Paper screenshots** for the reference cards.
- The **NPAS3 evidence montage** (sped-up literature scroll + citation crawl).
- The **MCP-Inspector + Claude-Science dual collage** footage (or I fake the split with the two clips).

## Change log
- **v3 (2026-07-10):** first person; cut the abstract cold open; impact-first with corrected dordaviprone
  framing and verified DIPG survival; Pollard as framing not quote; corrected name-drops (not "Corces
  model"; Pollard + Whalen are the Gladstone ties); reference cards on screen; honest about staged prompts;
  Popper (not Silas) for falsification; Cherny "loops" quote available; hardening -> six after A3/A4.
  Supersedes v2 (kept).
