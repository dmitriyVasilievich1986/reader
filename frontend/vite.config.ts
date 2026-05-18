import react from "@vitejs/plugin-react";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

const __dirname = dirname(fileURLToPath(import.meta.url));

let appVersion = "1.0.0";
try {
  appVersion = (
    JSON.parse(
      readFileSync(resolve(__dirname, "application-version.json"), "utf-8"),
    ) as {
      version: string;
    }
  ).version;
} catch (error) {
  console.error("Error reading application version:", error);
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    "process.env": { mode: "produciton" },
    "import.meta.env.VITE_APP_VERSION": JSON.stringify(appVersion),
  },
  resolve: {
    alias: {
      "@components": resolve(__dirname, "./src/components"),
      "@pages": resolve(__dirname, "./src/pages"),
      "@store": resolve(__dirname, "./src/store"),
      "@services": resolve(__dirname, "./src/services"),
    },
  },
  build: {
    outDir: resolve(__dirname, "../backend/static"),
    emptyOutDir: false,
    rollupOptions: {
      output: {
        assetFileNames: "assets/[name]-[hash][extname]",
        chunkFileNames: "assets/[name]-[hash].js",
        entryFileNames: "assets/[name]-[hash].js",
      },
    },
  },
});
