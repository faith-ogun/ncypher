import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Self-contained SPA. No backend, no Modal, no external hosts at runtime.
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "dist",
    assetsInlineLimit: 0,
  },
});
