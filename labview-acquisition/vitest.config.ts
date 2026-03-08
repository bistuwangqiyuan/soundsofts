import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  test: {
    include: ["api/test/**/*.test.ts"],
    environment: "node",
    globals: true,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "api"),
    },
  },
});
