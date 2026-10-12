import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  workers: 1,
  retries: 0,
  timeout: 45000,
  reporter: "list",
  use: { baseURL: "http://127.0.0.1:3101", headless: true, channel: process.platform === "win32" ? "msedge" : undefined, trace: "retain-on-failure" },
  projects: [
    { name: "desktop", use: { viewport: { width: 1440, height: 900 } } },
    { name: "phone", use: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
  ],
  webServer: [
    { command: process.platform === "win32" ? '"..\\backend\\.venv\\Scripts\\python.exe" "..\\backend\\tests\\e2e_server.py"' : "../backend/.venv/bin/python ../backend/tests/e2e_server.py", url: "http://127.0.0.1:8101/api/public/receipts", reuseExistingServer: false, timeout: 60000 },
    { command: "node node_modules/next/dist/bin/next start --hostname 127.0.0.1 --port 3101", url: "http://127.0.0.1:3101", reuseExistingServer: false, timeout: 60000 },
  ],
});
