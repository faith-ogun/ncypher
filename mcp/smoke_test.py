"""Smoke test for the NCypher MCP tools, WITHOUT an MCP client.

Imports the tool functions from server.py and calls each once on real cached
data, printing the text and a slice of the structured content so the server can
be verified before wiring it into Claude Science.

Run:
    /Users/faith/Desktop/NCypher/.venv/bin/python mcp/smoke_test.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # so `import server` works

import server  # noqa: E402


def _first_converged_key() -> str:
    """Pick the top converged variant from the sweep (highest |log2FC|)."""
    with open(server.SWEEP_TSV, newline="") as fh:
        rows = [r for r in csv.DictReader(fh, delimiter="\t")
                if r.get("converged_2ax") == "True"]
    rows.sort(key=lambda r: float(r["abs_logfc"]), reverse=True)
    return rows[0]["key"]


def _call(tool, **kwargs):
    """FastMCP wraps the function; .fn is the underlying callable."""
    fn = getattr(tool, "fn", tool)
    return fn(**kwargs)


def _show(title: str, result) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)
    content = result.content
    blocks = content if isinstance(content, list) else [content]
    for block in blocks:
        if isinstance(block, str):
            print(block)
        elif getattr(block, "type", None) == "text" or hasattr(block, "text"):
            print(block.text)
        elif getattr(block, "type", None) == "image" or hasattr(block, "data"):
            mime = getattr(block, "mimeType", "image")
            print(f"[image content attached: {mime}]")
        else:
            print(f"[content block: {type(block).__name__}]")
    sc = result.structured_content or {}
    keys = list(sc.keys())
    print(f"\n[structured_content keys] {keys}")


def main() -> None:
    key = _first_converged_key()
    print(f"Top converged cached variant: {key}")

    _show(f"score_variant({key!r})  [cache hit]", _call(server.score_variant, variant_id=key))

    # A variant not in the cache -> live phyloP path (chromatin flagged unscored).
    _show("score_variant('chr7-5530601-A-G')  [live phyloP path]",
          _call(server.score_variant, variant_id="chr7-5530601-A-G"))

    _show("top_candidates(n=10, converged_only=True)",
          _call(server.top_candidates, n=10, converged_only=True))

    _show("cohort_summary()", _call(server.cohort_summary))

    print("\nSMOKE TEST PASSED")


if __name__ == "__main__":
    main()
