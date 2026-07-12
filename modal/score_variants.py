"""NCypher ChromBPNet scoring on Modal.

The heavy TensorFlow forward pass (ChromBPNet variant scoring + DeepSHAP
saliency) runs here, on a clean Linux container, and writes results back to the
local repo. Everything else in NCypher (the MCP tool, the dashboard, the
constraint axis, the saliency rendering) runs locally.

Why Modal and not the Mac: the Corces models are TensorFlow/Keras `.h5` files and
the arm64 Mac cannot install that stack cleanly. Modal also gives us the
"triage a whole cohort in parallel" scale flex for free (`.map` over variants).

Dependency note: kundajelab/variant-scorer is self-contained (it does NOT import
the full chrombpnet package). It needs TensorFlow + tensorflow-probability +
shap + deepdish + pyfaidx. We pin a Keras-2 TF (2.15) because the deposited
models were saved in that era and Keras 3 (TF >= 2.16) breaks `load_model` on
them.

Setup (one time, done by Faith):
  pip install modal
  modal token new
  # Synapse: create a free account, then Account -> Personal Access Tokens ->
  # generate a token with "Download" scope, and register it as a Modal secret:
  modal secret create synapse-auth SYNAPSE_AUTH_TOKEN=<your-token>

Usage:
  # 1. stage the reference + the DMG (Trevino c15 OPC) model into the volume
  modal run modal/score_variants.py::prepare_all
  # 2. score a variant TSV (chrombpnet schema) and pull results locally
  modal run modal/score_variants.py::score --tsv data/scored/hero_variants.scorer.tsv
  # (saliency / DeepSHAP entrypoint is added once scoring is confirmed working)
"""

from __future__ import annotations

import pathlib

import modal

# --- context -> Corces/Trevino model selection -------------------------------
# The DMG cell of origin is OPC-like / radial-glia-like. Lead context is the
# Trevino 2021 OPC/oligodendrocyte cluster. These names are matched against the
# Synapse `chrombpnet_models/trevino_2021` folder contents at fetch time.
CONTEXTS = {
    "opc": "trevino_2021.c15",        # OPC / oligodendrocyte  (lead DMG context)
    "oligo_ipc": "trevino_2021.c10",  # oligodendrocyte intermediate progenitor
    "early_rg": "trevino_2021.c11",   # early radial glia
    "late_rg": "trevino_2021.c9",     # late radial glia
    # A3 multi-context specificity: a NON-NEURAL control (off-lineage; the signal
    # should be null/weak here). Confirm the exact study.cluster before running:
    #   modal run modal/score_variants.py::lssyn --syn-id syn64713927 --depth 2
    # then set the value to a fetal-heart study/cluster from the same deposition
    # (or a public ENCODE K562 ChromBPNet, noting the cross-deposition caveat).
    "heart_control": "domcke_2020.fetal_heart.Cardiomyocytes",  # non-neural off-lineage control (A3)
}
DEFAULT_CONTEXT = "opc"

# Synapse: neuro_variants project -> chrombpnet_models folder (Marderstein/Kundu).
SYNAPSE_MODELS_FOLDER = "syn64713927"
# peaks folder (ATAC-accessible regions per context) - the OPC regulatory landscape.
SYNAPSE_PEAKS_FOLDER = "syn64716764"

HG38_FA_URL = (
    "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/analysisSet/"
    "hg38.analysisSet.fa.gz"
)
# The analysisSet dir has no .chrom.sizes; the standard bigZips file carries the
# main-chromosome sizes (which match the analysis-set reference for our variants).
HG38_CHROMSIZES_URL = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.chrom.sizes"

VOL = modal.Volume.from_name("ncypher-ref", create_if_missing=True)
VOL_MNT = pathlib.Path("/vol")
VARIANT_SCORER_DIR = "/opt/variant-scorer"

image = (
    modal.Image.debian_slim(python_version="3.11")
    # bedtools binary backs pybedtools; build-essential/headers let pybedtools
    # compile its C++ extension (no manylinux wheel for this version).
    .apt_install("git", "wget", "bedtools", "build-essential", "python3-dev", "zlib1g-dev")
    .pip_install(
        "tensorflow-cpu==2.15.1",
        "tensorflow-probability==0.23.0",
        # ChromBPNet's variant-scorer uses the kundajelab shap fork, which
        # exposes shap.explainers.deep.TFDeepExplainer (absent from stock shap).
        "kundajelab-shap==1",
        "deepdish==0.3.7",
        "pyfaidx==0.8.1.1",
        "pandas",
        "numpy<2",
        "scipy",
        "h5py",
        "pysam",
        "deeplift",       # dinuc_shuffle generator
        "pybedtools",     # utils.io
        "statsmodels",    # shuffled-null p-values
        "psutil",
        "tqdm",
        "synapseclient==4.6.0",
    )
    .run_commands(
        f"git clone --depth 1 https://github.com/kundajelab/variant-scorer.git {VARIANT_SCORER_DIR}",
        # deepdish 0.3.7 uses numpy aliases removed in numpy>=1.24 (np.object etc).
        # Restoring the builtins is the safe fix the deprecation note recommends.
        "python - <<'PY'\n"
        "import deepdish, os, re, glob\n"
        "root = os.path.dirname(deepdish.__file__)\n"
        "for f in glob.glob(os.path.join(root, '**', '*.py'), recursive=True):\n"
        "    s = open(f).read()\n"
        "    s2 = re.sub(r'np\\.(object|bool|int|float|str|complex)\\b', r'\\1', s)\n"
        "    if s2 != s: open(f, 'w').write(s2)\n"
        "PY",
        # kundajelab-shap's force.py does `from IPython.core.display import display,
        # HTML`, which newer IPython (resolved under python 3.11) removed; the symbols
        # live in IPython.display now. Rewrite the import so `import shap` succeeds.
        "python - <<'PY'\n"
        "import os, glob, sysconfig\n"
        "sp = sysconfig.get_paths()['purelib']\n"
        "for f in glob.glob(os.path.join(sp, 'shap', '**', '*.py'), recursive=True):\n"
        "    s = open(f).read()\n"
        "    s2 = s.replace('from IPython.core.display import', 'from IPython.display import')\n"
        "    if s2 != s: open(f, 'w').write(s2)\n"
        "PY",
    )
)

