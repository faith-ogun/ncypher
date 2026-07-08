/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Light theme surfaces (the builder cannot read dark UIs)
        page: "#F6F8F9",
        card: "#FFFFFF",
        ink: "#0F1E24", // near-black teal-slate for body text
        muted: "#59717A", // secondary text
        faint: "#8497A0", // tertiary text
        line: "#E3E9EC", // borders
        lineStrong: "#CDD8DD",
        // Brand accent
        teal: {
          50: "#E7F6F3",
          100: "#C9ECE6",
          200: "#95DBD0",
          300: "#5FC6B7",
          400: "#2FAF9E",
          500: "#0E9E8A", // primary accent
          600: "#0B7F6F",
          700: "#0A6558",
          800: "#084F45",
        },
        // Verdict colours
        go: "#0E9E8A",
        hold: "#C77D11",
        nogo: "#DA4A42",
        // DNA base colours (fixed spec)
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
        card: "0 1px 2px rgba(15,30,36,0.04), 0 4px 16px rgba(15,30,36,0.05)",
        pill: "0 1px 2px rgba(15,30,36,0.10)",
        lift: "0 8px 30px rgba(15,30,36,0.08)",
      },
      borderRadius: {
        xl2: "1.1rem",
      },
    },
  },
  plugins: [],
};
