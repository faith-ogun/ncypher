// Small formatting helpers. British English, no em dashes.

export function fmtSigned(x: number | null | undefined, dp = 3): string {
  if (x === null || x === undefined) return "n/a";
  const s = x.toFixed(dp);
  return x >= 0 ? `+${s}` : s;
}

export function fmtNum(x: number | null | undefined, dp = 2): string {
  if (x === null || x === undefined) return "n/a";
  return x.toFixed(dp);
}

/** Format a p-value compactly: 4.8e-13, 0.029, 0.36. */
export function fmtP(p: number): string {
  if (p === 0) return "0";
  if (p < 1e-3) {
    const exp = Math.floor(Math.log10(p));
    const mant = p / Math.pow(10, exp);
    return `${mant.toFixed(1)}e${exp}`;
  }
  if (p < 0.1) return p.toFixed(3);
  return p.toFixed(2);
}

export function fmtPct(frac: number, dp = 0): string {
  return `${(frac * 100).toFixed(dp)}%`;
}

export function fmtInt(x: number): string {
  return x.toLocaleString("en-GB");
}

/** Parse and normalise a free-form variant id to the chr-pos-ref-alt key. */
export function normaliseVariantId(raw: string): string | null {
  const s = raw.trim();
  if (!s) return null;
  // Accept chr14-33788719-A-G, chr14:33788719:A:G, 14-33788719-A-G, chr14 33788719 A G
  const parts = s.replace(/[:\s]+/g, "-").split("-").filter(Boolean);
  if (parts.length !== 4) return null;
  let [chrom, pos, ref, alt] = parts;
  if (!/^chr/i.test(chrom)) chrom = `chr${chrom}`;
  chrom = chrom.toLowerCase().replace(/^chr/, "chr");
  if (!/^\d+$/.test(pos)) return null;
  ref = ref.toUpperCase();
  alt = alt.toUpperCase();
  if (!/^[ACGT]$/.test(ref) || !/^[ACGT]$/.test(alt)) return null;
  return `${chrom}-${pos}-${ref}-${alt}`;
}

export const BASE_COLOURS: Record<string, string> = {
  A: "#2E9E43",
  C: "#2F6FE0",
  G: "#C67F12",
  T: "#DA4A42",
};

export const VERDICT_META: Record<
  string,
  { label: string; colour: string; bg: string; ring: string; blurb: string }
> = {
  GO: {
    label: "GO",
    colour: "#0A6558",
    bg: "#E7F6F3",
    ring: "#0E9E8A",
    blurb: "Validate: two axes converge in domain",
  },
  HOLD: {
    label: "HOLD",
    colour: "#8A560B",
    bg: "#FBF0DE",
    ring: "#C77D11",
    blurb: "Informative disagreement: resolve before bench",
  },
  "NO-GO": {
    label: "NO-GO",
    colour: "#A32E28",
    bg: "#FBE9E8",
    ring: "#DA4A42",
    blurb: "Not promoted: single axis or out of domain",
  },
};
