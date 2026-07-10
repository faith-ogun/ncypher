import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Self-contained SPA. No backend, no Modal, no external hosts at runtime.
// base: relative ("./") for local dev + the Claude Science demo; on GitHub Pages
// the deploy workflow sets GITHUB_PAGES=true so assets resolve under /ncypher/.
export default defineConfig({
  plugins: [react()],
  base: process.env.GITHUB_PAGES ? "/ncypher/" : "./",
  server: { port: 5180, strictPort: false },
  build: {
    outDir: "dist",
    assetsInlineLimit: 0,
  },
});