app = modal.App("ncypher-score", image=image)


# --- helpers -----------------------------------------------------------------
def _synapse_login():
    import os

    import synapseclient

    syn = synapseclient.Synapse()
    syn.login(authToken=os.environ["SYNAPSE_AUTH_TOKEN"])
    return syn


def _find_child_folder(syn, parent_id: str, name: str, max_depth: int = 3):
    """Return the Synapse id of a folder named ``name`` under ``parent_id``,
    searching recursively (the layout is chrombpnet_models -> [study] ->
    context -> fold, and context folders may sit one level down)."""
    frontier = [(parent_id, 0)]
    while frontier:
        pid, depth = frontier.pop()
        for c in syn.getChildren(pid, includeTypes=["folder"]):
            if c["name"] == name:
                return c["id"]
            if depth + 1 < max_depth:
                frontier.append((c["id"], depth + 1))
    return None


def _find_model_h5(syn, context_id: str, fold: int = 0) -> str:
    """Download (and cache in the volume) the bias-corrected ChromBPNet model
    for ``context_id`` (e.g. 'trevino_2021.c15'), fold ``fold``.

    Layout: chrombpnet_models / trevino_2021.c15 / fold_0 / chrombpnet_nobias.h5.
    Fold 0 is used for the first pass; variant_summary_across_folds averages the
    five folds later.
    """
    dest = VOL_MNT / "models" / context_id / f"fold_{fold}"
    dest.mkdir(parents=True, exist_ok=True)
    cached = dest / "chrombpnet_nobias.h5"
    if cached.exists():
        return str(cached)

    ctx_folder = _find_child_folder(syn, SYNAPSE_MODELS_FOLDER, context_id)
    if ctx_folder is None:
        raise FileNotFoundError(f"context folder {context_id} not found under {SYNAPSE_MODELS_FOLDER}")
    fold_folder = _find_child_folder(syn, ctx_folder, f"fold_{fold}", max_depth=1)
    if fold_folder is None:
        raise FileNotFoundError(f"fold_{fold} not found under {context_id}")

    for c in syn.getChildren(fold_folder, includeTypes=["file"]):
        if c["name"] == "chrombpnet_nobias.h5":
            ent = syn.get(c["id"], downloadLocation=str(dest), ifcollision="keep.local")
            return ent.path
    raise FileNotFoundError(f"chrombpnet_nobias.h5 not found in {context_id}/fold_{fold}")


# --- diagnostics -------------------------------------------------------------
@app.function(secrets=[modal.Secret.from_name("synapse-auth")], timeout=15 * 60)
def list_models(context_id: str = "trevino_2021.c15", max_depth: int = 4):
    """Print the Synapse chrombpnet_models folder tree so we can see the real
    naming/nesting for a context (used to fix the model-path matcher)."""
    syn = _synapse_login()

    def children(parent):
        return list(syn.getChildren(parent, includeTypes=["folder", "file"]))

    lines = []

    def walk(parent_id, prefix, depth):
        if depth > max_depth:
            return
        for c in children(parent_id):
            kind = "D" if "Folder" in c["type"] else "F"
            lines.append(f"{prefix}[{kind}] {c['name']}  ({c['id']})")
            # only descend into folders whose name is plausibly on the path to
            # our context, to keep the listing focused and fast.
            study = context_id.split(".")[0]
            cluster = context_id.split(".")[-1]
            name = c["name"].lower()
            relevant = (
                "Folder" in c["type"]
                and (study in name or cluster in name or context_id.lower() in name
                     or name in ("models", "chrombpnet_models") or "trevino" in name
                     or "fold" in name)
            )
            if relevant:
                walk(c["id"], prefix + "  ", depth + 1)

    lines.append(f"root chrombpnet_models = {SYNAPSE_MODELS_FOLDER}")
    walk(SYNAPSE_MODELS_FOLDER, "  ", 1)
    print("\n".join(lines))
    return lines


