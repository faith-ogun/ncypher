---
title: "NCypher demo — asset manifest (renamed to true content)"
type: reference
status: current
last-reviewed: 2026-07-10
tags: [type/reference, status/current, deliverable/demo-video, project/ncypher]
---

# NCypher demo — asset manifest

> [!note] Files renamed 2026-07-10 to match their TRUE content.
> A frame-by-frame audit (5 agents) found the original names were wrong in three cases and the raw
> recordings had timestamp-only names. `demo/assets/` is now named by what each file actually shows.
> The rename log (old -> new) is at the bottom. `demo/assets/` is gitignored (not committed).

## Curated clips + stills (01-15)

| File | Content | Category | Best segments |
|---|---|---|---|
| `01_shot_discovery-framing.png` | Claude Code CLI: flagship hypothesis + gating papers | ClaudeCode | still |
| `02_clip_building-the-brief.mov` | Claude Code: finishing the brief PDF (static terminal) | ClaudeCode | 00:00-00:06 |
| `03_clip_figures-rebrand-a.mov` | Claude Code: savefig caQTL fig, re-render saliency | ClaudeCode | 00:03-00:10 |
| `04_clip_figures-rebrand-b.mov` | Claude Code: rebrand coverage checklist | ClaudeCode | 00:10-00:20 |
| `05_clip_claude-use-research-agents.mov` | Claude Code: parallel research subagents + web searches | ClaudeCode | **00:20-00:45** |
| `06_shot_claude-use-and-demo-concept.png` | Claude Code: the demo storyboard note | ClaudeCode | still |
| `07_clip_modal-dashboard-apps-logs-storage.mov` | **Modal** dashboard (apps/logs/storage, ncypher-score fns) | **Modal** | 00:00-00:09, 00:18-00:25 |
| `08_shot_claude-code-five-subagents-obsidianify.png` | **VS Code**: 5 subagents "obsidian-ify" (NOT Modal) | ClaudeCode | still |
| `09_clip_obsidian-graph-view.mov` | **Obsidian** graph view (MOC hub, force-directed) | **Obsidian** | 00:00-00:04, 00:10-00:16 |
| `10_shot_mascot-research-workflow.png` | Claude Code: 6-agent mascot-research workflow TUI | ClaudeCode | still |
| `11_shot_github-actions-reproducibility.png` | GitHub Actions: reproducibility runs (mixed green/red) | GitHub | still |
| `12_clip_ci-claude-verify-reproduces.mov` | GitHub Actions: Claude re-verifies headline -> **PASS** | GitHub | 00:00-00:12, **00:18-00:34** |
| `13_clip_mcp-inspector-rich-bundle.mov` | MCP Inspector: 3 tools, JSON verdict, saliency logo | MCPInspector | 00:08-00:20, **00:30-00:50** |
| `14_clip_dashboard-finding-walkthrough.mov` | NCypher React dashboard: triage, 3 axes, memo, validation | Dashboard | **00:05-00:41** (skip 00:00-00:03) |
| `15_clip_notebook-reproduce.mov` | Jupyter: reproduce the analysis, honesty section | Notebook | 00:04-00:30 |

## Short Claude Science / Modal recordings (16-22)

| File | Content | Category | Best segments |
|---|---|---|---|
| `16_clip_claude-science-create-skeptic-specialist.mov` (34s) | Claude Science: create the "Regulatory-genomics skeptic" specialist | ClaudeScience | 00:04-00:20, 00:26-00:34 |
| `17_clip_claude-science-add-ncypher-connector.mov` (20s) | Claude Science: wire NCypher MCP as a connector (3 tools) | ClaudeScience | 00:10-00:20 |
| `18_clip_claude-science-load-mcp-and-plan.mov` (11s) | Claude Science (A2): load NCypher MCP skill + lay out the plan | ClaudeScience | 00:00-00:11 |
| `19_clip_claude-science-reviewer-verifies-a2.mov` (24s) | Claude Science (A2): **Reviewer re-derives the numbers -> SURVIVES** | ClaudeScience | **00:04-00:24** |
| `20_clip_claude-science-figure-polish-reviewer.mov` (21s) | Claude Science (A2): agent edits its own figure from plain English | ClaudeScience | 00:06-00:21 |
| `21_clip_claude-science-cross-analysis-audit.mov` (8s) | Claude Science (A8): cross-analysis self-audit; sibling A5/A7/A9 tabs | ClaudeScience | 00:00-00:08 (crop tab bar) |
| `22_clip_modal-dashboard-deploy-logs-usage.mov` (44s) | **Modal** dashboard (ncypher-score fns, metrics, logs, **$0.65 usage**). NB: opens on a Claude Science tab; the modal.com view starts ~00:04. | Modal | 00:05-00:22, 00:26-00:44 |

## Long session recordings (23-27)

