import { API, BASE_URL } from "./support";
import { test, expect } from "./support";

test("local typography loads without external font services and fits both entry screens", async ({ page }, info) => {
  const fonts: string[] = [];
  page.on("request", request => { if (request.resourceType() === "font") fonts.push(request.url()); });
  await page.route(/https:\/\/(fonts.googleapis.com|fonts.gstatic.com)\//, route => route.abort());
  for (const [path, name] of [["/", "landing"], ["/sign-in", "sign-in"]]) {
    await page.goto(path);
    await page.evaluate(() => document.fonts.ready);
    const type = await page.evaluate(() => {
      const root = getComputedStyle(document.documentElement);
      const normalize = (value: string) => value.replace(/["']/g, "").trim();
      const body = normalize(getComputedStyle(document.body).fontFamily);
      const headingNode = document.querySelector("h1")!;
      const heading = normalize(getComputedStyle(headingNode).fontFamily);
      const localHeading = normalize(getComputedStyle(headingNode).getPropertyValue("--font-heading").split(",")[0]);
      return {
        bodyUsesLocal: body.includes(normalize(root.getPropertyValue("--font-body").split(",")[0])),
        headingUsesLocal: heading.includes(localHeading),
        loaded: [...document.fonts].filter(font => font.status === "loaded").length,
        fits: document.documentElement.scrollWidth <= innerWidth,
      };
    });
    expect(type).toMatchObject({ bodyUsesLocal: true, headingUsesLocal: true, fits: true });
    expect(type.loaded).toBeGreaterThanOrEqual(1);
    await page.screenshot({ path: info.outputPath(name + ".png"), fullPage: false });
  }
  expect(fonts.length).toBeGreaterThanOrEqual(2);
  expect(fonts.every(url => new URL(url).origin === BASE_URL)).toBe(true);
});
