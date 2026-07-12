# demo/ — the submission demo video

The one obvious home for the 3-minute submission video: the script, the assets, and the plan.

## Layout
- **`script/`** — the demo-video scripts, versioned. Current: `demo-script-ncypher-v1.md`
  (v2, v3 land here as we revise). These are *narration/shot* scripts, not code.
- **`assets/`** — the screen-recording clips and stills used in the cut (`13_clip_mcp-inspector-...`,
  `14_clip_dashboard-...`, etc.), plus `other/` and `outtakes/`. Large + gitignored (footage, not code).

## The rendered explainer snippets live in `video/out/`
The Remotion `[ANIM]` cutaways referenced by the script (`ncypher-finding.mp4`, `ncypher-consensus.mp4`,
`ncypher-a2/a5/a7/a9.mp4`, etc.) are rendered in `video/out/` (also gitignored). The script names which
file to pull each snippet from.

## The plan / research behind the script
`docs/plan/demo-video-playbook.md` — the hackathon-craft + Anthropic-style research and the competition
scan that the script is built from.

## Status
- v1 script: drafted (2026-07-10).
- Still to record: the clean Claude Science hero run (OpenScreen zoom-ins), Faith on-camera bookends.
  See the "Assets — NEED" section of the v1 script.
