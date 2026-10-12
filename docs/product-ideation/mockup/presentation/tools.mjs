// Shared helpers for extract-screens.mjs and render.mjs.
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import vm from "node:vm";
import puppeteer from "puppeteer-core";

export const HERE = dirname(fileURLToPath(import.meta.url));
export const MOCKUP = join(HERE, "..", "index.html");
export const fileUrl = (path) => pathToFileURL(path).href;

// Uses an installed browser; nothing is downloaded. Override with CHROME_PATH.
export function findChrome() {
  const env = process.env;
  const candidates = [
    env.CHROME_PATH,
    join(env.ProgramFiles || "", "Google/Chrome/Application/chrome.exe"),
    join(env["ProgramFiles(x86)"] || "", "Google/Chrome/Application/chrome.exe"),
    join(env.LOCALAPPDATA || "", "Google/Chrome/Application/chrome.exe"),
    join(env["ProgramFiles(x86)"] || "", "Microsoft/Edge/Application/msedge.exe"),
    join(env.ProgramFiles || "", "Microsoft/Edge/Application/msedge.exe"),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
  ];
  const found = candidates.find((p) => p && existsSync(p));
  if (!found) throw new Error("No Chrome or Edge found. Set CHROME_PATH to a Chromium-based browser.");
  return found;
}

export function launch() {
  return puppeteer.launch({
    executablePath: findChrome(),
    headless: true,
    args: ["--force-device-scale-factor=1", "--hide-scrollbars", "--font-render-hinting=none", "--force-color-profile=srgb"],
  });
}

// storyboard.js is a plain browser script; evaluate it here to read the same data.
export function loadStoryboard() {
  const context = { globalThis: {} };
  vm.runInNewContext(readFileSync(join(HERE, "storyboard.js"), "utf8"), context);
  return context.globalThis.STORYBOARD;
}
