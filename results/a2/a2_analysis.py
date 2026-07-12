#!/usr/bin/env python3
"""A2: harden the K27M super-enhancer constraint finding against distance-to-TSS and
replication-timing confounds. Reproducible end-to-end. Seeds fixed at 0.

Inputs (fetched or staged):
  - data/dmg/enhancers/a2_input.tsv                      (staged)
  - GENCODE v44 hg38 GTF (EBI FTP)                        (fetched)
  - UCSC UW Repli-seq SK-N-SH WaveSignal bigWig (hg19)    (fetched)
  - UCSC hg38ToHg19 liftover chain                        (fetched)
Outputs: a2_features.tsv.gz, a2_results.json, a2_phylop_se_confound.png
"""
import os, gzip, json, urllib.request
import numpy as np, pandas as pd
from scipy.stats import mannwhitneyu, spearmanr
import statsmodels.formula.api as smf
import pyBigWig
from pyliftover import LiftOver

IN = "data/dmg/enhancers/a2_input.tsv"
GTF_URL = "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/gencode.v44.annotation.gtf.gz"
BW_URL  = "https://hgdownload.soe.ucsc.edu/goldenPath/hg19/encodeDCC/wgEncodeUwRepliSeq/wgEncodeUwRepliSeqSknshWaveSignalRep1.bigWig"
CHAIN_URL = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/liftOver/hg38ToHg19.over.chain.gz"

def fetch(url, dst):
    if not os.path.exists(dst): urllib.request.urlretrieve(url, dst)
    return dst

def main():
    df = pd.read_csv(IN, sep="\t")
    df["in_se"] = df["in_se"].astype(str).str.strip().isin(["True","true","1"])

    # --- TSS from GENCODE v44 ---
    gtf = fetch(GTF_URL, "gencode.v44.annotation.gtf.gz")
    tss = {}
    with gzip.open(gtf, "rt") as fh:
        for line in fh:
            if line.startswith("#"): continue
            f = line.split("\t")
            if f[2] != "transcript": continue
            pos = int(f[3]) if f[6] == "+" else int(f[4])
            tss.setdefault(f[0], []).append(pos)
    tss = {c: np.sort(np.unique(v)) for c, v in tss.items()}
    def dtss(c, p):
        a = tss.get(c)
        if a is None: return np.nan
        i = np.searchsorted(a, p); cs = []
        if i < len(a): cs.append(abs(a[i]-p))
        if i > 0:      cs.append(abs(p-a[i-1]))
        return float(min(cs)) if cs else np.nan
    df["dist_tss"] = [dtss(c, p) for c, p in zip(df.chrom, df.pos)]

    # --- replication timing (hg38 -> hg19 -> WaveSignal) ---
    lo = LiftOver(fetch(CHAIN_URL, "hg38ToHg19.over.chain.gz"))
    bw = pyBigWig.open(fetch(BW_URL, "sknsh_wave.bigWig"))
    bwc = set(bw.chroms())
    rt = np.full(len(df), np.nan)
    for k, (c, p) in enumerate(zip(df.chrom, df.pos)):
        r = lo.convert_coordinate(c, p-1)
        if not r: continue
        c19, p19 = r[0][0], r[0][1]
        if c19 not in bwc: continue
        try:
            v = bw.values(c19, p19, p19+1)
            if v and not np.isnan(v[0]): rt[k] = v[0]
        except Exception: pass
    df["rep_timing"] = rt; bw.close()
    df.to_csv("a2_features.tsv.gz", sep="\t", index=False, compression="gzip")

    res = {}
    # naive
    fp = df.dropna(subset=["phylop"])
    res["naive"] = dict(
        median_in=round(fp.loc[fp.in_se,"phylop"].median(),4),
        median_out=round(fp.loc[~fp.in_se,"phylop"].median(),4),
        mwu_two_sided=mannwhitneyu(fp.loc[fp.in_se,"phylop"], fp.loc[~fp.in_se,"phylop"]).pvalue,
        mwu_one_sided=mannwhitneyu(fp.loc[fp.in_se,"phylop"], fp.loc[~fp.in_se,"phylop"], alternative="greater").pvalue)

    cc = df.dropna(subset=["phylop","rep_timing","dist_tss"]).copy()
    cc["log_dist_tss"] = np.log10(cc.dist_tss+1); cc["in_se_i"] = cc.in_se.astype(int)
    cc["dtss_dec"] = pd.qcut(cc.dist_tss,10,labels=False,duplicates="drop")
    cc["rt_dec"]   = pd.qcut(cc.rep_timing,10,labels=False,duplicates="drop")
    cc["stratum"]  = cc.dtss_dec.astype(str)+"|"+cc.rt_dec.astype(str)+"|"+cc.cls.astype(str)

    # permutation (seed 0)
    inS, outS = cc[cc.in_se], cc[~cc.in_se]
    dem = inS.stratum.value_counts()
    pool = {s: g.phylop.values for s, g in outS.groupby("stratum")}
    strata = [s for s in dem.index if s in pool and len(pool[s])>0]
    rng = np.random.default_rng(0); nm = np.empty(1000)
    for i in range(1000):
        nm[i] = np.median(np.concatenate([rng.choice(pool[s], size=dem[s], replace=True) for s in strata]))
    obs = inS[inS.stratum.isin(strata)].phylop.median()
    res["permutation"] = dict(obs_median=round(float(obs),4), null_median=round(float(np.median(nm)),4),
        null_ci=[round(float(np.percentile(nm,2.5)),4), round(float(np.percentile(nm,97.5)),4)],
        p_emp=round((np.sum(nm>=obs)+1)/1001,4), draws=1000, seed=0)

    # regressions
    mo = smf.ols("phylop ~ in_se_i + log_dist_tss + rep_timing + C(cls)", data=cc).fit(cov_type="HC3")
    mq = smf.quantreg("phylop ~ in_se_i + log_dist_tss + rep_timing + C(cls)", data=cc).fit(q=0.5)
    # bootstrap (seed 0)
    rng = np.random.default_rng(0); n = len(cc); bo = []; bm = []
    dd = cc.reset_index(drop=True)
    for _ in range(2000):
        sub = dd.iloc[rng.integers(0, n, n)]
        bo.append(smf.ols("phylop ~ in_se_i + log_dist_tss + rep_timing + C(cls)", data=sub).fit().params["in_se_i"])
        bm.append(smf.quantreg("phylop ~ in_se_i + log_dist_tss + rep_timing + C(cls)", data=sub).fit(q=0.5).params["in_se_i"])
    res["regression_ols"] = dict(coef=round(mo.params["in_se_i"],4), p=mo.pvalues["in_se_i"],
        boot_ci=[round(float(np.percentile(bo,2.5)),4), round(float(np.percentile(bo,97.5)),4)])
    res["regression_median"] = dict(coef=round(mq.params["in_se_i"],4), p=mq.pvalues["in_se_i"],
        boot_ci=[round(float(np.percentile(bm,2.5)),4), round(float(np.percentile(bm,97.5)),4)])
    res["verdict"] = "SURVIVES" if (res["permutation"]["p_emp"]<0.05 and
                                    res["regression_median"]["boot_ci"][0]>0) else "SEE NUMBERS"
    json.dump(res, open("a2_results.json","w"), indent=2, default=str)
    print(json.dumps(res, indent=2, default=str))

if __name__ == "__main__":
    main()
