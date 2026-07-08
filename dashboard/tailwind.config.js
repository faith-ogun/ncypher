/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Light theme surfaces (the builder cannot read dark UIs)
        page: "#ffffff", // white — true page background / negative space
        card: "#ffffff", // white, elevated cards
        panel: "#e2e8f0", // cream-200, secondary panels and the sidebar
        ink: "#0e0f23", // primary text
        ink800: "#16172f", // elevated dark surface
        muted: "#3d4152", // slate, secondary text
        faint: "#64748b", // slate, tertiary text
        line: "#d5dbe6", // borders
        lineStrong: "#b9c2d1",
        // Electric-blue brand accent (scale key kept as `brand`)
        brand: {
          50: "#ecebfe",
          100: "#d9d6fe",
          200: "#bab4fd",
          300: "#8b83fc",
          400: "#443cfb",
          500: "#0600f9", // primary accent
          600: "#0600f9", // accent text (exact brand hex)
          700: "#0500cc", // deeper accent text on tints
          800: "#0400a0",
        },
        // Verdict colours
        go: "#0600f9", // electric blue
        hold: "#eab308", // amber
        nogo: "#DA4A42", // red (kept)
        amber: "#eab308", // amber highlight
        // DNA base colours (fixed spec, sequence data only)
        baseA: "#2E9E43",
        baseC: "#2F6FE0",
        baseG: "#C67F12",
        baseT: "#DA4A42",
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "SF Mono",
          "Menlo",
          "Consolas",
          "Liberation Mono",
          "monospace",
        ],
      },
      boxShadow: {
        card: "0 1px 2px rgba(14,15,35,0.04), 0 4px 16px rgba(14,15,35,0.06)",
        pill: "0 1px 2px rgba(14,15,35,0.10)",
        lift: "0 8px 30px rgba(14,15,35,0.09)",
      },
      borderRadius: {
        xl2: "1.1rem",
      },
    },
  },
  plugins: [],
};
