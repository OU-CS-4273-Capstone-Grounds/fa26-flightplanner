import { defineConfig } from "vite";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const docsDir = dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  base: "/fa26-flightplanner/",

  build: {
    outDir: "dist",
    emptyOutDir: true,

    rollupOptions: {
      input: {
        main: resolve(docsDir, "index.html"),
        calculations: resolve(docsDir, "calculations.html"),
        weather: resolve(docsDir, "weather.html"),
      },
    },
  },
});