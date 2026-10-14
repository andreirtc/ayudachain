import { test as base } from "@playwright/test";
export * from "@playwright/test";

export const API = process.env.AYUDACHAIN_TEST_API_URL || "http://127.0.0.1:8301";
export const BASE_URL = process.env.AYUDACHAIN_TEST_BASE_URL || "http://127.0.0.1:3301";

export const test = base.extend<{ isolatedRecords: void }>({
  isolatedRecords: [async ({ context, request }, use) => {
    const reset = await request.post(API + "/__test__/reset", {
      headers: { "X-AyudaChain-Test-Reset": "synthetic-e2e-reset-only" },
    });
    if (!reset.ok()) throw new Error("Disposable browser fixture reset failed: " + reset.status());
    await context.route(/http:\/\/(?:127\.0\.0\.1|localhost):8000\//, route => {
      const url = new URL(route.request().url());
      const target = new URL(API);
      url.hostname = target.hostname;
      url.port = target.port;
      return route.continue({ url: url.toString() });
    });
    await use();
  }, { auto: true }],
});
