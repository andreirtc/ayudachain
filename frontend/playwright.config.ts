import { defineConfig } from "@playwright/test";

const baseURL = process.env.AYUDACHAIN_TEST_BASE_URL || "http://127.0.0.1:3301";
const apiURL = process.env.AYUDACHAIN_TEST_API_URL || "http://127.0.0.1:8301";
for (const value of [baseURL, apiURL]) {
  const url = new URL(value);
  if (url.protocol !== "http:" || !["127.0.0.1", "localhost"].includes(url.hostname)) throw new Error("Browser tests require owned loopback servers");
}
const frontendPort = new URL(baseURL).port;

export default defineConfig({
  testDir: "./tests/e2e",
  workers: 1,
  retries: 0,
  timeout: 45000,
  reporter: "list",
  use: { baseURL, headless: true, channel: process.platform === "win32" ? "msedge" : undefined, trace: "retain-on-failure" },
  projects: [
    { name: "desktop", use: { viewport: { width: 1440, height: 900 } } },
    { name: "phone", use: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
  ],
  webServer: [
    { command: process.platform === "win32" ? '"..\\backend\\.venv\\Scripts\\python.exe" "..\\backend\\tests\\e2e_server.py"' : "../backend/.venv/bin/python ../backend/tests/e2e_server.py", url: apiURL + "/api/public/receipts", env: { AYUDACHAIN_TEST_BASE_URL: baseURL, AYUDACHAIN_TEST_API_URL: apiURL, AYUDACHAIN_E2E_RESET_ENABLED: "1" }, reuseExistingServer: false, timeout: 60000 },
    { command: "node node_modules/next/dist/bin/next start --hostname 127.0.0.1 --port " + frontendPort, url: baseURL, reuseExistingServer: false, timeout: 60000 },
  ],
});
