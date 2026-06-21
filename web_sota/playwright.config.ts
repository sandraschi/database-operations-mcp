import { defineConfig } from '@playwright/test';
export default defineConfig({
    testDir: './e2e', timeout: 60000, retries: 1,
    use: { baseURL: 'http://localhost:10709', headless: true, screenshot: 'only-on-failure' },
    webServer: {
        command: 'uv run python -m database_operations_mcp.server --port 10708',
        port: 10708, timeout: 30000, reuseExistingServer: false
    }
});