@app.local_entrypoint()
def ls(context_id: str = "trevino_2021.c15"):
    for ln in list_models.remote(context_id):
        print(ln)


@app.function(secrets=[modal.Secret.from_name("synapse-auth")], timeout=10 * 60)
def ls_synapse(syn_id: str, depth: int = 2):
    """List children (folders + files) of a Synapse container, depth levels deep."""
    syn = _synapse_login()
    lines = []
    def walk(pid, prefix, d):
        if d > depth: return
        for c in syn.getChildren(pid, includeTypes=["folder", "file"]):
            kind = "D" if "Folder" in c["type"] else "F"
            lines.append(f"{prefix}[{kind}] {c['name']}  ({c['id']})")
            if kind == "D" and d < depth:
                walk(c["id"], prefix + "  ", d + 1)
    walk(syn_id, "", 1)
    print("\n".join(lines))
    return lines


@app.local_entrypoint()
def lssyn(syn_id: str, depth: int = 2):
    for ln in ls_synapse.remote(syn_id, depth):
        print(ln)


@app.function(secrets=[modal.Secret.from_name("synapse-auth")], timeout=15 * 60)
def fetch_peaks(context: str = DEFAULT_CONTEXT) -> bytes:
    """Find and return the ATAC peak file (BED-like) for a context from the Synapse
    peaks folder. Returns the raw bytes (gzip or plain) of the first peak-like file;
    prints the folder contents so we can see the naming."""
    syn = _synapse_login()
    ctx = CONTEXTS[context]  # e.g. trevino_2021.c15
    study = ctx.split(".")[0]  # trevino_2021
    # peaks are files named "<ctx>.overlap.peaks.bed.gz" under the study folder.
    study_folder = _find_child_folder(syn, SYNAPSE_PEAKS_FOLDER, study, max_depth=2)
    if study_folder is None:
        raise FileNotFoundError(f"study peaks folder {study} not found under {SYNAPSE_PEAKS_FOLDER}")
    want = f"{ctx}.overlap.peaks.bed.gz"
    for c in syn.getChildren(study_folder, includeTypes=["file"]):
        if c["name"] == want:
            ent = syn.get(c["id"], downloadLocation="/tmp/peaks", ifcollision="keep.local")
            import pathlib
            return pathlib.Path(ent.path).read_bytes()
    raise FileNotFoundError(f"{want} not found under {study} peaks folder")


@app.local_entrypoint()
def peaks(context: str = DEFAULT_CONTEXT, out: str = "data/dmg/c15_peaks.bed.gz"):
    data = fetch_peaks.remote(context)
    p = pathlib.Path(out); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    print("wrote", p, len(data), "bytes")


# --- functions ---------------------------------------------------------------
@app.function(volumes={VOL_MNT: VOL}, timeout=60 * 60)
def prepare(context: str = DEFAULT_CONTEXT):
    """Stage the hg38 reference, chrom.sizes, and the chosen model into the
    persistent volume so later scoring calls start warm."""
    import subprocess

    (VOL_MNT / "genome").mkdir(parents=True, exist_ok=True)
    fa = VOL_MNT / "genome" / "hg38.analysisSet.fa"
    sizes = VOL_MNT / "genome" / "hg38.chrom.sizes"
    # pipefail so a wget failure inside the pipe is not masked by gunzip's exit;
    # re-download if the fasta looks truncated (< 3 GB).
    if not fa.exists() or fa.stat().st_size < 3_000_000_000:
        subprocess.run(
            f"set -o pipefail; wget -qO- {HG38_FA_URL} | gunzip > {fa}",
            shell=True, check=True, executable="/bin/bash",
        )
    if not sizes.exists() or sizes.stat().st_size == 0:
        subprocess.run(f"wget -qO {sizes} {HG38_CHROMSIZES_URL}", shell=True, check=True)
    VOL.commit()
    return {
        "reference": str(fa),
        "reference_bytes": fa.stat().st_size,
        "chrom_sizes": str(sizes),
        "chrom_sizes_bytes": sizes.stat().st_size,
    }


@app.function(
    volumes={VOL_MNT: VOL},
    secrets=[modal.Secret.from_name("synapse-auth")],
    timeout=60 * 60,
)
def fetch_model(context: str = DEFAULT_CONTEXT) -> str:
    """Download the ChromBPNet bias-corrected model for a context from Synapse."""
    syn = _synapse_login()
    path = _find_model_h5(syn, CONTEXTS[context])
    VOL.commit()
    return path


