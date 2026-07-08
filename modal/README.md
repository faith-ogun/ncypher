# NCypher scoring on Modal

The ChromBPNet forward pass (variant scoring + DeepSHAP saliency) runs on Modal,
on a clean Linux container, because the Corces models are TensorFlow/Keras `.h5`
files that will not install cleanly on the arm64 Mac. Everything else in NCypher
runs locally. Modal also gives us the cohort-scale fan-out for free.

## One-time setup (Faith)

1. **Modal account + token**
   ```bash
   pip install modal
   modal token new        # opens a browser to authenticate
   ```

2. **Synapse account + token** (to download the Corces models, which are open
   access but require a free registered account)
   - Sign up at https://www.synapse.org (free).
   - Account menu -> Personal Access Tokens -> generate a token with the
     **Download** scope. Copy it.
   - Register it as a Modal secret named `synapse-auth`:
   ```bash
   modal secret create synapse-auth SYNAPSE_AUTH_TOKEN=<paste-your-token>
   ```

## Run

```bash
# 1. Stage the hg38 reference + chrom.sizes + the DMG (Trevino c15 OPC) model
#    into a persistent Modal volume. Slow the first time, warm afterwards.
modal run modal/score_variants.py::prepare_all

# 2. Score the hero variants and pull the results back into the repo.
modal run modal/score_variants.py::score --tsv data/scored/hero_variants.scorer.tsv
# -> writes data/scored/ncypher.variant_scores.tsv
#    (logfc, abs_logfc, jsd, active_allele_quantile, IES, IPS per variant)
```

## Contexts (DMG cell of origin)

`--context` selects the model. Lead is the OPC/oligodendrocyte cluster:

| flag        | Trevino context   | cell type                         |
|-------------|-------------------|-----------------------------------|
| `opc`       | `trevino_2021.c15`| OPC / oligodendrocyte (default)   |
| `oligo_ipc` | `trevino_2021.c10`| oligodendrocyte intermediate prog |
| `early_rg`  | `trevino_2021.c11`| early radial glia                 |
| `late_rg`   | `trevino_2021.c9` | late radial glia                  |

## Notes

- **Scoring is confirmed working** on `tensorflow-cpu==2.15.1` +
  `tensorflow-probability==0.23.0` (the deposited `.h5` loads fine under Keras 2).
- variant-scorer has several undeclared runtime deps, all pinned in the image:
  `deeplift` (dinuc shuffle), `pybedtools` + the `bedtools` binary +
  build-essential (compiles the pybedtools C++ extension), `statsmodels`, `tqdm`,
  `psutil`, and crucially **`kundajelab-shap`** (the shap fork exposing
  `shap.explainers.deep.TFDeepExplainer`; stock shap does not have it).
- `_find_model_h5` navigates chrombpnet_models (syn64713927) ->
  `trevino_2021.cN` -> `fold_0` -> `chrombpnet_nobias.h5`. Fold 0 is the first
  pass; averaging across the five folds (`variant_summary_across_folds.py`) is a
  later refinement.
- CPU is fine for the hero set and the 164 DAVs. Add a GPU (`gpu="A10G"`) to the
  scoring function for the full cohort fan-out.
- `score` writes the scores TSV locally; `saliency` writes a compact `.npz`
  (`data/scored/ncypher.shap.npz`) that `nc_score.saliency.SaliencyBundle` renders
  into ref-vs-alt logos.
