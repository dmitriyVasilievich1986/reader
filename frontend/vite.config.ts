import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "node:path";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    "process.env": { mode: "produciton" },
  },
  resolve: {
    alias: {
      "@components": resolve(__dirname, "./src/components"),
      "@pages": resolve(__dirname, "./src/pages"),
      "@services": resolve(__dirname, "./src/services"),
    },
  },
  build: {
    outDir: "../static/js",
    emptyOutDir: true,
    lib: {
      entry: "src/main.tsx",
      name: "Reader",
      // the proper extensions will be added
      fileName: "main",
    },
    commonjsOptions: {
      include: /node_modules/, // Ensure CommonJS dependencies are included
    },
    rollupOptions: {
      // make sure to externalize deps that shouldn't be bundled
      // into your library
      external: [],
      // external: ["react"],
      output: {
        // Provide global variables to use in the UMD build
        // for externalized deps
        globals: {
          react: "React",
        },
      },
    },
  },
});
