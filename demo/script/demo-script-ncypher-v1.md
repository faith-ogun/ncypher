---
title: "NCypher — 3-minute submission demo script (v1)"
type: deliverable
status: draft
version: v1
last-reviewed: 2026-07-10
deliverable: demo-video
source: "First pass. Built from: the winning-hackathon-demo-video research + Anthropic-presentation-style research (both in docs/plan/demo-video-playbook.md), the honorable-mention Relay + Unravel example scripts, and NCypher's own work (the finding, the A2/A5/A7/A9 hardening, the delivery layer). Target audience: scientists (genomics / transcriptomics / protein / builders), NOT lay."
tags: [type/deliverable, status/draft, deliverable/demo-video, project/ncypher]
---

# NCypher — 3-minute demo script (v1)

**Hard target: 3:00 (Life Sciences hackathon caps the demo at <=3 min; judges stop at the cap).**
**Format:** mixed. `[CAM]` Faith on camera · `[SCREEN]` screen recording with OpenScreen zoom-ins ·
`[ANIM]` Remotion explainer snippet · `[CAP]` on-screen caption. Voiceover carries the narration;
footage carries the proof.
**Audience:** scientists who read model details cold (a first-author ML-genomics scientist, a
comp-bio PI, Anthropic's life-sciences leads). Real numbers with denominators; honesty as a credibility
multiplier; no lay analogy tax. One human sentence on why DMG matters, no more.
**The one thing they must remember:** a TF motif collapsing at the exact broken base, and one honest
number that proves it is real. Everything sets that up or pays it off.

> Word count of the VO below: ~340 spoken words. At ~150 wpm that is ~2:15 of talking over ~3:00 of
> footage, which is deliberate: the demo run and the artifacts play without narration on top.

---

## 0:00–0:12 · Cold open (the wow, no title card first)
`[ANIM: the ref-vs-alt saliency logo — a crisp TF motif collapsing at the exact variant base.]`
(source: `video/out/ncypher-finding.mp4` mechanism scene, or `ncypher-demo.mp4`)
`[CAP: "non-coding variant — a change in a DNA switch, not a gene"]`

> "This is a child's brain tumour with a thousand mutations in its DNA switches, and no way to know
> which three are worth a year in the lab."

(the motif breaks on the word "which")

## 0:12–0:24 · Name + one line
`[SCREEN: the NCypher mark, lower third; the collapsed logo still visible]`
`[CAP: "Built with Claude: Life Sciences · Researcher track"]`

> "NCypher tells you which one to validate first, and the mechanistic reason why, in a single agent
> call."

## 0:24–0:40 · The gap (problem, sharpened, not a lecture)
`[ANIM: the competitor comparison, revealed one row at a time]`
(source: `video/out/ncypher-strategy.mp4` or the consensus "coupling layer" beat)

> "Today you get a score from one tool, a motif guess from a second, evolutionary constraint from a
> third. None of them is in your tumour's cell type, and none of them is coupled. So you rank by gut."

## 0:40–0:50 · The spine (Pollard, said to Pollard)
`[CAM: Faith]` (or `[CAP]` large)
`[CAP: "prediction is cheap · validation is the bottleneck"]`

> "Katherine Pollard says prediction is cheap and validation is the bottleneck. So NCypher does not
> hand you a leaderboard. It hands you a decision."

## 0:50–1:58 · THE LIVE RUN in Claude Science (the centre of gravity, ~68s)
`[SCREEN: Claude Science, OpenScreen zoom-ins throughout. ★ NEEDS A CLEAN RECORDING — see shot list.]`
Narrate the decision, not the UI. Sub-beats, each with a punch-in:

1. `[zoom on the prompt]` one sentence typed:
   > "It starts with one sentence: triage the somatic non-coding variants in this cohort, tell me which
   > to validate first, and be honest about what does not hold up."
2. `[zoom on the plan + its confidence score]` → approve.
   > "It plans the work, and scores its own confidence, before it runs."
3. `[SCREEN: subagents fan out]` + `[ANIM 4s cutaway: the three-axis convergence]`
   (source: consensus convergence beat)
   > "Sub-agents fan out and call the NCypher skill across three independent axes: chromatin
   > accessibility, measured function, and evolutionary constraint."
4. `[SCREEN: clip 13 `13_clip_mcp-inspector-rich-bundle.mov` — the rich artifact rendering]`
   > "One call returns the picture, the ranked shortlist, and the mechanism — the motif and the exact
   > base — not three lines of text."
5. `[zoom: the reviewer agent re-deriving the number]` — THE Claude-Use crown, hold on it.
   > "Then a second agent checks the first: it re-derives the headline number from the raw data before
   > anyone trusts it."
6. `[zoom: the go/no-go memo]`
   > "And it hands back a memo — validate this variant first, here is the experiment that settles it,
   > here is what would kill it."

## 1:58–2:20 · Credibility + the honest-negative "what surprised us" (Depth)
`[SCREEN: clip 14 `14_clip_dashboard-finding-walkthrough.mov` or `ncypher-validation.mp4` — freeze on
the caQTL bar and the out-of-domain flag]`

> "Validated where it should be: it recovers accessibility QTLs at seven-and-a-half times the base
> rate, in the matched fetal cell type. And here is what surprised us — it is null on the reporter-assay
> variants, because those measure different biology. So we never collapse the axes into one number."

`[MONTAGE ~6s: the four hardening explainers flashing their verdicts]`
(source: `ncypher-a2.mp4` SURVIVES · `ncypher-a5.mp4` partial · `ncypher-a7.mp4` independent ·
`ncypher-a9.mp4` honest resource)

> "We tried to break our own finding four times, and reported it honestly each time — including
> softening our own lead candidate when an independent model disagreed."

## 2:20–2:40 · Impact + the scale fan-out
`[SCREEN: clip 08 `08_shot_modal-logs.png` / a parallel fan-out visual; `ncypher-discovery.mp4`]`

> "One variant is a demo. This triages an entire cohort in parallel — diffuse midline glioma:
> paediatric, uniformly fatal, no targeted therapy. Why stop at one patient?"

## 2:40–3:00 · Close
`[CAM: Faith]` → `[logo card: "decode the non-coding" · github.com/... · Apache-2.0]`

> "We did not use Claude to build an app. We built the thing Claude Science is for — a research
> partner that ranks what to test next, shows you the mechanism, and tells you when it is wrong.
> Decode the non-coding."

---

## Where each judging criterion lands (so a judge ticks it without being told)
- **Demo 30%** → the 0:50–1:58 live run (a variant in, a decision out, on screen).
- **Claude Use 25%** → plan + confidence, sub-agent fan-out, the skill/MCP call, and the reviewer
  re-deriving the number (an agent checking an agent). This is why the demo lives *inside* Claude
  Science, not a standalone app.
- **Impact 25%** → the DMG framing + the cohort fan-out (2:20–2:40).
- **Depth 20%** → the caQTL number + the honest negative + the four-way hardening montage (1:58–2:20).

## Assets — HAVE (reuse these)
- Saliency collapse (hook): `video/out/ncypher-finding.mp4`, `ncypher-demo.mp4`.
- Competitor/coupling comparison: `ncypher-strategy.mp4`, `ncypher-consensus.mp4`.
- Three-axis convergence cutaway: `ncypher-consensus.mp4` (convergence beat), `ncypher-demo.mp4`.
- **Rich MCP bundle:** `demo/assets/13_clip_mcp-inspector-rich-bundle.mov`.
- **Dashboard walkthrough:** `demo/assets/14_clip_dashboard-finding-walkthrough.mov`.
- caQTL / validation: `ncypher-validation.mp4`, the dashboard.
- **Hardening montage:** `ncypher-a2.mp4` / `-a5` / `-a7` / `-a9`.
- Fan-out / scale: `demo/assets/08_shot_modal-logs.png`, `ncypher-discovery.mp4`.
- (Optional Depth/Claude-Use B-roll) reproducibility: `15_clip_notebook-reproduce.mov`,
  `12_clip_ci-claude-verify-reproduces.mov`; context harness: `07_clip_obsidian-graph-context-harness.mov`,
  `09_clip_five-subagents-obsidianify.mov`.

## Assets — NEED (record these; "video does not exist yet, but…")
- ★ **The clean Claude Science hero run** as a single OpenScreen-zoomed take: one sentence in → plan +
  confidence → sub-agent fan-out → the rich artifact → the reviewer re-deriving the number → the
  go/no-go memo. This is the 68-second centre; everything else is B-roll around it. (Raw material may
  exist in the unnamed Claude Science screen recordings, but a purpose-recorded hero run is best.)
- **Faith on camera** for the 0:40 spine line and the 2:40 close (a human to attach the work to).
- (Optional) a moving cohort fan-out shot; the modal-logs still works if not.

## Cut order if over 3:00 (never cut the live run, the honest negative, the memo, or the close)
1. Trim the hardening montage to ~3s (one verdict card). 2. Cut the gap `[ANIM]` to a single spoken
line. 3. Drop the optional reproducibility/context B-roll. 4. Tighten every zoom; cut all dead screen
time (spinners, typing).

## Production notes (from the research)
- Best mic in the room; re-record any muddy line (audio quality is the cheapest, biggest credibility win).
- Zoom in on every number and the GO/NO-GO verdict; never show a full screen with the result buried.
- Export 1080p, upload, then **watch it logged-out** to confirm access + captions + not age-gated.
- End at or under 3:00 with the close intact.

## Change log
- **v1 (2026-07-10):** first pass. Spine = Pollard's validation-bottleneck + the one-sentence-in /
  go-no-go-memo-out arc + the honest-negative "what surprised us" + agent-checks-agent. To be revised as
  A8 / A9b land and as footage is recorded.
