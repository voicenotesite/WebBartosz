const { chromium } = require('playwright');

const sites = [
  { name: "portfolio", url: "https://voicenotesite.github.io/WebBartosz/" },
  { name: "ai-chat-proxy", url: "https://ai-chat-proxy-twj4.onrender.com" },
  { name: "cliniguard", url: "https://cliniguard.pl" },
  { name: "search-engine", url: "https://search-engine-l2zt.onrender.com" },
  { name: "graphql-blog", url: "https://graphql-blog-lxjy.onrender.com" },
  { name: "link-shortener", url: "https://fastapiurl.onrender.com" }
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
      console.log(`  DONE`);
    } catch(e) {
      console.log(`  Error: ${e.message}`);
    }
    await page.close();
  }
  
  await browser.close();
})();
