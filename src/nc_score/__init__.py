"""NCypher: decode the non-coding.

A triage layer for non-coding regulatory variants. It couples a
regulatory-activity score (Corces developing-brain ChromBPNet), the mechanism
(the motif and base a variant breaks), and an honest confidence flag, delivered
as a rich MCP tool for Claude Science.

This package is the analysis engine. Three converging evidence axes:
  - chromatin: predicted accessibility change (ChromBPNet)
  - function:  measured lentiMPRA activity (Pollard 164 DAVs)
  - constraint: evolutionary conservation (Zoonomia phyloP)

NCypher promotes a variant when the axes agree and surfaces the informative
disagreements.
"""

__version__ = "0.1.0"

from nc_score.variants import Variant

__all__ = ["Variant", "__version__"]
