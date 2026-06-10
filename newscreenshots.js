const { chromium } = require('playwright');
const sites = [
  { name: "portfolio-api", url: "https://python-portfolio-y0z8.onrender.com" },
  { name: "novactorio", url: "https://factoryworld.mmc29213.workers.dev/" },
  { name: "cv-maker", url: "https://voicenotesite.github.io/CV-MAKER" },
  { name: "rag-qa", url: "https://github.com/voicenotesite/rag-qa" }
];

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1200, height: 800 } });
  
  for (const site of sites) {
    console.log(`Screenshot: ${site.name}`);
    const page = await context.newPage();
    try {
      await page.goto(site.url, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(3000);
      await page.screenshot({ path: `screenshots/${site.name}.png` });
      console.log('  DONE');
    } catch(e) {
      console.log('  Error:', e.message);
    }
    await page.close();
  }
  await browser.close();
})();