@app.function(
    volumes={VOL_MNT: VOL},
    secrets=[modal.Secret.from_name("synapse-auth")],
    timeout=2 * 60 * 60,
    memory=32768,  # variant-scorer holds all predictions in memory; large sweeps OOM the default
    cpu=8.0,
)
def score_tsv(tsv_bytes: bytes, context: str = DEFAULT_CONTEXT) -> bytes:
    """Run variant_scoring.py on a chrombpnet-schema TSV; return the scores TSV
    bytes. Model + reference are pulled/staged on demand."""
    import subprocess
    import tempfile

    syn = _synapse_login()
    model = _find_model_h5(syn, CONTEXTS[context])
    fa = VOL_MNT / "genome" / "hg38.analysisSet.fa"
    sizes = VOL_MNT / "genome" / "hg38.chrom.sizes"

    workdir = pathlib.Path(tempfile.mkdtemp())
    (workdir / "variants.tsv").write_bytes(tsv_bytes)
    out_prefix = workdir / "ncypher"

    cmd = [
        "python", f"{VARIANT_SCORER_DIR}/src/variant_scoring.py",
        "--list", str(workdir / "variants.tsv"),
        "--genome", str(fa),
        "--model", model,
        "--chrom_sizes", str(sizes),
        "--out_prefix", str(out_prefix),
        "--schema", "chrombpnet",
        "--no_hdf5",
    ]
    proc = subprocess.run(
        cmd, cwd=f"{VARIANT_SCORER_DIR}/src",
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        # surface the real variant-scorer error, not just the outer wrapper.
        raise RuntimeError(
            "variant_scoring.py failed\n"
            f"--- STDOUT (tail) ---\n{proc.stdout[-4000:]}\n"
            f"--- STDERR (tail) ---\n{proc.stderr[-4000:]}"
        )
    return (pathlib.Path(str(out_prefix) + ".variant_scores.tsv")).read_bytes()


@app.function(
    volumes={VOL_MNT: VOL},
    secrets=[modal.Secret.from_name("synapse-auth")],
    timeout=3 * 60 * 60,
    memory=32768,
    cpu=8.0,
)
def score_to_volume(tsv_bytes: bytes, out_name: str, context: str = DEFAULT_CONTEXT) -> dict:
    """Detach-safe scoring: run variant_scoring.py and WRITE the result to the
    persistent volume (/vol/results/<out_name>) rather than streaming it back, so a
    disconnected client cannot lose the compute. Retrieve later with fetch_result."""
    import subprocess
    import tempfile

    syn = _synapse_login()
    model = _find_model_h5(syn, CONTEXTS[context])
    fa = VOL_MNT / "genome" / "hg38.analysisSet.fa"
    sizes = VOL_MNT / "genome" / "hg38.chrom.sizes"
    workdir = pathlib.Path(tempfile.mkdtemp())
    (workdir / "variants.tsv").write_bytes(tsv_bytes)
    out_prefix = workdir / "ncypher"
    cmd = [
        "python", f"{VARIANT_SCORER_DIR}/src/variant_scoring.py",
        "--list", str(workdir / "variants.tsv"), "--genome", str(fa),
        "--model", model, "--chrom_sizes", str(sizes),
        "--out_prefix", str(out_prefix), "--schema", "chrombpnet", "--no_hdf5",
    ]
    proc = subprocess.run(cmd, cwd=f"{VARIANT_SCORER_DIR}/src", capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"variant_scoring.py failed\nSTDERR:\n{proc.stderr[-4000:]}")
    results = VOL_MNT / "results"
    results.mkdir(parents=True, exist_ok=True)
    dest = results / out_name
    dest.write_bytes(pathlib.Path(str(out_prefix) + ".variant_scores.tsv").read_bytes())
    VOL.commit()
    return {"path": str(dest), "bytes": dest.stat().st_size, "stdout_tail": proc.stdout[-500:]}


@app.function(volumes={VOL_MNT: VOL}, timeout=10 * 60)
def read_result(name: str):
    """Read a result file back from the volume (None if not ready yet)."""
    p = VOL_MNT / "results" / name
    return p.read_bytes() if p.exists() else None


@app.function(volumes={VOL_MNT: VOL}, timeout=10 * 60)
def sweep_status(out_name: str = "functional_sweep.variant_scores.tsv"):
    """Report chunk progress on the volume."""
    rdir = VOL_MNT / "results" / f"{out_name}.chunks"
    if not rdir.exists():
        return {"chunks_done": 0, "errors": [], "combined_exists": (VOL_MNT / "results" / out_name).exists()}
    done = sorted(p.name for p in rdir.glob("chunk*.tsv"))
    errs = sorted(p.name for p in rdir.glob("*.ERROR.txt"))
    return {"chunks_done": len(done), "done": done, "errors": errs,
            "combined_exists": (VOL_MNT / "results" / out_name).exists()}


@app.local_entrypoint()
def status(out_name: str = "functional_sweep.variant_scores.tsv"):
    print(sweep_status.remote(out_name))


@app.function(
    volumes={VOL_MNT: VOL},
    secrets=[modal.Secret.from_name("synapse-auth")],
    timeout=6 * 60 * 60,
    memory=32768,
    cpu=8.0,
)
def sweep_chunked(tsv_bytes: bytes, out_name: str, chunk_size: int = 1200,
                  context: str = DEFAULT_CONTEXT) -> dict:
    """Chunked, checkpointed, resumable sweep. Scores the variant TSV in small
    chunks, writing each chunk's scores to the volume (committed) as it finishes.
    Re-running SKIPS chunks already on the volume, so a cancelled run resumes.
    Finally concatenates all chunks into /vol/results/<out_name>."""
    import subprocess
    import tempfile

    syn = _synapse_login()
    model = _find_model_h5(syn, CONTEXTS[context])
    fa = str(VOL_MNT / "genome" / "hg38.analysisSet.fa")
    sizes = str(VOL_MNT / "genome" / "hg38.chrom.sizes")
    rdir = VOL_MNT / "results" / f"{out_name}.chunks"
    rdir.mkdir(parents=True, exist_ok=True)

    lines = tsv_bytes.decode().splitlines()
    chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
    n_done = 0
    for i, ch in enumerate(chunks):
        cf = rdir / f"chunk{i:03d}.tsv"
        if cf.exists() and cf.stat().st_size > 0:
            n_done += 1
            continue
        wd = pathlib.Path(tempfile.mkdtemp())
        (wd / "v.tsv").write_text("\n".join(ch) + "\n")
        op = wd / "out"
        cmd = ["python", f"{VARIANT_SCORER_DIR}/src/variant_scoring.py",
               "--list", str(wd / "v.tsv"), "--genome", fa, "--model", model,
               "--chrom_sizes", sizes, "--out_prefix", str(op),
               "--schema", "chrombpnet", "--no_hdf5"]
        proc = subprocess.run(cmd, cwd=f"{VARIANT_SCORER_DIR}/src", capture_output=True, text=True)
        # A single bad chunk must not kill the whole sweep. Record the failure and
        # move on; the chunk is retried on the next resume (no marker written).
        if proc.returncode != 0:
            (rdir / f"chunk{i:03d}.ERROR.txt").write_text(proc.stderr[-4000:])
            VOL.commit()
            print(f"chunk {i} FAILED (recorded, continuing): {proc.stderr[-300:]}")
            continue
        cf.write_bytes(pathlib.Path(str(op) + ".variant_scores.tsv").read_bytes())
        VOL.commit()
        n_done += 1

    # combine (header from first chunk, then bodies)
    combined, header_written = [], False
    for i in range(len(chunks)):
        cf = rdir / f"chunk{i:03d}.tsv"
        if not cf.exists():
            continue
        rows = cf.read_text().splitlines()
        if not rows:
            continue
        if not header_written:
            combined.append(rows[0]); header_written = True
        combined.extend(rows[1:])
    out = VOL_MNT / "results" / out_name
    out.write_text("\n".join(combined) + "\n")
    VOL.commit()
    return {"chunks_total": len(chunks), "chunks_done": n_done,
            "path": str(out), "rows": max(0, len(combined) - 1)}


@app.local_entrypoint()
def sweep_chunks(tsv: str, out_name: str = "functional_sweep.variant_scores.tsv",
                 chunk_size: int = 1200, context: str = DEFAULT_CONTEXT):
    """Detach-safe, resumable chunked sweep. Run with `modal run --detach`."""
    data = pathlib.Path(tsv).read_bytes()
    print(sweep_chunked.remote(data, out_name, chunk_size, context))


@app.function(
    volumes={VOL_MNT: VOL},
    secrets=[modal.Secret.from_name("synapse-auth")],
    timeout=2 * 60 * 60,
    memory=16384,
    cpu=4.0,
)
def score_chunk(args) -> int:
    """Score ONE chunk (idx, lines, out_name, context) and write it to the volume.
    Idempotent: skips if the chunk already exists. Designed to be run in parallel
    via .map() so the whole sweep fans out across many containers at once."""
    import subprocess
    import tempfile

    idx, lines, out_name, context = args
    rdir = VOL_MNT / "results" / f"{out_name}.chunks"
    rdir.mkdir(parents=True, exist_ok=True)
    cf = rdir / f"chunk{idx:03d}.tsv"
    VOL.reload()
    if cf.exists() and cf.stat().st_size > 0:
        return idx

    syn = _synapse_login()
    model = _find_model_h5(syn, CONTEXTS[context])
    fa = str(VOL_MNT / "genome" / "hg38.analysisSet.fa")
    sizes = str(VOL_MNT / "genome" / "hg38.chrom.sizes")
    wd = pathlib.Path(tempfile.mkdtemp())
    (wd / "v.tsv").write_text("\n".join(lines) + "\n")
    op = wd / "out"
    cmd = ["python", f"{VARIANT_SCORER_DIR}/src/variant_scoring.py",
           "--list", str(wd / "v.tsv"), "--genome", fa, "--model", model,
           "--chrom_sizes", sizes, "--out_prefix", str(op),
           "--schema", "chrombpnet", "--no_hdf5"]
    proc = subprocess.run(cmd, cwd=f"{VARIANT_SCORER_DIR}/src", capture_output=True, text=True)
    if proc.returncode != 0:
        (rdir / f"chunk{idx:03d}.ERROR.txt").write_text(proc.stderr[-4000:]); VOL.commit()
        raise RuntimeError(f"chunk {idx} failed: {proc.stderr[-300:]}")
    cf.write_bytes(pathlib.Path(str(op) + ".variant_scores.tsv").read_bytes())
    VOL.commit()
    return idx


@app.function(volumes={VOL_MNT: VOL}, timeout=3 * 60 * 60)
def sweep_parallel(tsv_bytes: bytes, out_name: str, chunk_size: int = 400,
                   context: str = DEFAULT_CONTEXT) -> dict:
    """Fan the sweep out across many containers in parallel via score_chunk.map(),
    then combine. Robust (spawned) + fast (parallel). Idempotent chunks = resumable."""
    lines = tsv_bytes.decode().splitlines()
    chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]
    args = [(i, ch, out_name, context) for i, ch in enumerate(chunks)]
    done = list(score_chunk.map(args, return_exceptions=True))  # PARALLEL fan-out

    # combine whatever chunks succeeded
    rdir = VOL_MNT / "results" / f"{out_name}.chunks"
    VOL.reload()
    combined, header = [], False
    for i in range(len(chunks)):
        cf = rdir / f"chunk{i:03d}.tsv"
        if not cf.exists():
            continue
        rows = cf.read_text().splitlines()
        if not rows:
            continue
        if not header:
            combined.append(rows[0]); header = True
        combined.extend(rows[1:])
    out = VOL_MNT / "results" / out_name
    out.write_text("\n".join(combined) + "\n"); VOL.commit()
    n_ok = sum(1 for d in done if isinstance(d, int))
    return {"chunks_total": len(chunks), "chunks_ok": n_ok, "rows": max(0, len(combined) - 1)}


