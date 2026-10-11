import path from "node:path";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": path.resolve(import.meta.dirname, "src") } },
  server: { port: 5173 },
  build: {
    rollupOptions: {
      output: {
        // Firebase is large and changes rarely: give it its own long-lived cache entry.
        manualChunks: (id: string) => {
          if (id.includes("node_modules/firebase") || id.includes("node_modules/@firebase"))
            return "firebase";
          if (id.includes("node_modules/react") || id.includes("node_modules/@tanstack"))
            return "react-vendor";
          return undefined;
        },
      },
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: false,
    restoreMocks: true,
  },
});
