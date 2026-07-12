---
title: "NCypher — 3-minute submission demo script (v2)"
type: deliverable
status: draft
version: v2
supersedes: demo-script-ncypher-v1.md
last-reviewed: 2026-07-10
deliverable: demo-video
tags: [type/deliverable, status/draft, deliverable/demo-video, project/ncypher]
---

# NCypher — 3-minute demo script (v2)

**What changed from v1 (why this exists):** v1 was a montage of proof (MCP, dashboard, CI, hardening)
but it never told the viewer *how the pieces fit into one story*, and it had no **consensus / discovery
storyline** — the thing that makes this Researcher-track, not Builder-track. v2 fixes three things:

1. **A spine: how NCypher found NPAS3.** The middle of the film is now the rigorous journey to a single
   candidate (10,869 variants to a convergence-backed shortlist led by NPAS3), told as a story, with the
   honesty (nulls, disagreements) as the credibility engine. This is the "consensus finding" Faith flagged
   as missing.
2. **One clear workflow that connects every surface**, so the viewer always knows *where they are and why*:
   Claude Science is the cockpit; the MCP is the tool the agent calls (and MCP Inspector proves it works);
   Modal is the muscle; GitHub Actions is the conscience; the React dashboard is the finding **rendered**,
   not a standalone app; Obsidian is the lab notebook that kept the science honest.
3. **The iteration line** ("we versioned our own claims, and changed one when the evidence said so") and the
   **Claude Science placement** (the four-way hardening is literally four Claude Science sessions — that is
   when we are "in Claude Life Sciences").

> **Rule borrowed from the April winner (Medkit):** open on the human and the problem for ~25-30s, then
> show, don't tell. The ONLY time you leave your own surfaces is to show *how it was built with Claude*.
> Everything else is the real thing on screen. We keep that discipline and add the rigour spine they lacked.

**Format:** `[CAM]` Faith on camera · `[SCREEN]` real screen recording (labelled "you are here" +
cam corner) · `[ANIM]` Remotion card on white · `[CAP]` caption. Voiceover carries narration; footage
carries proof.

