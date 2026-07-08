# NCypher — decode the non-coding

A calibrated, honest, context-specific engine for triaging **non-coding regulatory
variants** in paediatric **diffuse midline glioma (DMG)**, delivered as a rich MCP tool and
an Agent Skill for Claude Science.

Built for **Built with Claude: Life Sciences** (Anthropic x Cerebral Valley x Gladstone
Institutes), Researcher track. Apache-2.0.

> NCypher couples three independent lines of evidence for a non-coding variant, chromatin
> **accessibility**, evolutionary **constraint**, and reporter **function**, in the tumour's
> cell-of-origin context, promotes a variant only when they agree, shows the exact motif and
> base it breaks, and is honest about what it does and does not know. It is **not** a bigger
> variant-effect predictor; it is the coupling and triage layer.

## The finding

The first read of DMG's somatic non-coding variation against the enhancers the H3K27M
oncohistone builds. Honest and two-sided:

- **Somatic variants do not drive the DIPG super-enhancers** (the BET/CDK7 addiction):
  convergence 1.6% vs 1.5% (p=0.4), chromatin-impact 7.4% vs 6.8% (p=0.2) inside vs outside,
  the expected null for an epigenetic disease.
- **But the super-enhancers are anchored on more evolutionarily constrained OPC regulatory
  sequence**: constrained 17.0% vs 14.0% (p=6e-4), median phyloP 0.28 vs 0.19, robust to
  class- and GC-matched permutation (both p<0.001), bootstrap CI [+0.029, +0.162] (excludes 0),
  genic-driven.

So H3K27M's druggable super-enhancer addiction is anchored on the developing brain's conserved
OPC regulatory sequence; the conserved landscape is the signal, not somatic disruption. Lead
candidate: **NPAS3**, a validated glioma tumour suppressor, super-enhancer-resident. The result
fuses Zoonomia constraint, the DIPG super-enhancers, and the fetal-OPC model. Honest bound:
modest effect, hypothesis-generating, not a driver claim.

## How it works

Three orthogonal axes for a variant `chr-pos-ref-alt`:
1. **Chromatin** — predicted accessibility change from the pretrained Corces / Marderstein
   fetal-OPC **ChromBPNet** (`trevino_2021.c15`), DMG's cell of origin. No training.
2. **Constraint** — per-base **Zoonomia phyloP** (241 mammals), streamed remotely.
3. **Function** — measured caQTL / MPRA evidence where available.

A **convergence engine** promotes a variant only when the axes agree, surfaces the informative
disagreements, and emits a **go/no-go memo**. Mechanism is a ref-vs-alt **DeepSHAP saliency
logo** where the disrupted motif is visible at the exact base.

## Validation (honest)

- **Chromatin axis validated on its native ground truth, caQTLs**: recovers **progenitor
  caQTLs at AUROC 0.69 / 7.5x** in the matched fetal-OPC context (bootstrap CI [0.592, 0.777]),
  context-specific (neuron 0.64, mismatched null; the gap excludes 0).
- **Honest negative:** it does not recover the 164 MPRA differential-activity variants, because
  it predicts *accessibility* and MPRA measures reporter *activity*. The axes are orthogonal by design.

## Delivery

- **`mcp/`** — a FastMCP server (`score_variant`, `top_candidates`, `cohort_summary`).
- **`skill/`** — the `ncypher-triage` Agent Skill (score -> converge -> mechanism -> skeptic -> memo).
- **`modal/`** — ChromBPNet inference + DeepSHAP on Modal (parallel fan-out; cohort scale).
- **`dashboard/`** — a React dashboard (variant triage, the finding, validation).

## Reproduce

```bash
python3.10 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
PYTHONPATH=src python -m pytest tests/ -q                    # engine unit tests
# ChromBPNet scoring + DeepSHAP run on Modal (see modal/README.md)
PYTHONPATH=src python scripts/validate_caqtl.py             # the caQTL validation
PYTHONPATH=src python scripts/bootstrap_caqtl.py           # bootstrap CIs + context-specificity
PYTHONPATH=src python scripts/k27m_se_analysis.py          # the K27M super-enhancer finding
PYTHONPATH=src python scripts/k27m_se_constraint_control.py # the confound controls
```

Large data (hg38, OpenPedCan MAF, MPRA tables, models) is fetched, not committed; the model
accessions are in `modal/README.md`.

## Layout

```
src/nc_score/   variants, genome, constraint, scoring, converge, viz, saliency, cohort, validate, data
modal/          ChromBPNet inference + DeepSHAP (Modal, parallel fan-out)
mcp/  skill/    the MCP server + the Agent Skill (the delivery layer)
dashboard/      the React product surface
scripts/        validate_caqtl, bootstrap_caqtl, k27m_se_analysis, render_se_motif_figure, ...
tests/          engine unit tests
```

## Provenance

Engine: Marderstein, Kundu et al., *Nature Genetics* 2026 (Corces / Gladstone + Stanford),
Synapse `syn64693551`, context `trevino_2021.c15`. ChromBPNet: Pampari, Kundaje et al.
Constraint: Zoonomia `cactus241way` phyloP. Function: Deng, Whalen ... Pollard, *Science* 2024.
DIPG super-enhancers: Nagaraja et al., *Cancer Cell* 2017. DMG cohort: OpenPedCan v15.
NPAS3: Moreira et al., *Am J Pathol* 2011.

*Built by Faith Ogundimu, computational cancer genomics, RCSI.*