@app.local_entrypoint()
def sweep(tsv: str, out_name: str = "functional_sweep.variant_scores.tsv",
          context: str = DEFAULT_CONTEXT):
    """Launch a detach-safe sweep. Run with `modal run --detach` so the compute
    survives a client disconnect; results land on the volume, fetch with fetch_result."""
    data = pathlib.Path(tsv).read_bytes()
    print(score_to_volume.remote(data, out_name, context))


@app.local_entrypoint()
def fetch_result(name: str, out: str):
    data = read_result.remote(name)
    if data is None:
        print(f"result '{name}' not ready yet on the volume")
        return
    p = pathlib.Path(out); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    print("wrote", p, len(data), "bytes")


@app.function(
    volumes={VOL_MNT: VOL},
    secrets=[modal.Secret.from_name("synapse-auth")],
    timeout=2 * 60 * 60,
)
def shap_tsv(tsv_bytes: bytes, context: str = DEFAULT_CONTEXT) -> bytes:
    """Run variant_shap.py (DeepSHAP counts contributions) and return a compact
    .npz (so the local renderer needs no deepdish): per variant, the ref/alt
    projected per-base contribution and the ref/alt sequence indices."""
    import io
    import subprocess
    import tempfile

    import numpy as np

    syn = _synapse_login()
    model = _find_model_h5(syn, CONTEXTS[context])
    fa = VOL_MNT / "genome" / "hg38.analysisSet.fa"
    sizes = VOL_MNT / "genome" / "hg38.chrom.sizes"

    workdir = pathlib.Path(tempfile.mkdtemp())
    (workdir / "variants.tsv").write_bytes(tsv_bytes)
    out_prefix = workdir / "ncypher"

    cmd = [
        "python", f"{VARIANT_SCORER_DIR}/src/variant_shap.py",
        "--list", str(workdir / "variants.tsv"),
        "--genome", str(fa),
        "--model", model,
        "--chrom_sizes", str(sizes),
        "--out_prefix", str(out_prefix),
        "--schema", "chrombpnet",
    ]
    proc = subprocess.run(cmd, cwd=f"{VARIANT_SCORER_DIR}/src", capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "variant_shap.py failed\n"
            f"--- STDOUT (tail) ---\n{proc.stdout[-4000:]}\n"
            f"--- STDERR (tail) ---\n{proc.stderr[-4000:]}"
        )

    import deepdish as dd

    d = dd.io.load(str(out_prefix) + ".variant_shap.counts.h5")
    proj = np.asarray(d["projected_shap"]["seq"], dtype=np.float32)  # (2N, 4, L)
    raw = np.asarray(d["raw"]["seq"], dtype=np.int8)                 # (2N, 4, L)
    ids = np.asarray(d["variant_ids"]).astype(str)
    alleles = np.asarray(d["alleles"]).astype(int)

    contrib = proj.sum(axis=1)          # (2N, L) per-base contribution
    seq_idx = raw.argmax(axis=1).astype(np.int8)  # (2N, L) ACGT indices

    uniq = list(dict.fromkeys(ids[alleles == 0]))  # preserve order, ref rows
    L = contrib.shape[1]
    ref_c = np.zeros((len(uniq), L), np.float32)
    alt_c = np.zeros((len(uniq), L), np.float32)
    ref_s = np.zeros((len(uniq), L), np.int8)
    alt_s = np.zeros((len(uniq), L), np.int8)
    for i, vid in enumerate(uniq):
        r = np.where((ids == vid) & (alleles == 0))[0][0]
        a = np.where((ids == vid) & (alleles == 1))[0][0]
        ref_c[i], alt_c[i], ref_s[i], alt_s[i] = contrib[r], contrib[a], seq_idx[r], seq_idx[a]

    buf = io.BytesIO()
    np.savez_compressed(
        buf, variant_ids=np.array(uniq), ref_contrib=ref_c, alt_contrib=alt_c,
        ref_seq=ref_s, alt_seq=alt_s, input_len=np.array([L]),
    )
    return buf.getvalue()


