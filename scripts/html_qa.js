#!/usr/bin/env node
/**
 * Visual QA for DESIGN.html: open a rendered page offline in headless Chromium,
 * screenshot every view at 1440 px and 400 px, and record network requests.
 *
 * Usage: node scripts/html_qa.js <DESIGN.html> <out-dir> [--views brief,tasks,...]
 *        [--hash-views brief,tasks,...] [--jpeg] [--executable <chromium>]
 *
 * --hash-views drives a page by URL hash instead of section[data-view]; it is
 * how the reference files in evals/target/ are captured for the grader.
 * Writes <out-dir>/<view>-1440.<ext>, <out-dir>/<view>-400.<ext> and
 * <out-dir>/qa.json (views, sizes, console errors, external requests).
 * Needs the Playwright package and a Chromium it can launch; it makes no
 * network request itself and blocks any the page would attempt.
 */
const fs = require("fs");
const path = require("path");

async function main() {
  const [, , htmlPath, outDir, ...rest] = process.argv;
  if (!htmlPath || !outDir) {
    console.error("usage: html_qa.js <DESIGN.html> <out-dir> [--views a,b] [--executable path]");
    process.exit(2);
  }
  let only = null;
  let hashViews = null;
  let jpeg = false;
  let executablePath;
  for (let i = 0; i < rest.length; i++) {
    if (rest[i] === "--views") only = rest[++i].split(",");
    if (rest[i] === "--hash-views") hashViews = rest[++i].split(",");
    if (rest[i] === "--jpeg") jpeg = true;
    if (rest[i] === "--executable") executablePath = rest[++i];
  }
  const ext = jpeg ? "jpg" : "png";
  const shot = { fullPage: true, ...(jpeg ? { type: "jpeg", quality: 72 } : {}) };
  const { chromium } = require("playwright");
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch(executablePath ? { executablePath } : {});
  const report = { html: path.resolve(htmlPath), views: [], consoleErrors: [], externalRequests: [] };
  const fileUrl = "file://" + path.resolve(htmlPath);
  for (const width of [1440, 400]) {
    const context = await browser.newContext({ viewport: { width, height: width === 1440 ? 900 : 800 }, deviceScaleFactor: 1 });
    await context.route("**/*", route => {
      const url = route.request().url();
      if (url.startsWith("file://")) return route.continue();
      report.externalRequests.push(url);
      return route.abort();
    });
    const page = await context.newPage();
    page.on("console", msg => { if (msg.type() === "error") report.consoleErrors.push(width + ": " + msg.text()); });
    page.on("pageerror", err => report.consoleErrors.push(width + ": " + String(err)));
    if (hashViews) {
      for (const view of hashViews) {
        await page.goto(fileUrl + "#" + view, { waitUntil: "load" });
        await page.reload({ waitUntil: "load" });
        await page.waitForTimeout(150);
        const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
        const file = path.join(outDir, `${view}-${width}.${ext}`);
        await page.screenshot({ path: file, ...shot });
        report.views.push({ view, width, visible: view, pageScrollWidth: scrollWidth, horizontalPageScroll: scrollWidth > width + 1, file: path.basename(file), reference: true });
      }
      await context.close();
      continue;
    }
    await page.goto(fileUrl, { waitUntil: "load" });
    const views = await page.$$eval("section[data-view]", els => els.map(e => e.getAttribute("data-view")));
    for (const view of views) {
      if (only && !only.includes(view)) continue;
      await page.evaluate(v => { location.hash = v; }, view);
      await page.waitForTimeout(60);
      const visible = await page.$eval("section[data-view]:not([hidden])", e => e.getAttribute("data-view"));
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      const file = path.join(outDir, `${view}-${width}.${ext}`);
      await page.screenshot({ path: file, ...shot });
      report.views.push({ view, width, visible, pageScrollWidth: scrollWidth, horizontalPageScroll: scrollWidth > width + 1, file: path.basename(file) });
    }
    await context.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(outDir, "qa.json"), JSON.stringify(report, null, 2) + "\n");
  const bad = report.views.filter(v => v.visible !== v.view || v.horizontalPageScroll);
  console.log(JSON.stringify({ views: report.views.length, consoleErrors: report.consoleErrors.length, externalRequests: report.externalRequests.length, problems: bad.length, out: outDir }));
  // Reference captures may legitimately request fonts (blocked here); only rendered output must be clean.
  process.exit(!hashViews && (report.consoleErrors.length || report.externalRequests.length || bad.length) ? 1 : 0);
}

main().catch(err => { console.error(err); process.exit(1); });
