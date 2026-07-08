import data from "../data/ncypher.json";
import type { NCypherData } from "../types";
import { THERAPY_AXES } from "../data/content";
import { Card, SectionLabel, Tag, Stat } from "../components/ui";
import { HBarChart, type HBarRow } from "../components/HBarChart";
import { ViewHeader } from "./VariantTriage";
import { fmtP, fmtNum, fmtSigned } from "../lib/format";

const D = data as unknown as NCypherData;

export function TheFinding() {
  const f = D.finding;
  const c = D.cohort;

  const bars: HBarRow[] = f.axisDecomposition.map((a) => ({
    label: a.axis,
    sublabel: a.subset,
    value: a.fold,
    display: `${fmtNum(a.fold, 2)}x`,
    tone: a.sig === "ns" ? "grey" : "teal",
    annotation: `p = ${fmtP(a.p)}`,
    annotationTone: a.sig,
    emphasise: a.axis.startsWith("Converged"),
  }));

  return (
    <div className="mx-auto max-w-6xl px-8 py-8">
      <ViewHeader
        eyebrow="The finding"
        title="They do not recur at a locus. They converge on a pathway."
        blurb="Across 10,869 model-scored somatic non-coding variants in 152 DMG patients, the convergence shortlist concentrates in the neurodevelopmental gene programme. Decomposed by axis, this is a concrete, quantitative argument for why you need multi-axis convergence rather than a single scorer."
      />

      {/* Honest-negative strip */}
      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard value={c.n_scored.toLocaleString("en-GB")} label="Variants scored" sub="OPC-regulatory somatic SNVs" />
        <StatCard value={String(c.n_converged)} label="Two-axis converged" sub="chromatin + constraint" tone="teal" />
        <StatCard value={String(c.n_recurrent_converged)} label="Recurrent among converged" sub="each private, one patient" tone="amber" />
        <StatCard value={String(c.n_driver_genes)} label="In canonical DMG drivers" sub="the coding story is solved" tone="amber" />
      </div>

      {/* Axis decomposition chart */}
      <Card className="mt-6 p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <SectionLabel>Neurodevelopmental-programme enrichment, decomposed by axis</SectionLabel>
            <p className="mt-1.5 max-w-2xl text-[13.5px] leading-relaxed text-muted">
              Fold enrichment for a pre-registered canonical neurodevelopmental gene set, over an
              OPC-peak background (base rate {fmtNum(f.baseRate, 2)}%). Length-controlled.
            </p>
          </div>
        </div>

        <div className="mt-6">
          <HBarChart rows={bars} max={3.0} baseline={1.0} baselineLabel="no enrichment (1.0x)" unit="fold vs base rate" />
        </div>

        <div className="mt-6 grid grid-cols-1 gap-3 md:grid-cols-3">
          <ReadCell
            tone="grey"
            head="Chromatin alone is not enough"
            body="ChromBPNet fires on accessibility-changing sequence irrespective of the host gene. Not neural-enriched once gene length is controlled (1.13x, p = 0.36, n.s.). This is the honest limit of a single accessibility scorer."
          />
          <ReadCell
            tone="teal"
            head="Constraint carries the signal"
            body="Deeply conserved non-coding elements sit near neurodevelopmental genes. 2.62x at p = 4.8e-13, the statistically bulletproof number, and a label the chromatin model never trained on."
          />
          <ReadCell
            tone="teal"
            head="Convergence inherits the focus"
            body="The shortlist stays neurodevelopmentally specific (2.62x, p = 0.029) because it is multi-axis: the constraint focus, plus the chromatin filter. That is the argument for the whole method."
          />
        </div>

        <p className="mt-4 rounded-lg border border-line bg-[#fefce8]/70 px-4 py-3 text-[12.5px] leading-snug text-ink/90">
          <span className="font-semibold">Stated plainly.</span> The converged p = 0.029 is nominal,
          and several gene sets were tested before the strict canonical one, so treat it as
          suggestive, not decisive. The bulletproof number is the constraint-axis p = 4.8e-13. The
          neural focus is a constraint-axis property, not a chromatin-model finding.
        </p>
      </Card>

      {/* NPAS3 lead */}
      <Card className="mt-6 overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line bg-brand-50/40 px-6 py-4">
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-[19px] font-bold text-ink">NPAS3</h2>
              <Tag tone="teal">Lead candidate</Tag>
            </div>
            <p className="mt-0.5 text-[13px] text-muted">
              The single most elevatable hero: validate this first
            </p>
          </div>
          <div className="flex gap-6">
            <Stat value={String(f.npas3.n_patients)} label="patients" sub="3 distinct enhancers" />
            <Stat value={`${Math.round(f.npas3.deepshap_collapse * 100)}%`} label="DeepSHAP collapse" sub="0.299 to 0.059" tone="teal" />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 px-6 py-5 lg:grid-cols-[1.3fr_1fr]">
          {/* Variant table */}
          <div>
            <SectionLabel>Three distinct high-impact variants, three patients</SectionLabel>
            <div className="mt-3 overflow-x-auto">
              <table className="w-full border-collapse text-[12.5px]">
                <thead>
                  <tr className="border-b border-line text-left text-[11px] uppercase tracking-wide text-faint">
                    <th className="py-2 pr-3 font-semibold">Variant</th>
                    <th className="py-2 pr-3 font-semibold">Patient</th>
                    <th className="py-2 pr-3 text-right font-semibold">log2FC</th>
                    <th className="py-2 pr-3 text-right font-semibold">phyloP</th>
                    <th className="py-2 font-semibold">Flag</th>
                  </tr>
                </thead>
                <tbody>
                  {f.npas3.variants.map((v) => (
                    <tr key={v.key} className="border-b border-line/70">
                      <td className="py-2 pr-3 font-mono text-[11.5px] text-ink">{v.key}</td>
                      <td className="py-2 pr-3 font-mono text-[11px] text-muted">{v.patient}</td>
                      <td className="py-2 pr-3 text-right font-mono tnum text-ink">
                        {fmtSigned(v.logfc, 3)}
                      </td>
                      <td className="py-2 pr-3 text-right font-mono tnum text-ink">
                        {fmtNum(v.phylop, 2)}
                      </td>
                      <td className="py-2">
                        {v.flag === "converged" ? (
                          <Tag tone="teal">converged</Tag>
                        ) : (
                          <Tag>high-impact</Tag>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-3 text-[12px] leading-snug text-muted">
              Enrichment for high-impact within NPAS3: 3 observed vs {fmtNum(f.npas3.expected_hi, 2)}{" "}
              expected at the 6.9% base rate, binomial p = {fmtNum(f.npas3.binomial_p, 3)}. The
              converged variant shows an 80% collapse of local DeepSHAP contribution at the variant
              base.
            </p>
          </div>

          {/* Why + caveats */}
          <div className="space-y-4">
            <div className="rounded-xl border border-line bg-page/50 p-4">
              <div className="text-[12px] font-semibold uppercase tracking-wide text-faint">
                External validation
              </div>
              <p className="mt-1.5 text-[12.5px] leading-snug text-ink/90">
                NPAS3 is an experimentally validated tumour suppressor in malignant glioma (Moreira
                2011) and a tumour-suppressor master regulator in paediatric medulloblastoma
                (Michaelsen 2025). The accessibility-loss direction fits tumour-suppressor silencing.
              </p>
            </div>
            <div className="rounded-xl border border-[#fde68a] bg-[#fefce8]/70 p-4">
              <div className="text-[12px] font-semibold uppercase tracking-wide text-[#a16207]">
                Honest caveats
              </div>
              <ul className="mt-1.5 space-y-1.5 text-[12.5px] leading-snug text-ink/90">
                <li>Gene-level recurrence (3 enhancers), not a single recurrent element.</li>
                <li>Per-gene binomial p = 0.014 does NOT survive Bonferroni across ~6,800 genes.</li>
                <li>Only 1 of 3 variants is fully converged. A lead, not a genome-wide driver.</li>
              </ul>
            </div>
          </div>
        </div>
      </Card>

      {/* Therapy mapping + converged genes */}
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[1.5fr_1fr]">
        <Card className="p-6">
          <SectionLabel>The programme maps onto real DMG therapeutic axes</SectionLabel>
          <p className="mt-1.5 text-[13px] leading-relaxed text-muted">
            Hypothesis routing, not a treatment recommendation. If the target is an undruggable TF,
            nominate the actionable node one step away. Every node is an independently published DMG
            programme.
          </p>
          <div className="mt-4 space-y-2.5">
            {THERAPY_AXES.map((t) => (
              <div key={t.id} className="flex gap-3 rounded-xl border border-line bg-page/40 p-3.5">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-brand-500 font-mono text-[13px] font-bold text-white">
                  {t.id}
                </div>
                <div className="min-w-0">
                  <div className="text-[13.5px] font-semibold text-ink">{t.name}</div>
                  <div className="mt-0.5 text-[12px] text-muted">
                    <span className="text-faint">from </span>
                    {t.routeFrom}
                  </div>
                  <div className="mt-1.5 flex flex-wrap items-center gap-2">
                    <Tag tone="teal">{t.node}</Tag>
                    <span className="text-[11px] italic text-muted">{t.confidence}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <p className="mt-3 text-[11.5px] leading-snug text-muted">
            Every row carries the same closing guardrail: a mechanism-anchored hypothesis to
            validate, paired with a blood-brain-barrier delivery story. NCypher does not predict drug
            response.
          </p>
        </Card>

        <Card className="p-6">
          <SectionLabel>The six canonical converged genes</SectionLabel>
          <p className="mt-1.5 text-[12.5px] text-muted">
            Conspicuously neurodevelopmental, which is what the enrichment quantifies.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {D.finding.convergedGenes.map((g) => (
              <span
                key={g}
                className="rounded-lg border border-brand-200 bg-brand-50 px-3 py-1.5 font-mono text-[13px] font-semibold text-brand-700"
              >
                {g}
              </span>
            ))}
          </div>
          <div className="mt-5 rounded-xl border border-line bg-page/50 p-4 text-[12.5px] leading-snug text-ink/90">
            Extending to high-impact adds BCAS1 (oligodendrocyte differentiation), NFIX, TCF4 and
            NRXN3. The list is neurodevelopmental because convergence is multi-axis, not because the
            chromatin model prefers neural DNA.
          </div>
        </Card>
      </div>
    </div>
  );
}

function StatCard({
  value,
  label,
  sub,
  tone = "ink",
}: {
  value: string;
  label: string;
  sub: string;
  tone?: "ink" | "teal" | "amber";
}) {
  return (
    <Card className="p-4">
      <Stat value={value} label={label} sub={sub} tone={tone} />
    </Card>
  );
}

function ReadCell({
  tone,
  head,
  body,
}: {
  tone: "grey" | "teal";
  head: string;
  body: string;
}) {
  const border = tone === "teal" ? "border-l-brand-400" : "border-l-[#94a3b8]";
  return (
    <div className={`rounded-lg border border-line border-l-[3px] bg-card px-4 py-3 ${border}`}>
      <div className="text-[13px] font-bold text-ink">{head}</div>
      <p className="mt-1.5 text-[12.5px] leading-snug text-muted">{body}</p>
    </div>
  );
}
