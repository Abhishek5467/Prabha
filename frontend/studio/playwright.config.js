import {defineConfig} from '@playwright/test';

export default defineConfig({
  testDir: './tests/ui',
  timeout: 45_000,
  expect: {timeout: 10_000},
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:8000',
    viewport: {width: 1440, height: 1000},
    launchOptions: {
      executablePath: process.env.PRABHA_CHROMIUM || undefined,
      args: process.env.PRABHA_CHROMIUM_ARGS ? JSON.parse(process.env.PRABHA_CHROMIUM_ARGS) : []
    }
  },
  webServer: [
    {command: 'python ../../frontend/web/server.py', url: 'http://127.0.0.1:8000/api/health',
      timeout: 30_000, env: {PORT: '8000'}, reuseExistingServer: false},
    {command: 'python tests/serve_static.py', url: 'http://127.0.0.1:8081/Prabha/',
      timeout: 30_000, reuseExistingServer: false}
  ]
});