@app.function(
    volumes={VOL_MNT: VOL},
    secrets=[modal.Secret.from_name("synapse-auth")],
    timeout=3 * 60 * 60,
    memory=32768,
    cpu=8.0,
)
def shap_to_volume(tsv_bytes: bytes, out_name: str, context: str = DEFAULT_CONTEXT) -> dict:
    """Detach-safe DeepSHAP: compute the compact saliency .npz and write it to the
    volume (/vol/results/<out_name>). Retrieve with fetch_result."""
    data = shap_tsv.local(tsv_bytes, context)  # run the shap body inline in this container
    dest = VOL_MNT / "results" / out_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    VOL.commit()
    return {"path": str(dest), "bytes": len(data)}


@app.function(
    volumes={VOL_MNT: VOL},
    secrets=[modal.Secret.from_name("synapse-auth")],
    timeout=6 * 60 * 60,
    memory=16384,
    cpu=4.0,
)
def contribs_peaks_run(bed_bytes: bytes, context: str = DEFAULT_CONTEXT) -> bytes:
    """Thin Modal wrapper around _contribs_peaks_impl (kept for the small-N path)."""
    return _contribs_peaks_impl(bed_bytes, context)


def _contribs_peaks_impl(bed_bytes: bytes, context: str = DEFAULT_CONTEXT) -> bytes:
    """A4: DeepSHAP contribution scores over PEAK REGIONS, for TF-MoDISco.

    Reuses the kundajelab variant-scorer's variant_shap.py by treating each peak
    window as a pseudo-variant at its centre (ref = the genomic base, alt = a
    different base). The REF-side per-base contribution over the 2114 bp window is
    exactly the region contribution TF-MoDISco needs; the alt side is discarded.

    Returns a compressed .npz with:
      seqs         (N, 4, L)  one-hot reference sequence
      hyp_contribs (N, 4, L)  per-base DeepSHAP contribution (projected)
      names        (N,)       peak names

    VERIFY ON A LIVE MODAL RUN (two points a real run must confirm, then adjust):
      1. Contribution type. TF-MoDISco wants HYPOTHETICAL contributions. This saves
         projected_shap.seq (projected onto the present base). If variant_shap's h5
         also exposes a hypothetical key, prefer it; else a chrombpnet
         `contribs_bw --hyp` pass is the clean upgrade. modisco-lite runs on this
         either way; hypothetical just sharpens the motifs.
      2. Array orientation. This saves (N, 4, L). Confirm modisco-lite wants
         (N, 4, L) and not (N, L, 4) for the deposited version, and transpose if so.
    """
    import io
    import subprocess
    import tempfile

    import numpy as np
    import pyfaidx

    syn = _synapse_login()
    model = _find_model_h5(syn, CONTEXTS[context])
    fa_path = VOL_MNT / "genome" / "hg38.analysisSet.fa"
    sizes = VOL_MNT / "genome" / "hg38.chrom.sizes"
    fa = pyfaidx.Fasta(str(fa_path))

    # peak-window BED -> chrombpnet-schema pseudo-variant TSV (one per centre)
    lines = []
    for raw in bed_bytes.decode().splitlines():
        if not raw.strip():
            continue
        c = raw.split("\t")
        chrom, ws, we = c[0], int(c[1]), int(c[2])
        name = c[3] if len(c) > 3 else f"{chrom}:{ws}"
        centre = (ws + we) // 2
        try:
            ref = fa[chrom][centre].seq.upper()
        except Exception:
            continue
        if ref not in "ACGT":
            continue
        alt = "A" if ref != "A" else "C"
        lines.append(f"{chrom}\t{centre}\t{ref}\t{alt}\t{name}")

    workdir = pathlib.Path(tempfile.mkdtemp())
    (workdir / "peaks.tsv").write_text("\n".join(lines) + "\n")
    out_prefix = workdir / "a4"

    cmd = [
        "python", f"{VARIANT_SCORER_DIR}/src/variant_shap.py",
        "--list", str(workdir / "peaks.tsv"), "--genome", str(fa_path),
        "--model", model, "--chrom_sizes", str(sizes),
        "--out_prefix", str(out_prefix), "--schema", "chrombpnet",
        "--batch_size", "64",  # small batch keeps peak RAM low (fits 16 GiB); CPU time unchanged
    ]
    proc = subprocess.run(cmd, cwd=f"{VARIANT_SCORER_DIR}/src", capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "variant_shap.py failed\n"
            f"--- STDERR (tail) ---\n{proc.stderr[-4000:]}"
        )

    import deepdish as dd

    d = dd.io.load(str(out_prefix) + ".variant_shap.counts.h5")
    proj = np.asarray(d["projected_shap"]["seq"], dtype=np.float32)  # (2N, 4, L)
    raw_oh = np.asarray(d["raw"]["seq"], dtype=np.int8)              # (2N, 4, L)
    alleles = np.asarray(d["alleles"]).astype(int)
    ids = np.asarray(d["variant_ids"]).astype(str)

    ref_rows = np.where(alleles == 0)[0]  # keep the reference-sequence side only
    seqs = raw_oh[ref_rows]      # (N, 4, L)
    hyp = proj[ref_rows]         # (N, 4, L)
    names = ids[ref_rows]

    buf = io.BytesIO()
    np.savez_compressed(buf, seqs=seqs, hyp_contribs=hyp, names=names)
    return buf.getvalue()