**Audience:** scientists who read model details cold (an ML-genomics first author, a comp-bio PI,
Anthropic's life-sciences leads). Real numbers with denominators. Honesty as a credibility multiplier.

**The one thing they must remember:** a TF motif collapsing at the exact broken base — and the honest,
convergence-backed path that made NPAS3 the one variant worth validating first.

**Length:** target ~3:00, and **it is fine to run slightly over** (Faith's call: better a touch long with the
consensus story intact than short and thin). Hard ceiling only if the platform enforces one.

---

## THE STORY LOGIC (read this once; it is why the cut hangs together)

NCypher is one workflow with five surfaces. Narrate it as a single loop, never as a tour of apps:

- **Claude Science = the cockpit.** The researcher types one sentence. Claude Science plans it, scores its
  own confidence, and fans out sub-agents that call the NCypher tool. This is where a human actually sits.
- **The NCypher MCP = the tool the agent calls.** **MCP Inspector** is shown for one reason only: to prove
  the tool is real and returns a rich bundle (shortlist + mechanism + saliency), not three lines of text.
- **Modal = the muscle.** The heavy scoring (ChromBPNet across 10,869 variants) and the fetal-brain Hi-C run
  on Modal in the cloud. Use the REAL Modal dashboard footage (audit-confirmed: clip `07`; NOT the VS Code
  still `08`).
- **GitHub Actions = the conscience.** Every push, an agent re-derives the headline number from raw data.
  A finding you cannot reproduce is not a finding.
- **The React dashboard = the finding, rendered.** This is the honest answer to "is this a standalone app?"
  It is **not** a product a user logs into; it is the analysis made legible — the go/no-go memo, the three
  axes, the mechanism, the hardening — the same result the agent computed, shown for a human to read and
  present. It ships in the repo; you open it from the analysis. (No Firebase/Firestore needed: there is no
  backend or user data. If a public link is wanted, a static build on GitHub Pages / Vercel is a 5-minute,
  free deploy — optional, not part of the science.)
- **Obsidian = the lab notebook.** The linked-note graph is how the rigour was organised: every claim,
  its evidence, and its version history. Shown briefly (fast-forward) as proof the science was kept honest.

**When are we "in Claude Life Sciences"?** Twice, clearly: (1) the hero run (cockpit, plan+confidence,
reviewer, memo); (2) the **four-way hardening collage** — those four stress tests (A2, A5, A7, A9b) were each
run as a Claude Science session, so the quad-split IS four Claude Science windows working at once.

---

## THE CUT

### 0:00–0:10 · Cold open (the wow, no title card)
`[ANIM: the ref-vs-alt saliency logo — a crisp TF motif collapsing at the exact variant base]`
`[CAP: "non-coding variant — a change in a DNA switch, not a gene"]`

> "A child's brain tumour. A thousand mutations in its DNA switches. No way to know which three are worth a
> year at the bench." (the motif breaks on "which")

### 0:10–0:34 · Who + the problem (the human, ~24s — the Medkit-style open)
`[CAM: Faith]`

> "I'm Faith, a computational cancer-genomics first year PhD student in Dublin. In paediatric diffuse midline glioma the drivers hide in the non-coding genome — the switches, not the genes. And today you get a score from one tool, a motif guess
> from a second and evolutionary constraint from a third. None are in your tumour's cell type, and none of them
> are coupled. So you rank by gut. Katherine Pollard puts it best: prediction is cheap, validation is the
> bottleneck."

### 0:34–0:44 · Name + one line
`[ANIM: NCypher mark]` `[CAP: "Built with Claude: Life Sciences · Researcher track"]`

> "NCypher tells you which non-coding variant to validate first, and the mechanistic reason why — in a
> single agent call, so you can get to the bench as soon as possible to accelerate medicines to patients"

### 0:44–1:30 · THE SPINE: how NCypher found NPAS3 (the consensus story, ~46s)
This is the heart. Narrate the *journey to one candidate*, honesty included.
`[ANIM: the discovery funnel — 10,869 somatic non-coding variants]` then `[SCREEN/ANIM cutaways as noted]`

1. `[ANIM: the funnel]`
   > "We started with 10,869 somatic non-coding variants across 152 diffuse-midline-glioma patients. Naive
   > recurrence just finds artefacts — so we ranked by function, calibrated against a matched background."
2. `[ANIM: the three orthogonal axes light up]` (source: consensus convergence beat)
   > "Then three independent axes have to agree: chromatin accessibility, from a ChromBPNet model in the
   > matched fetal-OPC cell type, from Ryan Corces lab; evolutionary constraint, from Katie Pollard's Zoonomia; and measured reporter function.
   > We promote a variant only where all three converge."
3. `[ANIM: 164 converged; NPAS3 surfaces as the lead]`
   > "One hundred and sixty-four converged. And one kept rising to the top: NPAS3 — a neurodevelopmental
   > tumour suppressor — where a switch inside the gene loses accessibility at the exact conserved base."
4. `[SCREEN: Obsidian graph, fast-forward]` (audit-confirmed: clip `09`) + `[ANIM: the version log]`
   > "Every step is in the lab notebook, versioned. And when an independent model disagreed on NPAS3, we did
   > not bury it — we downgraded our own lead and said so. The disagreements can also be signal." Context Harnesses to allow work to persist even in high context session, second brain, Bories Cherny.

### 1:30–2:18 · HOW IT RUNS: one workflow, five surfaces (~48s)
Narrate the loop, not a tour. Each `[SCREEN]` carries a "you are here" label.
1. `[SCREEN: Claude Science — the typed one-sentence task, then the plan + its confidence score]`
   > "Here is the whole thing running. In Claude Science, one sentence: triage this cohort, tell me what to
   > validate first, and be honest about what does not hold up. It plans the work and scores its own
   > confidence before it runs."
2. `[SCREEN: sub-agents fan out]` (clip `05`) → `[SCREEN: MCP Inspector, the rich bundle]` (clip `13`)
   > "Sub-agents fan out and call the NCypher MCP tool. One call returns the picture, the ranked shortlist, and
   > the mechanism — the motif and the exact base — not three lines of text."
3. `[SCREEN: the reviewer agent re-deriving the headline number]` — hold on it (the Claude-Use crown).
   > "Then a second agent checks the first, re-deriving the headline number from the raw data."
4. `[SCREEN: real Modal dashboard/logs]` (clip `07`) + `[SCREEN: GitHub Actions green PASS]` (clip `12`)
   > "The heavy scoring and the fetal-brain Hi-C run on Modal. And on every push, CI re-verifies the number,
   > so the finding stays reproducible."
5. `[SCREEN: the React dashboard — the go/no-go memo, the three axes, the mechanism]` (clip `14`)
   > "And the same analysis renders here, for a human to read and present: validate NPAS3 first, here is the
   > experiment that settles it, here is what would kill it." compeltely open and live in the GitHub repo.

### 2:18–2:40 · Break our own finding — four Claude Science sessions (~22s)
`[SCREEN: 2x2 collage — four Claude Science windows: A2 SURVIVES · A5 PARTIAL · A7 INDEPENDENT · A9b LOOP CONFIRMED]`
(this is the honest "when are we in Claude Life Sciences" payoff; figures a2/a5/a7/a9b as the artifacts)

> "We tried to break our own finding four times, each as its own Claude Science session — confounds,
> an independent second opinion, whether the axes are really independent, and real fetal-brain Hi-C. It
> survived three, and the one that only partly held, we reported honestly."

### 2:40–3:00+ · Impact + close
`[CAM: Faith]` → `[ANIM: logo card — "decode the non-coding" · github.com/... · Apache-2.0]`

> "Diffuse midline glioma is paediatric, uniformly fatal, and has no targeted therapy. One variant is a
> demo — this triages a whole cohort in parallel. We didn't use Claude to build an app. We built the thing
> Claude Science is for: a research partner that ranks what to test next, shows you the mechanism, and tells
> you when it is wrong. Decode the non-coding."

---

## Where each judging criterion lands
- **Demo 30%** → the 1:30–2:18 workflow loop (a sentence in, a decision out, on real surfaces).
- **Claude Use 25%** → plan + confidence, sub-agent fan-out, the MCP call, the reviewer re-deriving the
  number, and the four-way hardening as four Claude Science sessions.
- **Impact 25%** → the DMG framing + the cohort fan-out.
- **Depth 20%** → the consensus spine (convergence to NPAS3), the version log, and the honest hardening.

## Asset mapping (AUDIT-CORRECTED — the source filenames were wrong)
Frame-by-frame audit (2026-07-10) corrected the swaps. Use these roles:
- **Real Modal dashboard** = `07_clip_modal-dashboard-apps-logs-storage.mov` (00:00-00:09 apps list,
  00:18-00:25 storage) or `22_clip_modal-dashboard-deploy-logs-usage.mov` (richer: metrics, logs,
  $0.65 usage; modal.com view starts ~00:04). Do NOT use `08_shot_claude-code-five-subagents-obsidianify.png`
  (that is VS Code, not Modal).
- **Obsidian graph** = `09_clip_obsidian-graph-view.mov`. Best: 00:00-00:04 (node highlighted, links lit),
  00:10-00:16 (settled graph).
- **MCP Inspector** = `13_clip_mcp-inspector-rich-bundle.mov` (correct).
- **React dashboard** = `14_clip_dashboard-finding-walkthrough.mov` (correct).
- **GitHub Actions CI** = `12_clip_ci-claude-verify-reproduces.mov` (correct). Note the still `11` shows
  mixed green/red runs; the clip `12` shows the green PASS log — use the clip.
- **Notebook reproduce** = `15_clip_notebook-reproduce.mov` (correct).
- **Claude Code subagents** = `05_clip_claude-use-research-agents.mov` (correct; best 00:20-00:45).
- **Claude Science hero run** (plan+confidence, reviewer, memo) and the **four A-session windows** =
  from the long raw recordings (`2026-07-*.mov`) — exact timestamps from the audit (pending long-clip agents).
  THIS IS THE KEY GAP TO FILL for the 1:30 cockpit beat and the 2:18 collage.
- Saliency hook, convergence, funnel, version log = Remotion (`ncypher-finding.mp4`, `ncypher-consensus.mp4`).

## What we still NEED to record
- A clean `[CAM]` take of Faith for 0:10–0:34 and the close.
- If the long recordings do not contain a clean Claude Science hero run (plan → reviewer → memo) or clean
  Modal logs, record a short purpose-built take of each.

## Change log
- **v2 (2026-07-10):** added the consensus/NPAS3 spine; recast the middle as one workflow across five
  surfaces with explicit "where you are / why"; reframed the dashboard as the finding rendered (not a
  standalone app; no Firebase needed); placed Claude Science explicitly (hero run + the four-session
  hardening collage); added the versioning/"changed our own claim" line; corrected the asset mapping after
  a frame-by-frame audit found the source filenames were wrong (07=Modal, 09=Obsidian, 08=VS Code).
  Supersedes v1 (kept for provenance).
