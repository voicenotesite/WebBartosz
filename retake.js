const { chromium } = require('playwright');
const sites = [
  { name: "ai-chat-proxy", url: "https://ai-chat-proxy-twj4.onrender.com" },
  { name: "search-engine", url: "https://search-engine-l2zt.onrender.com" },
  { name: "link-shortener", url: "https://fastapiurl.onrender.com" }
];

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1200, height: 800 } });
  
  for (const site of sites) {
    console.log(`Retaking: ${site.name}`);
    const page = await context.newPage();
    try {
      await page.goto(site.url, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(4000);
      await page.screenshot({ path: `screenshots/${site.name}.png` });
      console.log('  DONE');
    } catch(e) {
      console.log('  Error:', e.message);
    }
    await page.close();
  }
  await browser.close();
})();
