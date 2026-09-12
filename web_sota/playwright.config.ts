import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  timeout: 60000,
  retries: 1,
  use: {
    baseURL: "http://localhost:10709",
    headless: true,
    screenshot: "only-on-failure",
  },
  webServer: [
    {
      command:
        "C:/Users/sandr/.local/bin/uv.exe run database-operations-mcp --http --port 10709",
      cwd: "..",
      port: 10709,
      timeout: 120000,
      reuseExistingServer: true,
    },
    {
      command: "npx vite --port 10708 --strictPort",
      port: 10708,
      timeout: 120000,
      reuseExistingServer: true,
    },
  ],
});
