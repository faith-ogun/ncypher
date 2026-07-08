# NCypher dashboard

The product surface for NCypher: a calibrated, honest, context-specific non-coding
regulatory-variant triage engine for paediatric diffuse midline glioma (DMG).

This is the polished, judge-facing React dashboard. It renders the same rich output
the `score_variant` MCP tool returns (three orthogonal axes, a convergence verdict with a
calibrated confidence tier, a model-native mechanism, a skeptic check and a go/no-go memo),
plus the headline finding and the honest validation.

It is fully self-contained. No backend, no Modal, no network calls at runtime. Every number
is bundled from the real result tables into `src/data/ncypher.json`.

## Run it

Requires Node 18+ (built and screenshotted on Node 24, npm 11).

```bash
cd dashboard
npm install
npm run dev        # http://localhost:5173  (Vite picks a free port and prints it)
```

Build the static production bundle:

```bash
npm run build      # type-checks with tsc, then bundles with Vite into dist/
npm run preview    # serve the built dist/ locally
```

`npm run build` type-checks and bundles with zero errors. The output in `dist/` is a static
site (HTML + one CSS + one JS + the saliency PNGs) that can be opened from any static host.

## The three views

A left-nav switches between three views. Each view is deep-linkable by URL hash.

1. **Variant triage** (`#triage`). Pick a featured variant or type any `chr-pos-ref-alt`.
   The rich card shows:
   - the three orthogonal axes (chromatin log2FC and direction, phyloP and the constrained
     flag, the measured-function axis marked not-available for somatic variants);
   - the convergence verdict as a prominent status pill (GO teal, HOLD amber, NO-GO red)
     with the calibrated confidence tier and the convergence metrics;
   - the mechanism, either the real ref-vs-alt DeepSHAP saliency logo (for the cached
     heroes) or the model-native contribution collapse / accessibility-gain visual, plus
     the named motif only where the PWM disruption is clean;
   - the skeptic (falsification) check;
   - the go/no-go memo: validate first, decisive experiment, kill criterion, therapy angle.

   Featured variants demonstrate every verdict state: NPAS3 (the lead GO), SYN3 / SOX2-OT /
   FARP1 / GDPD5 (converged GO), TERT (positive control), IGFBP7 (an informative HOLD) and
   TLE4 (an honest NO-GO). The **model-context toggle** flips to a breast (out-of-domain)
   context, where the same variant that is a GO in domain is correctly refused as NO-GO. This
   is the honesty demo.

   Deep links: `#triage?v=chr22-33000876-C-T` selects a variant; add `&ctx=breast` to open
   in the out-of-domain context.

2. **The finding** (`#finding`). The headline: functional non-coding variants in DMG do not
   recur at a locus, they converge on a pathway. The axis-decomposition bar chart shows the
   neurodevelopmental-programme enrichment split by axis (constraint 2.62x, p = 4.8e-13;
   converged 2.62x, p = 0.029; chromatin alone 1.13x, p = 0.36, n.s.), the quantitative
   argument that convergence beats a single scorer. NPAS3 leads (three patients, three
   enhancers, a validated tumour suppressor) with its honest caveats stated, plus the
   neurodevelopmental-programme to therapy-axis mapping.

3. **Validation** (`#validation`). The caQTL context-specificity bars (progenitor 7.5x /
   AUROC 0.689, neuron 4.8x, any 3.7x, mismatched PsychENCODE 1.0x, n.s.) that prove the
   right-cell-context claim, alongside the honest MPRA-negative note (accessibility versus
   reporter-activity modality gap) and the orthogonality argument.

A persistent honesty-guardrails footer (the bright-line "do not say" list) sits under every
view.

## Design constraints

- **Light theme only.** White / near-white surfaces, dark ink, teal accent `#0E9E8A`.
- **DNA base colours** are fixed: A `#2E9E43`, C `#2F6FE0`, G `#C67F12`, T `#DA4A42`.
- **Verdict pills:** GO teal, HOLD amber, NO-GO red.
- British English, no em dashes in the UI copy.
- No external fonts, scripts, styles or images at runtime. Self-contained.

## Data provenance

All numbers are extracted from the real result tables (read-only) into `src/data/ncypher.json`
by a small generator script, so nothing is hand-typed and nothing drifts. Sources:

- `data/dmg/sweep_result.tsv` (10,869 OPC-regulatory somatic non-coding SNVs, 152 DMG
  patients; 753 chromatin high-impact, 1,583 constrained, 164 two-axis converged);
- `data/figures/mining/hero_candidates.tsv` (DeepSHAP contribution collapse, disrupted motif);
- `data/mpra/caqtl_validation.tsv` (the caQTL context-specificity numbers);
- `docs/plan/data-mining-findings.md`, `docs/audit/validation-result.md` (the finding and
  the honest framing);
- `skill/references/*` (thresholds, guardrails, therapy map);
- the real DeepSHAP saliency PNGs (`data/figures/hero/*`, `data/figures/real/TERT_*`), copied
  into `public/saliency/`.

Authored narrative (mechanism, skeptic, memo and therapy copy) lives in `src/data/content.ts`,
grounded line by line in the guardrails and the finding document. Numbers stay in the JSON;
prose stays in the TS. The two never disagree.

## Stack

Vite 6, React 18, TypeScript (strict), Tailwind CSS 3. Charts and the sequence-logo visuals
are hand-rolled SVG or the real model PNGs, so the bundle pulls in no chart or component
library and stays self-contained.

## Layout

```
dashboard/
  index.html                 self-contained shell, inline SVG favicon
  src/
    main.tsx, App.tsx         hash-routed shell + guardrails footer
    index.css                 Tailwind + light-theme base
    types.ts                  data + content types
    lib/format.ts             number / p-value / variant-id helpers, palette
    data/
      ncypher.json            generated numeric bundle (read from the result TSVs)
      content.ts              authored hero narratives, therapy axes, guardrails
    components/               Sidebar, StatusPill, AxisTriPanel, Mechanism, HBarChart, ui
    views/                    VariantTriage, TheFinding, Validation
  public/saliency/            real DeepSHAP saliency PNGs
```