| File | Dur | Content | Gold moments (mm:ss) |
|---|---|---|---|
| `23_session_claude-science-a5-alphagenome-30min.mov` | ~30m | Claude Science: the A5 AlphaGenome cross-check, one continuous PKU-arc session | plan approved **13:05**; GO/HOLD/NO-GO memo **14:00**; concordance figure **20:00**; **reviewer re-derives the number 22:20**; sub-agents + permission gates 03:40 / 08:20 |
| `24_session_claude-science-a7-conservation-19min.mov` | ~19m | Claude Science: A7 axis-independence session | convergence enrichment fig + reviewer verify **08:00**; **reviewer catches phyloP p=0.013, agent corrects 17:30**; deliverables memo 16:00 |
| `25_session_claude-science-a9-abc-37min.mov` | ~37m | Claude Science: A9 ABC target-gene linking session | agent grounding/task-in **00:30-01:10**; NPAS3/COL1A1 hero artifact **22:30** |
| `26_session_claude-science-multiagent-a2-a9-51min.mov` | ~51m | Claude Science: the multi-agent session, A2/A5/A7/A8/A9 tabs fanned out (Modal Hi-C dispatched in bg) | five-session fan-out throughout; **reviewer recomputes 110/40/54 + NPAS3 obs/exp 5.6 off raw Modal files, 39:00** |
| `27_session_claude-science-a2-hero-run-28min.mov` | ~28m | Claude Science: **the cleanest linear A2 hero run** (task -> plan -> MCP -> GO verdicts -> figure -> reviewer) | typed task **00:30**; "Use Cohort Summary?" MCP tool approval **03:00**; **GO-verdict table 06:00**; phyloP figure **19:00**; **reviewer "every headline number reproduces exactly, Step 8 of 8" 20:00** |

Notes: Modal, Obsidian, and the React dashboard do NOT appear inside the long Claude Science sessions
(their figures are matplotlib artifacts rendered in-session). Source those surfaces from `07` / `09` /
`14` / `22`. No `.mov` contains Faith's webcam yet (record separately for the CAM open + close).

## Role -> best source (what the reel uses)
- **Claude Science cockpit (task + plan)** -> `27 @00:30` (used in the reel as `cs-task`).
- **Sub-agents fan out** -> `26 @~05:00` (used as `cs-fanout`).
- **MCP Inspector (tool is real)** -> `13 @00:30-00:50` (used as `mcp`).
- **Reviewer re-derives the number** -> `27 @20:00` (used as `cs-reviewer`); alt `19`, `23 @22:20`.
- **GO/NO-GO memo** -> `23 @14:00`; dashboard memo also in `14 @00:18`.
- **Modal (the muscle)** -> `22 @00:05+` (used as `modal`); alt `07`.
- **GitHub Actions (the conscience)** -> `12 @00:18-00:34` (used as `ci`).
- **React dashboard (finding rendered)** -> `14 @00:05-00:41` (used as `dashboard`).
- **Obsidian graph (lab notebook)** -> `09 @00:00-00:16` (used as `obsidian`).
- **Four-session hardening** -> the four A-figures (a2/a5/a7/a9b) + sibling-tabs texture from `21`/`26`.

## Rename log (old -> new, 2026-07-10)
- `07_clip_obsidian-graph-context-harness.mov` -> `07_clip_modal-dashboard-apps-logs-storage.mov`  (was actually Modal)
- `08_shot_modal-logs.png` -> `08_shot_claude-code-five-subagents-obsidianify.png`  (was actually VS Code)
- `09_clip_five-subagents-obsidianify.mov` -> `09_clip_obsidian-graph-view.mov`  (was actually the Obsidian graph)
- `Screen Recording 2026-07-09 at 15.27.51.mov` -> `16_clip_claude-science-create-skeptic-specialist.mov`
- `Screen Recording 2026-07-09 at 17.14.28.mov` -> `17_clip_claude-science-add-ncypher-connector.mov`
- `Screen Recording 2026-07-09 at 17.50.52.mov` -> `18_clip_claude-science-load-mcp-and-plan.mov`
- `Screen Recording 2026-07-09 at 17.58.53.mov` -> `19_clip_claude-science-reviewer-verifies-a2.mov`
- `Screen Recording 2026-07-09 at 18.45.03.mov` -> `20_clip_claude-science-figure-polish-reviewer.mov`
- `Screen Recording 2026-07-10 at 14.58.35.mov` -> `21_clip_claude-science-cross-analysis-audit.mov`
- `Screen Recording 2026-07-10 at 15.42.34.mov` -> `22_clip_modal-dashboard-deploy-logs-usage.mov`
- `2026-07-09 19-08-24.mov` -> `23_session_claude-science-a5-alphagenome-30min.mov`
- `2026-07-10 08-37-46.mov` -> `24_session_claude-science-a7-conservation-19min.mov`
- `2026-07-10 09-41-51.mov` -> `25_session_claude-science-a9-abc-37min.mov`
- `2026-07-10 14-47-24.mov` -> `26_session_claude-science-multiagent-a2-a9-51min.mov`
- `Screen Recording 2026-07-09 at 17.22.52.mov` -> `27_session_claude-science-a2-hero-run-28min.mov`