@app.function(
    volumes={VOL_MNT: VOL},
    secrets=[modal.Secret.from_name("synapse-auth")],
    timeout=6 * 60 * 60,
    memory=16384,
    cpu=4.0,
)
def contribs_peaks_to_volume(bed_bytes: bytes, out_name: str, context: str = DEFAULT_CONTEXT) -> dict:
    """Detach-safe A4 contributions: compute and WRITE the tfmodisco .npz to the
    volume (/vol/results/<out_name>) so a disconnected client cannot lose the
    compute. Retrieve with fetch_result."""
    data = _contribs_peaks_impl(bed_bytes, context)
    dest = VOL_MNT / "results" / out_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    VOL.commit()
    return {"path": str(dest), "bytes": len(data)}


@app.function(volumes={VOL_MNT: VOL}, timeout=8 * 60 * 60)
def contribs_peaks_orchestrate(bed_bytes: bytes, n_chunks: int = 16,
                               out_name: str = "a4_c15_contribs.npz",
                               context: str = DEFAULT_CONTEXT) -> dict:
    """A4 detach-safe genome-wide contributions: split the peak BED into
    ``n_chunks``, fan the per-chunk DeepSHAP across containers with Modal's
    server-side ``.map`` (independent of the client connection), concatenate the
    returned arrays IN A CONTAINER (data plane, not the client's blocked blob
    proxy), and write ONE tfmodisco-ready .npz to /vol/results/<out_name>.

    Retrieve the single output via the job surface (a small job that copies the
    volume file into ./out/). This is the robust path for the 10k-peak A4 run.
    """
    import io
    import math

    import numpy as np

    lines = [l for l in bed_bytes.decode().splitlines() if l.strip()]
    per = math.ceil(len(lines) / n_chunks)
    chunks = [("\n".join(lines[i * per:(i + 1) * per]) + "\n").encode()
              for i in range(n_chunks) if lines[i * per:(i + 1) * per]]

    seqs_parts, hyp_parts, name_parts = [], [], []
    # server-side parallel map; each element is a compressed npz (bytes)
    for data in contribs_peaks_run.map(chunks, kwargs={"context": context}):
        d = np.load(io.BytesIO(data))
        seqs_parts.append(d["seqs"])
        hyp_parts.append(d["hyp_contribs"])
        name_parts.append(d["names"])

    seqs = np.concatenate(seqs_parts, axis=0)
    hyp = np.concatenate(hyp_parts, axis=0)
    names = np.concatenate(name_parts, axis=0)

    dest = VOL_MNT / "results" / out_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    np.savez_compressed(buf, seqs=seqs, hyp_contribs=hyp, names=names)
    dest.write_bytes(buf.getvalue())
    VOL.commit()
    return {"path": str(dest), "n": int(seqs.shape[0]), "bytes": dest.stat().st_size,
            "shape": list(seqs.shape)}


