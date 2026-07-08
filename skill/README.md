# NCypher triage skill

An **Agent Skill** that encodes NCypher's non-coding-variant triage **workflow** so an
agent (in Claude Code or Claude Science) can run the whole decision procedure, not just
call one tool. This is NCypher's "Claude Use" centrepiece: the reusable, inspectable
procedure a judge can open and read.

British English, no em dashes.

## What this is

The MCP server (`mcp/server.py`) gives an agent the **actions** (score a variant, get the
shortlist, get the cohort summary). This skill gives the agent the **procedure**: which
tool to call first, how to combine the three axes into a GO / HOLD / NO-GO call, how to
try to refute its own conclusion before promoting it, and what it may and may not say. In
the official framing, MCP is the aisles and a Skill is the employee's expertise.

The procedure is seven steps: intake, score (via MCP), converge, mechanism, a
structurally-independent **skeptic / falsification** step, the go/no-go memo, and an
honesty pass that tiers every claim. It is written out in `SKILL.md`.

## Why it is a Skill and not just a docstring

Because there is a real, repeatable, multi-step judgement here that no single tool call
captures: combining orthogonal axes, decomposing which axis drives a call, running an
adversarial falsification pass (the LUMEN "the reviewer is not the model checking itself"
pattern), routing a target gene to a therapeutic axis, and gating every claim behind a
confidence tier and a "Do NOT say" guardrail. Encoding that as a Skill makes the domain
expertise **inspectable data** rather than buried prompt text, which is exactly what this
hackathon rewards.

## Files

```
skill/
  SKILL.md              the skill: YAML frontmatter (name, description) + the 7-step workflow
  README.md             this file
  example_run.md        two worked examples (NPAS3, SOX2-OT) on the real cached data
  references/
    thresholds.md       calibrated thresholds, the three axis definitions, confidence tiers
    guardrails.md       the honesty registry: confidence tiers and the "Do NOT say" list
    therapy-map.md      the DMG therapy-axis routing (BET/CDK7, Monje synaptic, EZH2), cited
```

The reference files are loaded on demand (progressive disclosure): `SKILL.md` stays short
and points into them when a step needs the deep numbers.

## How to invoke it in Claude Code

A discovery copy lives at `.claude/skills/ncypher-triage/`, so Claude Code running in this
repository can find the skill automatically. Trigger it by asking in natural language, for
example:

- "Triage `chr14-33788719-A-G` with NCypher and give me the go/no-go memo."
- "Which DMG non-coding variants should I validate first? Use the NCypher triage skill."
- "Run the NCypher triage on the SOX2-OT variant and be honest about the confidence."

Claude matches the request against the skill `description`, loads `SKILL.md`, and follows
the procedure, calling the NCypher MCP tools where the steps say to. The canonical source
is this `skill/` directory; `.claude/skills/ncypher-triage/` is a copy kept in sync for
Claude Code discovery.

To make the MCP tools available to the skill, connect the server (from `mcp/README.md`):

```json
{
  "mcpServers": {
    "ncypher": {
      "command": "/Users/faith/Desktop/NCypher/.venv/bin/python",
      "args": ["/Users/faith/Desktop/NCypher/mcp/server.py"]
    }
  }
}
```

If the server is not connected, the skill still runs: the same numbers are in
`data/dmg/sweep_result.tsv` and the reference files, and `example_run.md` shows real tool
output to reason over.

## How it runs inside a Claude Science session

This is the hero demo shape (the PKU arc). One sentence in ("triage the SOX2-OT variant
for this DMG patient, or triage the whole cohort"):

1. Claude Science **plans** the analysis and states a confidence.
2. A subagent loads the `ncypher-triage` skill and calls the NCypher MCP
   (`cohort_summary`, then `top_candidates`, then `score_variant`).
3. The rich artifacts render in session: the axis table, the saliency logo image (for
   variants that have one on disk), the mechanism paragraph.
4. A **separate reviewer agent** runs step 5, the skeptic / falsification pass, so the
   verdict is challenged by a structurally-independent context, not self-graded.
5. The session returns the **go/no-go memo**: validate X first, the decisive base-edit
   experiment, the kill criterion, the therapy angle with the "we do not predict drug
   response" guardrail, and a confidence tier on every claim.

The second wow is the **scale fan-out**: run step by step across the whole DMG cohort in
parallel and report the programme-level convergence (neurodevelopmental, constraint-driven,
led by NPAS3), not a fabricated recurrent locus.

## The honest boundary (read before demoing)

NCypher is a triage / coupling layer, not a better predictor and not a driver caller. The
DMG converged hits are private, single-patient, hypothesis-generating candidates. The
chromatin axis is validated on caQTLs (not on MPRA), and it does not predict drug response.
The full "Do NOT say" list is in `references/guardrails.md`; honour it in every output.
