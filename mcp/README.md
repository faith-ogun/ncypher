# NCypher MCP server

A rich [MCP](https://modelcontextprotocol.io) server that exposes the NCypher
triage engine as agent-callable tools. NCypher couples three evidence axes for a
somatic non-coding regulatory variant in paediatric diffuse midline glioma (DMG):

- **chromatin accessibility** (ChromBPNet, the developing-brain fetal-OPC model,
  Trevino 2021 cluster c15),
- **evolutionary constraint** (Zoonomia cactus241way phyloP, 241 placental mammals),
- **measured function** (lentiMPRA; a later axis, not available for these somatic
  variants).

The convergence engine promotes a variant only when the available axes agree,
surfaces informative disagreements, and is honest when a call sits out of domain.
Every tool returns a **go/no-go memo** (verdict, decisive experiment, kill
criterion), structured content, and provenance, not a bare string.

The server does **no heavy scoring**. It serves the pre-computed discovery sweep
(`data/dmg/sweep_result.tsv`, 10,869 OPC-regulatory DMG variants, 164 converged)
and, for a variant not in that cache, does a fast live phyloP lookup while telling
the caller the chromatin axis still needs scoring.

## Tools

| Tool | Signature | Returns |
|------|-----------|---------|
| `score_variant` | `score_variant(variant_id: str)` | Full three-axis triage for one variant (e.g. `"chr22-33000876-C-T"`): structured axis values + a go/no-go memo built by the convergence engine. Cache hit gives the complete call; a miss does a live phyloP lookup and flags the chromatin axis as unscored. A saliency PNG is attached only if one already exists on disk (e.g. TERT logos). |
| `top_candidates` | `top_candidates(n: int = 20, converged_only: bool = True)` | The ranked "which to validate first" shortlist, as a markdown table plus a structured candidate list (key, gene, log2FC, phyloP, confidence, converged). |
| `cohort_summary` | `cohort_summary()` | The honest headline numbers from the sweep (10,869 scored, 753 chromatin high-impact, 1,583 constrained, 164 converged, 0 recurrent, 0 in canonical driver genes) with the honest caveat. Computed live from the cache. |
| `get_regulatory_map` | `get_regulatory_map(limit: int = 0)` | The downloadable DMG regulatory map: manifest + 37-column schema + the 164 converged hits (fully annotated, **typed** booleans/numbers) + paths to the full 10,869-row TSV/Parquet. The tool-accessible twin of the `ncypher://regulatory-map` resource, for hosts that surface tools but not resources. |

## Requirements

Use the project virtual environment (Python 3.10):

```bash
/Users/faith/Desktop/NCypher/.venv/bin/pip install fastmcp
```

`fastmcp` (3.x) is the only extra dependency; `pyBigWig` (already installed) is
used for the live phyloP path in `score_variant`. The tools read
`nc_score` from `src/` (added to `sys.path` automatically) and the cached TSVs
under `data/dmg/`.

## Run it

Directly (stdio transport, the default for local MCP):

```bash
/Users/faith/Desktop/NCypher/.venv/bin/python mcp/server.py
```

or via the FastMCP CLI:

```bash
/Users/faith/Desktop/NCypher/.venv/bin/fastmcp run mcp/server.py
```

## Verify without an MCP client

`smoke_test.py` imports the tool functions and calls each once on a real cached
variant (the top converged hit, `chr22-33000876-C-T`) plus a live-lookup variant:

```bash
/Users/faith/Desktop/NCypher/.venv/bin/python mcp/smoke_test.py
```

It prints each tool's text and structured-content keys and ends with
`SMOKE TEST PASSED`.

## Connect it to Claude Science / Claude Desktop

Add a local stdio connector to your MCP client config (for Claude Desktop:
`claude_desktop_config.json`; Claude Science uses the same connector stanza):

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

Use absolute paths (the client launches the server from an arbitrary working
directory). After saving, restart the client; the `ncypher` server and its three
tools (`score_variant`, `top_candidates`, `cohort_summary`) will appear. The
agent can then chain them into a triage workflow: `cohort_summary` for the
landscape, `top_candidates` for the shortlist, `score_variant` for the go/no-go
memo on any single variant.

## Provenance

Model context `trevino_2021.c15` (developing-brain fetal-OPC ChromBPNet), genome
GRCh38. Constraint from Zoonomia cactus241way phyloP (constrained at phyloP >=
2.27). Chromatin high-impact is calibrated at |log2FC| >= 0.162 (p99 of an
800-variant cohort background), not an arbitrary absolute. Full write-up:
`docs/audit/sweep-result.md`.