# --- local entrypoints -------------------------------------------------------
@app.local_entrypoint()
def prepare_all(context: str = DEFAULT_CONTEXT):
    print(prepare.remote(context))
    print("model:", fetch_model.remote(context))


@app.local_entrypoint()
def score(tsv: str, context: str = DEFAULT_CONTEXT, out: str = "data/scored/ncypher.variant_scores.tsv"):
    data = pathlib.Path(tsv).read_bytes()
    result = score_tsv.remote(data, context)
    outp = pathlib.Path(out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_bytes(result)
    print("wrote", outp)


@app.local_entrypoint()
def saliency(tsv: str, context: str = DEFAULT_CONTEXT, out: str = "data/scored/ncypher.shap.npz"):
    data = pathlib.Path(tsv).read_bytes()
    result = shap_tsv.remote(data, context)
    outp = pathlib.Path(out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_bytes(result)
    print("wrote", outp)


@app.local_entrypoint()
def contribs_peaks(bed: str, context: str = DEFAULT_CONTEXT,
                   out_name: str = "a4_c15_contribs.npz"):
    """A4: DeepSHAP contributions over the c15 peak windows for TF-MoDISco.

    Detach-safe: writes the .npz to the Modal volume, then fetch it locally:
      modal run --detach modal/score_variants.py::contribs_peaks --bed data/dmg/enhancers/a4_c15_peaks_subset.bed --context opc
      modal run modal/score_variants.py::fetch_result --name a4_c15_contribs.npz --out data/dmg/enhancers/a4_c15_contribs.npz
    Run the heavy job with `modal run --detach` (30k regions of DeepSHAP take a while)."""
    data = pathlib.Path(bed).read_bytes()
    print(contribs_peaks_to_volume.remote(data, out_name, context))
